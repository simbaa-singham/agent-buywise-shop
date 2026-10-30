# Local end-to-end build (2026-10-30) - Learning Index

The whole core assistant was built in one pass to run on the Mac (`make start` -> http://localhost:3000).
Simplifications against the decided design: [docs/09 section 4](../09_Implementation_Roadmap.md).

## How one chat message travels
```
browser --POST /api/chat/messages--> BFF (session in Redis) --POST /turns (202)--> agent
agent: LangGraph loop  llm -> tools -> llm ... ; tools = MCP servers (-> services REST) + pgvector knowledge search
agent --XADD conv:{id}--> Redis Stream <--XREAD-- BFF --SSE /api/chat/stream--> browser (SignalStore -> UI)
```

| Module | What was built | Notes |
|---|---|---|
| buywise-services | Catalog, inventory, customers, orders REST; quote + place + cancel; Flyway V4 | [learning](../../buywise-services/docs/learning.md) |
| buywise-mcp | 3 MCP servers in one process (`/mcp/catalog`, `/mcp/inventory`, `/mcp/orders`) | [learning](../../buywise-mcp/docs/learning.md) |
| buywise-agent | Tool loop, streaming events, RAG ingest/search, quote-then-yes ordering | [learning](../../buywise-agent/docs/learning.md) |
| buywise-web | BFF (session, SSE, Keycloak login) + Angular chat page | [learning](../../buywise-web/docs/learning.md) |

## Problems hit and fixes
| Problem | Fix |
|---|---|
| start.spring.io returned 500 for Gradle projects | Wrote the Gradle build by hand; wrapper from the Gradle distribution |
| MCP SDK v2 renamed `FastMCP` to `MCPServer`, client uses `httpx2` | Used the v2 API (`mcp.server.mcpserver`, `Client(streamable_http_client(...))`) |
| Model copied the example order id `BW-100000` from a tool description | Removed real-looking examples; "never guess an id"; `list_my_orders` for "my latest order" |
| Model read `pickupHoldUntil` as "pick up after" | Renamed to `heldAtStoreUntil` in tool results |
| Model lower-cased SKUs / asked "shall I place it?" itself | MCP upper-cases SKUs; a bare "yes" nudges the model to call `place_order`, which only quotes |
| Policy said pickup hold is 7 days, code had 5 | Code follows the policy (7 days) |
| Shipping policy v2 is not in effect until 2026-11-15 | Ingest skips not-yet-effective and replaced documents |
| Nest + Fastify: SPA fallback and redirects | Catch-all `GET /*` route for index.html; explicit 302 on redirects |
