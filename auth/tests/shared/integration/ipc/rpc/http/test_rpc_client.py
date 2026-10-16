from aiohttp import FormData
import pytest

from shared.infrastructure.ipc.rpc.adapters.http.client import HttpRpcCLient
from shared.infrastructure.ipc.rpc.exceptions import RpcClientError


@pytest.mark.asyncio
async def test_http_rpc_client():
    client = HttpRpcCLient("https://httpbin.org/")
    try:
        form = FormData()
        form.add_field("some", "shit")
        err_res = await client.call(
            "POST",
            "post",
            headers={"Content-Type": "application/json"},
            json_data={"foo": "bar"},
            form_data=form,
        )
    except Exception as e:
        assert isinstance(e, ValueError)

    res = await client.call("GET", "status/204")
    print(res)
    assert res is None

    try:
        res = await client.call("GET", "status/400")
    except Exception as e:
        assert isinstance(e, RpcClientError)
