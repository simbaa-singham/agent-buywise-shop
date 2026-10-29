# ui - Learning Notes

What the ui module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### The chat message contract (step 5, in progress)
- **Problem:** the agent (Python) and the website (TypeScript) must agree exactly on every chat message; a mismatch (`text` vs `content`) silently breaks the chat.
- **Solution:** one definition in **JSON Schema** - `web/projects/shared/contracts/schemas/chat-events.schema.json` - and code **generated** from it for both sides: `web/projects/shared/contracts/generated/chat-events.ts` (TypeScript) and `agent/buywise_agent/contracts/chat_contract.py` (Python/Pydantic). Generated files are never edited by hand (`make contracts`).
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

_To be completed: generated code walk-through (5.2) and contract tests (5.3)._

### Problems hit and fixes
| Problem | Cause | Fix |
|---|---|---|
| Generated TypeScript lost event fields (`StatusUpdated = Envelope`) | Schema used `allOf` composition | Flattened the common fields into each event |
| Python classes named `Payload1..12` | Generator ignored nested titles | Added payload titles + `--use-title-as-name` |

### Commands
| Task | Command |
|---|---|
| Regenerate contract code | `make contracts` |
| Check generated code is up to date | `make contracts-check` |
