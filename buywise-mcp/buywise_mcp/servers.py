"""One MCP server per business domain (ADR-031): /mcp/catalog, /mcp/inventory, /mcp/orders.

Tools return compact data: prices and stock always come from here, never from the model (NFR 8).
The customer is taken from the X-Customer-Id header the agent sets from the logged-in session; it is never a
tool argument (ADR-028, simplified locally: no token exchange yet).
"""
from mcp.server.mcpserver import Context, MCPServer

from .services import ServiceError, call

catalog = MCPServer("buywise-catalog", instructions="Search the store's product catalog.")
inventory = MCPServer("buywise-inventory", instructions="Stores and stock levels.")
orders = MCPServer("buywise-orders", instructions="The logged-in customer's orders.")


def _customer(ctx: Context) -> str:
    customer_id = (ctx.headers or {}).get("x-customer-id")
    if not customer_id:
        raise ServiceError("The customer is not logged in. Ask them to log in first.")
    return customer_id


# --- catalog ---------------------------------------------------------------------------------------------------
@catalog.tool()
async def search_products(query: str, category: str | None = None) -> list[dict]:
    """Find products by name or words, e.g. "iPhone 18 Pro", "noise cancelling earbuds".
    category is optional: phone, tablet, laptop, watch, audio or accessory."""
    return await call("GET", "/api/products", params={"q": query, "category": category or "", "limit": 5})


@catalog.tool()
async def get_product(product_id: str) -> dict:
    """Full details of one product: specs, and every variant (sku, storage, size, color, list price)."""
    return await call("GET", f"/api/products/{product_id}")


# --- inventory -------------------------------------------------------------------------------------------------
@inventory.tool()
async def list_stores() -> list[dict]:
    """All stores with store_id, city, address and opening hours."""
    stores = await call("GET", "/api/stores")
    return [{k: s[k] for k in ("storeId", "name", "address", "city", "state", "hours")} for s in stores]


@inventory.tool()
async def check_stock(product_id: str, store_id: str | None = None) -> dict:
    """Units in stock for every variant of a product, at one store (store_id) or at all stores."""
    product = await call("GET", f"/api/products/{product_id}")
    variants = {v["sku"]: v for v in product["variants"]}
    levels = await call("GET", "/api/stock", params={"skus": list(variants), "storeId": store_id or None})
    rows = [{"sku": s["sku"], "storage_gb": variants[s["sku"]].get("storageGb"), "size": variants[s["sku"]].get("size"),
             "color": variants[s["sku"]]["color"], "price": variants[s["sku"]]["listPrice"],
             "store": s["storeName"], "store_id": s["storeId"], "quantity": s["quantity"]} for s in levels]
    return {"product_id": product_id, "model": product["model"], "availability": product["availability"],
            "stock": [{k: v for k, v in r.items() if v is not None} for r in rows]}


# --- orders ----------------------------------------------------------------------------------------------------
@orders.tool()
async def list_my_orders(ctx: Context, limit: int = 5) -> list[dict]:
    """The logged-in customer's most recent orders (newest first)."""
    result = await call("GET", "/api/orders", customer_id=_customer(ctx), params={"limit": limit})
    return [_order_summary(o) for o in result]


@orders.tool()
async def get_order(ctx: Context, order_id: str) -> dict:
    """One order of the logged-in customer by its id, e.g. BW-100000."""
    return _order_summary(await call("GET", f"/api/orders/{order_id}", customer_id=_customer(ctx)))


@orders.tool()
async def quote_order(ctx: Context, items: list[dict], fulfilment: str, store_id: str | None = None) -> dict:
    """Price an order without placing it. items: [{"sku": "...", "quantity": 1}]; fulfilment: pickup or delivery
    (pickup needs store_id; delivery goes to the address on file)."""
    body = {"items": items, "fulfilment": fulfilment, "storeId": store_id}
    return _order_summary(await call("POST", "/api/orders/quote", customer_id=_customer(ctx), json=body))


@orders.tool()
async def place_order(ctx: Context, items: list[dict], fulfilment: str, store_id: str | None = None) -> dict:
    """Place an order. Only after the customer explicitly confirmed the quote."""
    body = {"items": items, "fulfilment": fulfilment, "storeId": store_id}
    return _order_summary(await call("POST", "/api/orders", customer_id=_customer(ctx), json=body))


@orders.tool()
async def cancel_order(ctx: Context, order_id: str) -> dict:
    """Cancel an order that has not shipped or been picked up yet."""
    return _order_summary(await call("POST", f"/api/orders/{order_id}/cancel", customer_id=_customer(ctx)))


def _order_summary(o: dict) -> dict:
    keep = ("orderId", "placedAt", "status", "fulfilment", "subtotal", "tax", "total", "trackingNumber",
            "pickupHoldUntil", "items")
    return {k: o[k] for k in keep if o.get(k) is not None}
