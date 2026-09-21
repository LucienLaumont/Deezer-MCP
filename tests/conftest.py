import pytest

from deezer_mcp.deezer_client import DeezerClient

DEEZER_BASE_URL = "https://api.deezer.com"


@pytest.fixture
async def client():
    c = DeezerClient()
    yield c
    await c.close()
