## Requirements

For local development:

- Python 3.13+
- Docker Desktop
- Git

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
APP_NAME=Network Incident Tracker API
DEBUG=true
TESTING=false
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/incidents_db
SECRET_KEY=change-this-to-a-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

For Docker Compose, the API service overrides `DATABASE_URL` internally to connect to the database service:

```env
postgresql+psycopg://postgres:postgres@db:5432/incidents_db
```

## Run with Docker Compose

Build and start the API and PostgreSQL database:

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health/db
```

Stop containers:

```bash
docker compose down
```

## Run Tests

Run all tests:

```bash
python -m pytest -q
```

Expected result:

```text
15 passed
```

## Main Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current authenticated user |

### Assets

| Method | Endpoint | Description |
|---|---|---|
| POST | `/assets/` | Create an asset |
| GET | `/assets/` | List assets |
| GET | `/assets/{asset_id}` | Get asset by ID |
| PATCH | `/assets/{asset_id}` | Update asset |
| DELETE | `/assets/{asset_id}` | Delete asset |

Example asset:

```json
{
  "hostname": "srv-web-01",
  "ip_address": "192.168.1.10",
  "owner": "network-team",
  "environment": "production"
}
```

### Incidents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/incidents/` | Create an incident |
| GET | `/incidents/` | List incidents |
| GET | `/incidents/{incident_id}` | Get incident by ID |
| PATCH | `/incidents/{incident_id}` | Update incident |
| DELETE | `/incidents/{incident_id}` | Delete incident |

Example incident:

```json
{
  "title": "High CPU usage on web server",
  "description": "CPU usage exceeded 95% for more than 10 minutes",
  "severity": "high",
  "asset_id": 1,
  "assigned_to": null
}
```

Available severities:

```text
low
medium
high
critical
```

Available statuses:

```text
open
in_progress
closed
```

### Incident Filters

```http
GET /incidents/?severity=critical
GET /incidents/?status=open
GET /incidents/?asset_id=1
GET /incidents/?severity=high&status=open&skip=0&limit=10
```

### Stats

| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats/summary` | Get incident summary statistics |

Example response:

```json
{
  "total_incidents": 3,
  "open_incidents": 1,
  "in_progress_incidents": 1,
  "closed_incidents": 1,
  "critical_incidents": 1
}
```

## Database Migrations

Apply all migrations:

```bash
python -m alembic upgrade head
```

Create a new migration after changing models:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Check current migration:

```bash
python -m alembic current
```

## Development Notes

- The API uses JWT Bearer authentication.
- Passwords are stored as hashes, never as plain text.
- PostgreSQL is used as the main database.
- Alembic is responsible for database schema changes.
- Tests use an isolated SQLite database through dependency overrides.
- Docker Compose runs both the API and PostgreSQL.

## Roadmap

Planned improvements:

- Add role-based permissions for `admin` and `analyst`
- Add comments to incidents
- Add evidence attachments
- Add GitHub Actions for automated tests
- Add better error response models
- Add more detailed statistics
- Add deployment instructions

## License

This project is currently for portfolio and learning purposes.