import time
from redis.asyncio import Redis


class SlidingWindowRateLimiter:
    """
    Redis-based sliding window rate limiter using sorted sets.

    Each request is stored as a timestamped entry, allowing precise
    rate limiting over a rolling time window.
    """

    def __init__(self, redis_client: Redis, limit: int, window_seconds: int = 60) -> None:
        # Shared async Redis client
        self.redis = redis_client

        # Maximum number of allowed requests within the window
        self.limit = limit

        # Sliding window size in seconds
        self.window_seconds = window_seconds

    async def allow(self, key: str) -> tuple[bool, int]:
        """
        Determine whether a request is allowed under the rate limit.

        Args:
            key: Unique identifier for the client (e.g., API key or IP)

        Returns:
            A tuple of (allowed, remaining), where:
            - allowed indicates if the request should be accepted
            - remaining is the number of requests left in the window
        """
        # Current timestamp in milliseconds
        now_ms = int(time.time() * 1000)

        # Earliest timestamp still inside the sliding window
        start_ms = now_ms - (self.window_seconds * 1000)

        # Namespaced Redis key for this rate limit
        redis_key = f"rl:{key}"

        # Use a pipeline to group operations and reduce round trips
        pipe = self.redis.pipeline()

        # Remove entries that fall outside the sliding window
        pipe.zremrangebyscore(redis_key, 0, start_ms)

        # Add the current request with timestamp as score and member
        pipe.zadd(redis_key, {str(now_ms): now_ms})

        # Count requests within the current window
        pipe.zcard(redis_key)

        # Set TTL to auto-expire idle keys
        pipe.expire(redis_key, self.window_seconds)

        # Execute pipeline and unpack the count result
        _, _, count, _ = await pipe.execute()

        # Request is allowed if under the configured limit
        allowed = count <= self.limit

        # Remaining requests available in the current window
        remaining = max(self.limit - count, 0)

        return allowed, remaining
