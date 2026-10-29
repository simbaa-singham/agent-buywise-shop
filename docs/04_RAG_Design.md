# RAG - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Answer product and store questions from trusted documents, with citations. Live data (price, stock, status) never comes from RAG.

## 2. Technology
| Concern | Choice |
|---|---|
| Parsing | Docling |
| Embeddings | `nomic-embed-text` (dev) -> `bge-m3` (prod) |
| Store | Postgres + pgvector (HNSW) + full-text, behind a retriever interface (ADR-011); BM25 upgrade: ParadeDB `pg_search`; production reads on a replica |
| Fusion | Reciprocal Rank Fusion |
| Reranker | `bge-reranker-v2-m3` |
| Evaluation | Ragas |

## 3. Ingestion pipeline
parse -> clean -> chunk -> enrich metadata -> embed -> index; idempotent with content hashes; re-indexing triggered by `catalog-events` (where it runs is deferred: agent vs event consumers) - TBD in detail.

## 4. Retrieval pipeline
query understanding -> metadata filters -> hybrid search (dense + keyword) -> RRF -> rerank -> top-k with citations - TBD in detail.

## 5. Techniques (planned)
Chunking strategies, parent-child chunks, metadata filters, hybrid search, reranking, query rewriting, agentic retrieval, citations, semantic cache, freshness via events, evaluation in CI.

## 6. Deployable
RAG pipeline runs inside `buywise-agent`.

## 7. Open decisions
1. ~~Vector store~~ - decided: pgvector + full-text (ADR-011).
2. Chunk size / strategy per document type.
3. Re-indexing location (deferred to implementation).
