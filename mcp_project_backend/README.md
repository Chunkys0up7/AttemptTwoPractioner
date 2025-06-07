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

## Backend API Documentation

### Authentication & User Management

- **POST /auth/register**: Register a new user
- **POST /auth/login**: Obtain JWT access token
- **GET /auth/me**: Get current user info
- **GET /users**: List users (admin only)
- **PUT /users/{user_id}**: Update user (admin or self)
- **DELETE /users/{user_id}**: Delete user (admin only)

**Example:**

```json
POST /auth/register
{
  "email": "user@example.com",
  "password": "string",
  "full_name": "User Name",
  "role_name": "Editor"
}
```

### RBAC & Session Management

- Role-based access enforced on protected endpoints
- Audit logging for login, logout, and sensitive actions

### Orchestration (Prefect)

- **POST /orchestration/register**: Register workflow (admin)
- **POST /orchestration/trigger**: Trigger workflow
- **GET /orchestration/status/{run_id}**: Get workflow status
- **POST /orchestration/log-event**: Log workflow event
- **POST /orchestration/trace**: Log trace data
- **POST /orchestration/elk-log**: Log to ELK stack

### Metrics & Monitoring

- **POST /metrics/performance**: Log model performance (admin)
- **POST /metrics/custom**: Log custom metric (admin)

### API Security

- CORS enabled (configurable)
- Rate limiting scaffolded
- HTTPS enforcement scaffolded
- Input validation via Pydantic

---

For more details and example requests, see the code in `mcp/api/routers/` and `mcp/core/`.

## Documentation Update Best Practices

- Update this README and relevant docs for every new feature, bugfix, or architectural change.
- For new or changed API endpoints, update `docs/api_reference.md` with details and examples.
- For security, performance, or error handling changes, update the corresponding doc in `docs/`.
- When adding new tests, update the testing section in this README and the checklist.
- Annotate major changes in the changelog below.

## Changelog

- [YYYY-MM-DD] Documentation best practices and changelog section added.
- [YYYY-MM-DD] All outstanding technical tasks completed and documented.
- [YYYY-MM-DD] Initial backend documentation created.

## Database Schema Updates (June 2025)

- Added `template_shares` table for workflow template sharing and permissions.
- Added `metrics` table for storing performance and usage metrics.
- Added `alerts` table for threshold-based and manual alerts.
- Added `workflow_step_executions` table for detailed workflow step tracking.
- Updated `workflow_definitions` and `workflow_runs` schema to match models.

The schema is now fully aligned with the backend models and supports advanced monitoring, alerting, and sharing features.
