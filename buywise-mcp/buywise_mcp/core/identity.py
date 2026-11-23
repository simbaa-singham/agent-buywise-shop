"""Who the customer is, for tools that need one (ADR-051): declared as
`customer: Customer` = `Annotated[str, Resolve(current_customer)]`, filled by this code, invisible to the model.

Today: the X-Customer-Id header the agent sets from the logged-in session (local simplification, ADR-028).
Phase M step 4 replaces only the inside of current_customer with the validated OAuth token (ADR-050).
"""

from typing import Annotated

from mcp.server.mcpserver import Context, Resolve

from .errors import ErrorCode, Unresolved


async def current_customer(ctx: Context) -> str | Unresolved:
    customer_id = (ctx.headers or {}).get("x-customer-id")
    if not customer_id:
        return Unresolved(
            ErrorCode.NOT_LOGGED_IN,
            "The customer is not logged in.",
            hint="Ask the customer to log in with the Log in button, then try again.",
        )
    return customer_id


Customer = Annotated[str, Resolve(current_customer)]
