# Customer Support Agent - Production Plan

Production-grade support agent that grows layer by layer, fixing one real failure at each stage:
FAQ only -> tool calling -> intent routing -> refund policy -> human handoff -> contract safety.

## Tech stack

| Part | Choice |
|---|---|
| Language | Python 3.12 |
| Agent orchestration | LangGraph |
| LLM | Ollama `qwen2.5:7b` (local, behind a pluggable client) |
| Embeddings / FAQ RAG | Ollama `nomic-embed-text` + Chroma |
| Tools | MCP servers (spec 2026-07-28, Python SDK) |
| Backend services | FastAPI (order, refund policy, helpdesk) |
| Database | PostgreSQL (Docker); SQLite for local tests |
| Data models | Pydantic |
| Observability | OpenTelemetry traces + structured logs |
| Tests | pytest: unit, contract, end-to-end eval |
| UI | Customer chat + human agent console |
| Packaging / run | `uv`, Docker Compose, GitHub Actions CI |

## Architecture

1. Customer message -> **agent API** (FastAPI).
2. **Sentiment check** -> if frustration over threshold, hand off to a human.
3. **Intent router** (classifier) -> tracking / refund / technical / compliance / faq.
4. **Intent handler** (LangGraph node) gets only that intent's tools.
5. Tools are called through **MCP servers**, which wrap the backend services.
6. **Refund policy engine** (refund service) decides; the agent can only request, never approve.
7. **Helpdesk service** stores tickets and lets a human join the same conversation.
8. Every step is traced (OpenTelemetry).

## Stages

| # | Stage | What to build | Done when |
|---|---|---|---|
| 0 | Foundation | Repo layout, `uv` project, Docker Compose (Postgres + services), seed orders, config | `docker compose up` starts everything |
| 1 | FAQ agent | FAQ docs -> chunk -> embed -> Chroma; answer with citations; "I don't know" when not found | FAQ eval set passes; no made-up answers |
| 2 | Tool calling | Order service (FastAPI) + order MCP server (`get_order`, `track_order`, `cancel_order`); agent calls tools | "Where is my order?" returns real status |
| 3 | Intent router | Classifier (LLM with structured output) -> intent + confidence; per-intent tool scoping; low confidence -> ask to clarify | Intent eval accuracy target met; "when will it arrive?" never reaches `cancel_order` |
| 4 | Refund policy engine | Refund service scores 0-1 (order value, user reputation, damage classifier); thresholds in service config: >0.8 approve, 0.4-0.8 ask for photo, <0.4 human | Agent cannot approve; policy unit tests pass; photo request via MCP input-required flow |
| 5 | Sentiment + handoff | Sentiment/frustration score per message (+ repeat-question detection); over threshold -> helpdesk ticket with order, intent, summary; human joins, bot steps aside | Angry "third time" message -> ticket + human takeover with full history |
| 6 | Contract safety | Versioned tool schemas; contract tests in CI between agent and each MCP server; schema snapshot diff; tool-error alerts | Changing the order API without updating the agent fails CI |
| 7 | Guardrails | PII masking in logs, prompt-injection defense on customer text, action confirmation for cancel/refund | Red-team test set passes |
| 8 | Observability | OpenTelemetry trace per conversation: route, tools, policy decision, handoff | One trace shows the whole flow |
| 9 | Evaluation | End-to-end scenario suite (tracking, refund tiers, angry customer, API change); run in CI | Suite green; results tracked per release |
| 10 | Customer memory | Past orders/issues per customer (later: own layered memory library) | Returning customer gets context-aware help |
| 11 | UI | Customer chat + human agent console (ticket queue, take over conversation) | Live handoff works end to end |
| 12 | Deployment | Docker images, cloud VM, secrets, health checks | Runs outside the local machine |

## Key design rules
- Money decisions live in services, never in prompts.
- Each intent handler sees only its own tools.
- Tool schemas are versioned and contract-tested.
- The human can always take over; the bot never argues with a frustrated customer.

## Status
Not started.
