"""The agent's own tool: knowledge search (RAG lives in the agent, ADR-011). Every other tool comes from MCP
(mcp_tools.py) - its name, description and schema are not repeated here."""
import asyncio

from .rag.search import search

KNOWLEDGE_SPEC = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": ("Search store policies, FAQs and how-to guides (shipping, pickup, returns, warranty, payment, "
                        "device setup). Use for any policy question."),
        "parameters": {"type": "object", "required": ["query"], "properties": {
            "query": {"type": "string", "description": "The policy or how-to question in the customer's words"}}},
    },
}


async def knowledge(query: str) -> tuple[list[dict], str]:
    hits = await asyncio.to_thread(search, query, 4)
    hits = [h for h in hits if h["distance"] < 0.55]
    text = "\n\n".join(f"[{i}] {h['title']} ({h['location'] or 'document'}):\n{h['content']}"
                       for i, h in enumerate(hits, 1)) or "No matching help article."
    return hits, text
