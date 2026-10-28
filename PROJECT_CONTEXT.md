# Project Context - read at the start of every work session

## Working agreement
- Sachin is the architect; we design step by step at production scale.
- Each topic: options -> trade-offs -> architect's decision -> update module doc + ADR log.
- Design before implementation. Explain each technology/technique when it is introduced.

## What we are building
agent-buywise-shop: AI shopping assistant for an online store selling electronic devices (Apple products as the sample catalog, US):
place orders, check order status, answer product/store questions, hand off to staff.
Delivery + in-store pickup. Website chat first. Returns/exchanges out of scope.

## Stack (decided)
- UI: Angular 22 | BFF: Node.js 24 LTS, NestJS 11 + Fastify
- Services: Java 25, Spring Boot 4.1, Spring AI 2.0 MCP, Spring Cloud Gateway (internal)
- Agent: Python 3.12, LangGraph 1.2, MCP Python SDK v2
- Data/events: PostgreSQL, Redis, Kafka (outbox)
- Repo: one monorepo - ui/, services/, data/, agent/, deploy/, docs/

## Where things are
- Main design: docs/00_Architecture_Overview.md
- Module designs: docs/01..08_*.md
- Decisions: docs/adr/ADR_Log.md
- Old material: docs/archive/

## Current status
- Design phase. Doc set created 2026-10-28.
- Next step: confirm NFR assumptions (docs/00 section 6), then open decisions in docs/00 section 8.

## Pending housekeeping
- Restructure module folders to match docs/00 section "Repository" layout (move pyproject.toml etc. into agent/).
- Git init + first commit/push.
