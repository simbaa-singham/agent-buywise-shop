"""The agent's tool policy follows the tools' annotations (ADR-053) - tested with a fake MCP, no LLM, no network."""

import pytest
from mcp import types

from buywise_agent.mcp_tools import ToolInfo, _info
from buywise_agent.tool_policy import ToolRunner, needs_confirmation

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def tool(name, *, read_only, idempotent=True, destructive=False, props=("order_id",)) -> ToolInfo:
    return ToolInfo(name=name, domain="orders", title=name.replace("_", " ").title(), description="d",
                    input_schema={"type": "object", "properties": {p: {"type": "string"} for p in props}},
                    read_only=read_only, destructive=destructive, idempotent=idempotent)


GET = tool("get_order", read_only=True)
QUOTE = tool("quote_order", read_only=True, props=("items", "fulfilment", "store_id"))
PLACE = tool("place_order", read_only=False, idempotent=False, props=("items", "fulfilment", "store_id"))
CANCEL = tool("cancel_order", read_only=False, destructive=True)
TOOLS = {t.name: t for t in (GET, QUOTE, PLACE, CANCEL)}
UNAVAILABLE = (False, "unavailable: down", {"code": "unavailable", "message": "down", "retryable": True})


class FakeMcp:
    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    async def __call__(self, info, args, customer_id):
        self.calls.append(info.name)
        return self.answers.pop(0) if self.answers else (True, "{}", {"ok": True})


def runner(fake) -> ToolRunner:
    return ToolRunner(fake, "cu-demo", delay_s=0)


# --- confirmation comes from the annotations -------------------------------------------------------------------
def test_writes_need_confirmation_reads_do_not():
    assert needs_confirmation(PLACE) and needs_confirmation(CANCEL)
    assert not needs_confirmation(GET) and not needs_confirmation(QUOTE)
    assert needs_confirmation(None)  # unknown tool: never run without asking


def test_a_tool_without_annotations_is_treated_as_a_risky_write():
    bare = _info("x", types.Tool(name="new_tool", input_schema={"type": "object"}))
    assert not bare.read_only and not bare.idempotent and bare.destructive and needs_confirmation(bare)


async def test_a_write_runs_its_preview_not_the_write():
    fake = FakeMcp((True, '{"total": 1295.94}', {"total": 1295.94}))
    args = {"items": [{"sku": "PH-1", "quantity": 1}], "fulfilment": "pickup", "store_id": "st-aus"}
    text, pending = await runner(fake).prepare(PLACE, args, TOOLS)
    assert fake.calls == ["quote_order"]  # place_order itself never ran
    assert pending == {"tool": "place_order", "args": args} and "NOT DONE YET" in text and "1295.94" in text


async def test_cancel_is_previewed_with_the_order():
    fake = FakeMcp()
    _, pending = await runner(fake).prepare(CANCEL, {"order_id": "BW-1"}, TOOLS)
    assert fake.calls == ["get_order"] and pending["tool"] == "cancel_order"


async def test_a_failed_preview_leaves_nothing_to_confirm():
    fake = FakeMcp((False, "not_found: Unknown order BW-9", {"code": "not_found", "retryable": False}))
    text, pending = await runner(fake).prepare(CANCEL, {"order_id": "BW-9"}, TOOLS)
    assert pending is None and "Unknown order" in text


# --- retry -----------------------------------------------------------------------------------------------------
async def test_read_only_is_retried_once_on_a_retryable_error():
    fake = FakeMcp(UNAVAILABLE, (True, "{}", {"order_id": "BW-1"}))
    ok, _, _ = await runner(fake).run(GET, {"order_id": "BW-1"})
    assert ok and fake.calls == ["get_order", "get_order"]


async def test_only_one_retry():
    fake = FakeMcp(UNAVAILABLE, UNAVAILABLE, (True, "{}", {}))
    ok, _, _ = await runner(fake).run(GET, {"order_id": "BW-1"})
    assert not ok and len(fake.calls) == 2


async def test_a_non_idempotent_write_is_never_retried():
    fake = FakeMcp(UNAVAILABLE, (True, "{}", {}))
    ok, _, _ = await runner(fake).run(PLACE, {})
    assert not ok and fake.calls == ["place_order"]  # a retry could place a second order


async def test_an_idempotent_write_may_be_retried():
    fake = FakeMcp(UNAVAILABLE, (True, "{}", {"status": "cancelled"}))
    ok, _, _ = await runner(fake).run(CANCEL, {"order_id": "BW-1"})
    assert ok and fake.calls == ["cancel_order", "cancel_order"]


async def test_errors_that_are_not_retryable_are_not_retried():
    fake = FakeMcp((False, "not_found", {"code": "not_found", "retryable": False}))
    await runner(fake).run(GET, {"order_id": "BW-9"})
    assert fake.calls == ["get_order"]


# --- per-turn cache --------------------------------------------------------------------------------------------
async def test_read_only_results_are_cached_within_a_turn():
    fake = FakeMcp()
    r = runner(fake)
    await r.run(GET, {"order_id": "BW-1"})
    await r.run(GET, {"order_id": "BW-1"})
    await r.run(GET, {"order_id": "BW-2"})
    assert fake.calls == ["get_order", "get_order"]  # second BW-1 from cache, BW-2 is a new call


async def test_writes_and_failures_are_never_cached():
    fake = FakeMcp((False, "x", {"retryable": False}))
    r = runner(fake)
    await r.run(GET, {"order_id": "BW-1"})  # failed -> not cached
    await r.run(GET, {"order_id": "BW-1"})
    await r.run(CANCEL, {"order_id": "BW-1"})
    await r.run(CANCEL, {"order_id": "BW-1"})
    assert fake.calls == ["get_order", "get_order", "cancel_order", "cancel_order"]


async def test_a_new_turn_starts_with_an_empty_cache():
    fake = FakeMcp()
    await runner(fake).run(GET, {"order_id": "BW-1"})
    await runner(fake).run(GET, {"order_id": "BW-1"})
    assert len(fake.calls) == 2


def test_model_specs_come_from_mcp_unchanged():
    spec = QUOTE.model_spec()["function"]
    assert spec["name"] == "quote_order" and spec["parameters"] == QUOTE.input_schema
