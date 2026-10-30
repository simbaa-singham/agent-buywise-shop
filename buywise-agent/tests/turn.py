"""Runs one chat turn through the agent API and prints the events from the Redis Stream.
Needs: stack, services, MCP and agent running. uv run python tests/turn.py "question" [customer_id] [conversation_id]"""
import json
import sys
import time
import uuid

import httpx
import redis

question = sys.argv[1]
customer = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
conv = sys.argv[3] if len(sys.argv) > 3 else f"c_{uuid.uuid4().hex[:8]}"
r = redis.Redis(decode_responses=True)
last = r.xinfo_stream(f"conv:{conv}")["last-generated-id"] if r.exists(f"conv:{conv}") else "0-0"
start = time.time()
resp = httpx.post("http://localhost:8000/turns", json={"conversationId": conv, "text": question, "customerId": customer,
                                                        "customerName": "Demo" if customer else None})
print("conversation", conv, resp.status_code, resp.json())
done = False
while not done and time.time() - start < 180:
    for _, entries in r.xread({f"conv:{conv}": last}, block=5000) or []:
        for entry_id, fields in entries:
            last = entry_id
            e = json.loads(fields["event"])
            t, p = e["type"], e["payload"]
            if t == "message.delta":
                print(p["text"], end="", flush=True)
            elif t == "message.completed":
                print(f"\n[completed in {time.time() - start:.1f}s] citations={p.get('citations')}")
                done = True
            else:
                print(f"\n[{t}] {json.dumps(p)}")
                done = t == "message.failed"
