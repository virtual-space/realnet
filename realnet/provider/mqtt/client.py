"""MQTT Client implementation for Realnet."""
import paho.mqtt.client as mqtt
from typing import Optional, Callable, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class MQTTClient:
    """MQTT Client wrapper for Realnet."""
    
    def __init__(self, host: str = "localhost", port: int = 1883):
        """Initialize MQTT client.
        
        Args:
            host: MQTT broker hostname
            port: MQTT broker port
        """
        self.host = host
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.subscriptions: Dict[str, Callable] = {}
        self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection established."""
        logger.info(f"Connected to MQTT broker with result code {rc}")
        self.connected = True
        # Resubscribe to topics on reconnect
        for topic in self.subscriptions:
            self.client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        """Handle received messages."""
        try:
            if msg.topic in self.subscriptions:
                payload = msg.payload.decode()
                try:
                    # Try to parse as JSON
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    # Use raw payload if not JSON
                    data = payload
                self.subscriptions[msg.topic](data)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        logger.info("Disconnected from MQTT broker")
        self.connected = False

    def connect(self) -> None:
        """Connect to MQTT broker."""
        try:
            self.client.connect(self.host, self.port)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> None:
        """Publish message to topic.
        
        Args:
            topic: Topic to publish to
            payload: Message payload (will be converted to JSON if possible)
            qos: Quality of Service level
            retain: Whether to retain the message
        """
        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)
            elif not isinstance(payload, str):
                payload = str(payload)
            self.client.publish(topic, payload, qos, retain)
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            raise

    def subscribe(self, topic: str, callback: Callable, qos: int = 0) -> None:
        """Subscribe to topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Callback function for received messages
            qos: Quality of Service level
        """
        try:
            self.subscriptions[topic] = callback
            self.client.subscribe(topic, qos)
        except Exception as e:
            logger.error(f"Failed to subscribe to {topic}: {e}")
            raise

    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from topic.
        
        Args:
            topic: Topic to unsubscribe from
        """
        try:
            if topic in self.subscriptions:
                del self.subscriptions[topic]
            self.client.unsubscribe(topic)
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {topic}: {e}")
            raise
