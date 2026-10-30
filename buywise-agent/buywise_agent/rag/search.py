"""Vector search over rag.chunks (cosine distance, HNSW)."""
import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from ..config import settings
from .embed import embed


def search(query: str, k: int = 4) -> list[dict]:
    vector = np.array(embed([query])[0])
    with psycopg.connect(settings.database_url) as conn:
        register_vector(conn)
        rows = conn.execute(
            "SELECT document_id, title, location, content, embedding <=> %s AS distance"
            " FROM rag.chunks ORDER BY embedding <=> %s LIMIT %s", (vector, vector, k)).fetchall()
    return [{"documentId": r[0], "title": r[1], "location": r[2], "content": r[3], "distance": round(r[4], 3)}
            for r in rows]
