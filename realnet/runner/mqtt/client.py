import paho.mqtt.client as mqtt
from typing import Callable, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, host: str = 'mosquitto', port: int = 1883):
        self.host = host
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.topic_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        
    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict[str, Any], rc: int):
        """Handle connection established."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
            # Resubscribe to topics on reconnect
            for topic in self.topic_handlers.keys():
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        """Handle received message."""
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic in self.topic_handlers:
                self.topic_handlers[msg.topic](payload)
            else:
                logger.warning(f"No handler for topic: {msg.topic}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload on topic {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing message on topic {msg.topic}: {str(e)}")

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int):
        """Handle disconnection."""
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
        else:
            logger.info("Disconnected from MQTT broker")

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client.connect(self.host, self.port)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        """Subscribe to a topic with a message handler."""
        self.topic_handlers[topic] = handler
        if self.client.is_connected():
            self.client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str):
        """Unsubscribe from a topic."""
        if topic in self.topic_handlers:
            del self.topic_handlers[topic]
            if self.client.is_connected():
                self.client.unsubscribe(topic)
                logger.info(f"Unsubscribed from topic: {topic}")

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 0) -> bool:
        """Publish a message to a topic."""
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published message to topic: {topic}")
                return True
            else:
                logger.error(f"Failed to publish message to topic {topic}, rc: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing to topic {topic}: {str(e)}")
            return False

    @property
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker."""
        return self.client.is_connected()
