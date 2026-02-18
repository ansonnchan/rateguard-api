from app.db.postgres import PostgresClient


class RequestLogger:
    """
    Persists incoming API request metadata for auditing, monitoring,
    and client usage analysis.
    """

    def __init__(self, postgres: PostgresClient) -> None:
        # Shared Postgres client used to execute write operations
        self.postgres = postgres

    async def log(
        self,
        api_key: str,
        client_ip: str,
        endpoint: str,
        status_code: int
    ) -> None:
        """
        Record a single API request entry.

        Stores the API key used, client IP address, requested endpoint,
        and resulting HTTP status code for later analysis.
        """
        query = """
        INSERT INTO request_logs (api_key, client_ip, endpoint, status_code)
        VALUES ($1, $2, $3, $4)
        """

        # execute parameterized query to prevent SQL injection
        await self.postgres.execute(
            query,
            api_key,
            client_ip,
            endpoint,
            status_code
        )
