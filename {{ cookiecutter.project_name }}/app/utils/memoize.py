from datetime import datetime
from functools import wraps


class Memo:
    def __init__(self, f: callable, *, max_hits: int = None, ttl: int = None):
        self.max_hits = max_hits
        self.ttl = ttl
        self._hits_count = 0
        self._initialized = False
        self._cache = None
        self._result_time = None
        self._function = f

    async def __call__(self, *args, **kwargs):
        current_ts = datetime.utcnow().timestamp()

        if (
                not self._initialized
                or kwargs.get('_reset_cache', False)
                or (bool(self.max_hits) and self._hits_count >= self.max_hits)
                or (bool(self.ttl) and (self._result_time + self.ttl) <= current_ts)
        ):
            self._cache = await self._function(*args, **kwargs)
            self._initialized = True
            self._result_time = current_ts
            self._hits_count = 0

        self._hits_count += 1
        return self._cache


def memoize(max_hits: int = None, ttl: int = None):
    def decorator(f: callable):
        memo = Memo(f, max_hits=max_hits, ttl=ttl)

        @wraps(f)
        async def decorated(*args, **kwargs):
            return await memo(*args, **kwargs)

        return decorated

    return decorator
