"""bge-m3 embeddings through LiteLLM (ADR-040)."""
import httpx

from ..config import settings

EMBED_VERSION = "bge-m3@ollama"


def embed(texts: list[str]) -> list[list[float]]:
    resp = httpx.post(f"{settings.llm_gateway_url}/v1/embeddings", timeout=120,
                      headers={"Authorization": f"Bearer {settings.litellm_master_key}"},
                      json={"model": settings.embed_model, "input": texts})
    resp.raise_for_status()
    return [d["embedding"] for d in sorted(resp.json()["data"], key=lambda d: d["index"])]
