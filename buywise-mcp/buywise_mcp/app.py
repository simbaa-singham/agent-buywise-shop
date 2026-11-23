"""One process serving every domain server under /mcp/{domain} (ADR-031). Run: uv run uvicorn buywise_mcp.app:app
Each domain package (buywise_mcp/domains/<domain>/) holds its server, tools and result models."""
import contextlib

from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .domains import catalog, inventory, orders

SERVERS: dict[str, MCPServer] = {"catalog": catalog.server, "inventory": inventory.server, "orders": orders.server}

routes = [Route("/health", lambda request: JSONResponse({"status": "UP"}))]
for domain, server in SERVERS.items():
    routes += server.streamable_http_app(streamable_http_path=f"/mcp/{domain}", stateless_http=True).routes


@contextlib.asynccontextmanager
async def lifespan(_app):
    async with contextlib.AsyncExitStack() as stack:
        for server in SERVERS.values():
            await stack.enter_async_context(server.session_manager.run())
        yield


app = Starlette(routes=routes, lifespan=lifespan)
