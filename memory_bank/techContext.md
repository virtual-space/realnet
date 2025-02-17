# Technical Context

## Technology Stack

### Core Technologies
- Python 3.x
- PostgreSQL Database
- AWS Services (S3, SQS)
- HTTP/REST APIs
- Docker/Kubernetes

### Key Dependencies
- PostgreSQL client
- AWS SDK
- Cryptography module
- HTTP server
- Template engine

## Development Setup

### Project Structure
```
realnet/
├── cmd/           # Command line interface
│   ├── create.py
│   ├── get.py
│   ├── info.py
│   ├── runner.py
│   └── server.py
├── core/          # Core functionality
│   ├── acl.py
│   ├── config.py
│   ├── hierarchy.py
│   ├── provider.py
│   └── type.py
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
│   └── ...
├── runner/        # Protocol runners
│   ├── http/
│   └── sqs/
├── shell/         # Shell interface
└── templates/     # HTML templates
```

### Environment Setup
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

## Technical Constraints

1. Database
- PostgreSQL compatibility
- Transaction support
- Connection pooling
- Schema management

2. Storage
- S3 bucket access
- File handling
- MIME type support
- Upload/download management

3. Security
- Token authentication
- Environment variables
- Secure storage
- Access control

4. Deployment
- Docker support
- Kubernetes compatibility
- Environment isolation
- Service configuration

## Dependencies

### System Requirements
- Python 3.x
- PostgreSQL
- gcc/g++
- Development tools

### Python Dependencies
- setuptools-rust
- cryptography
- database drivers
- AWS SDK
- HTTP server

### External Services
- PostgreSQL database
- AWS S3 storage
- AWS SQS queue
- (Optional) ChatGPT API

### Development Tools
- Python virtual environment
- Database client
- AWS CLI
- Docker/Kubernetes CLI

This context guides technical implementation and infrastructure decisions.
