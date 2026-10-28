# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [docs/00_Architecture_Overview.md](docs/00_Architecture_Overview.md)

| Folder | Purpose |
|---|---|
| `agent/` | LangGraph agent: router, handlers, state |
| `services/` | Backend services the agent depends on (order, refund policy, helpdesk) |
| `mcp_servers/` | MCP servers exposing those services as tools |
| `data/` | FAQ docs, seed orders, eval sets |
| `tests/` | Unit, contract and end-to-end eval tests |
| `ui/` | Customer chat + human agent console |
| `deploy/` | Docker Compose, CI |
