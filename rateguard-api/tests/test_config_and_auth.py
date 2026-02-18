import pytest
from fastapi import HTTPException

from app.config import Settings
from app.middleware.auth import require_api_key


@pytest.mark.asyncio
async def test_require_api_key_rejects_invalid(monkeypatch):
    monkeypatch.setenv("API_KEYS", "key-a,key-b")

    with pytest.raises(HTTPException) as exc:
        await require_api_key("bad-key")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_require_api_key_accepts_valid(monkeypatch):
    monkeypatch.setenv("API_KEYS", "key-a,key-b")

    key = await require_api_key("key-a")
    assert key == "key-a"


def test_settings_parse_api_keys():
    settings = Settings(api_keys="alpha, beta, ,gamma")
    assert settings.parsed_api_keys == {"alpha", "beta", "gamma"}
