# buywise-web - Learning Notes

What the buywise-web module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### The chat message contract (step 5, in progress)
- **Problem:** the agent (Python) and the website (TypeScript) must agree exactly on every chat message; a mismatch (`text` vs `content`) silently breaks the chat.
- **Solution:** one definition in **JSON Schema** - `web/projects/shared/contracts/schemas/chat-events.schema.json` - and code **generated** from it for both sides: `web/projects/shared/contracts/generated/chat-events.ts` (TypeScript) and `buywise-agent/buywise_agent/contracts/chat_contract.py` (Python/Pydantic). Generated files are never edited by hand (`make contracts`).
- **CI drift check:** `make contracts-check` fails if the schema changed but the generated code was not regenerated.

**Message shape** - every message has:
| Field | Meaning |
|---|---|
| `v` | Contract version (1); bumped only for breaking changes |
| `type` | Kind of message, e.g. `message.delta` |
| `ts` | Timestamp |
| `conversationId` | Which chat |
| `messageId` | Which reply (all pieces of one answer share it) |
| `payload` | Content, different per type |

**13 message types:** `status.updated`, `message.started`, `message.delta`, `message.completed`, `message.failed`, `message.created`, `message.metrics`, `block.product_card`, `handoff.requested` / `accepted` / `ended`, `ticket.created` / `updated`, `order.status_changed`. Plus `SendMessageRequest` from the browser with `clientMessageId` (duplicates ignored = idempotent send).

**JSON Schema keywords:** `type`, `const` (exact value), `enum` (one of a list), `required`, `additionalProperties: false` (rejects unknown fields and typos), `$ref` (reuse a definition), `oneOf` (one of several shapes).

**A full answer as messages:** `status.updated` "Thinking..." -> `status.updated` "Checking stock..." -> `message.started` -> several `message.delta` -> `block.product_card` -> `message.completed`.

**Tightening found during the walkthrough (step 5.1, 2026-10-30):**
- `block.product_card.stockAtStore`: `storeId`, `storeName`, `quantity` now required - an empty `{}` was valid before.
- `block.product_card.availability`: was free text, now `available | preorder | discontinued` (sale status from the catalog, ADR-043) + optional `shipsOn` date. Stock is only `stockAtStore.quantity`.
- One schema edit -> `make contracts` -> both generated files change (Python `str | None` became `Literal[...]`; TypeScript `storeId?: string` became `storeId: string`) -> contract tests re-run.

**Q: What are NFR and ADR?** NFR = non-functional requirement: *how well* the system works (speed, availability, cost, security), docs/00 section 7.2. ADR = Architecture Decision Record: one decision with context, options, decision, consequences (docs/adr/ADR_Log.md).

_To be completed: generated code walk-through (5.2) and contract tests (5.3)._

### Problems hit and fixes
| Problem | Cause | Fix |
|---|---|---|
| Generated TypeScript lost event fields (`StatusUpdated = Envelope`) | Schema used `allOf` composition | Flattened the common fields into each event |
| Python classes named `Payload1..12` | Generator ignored nested titles | Added payload titles + `--use-title-as-name` |
| A bad event gave 25 Pydantic errors (one per shape tried) | `oneOf` without a discriminator: Pydantic tries all 13 shapes | Added `discriminator: {propertyName: type}` to `ChatEvent`; Pydantic picks the shape from `type` -> 1 precise error |
| With the discriminator, `ticket.created`/`ticket.updated` were rejected by Pydantic (caught by the new examples) | Generator turned the two-value `type` enum of `TicketChanged` into `Literal["TicketChanged"]` | Split into `TicketCreated` + `TicketUpdated`, each with one `const` type, sharing `TicketPayload`; wire format unchanged |
| Generator warning "Black/isort will become optional" on every run | The warning fires whenever black/isort are the formatters, even with extras declared | Formatters switched to ruff (`--formatters ruff-format ruff-check`, `datamodel-code-generator[ruff]`) - the lint tool the project already uses |

### Commands
| Task | Command |
|---|---|
| Regenerate contract code | `make contracts` |
| Check generated code is up to date | `make contracts-check` |

## Local end-to-end build (2026-10-30)
- **BFF (NestJS 12 + Fastify):** guest session on first request (cookie `bw_sid` -> `sess:{id}` in Redis); `POST /api/chat/messages` is idempotent by `clientMessageId`; `GET /api/chat/stream` is SSE reading the Redis Stream (`XREAD BLOCK`), each event's SSE `id` = stream entry id so a reconnect resumes with `Last-Event-ID`.
- **Login:** BFF does the Keycloak code flow with PKCE; tokens stay in Redis, the browser only has the cookie; the conversation is kept across login.
- **Angular:** `ChatStore` (NgRx SignalStore) is fed only by the SSE stream - reloading the page replays the conversation; components: chat, product card; Markdown rendered through Angular's sanitizer.
- **Try:** `make start`, open http://localhost:3000.
