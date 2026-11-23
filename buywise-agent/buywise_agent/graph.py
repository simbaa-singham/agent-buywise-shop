"""One chat turn as a LangGraph loop: llm -> (tools -> llm)* -> end.

Simplified for the local end-to-end build: the model routes by choosing tools (the ADR-030 routing cascade comes
later). Text streams to the conversation's Redis Stream as it is generated.
Tools come from MCP with their annotations; what the agent may do with each is decided in tool_policy (ADR-053):
a tool that changes data (place, cancel) never runs on the model's word - the customer sees a preview and says yes.
"""
import datetime as dt
import json
import logging
import re
from typing import Annotated, TypedDict

import redis.asyncio as redis
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from .config import settings
from .events import Emitter
from .mcp_tools import ToolInfo, call_mcp, catalog
from .tool_policy import ToolRunner, needs_confirmation
from .tools import KNOWLEDGE_SPEC, knowledge

MAX_TOOL_ROUNDS = 5
log = logging.getLogger("buywise.agent")
logging.basicConfig(level=logging.INFO)
HISTORY_TURNS = 6
store = redis.from_url(settings.redis_url, decode_responses=True)
YES = re.compile(r"^\s*(yes|y|yeah|yep|sure|confirm(ed)?|ok(ay)?|go ahead|place (it|the order)|do it)\b", re.IGNORECASE)

base_model = ChatOpenAI(model=settings.llm_primary_model, base_url=f"{settings.llm_gateway_url}/v1",
                        api_key=settings.litellm_master_key, temperature=0.2, timeout=120, stream_usage=True)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    citations: list[dict]
    pending: dict | None
    rounds: int


class Turn:
    """Per-turn context: who is asking and where the reply streams to."""

    def __init__(self, emitter: Emitter, customer_id: str | None, tools: dict[str, ToolInfo]):
        self.emitter = emitter
        self.customer_id = customer_id
        self.tools = tools  # discovered from MCP this turn (cached per ttlMs)
        self.runner = ToolRunner(call_mcp, customer_id)
        self.model = base_model.bind_tools([t.model_spec() for t in tools.values()] + [KNOWLEDGE_SPEC])
        self.started = False
        self.text = ""

    async def say(self, delta: str) -> None:
        if not self.started:
            await self.emitter.emit("message.started", {"role": "assistant"})
            self.started = True
        self.text += delta
        await self.emitter.emit("message.delta", {"text": delta})


async def llm(state: State, config: RunnableConfig) -> dict:
    turn: Turn = config["configurable"]["turn"]
    await turn.emitter.status("generating", "Writing the answer")
    full: AIMessageChunk | None = None
    async for chunk in turn.model.astream(state["messages"]):
        full = chunk if full is None else full + chunk
        if chunk.content and not (full.tool_call_chunks):
            await turn.say(chunk.content)
    return {"messages": [full or AIMessage(content="")], "rounds": state["rounds"] + 1}


def route(state: State) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) and state["rounds"] <= MAX_TOOL_ROUNDS else END


async def tools(state: State, config: RunnableConfig) -> dict:
    turn: Turn = config["configurable"]["turn"]
    out, citations, pending = [], list(state["citations"]), state["pending"]
    for call in state["messages"][-1].tool_calls:
        name, args = call["name"], call["args"]
        info = turn.tools.get(name)
        if name == "search_knowledge":
            await turn.emitter.status("retrieval", "Searching help articles")
            hits, text = await knowledge(args.get("query", ""))
            citations += [{"documentId": h["documentId"], "title": h["title"], "location": h["location"]} for h in hits]
        elif info is None:
            text = f"invalid_input: There is no tool called {name}."
        elif needs_confirmation(info):  # from the annotations, not the tool name (ADR-053)
            await turn.emitter.status("tool_call", info.title)
            text, action = await turn.runner.prepare(info, args, turn.tools)
            pending = action or pending
        else:
            await turn.emitter.status("tool_call", info.title)
            ok, text, data = await turn.runner.run(info, args)
            if ok and name in ("check_stock", "get_product"):
                await product_card(turn.emitter, name, data)
        log.info("tool %s %s -> %s", name, json.dumps(args), text[:200].replace("\n", " "))
        out.append(ToolMessage(content=text, tool_call_id=call["id"], name=name))
    return {"messages": out, "citations": citations, "pending": pending}


async def product_card(emitter: Emitter, name: str, data: dict | None) -> None:
    """Builds the chat contract's camelCase product card (ADR-024) from the tool's typed snake_case result
    (ADR-054): get_product -> ProductDetail, check_stock -> StockReport."""
    if not data:
        return
    card = {"productId": data["product_id"], "model": data["model"], "availability": data["availability"]}
    if name == "get_product" and data["variants"]:
        card["listPrice"] = min(v["list_price"] for v in data["variants"])
        if data.get("ships_on"):
            card["shipsOn"] = data["ships_on"]
    if name == "check_stock" and data["stock"]:
        card["listPrice"] = min(s["list_price"] for s in data["stock"])
        if data.get("store_id"):
            first = data["stock"][0]
            card["stockAtStore"] = {"storeId": first["store_id"], "storeName": first["store_name"],
                                    "quantity": data["total_units"]}
    await emitter.emit("block.product_card", card)


graph = StateGraph(State)
graph.add_node("llm", llm)
graph.add_node("tools", tools)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", route, {"tools": "tools", END: END})
graph.add_edge("tools", "llm")
app = graph.compile()

_stores: str | None = None


async def stores_line() -> str:
    global _stores
    if _stores is None:  # through MCP, never services directly; becomes an MCP resource in Phase M step 7 (ADR-058)
        stores = (await catalog.tools()).get("list_stores")
        ok, _, data = await call_mcp(stores, {}, None) if stores else (False, "", None)
        if not ok or not data:
            return "(store list unavailable - use list_stores)"
        _stores = "; ".join(f"{s['name']} - {s['city']}, {s['state']} (store_id {s['store_id']})"
                            for s in data["stores"])
    return _stores


async def system_prompt(customer_name: str | None) -> str:
    who = (f"The customer is logged in as {customer_name}." if customer_name else
           "The customer is a guest (not logged in). Orders and order lookups need login: ask them to use the "
           "Log in button.")
    return f"""You are the BuyWise shopping assistant for a US online electronics store with delivery and in-store pickup.
Today is {dt.date.today():%A, %B %d, %Y}. {who}

Rules:
- Prices, stock and order details come ONLY from tool results in this conversation. Never guess them and never take
  prices from help articles.
- To answer about a product: search_products to get its product_id, then check_stock (stock) or get_product (specs,
  variants, prices).
- Policy, shipping, pickup, returns, warranty, payment or how-to questions: call search_knowledge and answer only from
  what it returns. If nothing relevant comes back, say you don't know.
- To order: the customer must be logged in. Find the exact variant sku (ask storage/color if unclear), ask pickup (which
  store) or delivery (to the address on file). As soon as you know the sku and pickup/delivery, call place_order
  immediately - do NOT ask "shall I place it?" yourself: the system shows the quote and asks the customer to
  confirm. cancel_order works the same way: call it, and the system asks the customer to confirm.
- Order questions without an order id: call list_my_orders. Never make up an order id.
- Answer briefly and warmly in Markdown. Don't mention tools or internal ids unless useful (order ids are useful).

Stores: {await stores_line()}"""


async def load_history(conversation_id: str) -> list[BaseMessage]:
    raw = await store.lrange(f"conv:{conversation_id}:history", -2 * HISTORY_TURNS, -1)
    msgs = [json.loads(m) for m in raw]
    return [HumanMessage(m["text"]) if m["role"] == "user" else AIMessage(m["text"]) for m in msgs]


async def save_history(conversation_id: str, user: str, assistant: str) -> None:
    key = f"conv:{conversation_id}:history"
    await store.rpush(key, json.dumps({"role": "user", "text": user}),
                      json.dumps({"role": "assistant", "text": assistant}))
    await store.ltrim(key, -40, -1)
    await store.expire(key, 60 * 60 * 24)


async def run_turn(conversation_id: str, message_id: str, text: str,
                   customer_id: str | None, customer_name: str | None) -> None:
    emitter = Emitter(conversation_id, message_id)
    turn = Turn(emitter, customer_id, await catalog.tools())
    pending_key = f"conv:{conversation_id}:pending_action"
    try:
        await emitter.status("thinking", "Thinking")
        pending = await store.get(pending_key)
        await store.delete(pending_key)
        if pending and customer_id and YES.match(text):
            await run_confirmed(turn, json.loads(pending))
            citations = []
        else:
            prompt = text
            if YES.match(text) and customer_id:
                # a small model often asks "shall I place it?" itself; a yes then means: prepare the real quote
                prompt += ("\n\n(The customer agrees. If this is about ordering, call place_order now with the sku "
                           "and pickup/delivery discussed above.)")
            messages = [SystemMessage(await system_prompt(customer_name)), *await load_history(conversation_id),
                        HumanMessage(prompt)]
            result = await app.ainvoke({"messages": messages, "citations": [], "pending": None, "rounds": 0},
                                       config={"configurable": {"turn": turn}, "recursion_limit": 30})
            if not turn.text.strip():
                await turn.say("Sorry, I couldn't work that out. Could you rephrase?")
            if result["pending"]:
                await store.set(pending_key, json.dumps(result["pending"]), ex=15 * 60)
            seen, citations = set(), []
            for c in result["citations"]:
                key = (c["documentId"], c["location"])
                if key not in seen and len(citations) < 3:
                    seen.add(key)
                    citations.append({k: v for k, v in c.items() if v is not None})
        payload = {"text": turn.text}
        if citations:
            payload["citations"] = citations
        await emitter.emit("message.completed", payload)
        await save_history(conversation_id, text, turn.text)
    except Exception:  # never leave the customer without an answer or a fallback (NFR 7)
        await emitter.emit("message.failed", {"reason": "error", "userMessage":
                           "Sorry, something went wrong on our side. Please try again in a moment."})
        raise


async def run_confirmed(turn: Turn, action: dict) -> None:
    """The customer said yes to a pending write: run it now (no retry unless the tool is idempotent, ADR-053)."""
    info = turn.tools.get(action["tool"])
    if info is None:
        await turn.say("Sorry, that action is no longer available. Please ask again.")
        return
    await turn.emitter.status("tool_call", info.title)
    ok, _, data = await turn.runner.run(info, action["args"])
    if not ok or not data:
        reason = data["message"] if data else "the store system is not responding"
        await turn.say(f"Sorry, I couldn't {info.title.lower()}: {reason}")
        return
    if info.name == "cancel_order":
        await turn.say(f"Your order **{data['order_id']}** is cancelled."
                       + (" The items are back on the store's shelf." if data["fulfilment"]["type"] == "pickup" else ""))
        return
    f = data["fulfilment"]
    where = "delivery to your address on file"
    if f["type"] == "pickup":
        hold = (data.get("held_at_store_until") or "")[:10]
        where = f"pickup at **{f.get('store_name') or f['store_id']}**" + (f" (held until {hold})" if hold else "")
    lines = "\n".join(f"- {i['quantity']} x {i['model']} ({i['sku']}) - ${i['unit_price']:,.2f}" for i in data["items"])
    await turn.say(f"Your order **{data['order_id']}** is placed for {where}.\n\n{lines}\n\n"
                   f"Subtotal ${data['subtotal']:,.2f}, tax ${data['tax']:,.2f}, **total ${data['total']:,.2f}**. "
                   "You'll get updates as it moves along.")
