from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status

from app.config import get_settings
from app.db.postgres import PostgresClient
from app.db.redis_client import RedisClient
from app.middleware.auth import require_api_key
from app.services.logger import RequestLogger
from app.services.rate_limiter import SlidingWindowRateLimiter

settings = get_settings()
postgres_client = PostgresClient(settings.database_url)
redis_client = RedisClient(settings.redis_url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await postgres_client.connect()
    await postgres_client.ensure_schema()
    await redis_client.connect()
    yield
    await redis_client.disconnect()
    await postgres_client.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


async def enforce_limits(request: Request, api_key: str) -> tuple[str, int]:
    client_ip = request.client.host if request.client else "unknown"
    redis = redis_client.client

    if redis is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis not available")

    limiter = SlidingWindowRateLimiter(redis, settings.rate_limit_per_minute, window_seconds=60)
    user_allowed, user_remaining = await limiter.allow(f"user:{api_key}")
    ip_allowed, ip_remaining = await limiter.allow(f"ip:{client_ip}")

    if not user_allowed or not ip_allowed:
        remaining = min(user_remaining, ip_remaining)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Remaining requests: {remaining}",
        )

    return client_ip, min(user_remaining, ip_remaining)


@app.get("/health/liveness")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/readiness")
async def readiness() -> dict[str, str]:
    redis = redis_client.client
    if redis is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis not ready")

    try:
        await redis.ping()
        await postgres_client.fetchval("SELECT 1")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Dependency error: {exc}") from exc

    return {"status": "ready"}


@app.get(f"{settings.api_prefix}/limited")
async def limited_endpoint(request: Request, api_key: str = Depends(require_api_key)) -> dict[str, str | int]:
    logger = RequestLogger(postgres_client)

    try:
        client_ip, remaining = await enforce_limits(request, api_key)
    except HTTPException as exc:
        client_ip = request.client.host if request.client else "unknown"
        await logger.log(api_key, client_ip, request.url.path, exc.status_code)
        raise

    await logger.log(api_key, client_ip, request.url.path, status.HTTP_200_OK)

    return {
        "message": "Request accepted",
        "remaining_in_window": remaining,
    }
