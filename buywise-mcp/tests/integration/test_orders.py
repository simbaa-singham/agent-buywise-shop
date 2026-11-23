"""Orders tools against real services + Postgres (ADR-051, ADR-054, ADR-055).
Confirmation before place/cancel arrives in step 5 (ADR-052); its tests are written then."""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.anyio]

STORE = "st-aus"


def err(result) -> dict:
    assert result.is_error, f"expected a tool error, got {result.structured_content}"
    return result.structured_content


@pytest.fixture
def sku(stack) -> str:
    """A pickup-able variant with at least 2 units at the store."""
    return stack.sql(
        f"SELECT s.sku FROM inventory.stock s JOIN catalog.variants v USING (sku) JOIN catalog.products p "
        f"USING (product_id) WHERE s.store_id = '{STORE}' AND p.availability = 'available' AND s.quantity >= 2 "
        "ORDER BY s.sku LIMIT 1"
    )


def stock(stack, sku: str) -> int:
    return int(stack.sql(f"SELECT quantity FROM inventory.stock WHERE store_id = '{STORE}' AND sku = '{sku}'"))


def pickup(sku: str, quantity: int = 1) -> dict:
    return {"items": [{"sku": sku, "quantity": quantity}], "fulfilment": "pickup", "store_id": STORE}


# --- identity --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("tool", "args"),
    [
        ("list_my_orders", {}),
        ("get_order", {"order_id": "BW-1"}),
        ("quote_order", pickup("X")),
        ("place_order", pickup("X")),
        ("cancel_order", {"order_id": "BW-1"}),
    ],
)
async def test_every_order_tool_needs_a_logged_in_customer(call, tool, args):
    e = err(await call("orders", tool, args))
    assert e["code"] == "not_logged_in" and e["hint"]


async def test_another_customers_order_is_not_found(call, stack):
    order_id = stack.sql("SELECT order_id FROM orders.orders WHERE customer_id = 'cu-demo' LIMIT 1")
    own = (await call("orders", "get_order", {"order_id": order_id}, customer="cu-demo")).structured_content
    assert own["order_id"] == order_id
    e = err(await call("orders", "get_order", {"order_id": order_id}, customer="cu-0002"))
    assert e["code"] == "not_found" and "list_my_orders" in e["hint"]


# --- reading ---------------------------------------------------------------------------------------------------
async def test_list_my_orders_newest_first_with_store_names(call):
    orders = (await call("orders", "list_my_orders", {"limit": 5}, customer="cu-demo")).structured_content["orders"]
    assert orders and len(orders) <= 5
    assert [o["placed_at"] for o in orders] == sorted((o["placed_at"] for o in orders), reverse=True)
    for o in orders:
        if o["fulfilment"]["type"] == "pickup":
            assert o["fulfilment"]["store_name"]


async def test_delivery_orders_show_city_and_state_but_no_street(call, stack):
    customer = stack.sql("SELECT customer_id FROM orders.orders WHERE fulfilment->>'type' = 'delivery' LIMIT 1")
    orders = (await call("orders", "list_my_orders", {"limit": 20}, customer=customer)).structured_content["orders"]
    delivery = next(o for o in orders if o["fulfilment"]["type"] == "delivery")
    assert delivery["fulfilment"]["ship_to_state"]
    assert "address" not in delivery["fulfilment"] and "street" not in str(delivery).lower()


async def test_bad_arguments_are_rejected_by_the_sdk_before_services(call):
    r = await call("orders", "list_my_orders", {"limit": 0}, customer="cu-demo")
    assert r.is_error and "greater than or equal to 1" in r.content[0].text


# --- quote -----------------------------------------------------------------------------------------------------
async def test_quote_prices_without_saving_or_taking_stock(call, stack, sku):
    orders_before, stock_before = stack.sql("SELECT count(*) FROM orders.orders"), stock(stack, sku)
    q = (await call("orders", "quote_order", pickup(sku, 2), customer="cu-demo")).structured_content
    assert q["currency"] == "USD" and q["fulfilment"]["store_name"] == "BuyWise Austin"
    assert q["subtotal"] == round(2 * q["items"][0]["unit_price"], 2)
    assert q["total"] == round(q["subtotal"] + q["shipping_fee"] + q["tax"], 2)
    assert stack.sql("SELECT count(*) FROM orders.orders") == orders_before and stock(stack, sku) == stock_before


async def test_quote_accepts_a_lower_case_sku(call, sku):
    q = (await call("orders", "quote_order", pickup(sku.lower()), customer="cu-demo")).structured_content
    assert q["items"][0]["sku"] == sku


async def test_unknown_sku_is_invalid_input_with_a_hint_from_mcp(call):
    e = err(await call("orders", "quote_order", pickup("NOPE-123"), customer="cu-demo"))
    assert e["code"] == "invalid_input" and e["message"] == "Unknown SKU NOPE-123" and "get_product" in e["hint"]


async def test_pickup_without_a_store_is_invalid_input(call, sku):
    args = {"items": [{"sku": sku, "quantity": 1}], "fulfilment": "pickup"}
    assert err(await call("orders", "quote_order", args, customer="cu-demo"))["code"] == "invalid_input"


async def test_more_than_the_shelf_holds_is_a_conflict(call, stack, sku):
    args = pickup(sku, 5)
    stack.sql(f"UPDATE inventory.stock SET quantity = 1 WHERE store_id = '{STORE}' AND sku = '{sku}'")
    try:
        e = err(await call("orders", "place_order", args, customer="cu-demo"))
        assert e["code"] == "conflict" and "Not enough stock" in e["message"]
        assert stock(stack, sku) == 1
    finally:
        stack.sql(f"UPDATE inventory.stock SET quantity = 10 WHERE store_id = '{STORE}' AND sku = '{sku}'")


# --- place and cancel ------------------------------------------------------------------------------------------
async def test_place_takes_stock_and_cancel_gives_it_back(call, stack, sku):
    before = stock(stack, sku)
    o = (await call("orders", "place_order", pickup(sku), customer="cu-demo")).structured_content
    assert o["status"] == "placed" and o["order_id"].startswith("BW-") and o["held_at_store_until"]
    assert stock(stack, sku) == before - 1

    c = (await call("orders", "cancel_order", {"order_id": o["order_id"]}, customer="cu-demo")).structured_content
    assert c["status"] == "cancelled" and stock(stack, sku) == before

    e = err(await call("orders", "cancel_order", {"order_id": o["order_id"]}, customer="cu-demo"))
    assert e["code"] == "conflict" and stock(stack, sku) == before
