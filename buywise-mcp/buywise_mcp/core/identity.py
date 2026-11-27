"""Who is calling and what they may do - per tool, from the validated token (ADR-050, ADR-051).

Each tool declares what it needs as a parameter the model never sees:
    caller: CatalogReader                      -> scope catalog:read
    customer: OrdersWriter                     -> scope orders:write + role customer + a customer_id claim
`Resolve` runs the check before the tool body. Authorization is three things (ADR-050 amendment):
scope = what the calling app may do, role `customer` = what the user is, `customer_id` = whose data.
A failed check returns `Unresolved`, which @typed_errors turns into the typed error without running the tool.
"""

from dataclasses import dataclass
from typing import Annotated

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver import Resolve

from .errors import ErrorCode, Unresolved

CUSTOMER_ROLE = "customer"


@dataclass(frozen=True)
class Principal:
    """The checked caller of one tool call. `token` is the incoming MCP token, swapped before calling services."""

    token: str
    sub: str | None
    azp: str  # the client that called MCP (the agent)
    scopes: frozenset[str]
    roles: frozenset[str]
    customer_id: str | None
    expires_at: int


def requires(scope: str, *, customer: bool = False):
    async def resolve() -> Principal | Unresolved:
        access = get_access_token()
        if access is None:  # only possible in-process (tests): over HTTP the SDK refuses a missing token with 401
            return Unresolved(
                ErrorCode.NOT_LOGGED_IN,
                "No valid sign-in for this request.",
                hint="Ask the customer to log in with the Log in button, then try again.",
            )
        claims = access.claims or {}
        p = Principal(
            token=access.token,
            sub=access.subject,
            azp=access.client_id,
            scopes=frozenset(access.scopes),
            roles=frozenset(claims.get("realm_access", {}).get("roles", [])),
            customer_id=claims.get("customer_id"),
            expires_at=access.expires_at or 0,
        )
        if customer and not p.customer_id:
            return Unresolved(
                ErrorCode.NOT_LOGGED_IN,
                "The customer is not logged in.",
                hint="Ask the customer to log in with the Log in button, then try again.",
            )
        if customer and CUSTOMER_ROLE not in p.roles:
            return Unresolved(
                ErrorCode.FORBIDDEN,
                "This login is not a customer account.",
                hint="Tell the customer this account cannot shop; offer help from staff.",
            )
        if scope not in p.scopes:
            return Unresolved(ErrorCode.FORBIDDEN, f"This assistant is not allowed to use this ({scope}).")
        return p

    resolve.__name__ = f"requires_{scope.replace(':', '_')}"
    return resolve


CatalogReader = Annotated[Principal, Resolve(requires("catalog:read"))]
InventoryReader = Annotated[Principal, Resolve(requires("inventory:read"))]
OrdersReader = Annotated[Principal, Resolve(requires("orders:read", customer=True))]
OrdersWriter = Annotated[Principal, Resolve(requires("orders:write", customer=True))]
