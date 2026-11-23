"""Catalog tool results (ADR-054). Mapped from buywise-services JSON (camelCase) to snake_case for the model."""

from datetime import date
from typing import Any

from pydantic import Field

from ...core.models import Availability, Money, ToolModel


class ProductSummary(ToolModel):
    product_id: str
    model: str
    category: str
    family: str
    availability: Availability
    release_date: date | None = None
    from_price: Money = Field(description="Lowest list price of any variant")

    @classmethod
    def of(cls, p: dict) -> "ProductSummary":
        return cls(
            product_id=p["productId"],
            model=p["model"],
            category=p["category"],
            family=p["family"],
            availability=p["availability"],
            release_date=p.get("releaseDate"),
            from_price=p["fromPrice"],
        )


class ProductSearch(ToolModel):
    query: str
    products: list[ProductSummary] = Field(description="Best match first; empty when nothing matches")


class Variant(ToolModel):
    sku: str = Field(description="Exact sku to use in orders")
    storage_gb: int | None = None
    size: str | None = None
    color: str | None = None
    list_price: Money

    @classmethod
    def of(cls, v: dict) -> "Variant":
        return cls(
            sku=v["sku"],
            storage_gb=v.get("storageGb"),
            size=v.get("size"),
            color=v.get("color"),
            list_price=v["listPrice"],
        )


class ProductDetail(ToolModel):
    product_id: str
    model: str
    category: str
    family: str
    availability: Availability
    release_date: date | None = None
    ships_on: date | None = Field(None, description="For preorder products: the date it ships")
    specs: dict[str, Any] = Field(description="Technical specifications as the catalog lists them")
    compatibility_note: str | None = None
    variants: list[Variant]

    @classmethod
    def of(cls, p: dict) -> "ProductDetail":
        return cls(
            product_id=p["productId"],
            model=p["model"],
            category=p["category"],
            family=p["family"],
            availability=p["availability"],
            release_date=p.get("releaseDate"),
            ships_on=p.get("releaseDate") if p["availability"] == "preorder" else None,
            specs=p.get("specs") or {},
            compatibility_note=p.get("compatibilityNote"),
            variants=[Variant.of(v) for v in p.get("variants", [])],
        )
