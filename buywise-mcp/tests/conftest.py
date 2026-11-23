import pytest


@pytest.fixture
def anyio_backend():
    """MCP and httpx are anyio-based; run async tests on asyncio."""
    return "asyncio"
