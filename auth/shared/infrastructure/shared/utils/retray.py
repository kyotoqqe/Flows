import asyncio
import random


class RetrayError(Exception):
    # must save last raised error
    pass


def retray(
    expected_errors: tuple[type[Exception]] | None,
    retray_count: int = 1,
    max_backoffs: int = 5,
    max_elapsed: int = 0,
):

    expected_errors = expected_errors or (Exception,)

    def decorator(func):
        async def wrapper(*args, **kwargs):
            backoff = 1
            for i in range(1, retray_count + 1):
                try:
                    return await func(*args, **kwargs)
                except expected_errors:
                    sleep_time = (backoff * i if i <= max_backoffs else backoff) + random.uniform(
                        -1, 2
                    )
                    await asyncio.sleep(sleep_time)

            raise RetrayError
