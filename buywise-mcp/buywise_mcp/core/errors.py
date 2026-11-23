"""Typed tool errors (ADR-055).

A tool error is a normal tool result with is_error=true and structured content {code, message, retryable, hint}:
the model reads `message` (plain words it can repeat), `hint` (what to do next) and `retryable` (try again or not).
Protocol (JSON-RPC) errors are left to the SDK: unknown tool, invalid arguments.
Nothing internal - stack traces, SQL, URLs - ever goes into an error; it is logged here instead.
"""

import functools
import logging
from collections.abc import Awaitable, Callable
from enum import StrEnum

from mcp import types
from pydantic import BaseModel

log = logging.getLogger("buywise_mcp")


class ErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INVALID_INPUT = "invalid_input"
    NOT_LOGGED_IN = "not_logged_in"
    FORBIDDEN = "forbidden"
    UNAVAILABLE = "unavailable"


class ToolErrorInfo(BaseModel):
    code: ErrorCode
    message: str
    retryable: bool = False
    hint: str | None = None


class ToolFailure(Exception):
    """Raised anywhere inside a tool; turned into a typed error result by @typed_errors."""

    def __init__(self, code: ErrorCode, message: str, *, retryable: bool = False, hint: str | None = None):
        super().__init__(message)
        self.info = ToolErrorInfo(code=code, message=message, retryable=retryable, hint=hint)


Hints = dict[ErrorCode, str]


class Unresolved:
    """Returned by a Resolve(...) function that cannot fill its parameter (e.g. not logged in). The SDK runs
    resolvers before the tool and would turn a raised error into plain text, so resolvers return this instead and
    @typed_errors answers with the typed error without running the tool body."""

    def __init__(self, code: ErrorCode, message: str, *, hint: str | None = None):
        self.info = ToolErrorInfo(code=code, message=message, retryable=False, hint=hint)


def error_result(info: ToolErrorInfo) -> types.CallToolResult:
    text = f"{info.code}: {info.message}" + (f" Hint: {info.hint}" if info.hint else "")
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content=info.model_dump(mode="json", exclude_none=True),
        is_error=True,
    )


def typed_errors(hints: Hints | None = None):
    """Decorator for every tool: ToolFailure -> typed error result; any other exception -> logged, generic
    `unavailable` (no internals). `hints` adds tool-specific advice for the model per error code."""
    hints = hints or {}

    def wrap(fn: Callable[..., Awaitable]):
        @functools.wraps(fn)  # keeps the signature and return type: the SDK builds the schemas from them
        async def tool(*args, **kwargs):
            unresolved = next((v for v in kwargs.values() if isinstance(v, Unresolved)), None)
            if unresolved:
                return error_result(unresolved.info)
            try:
                return await fn(*args, **kwargs)
            except ToolFailure as failure:
                info = failure.info
                if info.hint is None and info.code in hints:
                    info = info.model_copy(update={"hint": hints[info.code]})
                return error_result(info)
            except Exception:
                log.exception("tool %s failed", fn.__name__)
                return error_result(
                    ToolErrorInfo(
                        code=ErrorCode.UNAVAILABLE, message="Something went wrong on our side.", retryable=False
                    )
                )

        return tool

    return wrap
