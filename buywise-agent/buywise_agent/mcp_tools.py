"""MCP tools as the model sees them - discovered from buywise-mcp, never written here (ADR-053, ADR-057).

Each domain server (ADR-031) is asked for its tools: name, description, input schema and annotations. That is the
reviewed tool contract (buywise-mcp snapshots), so the model reads exactly what was approved. The list is cached
for as long as the server allows (ttlMs, ADR-057). The customer travels as a header from the logged-in session,
never as a tool argument (ADR-028; OAuth token in Phase M step 4).
"""

import time
from dataclasses import dataclass

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from .config import settings

FALLBACK_TTL_S = 60.0  # if a server sends no ttlMs


@dataclass(frozen=True)
class ToolInfo:
    name: str
    domain: str
    title: str
    description: str
    input_schema: dict
    read_only: bool
    destructive: bool
    idempotent: bool

    def model_spec(self) -> dict:
        """OpenAI-style function definition for bind_tools."""
        return {"type": "function",
                "function": {"name": self.name, "description": self.description, "parameters": self.input_schema}}


def _info(domain: str, tool) -> ToolInfo:
    a = tool.annotations
    # A tool without hints is treated as the riskiest kind: a non-idempotent write (MCP spec defaults)
    return ToolInfo(name=tool.name, domain=domain, title=tool.title or tool.name, description=tool.description or "",
                    input_schema=tool.input_schema, read_only=bool(a and a.read_only_hint),
                    destructive=bool(a is None or a.destructive_hint is not False),
                    idempotent=bool(a and a.idempotent_hint))


def _client(domain: str, customer_id: str | None) -> Client:
    http = httpx2.AsyncClient(headers={"X-Customer-Id": customer_id} if customer_id else {}, timeout=20)
    return Client(streamable_http_client(f"{settings.mcp_url}/{domain}", http_client=http))


class ToolCatalog:
    def __init__(self, domains: list[str]):
        self.domains = domains
        self._tools: dict[str, ToolInfo] = {}
        self._expires = 0.0

    async def tools(self) -> dict[str, ToolInfo]:
        if time.monotonic() >= self._expires:
            tools, ttls = {}, []
            for domain in self.domains:
                async with _client(domain, None) as client:
                    listing = await client.list_tools()
                tools |= {t.name: _info(domain, t) for t in listing.tools}
                if listing.ttl_ms:
                    ttls.append(listing.ttl_ms / 1000)
            # refresh when the first server's hint runs out
            self._tools, self._expires = tools, time.monotonic() + (min(ttls) if ttls else FALLBACK_TTL_S)
        return self._tools


catalog = ToolCatalog(settings.mcp_domains)


async def call_mcp(info: ToolInfo, args: dict, customer_id: str | None) -> tuple[bool, str, dict | None]:
    """Returns (ok, text, data). `text` goes to the model (results as JSON, errors as "code: message Hint: ...").
    `data` is the typed structured result (ADR-054) or the typed error {code, message, retryable, hint} (ADR-055),
    used by code, e.g. to build product cards; never parsed from text."""
    try:
        async with _client(info.domain, customer_id) as client:
            result = await client.call_tool(info.name, args)
        text = "\n".join(getattr(part, "text", "") for part in result.content)
        return (not result.is_error), text, result.structured_content
    except Exception as e:  # noqa: BLE001 - any transport failure; tool server down -> the model says it cannot check right now
        return False, f"unavailable: Tool unavailable ({type(e).__name__}).", {
            "code": "unavailable", "message": "Tool unavailable", "retryable": True}
