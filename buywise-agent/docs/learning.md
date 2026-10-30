# buywise-agent - Learning Notes

What the buywise-agent module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### Using the chat contract from Python
- The agent does not define chat messages itself: it uses models **generated** from the ui module's JSON Schema (see [buywise-web/docs/learning.md](../../buywise-web/docs/learning.md)) into `buywise_agent/contracts/chat_contract.py`.
- **Pydantic** models validate data: building a `MessageDelta` without `payload.text`, or with an unknown field, raises a `ValidationError`.
- **Contract tests** (`tests/contract/test_chat_contract.py`, 6 tests): the schema itself is valid; example messages pass both the JSON Schema and the Pydantic models; an invalid example is rejected by both; `SendMessageRequest` requires `clientMessageId`.
- Dev tools live in `.venv` (`make agent-dev`): pytest, ruff (lint), jsonschema, datamodel-code-generator.

- **Step 5.3 decision (ADR-044): strict when writing, tolerant when reading.** The agent is a writer: every event it builds goes through the generated Pydantic models (`extra='forbid'`), so a typo like `txt` fails before the event is sent. Readers (BFF forwarding, browser) ignore unknown fields and types, so a new optional field never breaks an old browser tab. Test: `examples/invalid-unknown-field.json` must be rejected (7 tests now).
- **Discriminator (step 5.2 fix):** `ChatEvent` picks the class from `type`; a bad event gives 1 precise error instead of 25.

### Switching from pip to uv (ADR-042)
- **The problem with pip here:** `pyproject.toml` listed libraries with no versions and there was no lock file, so every `pip install` took the newest versions that day. Laptop, CI and a later reinstall could each get different versions (including the ~90 indirect libraries LangGraph pulls in): "works on my machine". The Python version was whatever `python3` was on PATH.
- **The fix:** uv reads the same `pyproject.toml` and writes **`uv.lock`**: every library (direct and indirect) at an exact version with a checksum, committed to Git. `.python-version` pins 3.12; uv downloads that Python if missing. `uv sync --locked` installs exactly the lock; `--locked` fails if `pyproject.toml` changed without re-locking, so CI catches it.
- **Upgrading on purpose:** `make -C buywise-agent lock ARGS=--upgrade`, then review the `uv.lock` diff like code.
- Full environment build went from minutes (pip) to ~1.5 s (uv, warm cache).

**Q: Do I still have a `.venv`?** Yes. uv creates `buywise-agent/.venv` as before, so PyCharm uses the same interpreter path. `uv run <cmd>` runs a command inside it without activating anything.

### Commands
| Task | Command |
|---|---|
| Create dev environment (from uv.lock) | `make agent-dev` |
| Re-lock after editing dependencies | `make -C buywise-agent lock` |
| Upgrade all libraries deliberately | `make -C buywise-agent lock ARGS=--upgrade` |
| Run any tool in the environment | `cd buywise-agent && uv run <tool>` |
| Tests + lint | `make test` |

## Local end-to-end build (2026-10-30)
- **Turn:** `POST /turns` answers 202 at once; the turn runs in the background and writes contract events to `conv:{id}` (Redis Stream), validated by the generated Pydantic models first.
- **LangGraph loop:** `llm` node streams text (each piece = `message.delta`) and may ask for tools -> `tools` node runs them (MCP or knowledge search), emits `status.updated` and `block.product_card` -> back to `llm` until it answers (max 5 rounds).
- **Ordering safety:** `place_order` from the model only produces a quote (stored as pending for 15 min); the order is placed by code when the customer replies "yes".
- **RAG:** `make -C buywise-agent ingest` parses md/txt/html/pdf/docx into sections -> ~1,000-char chunks -> bge-m3 vectors via LiteLLM -> `rag.chunks` (pgvector, HNSW cosine). Search returns the 4 nearest chunks under a distance cut-off; they become the answer's citations.
- **Try:** `make -C buywise-agent turn Q="How long will the store hold my pickup order?"`; tool calls are logged in `logs/agent.log`.
