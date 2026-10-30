"""Knowledge ingestion, simplified for the local end-to-end build: Markdown, text, HTML, digital PDF and DOCX.
Scanned files, email, spreadsheets and slides wait for the full pipeline (ADR-039).

detect (extension) -> parse into sections with a location -> skip staff-only / superseded / expired documents
-> chunk (~1,000 chars on paragraph boundaries) -> embed (bge-m3) -> replace rows in rag.chunks.
Run: uv run python -m buywise_agent.rag.ingest
"""
import datetime as dt
import re
from pathlib import Path

import psycopg
import yaml
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pgvector.psycopg import register_vector
from pypdf import PdfReader

from ..config import settings
from .embed import EMBED_VERSION, embed

FORMATS = {".md", ".txt", ".html", ".pdf", ".docx"}
CHUNK_CHARS = 1000

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE IF NOT EXISTS rag.chunks (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id   text   NOT NULL,
    title         text   NOT NULL,
    doc_type      text,
    location      text,
    content       text   NOT NULL,
    embedding     vector(1024) NOT NULL,
    model_version text   NOT NULL
);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON rag.chunks USING hnsw (embedding vector_cosine_ops);
"""


def metadata(path: Path) -> tuple[dict, str | None]:
    """Returns (meta, text-without-front-matter for .md)."""
    side = path.with_name(path.name + ".meta.yaml")
    if side.exists():
        return yaml.safe_load(side.read_text()) or {}, None
    if path.suffix == ".md":
        text = path.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if m:
            return yaml.safe_load(m.group(1)) or {}, text[m.end():]
        return {}, text
    return {}, None


def usable(meta: dict) -> bool:
    today = dt.date.today().isoformat()
    if meta.get("audience") == "staff" or meta.get("doc_type") == "internal_note":
        return False
    if meta.get("superseded_on") and str(meta["superseded_on"]) <= today:
        return False
    if meta.get("expires") and str(meta["expires"]) < today:
        return False
    if meta.get("effective_date") and str(meta["effective_date"]) > today:
        return False
    return True


def sections(path: Path, md_text: str | None) -> list[tuple[str | None, str]]:
    """(location, text) pairs. Location is a section heading or a page number."""
    ext = path.suffix
    if ext in (".md", ".txt"):
        text = md_text if md_text is not None else path.read_text()
        parts = re.split(r"^(#{1,3} .+)$", text, flags=re.MULTILINE)
        out, heading = [], None
        for part in parts:
            if re.match(r"^#{1,3} ", part):
                heading = part.lstrip("# ").strip()
            elif part.strip():
                out.append((heading, part.strip()))
        return out
    if ext == ".html":
        soup = BeautifulSoup(path.read_text(), "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "form", "aside"]):
            tag.decompose()
        for tag in soup.select("#cookie-banner, .cookie"):
            tag.decompose()
        body = soup.find("main") or soup.find("article") or soup.body or soup
        out, heading, buf = [], None, []
        for el in body.find_all(["h1", "h2", "h3", "p", "li", "dt", "dd", "td"]):
            if el.name in ("h1", "h2", "h3"):
                if buf:
                    out.append((heading, "\n".join(buf)))
                heading, buf = el.get_text(" ", strip=True), []
            else:
                text = el.get_text(" ", strip=True)
                if text:
                    buf.append(text)
        if buf:
            out.append((heading, "\n".join(buf)))
        return out
    if ext == ".pdf":
        return [(f"page {i}", (page.extract_text() or "").strip())
                for i, page in enumerate(PdfReader(path).pages, 1) if (page.extract_text() or "").strip()]
    if ext == ".docx":
        out, heading, buf = [], None, []
        for p in DocxDocument(path).paragraphs:
            if p.style.name.lower().startswith(("heading", "title")):
                if buf:
                    out.append((heading, "\n".join(buf)))
                heading, buf = p.text.strip(), []
            elif p.text.strip():
                buf.append(p.text.strip())
        if buf:
            out.append((heading, "\n".join(buf)))
        return out
    return []


def chunks(secs: list[tuple[str | None, str]]) -> list[tuple[str | None, str]]:
    out = []
    for location, text in secs:
        buf = ""
        for para in re.split(r"\n\s*\n|\n", text):
            if buf and len(buf) + len(para) > CHUNK_CHARS:
                out.append((location, buf.strip()))
                buf = ""
            buf += para + "\n"
        if buf.strip():
            out.append((location, buf.strip()))
    return out


def main():
    root = Path(settings.knowledge_dir).resolve()
    rows, skipped = [], []
    paths = [p for p in sorted(root.rglob("*"))
             if p.suffix in FORMATS and "_outline" not in p.parts and p.is_file()]
    # a document replaced by a newer one that is already in effect is left out
    replaced = {metadata(p)[0].get("supersedes") for p in paths if usable(metadata(p)[0])}
    for path in paths:
        meta, md_text = metadata(path)
        if not usable(meta) or path.stem in replaced:
            skipped.append(f"{path.relative_to(root)} (staff-only, superseded, expired or not yet effective)")
            continue
        parts = chunks(sections(path, md_text))
        if not parts:
            skipped.append(f"{path.relative_to(root)} (no text - scanned?)")
            continue
        doc_id = str(path.relative_to(root))
        title = meta.get("title") or path.stem.replace("_", " ").replace("-", " ")
        for location, text in parts:
            rows.append((doc_id, title, meta.get("doc_type"), location, f"{title}\n{location or ''}\n{text}".strip()))

    print(f"{len(rows)} chunks from {len({r[0] for r in rows})} documents; embedding...")
    vectors = []
    for i in range(0, len(rows), 32):
        vectors += embed([r[4] for r in rows[i:i + 32]])

    with psycopg.connect(settings.database_url) as conn:
        conn.execute(SCHEMA)
        register_vector(conn)
        with conn.transaction():
            conn.execute("TRUNCATE rag.chunks")
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO rag.chunks (document_id, title, doc_type, location, content, embedding, model_version)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [(*r, v, EMBED_VERSION) for r, v in zip(rows, vectors)])
    print(f"stored {len(rows)} chunks; skipped {len(skipped)}:")
    for s in skipped:
        print("  -", s)


if __name__ == "__main__":
    main()
