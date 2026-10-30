# buywise-mcp - Learning Notes

## Local end-to-end build (2026-10-30)
- **MCP** = a standard way to offer tools to an AI: each tool has a name, description and JSON input schema; the agent lists and calls them over HTTP.
- **Layout (ADR-031):** one process, one server per domain: `/mcp/catalog` (search_products, get_product), `/mcp/inventory` (list_stores, check_stock), `/mcp/orders` (list_my_orders, get_order, quote_order, place_order, cancel_order).
- **SDK v2:** `MCPServer` + `@server.tool()`; stateless streamable HTTP; tool errors raised as `ToolError` so the reason reaches the model.
- **Try:** `make -C buywise-mcp smoke`.
