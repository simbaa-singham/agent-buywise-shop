"""Rules every tool must follow (ADR-051, ADR-054) - checked on the real servers, in-process, no services needed.
A new tool that breaks one of these fails here before anyone reviews its snapshot."""

import typing

import pytest
from mcp import Client
from mcp.server.mcpserver import Resolve

from buywise_mcp.app import SERVERS

pytestmark = pytest.mark.anyio


async def all_tools():
    tools = []
    for domain, server in sorted(SERVERS.items()):
        async with Client(server) as client:
            tools += [(domain, t) for t in (await client.list_tools()).tools]
    return tools


def walk(schema: dict, defs: dict):
    """Every property schema inside an output schema, following $ref."""
    if "$ref" in schema:
        schema = defs[schema["$ref"].split("/")[-1]]
    for name, prop in schema.get("properties", {}).items():
        yield name, prop
        for sub in [prop, prop.get("items", {}), *prop.get("anyOf", [])]:
            if "$ref" in sub or "properties" in sub:
                yield from walk(sub, defs)


async def test_every_tool_has_a_description_and_a_typed_object_result():
    for domain, tool in await all_tools():
        assert tool.description and len(tool.description) > 40, f"{domain}.{tool.name}: write a real description"
        schema = tool.output_schema
        assert schema and schema.get("type") == "object", f"{domain}.{tool.name}: return a ToolModel"
        assert set(schema.get("properties", {})) != {"result"}, f"{domain}.{tool.name}: no bare lists, use an object"
        assert schema.get("additionalProperties") is False, f"{domain}.{tool.name}: result model must be strict"


async def test_no_tool_lets_the_model_choose_the_customer():
    for domain, tool in await all_tools():
        args = set(tool.input_schema.get("properties", {}))
        assert not args & {"customer", "customer_id", "customerId", "user_id"}, f"{domain}.{tool.name}: {args}"


async def test_every_argument_is_described_for_the_model():
    for domain, tool in await all_tools():
        for name, prop in tool.input_schema.get("properties", {}).items():
            assert prop.get("description"), f"{domain}.{tool.name}({name}) has no description"


async def test_fields_are_snake_case_and_money_is_a_number():
    for domain, tool in await all_tools():
        defs = tool.output_schema.get("$defs", {})
        for name, prop in walk(tool.output_schema, defs):
            assert name == name.lower(), f"{domain}.{tool.name}: {name} is not snake_case"
            if name in {"price", "list_price", "from_price", "unit_price", "subtotal", "tax", "total", "shipping_fee"}:
                assert prop.get("type") == "number", f"{domain}.{tool.name}: {name} must be a number"


async def test_every_tool_declares_all_four_annotations_and_a_title():
    """The agent's policy (confirm, retry, cache) trusts these hints, so none may be left to a default (ADR-053)."""
    for domain, tool in await all_tools():
        a = tool.annotations
        assert a and tool.title, f"{domain}.{tool.name}: needs title + annotations"
        hints = (a.read_only_hint, a.destructive_hint, a.idempotent_hint, a.open_world_hint)
        assert None not in hints, f"{domain}.{tool.name}: set all four hints"
        if a.read_only_hint:
            assert not a.destructive_hint and a.idempotent_hint, f"{domain}.{tool.name}: read-only must be safe"


async def test_tool_lists_are_cacheable_and_versioned():
    for domain, server in sorted(SERVERS.items()):
        async with Client(server) as client:
            listing = await client.list_tools()
            assert client.server_info.version == "1.0.0", domain
        assert listing.ttl_ms == 600_000 and listing.cache_scope == "public", domain


def test_every_tool_checks_its_caller():
    """ADR-050/051: no tool without a resolved, checked caller (scope; plus role + customer for order tools)."""
    for domain, server in sorted(SERVERS.items()):
        for tool in server._tool_manager.list_tools():
            hints = typing.get_type_hints(tool.fn, include_extras=True)
            checks = [
                m.fn.__name__ for h in hints.values() for m in getattr(h, "__metadata__", ()) if isinstance(m, Resolve)
            ]
            assert any(c.startswith("requires_") for c in checks), f"{domain}.{tool.name} does not check its caller"
            if domain == "orders":
                assert any(c.startswith("requires_orders_") for c in checks), f"{domain}.{tool.name}"
