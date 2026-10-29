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
- Agent API (ADR-029): `POST /turns` -> 202 Accepted with `turnId`; turn runs in the background and appends ADR-024 contract events (Pydantic types generated from the JSON Schema) to the conversation's Redis Stream `conv:{id}`. `POST /turns/{id}/cancel` stops a running turn. A turn is never tied to the BFF pod that started it.
- `POST /conversations/{id}/pause` and `/resume` (called by the BFF on staff accept/release, ADR-037); the agent refuses new turns while paused as a second safety check.

## 4. Graph design
- **State:** conversation_id, customer_id (from the token `sub`, read-only, never from the LLM), messages, intent, confidence, sentiment, tool_results, paused (read-only mirror of conversation ownership; helpdesk module owns it, ADR-037).
- **Nodes:** load_context -> sentiment_check -> route_intent -> handler -> guardrails -> respond.
- **Routing (ADR-030) - cascade in `route_intent`:**
  1. Rules: deterministic patterns (order number `BW-\d+` -> `order_status`; "talk to a person" -> `handoff`).
  2. Fast classifier: small in-process model (SetFit or fine-tuned ModernBERT, CPU/ONNX, ~10-30 ms); used when confidence >= threshold.
  3. LLM classifier: economy tier (`buywise-economy`), structured JSON output (`intents[]`, `confidence`, `entities`), recent history included; handles follow-ups and multi-intent messages.
  4. Still low confidence -> clarifying question; low confidence after clarifying, or negative sentiment -> offer staff handoff.
  - Flow stickiness: active multi-step flows (checkout, OTP verification) keep control until done unless the customer clearly changes topic; the router is not re-run on every message.
  - Multi-intent: handlers run in order of the `intents[]` list within one turn.
  - Every decision recorded (tier, intent(s), confidence, latency) in `router_decisions`; shown in AI Operations (ADR-027).
  - Phase 1: rules + LLM classifier; build the labelled eval set (synthetic, human-reviewed). Phase 2: train the fast classifier on the eval set + logged LLM decisions, enable tier 2; thresholds tuned on the eval set.
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
- Identity (ADR-028): agent accepts only tokens with `aud: buywise-agent`; exchanges them for `aud: buywise-mcp` with scopes for the current intent; exchanged tokens held in memory only, never written to LangGraph checkpoints, logs or traces.
- PII in prompts (ADR-036): Presidio replaces PII with reversible placeholders before every LLM call; real values restored in tool calls and replies; mapping kept in memory for the turn only. Adds ~10-30 ms per turn.
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

Tool-call limits (ADR-032): max 8 tool calls per turn, max 3 identical consecutive calls; on a rate-limit error the agent explains `retryAfter` to the customer and does not retry in a loop.

Admission control and deadlines (docs/00 section 7.3): per-pod cap on concurrent generations with a bounded queue (`status.updated` shows queue position); per-stage deadlines scaled by `k` locally; circuit breaker on the LiteLLM client.

Degradation ladder (never a bare error):
1. Global spend >= 80% -> alert (Grafana).
2. Global spend >= 90% -> new turns use `fallback_model`.
3. Global spend 100%, or per-conversation / per-customer cap hit -> no generation: FAQ answers from RAG retrieval (no LLM) + offer staff handoff.
4. Per-turn cap -> answer is cut at a sentence boundary with "Want me to continue?".

## 8. Testing
- Scenario suite (DeepEval), intent accuracy set - TBD.
- Router eval set (ADR-030): labelled messages incl. follow-ups and multi-intent; accuracy >= 95% overall (NFR 8), reported per tier; also used to train the fast classifier and tune thresholds.

## 9. Open decisions
1. ~~Router~~ - decided: rules -> fast classifier -> LLM classifier cascade (ADR-030).
2. Production LLM choice.
3. ~~User identity propagation~~ - decided: token exchange per hop (ADR-028).
4. ~~Agent -> BFF stream format~~ - decided: agent writes ADR-024 events to the conversation Redis Stream (ADR-029).
