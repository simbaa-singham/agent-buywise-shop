"""Writes ADR-024 chat events to the conversation's Redis Stream conv:{id} (ADR-029).
Every event is validated against the generated strict models before it is written (ADR-044)."""
import datetime as dt
import json

import redis.asyncio as redis

from .config import settings
from .contracts.chat_contract import ChatEvent

r = redis.from_url(settings.redis_url, decode_responses=True)
STREAM_MAXLEN = 1000


class Emitter:
    def __init__(self, conversation_id: str, message_id: str):
        self.conversation_id = conversation_id
        self.message_id = message_id

    async def emit(self, type_: str, payload: dict) -> None:
        event = {"v": 1, "ts": dt.datetime.now(dt.UTC).isoformat(), "conversationId": self.conversation_id,
                 "messageId": self.message_id, "type": type_, "payload": payload}
        ChatEvent.model_validate(event)  # strict when writing
        await r.xadd(f"conv:{self.conversation_id}", {"event": json.dumps(event)},
                     maxlen=STREAM_MAXLEN, approximate=True)

    async def status(self, stage: str, label: str) -> None:
        await self.emit("status.updated", {"stage": stage, "label": label})
