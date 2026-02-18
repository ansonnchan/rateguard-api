from redis.asyncio import Redis


class RedisClient:
    """Connection lifecycle wrapper for Redis."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self.client: Redis | None = None

    async def connect(self) -> None:
        # Decode responses so values are returned as strings instead of bytes.
        self.client = Redis.from_url(self._redis_url, decode_responses=True)
        await self.client.ping()

    async def disconnect(self) -> None:
        if self.client is not None:
            await self.client.close()
            self.client = None
