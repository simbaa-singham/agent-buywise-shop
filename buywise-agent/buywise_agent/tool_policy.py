"""What the agent may do with a tool, decided by the tool's own annotations (ADR-053) - not by its name.

- Not read-only (place, cancel): never run on the model's word alone. The agent shows a preview and runs the tool
  only after the customer says yes. (Phase M step 5 moves this confirmation into MCP itself, ADR-052.)
- Read-only or idempotent: retried once after 0.5 s if the error says `retryable` (ADR-055).
- Read-only: the same call within one turn is answered from a per-turn cache.
"""

import asyncio
import json
from collections.abc import Awaitable, Callable

from .mcp_tools import ToolInfo

RETRY_DELAY_S = 0.5
Result = tuple[bool, str, dict | None]
Call = Callable[[ToolInfo, dict, str | None], Awaitable[Result]]

# What to show the customer before a write runs. Until step 5 the agent picks the read-only tool that previews it;
# afterwards MCP sends the confirmation itself.
PREVIEW = {"place_order": "quote_order", "cancel_order": "get_order"}


def needs_confirmation(info: ToolInfo | None) -> bool:
    return info is None or not info.read_only


class ToolRunner:
    """One per turn: holds that turn's read-only cache."""

    def __init__(self, call: Call, customer_id: str | None, delay_s: float = RETRY_DELAY_S):
        self.call, self.customer_id, self.delay_s = call, customer_id, delay_s
        self.cache: dict[str, Result] = {}

    async def run(self, info: ToolInfo, args: dict) -> Result:
        key = f"{info.name}:{json.dumps(args, sort_keys=True)}"
        if info.read_only and key in self.cache:
            return self.cache[key]
        result = await self.call(info, args, self.customer_id)
        ok, _, data = result
        if not ok and (info.read_only or info.idempotent) and (data or {}).get("retryable"):
            await asyncio.sleep(self.delay_s)
            result = await self.call(info, args, self.customer_id)
        if info.read_only and result[0]:
            self.cache[key] = result
        return result

    async def prepare(self, info: ToolInfo, args: dict, tools: dict[str, ToolInfo]) -> tuple[str, dict | None]:
        """A write the model asked for: run its preview instead and return (text for the model, pending action).
        Pending is None when the preview failed (nothing to confirm)."""
        preview = tools.get(PREVIEW.get(info.name, ""))
        preview_args = {k: v for k, v in args.items() if preview and k in preview.input_schema.get("properties", {})}
        if preview:
            ok, text, _ = await self.run(preview, preview_args)
            if not ok:
                return text, None
        else:
            text = json.dumps(args)
        what = info.title.lower()
        return (f"NOT DONE YET - '{what}' needs the customer's confirmation. Details from the store system: {text}\n"
                f"Show the customer these details and ask them to reply 'yes' to {what}."), {"tool": info.name,
                                                                                               "args": args}
