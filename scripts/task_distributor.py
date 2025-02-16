import yaml
from pathlib import Path
from typing import Dict, List

class AgentTaskManager:
    def __init__(self):
        self.agents = self.load_agents_from_config()
        
    def load_agents_from_config(self) -> Dict:
        config_path = Path('.github/team-config.yml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)['agents']
            
    def assign_task(self, task_description: str) -> List[str]:
        assigned_agents = []
        for agent_name, agent_data in self.agents.items():
            if any(keyword in task_description.lower() for keyword in agent_data['expertise']):
                assigned_agents.append(agent_name)
        return assigned_agents
        
    def get_agent_info(self, agent_name: str) -> Dict:
        return self.agents.get(agent_name, {})
        
    def list_all_agents(self) -> List[str]:
        return list(self.agents.keys())

def main():
    manager = AgentTaskManager()
    # Example usage
    print("Available agents:", manager.list_all_agents())
    
if __name__ == "__main__":
    main()