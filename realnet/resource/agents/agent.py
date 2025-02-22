"""Agent entity implementation for Realnet."""
from typing import Optional, Dict, Any
from realnet.core.type import Type
from realnet.core.provider import Provider
from realnet.provider.mqtt.client import MQTTClient

class Agent(Type):
    """Agent entity type that communicates via MQTT."""

    def __init__(self, provider: Provider):
        """Initialize Agent type.
        
        Args:
            provider: Provider instance
        """
        super().__init__(provider)
        self.mqtt_client: Optional[MQTTClient] = None
        self.active_agents: Dict[str, Dict] = {}

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
        """Create a new agent.
        
        Args:
            data: Agent data including name, description, and communication settings
        
        Returns:
            Created agent data
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        agent_id = data.get('id')
        if not agent_id:
            raise ValueError("Agent ID is required")

        name = data.get('name', agent_id)
        description = data.get('description', '')
        
        # Configure agent's MQTT topics
        command_topic = f"realnet/agents/{agent_id}/command"
        status_topic = f"realnet/agents/{agent_id}/status"
        
        # Store agent configuration
        agent_data = {
            'id': agent_id,
            'name': name,
            'description': description,
            'command_topic': command_topic,
            'status_topic': status_topic,
            'status': 'created',
            'last_status': None
        }
        self.active_agents[agent_id] = agent_data

        # Subscribe to agent's status topic
        def status_callback(payload: Any) -> None:
            self.active_agents[agent_id]['last_status'] = payload
            self.active_agents[agent_id]['status'] = 'active'

        self.mqtt_client.subscribe(status_topic, status_callback)

        return agent_data

    def read(self, agent_id: str) -> Dict[str, Any]:
        """Read agent data.
        
        Args:
            agent_id: ID of the agent
        
        Returns:
            Agent data including current status
        """
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        return self.active_agents[agent_id]

    def update(self, agent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent configuration and send command if provided.
        
        Args:
            agent_id: ID of the agent
            data: Updated agent data and optional command
        
        Returns:
            Updated agent data
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent_data = self.active_agents[agent_id]
        
        # Update basic info
        if 'name' in data:
            agent_data['name'] = data['name']
        if 'description' in data:
            agent_data['description'] = data['description']

        # Send command if provided
        if 'command' in data:
            self.mqtt_client.publish(
                agent_data['command_topic'],
                data['command']
            )

        return agent_data

    def delete(self, agent_id: str) -> None:
        """Delete agent.
        
        Args:
            agent_id: ID of the agent to delete
        """
        if not self.mqtt_client:
            raise RuntimeError("MQTT client not initialized")

        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent_data = self.active_agents[agent_id]
        
        # Unsubscribe from status topic
        self.mqtt_client.unsubscribe(agent_data['status_topic'])
        
        # Send shutdown command
        self.mqtt_client.publish(
            agent_data['command_topic'],
            {'action': 'shutdown'}
        )
        
        # Remove from tracking
        del self.active_agents[agent_id]

    def cleanup(self) -> None:
        """Clean up MQTT client resources."""
        if self.mqtt_client:
            for agent_id in list(self.active_agents.keys()):
                self.delete(agent_id)
            self.mqtt_client.disconnect()
            self.mqtt_client = None
            self.active_agents.clear()
