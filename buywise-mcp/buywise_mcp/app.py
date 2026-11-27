"""One process serving every domain server under /mcp/{domain} (ADR-031). Run: uv run uvicorn buywise_mcp.app:app
Each domain package (buywise_mcp/domains/<domain>/) holds its server, tools and result models.

Auth (ADR-050): the SDK puts its token middleware on the app it builds per server; we mount only each server's
routes (which keep their per-route "token required" guard and metadata route), so the middleware is added here,
once - one audience (buywise-mcp) and one verifier serve every domain. /health stays open."""

import contextlib

from mcp.server.auth.middleware.auth_context import AuthContextMiddleware
from mcp.server.auth.middleware.bearer_auth import BearerAuthBackend
from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from .core.auth import verifier
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


middleware = [
    Middleware(AuthenticationMiddleware, backend=BearerAuthBackend(verifier)),  # Bearer token -> checked caller
    Middleware(AuthContextMiddleware),  # makes it available to the tools (identity.py)
]
app = Starlette(routes=routes, middleware=middleware, lifespan=lifespan)
