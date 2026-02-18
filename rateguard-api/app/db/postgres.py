from typing import Any

import asyncpg


class PostgresClient:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(self._database_url, min_size=1, max_size=10)

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, *args: Any) -> str:
        if self._pool is None:
            raise RuntimeError("Postgres pool is not initialized")
        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        if self._pool is None:
            raise RuntimeError("Postgres pool is not initialized")
        async with self._pool.acquire() as connection:
            return await connection.fetchval(query, *args)

    async def ensure_schema(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS request_logs (
            id BIGSERIAL PRIMARY KEY,
            api_key TEXT NOT NULL,
            client_ip TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(create_table_query)
