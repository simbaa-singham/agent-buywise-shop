# MCP - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose
Expose domain capabilities to the agent as versioned, scoped, secure tools.

## 2. Technology
- Servers: inside each Java service with Spring AI 2.0 (`@McpTool`), MCP Java SDK 2.0 (spec 2025-11-25 today; 2026-07-28 when Spring AI supports it).
- Client: MCP Python SDK v2 in the agent (negotiates spec version per server).

## 3. Tool contracts (v1)
| Server | Tool | Input | Output |
|---|---|---|---|
| catalog | `search_products` | query, filters | product list |
| catalog | `get_product` | product_id | details, variants, prices |
| catalog | `check_compatibility` | accessory_id, device_model | compatible + note |
| inventory | `check_stock` | variant_id, fulfilment | qty, pickup ready time |
| order | `create_cart` | customer_id (optional) | cart_id |
| order | `add_to_cart` | cart_id, variant_id, qty | cart summary |
| order | `get_cart` | cart_id | items, subtotal, tax, total |
| order | `checkout` | cart_id, fulfilment, address/pickup | order_id, payment_link (confirmation required) |
| order | `list_orders` | customer_id | orders |
| order | `get_order_status` | order_id | status, tracking/pickup info |
| customer | `verify_customer` | email/phone, otp | customer_id |
| helpdesk | `create_ticket` | conversation_id, intent, summary | ticket_id |

## 4. Design rules
- Explicit handles (`cart_id`, `order_id`), no session state.
- Versioned schemas; contract tests in CI; runtime output validation.
- Read tools free; write tools need confirmation.
- OAuth-protected; per-intent tool scoping in the agent.

## 5. Open decisions
1. Move to 2026-07-28 spec timing.
2. Tool-level rate limits.
