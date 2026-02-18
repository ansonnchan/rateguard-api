import time

import pytest

from app.services.rate_limiter import SlidingWindowRateLimiter

#tests - not comprehensive enough (17/2/26)

class FakePipeline:
    """Minimal Redis pipeline emulator for deterministic limiter tests."""

    def __init__(self, redis):
        self.redis = redis
        self.ops = []

    def zremrangebyscore(self, key, min_score, max_score):
        self.ops.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zadd(self, key, values):
        self.ops.append(("zadd", key, values))
        return self

    def zcard(self, key):
        self.ops.append(("zcard", key))
        return self

    def expire(self, key, _ttl):
        self.ops.append(("expire", key))
        return self

    async def execute(self):
        results = []
        for op in self.ops:
            name = op[0]
            if name == "zremrangebyscore":
                key, min_score, max_score = op[1], op[2], op[3]
                kept = [s for s in self.redis.data.get(key, []) if not (min_score <= s <= max_score)]
                removed = len(self.redis.data.get(key, [])) - len(kept)
                self.redis.data[key] = kept
                results.append(removed)
            elif name == "zadd":
                key = op[1]
                score = list(op[2].values())[0]
                self.redis.data.setdefault(key, []).append(score)
                results.append(1)
            elif name == "zcard":
                key = op[1]
                results.append(len(self.redis.data.get(key, [])))
            elif name == "expire":
                results.append(True)
        self.ops = []
        return results


class FakeRedis:
    """In-memory stand-in for Redis sorted-set storage."""

    def __init__(self):
        self.data = {}

    def pipeline(self):
        return FakePipeline(self)


@pytest.mark.asyncio
async def test_sliding_window_blocks_after_limit():
    # Third request in same window should be denied when limit is 2.
    redis = FakeRedis()
    limiter = SlidingWindowRateLimiter(redis, limit=2, window_seconds=60)

    allowed_1, remaining_1 = await limiter.allow("user:1")
    allowed_2, remaining_2 = await limiter.allow("user:1")
    allowed_3, remaining_3 = await limiter.allow("user:1")

    assert allowed_1 is True and remaining_1 == 1
    assert allowed_2 is True and remaining_2 == 0
    assert allowed_3 is False and remaining_3 == 0


@pytest.mark.asyncio
async def test_sliding_window_resets_after_window(monkeypatch):
    # Requests become allowed again once the first window expires.
    redis = FakeRedis()
    limiter = SlidingWindowRateLimiter(redis, limit=1, window_seconds=1)

    t0 = 1000.0
    monkeypatch.setattr(time, "time", lambda: t0)
    allowed_1, _ = await limiter.allow("ip:127.0.0.1")

    monkeypatch.setattr(time, "time", lambda: t0 + 2.0)
    allowed_2, _ = await limiter.allow("ip:127.0.0.1")

    assert allowed_1 is True
    assert allowed_2 is True
