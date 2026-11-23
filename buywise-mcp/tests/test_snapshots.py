"""Tool contract snapshots (ADR-064): what each MCP server shows the model - tool names, descriptions, input/output
schemas, annotations, prompts and resources - must match tests/snapshots/{server}.json.

A description is a prompt: changing it changes the AI's behaviour, so every change must be seen in review.
The first snapshot of a server is its approved contract (the Phase M design is the base, not the prototype);
after an intended change: make snapshots (rewrites the files), then review the git diff.
A server without an approved snapshot yet is skipped. Runs in-process (no HTTP, no services needed).
"""
import json
import os
from pathlib import Path

import pytest
from mcp import Client

from buywise_mcp.app import SERVERS

SNAPSHOTS = Path(__file__).parent / "snapshots"
UPDATE = os.environ.get("SNAPSHOT_UPDATE") == "1"


def _dump(items) -> list[dict]:
    rows = [i.model_dump(mode="json", by_alias=True, exclude_none=True) for i in items]
    return sorted(rows, key=lambda r: r.get("name") or r.get("uri") or r.get("uriTemplate"))


async def _contract(server) -> dict:
    async with Client(server) as client:
        return {
            "server": server.name,
            "instructions": server.instructions,
            "tools": _dump((await client.list_tools()).tools),
            "prompts": _dump((await client.list_prompts()).prompts),
            "resources": _dump((await client.list_resources()).resources),
            "resource_templates": _dump((await client.list_resource_templates()).resource_templates),
        }


@pytest.mark.anyio
@pytest.mark.parametrize("domain", sorted(SERVERS))
async def test_contract_matches_snapshot(domain):
    actual = await _contract(SERVERS[domain])
    path = SNAPSHOTS / f"{domain}.json"
    if UPDATE:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(actual, indent=2, ensure_ascii=False) + "\n")
    if not path.exists():
        pytest.skip(f"{domain}: no approved contract yet - review the tools, then run make snapshots")
    expected = json.loads(path.read_text())
    assert actual == expected, f"{domain} tool contract changed: review it, then run make snapshots"
