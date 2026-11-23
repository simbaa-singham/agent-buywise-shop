"""Inventory tool results (ADR-054)."""

from pydantic import Field

from ...core.models import Availability, Money, ToolModel


class Store(ToolModel):
    store_id: str
    name: str
    address: str
    city: str
    state: str
    hours: dict[str, str] = Field(description="Opening hours, e.g. {'mon_sat': '10:00-21:00', 'sun': '11:00-18:00'}")

    @classmethod
    def of(cls, s: dict) -> "Store":
        return cls(
            store_id=s["storeId"],
            name=s["name"],
            address=s["address"],
            city=s["city"],
            state=s["state"],
            hours=s.get("hours") or {},
        )


class StoreList(ToolModel):
    stores: list[Store]


class StockRow(ToolModel):
    sku: str
    storage_gb: int | None = None
    size: str | None = None
    color: str | None = None
    list_price: Money
    store_id: str
    store_name: str
    quantity: int = Field(ge=0, description="Units on the shelf now")


class StockReport(ToolModel):
    product_id: str
    model: str
    availability: Availability
    store_id: str | None = Field(None, description="The store asked about; null = every store")
    stock: list[StockRow] = Field(description="One row per variant per store")
    total_units: int = Field(ge=0, description="Sum of quantity over all rows")
