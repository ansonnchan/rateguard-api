from app.db.postgres import PostgresClient


class RequestLogger:
    def __init__(self, postgres: PostgresClient) -> None:
        self.postgres = postgres

    async def log(self, api_key: str, client_ip: str, endpoint: str, status_code: int) -> None:
        query = """
        INSERT INTO request_logs (api_key, client_ip, endpoint, status_code)
        VALUES ($1, $2, $3, $4)
        """
        await self.postgres.execute(query, api_key, client_ip, endpoint, status_code)
