"""Typed errors and the circuit breaker (ADR-055) - no services needed: services answers are faked with httpx."""

import json

import httpx
import pytest
from mcp import Client
from mcp.server.mcpserver import MCPServer

from buywise_mcp.core.errors import ErrorCode, ToolFailure, typed_errors
from buywise_mcp.core.identity import Customer
from buywise_mcp.core.services import CircuitBreaker, Services

pytestmark = pytest.mark.anyio


def fake_services(handler, failures: int = 5, clock=lambda: 0.0) -> Services:
    s = Services("http://services.test", 1.0, CircuitBreaker(failures, 10.0, clock))
    s.client = httpx.AsyncClient(base_url="http://services.test", transport=httpx.MockTransport(handler))
    return s


def answer(status: int, body: dict | None = None):
    return lambda request: httpx.Response(status, json=body or {})


async def failure(services: Services) -> ToolFailure:
    with pytest.raises(ToolFailure) as caught:
        await services.call("GET", "/api/x")
    return caught.value


# --- HTTP status -> error code ---------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("status", "code"),
    [
        (400, ErrorCode.INVALID_INPUT),
        (401, ErrorCode.NOT_LOGGED_IN),
        (403, ErrorCode.FORBIDDEN),
        (404, ErrorCode.NOT_FOUND),
        (409, ErrorCode.CONFLICT),
        (422, ErrorCode.INVALID_INPUT),
    ],
)
async def test_business_errors_keep_the_services_message(status, code):
    f = await failure(fake_services(answer(status, {"detail": "Unknown SKU NOPE-1"})))
    assert (f.info.code, f.info.message, f.info.retryable) == (code, "Unknown SKU NOPE-1", False)


@pytest.mark.parametrize("status", [500, 502, 503, 429])
async def test_server_errors_are_unavailable_retryable_and_never_leak_the_detail(status):
    f = await failure(fake_services(answer(status, {"detail": "PSQLException: relation orders.x at 10.0.0.5"})))
    assert f.info.code == ErrorCode.UNAVAILABLE and f.info.retryable
    assert "PSQL" not in f.info.message and "10.0.0.5" not in f.info.message


async def test_timeout_is_unavailable_retryable():
    def timeout(request):
        raise httpx.ReadTimeout("slow", request=request)

    f = await failure(fake_services(timeout))
    assert f.info.code == ErrorCode.UNAVAILABLE and f.info.retryable


# --- circuit breaker -------------------------------------------------------------------------------------------
async def test_breaker_opens_after_repeated_failures_and_then_fails_fast():
    calls, now = [], [0.0]

    def down(request):
        calls.append(request)
        return httpx.Response(503)

    services = fake_services(down, failures=3, clock=lambda: now[0])
    for _ in range(3):
        await failure(services)
    assert services.breaker.state == "open"
    f = await failure(services)  # no call is sent while open
    assert len(calls) == 3 and f.info.code == ErrorCode.UNAVAILABLE and f.info.hint
    assert not f.info.retryable  # retrying at once is pointless while the circuit is open

    now[0] = 10.0  # cool-down over: half-open lets one trial call through
    assert services.breaker.state == "half_open"
    await failure(services)  # trial fails -> open again
    assert len(calls) == 4 and services.breaker.state == "open"


async def test_breaker_closes_after_a_successful_trial():
    now, healthy = [0.0], [False]
    services = fake_services(lambda r: httpx.Response(200 if healthy[0] else 503, json={}), 2, lambda: now[0])
    for _ in range(2):
        await failure(services)
    now[0], healthy[0] = 10.0, True
    assert await services.call("GET", "/api/x") == {}
    assert services.breaker.state == "closed" and services.breaker.failures == 0


async def test_business_errors_do_not_open_the_breaker():
    services = fake_services(answer(404, {"detail": "Unknown order"}), failures=2)
    for _ in range(5):
        await failure(services)
    assert services.breaker.state == "closed"


# --- the tool decorator ----------------------------------------------------------------------------------------
server = MCPServer("test")


@server.tool()
@typed_errors({ErrorCode.CONFLICT: "Offer another store."})
async def conflicting() -> dict:
    """x"""
    raise ToolFailure(ErrorCode.CONFLICT, "Not enough stock")


@server.tool()
@typed_errors()
async def crashing() -> dict:
    """x"""
    raise RuntimeError("SELECT * FROM orders.orders failed at /srv/app.py line 42")


@server.tool()
@typed_errors()
async def needs_customer(customer: Customer) -> dict:
    """x"""
    return {"customer": customer}


async def call(name: str):
    async with Client(server) as client:
        return await client.call_tool(name, {})


async def test_tool_failure_becomes_a_typed_error_with_the_tool_hint():
    r = await call("conflicting")
    assert r.is_error
    assert r.structured_content == {
        "code": "conflict",
        "message": "Not enough stock",
        "retryable": False,
        "hint": "Offer another store.",
    }
    assert r.content[0].text == "conflict: Not enough stock Hint: Offer another store."


async def test_unexpected_exception_is_generic_and_hides_internals():
    r = await call("crashing")
    assert r.is_error and r.structured_content["code"] == "unavailable"
    assert "SELECT" not in json.dumps(r.structured_content) and "app.py" not in r.content[0].text


async def test_missing_customer_is_a_typed_not_logged_in_error():
    r = await call("needs_customer")
    assert r.is_error and r.structured_content["code"] == "not_logged_in" and r.structured_content["hint"]
