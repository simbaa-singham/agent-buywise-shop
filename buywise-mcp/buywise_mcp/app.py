"""One process serving every domain server under /mcp/{domain} (ADR-031). Run: uv run uvicorn buywise_mcp.app:app"""
import contextlib

from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .servers import catalog, inventory, orders

SERVERS: dict[str, MCPServer] = {"catalog": catalog, "inventory": inventory, "orders": orders}

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
