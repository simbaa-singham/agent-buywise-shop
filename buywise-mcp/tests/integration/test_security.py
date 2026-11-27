"""Who may do what (ADR-050): scope + role + owner, checked by MCP and again by services, with real Keycloak tokens."""

import httpx
import pytest

from .keycloak import NO_CUSTOMER_ROLE, USERS

pytestmark = pytest.mark.integration


def err(result) -> dict:
    assert result.is_error, f"expected a tool error, got {result.structured_content}"
    return result.structured_content


# --- MCP refuses tokens that are not for it --------------------------------------------------------------------
def test_mcp_without_a_token_answers_401_with_resource_metadata(mcp_url):
    r = httpx.post(
        f"{mcp_url}/catalog",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Accept": "application/json, text/event-stream"},
    )
    assert r.status_code == 401
    assert "oauth-protected-resource/mcp/catalog" in r.headers["www-authenticate"]  # RFC 9728 pointer


def test_resource_metadata_names_our_keycloak_realm(mcp_url):
    base = mcp_url.removesuffix("/mcp")
    meta = httpx.get(f"{base}/.well-known/oauth-protected-resource/mcp/orders").json()
    assert meta["resource"].endswith("/mcp/orders") and meta["authorization_servers"][0].endswith("/realms/buywise")


def test_mcp_refuses_the_users_own_token_no_passthrough(mcp_url, keycloak):
    user = keycloak.user_token("demo")  # aud = buywise-agent, not MCP
    r = httpx.post(
        f"{mcp_url}/catalog",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Authorization": f"Bearer {user}", "Accept": "application/json, text/event-stream"},
    )
    assert r.status_code == 401


def test_mcp_refuses_a_forged_token(mcp_url, mcp_token):
    head, body, _ = mcp_token("cu-demo").split(".")
    r = httpx.post(
        f"{mcp_url}/catalog",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={
            "Authorization": f"Bearer {head}.{body}.bm90LWEtc2lnbmF0dXJl",
            "Accept": "application/json, text/event-stream",
        },
    )
    assert r.status_code == 401


# --- per tool: scope, role, customer ---------------------------------------------------------------------------
@pytest.mark.anyio
async def test_guest_may_browse_but_not_see_orders(call):
    assert not (await call("catalog", "search_products", {"query": "iPhone"})).is_error
    assert not (await call("inventory", "list_stores", {})).is_error
    assert err(await call("orders", "list_my_orders", {}))["code"] == "not_logged_in"


@pytest.mark.anyio
async def test_a_token_without_the_tools_scope_is_forbidden(call, mcp_token):
    read_only = mcp_token("cu-demo", scope="catalog:read inventory:read orders:read")
    e = err(await call("orders", "cancel_order", {"order_id": "BW-1"}, token=read_only))
    assert e["code"] == "forbidden" and "orders:write" in e["message"]


@pytest.mark.anyio
async def test_a_login_without_the_customer_role_cannot_use_order_tools(call):
    e = err(await call("orders", "list_my_orders", {}, customer=USERS[NO_CUSTOMER_ROLE]))
    assert e["code"] == "forbidden" and "not a customer account" in e["message"]


@pytest.mark.anyio
async def test_the_customer_comes_from_the_token(call, stack):
    mine = (await call("orders", "list_my_orders", {"limit": 20}, customer="cu-demo")).structured_content["orders"]
    db = stack.sql(
        "SELECT string_agg(order_id, ',' ORDER BY placed_at DESC) FROM "
        "(SELECT order_id, placed_at FROM orders.orders WHERE customer_id = 'cu-demo' "
        "ORDER BY placed_at DESC LIMIT 20) t"
    )
    assert [o["order_id"] for o in mine] == db.split(",")


# --- services checks again, on its own -------------------------------------------------------------------------
def test_services_refuse_requests_without_a_token(stack):
    assert httpx.get(f"{stack.services_url}/api/products").status_code == 401
    assert httpx.get(f"{stack.services_url}/actuator/health").status_code == 200  # only the health check is open


def test_services_refuse_a_token_for_mcp(stack, mcp_token):
    r = httpx.get(f"{stack.services_url}/api/products", headers={"Authorization": f"Bearer {mcp_token('cu-demo')}"})
    assert r.status_code == 401  # aud buywise-mcp, not buywise-services


def test_services_check_the_scope_per_endpoint(stack, keycloak, mcp_token):
    catalog_only = keycloak.exchange("buywise-mcp", mcp_token("cu-demo"), "buywise-services", "catalog:read")
    h = {"Authorization": f"Bearer {catalog_only.json()['access_token']}"}
    assert httpx.get(f"{stack.services_url}/api/products", headers=h).status_code == 200
    assert httpx.get(f"{stack.services_url}/api/orders", headers=h).status_code == 403


def test_customers_me_returns_only_the_callers_record(stack, keycloak, mcp_token):
    t = keycloak.exchange("buywise-mcp", mcp_token("cu-demo"), "buywise-services", "orders:read").json()
    h = {"Authorization": f"Bearer {t['access_token']}"}
    assert httpx.get(f"{stack.services_url}/api/customers/me", headers=h).json()["customerId"] == "cu-demo"
    assert httpx.get(f"{stack.services_url}/api/customers/cu-0002", headers=h).status_code == 403  # gone: denied


@pytest.mark.anyio
async def test_every_tool_call_writes_one_audit_line(call, caplog):
    """No act claim in Keycloak 26.4, so each hop logs who acted for whom (ADR-050 amendment)."""
    import json

    caplog.set_level("INFO", logger="buywise_mcp.audit")
    await call("orders", "list_my_orders", {"limit": 1}, customer="cu-demo")
    await call("orders", "list_my_orders", {})  # guest
    lines = [json.loads(r.getMessage()) for r in caplog.records if r.name == "buywise_mcp.audit"]
    ok, refused = lines[-2], lines[-1]
    assert ok | {"sub": None} == {
        "event": "tool_call",
        "tool": "list_my_orders",
        "result": "ok",
        "client": "buywise-mcp",
        "sub": None,
        "customer_id": "cu-demo",
        "azp": "buywise-agent",
    }
    assert ok["sub"] and refused["result"] == "not_logged_in"
