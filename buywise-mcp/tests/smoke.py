"""Calls each MCP domain server over HTTP. Needs services (8081) and MCP (8090) running: uv run python tests/smoke.py"""
import asyncio
import json

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

BASE = "http://localhost:8090/mcp"


async def tool(domain: str, name: str, args: dict, customer: str | None = None):
    http = httpx2.AsyncClient(headers={"X-Customer-Id": customer} if customer else {})
    async with Client(streamable_http_client(f"{BASE}/{domain}", http_client=http)) as client:
        result = await client.call_tool(name, args)
        text = result.content[0].text if result.content else ""
        print(f"{domain}.{name}: error={result.is_error} {text[:300]}")
        return result


async def main():
    async with Client(f"{BASE}/orders") as client:
        print("orders tools:", [t.name for t in (await client.list_tools()).tools])
    await tool("catalog", "search_products", {"query": "iPhone 18 Pro"})
    await tool("inventory", "check_stock", {"product_id": "ph-18pro", "store_id": "st-aus"})
    await tool("orders", "list_my_orders", {"limit": 1})  # no customer -> error
    await tool("orders", "list_my_orders", {"limit": 1}, customer="cu-demo")
    await tool("orders", "quote_order", {"items": [{"sku": "PH-18PRO-256GB-BLACK", "quantity": 1}],
                                         "fulfilment": "pickup", "store_id": "st-aus"}, customer="cu-demo")


asyncio.run(main())
