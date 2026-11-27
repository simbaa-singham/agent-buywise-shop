"""Catalog MCP server (`/mcp/catalog`): find products and their variants. Read-only."""

from typing import Annotated, Literal

from pydantic import Field

from ...core.errors import ErrorCode, typed_errors
from ...core.identity import CatalogReader
from ...core.services import services
from ...core.tooling import READ, domain_server
from .models import ProductDetail, ProductSearch, ProductSummary

Category = Literal["phone", "tablet", "laptop", "watch", "audio", "accessory"]

server = domain_server("catalog", "The store's product catalog: products, variants, list prices.")


@server.tool(title="Search products", annotations=READ)
@typed_errors({ErrorCode.INVALID_INPUT: "Use a few words of the product name, e.g. 'iPhone 18 Pro'."})
async def search_products(
    caller: CatalogReader,
    query: Annotated[
        str, Field(description="Product name or words from it, e.g. 'iPhone 18 Pro', 'noise cancelling earbuds'")
    ],
    category: Annotated[Category | None, Field(description="Only this kind of product")] = None,
) -> ProductSearch:
    """Find products by name or words. Returns up to 5 matches, best first, each with its product_id and lowest
    price. Use the product_id with get_product (specs, variants) or check_stock (stock)."""
    found = await services.call(
        "GET",
        "/api/products",
        caller=caller,
        scope="catalog:read",
        params={"q": query, "category": category or "", "limit": 5},
    )
    return ProductSearch(query=query, products=[ProductSummary.of(p) for p in found])


@server.tool(title="Product details", annotations=READ)
@typed_errors({ErrorCode.NOT_FOUND: "Call search_products to find the right product_id."})
async def get_product(
    caller: CatalogReader,
    product_id: Annotated[str, Field(description="product_id from search_products, e.g. 'ph-18pro'")],
) -> ProductDetail:
    """Full details of one product: specs and every variant with its exact sku, storage, size, color and list
    price. Call this before ordering to get the exact sku."""
    return ProductDetail.of(
        await services.call("GET", f"/api/products/{product_id}", caller=caller, scope="catalog:read")
    )
