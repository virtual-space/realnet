"""Sample agent implementation that connects to realnet via MQTT."""
import paho.mqtt.client as mqtt
import json
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleAgent:
    """A sample agent that connects to realnet via MQTT."""
    
    def __init__(self, agent_id: str, host: str = "localhost", port: int = 1883):
        """Initialize the agent.
        
        Args:
            agent_id: Unique identifier for this agent
            host: MQTT broker hostname
            port: MQTT broker port
        """
        self.agent_id = agent_id
        self.host = host
        self.port = port
        
        # Configure MQTT topics
        self.command_topic = f"realnet/agents/{agent_id}/command"
        self.status_topic = f"realnet/agents/{agent_id}/status"
        
        # Initialize MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.running = False

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection established."""
        logger.info(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to command topic
        self.client.subscribe(self.command_topic)
        # Publish initial status
        self.publish_status({
            "state": "ready",
            "timestamp": time.time()
        })

    def _on_message(self, client, userdata, msg):
        """Handle received messages."""
        try:
            payload = msg.payload.decode()
            try:
                command = json.loads(payload)
            except json.JSONDecodeError:
                command = payload

            logger.info(f"Received command: {command}")
            
            # Handle shutdown command
            if isinstance(command, dict) and command.get('action') == 'shutdown':
                logger.info("Received shutdown command")
                self.running = False
                return
                
            # Process command and get response
            response = self.process_command(command)
            
            # Publish status update
            self.publish_status({
                "state": "processed_command",
                "last_command": command,
                "response": response,
                "timestamp": time.time()
            })

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.publish_status({
                "state": "error",
                "error": str(e),
                "timestamp": time.time()
            })

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        logger.info("Disconnected from MQTT broker")
        self.running = False

    def publish_status(self, status: Dict[str, Any]):
        """Publish status update.
        
        Args:
            status: Status data to publish
        """
        try:
            self.client.publish(self.status_topic, json.dumps(status))
        except Exception as e:
            logger.error(f"Error publishing status: {e}")

    def process_command(self, command: Any) -> Any:
        """Process received command and return response.
        
        This is a sample implementation that simply echoes the command.
        Override this method to implement custom command processing.
        
        Args:
            command: Received command data
            
        Returns:
            Command response
        """
        return f"Processed command: {command}"

    def run(self):
        """Run the agent."""
        try:
            # Connect to MQTT broker
            self.client.connect(self.host, self.port)
            self.client.loop_start()
            self.running = True
            
            logger.info(f"Agent {self.agent_id} started")
            
            # Main loop
            while self.running:
                # Publish periodic status updates
                self.publish_status({
                    "state": "running",
                    "timestamp": time.time()
                })
                time.sleep(60)  # Status update interval
                
        except Exception as e:
            logger.error(f"Error in agent main loop: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info(f"Agent {self.agent_id} stopped")

if __name__ == "__main__":
    # Create and run a sample agent
    agent = SampleAgent("sample-agent")
    agent.run()
