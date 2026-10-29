# Project Context - read at the start of every work session

## Working agreement
- Sachin is the architect; we design step by step at production scale.
- Each topic: options -> trade-offs -> architect's decision -> update module doc + ADR log.
- Design before implementation. Explain each technology/technique when it is introduced.
- Whenever a decision changes the design, list what in the project no longer matches and ask before changing it.
- Documents and scripts live in the module they belong to (<module>/docs, <module>/Makefile, module scripts); only cross-module documents stay in docs/.
- After every phase (and as its steps finish), update <module>/docs/learning.md for each module touched (concepts, what was built and why, questions asked with answers, commands, problems and fixes) and the phase index docs/learning/Phase-<N>.md. It is part of the phase's definition of done.
- After every change, explain each changed file in plain words: what it is, what it does, why it is needed, and how to see it working. ADR numbers are references only, never the explanation.
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
- Editors: one Git repo, one IDE per module folder - WebStorm `buywise-web/`, PyCharm `buywise-agent/` + attached `buywise-mcp/`, IntelliJ `buywise-services/` (+ `buywise-events/`), any editor for root/deploy/data/docs.
- Module layout: each module has README.md, Makefile, docs/design.md, docs/learning.md (agent also docs/rag.md). Root Makefile delegates to module Makefiles.
- Implementation roadmap: docs/09_Implementation_Roadmap.md
- Learning: per module in <module>/docs/learning.md (one section per phase); phase index in docs/learning/Phase-<N>.md
- Decisions: docs/adr/ADR_Log.md
- Old material: docs/archive/

## Current status
- Design phase. Docs updated 2026-10-28 for: modular monolith, 6 deployables, buywise-mcp, no internal gateway, rename.
- Done 2026-10-28: UI module design decisions ADR-018 to ADR-025 (app structure, component library, real-time channel, session, state, rendering, chat contract, accessibility). Browser support set (buywise-web/docs/design.md section 6).
- Done 2026-10-28: NFR targets set as ideal production targets, local scaled by S=40 and LLM hardware factor k, with failure behavior (docs/00 section 7); LLM metering/budgets (ADR-026) and LLM observability UI (ADR-027).
- Done 2026-10-28: identity propagation via token exchange (ADR-028); agent output path via conversation Redis Streams (ADR-029); intent routing cascade (ADR-030); MCP server layout (ADR-031) and tool rate limits (ADR-032); data sources (ADR-033) and chunking (ADR-034); backup policy, design only (ADR-035); PII policy (ADR-036); UI key flows (buywise-web/docs/design.md section 5); conversation ownership (ADR-037); AI Operations charts (ADR-038); multi-format parsing (ADR-039); embedding model bge-m3 everywhere (ADR-040); policy outline approved (data/knowledge/_outline/policy_outline.md). Local vs design-only scope: docs/00 section 7.4.
- Open items raised for later modules: AI Operations chart library (buywise-web/docs/design.md).
- Done 2026-10-28: vector store (ADR-011), Postgres organisation (ADR-010). Kept open by architect: production LLM (docs/00 #5), event schema format (docs/00 #6), event partitions/retention/DLQ (buywise-events/docs/design.md), secrets management (deploy/docs/design.md).
- Done 2026-10-28: data created (`make data`): catalog (50 products, 240 variants, verified 2026-10-28), seed (stores, stock, 500 customers, 2,000 orders, tickets), 103 knowledge docs in 11 formats, eval sets. Gaps: router eval 35/~95, FAQs 171/~200, parser golden snapshots in phase 3.
- Done 2026-10-29: implementation roadmap approved (docs/09) as drafted.
- Done 2026-10-29: phase 0 foundations (docs/09). Local k = 2.96 (deploy/local/scale.yaml).
- In progress: step-by-step walkthrough of phase 0 for the architect. Done: steps 1-4 (supporting programs in Docker with health checks; separate databases; tables via Flyway; architect loaded seed data by hand in pgAdmin with data/docs/walkthroughs/load-seed-data.sql - counts verified). Resume at step 5.1 (chat message contract: walk through the schema definition with the architect - started, not finished), then 5.2 generated code, 5.3 contract tests, then step 6 (k benchmark), step 7 (Makefile, CI, README).
- Then: phase 1 thin slice (docs/09).

## Pending housekeeping
- Done 2026-10-28: folders restructured to docs/00 section 6; buywise-agent/pyproject.toml aligned with ADR-011 (pgvector) and ADR-026 (LiteLLM via langchain-openai); buywise-agent/.env.example aligned with ADR-010/026/029.
- Done 2026-10-28: git init + first commit, pushed to github.com:simbaa-singham/agent-buywise-shop (main).
