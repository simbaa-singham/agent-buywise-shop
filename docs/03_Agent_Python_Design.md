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
| LLM | Always via LiteLLM model gateway (OpenAI-compatible API): Ollama `qwen2.5:7b` locally; vLLM or hosted API (prod). Shadow pricing locally (ADR-026) |
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

## 7a. LLM client, metering and budgets (ADR-026)
One LLM client module in the agent; no node calls the model directly.

| Responsibility | Where |
|---|---|
| Price table (USD per 1M input/output tokens per model, shadow prices for local models) | LiteLLM config |
| Spend tracking, global daily USD budget, per-model rate limits, token/latency Prometheus metrics | LiteLLM |
| Per-turn output cap, per-conversation cap, per-customer daily cap (Redis counters) | Agent LLM client |
| Record every call: stage, model, TTFT, duration, tokens in/out, tokens/sec, cost, budget events -> `llm_calls` table + OTel GenAI spans (Langfuse) | Agent LLM client |
| Emit `status.updated` before each stage and `message.metrics` (dev overlay) per ADR-024 | Agent |

Example config (values are examples, set per environment):
```yaml
llm:
  gateway_url: http://litellm:4000
  primary_model: buywise-primary      # LiteLLM alias -> ollama/qwen2.5:7b locally
  fallback_model: buywise-economy     # cheaper model used under budget pressure
  budgets:
    per_turn_output_tokens: 1024
    per_conversation_tokens: 20000
    per_customer_daily_tokens: 100000
    global_daily_usd: TBD             # enforced in LiteLLM; alert 80%, fallback 90%, stop 100%.
                                      # Set when the production LLM is decided (docs/00 #5); rough estimate
                                      # ~$2,000-3,000/day production, local = production / S
```

Admission control and deadlines (docs/00 section 7.3): per-pod cap on concurrent generations with a bounded queue (`status.updated` shows queue position); per-stage deadlines scaled by `k` locally; circuit breaker on the LiteLLM client.

Degradation ladder (never a bare error):
1. Global spend >= 80% -> alert (Grafana).
2. Global spend >= 90% -> new turns use `fallback_model`.
3. Global spend 100%, or per-conversation / per-customer cap hit -> no generation: FAQ answers from RAG retrieval (no LLM) + offer staff handoff.
4. Per-turn cap -> answer is cut at a sentence boundary with "Want me to continue?".

## 8. Testing
- Scenario suite (DeepEval), intent accuracy set - TBD.

## 9. Open decisions
1. Router: LLM classifier vs small fine-tuned classifier.
2. Production LLM choice.
3. User identity propagation BFF -> agent -> `buywise-mcp` -> services (e.g. token exchange RFC 8693 vs passing the user token through). Raised by ADR-021.
4. Agent -> BFF stream format: agent emits ADR-024 contract events directly vs BFF maps an agent-specific stream into the contract.
