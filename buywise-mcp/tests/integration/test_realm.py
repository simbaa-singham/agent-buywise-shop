"""The buywise realm as imported from buywise-realm.json (ADR-050): what every token in the chain carries.
user (aud agent) -> agent swaps -> aud mcp -> MCP swaps -> aud services; guests use the agent's own token."""

import pytest

from .keycloak import NO_CUSTOMER_ROLE, claims

pytestmark = pytest.mark.integration

TOOL_SCOPES = {"catalog:read", "inventory:read", "orders:read", "orders:write"}


def aud(c: dict) -> set[str]:
    a = c.get("aud", [])
    return {a} if isinstance(a, str) else set(a)


def roles(c: dict) -> set[str]:
    return set(c.get("realm_access", {}).get("roles", []))


def test_user_token_is_for_the_agent_and_carries_who_and_what(keycloak):
    c = claims(keycloak.user_token("demo"))
    assert c["iss"] == keycloak.issuer and "buywise-agent" in aud(c) and c["azp"] == "buywise-customer-web"
    assert c["customer_id"] == "cu-demo" and "customer" in roles(c)
    assert TOOL_SCOPES <= set(c["scope"].split())


def test_agent_swaps_for_an_mcp_token_with_fewer_scopes(keycloak):
    r = keycloak.exchange("buywise-agent", keycloak.user_token("demo"), "buywise-mcp", "catalog:read orders:read")
    assert r.status_code == 200, r.text
    c = claims(r.json()["access_token"])
    assert "buywise-mcp" in aud(c) and c["azp"] == "buywise-agent"
    assert set(c["scope"].split()) == {"catalog:read", "orders:read"}
    assert c["customer_id"] == "cu-demo" and "customer" in roles(c)  # who survives the swap


def test_mcp_swaps_again_for_a_services_token(keycloak):
    mcp_token = keycloak.exchange("buywise-agent", keycloak.user_token("demo"), "buywise-mcp").json()["access_token"]
    r = keycloak.exchange("buywise-mcp", mcp_token, "buywise-services", "orders:read")
    assert r.status_code == 200, r.text
    c = claims(r.json()["access_token"])
    assert "buywise-services" in aud(c) and c["azp"] == "buywise-mcp" and c["scope"] == "orders:read"
    assert c["customer_id"] == "cu-demo"


def test_no_token_passthrough_mcp_cannot_use_the_users_token(keycloak):
    r = keycloak.exchange("buywise-mcp", keycloak.user_token("demo"), "buywise-services")
    assert r.status_code == 403  # the user's token is not for MCP


def test_the_agent_cannot_jump_straight_to_services(keycloak):
    r = keycloak.exchange("buywise-agent", keycloak.user_token("demo"), "buywise-services")
    assert r.status_code == 400  # services is not an audience the agent may ask for


def test_the_customer_web_cannot_swap_tokens(keycloak):
    r = keycloak.exchange("buywise-customer-web", keycloak.user_token("demo"), "buywise-mcp")
    assert r.status_code in (400, 401, 403)


def test_guest_token_is_the_agents_own_read_only_token(keycloak):
    c = claims(keycloak.client_token("buywise-agent", "catalog:read inventory:read"))
    assert "buywise-mcp" in aud(c) and c["azp"] == "buywise-agent"
    assert set(c["scope"].split()) == {"catalog:read", "inventory:read"}
    assert "customer_id" not in c and "customer" not in roles(c)


def test_without_the_customer_role_the_token_says_so(keycloak):
    c = claims(keycloak.user_token(NO_CUSTOMER_ROLE))
    assert c["customer_id"] and "customer" not in roles(c)  # MCP and services refuse order tools for this user
