"""Inventory MCP server (`/mcp/inventory`): stores and stock. Read-only."""

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ...core.errors import ErrorCode, typed_errors
from ...core.services import services
from .models import StockReport, StockRow, Store, StoreList

server = MCPServer("buywise-inventory", instructions="The store locations and the stock on their shelves.")


@server.tool()
@typed_errors()
async def list_stores() -> StoreList:
    """All stores with store_id, name, address, city, state and opening hours. Use the store_id for check_stock
    and for pickup orders."""
    return StoreList(stores=[Store.of(s) for s in await services.call("GET", "/api/stores")])


@server.tool()
@typed_errors(
    {ErrorCode.NOT_FOUND: "Call search_products to find the right product_id, or list_stores for the store_id."}
)
async def check_stock(
    product_id: Annotated[str, Field(description="product_id from search_products, e.g. 'ph-18pro'")],
    store_id: Annotated[
        str | None, Field(description="store_id from list_stores, e.g. 'st-aus'; omit for every store")
    ] = None,
) -> StockReport:
    """Units on the shelf for every variant of a product, at one store or at every store, with each variant's sku
    and list price. Stock numbers come only from here - never guess them."""
    product = await services.call("GET", f"/api/products/{product_id}")
    variants = {v["sku"]: v for v in product["variants"]}
    # only send storeId when asked: an empty storeId= would match no store at all
    levels = await services.call(
        "GET", "/api/stock", params={"skus": list(variants)} | ({"storeId": store_id} if store_id else {})
    )
    if store_id and not levels:  # services answers an unknown store with an empty list: say so, not "0 in stock"
        await services.call("GET", f"/api/stores/{store_id}")  # 404 -> not_found
    rows = [
        StockRow(
            sku=s["sku"],
            storage_gb=variants[s["sku"]].get("storageGb"),
            size=variants[s["sku"]].get("size"),
            color=variants[s["sku"]].get("color"),
            list_price=variants[s["sku"]]["listPrice"],
            store_id=s["storeId"],
            store_name=s["storeName"],
            quantity=s["quantity"],
        )
        for s in levels
    ]
    return StockReport(
        product_id=product_id,
        model=product["model"],
        availability=product["availability"],
        store_id=store_id,
        stock=rows,
        total_units=sum(r.quantity for r in rows),
    )
