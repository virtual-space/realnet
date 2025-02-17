# System Patterns

## Architecture Overview

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

## Implementation Guidelines

1. Command Implementation
- Use cmd/ directory structure
- Implement command handlers
- Follow CLI patterns
- Handle errors consistently

2. Provider Implementation
- Follow provider interface
- Implement storage backends
- Handle transactions
- Manage connections

3. Resource Implementation
- Define resource types
- Handle file operations
- Manage templates
- Process forms

4. Runner Implementation
- Handle protocols
- Serve static files
- Process templates
- Manage services

These patterns guide development and ensure system consistency.
