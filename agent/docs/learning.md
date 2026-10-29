# agent - Learning Notes

What the agent module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### Using the chat contract from Python
- The agent does not define chat messages itself: it uses models **generated** from the ui module's JSON Schema (see [ui/docs/learning.md](../../ui/docs/learning.md)) into `buywise_agent/contracts/chat_contract.py`.
- **Pydantic** models validate data: building a `MessageDelta` without `payload.text`, or with an unknown field, raises a `ValidationError`.
- **Contract tests** (`tests/contract/test_chat_contract.py`, 6 tests): the schema itself is valid; example messages pass both the JSON Schema and the Pydantic models; an invalid example is rejected by both; `SendMessageRequest` requires `clientMessageId`.
- Dev tools live in `.venv` (`make agent-dev`): pytest, ruff (lint), jsonschema, datamodel-code-generator.

_To be completed with step 5.2 / 5.3._

### Commands
| Task | Command |
|---|---|
| Create dev environment | `make agent-dev` |
| Tests + lint | `make test` |
