from contextlib import asynccontextmanager

from aiohttp import ClientSession, TCPConnector


class ConnectionPool:
    def __init__(
        self,
        keepalive_timeout: float = 30.0,
        limit: int = 100,
        limit_per_host: int = 15,
        ttl_dns_cache: int = 300,
        **session_kwargs,
    ) -> None:
        self._connector: TCPConnector | None = None
        self.keepalive_timeout = keepalive_timeout
        self.limit = limit
        self.limit_per_host = limit_per_host
        self.ttl_dns_cache = ttl_dns_cache
        self.session_setup = {**session_kwargs}

    def _get_connector(self):
        if self._connector is None or self.connector.closed:
            self.connector = TCPConnector(
                keepalive_timeout=self.keepalive_timeout,
                limit=self.limit,
                limit_per_host=self.limit_per_host,
                ttl_dns_cache=self.ttl_dns_cache,
                enable_cleanup_closed=True,
            )
            return self._connector

    async def close(self):
        if self._connector and not self._connector.closed:
            await self._connector.close()

    @asynccontextmanager
    async def get_session(self, **kwargs):
        session_kwargs = {**self.session_setup, **kwargs}

        async with ClientSession(
            connector=self._get_connector(), connector_owner=True, **session_kwargs
        ) as session:
            yield session


connection_pool = ConnectionPool()
