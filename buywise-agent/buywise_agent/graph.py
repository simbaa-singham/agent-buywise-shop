"""One chat turn as a LangGraph loop: llm -> (tools -> llm)* -> end.

Simplified for the local end-to-end build: the model routes by choosing tools (the ADR-030 routing cascade comes
later). Text streams to the conversation's Redis Stream as it is generated. Placing an order is never done by the
model directly: place_order is turned into a quote, and the order is only placed after the customer says yes.
"""
import datetime as dt
import json
import logging
import re
from typing import Annotated, TypedDict

import httpx
import redis.asyncio as redis
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from .config import settings
from .events import Emitter
from .tools import STATUS_LABEL, call_mcp, knowledge, parse, tool_specs

MAX_TOOL_ROUNDS = 5
log = logging.getLogger("buywise.agent")
logging.basicConfig(level=logging.INFO)
HISTORY_TURNS = 6
store = redis.from_url(settings.redis_url, decode_responses=True)
YES = re.compile(r"^\s*(yes|y|yeah|yep|sure|confirm(ed)?|ok(ay)?|go ahead|place (it|the order)|do it)\b", re.IGNORECASE)

model = ChatOpenAI(model=settings.llm_primary_model, base_url=f"{settings.llm_gateway_url}/v1",
                   api_key=settings.litellm_master_key, temperature=0.2, timeout=120,
                   stream_usage=True).bind_tools(tool_specs())


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    citations: list[dict]
    pending: dict | None
    rounds: int


class Turn:
    """Per-turn context: who is asking and where the reply streams to."""

    def __init__(self, emitter: Emitter, customer_id: str | None):
        self.emitter = emitter
        self.customer_id = customer_id
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
    async for chunk in model.astream(state["messages"]):
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
        await turn.emitter.status("retrieval" if name == "search_knowledge" else "tool_call",
                                  STATUS_LABEL.get(name, "Working on it"))
        if name == "search_knowledge":
            hits, text = await knowledge(args.get("query", ""))
            citations += [{"documentId": h["documentId"], "title": h["title"], "location": h["location"]} for h in hits]
        elif name == "place_order":
            if not turn.customer_id:
                text = "Not placed: the customer is not logged in. Ask them to log in with the Log in button first."
            else:
                ok, text = await call_mcp("quote_order", args, turn.customer_id)
                if ok:
                    pending = args
                    text = ("NOT PLACED YET. Quote from the store system: " + text + "\nShow the customer the items, "
                            "pickup store or delivery, tax and total from this quote, and ask them to reply 'yes' "
                            "to place the order.")
        else:
            ok, text = await call_mcp(name, args, turn.customer_id)
            if ok and name in ("check_stock", "get_product"):
                await product_card(turn.emitter, name, args, parse(text))
        log.info("tool %s %s -> %s", name, json.dumps(args), text[:200].replace("\n", " "))
        out.append(ToolMessage(content=text, tool_call_id=call["id"], name=name))
    return {"messages": out, "citations": citations, "pending": pending}


async def product_card(emitter: Emitter, name: str, args: dict, data) -> None:
    if not isinstance(data, dict):
        return
    card = {"productId": data.get("product_id") or data.get("productId") or args.get("product_id"),
            "model": data.get("model", "")}
    if data.get("availability") in ("available", "preorder", "discontinued"):
        card["availability"] = data["availability"]
    if name == "get_product" and data.get("variants"):
        card["listPrice"] = min(v["listPrice"] for v in data["variants"])
        if data.get("availability") == "preorder" and data.get("releaseDate"):
            card["shipsOn"] = data["releaseDate"]
    if name == "check_stock" and data.get("stock"):
        card["listPrice"] = min(s["price"] for s in data["stock"])
        if args.get("store_id"):
            first = data["stock"][0]
            card["stockAtStore"] = {"storeId": first["store_id"], "storeName": first["store"],
                                    "quantity": sum(s["quantity"] for s in data["stock"])}
    if card["productId"] and card["model"]:
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
    if _stores is None:
        try:
            async with httpx.AsyncClient() as c:
                data = (await c.get(f"{settings.services_url}/api/stores", timeout=5)).json()
            _stores = "; ".join(f"{s['name']} - {s['city']}, {s['state']} (store_id {s['storeId']})" for s in data)
        except Exception:
            return "(store list unavailable - use list_stores)"
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
  store) or delivery (to the address on file), then call place_order. The system shows a quote and asks for a yes.
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
    turn = Turn(emitter, customer_id)
    pending_key = f"conv:{conversation_id}:pending_order"
    try:
        await emitter.status("thinking", "Thinking")
        pending = await store.get(pending_key)
        await store.delete(pending_key)
        if pending and customer_id and YES.match(text):
            await place_confirmed(turn, json.loads(pending))
            citations = []
        else:
            messages = [SystemMessage(await system_prompt(customer_name)), *await load_history(conversation_id),
                        HumanMessage(text)]
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
    except Exception as e:  # never leave the customer without an answer or a fallback (NFR 7)
        await emitter.emit("message.failed", {"reason": "error", "userMessage":
                           "Sorry, something went wrong on our side. Please try again in a moment."})
        raise e


async def place_confirmed(turn: Turn, order: dict) -> None:
    await turn.emitter.status("tool_call", "Placing your order")
    ok, text = await call_mcp("place_order", order, turn.customer_id)
    data = parse(text) if ok else None
    if not data:
        await turn.say(f"Sorry, I couldn't place the order: {text}")
        return
    f = data.get("fulfilment", {})
    where = "delivery to your address on file"
    if f.get("type") == "pickup":
        store_name = f.get("store_id")
        try:
            async with httpx.AsyncClient() as c:
                store_name = (await c.get(f"{settings.services_url}/api/stores/{store_name}", timeout=5)).json()["name"]
        except Exception:
            pass
        hold = (data.get("pickupHoldUntil") or "")[:10]
        where = f"pickup at **{store_name}**" + (f" (held until {hold})" if hold else "")
    lines = "\n".join(f"- {i['quantity']} x {i['model']} ({i['sku']}) - ${i['unitPrice']:,.2f}" for i in data["items"])
    await turn.say(f"Your order **{data['orderId']}** is placed for {where}.\n\n{lines}\n\n"
                   f"Subtotal ${data['subtotal']:,.2f}, tax ${data['tax']:,.2f}, **total ${data['total']:,.2f}**. "
                   "You'll get updates as it moves along.")
