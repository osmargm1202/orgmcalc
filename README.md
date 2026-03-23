# orgmcalc

Shared calculations API for orgm projects. FastAPI service providing projects, companies, engineers, calculations, and file management with PostgreSQL and R2 object storage.

## Quick Start

Requires Python 3.11+ and PostgreSQL.

```bash
# 1. Install dependencies with uv
cd /home/osmarg/Code/orgmcalc
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and other credentials

# 3. Run migrations and start server
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## Documentation

- **OpenAPI (Swagger UI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **API Documentation (Markdown)**: http://localhost:8000/externo/api-md

## Environment Variables

Copy `.env.example` to `.env` and configure all required variables:

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/orgmcalc` |
| `BASE_URL` | Public URL for OAuth callbacks | `http://localhost:8000` |

### Google OAuth (Required for write operations)

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 client secret |

Set up OAuth in [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
1. Create OAuth 2.0 credentials
2. Add authorized redirect URI: `{BASE_URL}/auth/google/callback`
3. Enable Google+ API

### Object Storage (R2/S3 - Required for file uploads)

| Variable | Description |
|----------|-------------|
| `R2_ENDPOINT_URL` | S3-compatible endpoint (e.g., Cloudflare R2) |
| `R2_ACCESS_KEY_ID` | Access key for object storage |
| `R2_SECRET_ACCESS_KEY` | Secret key for object storage |
| `R2_BUCKET_NAME` | Bucket name for uploads (default: `orgmcalc-uploads`) |

## Authentication Model

The API uses a **protected-write boundary** approach:

- **GET endpoints** (all read operations): **Public access** - No authentication required
- **POST, PATCH, DELETE endpoints** (write operations): **Require authentication**
- **File uploads** (POST /storage/*): **Require authentication**

### OAuth Flow

1. Visit `/auth/google` in browser to start OAuth
2. Authenticate with Google
3. Google redirects to `/auth/google/callback?code=...`
4. API returns bearer token in JSON response
5. Include token in all write requests:
   ```
   Authorization: Bearer <token>
   ```

## Development

### Code Quality

```bash
# Format and lint code
ruff check --fix src/
ruff format src/

# Type check
mypy src/

# Run tests
pytest tests/ -v
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/orgmcalc --cov-report=html

# Run specific test file
pytest tests/test_api_basic.py -v
```

### Database Migrations

Migrations are automatically run on startup. Manual migration:

```bash
# Run all pending migrations
python -m orgmcalc.db.migrate

# Check migration status (see code in src/orgmcalc/db/migrate.py)
```

Migration files are in `migrations/` directory and run in order by filename.

## Deployment

### Docker

Build and run with Docker:

```bash
# Build image
docker build -t orgmcalc:latest .

# Run container
docker run -d \
  --name orgmcalc \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e GOOGLE_CLIENT_ID=... \
  -e GOOGLE_CLIENT_SECRET=... \
  -e R2_ENDPOINT_URL=... \
  orgmcalc:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://orgmcalc:password@db:5432/orgmcalc
      - BASE_URL=http://localhost:8000
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - R2_ENDPOINT_URL=${R2_ENDPOINT_URL}
      - R2_ACCESS_KEY_ID=${R2_ACCESS_KEY_ID}
      - R2_SECRET_ACCESS_KEY=${R2_SECRET_ACCESS_KEY}
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=orgmcalc
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=orgmcalc
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

### Cloud Deployment

#### Railway/Render

1. Connect your GitHub repository
2. Set environment variables in dashboard
3. Deploy (Dockerfile will be used automatically)

#### Fly.io

```bash
# Install flyctl and login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set DATABASE_URL=...
fly secrets set GOOGLE_CLIENT_ID=...
# ... etc

# Deploy
fly deploy
```

### Database Setup

On first deployment:

```bash
# Create database (if not exists)
createdb orgmcalc

# Migrations run automatically on startup
# Or run manually:
docker exec orgmcalc python -m orgmcalc.db.migrate
```

### Import Data from orgmbt

To migrate existing data from orgmbt:

```bash
# Set source and target database URLs
export ORGMBT_DATABASE_URL="postgresql://user:pass@old-host:5432/orgmbt"
export ORGMCALC_DATABASE_URL="postgresql://user:pass@new-host:5432/orgmcalc"

# Preview changes (dry run)
export DRY_RUN=true
python scripts/import_from_orgmbt.py

# Import data
unset DRY_RUN
python scripts/import_from_orgmbt.py
```

This imports:
- Projects (proyectos)
- Companies (empresas)  
- Engineers (ingenieros)

The script is idempotent - safe to run multiple times.

### Smoke Testing

After deployment, verify everything works:

```bash
# Set target URL
export BASE_URL=https://your-api.example.com

# Run smoke tests
./scripts/smoke_test.sh
```

This tests:
- Health endpoint
- Documentation endpoints
- All CRUD routes (public reads, protected writes)
- Authentication requirements

## API Structure

Routes follow Spanish naming for compatibility (`/proyectos`, `/empresas`, `/ingenieros`).

### Main Endpoints

| Resource | List | Get | Create | Update | Delete |
|----------|------|-----|--------|--------|--------|
| Proyectos | GET /proyectos | GET /proyectos/{id} | POST /proyectos | PATCH /proyectos/{id} | DELETE /proyectos/{id} |
| Empresas | GET /empresas | GET /empresas/{id} | POST /empresas | PATCH /empresas/{id} | DELETE /empresas/{id} |
| Ingenieros | GET /ingenieros | GET /ingenieros/{id} | POST /ingenieros | PATCH /ingenieros/{id} | DELETE /ingenieros/{id} |
| Calculos | GET /proyectos/{id}/calculos | GET /proyectos/{id}/calculos/{cid} | POST /proyectos/{id}/calculos | PATCH ... | DELETE ... |
| Documentos | GET /proyectos/{id}/documentos | - | POST ... | - | DELETE ... |

All POST/PATCH/DELETE endpoints require authentication via Bearer token.

## Project Structure

```
orgmcalc/
├── main.py                  # Entry point
├── Dockerfile               # Container image
├── docker-compose.yml       # Local orchestration (create as needed)
├── .github/workflows/ci.yml # CI/CD pipeline
├── externo/
│   └── api.md              # API documentation source
├── scripts/
│   ├── smoke_test.sh       # Deployment verification
│   └── import_from_orgmbt.py  # Data migration
├── src/orgmcalc/
│   ├── api/
│   │   ├── app.py          # FastAPI application factory
│   │   ├── dependencies.py # Dependencies (DB, auth)
│   │   └── routes/         # HTTP route handlers
│   ├── db/
│   │   ├── connection.py   # Database pool management
│   │   └── migrate.py      # Migration runner
│   ├── models/             # Database models (if using ORM)
│   ├── repositories/       # Data access layer
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── storage/            # Object storage abstraction
│   └── config.py           # Application settings
├── migrations/             # Numbered SQL migrations
└── tests/                  # Test suite
    ├── conftest.py         # Test fixtures
    └── test_*.py           # Test files
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

1. **Lint**: ruff check and format validation
2. **Test**: pytest with PostgreSQL service
3. **Build**: Docker image build
4. **Push**: Push to GitHub Container Registry (main branch only)

## License

MIT
