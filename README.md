# Realnet

Realnet is a flexible backend infrastructure for building and managing applications, now with Kubernetes cluster management capabilities and agent system support.

## Features

- Multi-provider data storage (PostgreSQL, AWS S3)
- Authentication and authorization
- API and CLI interfaces
- Kubernetes cluster management
- MQTT message broker integration
- Persistent storage management
- Agent system for distributed task execution

## Prerequisites

### 1. Install Docker
- Windows: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux:
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

### 2. Install Kubernetes
#### Windows (using Docker Desktop)
1. Open Docker Desktop
2. Go to Settings > Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"

#### Linux (using Minikube)
1. Install Minikube:
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```
2. Start Minikube:
   ```bash
   minikube start
   ```

### 3. Install kubectl
#### Windows
1. Download kubectl:
   ```powershell
   curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
   ```
2. Add to PATH or move to a directory in your PATH

#### Linux
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/realnet.git
   cd realnet
   ```

2. Build the Docker image:
   ```bash
   docker build -t realnet:latest .
   ```

## Running Realnet Cluster

### 1. Configure Storage
By default, Realnet uses `/data` for persistent storage. You can modify this in `k8s/base/storage.yaml`.

### 2. Deploy the Cluster

#### Linux/macOS
```bash
chmod +x k8s/deploy.sh  # Make script executable

# Basic deployment with initialization
./k8s/deploy.sh

# Deploy with database clear
./k8s/deploy.sh -c
# or
./k8s/deploy.sh --clear-db

# Deploy without initialization
./k8s/deploy.sh -s
# or
./k8s/deploy.sh --skip-init

# Deploy with database clear but skip initialization
./k8s/deploy.sh -c -s
# or
./k8s/deploy.sh --clear-db --skip-init
```

#### Windows (PowerShell)
```powershell
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force

# Basic deployment with initialization
.\k8s\deploy.ps1

# Deploy with database clear
.\k8s\deploy.ps1 -ClearDB

# Deploy without initialization
.\k8s\deploy.ps1 -SkipInit

# Deploy with database clear but skip initialization
.\k8s\deploy.ps1 -ClearDB -SkipInit
```

The deployment scripts support the following options:
- Database clearing: Removes all existing data and starts fresh
- Initialization skipping: Deploys services without running the initialization step

### 3. Verify Deployment
```bash
kubectl get pods -n realnet
```

You should see:
- postgresql-0
- mosquitto-xxxxxx
- realnet-xxxxxx

All pods should show status as "Running".

Note for Windows users: If you're using Docker Desktop, ensure Kubernetes is enabled in Docker Desktop settings and the context is set correctly:
```powershell
# Check current context
kubectl config current-context

# If needed, switch to docker-desktop context
kubectl config use-context docker-desktop
```

### 4. Access Services

Services are available locally at:
- PostgreSQL: localhost:5433 (external) / postgresql:5432 (internal)
  - Database: realnet
  - Username: realnet
  - Password: realnet
- MQTT Broker: 
  - MQTT: localhost:1883
  - WebSockets: localhost:9001
- Realnet API: http://localhost:8080

All services are exposed via LoadBalancer, so no manual port forwarding is needed.

## Agent System

Realnet includes an agent system that enables communication via MQTT topics. Agents can be created and managed through the realnet API and communicate using MQTT messages.

### Creating an Agent

1. Using the API:
```python
agent_data = {
    'id': 'my-agent',
    'name': 'My Agent',
    'description': 'Sample agent instance'
}
agent = Agent(provider)
agent.create(agent_data)
```

2. Running a Sample Agent:
```bash
# Linux/macOS
python examples/sample_agent.py

# Windows
python.exe examples\sample_agent.py
```

### Agent Communication

Each agent uses two MQTT topics:
- Command topic: `realnet/agents/{agent_id}/command`
- Status topic: `realnet/agents/{agent_id}/status`

Example command:
```json
{
    "action": "process",
    "data": {
        "task": "example_task",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }
}
```

Example status:
```json
{
    "state": "processing",
    "last_command": {
        "action": "process",
        "data": {...}
    },
    "timestamp": 1645123456.789
}
```

## Configuration

### Environment Variables
- `REALNET_DB_TYPE`: Database type (default: postgresql)
- `REALNET_DB_HOST`: Database host
- `REALNET_DB_PORT`: Database port
- `REALNET_DB_NAME`: Database name
- `REALNET_DB_USER`: Database user
- `REALNET_DB_PASS`: Database password
- `REALNET_MQTT_HOST`: MQTT broker host
- `REALNET_MQTT_PORT`: MQTT broker port

### Kubernetes Configuration
Configuration files in `k8s/base/`:
- `namespace.yaml`: Namespace definition
- `storage.yaml`: Persistent volume configuration
- `postgresql.yaml`: Database deployment
- `mosquitto.yaml`: MQTT broker deployment
- `realnet.yaml`: Main application deployment

## User Roles

- **Admin**: Full system access
- **User**: Limited access to specific applications
- **Visitor**: Access restricted to home directory only

## Development

### Local Development
1. Create Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Run development server:
   ```bash
   realnet server start
   ```

### Building Docker Image
```bash
docker build -t realnet:latest .
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod -n realnet <pod-name>
   ```

2. **Storage issues**
   - Check persistent volumes:
     ```bash
     kubectl get pv,pvc -n realnet
     ```
   - Verify storage paths exist

3. **Service connectivity**
   - Check services:
     ```bash
     kubectl get svc -n realnet
     ```
   - Verify DNS resolution:
     ```bash
     kubectl run -n realnet -it --rm debug --image=busybox -- nslookup postgresql
     ```

### Logs
```bash
# Realnet logs
kubectl logs -n realnet -l app=realnet

# PostgreSQL logs
kubectl logs -n realnet postgresql-0

# MQTT broker logs
kubectl logs -n realnet -l app=mosquitto
```

## License

See LICENSE file for details.
