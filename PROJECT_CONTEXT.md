# Realnet Project Context

## Project Overview

Realnet is a server application that provides a flexible backend infrastructure for building and managing applications. It offers multi-provider data storage, authentication, and API capabilities with a focus on security and scalability. The system is designed to address common challenges in backend infrastructure, including:

- Complex deployment requirements
- Multiple storage backend needs
- Security configuration management
- Service integration complexity

Realnet provides solutions through:
- Flexible database support (primarily PostgreSQL)
- Cloud storage integration (AWS S3)
- Message queue handling (SQS)
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
   - HTTP Server
   - SQS Handler
   - Shell Interface
   - Static file serving
   - Template processing

5. **Type System**
   - Base types in core.json
   - Resource types in specific JSONs
   - App types for UI
   - Module attribute for handling

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
- PostgreSQL Database
- AWS Services (S3, SQS)
- HTTP/REST APIs
- Docker/Kubernetes
- WordPress (Multisite)

### Key Dependencies
- PostgreSQL client
- AWS SDK
- Cryptography module
- HTTP server
- Template engine
- Kubernetes client

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
- Runner architecture
- Configuration management
- SQL Provider (PostgreSQL)
- AWS Provider
- Generic Provider
- File Provider
- JSON/XML/YAML Providers
- File handling
- Form management
- View system
- Application resources
- User/Group management
- Access control
- GLTF 3D model support
- Kubernetes cluster integration
- HTTP Server
- SQS Handler
- Shell Interface
- Static file serving
- Template processing
- Local development setup
- Docker support
- Kubernetes configuration
- Pip package distribution
- WordPress base deployment

### Current Focus
1. Kubernetes cluster integration through realnet's resource and app system
2. WordPress multisite deployment and configuration in Kubernetes

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
   - WordPress deployment
   - MySQL database deployment
   - Plugin integration mechanism
   - Ingress configuration
   - Database secrets
   - Plugin ConfigMap
   - WordPress settings
   - Service configuration
   - Ingress rules

### Known Issues
1. Documentation needs expansion
2. Testing coverage could be improved
3. Performance benchmarks needed
4. Integration examples required
5. Deployment guides need detail
6. WordPress multisite configuration not working
7. WordPress plugin activation failing
8. WordPress URL resolution issues

### Next Steps
1. Documentation enhancement
2. Testing coverage
3. Performance optimization
4. Integration examples
5. Usage guidelines
6. Fix WordPress multisite setup
7. Improve WordPress networking
8. Document WordPress integration

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
1. Token generation
2. Validation
3. Access control
4. Session management

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