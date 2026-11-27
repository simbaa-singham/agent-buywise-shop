"""Shared tool metadata (ADR-053, ADR-057).

Annotations describe what a tool does TODAY - the agent's policy trusts them (confirm, retry, cache):
- READ: reads only; safe to retry and to cache within a turn.
- WRITE: changes data, not idempotent: a repeat does it again -> always confirmed, never retried.
- WRITE_IDEMPOTENT_DESTRUCTIVE: changes data, a repeat has no further effect, cannot be undone -> confirmed.
All tools are closed-world: they only touch BuyWise systems.
"""

from mcp.server.auth.settings import AuthSettings
from mcp.server.caching import CacheHint
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from ..config import settings
from .auth import verifier

VERSION = "1.0.0"  # tool contract version; bump on a breaking change (ADR-064)

READ = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)
WRITE_IDEMPOTENT_DESTRUCTIVE = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=False
)


def domain_server(domain: str, instructions: str) -> MCPServer:
    """One MCP server per domain at /mcp/{domain} (ADR-031): an OAuth resource server for Keycloak tokens (ADR-050),
    with its protected-resource metadata at /.well-known/oauth-protected-resource/mcp/{domain} (RFC 9728).
    Its lists may be cached by every client for 10 minutes (ADR-057)."""
    hint = CacheHint(ttl_ms=600_000, scope="public")
    return MCPServer(
        f"buywise-{domain}",
        instructions=instructions,
        version=VERSION,
        cache_hints={"tools/list": hint, "prompts/list": hint, "resources/list": hint},
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=settings.issuer,
            resource_server_url=f"{settings.public_url}/mcp/{domain}",
            validate_token_resource=False,  # the verifier checks the audience itself (aud: buywise-mcp)
        ),
    )
