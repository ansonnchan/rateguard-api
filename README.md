# RateGuard API

FastAPI rate-limiting service with Redis sliding windows, API key authentication, and PostgreSQL request logging.

## Features

- Per-user and per-IP rate limiting (`60 req/min` by default)
- API key authentication via `X-API-Key`
- Request logs persisted in PostgreSQL
- Health checks for liveness and readiness
- Dockerized deployment with Redis + Postgres dependencies

## Stack

- Python
- FastAPI
- Redis
- PostgreSQL
- Docker

## Quick Start

1. Copy env file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. Test endpoints:

```bash
curl http://localhost:8000/health/liveness
curl http://localhost:8000/health/readiness
curl -H "X-API-Key: local-dev-key" http://localhost:8000/api/v1/limited
```

## Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

You still need Redis and Postgres running and configured in `.env`.

## Tests

```bash
pytest
```
