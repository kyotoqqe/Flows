import json

from aiohttp import FormData

from shared.infrastructure.ipc.rpc.adapters.http.connection import connection_pool
from shared.infrastructure.ipc.rpc.exceptions import RpcClientError
from shared.infrastructure.ipc.rpc.ports.client import AbstractRpcClient

AVAILABLE_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


# add ssl in future
class HttpRpcCLient(AbstractRpcClient):
    def __init__(
        self, base_url: str, headers: dict | None = None, cookies: dict | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "User-Agent": "BackendService/1.0",
            "Accept": "application/json",
            **(headers or {}),
        }
        self.cookies = cookies or {}

    async def call(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        form_data: FormData | bytes | None = None,
        json_data: dict | None = None,
        headers: dict | None = None,
    ):
        if method not in AVAILABLE_METHODS:
            raise ValueError("Passed method is unsupported or uncorrect")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        print(url)

        if form_data and json_data:
            raise ValueError("Not available to pass form data and json data at the same time")

        data = form_data

        if json_data:
            data = json.dumps(json_data)

        all_headers = {**self.headers, **(headers or {})}

        # add timeout

        async with connection_pool.get_session(  # noqa: SIM117
            cookies=self.cookies, headers=self.headers
        ) as session:
            async with session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=all_headers,
            ) as resp:
                # add more status handling
                if resp.status == 204 and (resp.content_length == 0 or resp.content_length is None):
                    return

                if 400 <= resp.status <= 500:
                    content_type = resp.headers.get("Content-Type", "")

                    # create multiple classes for content type handling
                    if "application/json" in content_type:
                        res = await resp.json(content_type=None)

                        raise RpcClientError(resp.status, res)
                    raise RpcClientError(resp.status)

                content_type = resp.headers.get("Content-Type", "")

                # create multiple classes for content type handling
                if "application/json" in content_type:
                    return await resp.json(content_type=None)

                if "text/" in content_type:
                    return await resp.text()

                return await resp.read()
