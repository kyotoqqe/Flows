from ast import arg
import asyncio
import functools


class BulkheadException(Exception):
    pass


class Bulkhead:
    def __init__(self, name: str, max_concurent: int, max_wait: int = 0) -> None:
        self.name = name
        self.max_concurent = max_concurent
        self.max_wait = max_wait
        self._semaphore = asyncio.BoundedSemaphore(max_concurent)
        self._lock = asyncio.Lock()
        self._current = 0

    async def acquire(self):

        if self.max_wait > 0:
            try:
                await asyncio.wait_for(self._semaphore.acquire(), self.max_wait)
            except TimeoutError:
                return False
        else:
            async with self._lock:
                if self._current > self.max_concurent:
                    self._current += 1
                    await self._semaphore.acquire()
                    return True
                return False

        async with self._lock:
            self._current += 1

        return True

    async def release(self):
        async with self._lock:
            self._semaphore.release()
            self._current -= 1

    async def execute(self, func, *args, **kwargs):
        if not await self.acquire():
            raise BulkheadException

        try:
            res = await func(*args, **kwargs)
            return res
        finally:
            await self.release()


def bulkhead(name: str, max_concurent: int, max_wait: int = 0):
    _bulkhead = Bulkhead(name=name, max_concurent=max_concurent, max_wait=max_wait)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await _bulkhead.execute(func, *args, **kwargs)

        return wrapper

    return decorator
