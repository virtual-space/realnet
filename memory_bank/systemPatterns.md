# System Patterns

## Architecture Overview

### WordPress Deployment Pattern

1. Component Structure
```mermaid
graph TD
    A[WordPress Pod] --> B[MySQL Pod]
    A --> C[Plugin ConfigMap]
    A --> D[Persistent Volume]
    B --> E[DB Secret]
    A --> F[API Secret]
    A --> G[Ingress]

    subgraph Initialization Flow
        H[Install Packages] --> I[Configure WP-CLI]
        I --> J[Setup Database]
        J --> K[Install WordPress]
        K --> L[Configure Multisite]
        L --> M[Install Plugins]
    end
```

2. Configuration Pattern
```mermaid
graph TD
    A[Secrets] --> B[Database Credentials]
    A --> C[API Tokens]
    D[ConfigMaps] --> E[Plugin Files]
    D --> F[WordPress Settings]
    G[Environment] --> H[Database Config]
    G --> I[WordPress Config]
```

3. Plugin Integration Pattern
```mermaid
graph TD
    A[ConfigMap] --> B[Temporary Mount]
    B --> C[Copy to Plugin Dir]
    C --> D[Set Permissions]
    D --> E[WordPress Activation]
```

4. Startup Sequence
```mermaid
graph TD
    A[Install Tools] --> B[Wait for Database]
    B --> C[Start WordPress]
    C --> D[Configure Site]
    D --> E[Install Plugins]
    E --> F[Update Settings]
```

### Core Components

1. Command System
```mermaid
graph TD
    A[CLI Entry] --> B[Command Handlers]
    B --> C[Server Commands]
    B --> D[Auth Commands]
    B --> E[Info Commands]
```

2. Provider System
```mermaid
graph TD
    A[Core Provider] --> B[SQL Provider]
    A --> C[AWS Provider]
    A --> D[Generic Provider]
    A --> E[File Provider]
```

3. Resource System
```mermaid
graph TD
    A[Resource Types] --> B[Files]
    A --> C[Forms]
    A --> D[Views]
    A --> E[Applications]
```

4. Runner System
```mermaid
graph TD
    A[Runner Base] --> B[HTTP Runner]
    A --> C[SQS Runner]
    B --> D[Static Files]
    B --> E[Templates]
```

### Design Patterns

1. Command Pattern
- Centralized command handling
- Modular command implementation
- Consistent CLI interface
- Command validation

2. Provider Pattern
- Abstract provider interface
- Multiple backend support
- Storage agnostic operations
- Consistent data access

3. Resource Pattern
- Type-based resources
- File handling
- Form management
- View rendering

4. Runner Pattern
- Protocol abstraction
- Service integration
- Template handling
- Static file serving

## Component Relationships

### Command Flow
```mermaid
graph TD
    A[CLI Input] --> B[Command Parser]
    B --> C[Command Handler]
    C --> D[Core Logic]
    D --> E[Provider/Runner]
```

### Data Flow
```mermaid
graph TD
    A[Request] --> B[Runner]
    B --> C[Resource]
    C --> D[Provider]
    D --> E[Storage]
```

### Authentication Flow
```mermaid
graph TD
    A[Request] --> B[Token Check]
    B --> C[Auth Validation]
    C --> D[Access Grant]
    D --> E[Resource Access]
```

## Resource Creation Pattern

1. Resource Implementation
```mermaid
graph TD
    A[Create Python Class] --> B[Inherit from Type]
    B --> C[Add Provider Parameter]
    C --> D[Call super.__init__]
    D --> E[Implement Methods]
    E --> F[Handle Errors]
```

2. Resource Definition
```mermaid
graph TD
    A[Create JSON Type] --> B[Set Module Attribute]
    B --> C[Add Basic Attributes]
    C --> D[Add to Resource JSON]
    D --> E[Add to Initialization]

    subgraph Type System Dependencies
        F[Core Types] --> G[Resource Types]
        G --> H[App Types]
        H -.-> |Can Reference| G
        G -.- x|Avoid Reference| H
    end

    subgraph View Organization
        I[Resource Type] --> J[Basic Attributes]
        K[App Type] --> L[Views]
        L --> M[Query Resource Types]
        M -.-> I
        I -.- x|No Views| L
    end
```

Key Rules:
- Resource types go in domain JSONs (kubernetes.json)
  * Basic attributes only (icon, module)
  * No views or queries
- App types go in domain_apps.json
  * All views and queries
  * Can reference resource types
- General app types in apps.json
- This separation prevents circular dependencies

3. Resource Integration
```mermaid
graph TD
    A[Add to server.py] --> B[Create Endpoint]
    B --> C[Configure Access]
    C --> D[Test Resource]
```

## App Creation Pattern

1. App Structure
```mermaid
graph TD
    A[App Type] --> B[Views]
    B --> C[Menu Items]
    C --> D[Resource Types]
    D --> E[Query Config]
```

2. App Definition Steps
```mermaid
graph TD
    A[Define Base Type] --> B[Configure Views]
    B --> C[Add Menu Items]
    C --> D[Set Icons]
    D --> E[Configure Queries]
```

3. App Integration
```mermaid
graph TD
    A[Add to JSON] --> B[Create Instance]
    B --> C[Add to Items]
    C --> D[Set Permissions]
```

## Implementation Guidelines

1. Resource Implementation
- Create resource class in resource/
- Inherit from Type base class
- Implement required methods
- Add error handling
- Configure provider

2. JSON Definition
- Define types in initialization/
- Set module and icon attributes
- Configure views and queries
- Add resource endpoints
- Set up app integration

3. App Creation
- Define app type
- Configure views and menus
- Add app instance
- Set icons and queries
- Handle permissions

4. Integration Steps
```mermaid
graph TD
    A[Core System Files] --> B[Resource Type Files]
    B --> C[Apps and Access Files]
    C --> D[Create Endpoints]
    D --> E[Configure Access]
    E --> F[Test Functionality]
```

Key Initialization Order:
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

3. Apps and Access Files
   - apps.json: App definitions
   - access.json: Access control

This order ensures dependencies exist before they're referenced.

These patterns guide development and ensure system consistency.
