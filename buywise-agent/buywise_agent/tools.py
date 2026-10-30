"""Tools the model may call: MCP tools on buywise-mcp (one server per domain, ADR-031) plus knowledge search.
The customer id travels as a header set from the logged-in session - never as a tool argument (ADR-028)."""
import asyncio
import json

import httpx2
from langchain_core.tools import StructuredTool
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from pydantic import BaseModel, Field

from .config import settings
from .rag.search import search

TOOL_DOMAIN = {
    "search_products": "catalog", "get_product": "catalog",
    "list_stores": "inventory", "check_stock": "inventory",
    "list_my_orders": "orders", "get_order": "orders", "quote_order": "orders",
    "place_order": "orders", "cancel_order": "orders",
}
STATUS_LABEL = {
    "search_products": "Searching products", "get_product": "Looking up product details",
    "list_stores": "Looking up stores", "check_stock": "Checking stock", "list_my_orders": "Looking up your orders",
    "get_order": "Looking up your order", "quote_order": "Pricing your order", "place_order": "Placing your order",
    "cancel_order": "Cancelling your order", "search_knowledge": "Searching help articles",
}


async def call_mcp(name: str, args: dict, customer_id: str | None) -> tuple[bool, str]:
    """Returns (ok, text). Errors come back as text the model can explain to the customer."""
    http = httpx2.AsyncClient(headers={"X-Customer-Id": customer_id} if customer_id else {}, timeout=20)
    try:
        async with Client(streamable_http_client(f"{settings.mcp_url}/{TOOL_DOMAIN[name]}", http_client=http)) as c:
            result = await c.call_tool(name, args)
        text = "\n".join(getattr(part, "text", "") for part in result.content)
        return (not result.is_error), text
    except Exception as e:  # noqa: BLE001 - any transport failure; tool server down -> the model says it cannot check right now
        return False, f"Tool unavailable: {e}"


# --- schemas the model sees (no customer id anywhere) -------------------------------------------------------------
class SearchProducts(BaseModel):
    query: str = Field(description="Product name or words, e.g. 'iPhone 18 Pro'")
    category: str | None = Field(None, description="phone, tablet, laptop, watch, audio or accessory")


class ProductId(BaseModel):
    product_id: str = Field(description="product_id from search_products, e.g. 'ph-18pro'")


class CheckStock(BaseModel):
    product_id: str = Field(description="product_id from search_products")
    store_id: str | None = Field(None, description="store_id like 'st-aus'; omit for all stores")


class NoArgs(BaseModel):
    pass


class ListOrders(BaseModel):
    limit: int = Field(5, description="How many recent orders")


class OrderId(BaseModel):
    order_id: str = Field(description="An order id the customer typed or one returned by list_my_orders")


class Line(BaseModel):
    sku: str = Field(description="Exact variant sku as returned by get_product or check_stock, e.g. PH-18PRO-256GB-SILVER. If you have not seen it in a tool result, call get_product first.")
    quantity: int = 1


class PlaceOrder(BaseModel):
    items: list[Line]
    fulfilment: str = Field(description="'pickup' or 'delivery'")
    store_id: str | None = Field(None, description="Required for pickup")


class Knowledge(BaseModel):
    query: str = Field(description="The policy or how-to question in the customer's words")


DESCRIPTIONS = {
    "search_products": (SearchProducts, "Find products in the catalog by name or description."),
    "get_product": (ProductId, "Specs and every variant (sku, storage, color, list price) of one product."),
    "list_stores": (NoArgs, "All stores with store_id, city, address and hours."),
    "check_stock": (CheckStock, "Units in stock per variant at one store or all stores."),
    "list_my_orders": (ListOrders, "The logged-in customer's recent orders, newest first. Use this for 'my order', 'my latest order' or when no order id is given."),
    "get_order": (OrderId, "Details of one order. Only with an order id the customer gave or that list_my_orders returned - never guess an id."),
    "place_order": (PlaceOrder, ("Order items for the logged-in customer. The system shows the customer a quote "
                                 "and asks them to confirm before anything is placed.")),
    "cancel_order": (OrderId, "Cancel one of the customer's orders that has not shipped or been picked up."),
    "search_knowledge": (Knowledge, ("Search store policies, FAQs and how-to guides (shipping, pickup, returns, "
                                     "warranty, payment, device setup). Use for any policy question.")),
}


def tool_specs() -> list[StructuredTool]:
    """Tool definitions for bind_tools; execution happens in the graph's tool node."""
    async def _noop(**_):
        return ""
    return [StructuredTool.from_function(coroutine=_noop, name=n, description=d, args_schema=s)
            for n, (s, d) in DESCRIPTIONS.items()]


async def knowledge(query: str) -> tuple[list[dict], str]:
    hits = await asyncio.to_thread(search, query, 4)
    hits = [h for h in hits if h["distance"] < 0.55]
    text = "\n\n".join(f"[{i}] {h['title']} ({h['location'] or 'document'}):\n{h['content']}"
                       for i, h in enumerate(hits, 1)) or "No matching help article."
    return hits, text


def parse(text: str):
    try:
        return json.loads(text)
    except ValueError:
        return None
