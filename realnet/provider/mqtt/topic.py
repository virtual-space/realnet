"""MQTT Topic entity implementation for Realnet."""
from typing import Optional, Dict, Any
from realnet.core.type import Type
from realnet.core.provider import Provider
from .client import MQTTClient

class Topic(Type):
    """MQTT Topic entity type."""

    def __init__(self, provider: Provider):
        """Initialize Topic type.
        
        Args:
            provider: Provider instance
        """
        super().__init__(provider)
        self.mqtt_client: Optional[MQTTClient] = None
        self.subscribed_topics: Dict[str, Dict] = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize MQTT client with configuration.
        
        Args:
            config: Configuration dictionary with MQTT settings
        """
        host = config.get('mqtt_host', 'localhost')
        port = config.get('mqtt_port', 1883)
        self.mqtt_client = MQTTClient(host, port)
        self.mqtt_client.connect()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new topic subscription.
        
        Args:
            data: Topic data including name, qos, etc.
        
        Returns:
            Created topic data
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        topic_name = data.get('name')
        if not topic_name:
            raise ValueError("Topic name is required")

        qos = data.get('qos', 0)
        retain = data.get('retain', False)
        access = data.get('access', 'rw')  # read-write by default

        # Store topic configuration
        topic_data = {
            'name': topic_name,
            'qos': qos,
            'retain': retain,
            'access': access,
            'last_value': None
        }
        self.subscribed_topics[topic_name] = topic_data

        # Set up subscription if read access
        if 'r' in access:
            def message_callback(payload: Any) -> None:
                self.subscribed_topics[topic_name]['last_value'] = payload

            self.mqtt_client.subscribe(topic_name, message_callback, qos)

        return topic_data

    def read(self, topic_name: str) -> Dict[str, Any]:
        """Read topic data.
        
        Args:
            topic_name: Name of the topic
        
        Returns:
            Topic data including last received value
        """
        if topic_name not in self.subscribed_topics:
            raise ValueError(f"Topic {topic_name} not found")
        
        return self.subscribed_topics[topic_name]

    def update(self, topic_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update topic configuration and publish message if provided.
        
        Args:
            topic_name: Name of the topic
            data: Updated topic data and optional message
        
        Returns:
            Updated topic data
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        if topic_name not in self.subscribed_topics:
            raise ValueError(f"Topic {topic_name} not found")

        topic_data = self.subscribed_topics[topic_name]
        
        # Update configuration
        if 'qos' in data:
            topic_data['qos'] = data['qos']
        if 'retain' in data:
            topic_data['retain'] = data['retain']
        if 'access' in data:
            topic_data['access'] = data['access']

        # Publish message if provided and have write access
        if 'message' in data and 'w' in topic_data['access']:
            self.mqtt_client.publish(
                topic_name,
                data['message'],
                topic_data['qos'],
                topic_data['retain']
            )

        return topic_data

    def delete(self, topic_name: str) -> None:
        """Delete topic subscription.
        
        Args:
            topic_name: Name of the topic to delete
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        if topic_name not in self.subscribed_topics:
            raise ValueError(f"Topic {topic_name} not found")

        # Unsubscribe and remove from tracking
        self.mqtt_client.unsubscribe(topic_name)
        del self.subscribed_topics[topic_name]

    def cleanup(self) -> None:
        """Clean up MQTT client resources."""
        if self.mqtt_client:
            for topic in list(self.subscribed_topics.keys()):
                self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.disconnect()
            self.mqtt_client = None
            self.subscribed_topics.clear()
