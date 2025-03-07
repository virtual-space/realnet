# RealNet Integration Guide

## 1. Introduction

### 1.1 What is RealNet?

RealNet is a server application that provides flexible backend infrastructure for building and managing applications. It offers multi-provider data storage, authentication, and API capabilities with a focus on security and scalability.

### 1.2 Core Capabilities

- **Data Management**: PostgreSQL database support, AWS S3 storage integration, SQS message queue support, file handling
- **Authentication & Security**: User authentication, token-based authorization, secure configuration
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
│   ├── aws/
│   ├── generic/
│   ├── json/
│   ├── sql/
│   ├── xml/
│   └── yaml/
├── resource/      # Resource types
│   ├── files/
│   ├── forms/
│   ├── views/
│   ├── cluster/   # K8s integration
│   └── ...
├── runner/        # Protocol runners
│   ├── http/
│   └── sqs/
├── shell/         # Shell interface
├── static/        # Static resources
│   └── initialization/  # Resource definitions
│       ├── core.json
│       ├── apps.json
│       ├── kubernetes.json
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
- PostgreSQL
- gcc/g++ (for some dependencies)
- Development tools
- (Optional) Docker and Kubernetes for container deployment
- (Optional) AWS credentials for S3/SQS integration

### 3.2 Python Dependencies

```
setuptools-rust
cryptography
database drivers
AWS SDK
HTTP server
kubernetes client
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

```
REALNET_SERVER_HOST='0.0.0.0'
REALNET_SERVER_PORT='8080'
REALNET_DB_TYPE=postgresql
REALNET_DB_USER=<username>
REALNET_DB_PASS=<password>
REALNET_DB_HOST=<host>
REALNET_DB_PORT=<port>
REALNET_DB_NAME=<dbname>
REALNET_STORAGE_TYPE='s3'
REALNET_STORAGE_S3_BUCKET=<bucket>
REALNET_STORAGE_S3_KEY=<key>
REALNET_STORAGE_S3_SECRET=<secret>
REALNET_STORAGE_S3_REGION=<region>
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

#### 4.2.3 Get Kubernetes Clusters

```
GET /api/cluster
Authorization: Bearer <token>
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

RealNet includes WordPress integration capabilities:

#### 5.3.1 WordPress Deployment

1. Configure WordPress deployment in Kubernetes:
   - WordPress container
   - MySQL database
   - Plugin integration
   - Networking setup

2. Deploy using Kubernetes manifests in `k8s/base/wordpress.yaml`

#### 5.3.2 WordPress Plugin

RealNet includes a WordPress plugin for integration:

- Located in `realnet-wordpress/`
- Provides API connectivity between WordPress and RealNet
- Supports custom post types and fields

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

#### 6.1.3 WordPress Integration

**Issue**: WordPress multisite configuration not working.
**Solution**:
- Review WordPress multisite configuration approach
- Check site URL resolution between localhost and wordpress.local
- Consider separating multisite setup into post-installation step

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
| REALNET_DB_TYPE | Database type | postgresql |
| REALNET_DB_USER | Database username | |
| REALNET_DB_PASS | Database password | |
| REALNET_DB_HOST | Database host | localhost |
| REALNET_DB_PORT | Database port | 5432 |
| REALNET_DB_NAME | Database name | realnet |
| REALNET_STORAGE_TYPE | Storage type | local |
| REALNET_STORAGE_S3_BUCKET | S3 bucket name | |
| REALNET_STORAGE_S3_KEY | S3 access key | |
| REALNET_STORAGE_S3_SECRET | S3 secret key | |
| REALNET_STORAGE_S3_REGION | S3 region | us-east-1 |
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
| Cluster | Kubernetes integration | resource/cluster/cluster.py |

### 7.4 Initialization Order

The correct initialization order in `server.py` is crucial:

1. Core System Files
   - core.json: Base types
   - controls.json: UI controls
   - views.json: View definitions
   - forms.json: Form definitions
   - geometry.json: Layout definitions

2. Resource Type Files
   - kubernetes.json: K8s resources
   - crm.json: CRM resources
   - Other domain resources

3. App Type Files
   - domain_apps.json: Domain-specific apps

4. General Apps and Access Files
   - apps.json: App definitions
   - access.json: Access control

This order ensures dependencies exist before they're referenced.

## 8. Current Development Status

RealNet has a solid foundation with core features implemented. Kubernetes integration adds cluster management capabilities. WordPress integration is in progress with basic deployment working but multisite configuration needs improvement. Focus is on improving documentation, testing, and providing better examples and guides.

### 8.1 Completed Components
- Core system (CLI, providers, resources, runners)
- Multiple deployment options
- Kubernetes integration
- Basic WordPress deployment

### 8.2 In Progress
- WordPress multisite configuration
- Documentation enhancement
- Testing coverage
- Performance optimization

### 8.3 Known Issues
- WordPress multisite configuration not fully working
- Site URL resolution issues between localhost and wordpress.local
- Plugin activation failing due to site URL issues

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