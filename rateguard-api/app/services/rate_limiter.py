import time

from redis.asyncio import Redis


class SlidingWindowRateLimiter:
    """Redis sorted-set sliding window limiter."""

    def __init__(self, redis_client: Redis, limit: int, window_seconds: int = 60) -> None:
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds

    async def allow(self, key: str) -> tuple[bool, int]:
        # Use current timestamp (ms) as both member and score.
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (self.window_seconds * 1000)
        redis_key = f"rl:{key}"

        # Pipeline keeps operations atomic enough for common API workloads.
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, start_ms)
        pipe.zadd(redis_key, {str(now_ms): now_ms})
        pipe.zcard(redis_key)
        pipe.expire(redis_key, self.window_seconds)
        _, _, count, _ = await pipe.execute()

        allowed = count <= self.limit
        remaining = max(self.limit - count, 0)
        return allowed, remaining
