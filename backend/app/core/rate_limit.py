import time
from typing import Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None

from .config import settings


class RateLimiter:
    def __init__(self, url: str):
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.per_minute = settings.RATE_LIMIT_PER_MINUTE

    def allow(self, key: str) -> bool:
        now_min = int(time.time() // 60)
        bucket_key = f"rl:{key}:{now_min}"
        current = self.client.incr(bucket_key)
        if current == 1:
            self.client.expire(bucket_key, 120)
        return current <= self.per_minute


class InMemoryRateLimiter:
    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self._buckets: dict[str, tuple[int, int]] = {}

    def allow(self, key: str) -> bool:
        now_min = int(time.time() // 60)
        current_min, count = self._buckets.get(key, (now_min, 0))
        if current_min != now_min:
            current_min, count = now_min, 0
        count += 1
        self._buckets[key] = (current_min, count)
        return count <= self.per_minute

rate_limiter: Optional[object] = None

def init_rate_limiter():
    global rate_limiter
    try:
        rate_limiter = RateLimiter(settings.REDIS_URL)
    except Exception:
        # Best-effort: fall back to an in-memory limiter when Redis isn't available.
        rate_limiter = InMemoryRateLimiter(settings.RATE_LIMIT_PER_MINUTE)
