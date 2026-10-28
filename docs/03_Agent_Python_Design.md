# Agent (`buywise-agent`) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose and responsibilities
Understand customer messages, route to the right handler, call tools and knowledge, and respond safely.

## 2. Technology and versions
| Concern | Choice |
|---|---|
| Orchestration | LangGraph 1.2 + Postgres checkpointer |
| Agent API | FastAPI (async) |
| MCP client | MCP Python SDK v2, calling `buywise-mcp` (spec 2026-07-28) |
| LLM | Ollama `qwen2.5:7b` (dev); model gateway -> vLLM or hosted API (prod) |
| Tracing | OpenTelemetry -> Langfuse |
| Evaluation | DeepEval scenario suites in CI |

## 3. Deployable
- `buywise-agent`: Agent API + LangGraph graph + RAG pipeline; tools only via `buywise-mcp`.
- Stateless instances (state in Postgres checkpointer); 2 replicas locally.

## 4. Graph design
- **State:** conversation_id, customer_id, messages, intent, confidence, sentiment, tool_results, owner (bot/staff).
- **Nodes:** load_context -> sentiment_check -> route_intent -> handler -> guardrails -> respond.
- **Handlers:** browse/recommend, product_question, compatibility, stock_check, place_order, order_status, store_question, out_of_scope, handoff.

## 5. Intents and tool scoping
| Intent | Tools |
|---|---|
| browse / recommend | `search_products`, `get_product`, `search_knowledge` |
| product_question | `search_knowledge`, `get_product` |
| compatibility | `check_compatibility`, `search_knowledge` |
| stock_check | `check_stock` |
| place_order | `create_cart`, `add_to_cart`, `get_cart`, `checkout` |
| order_status | `verify_customer`, `list_orders`, `get_order_status` |
| store_question | `search_knowledge` |
| out_of_scope / handoff | `create_ticket` |

## 6. Key flows
- Place order and order status - TBD in detail.

## 7. Guardrails and safety
- Prices, stock, status only from tools; no card data; explicit confirmation before checkout; prompt-injection defense; PII masking.

## 8. Testing
- Scenario suite (DeepEval), intent accuracy set - TBD.

## 9. Open decisions
1. Router: LLM classifier vs small fine-tuned classifier.
2. Production LLM choice.
3. User identity propagation BFF -> agent -> `buywise-mcp` -> services (e.g. token exchange RFC 8693 vs passing the user token through). Raised by ADR-021.
4. Agent -> BFF stream format: agent emits ADR-024 contract events directly vs BFF maps an agent-specific stream into the contract.
