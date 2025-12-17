# RealNet

**RealNet** is an open-source entity-based CMS that serves as the backend engine for the VirtualSpace ecosystem. It provides JSON schema object feeds and acts as the data/logic layer for digital twin, mixed reality, and content management applications.

## Overview

RealNet is built on Flask and SQLAlchemy with PostgreSQL, featuring:

- **Entity-Based Type System** - Types define schemas, instances are data
- **Multi-Tenancy** - Organization and account isolation
- **OAuth2 Authentication** - Secure API access with delegated auth support
- **Hierarchical Storage** - Tree-structured items with spatial support (PostGIS)
- **Dynamic API** - RESTful endpoints registered as database entities
- **Kubernetes Integration** - Full K8s resource management through type system
- **AI Agents** - Distributed agent communication via MQTT
- **WordPress Integration** - Bidirectional content synchronization
- **Flexible Storage** - Local filesystem or AWS S3

## Core Features

### Entity Type System

Everything in RealNet is data:
- **Types** define structure (like classes)
- **Instances** contain data conforming to types (like objects)
- **Items** provide hierarchical organization with parent/child relationships
- **Attributes** are JSON key-value data on types and instances

### Multi-Provider Architecture

RealNet uses a provider pattern for all data operations:
- `TypeProvider` - Type definitions and instances
- `ItemProvider` - Hierarchical item CRUD
- `DataProvider` - File storage (local or S3)
- `EndpointProvider` - Dynamic API routing
- Context-scoped providers ensure tenant isolation

### Kubernetes Management

Manage Kubernetes resources as RealNet types:
- 20+ resource types: Pod, Deployment, Service, ConfigMap, Secret, StatefulSet, Job, CronJob, Ingress, and more
- Full CRUD operations through RealNet API
- In-cluster and kubeconfig support
- Automatic manifest generation

### AI Agents

MQTT-based distributed agent system:
- Create agents with command and status topics
- Bidirectional communication
- Active/inactive status tracking
- Script-based message handling

### WordPress Integration

Full WordPress CMS integration:
- Bidirectional content synchronization
- PHP plugin + Python client
- Multisite support
- REST API with JWT authentication
- Custom template system

## Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from source
python setup.py install

# Or via pip
pip install realnet
```

### Initialize Database

```bash
# Initialize database and create admin account
realnet server initialize

# Start the server
realnet server start
```

### Configuration

Create a `.env` file in the project root:

```bash
# Server
REALNET_SERVER_HOST=0.0.0.0
REALNET_SERVER_PORT=8080

# Database
REALNET_DB_TYPE=postgresql
REALNET_DB_HOST=localhost
REALNET_DB_PORT=5432
REALNET_DB_NAME=realnet
REALNET_DB_USER=realnet
REALNET_DB_PASS=realnet

# Storage (defaults to local)
REALNET_STORAGE_TYPE=local
REALNET_STORAGE_PATH=data

# Or use S3
# REALNET_STORAGE_TYPE=s3
# REALNET_STORAGE_S3_BUCKET=my-bucket
# REALNET_STORAGE_S3_KEY=AWS_KEY
# REALNET_STORAGE_S3_SECRET=AWS_SECRET
# REALNET_STORAGE_S3_REGION=us-east-1

# MQTT (optional, for agents and runners)
REALNET_MQTT_HOST=localhost
REALNET_MQTT_PORT=1883

# WordPress Integration (optional)
REALNET_WORDPRESS_URL=http://wordpress:8081
REALNET_WORDPRESS_ADMIN_USER=admin
REALNET_WORDPRESS_ADMIN_PASS=admin
REALNET_WORDPRESS_TOKEN=your-jwt-token

# OAuth
REALNET_APP_SECRET=your-secret-key
REALNET_URI=http://localhost:8080
REALNET_REDIRECT_URI=http://localhost:8080/oauth/callback
```

## Deployment Options

### Local Development

```bash
# Using SQLite (minimal setup)
REALNET_DB_TYPE=sqlite realnet server start

# Using PostgreSQL
realnet server initialize
realnet server start
```

### Docker

```bash
# Build image
./build_docker

# Run container
docker run -p 8080:8080 --env-file .env realnet:latest
```

### Kubernetes

```bash
# Deploy full stack (RealNet + PostgreSQL + Mosquitto MQTT)
kubectl apply -k k8s/base

# Or use deployment script
cd k8s
./deploy.sh

# On Windows
.\deploy.ps1

# Access the service
kubectl port-forward -n realnet svc/realnet 8080:8080
```

The Kubernetes deployment includes:
- RealNet service (LoadBalancer on port 8080)
- RealNet runner (MQTT message processor)
- PostgreSQL database with persistent storage
- Mosquitto MQTT broker
- RBAC configuration for K8s resource management

## Architecture

### Request Flow

1. **HTTP Request** → Flask app via `router_bp` blueprint
2. **Authentication** → OAuth2 token or session validation
3. **Context Creation** → Scoped to (org_id, account_id) with providers
4. **Endpoint Lookup** → Dynamic resolution from database
5. **Resource Invocation** → Polymorphic dispatch to resource class
6. **Provider Calls** → Data access through provider layer
7. **Response** → JSON or HTML (Jinja2 templates)

### Components

- **Shell/Command System** (`realnet/shell/`) - CLI interface
- **Provider Pattern** (`realnet/core/provider.py`) - Abstract data interfaces
- **Context System** (`realnet/cmd/server.py`) - Per-request provider factory
- **Resource Modules** (`realnet/resource/`) - HTTP verb handlers
- **SQL Providers** (`realnet/provider/sql/`) - SQLAlchemy ORM
- **HTTP Runner** (`realnet/runner/http/`) - Flask application
- **MQTT Runner** (`realnet/runner/mqtt/`) - Message queue processor
- **Kubernetes Client** (`realnet/resource/cluster/`) - K8s API integration
- **WordPress Client** (`realnet/provider/wordpress/`) - WP API integration

### Message Flow (WordPress Sync Example)

```
RealNet API → Create Page
    ↓
Publish MQTT Message → realnet/system topic
    ↓
Runner Pod Receives → Execute sync script
    ↓
WordPress API Call → Create WP page
    ↓
Result Published → realnet/system/result topic
```

## VirtualSpace Ecosystem

RealNet is the backend data layer for the VirtualSpace product stack:

**RealNet** → **RealScape** → **RealFusion**

- **RealNet** (this project): Entity CMS with type/instance system
- **RealScape**: 3D/AR/MR viewer and mixed reality browser
- **RealFusion**: Manufacturing workflow system with SAP Visual Enterprise integration

## API Examples

### Create a Type

```bash
curl -X POST http://localhost:8080/types \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product",
    "attributes": {
      "sku": {"type": "string"},
      "price": {"type": "number"},
      "description": {"type": "string"}
    }
  }'
```

### Create an Instance

```bash
curl -X POST http://localhost:8080/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Product",
    "attributes": {
      "sku": "PROD-001",
      "price": 29.99,
      "description": "Example product"
    }
  }'
```

### Query Items

```bash
# Get all items of a type
curl http://localhost:8080/items?type=Product \
  -H "Authorization: Bearer $TOKEN"

# Get item with children
curl http://localhost:8080/items/12345?children=true \
  -H "Authorization: Bearer $TOKEN"
```

### Manage Kubernetes Resources

```bash
# List all pods
curl http://localhost:8080/cluster/pods \
  -H "Authorization: Bearer $TOKEN"

# Create deployment
curl -X POST http://localhost:8080/cluster/deployments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @deployment.json
```

## Development

### Project Structure

```
realnet/
├── realnet/              # Main package
│   ├── cmd/             # Command implementations
│   ├── core/            # Core abstractions (provider, type system)
│   ├── provider/        # Provider implementations
│   │   ├── sql/        # PostgreSQL providers
│   │   ├── aws/        # S3 data provider
│   │   ├── generic/    # Local data provider
│   │   └── wordpress/  # WordPress client
│   ├── resource/        # Resource handlers (Items, Types, Files, etc.)
│   │   ├── cluster/    # Kubernetes resources
│   │   └── agents/     # AI agent resources
│   ├── runner/          # Background processors
│   │   ├── http/       # Flask application
│   │   └── mqtt/       # MQTT runner
│   ├── shell/          # CLI framework
│   └── static/         # Static files and initialization data
│       └── initialization/  # Type definitions (JSON)
├── k8s/                 # Kubernetes manifests
│   ├── base/           # Base deployment config
│   └── deploy.sh       # Deployment script
├── realnet-wordpress/   # WordPress plugin
├── docs/               # Documentation
└── setup.py            # Package configuration
```

### Adding New Features

**New Type (Data-Driven)**:
1. Add type definition to `static/initialization/*.json`
2. Run `realnet server initialize` to import
3. Types are versioned in JSON, not database migrations

**New Resource (Code-Driven)**:
1. Create resource class extending `Items` in `realnet/resource/`
2. Override HTTP verb methods (`get`, `post`, `put`, `delete`)
3. Register resource in context provider

**New Provider**:
1. Define interface in `realnet/core/provider.py`
2. Implement in `realnet/provider/`
3. Wire into `StandardContextProvider` in `cmd/server.py`

### Testing

Manual testing workflow:
```bash
# Initialize test database
realnet server initialize

# Start server
realnet server start

# Test API endpoints
curl http://localhost:8080/types
```

Automated testing is not currently implemented.

### Running Commands

```bash
# Get help
realnet -h

# Server commands
realnet server initialize
realnet server start

# Info commands
realnet info types
realnet info items

# MQTT Runner (requires MQTT broker)
realnet runner
```

## Key Files

- `realnet/realnet.py` - Main CLI entry point
- `realnet/cmd/server.py` - Server initialization and start
- `realnet/runner/http/app.py` - Flask application factory
- `realnet/runner/http/router.py` - Request routing and dispatch
- `realnet/core/config.py` - Configuration management
- `realnet/core/provider.py` - Provider interfaces
- `realnet/core/hierarchy.py` - Type system import/export
- `realnet/provider/sql/models.py` - Database schema (SQLAlchemy)
- `setup.py` - Package metadata and dependencies

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive development guide for Claude Code
- **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** - Project architecture and context
- **[RealNet_Integration_Guide.md](RealNet_Integration_Guide.md)** - Multi-provider integration patterns
- **[docs/realnet_type_system_guide.md](docs/realnet_type_system_guide.md)** - Type system deep dive

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit with descriptive messages (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Security Considerations

- Never commit `.env` file (in .gitignore)
- All secrets must be in environment variables
- OAuth2 redirect URIs must be whitelisted per client
- Multi-tenancy isolation is enforced at provider level
- Use `REALNET_ALLOW_HTTP=True` only for development (enables `OAUTHLIB_INSECURE_TRANSPORT`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Links

- **GitHub**: [https://github.com/virtual-space/realnet](https://github.com/virtual-space/realnet)
- **VirtualSpace**: [https://virtualspace.io](https://virtualspace.io)
- **Documentation**: See `docs/` directory
