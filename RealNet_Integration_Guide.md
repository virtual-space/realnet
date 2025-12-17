# RealNet Integration Guide

## 1. Introduction

### 1.1 What is RealNet?

RealNet is a server application that provides flexible backend infrastructure for building and managing applications. It offers multi-provider data storage, authentication, and API capabilities with a focus on security and scalability.

### 1.2 Core Capabilities

- **Data Management**: PostgreSQL database support (with PostGIS), local filesystem storage (default), AWS S3 storage (optional), MQTT message queue, file handling
- **Kubernetes Management**: 20+ K8s resource types, full CRUD operations, in-cluster and kubeconfig support, manifest generation
- **AI Agents**: MQTT-based distributed agents, command/status topics, lifecycle management, script-based processing
- **WordPress Integration**: Bidirectional content sync, PHP plugin, Python client, multisite support, JWT authentication
- **Authentication & Security**: OAuth2 with JWT tokens, session-based auth, token-based authorization, secure configuration
- **API & Integration**: REST API endpoints, CLI interface, multiple deployment options
- **Deployment Flexibility**: Local development, Docker containerization, Kubernetes deployment, Pip package

### 1.3 Use Cases

- **Application Backend**: Database management, file storage, message queue processing, API endpoints
- **Infrastructure Management**: Multi-environment deployment, security configuration, service integration
- **Development Support**: Local development, testing environments, integration testing

## 2. Architecture

### 2.1 Component Overview

RealNet is built on several core components:

```
realnet/
├── cmd/           # Command line interface
│   ├── create.py
│   ├── get.py
│   ├── info.py
│   ├── runner.py
│   └── server.py  # Server initialization and resource loading
├── core/          # Core functionality
│   ├── acl.py
│   ├── config.py
│   ├── hierarchy.py
│   ├── provider.py  # Base provider classes
│   └── type.py    # Base type system
├── provider/      # Storage providers
│   ├── aws/       # S3 data provider
│   ├── generic/   # Local data provider (default)
│   ├── json/
│   ├── sql/       # PostgreSQL providers
│   ├── wordpress/ # WordPress API client
│   ├── xml/
│   └── yaml/
├── resource/      # Resource types
│   ├── agents/    # AI agent resources
│   ├── cluster/   # K8s resource management (20+ types)
│   ├── files/
│   ├── forms/
│   ├── views/
│   └── ...
├── runner/        # Protocol runners
│   ├── http/      # Flask REST API server
│   ├── mqtt/      # MQTT message processor
│   └── sqs/       # AWS SQS handler
├── shell/         # Shell interface
├── static/        # Static resources
│   └── initialization/  # Resource definitions
│       ├── core.json
│       ├── controls.json
│       ├── views.json
│       ├── forms.json
│       ├── geometry.json
│       ├── kubernetes.json    # 19 K8s resource types
│       ├── websites.json      # Website/page/post types
│       ├── wordpress.json     # WordPress resource types
│       ├── runner.json        # Runner task types
│       ├── runner_apps.json
│       ├── websites_apps.json
│       ├── wordpress_apps.json
│       ├── crm.json
│       ├── crm_apps.json
│       ├── apps.json
│       ├── access.json
│       └── ...
└── templates/     # HTML templates
```

### 2.2 Type System

RealNet uses a hierarchical type system:

1. **Core Types**: Base functionality (Item, Resource, etc.)
2. **Resource Types**: Domain logic extending core types
3. **App Types**: UI and interaction components

Dependencies flow from core → resources → apps:
- Apps can reference resource types (e.g., in queries)
- Resource types must not reference app types
- Each layer has its own initialization file
- Initialization order follows dependency flow

### 2.3 Key Design Patterns

#### 2.3.1 Provider Pattern
- Abstract provider interface
- Multiple backend support
- Storage agnostic operations
- Consistent data access

#### 2.3.2 Resource Pattern
- Type-based resources
- File handling
- Form management
- View rendering

#### 2.3.3 Runner Pattern
- Protocol abstraction
- Service integration
- Template handling
- Static file serving

#### 2.3.4 Command Pattern
- Centralized command handling
- Modular command implementation
- Consistent CLI interface
- Command validation

### 2.4 Data Flow

```
Request → Runner → Resource → Provider → Storage
```

### 2.5 Authentication Flow

```
Request → Token Check → Auth Validation → Access Grant → Resource Access
```

## 3. Installation and Deployment

### 3.1 Prerequisites

- Python 3.x
- PostgreSQL (with PostGIS extension for spatial data)
- gcc/g++ (for some dependencies)
- Development tools
- (Optional) Docker and Kubernetes for container deployment
- (Optional) AWS credentials for S3/SQS integration
- (Optional) MQTT broker (Mosquitto) for agents and runners
- (Optional) WordPress instance for CMS integration

### 3.2 Python Dependencies

```
setuptools-rust
cryptography
psycopg2 (PostgreSQL client)
boto3 (AWS SDK)
Flask (HTTP server)
Jinja2 (template engine)
kubernetes (K8s Python client)
paho-mqtt (MQTT client)
SQLAlchemy (ORM)
Authlib (OAuth2)
GeoAlchemy2 (PostGIS spatial data)
PyYAML (K8s manifest parsing)
```

### 3.3 Deployment Options

#### 3.3.1 Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see section 3.4)
4. Run the server: `python -m realnet server`

#### 3.3.2 Docker Deployment

1. Build the Docker image: `./build_docker`
2. Run the container:
   ```
   docker run -p 8080:8080 \
     -e REALNET_SERVER_HOST=0.0.0.0 \
     -e REALNET_SERVER_PORT=8080 \
     -e REALNET_DB_TYPE=postgresql \
     -e REALNET_DB_USER=username \
     -e REALNET_DB_PASS=password \
     -e REALNET_DB_HOST=host \
     -e REALNET_DB_PORT=port \
     -e REALNET_DB_NAME=dbname \
     realnet:latest
   ```

#### 3.3.3 Kubernetes Deployment

1. Configure Kubernetes manifests in `k8s/` directory
2. Deploy using: 
   - Windows: `k8s/deploy.ps1`
   - Linux/Mac: `k8s/deploy.sh`

#### 3.3.4 Pip Package Installation

1. Build the package: `./build_package`
2. Install: `pip install dist/realnet-*.whl`

### 3.4 Configuration

RealNet uses environment variables for configuration:

```bash
# Server
REALNET_SERVER_HOST='0.0.0.0'
REALNET_SERVER_PORT='8080'

# Database
REALNET_DB_TYPE=postgresql
REALNET_DB_USER=<username>
REALNET_DB_PASS=<password>
REALNET_DB_HOST=<host>
REALNET_DB_PORT=<port>
REALNET_DB_NAME=<dbname>

# Storage (defaults to local)
REALNET_STORAGE_TYPE=local
REALNET_STORAGE_PATH=data

# Or use S3
# REALNET_STORAGE_TYPE=s3
# REALNET_STORAGE_S3_BUCKET=<bucket>
# REALNET_STORAGE_S3_KEY=<key>
# REALNET_STORAGE_S3_SECRET=<secret>
# REALNET_STORAGE_S3_REGION=<region>

# MQTT (for agents and runners)
REALNET_MQTT_HOST=mosquitto
REALNET_MQTT_PORT=1883
REALNET_MQTT_RATE_LIMIT=10
REALNET_MQTT_RATE_PERIOD=1.0

# WordPress Integration
REALNET_WORDPRESS_URL=http://wordpress:8081
REALNET_WORDPRESS_ADMIN_USER=admin
REALNET_WORDPRESS_ADMIN_PASS=<password>
REALNET_WORDPRESS_TOKEN=<jwt-token>

# Runner
REALNET_RUNNER_SCRIPT=/app/script.py

# OAuth
REALNET_APP_SECRET=<secret-key>
REALNET_URI=http://localhost:8080
REALNET_REDIRECT_URI=http://localhost:8080/oauth/callback
```

## 4. API Interaction

### 4.1 REST API Endpoints

RealNet exposes REST API endpoints for interacting with resources. The base URL is determined by your server configuration (default: http://localhost:8080).

#### 4.1.1 Authentication

Most endpoints require authentication using a token:

```
GET /api/resource
Authorization: Bearer <token>
```

To obtain a token, use the authentication endpoint:

```
POST /api/auth
Content-Type: application/json

{
  "username": "user",
  "password": "pass"
}
```

Response:
```json
{
  "token": "your-auth-token",
  "expires": "expiration-timestamp"
}
```

#### 4.1.2 Common Resource Operations

- **List Resources**: `GET /api/resource_type`
- **Get Resource**: `GET /api/resource_type/{id}`
- **Create Resource**: `POST /api/resource_type`
- **Update Resource**: `PUT /api/resource_type/{id}`
- **Delete Resource**: `DELETE /api/resource_type/{id}`

### 4.2 Example API Requests

#### 4.2.1 List Files

```
GET /api/files
Authorization: Bearer <token>
```

#### 4.2.2 Upload File

```
POST /api/files
Authorization: Bearer <token>
Content-Type: multipart/form-data

[file data]
```

#### 4.2.3 Get Kubernetes Pods

```
GET /cluster/pods
Authorization: Bearer <token>
```

#### 4.2.4 Create Kubernetes Deployment

```
POST /cluster/deployments
Authorization: Bearer <token>
Content-Type: application/json

{
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "my-app"
  },
  "spec": {
    "replicas": 3,
    "selector": {
      "matchLabels": {
        "app": "my-app"
      }
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "my-app"
        }
      },
      "spec": {
        "containers": [{
          "name": "my-app",
          "image": "my-app:latest",
          "ports": [{"containerPort": 8080}]
        }]
      }
    }
  }
}
```

#### 4.2.5 Create AI Agent

```
POST /agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Agent",
  "attributes": {
    "description": "Example agent",
    "config": {
      "rate_limit": 10
    }
  }
}
```

#### 4.2.6 Send Agent Command via MQTT

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("mosquitto", 1883)

# Send command to agent
client.publish(
    "realnet/agents/{agent_id}/command",
    json.dumps({"action": "process", "data": {...}})
)
```

### 4.3 CLI Interaction

RealNet provides a command-line interface for interacting with the server:

```
# Get information about the server
python -m realnet info

# Create a resource
python -m realnet create resource_type --name "Resource Name" --attribute value

# Get resources
python -m realnet get resource_type [id]
```

## 5. Integration Patterns

### 5.1 Incorporating RealNet into Other Projects

#### 5.1.1 As a Backend Service

1. Deploy RealNet using one of the methods in section 3.3
2. Configure your application to communicate with RealNet's REST API
3. Use authentication tokens for secure access
4. Interact with resources through API endpoints

#### 5.1.2 As a Python Library

1. Install RealNet as a package: `pip install realnet`
2. Import and use in your Python code:

```python
from realnet import client

# Initialize client
c = client.Client(host="localhost", port=8080)

# Authenticate
c.authenticate(username="user", password="pass")

# Interact with resources
files = c.get_resources("files")
```

### 5.2 Extending RealNet

#### 5.2.1 Creating Custom Resources

1. Create a Python implementation:

```python
# In realnet/resource/custom/custom.py
from realnet.core.type import Type

class CustomResource(Type):
    def __init__(self, provider):
        super().__init__(provider)
        
    def get_items(self, query=None):
        # Implementation
        pass
        
    def get_item(self, id):
        # Implementation
        pass
```

2. Define the resource type in JSON:

```json
// In static/initialization/custom.json
{
  "types": [
    {
      "name": "CustomResource",
      "module": "realnet.resource.custom.custom",
      "icon": "custom_icon"
    }
  ]
}
```

3. Add to server initialization in `server.py`:

```python
# Add to initialization files list
initialization_files = [
    # ...existing files
    "custom.json"
]
```

#### 5.2.2 Creating Custom Apps

1. Define app type in JSON:

```json
// In static/initialization/custom_apps.json
{
  "types": [
    {
      "name": "CustomApp",
      "base": "App",
      "icon": "app_icon",
      "views": [
        {
          "name": "Main",
          "query": {
            "type": "CustomResource"
          }
        }
      ]
    }
  ]
}
```

2. Add app instance:

```json
// In static/initialization/apps.json
{
  "items": [
    {
      "type": "CustomApp",
      "name": "Custom Application"
    }
  ]
}
```

### 5.3 WordPress Integration

RealNet includes comprehensive WordPress CMS integration with bidirectional content synchronization:

#### 5.3.1 WordPress Architecture

The integration consists of three main components:

1. **PHP WordPress Plugin** (`realnet-wordpress/realnet.php`)
   - REST API endpoints for content synchronization
   - JWT authentication via `X-Realnet-Token` header
   - Sync endpoints: `/wp-json/realnet/v1/sync`
   - Template override system for RealNet-managed content
   - Hooks into WordPress action/filter system

2. **Python WordPress Client** (`realnet/provider/wordpress/client.py`)
   - JWT authentication with WordPress API
   - Multisite support for WordPress networks
   - CRUD operations for sites, pages, posts, users
   - Methods: `get_sites()`, `get_pages()`, `create_page()`, `update_post()`, etc.

3. **MQTT Sync Runner** (Kubernetes pod with `realnet runner` command)
   - Listens on `realnet/system` topic for content changes
   - Executes sync script to push changes to WordPress
   - Rate-limited message processing
   - Dynamic script reload capability

#### 5.3.2 Content Sync Flow

```
RealNet API → Create/Update Page
    ↓
Publish MQTT Message → realnet/system topic
    ↓
Runner Pod Receives → Execute sync script
    ↓
WordPress API Call → Create/Update WP content
    ↓
Result Published → realnet/system/result topic
```

#### 5.3.3 WordPress Deployment

Deploy WordPress with RealNet in Kubernetes:

```bash
# Full stack deployment includes WordPress + MySQL
kubectl apply -k k8s/base

# Or deploy individually
kubectl apply -f k8s/base/wordpress.yaml
kubectl apply -f k8s/base/mysql.yaml
```

Configuration via ConfigMap and Secrets:
- WordPress admin credentials in Secret
- Plugin code in ConfigMap
- Runner script in ConfigMap
- Environment variables for WordPress URL and token

#### 5.3.4 WordPress Plugin Installation

1. Plugin is automatically mounted via Kubernetes ConfigMap
2. Located at `/var/www/html/wp-content/plugins/realnet/realnet.php`
3. Activate through WordPress admin or via wp-cli in pod
4. Configure authentication token to match `REALNET_WORDPRESS_TOKEN`

#### 5.3.5 Supported Content Types

- **Website** → WordPress Multisite instance
- **WebPage** → WordPress Page with metadata
- **WebPost** → WordPress Post with categories, tags, authors

Each type maps to WordPress entities with attribute synchronization.

## 6. Troubleshooting

### 6.1 Common Issues

#### 6.1.1 Database Connection

**Issue**: Unable to connect to PostgreSQL database.
**Solution**: 
- Verify database credentials in environment variables
- Ensure PostgreSQL is running and accessible
- Check network connectivity and firewall settings

#### 6.1.2 Authentication Failures

**Issue**: Authentication token rejected.
**Solution**:
- Verify token is not expired
- Ensure proper token format in Authorization header
- Check user permissions for the requested resource

#### 6.1.3 MQTT Connection

**Issue**: Unable to connect to MQTT broker.
**Solution**:
- Verify MQTT broker (Mosquitto) is running
- Check `REALNET_MQTT_HOST` and `REALNET_MQTT_PORT` configuration
- Ensure network connectivity between RealNet and MQTT broker
- Check firewall rules for MQTT port (default 1883)

#### 6.1.4 Kubernetes API Access

**Issue**: Cannot access Kubernetes resources.
**Solution**:
- Verify ServiceAccount has proper RBAC permissions
- Check kubeconfig file for local development
- Ensure ClusterRole/RoleBinding are configured correctly
- Verify namespace access permissions

### 6.2 Debugging Tips

1. Enable debug logging:
   ```
   REALNET_DEBUG=true python -m realnet server
   ```

2. Check server logs for detailed error messages

3. Verify resource initialization order in `server.py`

4. Test API endpoints directly using curl or Postman

## 7. Reference

### 7.1 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| REALNET_SERVER_HOST | Server host | 127.0.0.1 |
| REALNET_SERVER_PORT | Server port | 8080 |
| REALNET_DB_TYPE | Database type (postgresql or sqlite) | postgresql |
| REALNET_DB_USER | Database username | |
| REALNET_DB_PASS | Database password | |
| REALNET_DB_HOST | Database host | localhost |
| REALNET_DB_PORT | Database port | 5432 |
| REALNET_DB_NAME | Database name | realnet |
| REALNET_STORAGE_TYPE | Storage type (local or s3) | local |
| REALNET_STORAGE_PATH | Local storage directory | data |
| REALNET_STORAGE_S3_BUCKET | S3 bucket name | |
| REALNET_STORAGE_S3_KEY | S3 access key | |
| REALNET_STORAGE_S3_SECRET | S3 secret key | |
| REALNET_STORAGE_S3_REGION | S3 region | us-east-1 |
| REALNET_MQTT_HOST | MQTT broker host | mosquitto |
| REALNET_MQTT_PORT | MQTT broker port | 1883 |
| REALNET_MQTT_RATE_LIMIT | Rate limit (requests) | 10 |
| REALNET_MQTT_RATE_PERIOD | Rate period (seconds) | 1.0 |
| REALNET_WORDPRESS_URL | WordPress instance URL | |
| REALNET_WORDPRESS_ADMIN_USER | WordPress admin username | |
| REALNET_WORDPRESS_ADMIN_PASS | WordPress admin password | |
| REALNET_WORDPRESS_TOKEN | WordPress JWT token | |
| REALNET_RUNNER_SCRIPT | Path to runner script | /app/script.py |
| REALNET_APP_SECRET | Flask secret key | |
| REALNET_URI | Base URI | http://localhost:8080 |
| REALNET_REDIRECT_URI | OAuth redirect URI | |
| REALNET_MOBILE_REDIRECT_URI | Mobile OAuth redirect | |
| REALNET_ALLOW_HTTP | Allow insecure HTTP (dev only) | false |
| REALNET_DEBUG | Enable debug mode | false |

### 7.2 Key Files and Paths

| Path | Description |
|------|-------------|
| realnet.py | Main entry point |
| core/config.py | Configuration management |
| core/acl.py | Access control |
| core/type.py | Type system |
| runner/http/runner.py | HTTP server |
| cmd/server.py | Server command |
| static/initialization/ | Resource definitions |

### 7.3 Resource Types

| Type | Description | Path |
|------|-------------|------|
| File | File management | resource/files/files.py |
| Form | Form handling | resource/forms/forms.py |
| View | View rendering | resource/views/views.py |
| App | Application | resource/apps/apps.py |
| Cluster | Kubernetes cluster management | resource/cluster/cluster.py |
| Clusters | Kubernetes resources (20+ types) | resource/cluster/clusters.py |
| Agent | AI agent management | resource/agents/agent.py |
| Website | Website/CMS content | provider/websites/resource.py |
| WordPress* | WordPress integration types | provider/wordpress/ |

*WordPress types include: WordPressSite, WordPressPage, WordPressPost, WordPressUser

### 7.4 Initialization Order

The correct initialization order in `server.py` is crucial:

1. Core System Files
   - core.json: Base types
   - controls.json: UI controls
   - views.json: View definitions
   - forms.json: Form definitions
   - geometry.json: Layout definitions

2. Resource Type Files
   - kubernetes.json: 19 K8s resource types
   - websites.json: Website/page/post types
   - wordpress.json: WordPress resource types
   - runner.json: Runner task types
   - crm.json: CRM resources
   - Other domain resources

3. App Type Files
   - runner_apps.json: Runner management apps
   - websites_apps.json: Website management apps
   - wordpress_apps.json: WordPress management apps
   - crm_apps.json: CRM applications
   - Other domain-specific apps

4. General Apps and Access Files
   - apps.json: Core app definitions
   - access.json: Access control and permissions

This order ensures dependencies exist before they're referenced.

## 8. Current Development Status

RealNet has evolved into a comprehensive infrastructure management platform with a solid foundation and advanced features implemented.

### 8.1 Completed Components
- Core system (CLI, providers, resources, runners)
- Entity-based type system with hierarchical items
- Multi-tenancy (organizations and accounts)
- OAuth2 authentication with session support
- Multiple deployment options (local, Docker, Kubernetes)
- Kubernetes integration (20+ resource types with full CRUD)
- AI Agents system (MQTT-based distributed agents)
- WordPress integration (bidirectional sync with PHP plugin)
- MQTT Runner infrastructure (message-driven processing)
- Local data provider (default filesystem storage)
- AWS integrations (S3 storage, SQS messaging)
- PostgreSQL with PostGIS spatial data support
- RBAC for Kubernetes resources
- Full documentation suite

### 8.2 Current Focus
- Documentation maintenance and updates
- Cluster deployment optimization
- Expanding agent capabilities
- Enhanced WordPress integration features
- Performance optimization

### 8.3 Known Issues
- Automated testing coverage needs improvement
- Performance benchmarks needed
- More integration examples would be beneficial

## 9. Best Practices

1. Always validate configuration before starting the server
2. Handle database transactions properly
3. Implement proper error handling in custom resources
4. Follow access control patterns for security
5. Document command usage for CLI operations
6. Test provider implementations thoroughly
7. Validate resource types before deployment
8. Handle file operations safely to prevent data loss
9. Follow the initialization order for resource definitions
10. Keep resource types and app types in separate files