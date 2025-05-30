# MCP Backend

The MCP (Model Control Panel) Backend is a FastAPI-based service that provides a robust API for managing machine learning models, workflows, and external database connections.

## Features

- MCP Definition Management
  - Create, read, update, and delete MCP definitions
  - Version control for MCP configurations
  - Support for various MCP types (LLM, Notebook, Script)

- Workflow Management
  - Workflow definition and execution
  - Real-time workflow monitoring via SSE
  - Workflow status tracking and result management

- External Database Integration
  - Support for multiple database types
  - Secure credential management
  - Database schema scanning

- Security
  - API key authentication
  - Rate limiting
  - Security headers
  - CORS configuration

- Monitoring & Logging
  - Performance metrics
  - Action logging
  - Error tracking
  - Health checks

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker (optional)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-backend.git
   cd mcp-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Update the `.env` file with your configuration:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/mcpdb
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key-here
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development

```bash
uvicorn mcp.api.main:app --reload
```

### Production

```bash
uvicorn mcp.api.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t mcp-backend .
docker run -p 8000:8000 mcp-backend
```

## API Documentation

Once the application is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- API Reference: See `docs/api_reference.md`

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=mcp
```

## Project Structure

```
mcp_project_backend/
├── alembic/              # Database migrations
├── docs/                 # Documentation
├── mcp/
│   ├── api/             # API routes and dependencies
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── external_db/     # External database connectors
│   └── schemas/         # Pydantic models
├── tests/               # Test suite
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Documentation

- [API Reference](docs/api_reference.md)
- [Security Enhancements](docs/security_enhancements.md)
- [Performance Monitoring](docs/performance_monitoring.md)
- [Error Handling](docs/error_handling.md)
- [API Key Management](docs/api_key_management.md)
- [Action Logging](docs/action_logging.md)
- [Workflow Engine](docs/workflow_engine_service.md)
- [Dashboard Implementation](docs/dashboard_implementation.md)
- [Entity Routes](docs/entity_routes.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 