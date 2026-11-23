"""Orders tool inputs and results (ADR-054). Delivery addresses are reduced to city and state: the model needs to
say where an order goes, not the street (least personal data, ADR-036)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ...core.models import Money, ToolModel

OrderStatus = Literal[
    "placed",
    "processing",
    "ready_for_pickup",
    "picked_up",
    "shipped",
    "out_for_delivery",
    "delayed",
    "delivered",
    "cancelled",
]


class OrderLineInput(BaseModel):
    sku: str = Field(description="Exact variant sku from get_product or check_stock, e.g. PH-18PRO-256GB-SILVER")
    quantity: int = Field(1, ge=1, le=5)


class Fulfilment(ToolModel):
    type: Literal["pickup", "delivery"]
    store_id: str | None = None
    store_name: str | None = None
    method: str | None = Field(None, description="Delivery method, e.g. standard")
    ship_to_city: str | None = None
    ship_to_state: str | None = None

    @classmethod
    def of(cls, f: dict, store_names: dict[str, str]) -> "Fulfilment":
        address = f.get("address") or {}
        return cls(
            type=f["type"],
            store_id=f.get("store_id"),
            store_name=store_names.get(f.get("store_id") or ""),
            method=f.get("method"),
            ship_to_city=address.get("city"),
            ship_to_state=address.get("state"),
        )


class OrderLine(ToolModel):
    sku: str
    product_id: str
    model: str
    quantity: int
    unit_price: Money

    @classmethod
    def of(cls, i: dict) -> "OrderLine":
        return cls(
            sku=i["sku"], product_id=i["productId"], model=i["model"], quantity=i["quantity"], unit_price=i["unitPrice"]
        )


class _Priced(ToolModel):
    fulfilment: Fulfilment
    items: list[OrderLine]
    subtotal: Money
    shipping_fee: Money
    tax: Money
    total: Money
    currency: Literal["USD"] = "USD"
    held_at_store_until: datetime | None = Field(None, description="Pickup orders: last day the store keeps it")


class Quote(_Priced):
    """What the order would cost; nothing is saved and no stock is taken."""


class OrderSummary(_Priced):
    order_id: str
    status: OrderStatus
    placed_at: datetime
    tracking_number: str | None = None


class OrderList(ToolModel):
    orders: list[OrderSummary] = Field(description="Newest first")


def priced(o: dict, store_names: dict[str, str]) -> dict:
    return {
        "fulfilment": Fulfilment.of(o["fulfilment"], store_names),
        "items": [OrderLine.of(i) for i in o["items"]],
        "subtotal": o["subtotal"],
        "shipping_fee": o.get("shippingFee") or 0,
        "tax": o["tax"],
        "total": o["total"],
        "held_at_store_until": o.get("pickupHoldUntil"),
    }


def order_summary(o: dict, store_names: dict[str, str]) -> OrderSummary:
    return OrderSummary(
        order_id=o["orderId"],
        status=o["status"],
        placed_at=o["placedAt"],
        tracking_number=o.get("trackingNumber"),
        **priced(o, store_names),
    )
