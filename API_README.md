# User Management API

A production-ready RESTful API for user management built with FastAPI, SQLAlchemy, and deployed on Google Cloud Platform.

## Features

- **Complete CRUD Operations**: Create, Read, Update, Delete users
- **Pagination & Filtering**: Efficient data retrieval with query parameters
- **Input Validation**: Comprehensive validation using Pydantic v2
- **Async Database**: Non-blocking operations with SQLAlchemy 2.0
- **Health Checks**: Kubernetes-ready health endpoints
- **Structured Logging**: JSON logging with correlation IDs
- **Docker Support**: Multi-stage build for optimized images
- **Cloud Deployment**: Google Cloud Build and Cloud Run ready

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.109+ |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL / SQLite |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio |
| Container | Docker |
| Cloud | GCP Cloud Run |
| CI/CD | Google Cloud Build |

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- PostgreSQL (or use SQLite for development)

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd user-management-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run with SQLite (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users` | Create a new user |
| GET | `/api/v1/users` | List all users (paginated) |
| GET | `/api/v1/users/{id}` | Get user by ID |
| GET | `/api/v1/users/by-username/{username}` | Get user by username |
| GET | `/api/v1/users/by-email/{email}` | Get user by email |
| PUT | `/api/v1/users/{id}` | Update user |
| PATCH | `/api/v1/users/{id}` | Partial update user |
| DELETE | `/api/v1/users/{id}` | Delete user |
| POST | `/api/v1/users/{id}/activate` | Activate user |
| POST | `/api/v1/users/{id}/deactivate` | Deactivate user |
| GET | `/api/v1/users/statistics` | Get user statistics |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe |
| GET | `/health/detailed` | Detailed health info |

## API Examples

### Create User

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "active": true
  }'
```

### List Users with Filters

```bash
curl "http://localhost:8000/api/v1/users?page=1&page_size=10&role=user&active=true"
```

### Update User

```bash
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "role": "admin"
  }'
```

### Delete User

```bash
curl -X DELETE http://localhost:8000/api/v1/users/{user_id}
```

## User Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| username | String(50) | Unique username |
| email | String(255) | Unique email address |
| first_name | String(100) | User's first name |
| last_name | String(100) | User's last name |
| role | Enum | admin, user, guest |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| active | Boolean | Account status |

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py -v
```

## Deployment

### Google Cloud Build

The project includes a `cloudbuild.yaml` for automated CI/CD:

1. Builds Docker image
2. Runs tests
3. Deploys to Cloud Run

```bash
# Submit build manually
gcloud builds submit --config cloudbuild.yaml
```

### Required GCP Setup

1. Enable APIs:
   - Cloud Build
   - Cloud Run
   - Container Registry
   - Cloud SQL (if using PostgreSQL)

2. Create secrets in Secret Manager:
   - `database-url`: PostgreSQL connection string
   - `secret-key`: Application secret key

3. Grant necessary IAM permissions to Cloud Build service account

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── middleware.py        # Custom middleware
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   ├── routers/             # API endpoints
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── documentation/           # Phase documentation
├── Dockerfile
├── docker-compose.yml
├── cloudbuild.yaml
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection URL | sqlite+aiosqlite:///./app.db |
| SECRET_KEY | Application secret key | (required) |
| ENVIRONMENT | Runtime environment | development |
| DEBUG | Debug mode | false |
| LOG_LEVEL | Logging level | INFO |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |

## License

This project is created for the Software Engineer Challenge.
