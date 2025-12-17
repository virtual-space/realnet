# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**RealNet** is an open-source Web 2.0 entity-based CMS that serves as the backend engine for the VirtualSpace ecosystem. It provides JSON schema object feeds and acts as the data/logic layer for:
- **RealScape** - 3D/AR/MR viewer and mixed reality browser
- **RealFusion** - Manufacturing workflow system with SAP Visual Enterprise integration

RealNet is built on Flask and SQLAlchemy with PostgreSQL, featuring:
- Entity-based type system (types define schemas, instances are data)
- Multi-tenancy (organizations/accounts)
- OAuth2 authentication
- Hierarchical item storage with spatial support (PostGIS)
- Flexible file storage (local filesystem by default, AWS S3 optional)
- Kubernetes resource management (20+ resource types)
- AI agents via MQTT messaging
- WordPress CMS integration
- RESTful API with dynamic endpoint registration
- Digital twin and mixed reality capabilities

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
. ./venv/bin/activate

# Install from source
python setup.py install

# Or install via pip
pip install realnet
pip install pyopenssl --upgrade
```

### Server Operations
```bash
# Initialize the database and create admin account
realnet server initialize

# Start the server
realnet server start

# Get help on available commands
realnet -h
```

### Package Building
```bash
# Build pip package
./build_package

# Build Docker image
./build_docker
```

## Configuration

The application requires a `.env` file in the project root. Key environment variables:

- `REALNET_SERVER_HOST` / `REALNET_SERVER_PORT` - Server binding
- `REALNET_DB_TYPE` - Database type (postgresql or sqlite)
- `REALNET_DB_USER` / `REALNET_DB_HOST` / `REALNET_DB_PASS` / `REALNET_DB_PORT` / `REALNET_DB_NAME` - Database connection
- `REALNET_STORAGE_TYPE` - Storage backend (local or s3, defaults to local)
- `REALNET_STORAGE_PATH` - Local storage directory (defaults to 'data')
- `REALNET_STORAGE_S3_BUCKET` / `REALNET_STORAGE_S3_KEY` / `REALNET_STORAGE_S3_SECRET` / `REALNET_STORAGE_S3_REGION` - AWS S3 configuration (optional)
- `REALNET_MQTT_HOST` / `REALNET_MQTT_PORT` - MQTT broker configuration for agents and runners
- `REALNET_WORDPRESS_URL` / `REALNET_WORDPRESS_ADMIN_USER` / `REALNET_WORDPRESS_ADMIN_PASS` / `REALNET_WORDPRESS_TOKEN` - WordPress integration
- `REALNET_SQS_URL` - AWS SQS queue URL
- `REALNET_APP_SECRET` - Flask secret key for sessions
- `REALNET_URI` / `REALNET_REDIRECT_URI` / `REALNET_MOBILE_REDIRECT_URI` - OAuth redirect URIs

All configuration is loaded via `realnet/core/config.py` using python-dotenv.

## Architecture

### Request Flow

All HTTP requests follow this unified path:

1. **Routing** - Flask app receives request at `router_bp` blueprint (router.py:349-466)
   - Single catch-all route: `/<endpoint_name>/<path:path>`
   - Special routes: `/signin`, `/register`, `/oauth/token`, `/<org>/login`

2. **Authentication** - Two modes:
   - OAuth2 token validation via `@require_oauth` decorator
   - Session-based auth via Flask sessions (session['id'])
   - Public endpoints bypass auth: `/public/apps`, `/public/types`, `/public/items`

3. **Context Creation** - Per-request context factory:
   - `StandardContextProvider.context(org_id, account_id)` creates Context
   - Context wires up 15+ provider instances scoped to org/account
   - Provides unified API: `context.get_types()`, `context.get_items()`, etc.

4. **Endpoint Lookup** - Dynamic endpoint resolution:
   - Endpoints are themselves items stored in the database
   - Context finds matching endpoint by name
   - Endpoint contains resource type and configuration

5. **Resource Invocation** - Polymorphic dispatch:
   - Endpoint delegates to resource class (Items, Types, Files, etc.)
   - HTTP method mapped to resource method: GET→get(), POST→post(), etc.
   - Special method override: `_method` parameter in request

6. **Provider Calls** - Data access through providers:
   - Resource uses context providers (type/item/data) to access storage
   - All SQL queries go through provider layer
   - Multi-tenancy enforced at provider level via org_id/account_id

7. **Response Rendering** - Content negotiation:
   - JSON: `application/json` → serialized dicts
   - HTML: `text/html` → Jinja2 templates
   - Binary: File downloads for `/data` paths

### Core Components

1. **Shell/Command System** (`realnet/shell/`)
   - Command-line interface built on argparse
   - `Shell` class provides nested command structure with subparsers
   - Main commands: `info`, `get`, `create`, `runner`, `server`
   - Commands use `ProtoCmd` and `ProtoShell` base classes

2. **Provider Pattern** (`realnet/core/provider.py`)
   - Abstract base classes define interfaces for all data operations
   - Providers are dependency-injected into Context objects
   - Key providers:
     - `TypeProvider` - Manages type definitions and instances
     - `ItemProvider` - Handles hierarchical item CRUD operations
     - `DataProvider` - Storage operations (S3/local files)
     - `ContextProvider` - Factory that creates contexts with provider implementations
     - `EndpointProvider`, `ResourceProvider`, `ImportProvider`
     - Organization, client, and role providers

3. **Context System** (`realnet/cmd/server.py:20-38`)
   - `StandardContextProvider` is the concrete ContextProvider implementation
   - Creates a `Context` object per request with all provider instances
   - Context is scoped to `(org_id, account_id)` for tenant isolation
   - All SQL providers receive org_id/account_id in constructor
   - Provides unified interface hiding provider complexity

4. **Resource Modules** (`realnet/resource/`)
   - Base `Resource` class (core/type.py) defines HTTP verbs as abstract methods
   - `Items` extends Resource - base class for most resource types
   - Inheritance chain: `Resource` → `Items` → `Types`/`Files`/`Apps`/etc.
   - Resources handle both HTML (Jinja2 templates) and JSON rendering
   - Content negotiation via Accept header or query parameters

5. **SQL Providers** (`realnet/provider/sql/`)
   - Single SQLAlchemy engine and session in `models.py:32-34`
   - ORM models: Org, Account, Group, Role, Authenticator, OAuth2 entities
   - `models.py` includes Authlib OAuth2 mixins for token management
   - `org.py` / `orgs.py` - Multi-tenant organization management
   - `type.py` - Type system backed by PostgreSQL (types stored as JSON)
   - `postgres/item.py` - Hierarchical item storage with PostGIS support (GeoAlchemy2)
   - `init.py` - Database initialization via `SqlInitProvider.initialize()`
   - `utility.py` - Common SQL operations and queries

6. **HTTP Runner** (`realnet/runner/http/`)
   - `app.py:18-50` - Flask app factory `create_app(contextProvider)`
   - Single blueprint: `router_bp` handles all routes dynamically
   - `auth.py` - OAuth2 configuration using Authlib (authorization code flow)
   - `router.py` - Mega-router with authentication, endpoint dispatch, and special routes
   - Supports delegated authentication (Google, etc.) via Authenticator entities
   - Runs via Gunicorn in production (dependency in setup.py:50)

### Entity-Based Type System

RealNet is an entity CMS where **everything is data**. The type system (`realnet/core/type.py` and `realnet/core/hierarchy.py`) is central to the entire architecture:

**Key Concepts:**
- **Types** - Define schemas/structure with attributes (like classes)
- **Instances** - Concrete data conforming to a type (like objects)
- **Items** - Hierarchical wrapper around instances providing tree structure
- **Attributes** - JSON key-value data on types/instances

**Type Inheritance:**
- Types can inherit from base types (single inheritance)
- Derived types inherit attributes from their base
- Type hierarchy: `Type.base` references parent type
- Instances inherit structure from their type

**Bootstrap Process:**
- On initialization, core types are imported from JSON files in `static/initialization/`
- Import order matters: `core.json` → `controls.json` → `views.json` → `forms.json` → `geometry.json` → `apps.json` → `access.json`
- `import_structure_from_resource()` (hierarchy.py) handles dependency resolution
- Types are created first, then instances, respecting dependencies

**Schema Preferences:**
- Types define logical relationships
- Instances created dynamically for data
- Only app types have views unless specifically required
- JSON schema object feeds power RealScape and RealFusion clients

### Multi-Tenancy

- Organizations (`org`) are the top-level tenant boundary
- Accounts belong to organizations
- Each context is scoped to an org_id and account_id
- Providers enforce tenant isolation at the data layer

### Authentication Flow

1. OAuth2 authorization code flow
2. Client credentials stored per organization
3. JWT tokens for API access
4. ACL system based on roles and permissions

## Key Files

- `realnet/realnet.py` - Main CLI entry point, registers all commands
- `realnet/__main__.py` - Python module entry point
- `realnet/cmd/server.py` - Server initialization and start commands
- `realnet/runner/http/app.py` - Flask application factory
- `realnet/core/config.py` - Configuration management
- `realnet/core/provider.py` - Provider interface definitions
- `realnet/core/hierarchy.py` - Type system import/export logic
- `realnet/provider/sql/models.py` - Database schema
- `setup.py` - Package metadata and dependencies

## VirtualSpace Ecosystem Integration

RealNet serves as the backend entity engine in the VirtualSpace product stack:

**Product Flow:** RealNet → RealScape → RealFusion

- **RealNet** provides the data layer:
  - Entity CMS with type/instance system
  - JSON schema object feeds via RESTful API
  - Multi-tenant organization management
  - OAuth2 authentication for clients

- **RealScape** (separate product) consumes RealNet:
  - 3D/AR/MR viewer and mixed reality browser
  - Visualizes digital twins from RealNet entities
  - Renders spatial data (PostGIS geometries)
  - Uses RealNet authentication

- **RealFusion** (separate product) builds on RealScape:
  - Manufacturing workflow system
  - SAP Visual Enterprise integration
  - EBOM import, MBOM generation
  - Visual work instructions
  - Consumes RealNet types for workflow definitions

**File Format Support:**
- GLTF for 3D models (pygltflib, trimesh in setup.py)
- HEIF image format support (pillow-heif)
- Spatial geometries (Shapely, GeoAlchemy2)
- Binary data storage (local filesystem by default, S3 optional)

## Data Flow Example

Typical RealNet API request (e.g., `GET /items/12345`):

1. HTTP request arrives at Flask app via `router_bp`
2. `@require_oauth` decorator validates token or checks session
3. `router()` function extracts endpoint name ("items") and path ("12345")
4. Context created: `contextProvider.context(account.org.id, account.id)`
5. Endpoint lookup: `context.get_endpoint(context, "items")`
6. Resource invocation: `endpoint.invoke(context, endpoint, "get", args, path)`
7. Items resource: `items.get(module=context, endpoint, args, path="12345")`
8. Provider calls: `context.get_item("12345", children=True)`
9. SQL provider: `PostgresItemProvider.get_item()` queries database
10. Data enrichment: Check for `/data` files via S3DataProvider
11. Response rendering:
    - JSON: `item.to_dict()` → jsonify
    - HTML: Jinja2 template with item data
12. Response sent to client (RealScape, RealFusion, or browser)

## Testing

This codebase does not currently have automated tests. Manual testing is performed via:
- Running `realnet server initialize` to setup test database
- Using `realnet server start` to verify server functionality
- Testing API endpoints with HTTP clients

## Database Migrations

Database schema changes are handled via:
1. Modify SQLAlchemy models in `realnet/provider/sql/models.py`
2. Run `realnet server initialize` which creates all tables via `db.create_all()`
3. Note: This does not support incremental migrations - fresh initialization only

**Important:** The database schema is coupled to the entity type system. Core types defined in `static/initialization/*.json` must align with ORM models and provider implementations.

## Development Considerations

**When Adding New Features:**
- Consider whether to implement as new type (data-driven) or code (feature)
- Entity CMS philosophy: prefer types/instances over hardcoded logic
- New endpoints should be entities in database, not Flask routes
- New resource types extend `Items` and override specific methods

**When Modifying Types:**
- Check initialization JSON files in `static/initialization/`
- Understand dependency order in `server.py:139-145`
- Test with `realnet server initialize` to ensure clean bootstrap
- Types are version-controlled in JSON, not in database migrations

**When Working with Spatial Data:**
- PostGIS extension required in PostgreSQL
- Use GeoAlchemy2 WKBElement for geometry columns
- Shapely for geometry manipulation
- Coordinate systems matter - be explicit about SRID

**When Debugging:**
- SQLAlchemy echo mode enabled (models.py:32) - check logs for SQL
- Flask debug mode controlled by `app.run()` third parameter
- Logger level set to INFO in router.py:22
- Check `.env` file for configuration issues

**Security Considerations:**
- NEVER commit `.env` file (in .gitignore)
- All secrets must be in environment variables
- OAuth2 redirect URIs must be whitelisted per client
- Multi-tenancy isolation is critical - test org boundaries
- INSECURE_TRANSPORT only for development (`REALNET_ALLOW_HTTP=True`)

**Performance Notes:**
- Single SQLAlchemy session shared globally (models.py:34)
- No connection pooling configuration visible
- S3 uploads use presigned URLs when `REALNET_USE_S3_UPLOAD_URL=True`
- No caching layer - all requests hit database
- PostGIS queries can be expensive - consider spatial indexes

## Common Patterns

**Provider Pattern:**
- All providers follow ABC pattern with abstract methods in `core/provider.py`
- Concrete implementations in `provider/sql/`, `provider/aws/`, `provider/generic/`
- Providers injected into Context for dependency inversion
- All database access goes through provider interfaces, never direct ORM queries in resources

**Resource Inheritance:**
- Resource modules inherit from base classes and override specific HTTP verb methods
- Most resources extend `Items` which extends `Resource`
- Template rendering and JSON serialization handled by base classes
- Override `get_items()`, `get_item()`, `get_template()` for custom behavior

**Configuration:**
- All configuration comes from environment variables via `.env` file
- Never hardcode credentials, URLs, or secrets
- `Config` class (core/config.py) provides typed access to env vars
- Missing required env vars will cause runtime errors

**Multi-Tenancy:**
- Every context scoped to `(org_id, account_id)` tuple
- Org isolation enforced at provider level in SQL queries
- Never trust client-provided org_id - always use authenticated account's org
- Public endpoints are special case with no org/account context

**Entity CMS Patterns:**
- Types are schemas, instances are data - this is fundamental
- Items provide hierarchical structure (parent/child relationships)
- Attributes are JSON dicts - flexible schema
- Type inheritance via `base` property
- Instances always reference a type

**JSON Structure:**
- Types/instances serialize via `to_dict()` method
- Attributes merged from type hierarchy (base attributes + own attributes)
- Circular references avoided in serialization
- Import/export uses JSON files with specific structure

**Authentication:**
- Dual mode: OAuth2 tokens (for API clients) or sessions (for web UI)
- OAuth2 uses Authlib with authorization code flow
- Clients and tokens stored per organization
- Delegated auth (Google, etc.) creates accounts via `external_id`

**URL Routing:**
- Pattern: `/<endpoint_name>/<path>`
- Endpoint name matches database endpoint entity
- Path can be item ID or nested path like `12345/children`
- Special paths: `/data` for file downloads, `/<org>/login` for auth

**Database Models:**
- All tables have String(36) UUID primary keys
- Enums for fixed vocabularies (AccountType, OrgRoleType, etc.)
- JSON columns for flexible attributes
- Foreign keys with CASCADE delete for org cleanup
- GeoAlchemy2 for spatial data (PostGIS required)
