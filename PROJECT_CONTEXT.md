# Project Context - read at the start of every work session

## Working agreement
- Sachin is the architect; we design step by step at production scale.
- Each topic: options -> trade-offs -> architect's decision -> update module doc + ADR log.
- Design before implementation. Explain each technology/technique when it is introduced.
- Whenever a decision changes the design, list what in the project no longer matches and ask before changing it.
- During implementation, before writing code in an area, remind Sachin of the decisions (ADR numbers + what they mean in code) that apply to it; flag any new decision that comes up instead of making it silently.

## What we are building
agent-buywise-shop: an AI shopping assistant that helps customers choose, order and track electronic devices.
Online electronics store (Apple products as the sample catalog, US). Delivery + in-store pickup.
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
- Done 2026-10-28: UI module design decisions ADR-018 to ADR-025 (app structure, component library, real-time channel, session, state, rendering, chat contract, accessibility). Remaining UI TBDs: key flows (docs/01 section 5), browser support.
- Open items raised for later modules: identity propagation (docs/03, docs/05); agent -> BFF stream format (docs/03).
- Next: confirm NFR targets (docs/00 section 7), then remaining open decisions (docs/00 section 9).

## Pending housekeeping
- Restructure folders to match docs/00 section 6 (ui/, services/, mcp/, agent/, events/, data/, deploy/); move pyproject.toml etc. into agent/; retire mcp_servers/ and root tests/.
- Done 2026-10-28: git init + first commit, pushed to github.com:simbaa-singham/agent-buywise-shop (main).
