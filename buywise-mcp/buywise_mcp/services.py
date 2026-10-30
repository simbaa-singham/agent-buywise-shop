"""HTTP client for buywise-services. Errors come back as a short message the model can relay."""
import os

import httpx
from mcp.server.mcpserver.exceptions import ToolError

BASE_URL = os.environ.get("SERVICES_URL", "http://localhost:8081")
_client = httpx.AsyncClient(base_url=BASE_URL, timeout=10)


class ServiceError(ToolError):
    pass


async def call(method: str, path: str, *, customer_id: str | None = None, **kwargs):
    headers = {"X-Customer-Id": customer_id} if customer_id else {}
    resp = await _client.request(method, path, headers=headers, **kwargs)
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail") or resp.text
        except ValueError:
            detail = resp.text
        raise ServiceError(detail)
    return resp.json()
