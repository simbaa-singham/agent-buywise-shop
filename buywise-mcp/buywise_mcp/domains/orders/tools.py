"""Orders MCP server (`/mcp/orders`): the logged-in customer's orders. The customer always comes from the
validated token via `OrdersReader` / `OrdersWriter` (ADR-050/051) - never a tool argument. Place and cancel get
confirmation in step 5 (ADR-052)."""

import time
from typing import Annotated, Literal

from pydantic import Field

from ...core.errors import ErrorCode, typed_errors
from ...core.identity import OrdersReader, OrdersWriter
from ...core.services import services
from ...core.tooling import READ, WRITE, WRITE_IDEMPOTENT_DESTRUCTIVE, domain_server
from .models import OrderLineInput, OrderList, OrderSummary, Quote, order_summary, priced

server = domain_server("orders", "The logged-in customer's orders: look up, price, place, cancel.")

ORDER_HINTS = {
    ErrorCode.INVALID_INPUT: "Check each sku with get_product (exact sku, upper case) and that pickup has a store_id "
    "from list_stores.",
    ErrorCode.CONFLICT: "Explain the reason to the customer; offer another store, variant or delivery if it fits.",
}
LOOKUP_HINTS = {ErrorCode.NOT_FOUND: "Use list_my_orders to see the customer's orders; never guess an order id."}

Items = list[OrderLineInput]
FulfilmentType = Literal["pickup", "delivery"]
_stores: tuple[float, dict[str, str]] = (0.0, {})


async def _store_names() -> dict[str, str]:
    """store_id -> name, refreshed every 10 minutes (stores rarely change)."""
    global _stores
    if time.monotonic() - _stores[0] > 600:
        _stores = (
            time.monotonic(),
            {s["storeId"]: s["name"] for s in await services.call("GET", "/api/stores", scope="inventory:read")},
        )
    return _stores[1]


def _order_body(items: Items, fulfilment: str, store_id: str | None) -> dict:
    return {
        "items": [{"sku": i.sku.strip().upper(), "quantity": i.quantity} for i in items],
        "fulfilment": fulfilment,
        "storeId": store_id,
    }


@server.tool(title="My orders", annotations=READ)
@typed_errors()
async def list_my_orders(
    customer: OrdersReader,
    limit: Annotated[int, Field(ge=1, le=20, description="How many recent orders")] = 5,
) -> OrderList:
    """The logged-in customer's most recent orders, newest first. Use for 'my order', 'my latest order' or when
    the customer gives no order id."""
    orders = await services.call("GET", "/api/orders", caller=customer, scope="orders:read", params={"limit": limit})
    names = await _store_names()
    return OrderList(orders=[order_summary(o, names) for o in orders])


@server.tool(title="Order details", annotations=READ)
@typed_errors(LOOKUP_HINTS)
async def get_order(
    customer: OrdersReader,
    order_id: Annotated[
        str, Field(description="Order id the customer gave or list_my_orders returned, e.g. BW-200004")
    ],
) -> OrderSummary:
    """One of the logged-in customer's orders: status, items, totals, pickup or delivery, tracking."""
    return order_summary(
        await services.call("GET", f"/api/orders/{order_id}", caller=customer, scope="orders:read"),
        await _store_names(),
    )


@server.tool(title="Price an order", annotations=READ)
@typed_errors(ORDER_HINTS)
async def quote_order(
    customer: OrdersReader,
    items: Annotated[Items, Field(description="What to order: exact sku and quantity (1-5) per line")],
    fulfilment: Annotated[FulfilmentType, Field(description="pickup at a store, or delivery to the address on file")],
    store_id: Annotated[str | None, Field(description="Required for pickup: store_id from list_stores")] = None,
) -> Quote:
    """Price an order without placing it: items, tax, total, pickup store or delivery. Nothing is saved and no
    stock is taken."""
    q = await services.call(
        "POST", "/api/orders/quote", caller=customer, scope="orders:read", json=_order_body(items, fulfilment, store_id)
    )
    return Quote(**priced(q, await _store_names()))


@server.tool(title="Place an order", annotations=WRITE)
@typed_errors(ORDER_HINTS)
async def place_order(
    customer: OrdersWriter,
    items: Annotated[Items, Field(description="What to order: exact sku and quantity (1-5) per line")],
    fulfilment: Annotated[FulfilmentType, Field(description="pickup at a store, or delivery to the address on file")],
    store_id: Annotated[str | None, Field(description="Required for pickup: store_id from list_stores")] = None,
) -> OrderSummary:
    """Place an order for the logged-in customer. Only after the customer has seen the quote and confirmed it.
    Pickup orders take the units off the store's shelf."""
    o = await services.call(
        "POST", "/api/orders", caller=customer, scope="orders:write", json=_order_body(items, fulfilment, store_id)
    )
    return order_summary(o, await _store_names())


@server.tool(title="Cancel an order", annotations=WRITE_IDEMPOTENT_DESTRUCTIVE)
@typed_errors({**LOOKUP_HINTS, ErrorCode.CONFLICT: "Tell the customer why it can no longer be cancelled."})
async def cancel_order(
    customer: OrdersWriter,
    order_id: Annotated[str, Field(description="Order id the customer gave or list_my_orders returned")],
) -> OrderSummary:
    """Cancel one of the customer's orders that has not shipped or been picked up yet. Pickup units go back on the
    shelf."""
    o = await services.call("POST", f"/api/orders/{order_id}/cancel", caller=customer, scope="orders:write")
    return order_summary(o, await _store_names())
