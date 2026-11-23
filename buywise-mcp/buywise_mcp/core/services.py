"""HTTP client for buywise-services (ADR-055): timeout, HTTP status -> typed error, circuit breaker.

MCP never retries: a retried write could place an order twice. It tells the agent `retryable` and the agent decides.
"""

import time
from collections.abc import Callable

import httpx

from ..config import settings
from .errors import ErrorCode, ToolFailure

UNAVAILABLE = "The store system is not responding right now."

# Business errors carry a safe, plain message from services; server errors never do (it may hold internals).
_CODES = {
    400: ErrorCode.INVALID_INPUT,
    401: ErrorCode.NOT_LOGGED_IN,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.INVALID_INPUT,
}


class CircuitBreaker:
    """closed -> (N consecutive failures) -> open: fail fast, no calls -> (after open_s) half-open: one trial call
    -> success closes it, failure opens it again. Protects services from a stampede while it is down."""

    def __init__(self, failures: int, open_s: float, clock: Callable[[], float] = time.monotonic):
        self.threshold, self.open_s, self.clock = failures, open_s, clock
        self.failures, self.opened_at = 0, None

    @property
    def state(self) -> str:
        if self.opened_at is None:
            return "closed"
        return "half_open" if self.clock() - self.opened_at >= self.open_s else "open"

    def allow(self) -> bool:
        return self.state != "open"

    def success(self) -> None:
        self.failures, self.opened_at = 0, None

    def failure(self) -> None:
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.threshold:
            self.opened_at = self.clock()


class Services:
    def __init__(self, base_url: str, timeout_s: float, breaker: CircuitBreaker):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout_s)
        self.breaker = breaker

    async def call(self, method: str, path: str, *, customer_id: str | None = None, **kwargs):
        if not self.breaker.allow():
            raise ToolFailure(  # open circuit: an immediate retry would fail the same way
                ErrorCode.UNAVAILABLE,
                UNAVAILABLE,
                retryable=False,
                hint="Tell the customer to try again in a minute; do not call this tool again now.",
            )
        headers = {"X-Customer-Id": customer_id} if customer_id else {}
        try:
            resp = await self.client.request(method, path, headers=headers, **kwargs)
        except httpx.HTTPError:  # timeout, connection refused, ...
            self.breaker.failure()
            raise ToolFailure(ErrorCode.UNAVAILABLE, UNAVAILABLE, retryable=True) from None
        if resp.status_code >= 500 or resp.status_code == 429:
            self.breaker.failure()
            raise ToolFailure(ErrorCode.UNAVAILABLE, UNAVAILABLE, retryable=True)
        self.breaker.success()
        if resp.status_code >= 400:
            raise ToolFailure(_CODES.get(resp.status_code, ErrorCode.INVALID_INPUT), _detail(resp))
        return resp.json()


def _detail(resp: httpx.Response) -> str:
    try:
        return resp.json().get("detail") or "The request was not accepted."
    except ValueError:
        return "The request was not accepted."


services = Services(
    settings.services_url,
    settings.services_timeout_s,
    CircuitBreaker(settings.breaker_failures, settings.breaker_open_s),
)
