# Project Context - read at the start of every work session

## Working agreement
- Sachin is the architect; we design step by step at production scale.
- Each topic: options -> trade-offs -> architect's decision -> update module doc + ADR log.
- Design before implementation. Explain each technology/technique when it is introduced.
- Whenever a decision changes the design, list what in the project no longer matches and ask before changing it.
- During implementation, before writing code in an area, remind Sachin of the decisions (ADR numbers + what they mean in code) that apply to it; flag any new decision that comes up instead of making it silently.

## What we are building
agent-buywise-shop: an AI shopping assistant that helps customers choose, order and track electronic devices.
Online electronics store with a catalog of real products (real model names, specs and list prices; maker not named), starting with one maker's lineup, other makers later (US). Delivery + in-store pickup.
Website chat first. Returns/exchanges out of scope.
Learning and portfolio project: production-grade design and code, run locally at small scale (not hosted).

## Deployables (decided)
1. buywise-web - Angular 22 + NestJS 11 (Fastify) BFF, Node.js 24 LTS
2. buywise-services - Java 25, Spring Boot 4.1 modular monolith (Spring Modulith)
3. buywise-agent - Python 3.12, LangGraph 1.2, RAG
4. buywise-mcp - Python, MCP Python SDK v2, spec 2026-07-28
5. buywise-event-publisher - Kafka producers (design deferred)
6. buywise-event-consumers - Kafka consumers (design deferred)
Edge: Envoy Gateway. No internal gateway. Data: PostgreSQL, Redis, Kafka, Keycloak.

## Where things are
- Main design: docs/00_Architecture_Overview.md
- Module designs: docs/01..08_*.md
- Decisions: docs/adr/ADR_Log.md
- Old material: docs/archive/

## Current status
- Design phase. Docs updated 2026-10-28 for: modular monolith, 6 deployables, buywise-mcp, no internal gateway, rename.
- Done 2026-10-28: UI module design decisions ADR-018 to ADR-025 (app structure, component library, real-time channel, session, state, rendering, chat contract, accessibility). Browser support set (docs/01 section 6).
- Done 2026-10-28: NFR targets set as ideal production targets, local scaled by S=40 and LLM hardware factor k, with failure behavior (docs/00 section 7); LLM metering/budgets (ADR-026) and LLM observability UI (ADR-027).
- Done 2026-10-28: identity propagation via token exchange (ADR-028); agent output path via conversation Redis Streams (ADR-029); intent routing cascade (ADR-030); MCP server layout (ADR-031) and tool rate limits (ADR-032); data sources (ADR-033) and chunking (ADR-034); backup policy, design only (ADR-035); PII policy (ADR-036); UI key flows (docs/01 section 5); conversation ownership (ADR-037); AI Operations charts (ADR-038). Local vs design-only scope: docs/00 section 7.4.
- Open items raised for later modules: AI Operations chart library (docs/01).
- Done 2026-10-28: vector store (ADR-011), Postgres organisation (ADR-010). Kept open by architect: production LLM (docs/00 #5), event schema format (docs/00 #6), event partitions/retention/DLQ (docs/06), secrets management (docs/08).
- Next: module-level open decisions (docs/01-08 "Open decisions" sections); pending housekeeping below.

## Pending housekeeping
- Done 2026-10-28: folders restructured to docs/00 section 6; agent/pyproject.toml aligned with ADR-011 (pgvector) and ADR-026 (LiteLLM via langchain-openai); agent/.env.example aligned with ADR-010/026/029.
- Done 2026-10-28: git init + first commit, pushed to github.com:simbaa-singham/agent-buywise-shop (main).
