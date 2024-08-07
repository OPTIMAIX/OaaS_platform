import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_hello(client:  AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200