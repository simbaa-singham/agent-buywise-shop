"""Agent HTTP API (ADR-029): POST /turns returns 202 at once; the turn runs in the background and its events go to
the conversation's Redis Stream. Run: uv run uvicorn buywise_agent.api:app --port 8000"""
import asyncio
import logging
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .graph import run_turn

log = logging.getLogger("buywise.agent")
app = FastAPI(title="buywise-agent")
_running: set[asyncio.Task] = set()


class TurnRequest(BaseModel):
    conversationId: str
    text: str = Field(min_length=1, max_length=4000)
    customerId: str | None = None  # set by the BFF from the logged-in session, never by the browser
    customerName: str | None = None


@app.post("/turns", status_code=202)
async def turns(req: TurnRequest) -> dict:
    message_id = f"m_{uuid.uuid4().hex[:16]}"
    task = asyncio.create_task(run_turn(req.conversationId, message_id, req.text, req.customerId, req.customerName))
    _running.add(task)
    task.add_done_callback(_finished)
    return {"messageId": message_id}


def _finished(task: asyncio.Task) -> None:
    _running.discard(task)
    if not task.cancelled() and task.exception():
        log.error("turn failed", exc_info=task.exception())


@app.get("/health")
async def health() -> dict:
    return {"status": "UP"}
