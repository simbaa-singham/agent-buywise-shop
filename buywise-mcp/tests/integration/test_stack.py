"""Checks the integration test stack itself (not any tool): services healthy, seed data loaded, MCP answering.
Tool tests are written from the Phase M design (ADR-050 to ADR-064), test-first, as each part is built."""
import httpx
import pytest

pytestmark = pytest.mark.integration


def test_services_is_healthy_and_seeded(stack):
    assert httpx.get(f"{stack.services_url}/actuator/health").json()["status"] == "UP"
    assert stack.sql("SELECT count(*) FROM catalog.products") == "50"
    assert stack.sql("SELECT count(*) FROM inventory.stores") == "10"
    assert int(stack.sql("SELECT count(*) FROM orders.orders")) > 0


def test_mcp_is_up(mcp_url):
    assert httpx.get(mcp_url.removesuffix("/mcp") + "/health").json() == {"status": "UP"}
