"""Measure the LLM hardware factor k (docs/00 section 7.1).

k = production reference tokens/s / local tokens/s, measured through LiteLLM (ADR-026) so the
measurement covers the same path the agent uses. The production reference is the NFR 5 target
(>= 50 tokens/s per stream) until the production LLM is decided (docs/00 #5).
Writes deploy/local/scale.yaml with S and k; local LLM deadlines and targets derive from it.
"""
import json
import os
import statistics
import time
import urllib.request
from pathlib import Path

GATEWAY = os.environ.get("LLM_GATEWAY_URL", "http://localhost:4000")
KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-buywise-local")
MODEL = os.environ.get("LLM_PRIMARY_MODEL", "buywise-primary")
PROD_TOKENS_PER_SEC = 50.0
S = 40
RUNS = 5
PROMPT = "In about 150 words, explain how in-store pickup works at an electronics store."
OUT = Path(__file__).resolve().parents[1] / "local" / "scale.yaml"


def one_run():
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": PROMPT}],
                       "max_tokens": 256, "stream": True, "stream_options": {"include_usage": True}}).encode()
    req = urllib.request.Request(f"{GATEWAY}/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    start, first, tokens = time.perf_counter(), None, 0
    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw in resp:
            line = raw.decode().strip()
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            chunk = json.loads(line[6:])
            if chunk.get("choices") and chunk["choices"][0]["delta"].get("content") and first is None:
                first = time.perf_counter()
            if chunk.get("usage"):
                tokens = chunk["usage"]["completion_tokens"]
    end = time.perf_counter()
    return {"ttft_s": first - start, "tokens": tokens, "tokens_per_sec": tokens / (end - first)}


def main():
    one_run()  # warm-up: loads the model into memory
    runs = [one_run() for _ in range(RUNS)]
    tps = statistics.median(r["tokens_per_sec"] for r in runs)
    ttft = statistics.median(r["ttft_s"] for r in runs)
    k = round(max(1.0, PROD_TOKENS_PER_SEC / tps), 2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        f"S: {S}\nk: {k}\nmeasured:\n  model: {MODEL}\n  median_tokens_per_sec: {tps:.1f}\n"
        f"  median_ttft_s: {ttft:.2f}\n  runs: {RUNS}\n  at: '{time.strftime('%Y-%m-%dT%H:%M:%S')}'\n"
        f"reference_tokens_per_sec: {PROD_TOKENS_PER_SEC}\n")
    print(f"local {tps:.1f} tokens/s, TTFT {ttft:.2f}s -> k = {k} (written to {OUT})")


if __name__ == "__main__":
    main()
