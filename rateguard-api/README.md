# RateGuard API

A production-style backend project that protects APIs during burst traffic using Redis sliding-window rate limiting, API key authentication, and PostgreSQL request logging.

## Highlights

- Dual rate limiting: per API key and per client IP
- Sliding-window implementation on Redis sorted sets
- API key auth via `X-API-Key`
- Persistent request logging in PostgreSQL
- Liveness/readiness health checks for deployment platforms
- Dockerized stack (`api`, `redis`, `postgres`)

## Tech Stack

- Python 3.12
- FastAPI + Uvicorn
- Redis
- PostgreSQL
- Docker / Docker Compose
- Pytest

## Project Structure

```text
rateguard-api/
├── app/
│   ├── config.py
│   ├── main.py
│   ├── db/
│   │   ├── postgres.py
│   │   └── redis_client.py
│   ├── middleware/
│   │   └── auth.py
│   └── services/
│       ├── logger.py
│       └── rate_limiter.py
├── sql/
│   └── init.sql
├── tests/
│   ├── test_config_and_auth.py
│   └── test_rate_limiter.py
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## API Endpoints

- `GET /health/liveness`  
  Returns `{"status": "alive"}` when the API process is running.

- `GET /health/readiness`  
  Returns `{"status": "ready"}` when Redis and PostgreSQL are reachable.

- `GET /api/v1/limited`  
  Protected endpoint. Requires `X-API-Key` header and enforces rate limits.

Example request:

```bash
curl -H "X-API-Key: local-dev-key" http://localhost:8000/api/v1/limited
```

## Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `APP_NAME` | FastAPI app title | `RateGuard API` |
| `APP_ENV` | Environment label | `development` |
| `API_PREFIX` | Versioned API prefix | `/api/v1` |
| `RATE_LIMIT_PER_MINUTE` | Max requests/window per API key and IP | `60` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://postgres:postgres@postgres:5432/rateguard` |
| `API_KEYS` | Comma-separated valid API keys | `local-dev-key` |

## Run With Docker

```bash
cp .env.example .env
docker compose up --build
```

Then test:

```bash
curl http://localhost:8000/health/liveness
curl http://localhost:8000/health/readiness
curl -H "X-API-Key: local-dev-key" http://localhost:8000/api/v1/limited
```

## Run Locally (No Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

You still need Redis and PostgreSQL running locally and matching `.env` values.

## Testing

```bash
pytest
```

## Resume-Friendly Impact

- Prevented API overload during burst traffic with Redis-based sliding windows.
- Enabled secure client usage tracking through API key auth + PostgreSQL logging.
- Improved deployment reliability with containerization and health probes.
