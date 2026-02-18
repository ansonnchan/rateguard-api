from fastapi import Header, HTTPException, status

from app.config import get_settings


async def require_api_key(x_api_key: str = Header(default="")) -> str:
    settings = get_settings()

    if not x_api_key or x_api_key not in settings.parsed_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return x_api_key
