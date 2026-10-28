# Agent (Python) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose and responsibilities
Understand customer messages, route to the right handler, call tools and knowledge, and respond safely.

## 2. Technology and versions
| Concern | Choice |
|---|---|
| Orchestration | LangGraph 1.2 + Postgres checkpointer |
| Agent API | FastAPI (async) |
| MCP client | MCP Python SDK v2 |
| LLM | Ollama `qwen2.5:7b` (dev); model gateway -> vLLM or hosted API (prod) |
| Tracing | OpenTelemetry -> Langfuse |
| Evaluation | DeepEval scenario suites in CI |

## 3. Graph design
- **State:** conversation_id, customer_id, messages, intent, confidence, sentiment, tool_results, owner (bot/staff).
- **Nodes:** load_context -> sentiment_check -> route_intent -> handler -> guardrails -> respond.
- **Handlers:** browse/recommend, product_question, compatibility, stock_check, place_order, order_status, store_question, out_of_scope, handoff.

## 4. Intents and tool scoping
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

## 5. Key flows
- Place order and order status - TBD in detail.

## 6. Guardrails and safety
- Prices, stock, status only from tools; no card data; explicit confirmation before checkout; prompt-injection defense; PII masking.

## 7. Testing
- Scenario suite (DeepEval), intent accuracy set - TBD.

## 8. Open decisions
1. Router: LLM classifier vs small fine-tuned classifier.
2. Production LLM choice.
