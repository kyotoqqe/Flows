import asyncio
import functools
import time
from collections import deque
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class CircuitBreakerException(Exception):
    pass


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        excluded_errors: tuple[type[Exception], ...],
        errors_threshold: int = 3,
        recovery_timeout: float = 60.0,
        success_threshold: int = 1,
        permitted_number_of_calls_in_half_open_state: int = 2,
        failover_func: Callable[[], Coroutine[Any, Any, Any]] | None = None,
    ) -> None:
        self._state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self.errors_threshold: int = errors_threshold
        self.success_calls: int = 0
        self.error_calls: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()
        self.recovery_timeout: float = recovery_timeout
        self.failover_func: Callable[[], Coroutine[Any, Any, Any]] | None = failover_func
        self.permitted_number_of_calls_in_half_open_state: int = (
            permitted_number_of_calls_in_half_open_state
        )
        self.release_time: float | None = None
        self.excluded_errors: tuple[type[Exception], ...] = excluded_errors
        self.failures_queue: deque[float] = deque(maxlen=errors_threshold)
        self.success_threshold: int = success_threshold
        self.in_flight_half_open_calls: int = 0

    async def __can_execute(self) -> bool:
        async with self._lock:
            await self.__state_transition()

            if self._state == CircuitBreakerState.OPEN:
                return False

            if self._state == CircuitBreakerState.HALF_OPEN:
                if (
                    self.in_flight_half_open_calls
                    >= self.permitted_number_of_calls_in_half_open_state
                ):
                    return False
                self.in_flight_half_open_calls += 1
                return True

            return True

    async def __state_transition(self) -> None:
        if (
            self._state == CircuitBreakerState.HALF_OPEN
            and (self.success_calls + self.error_calls)
            == self.permitted_number_of_calls_in_half_open_state
        ):
            if self.success_calls >= self.success_threshold:
                self._state = CircuitBreakerState.CLOSED
                self.success_calls = 0
                self.error_calls = 0
                self.failures_queue.clear()
                self.release_time = None
            else:
                self._state = CircuitBreakerState.OPEN
                self.success_calls = 0
                self.error_calls = 0
                self.failures_queue.clear()
                self.release_time = time.monotonic() + self.recovery_timeout

        if self._state == CircuitBreakerState.CLOSED and self.error_calls >= self.errors_threshold:
            if len(self.failures_queue) > 1:
                last_and_first_err_diff = self.failures_queue[-1] - self.failures_queue[0]
            else:
                last_and_first_err_diff = 0.0

            if last_and_first_err_diff <= 60.0:
                self._state = CircuitBreakerState.OPEN
                self.error_calls = 0
                self.failures_queue.clear()
                self.release_time = time.monotonic() + self.recovery_timeout

        if self._state == CircuitBreakerState.OPEN:
            current_time = time.monotonic()
            if self.release_time and (current_time - self.release_time) > 0:
                self._state = CircuitBreakerState.HALF_OPEN

    async def _success_reg(self) -> None:
        async with self._lock:
            if self._state == CircuitBreakerState.HALF_OPEN:
                self.success_calls += 1
                self.in_flight_half_open_calls -= 1
                await self.__state_transition()

    async def _fail_reg(self) -> None:
        async with self._lock:
            self.error_calls += 1
            if self._state == CircuitBreakerState.HALF_OPEN:
                self.in_flight_half_open_calls -= 1
            self.failures_queue.append(time.monotonic())
            await self.__state_transition()

    async def call(
        self,
        func: Callable[P, Coroutine[Any, Any, R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R | Any:
        if not await self.__can_execute():
            if self.failover_func:
                return await self.failover_func()
            raise CircuitBreakerException()

        try:
            res = await func(*args, **kwargs)
            await self._success_reg()
            return res
        except Exception as e:
            if not isinstance(e, self.excluded_errors):
                await self._fail_reg()
            raise

    def __call__(
        self,
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R | Any]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | Any:
            return await self.call(func, *args, **kwargs)

        return wrapper
