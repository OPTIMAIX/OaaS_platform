import pytest
from httpx import AsyncClient

from oaasplatform.main import create_app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=create_app(), base_url="http://test") as client:

        print("Client is ready")
        yield client