# RateGuard API

RateGuard API is a backend service built to keep APIs stable under burst traffic.
It combines Redis sliding-window rate limiting, API key authentication, and PostgreSQL logging so systems can stay responsive, fair, and observable when request volume spikes.

## Why This Project Exists

Modern APIs often fail in two predictable ways:

- Sudden traffic bursts overwhelm application threads and downstream services.
- A small number of aggressive clients can starve everyone else.

RateGuard addresses both by placing a lightweight protection layer in front of sensitive endpoints.  
Instead of waiting for overload and reacting after incidents, this service enforces limits proactively.

## Real-World Effect

Using this pattern in production-style systems typically leads to:

- Better uptime during traffic spikes by rejecting excess requests early.
- Fairness across tenants/clients through per-key and per-IP controls.
- Clear incident debugging from structured request logs in PostgreSQL.
- Safer deployments via health checks and containerized dependencies.

In short: RateGuard turns unpredictable traffic into controlled, measurable behavior.

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
  Confirms the API process is running.

- `GET /health/readiness`  
  Confirms Redis and PostgreSQL are reachable and queryable.

- `GET /api/v1/limited`  
  Protected endpoint requiring `X-API-Key`; enforces both per-user and per-IP limits.

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

To validate rate limiting quickly, run the protected endpoint repeatedly and observe `429 Too Many Requests` after the configured threshold.

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

## Design Decisions

- Redis sorted sets for sliding windows: supports precise time-based limiting rather than coarse fixed windows.
- Per-key + per-IP checks: protects against both key abuse and anonymous/high-volume IP abuse.
- PostgreSQL logging: preserves request history for auditing and usage analytics.
- Health endpoints: supports orchestrators/load balancers deciding if instances should receive traffic.

## Resume-Friendly Impact

- Prevented API overload during burst traffic with Redis-based sliding windows.
- Enabled secure client usage tracking through API key auth + PostgreSQL logging.
- Improved deployment reliability with containerization and health probes.
