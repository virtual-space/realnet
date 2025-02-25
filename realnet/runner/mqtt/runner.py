import os
import time
import logging
from typing import Dict, Any, Optional, List
from realnet.core.type import Type
from realnet.core.provider import ContextProvider
from .client import MQTTClient

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, rate: int = 10, per: float = 1.0):
        """Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed per time period
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    def check(self) -> bool:
        """Check if action is allowed under current rate limit."""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * (self.rate / self.per)
        
        if self.allowance > self.rate:
            self.allowance = self.rate
            
        if self.allowance < 1.0:
            return False
            
        self.allowance -= 1.0
        return True

class MQTTRunner:
    def __init__(self, context: Dict[str, Any]):
        """Initialize MQTT runner.
        
        Args:
            context: Configuration context
        """
        self.context = context
        # Get MQTT configuration from environment
        mqtt_host = os.getenv('REALNET_MQTT_HOST', 'mosquitto')
        mqtt_port = int(os.getenv('REALNET_MQTT_PORT', '1883'))
        mqtt_rate_limit = int(os.getenv('REALNET_MQTT_RATE_LIMIT', '10'))
        mqtt_rate_period = float(os.getenv('REALNET_MQTT_RATE_PERIOD', '1.0'))

        self.client = MQTTClient(
            host=mqtt_host,
            port=mqtt_port
        )
        self.rate_limiter = RateLimiter(
            rate=mqtt_rate_limit,
            per=mqtt_rate_period
        )
        self.system_topic = "realnet/system"
        self.script = None

    def start(self):
        """Start the MQTT runner."""
        if self.client.connect():
            # Subscribe to system topic
            self.client.subscribe(self.system_topic, self._handle_system_message)
            logger.info(f"MQTT runner started, listening on {self.system_topic}")
        else:
            logger.error("Failed to start MQTT runner")

    def stop(self):
        """Stop the MQTT runner."""
        self.client.disconnect()
        logger.info("MQTT runner stopped")

    def _handle_system_message(self, message: Dict[str, Any]):
        """Handle messages on the system topic."""
        if not self.rate_limiter.check():
            logger.warning("Rate limit exceeded, message dropped")
            return

        try:
            action = message.get('action')
            if not action:
                logger.warning("Message missing 'action' field")
                return

            if action == 'execute':
                self._handle_execute(message)
            elif action == 'update_script':
                self._handle_update_script(message)
            else:
                logger.warning(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            self._publish_result({
                'status': 'error',
                'error': str(e)
            })

    def _handle_execute(self, message: Dict[str, Any]):
        """Handle execute action."""
        if not self.script:
            logger.error("No script loaded")
            self._publish_result({
                'status': 'error',
                'error': 'No script loaded'
            })
            return

        try:
            # Create a clean execution context
            context = {
                'message': message,
                'publish': self._publish_result
            }

            # Execute the script
            exec(self.script, context)
            
            logger.info("Script executed successfully")

        except Exception as e:
            logger.error(f"Script execution error: {str(e)}")
            self._publish_result({
                'status': 'error',
                'error': f'Script execution error: {str(e)}'
            })

    def _handle_update_script(self, message: Dict[str, Any]):
        """Handle script update action."""
        try:
            script = message.get('script')
            if not script:
                raise ValueError("No script provided")

            # Validate script by attempting to compile it
            compile(script, '<string>', 'exec')
            
            # Store the script
            self.script = script
            
            logger.info("Script updated successfully")
            self._publish_result({
                'status': 'success',
                'message': 'Script updated'
            })

        except Exception as e:
            logger.error(f"Script update error: {str(e)}")
            self._publish_result({
                'status': 'error',
                'error': f'Script update error: {str(e)}'
            })

    def _publish_result(self, result: Dict[str, Any]):
        """Publish result to system topic."""
        self.client.publish(f"{self.system_topic}/result", result)
