"""Catalog and inventory tools against real services + Postgres (ADR-054/055). Each call is also validated against
the tool's output schema by the `call` fixture."""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.anyio]


def err(result) -> dict:
    assert result.is_error, f"expected a tool error, got {result.structured_content}"
    return result.structured_content


async def test_search_ranks_the_exact_model_first(call):
    r = (await call("catalog", "search_products", {"query": "iPhone 18 Pro"})).structured_content
    assert r["query"] == "iPhone 18 Pro"
    assert r["products"][0]["product_id"] == "ph-18pro" and len(r["products"]) <= 5
    assert isinstance(r["products"][0]["from_price"], float)


async def test_search_can_filter_by_category(call):
    r = (await call("catalog", "search_products", {"query": "pro", "category": "laptop"})).structured_content
    assert r["products"] and {p["category"] for p in r["products"]} == {"laptop"}


async def test_search_with_no_match_is_an_empty_list_not_an_error(call):
    r = await call("catalog", "search_products", {"query": "zzzz-no-such-thing"})
    assert not r.is_error and r.structured_content["products"] == []


async def test_get_product_has_every_variant_with_a_price(call, stack):
    p = (await call("catalog", "get_product", {"product_id": "ph-18pro"})).structured_content
    expected = int(stack.sql("SELECT count(*) FROM catalog.variants WHERE product_id = 'ph-18pro'"))
    assert len(p["variants"]) == expected
    assert all(v["sku"] and v["list_price"] > 0 for v in p["variants"])


async def test_preorder_product_says_when_it_ships(call, stack):
    product_id = stack.sql("SELECT product_id FROM catalog.products WHERE availability = 'preorder' LIMIT 1")
    if not product_id:
        pytest.skip("no preorder product in the seed data")
    p = (await call("catalog", "get_product", {"product_id": product_id})).structured_content
    assert p["availability"] == "preorder" and p["ships_on"]


async def test_unknown_product_is_not_found_with_a_hint(call):
    e = err(await call("catalog", "get_product", {"product_id": "nope-1"}))
    assert e["code"] == "not_found" and "search_products" in e["hint"]


async def test_list_stores_has_hours_for_every_store(call):
    stores = (await call("inventory", "list_stores", {})).structured_content["stores"]
    assert len(stores) == 10 and all(s["hours"] for s in stores)


async def test_stock_at_one_store_equals_the_database(call, stack):
    r = (await call("inventory", "check_stock", {"product_id": "ph-18pro", "store_id": "st-aus"})).structured_content
    assert r["store_id"] == "st-aus" and {row["store_id"] for row in r["stock"]} == {"st-aus"}
    db = stack.sql(
        "SELECT sum(s.quantity) FROM inventory.stock s JOIN catalog.variants v USING (sku) "
        "WHERE v.product_id = 'ph-18pro' AND s.store_id = 'st-aus'"
    )
    assert r["total_units"] == int(db) == sum(row["quantity"] for row in r["stock"])


async def test_stock_at_every_store_covers_all_stores(call):
    r = (await call("inventory", "check_stock", {"product_id": "ph-18pro"})).structured_content
    assert r["store_id"] is None and len({row["store_id"] for row in r["stock"]}) == 10


async def test_stock_at_an_unknown_store_is_not_found_not_zero(call):
    e = err(await call("inventory", "check_stock", {"product_id": "ph-18pro", "store_id": "st-nowhere"}))
    assert e["code"] == "not_found"
