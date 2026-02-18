import pytest
from fastapi import HTTPException

from app.config import Settings
from app.middleware.auth import require_api_key


@pytest.mark.asyncio
async def test_require_api_key_rejects_invalid(monkeypatch):
    # Auth dependency should reject keys outside configured allow-list.
    monkeypatch.setenv("API_KEYS", "key-a,key-b")

    with pytest.raises(HTTPException) as exc:
        await require_api_key("bad-key")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_require_api_key_accepts_valid(monkeypatch):
    # Happy path: key is returned for downstream handlers.
    monkeypatch.setenv("API_KEYS", "key-a,key-b")

    key = await require_api_key("key-a")
    assert key == "key-a"


def test_settings_parse_api_keys():
    # Empty entries/spaces are ignored during parsing.
    settings = Settings(api_keys="alpha, beta, ,gamma")
    assert settings.parsed_api_keys == {"alpha", "beta", "gamma"}
