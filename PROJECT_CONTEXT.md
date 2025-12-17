# Realnet Project Context

## Project Overview

Realnet is a server application that provides a flexible backend infrastructure for building and managing applications. It offers multi-provider data storage, authentication, and API capabilities with a focus on security and scalability. The system is designed to address common challenges in backend infrastructure, including:

- Complex deployment requirements
- Multiple storage backend needs
- Security configuration management
- Service integration complexity

Realnet provides solutions through:
- Flexible database support (primarily PostgreSQL)
- Local and cloud storage (local filesystem by default, AWS S3 optional)
- Message queue handling (MQTT for distributed processing, SQS for AWS)
- Kubernetes resource management (20+ resource types)
- AI agent orchestration via MQTT
- WordPress CMS integration with bidirectional sync
- File management system
- Token-based authentication
- Environment-based configuration
- Multiple deployment options (local, Docker, Kubernetes)

## Architecture

### Core Components

1. **Command System**
   - CLI entry point
   - Command handlers (server, auth, info)
   - Consistent argument parsing
   - Error handling and help documentation

2. **Provider System**
   - Abstract provider interface
   - Multiple backend implementations:
     - SQL Provider (PostgreSQL)
     - AWS Provider
     - Generic Provider
     - File Provider
     - JSON/XML/YAML Providers
   - Storage-agnostic operations
   - Transaction handling

3. **Resource System**
   - Type-based resources
   - Hierarchical organization
   - Access control integration
   - Attribute management
   - File handling
   - Form management
   - View rendering

4. **Runner System**
   - Protocol abstraction
   - HTTP Server (Flask-based REST API)
   - MQTT Runner (message-driven async processing)
   - SQS Handler (AWS integration)
   - Shell Interface
   - Static file serving
   - Template processing

5. **Type System**
   - Base types in core.json
   - Resource types in specific JSONs (kubernetes.json, websites.json, wordpress.json, runner.json, crm.json)
   - App types for UI
   - Module attribute for handling

6. **Agent System**
   - MQTT-based distributed agents
   - Command and status topics per agent
   - Active/inactive lifecycle management
   - Script-based message processing

7. **Kubernetes Integration**
   - K8s API client wrapper
   - 20+ resource types (Pod, Deployment, Service, etc.)
   - In-cluster and kubeconfig authentication
   - Manifest generation and deployment

8. **WordPress Integration**
   - PHP plugin for WordPress multisite
   - Python client for WordPress API
   - JWT authentication
   - Website, Page, Post synchronization
   - MQTT-driven sync runner

### Component Relationships

1. **Command Flow**
   - CLI Input → Command Parser → Command Handler → Core Logic → Provider/Runner

2. **Data Flow**
   - Request → Runner → Resource → Provider → Storage

3. **Authentication Flow**
   - Request → Token Check → Auth Validation → Access Grant → Resource Access

## Technology Stack

### Core Technologies
- Python 3.x
- PostgreSQL Database (with PostGIS for spatial data)
- AWS Services (S3, SQS)
- MQTT (Mosquitto broker)
- Kubernetes API
- HTTP/REST APIs
- Docker/Kubernetes
- WordPress (Multisite)
- Flask (HTTP server)

### Key Dependencies
- PostgreSQL client (psycopg2)
- AWS SDK (boto3)
- Cryptography module
- Flask (HTTP server)
- Template engine (Jinja2)
- Kubernetes client (official Python client)
- MQTT client (paho-mqtt)
- SQLAlchemy (ORM)
- Authlib (OAuth2)
- GeoAlchemy2 (PostGIS spatial data)
- PyYAML (K8s manifest parsing)

## Project Structure

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
│   ├── cluster/   # K8s resource management
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
│       ├── kubernetes.json  # 19 K8s resource types
│       ├── websites.json    # Website/page/post types
│       ├── wordpress.json   # WordPress resource types
│       ├── runner.json      # Runner task types
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

## Key Patterns

### Provider Pattern
- Abstract provider interface in core/provider.py
- Concrete implementations in provider/
- Each provider must implement CRUD operations
- Provider selection through configuration
- Transaction handling required
- Error management consistent

### Resource Pattern
- Resources inherit from Type base class
- Resources use appropriate provider (ContextProvider)
- Resources handle errors properly
- Resources implement required methods (get_items, get_item)
- Resources can use external clients (e.g. kubernetes)
- Resources MUST receive provider in __init__ and pass to super()
- GenericResourceProvider instantiates resources with self as provider

### Runner Pattern
- Base runner in runner/runner.py
- Protocol-specific implementations
- Middleware support
- Template processing
- Static file handling
- Error responses

### Command Pattern
- Command modules in cmd/
- Consistent argument parsing
- Error handling
- Help documentation
- Status feedback

### Resource Creation Pattern
1. Create Python class in resource/
2. Inherit from Type base class
3. Implement required methods
4. Add error handling
5. Configure provider
6. Define types in initialization/
7. Set module and icon attributes
8. Configure views and queries
9. Add resource endpoints
10. Set up app integration

### App Creation Pattern
1. Define app type
2. Configure views and menus
3. Add app instance
4. Set icons and queries
5. Handle permissions

### Type System Dependencies
- Core types → Resource types → App types
- Apps can reference resource types (e.g. in queries)
- Resource types must not reference app types
- Each layer has its own initialization file
- Initialization order follows dependency flow

## Current Status

### Completed Components
- Command-line interface
- Provider interface
- Resource type system
- Runner architecture (HTTP, MQTT, SQS)
- Configuration management
- SQL Provider (PostgreSQL with PostGIS)
- AWS Provider (S3 data storage)
- Local Data Provider (default filesystem storage)
- Generic Provider
- File Provider
- JSON/XML/YAML Providers
- WordPress Provider (API client with JWT auth)
- File handling
- Form management
- View system
- Application resources
- User/Group management
- Access control (OAuth2 + sessions)
- GLTF 3D model support
- Kubernetes cluster integration (20+ resource types)
- AI Agents system (MQTT-based distributed agents)
- WordPress CMS integration (bidirectional sync)
- HTTP Server (Flask with Authlib OAuth2)
- MQTT Runner (message-driven processing)
- SQS Handler
- Shell Interface
- Static file serving
- Template processing
- Local development setup
- Docker support
- Kubernetes configuration (full stack deployment)
- Pip package distribution
- WordPress plugin (PHP with REST API)
- RBAC for Kubernetes resources

### Current Focus
1. Documentation updates and maintenance
2. Cluster deployment optimization
3. Expanding agent capabilities
4. Enhanced WordPress integration features

### Recent Achievements
1. Kubernetes Integration:
   - Cluster resource with K8s API integration
   - In-cluster and local authentication
   - Resource type mapping
   - Error handling
   - K8s resource types
   - Cluster app type
   - Resource views
   - Material icons
   - RBAC configuration
   - ServiceAccount setup
   - Initialization sequence
   - App visibility

2. WordPress Integration:
   - WordPress deployment in Kubernetes
   - MySQL database deployment
   - PHP plugin with REST API endpoints
   - Python client with JWT authentication
   - Bidirectional content sync (Website, Page, Post)
   - MQTT-driven sync runner
   - Multisite support
   - Custom template system
   - Ingress configuration
   - Database secrets and ConfigMaps

3. AI Agents System:
   - MQTT-based agent communication
   - Agent resource type and management
   - Command/status topic architecture
   - Active/inactive lifecycle
   - Script-based message handling
   - Rate limiting for message processing

4. MQTT Runner Infrastructure:
   - Message-driven async processing
   - Rate-limited script execution
   - Dynamic script reload capability
   - WordPress sync integration
   - Kubernetes pod deployment
   - ConfigMap-based script management

5. Local Data Provider:
   - Default filesystem storage
   - Replaces S3 as default
   - Directory traversal protection
   - Automatic MIME type detection
   - Configurable storage path
   - Seamless S3 fallback

### Known Issues
1. Automated testing coverage could be improved
2. Performance benchmarks needed
3. More integration examples required

### Next Steps
1. Expand automated testing coverage
2. Performance optimization and benchmarking
3. Additional integration examples
4. Enhanced agent capabilities
5. Advanced K8s operations (scaling, rollouts)
6. Additional storage providers
7. Monitoring and observability improvements

## Development Guidelines

### Resource Implementation
- Create resource class in resource/
- Inherit from Type base class
- Implement required methods
- Add error handling
- Configure provider

### JSON Definition
- Define types in initialization/
- Set module and icon attributes
- Configure views and queries
- Add resource endpoints
- Set up app integration

### Initialization Order
1. Core System Files
   - core.json: Base types
   - controls.json: UI controls
   - views.json: View definitions
   - forms.json: Form definitions
   - geometry.json: Layout definitions

2. Resource Type Files
   - Domain-specific resources (kubernetes.json, crm.json)
   - Only contain resource type definitions
   - No app type references

3. App Type Files
   - Domain-specific apps (crm_apps.json)
   - Can reference domain resource types
   - Keep separate from resource definitions

4. General Apps and Access
   - apps.json: Core app definitions
   - access.json: Access control and permissions

### File Organization Pattern
- domain.json: Resource types only
  - Basic type definitions
  - Attributes like icon
  - No views or queries
- domain_apps.json: Domain app types
  - App type definitions
  - Views and queries
  - Can reference domain resource types
- apps.json: General app types
  - Core app definitions
  - System-wide apps

### Best Practices
1. Always validate configuration
2. Handle transactions properly
3. Implement proper error handling
4. Follow access control patterns
5. Document command usage
6. Test provider implementations
7. Validate resource types
8. Handle file operations safely

## Deployment Options

### Local Development
- Environment configuration
- Database initialization
- Server startup
- Token management

### Docker Container
- Dockerfile provided
- Build process
- Environment variables
- Volume mapping

### Kubernetes Deployment
- Deployment configuration
- Service setup
- ConfigMap for settings
- Secret management
- RBAC configuration
- ServiceAccount setup
- Persistent volume claims

### WordPress Integration
- WordPress and MySQL pods
- Plugin ConfigMap
- Persistent volumes
- Database secrets
- API secrets
- Ingress configuration
- Plugin integration via ConfigMap
- Multisite configuration (in progress)

### Environment Configuration
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

## Common Workflows

### Server Management
1. Environment configuration
2. Database initialization
3. Server startup
4. Token management

### Resource Handling
1. Type definition
2. Instance creation
3. Access control
4. Attribute management
5. File operations

### Provider Usage
1. Provider selection
2. Connection management
3. CRUD operations
4. Transaction handling
5. Error recovery

### Authentication
1. Token generation (OAuth2)
2. Validation (Bearer tokens + sessions)
3. Access control (role-based)
4. Session management

### Agent Management
1. Create agent with command/status topics
2. Subscribe to MQTT topics
3. Send commands via MQTT publish
4. Monitor agent status
5. Update agent configuration
6. Cleanup on agent deletion

### Kubernetes Resource Management
1. Initialize K8s client (in-cluster or kubeconfig)
2. Query resources via RealNet API
3. Create/update resources with manifests
4. Monitor resource status
5. Delete resources
6. Namespace management

## Key Paths
- Main entry: realnet.py
- Configuration: core/config.py
- Access control: core/acl.py
- Type system: core/type.py
- HTTP runner: runner/http/runner.py
- Server command: cmd/server.py

## Critical Operations
1. Database initialization
2. Token management
3. File storage
4. Access control
5. Error handling

This document provides a comprehensive overview of the Realnet project, its architecture, components, and development guidelines. It will be updated as the project evolves.