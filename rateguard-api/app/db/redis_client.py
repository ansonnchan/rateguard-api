from redis.asyncio import Redis

class RedisClient:
    """
    Lightweight async Redis client wrapper.

    Handles connection lifecycle (connect / disconnect) and
    stores a shared Redis client instance for reuse.
    """

    def __init__(self, redis_url: str) -> None:
        # Redis connection URL 
        self._redis_url = redis_url

        # Redis client instance (initialized on connect)
        self.client: Redis | None = None

    async def connect(self) -> None:
        """
        establish connection to Redis
        Creates an async Redis client and verifies connection by sending a PING command. 
        """
        self.client = Redis.from_url(
            self._redis_url,
            decode_responses=True
        )
        await self.client.ping()

    async def disconnect(self) -> None:
        """
        Closes the Redis connection safely and clears the client reference
        to prevent reuse after closing. 
        """
        if self.client is not None:
            await self.client.close()
            self.client = None
