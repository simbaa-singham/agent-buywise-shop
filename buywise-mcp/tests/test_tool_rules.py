"""Rules every tool must follow (ADR-051, ADR-054) - checked on the real servers, in-process, no services needed.
A new tool that breaks one of these fails here before anyone reviews its snapshot."""

import pytest
from mcp import Client

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
