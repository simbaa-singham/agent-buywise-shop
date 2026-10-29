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
parse -> clean -> chunk -> enrich metadata -> embed -> index; idempotent with content hashes; re-indexing triggered by `catalog-events` (where it runs is deferred: agent vs event consumers) and by Git changes to `data/knowledge/`.

**Cleaning rule:** prices, stock and availability text are removed before chunking (NFR 8: live data only from tools); an eval check confirms no answer takes a price from a chunk.

### 3a. Knowledge sources (ADR-033)
| Doc type | Source | Format |
|---|---|---|
| Spec sheets | Generated from catalog seed data (Jinja2 templates) | Markdown |
| Product overviews | Generated from catalog seed data; factual, our own wording | Markdown |
| Store info | Generated from stores seed data | Markdown |
| Compatibility notes | Catalog `compatibility` table + short written notes | Markdown |
| Policies (shipping, pickup, warranty, payment) | Written from an architect-approved outline | Markdown; a few rendered to PDF (Docling PDF path) |
| FAQs (~200) | Written, reviewed | Markdown |
| How-to / setup guides | Written, reviewed | Markdown |

Front matter on every doc: `doc_type`, `product_family`, `model`, `brand_id`, `effective_date`, `version`.

### 3b. Chunking (ADR-034)
Structure-aware, per doc type; sizes in embedding-model tokens; starting values tuned with Ragas.
| Type | Rule | Child chunk (searched) | Parent (sent to LLM) |
|---|---|---|---|
| Spec sheets | One chunk per spec group per model, rows as sentences | ~150-250 | Model's full spec table |
| Product overviews | One chunk per model | ~200-300 | Itself |
| Compatibility | One note per chunk | ~100-200 | Itself |
| Policies | By heading, long sections split by paragraph | ~300-400 | Section (~1,000-1,500) |
| FAQs | One Q&A pair | Q&A | Q&A |
| How-to guides | Step groups under a heading; never split a step | ~300-400 | Guide section |
| Store info | One chunk per store | Store record | Store record |

- Parent-child retrieval: children are searched, parents are given to the LLM.
- Context header prepended before embedding: title + heading path + model, e.g. `Policies > Store pickup > Hold period | US`. LLM-generated context (contextual retrieval) is a phase-2 experiment, kept only if Ragas shows gains (ingest tokens count against the budget).
- Metadata for filters: `doc_type`, `product_family`, `model`, `variant`, `brand_id`, `store_id`, `region`, `effective_date`, `version`.

## 4. Retrieval pipeline
query understanding -> metadata filters -> hybrid search (dense + keyword) -> RRF -> rerank -> top-k with citations - TBD in detail.

## 5. Techniques (planned)
Chunking strategies, parent-child chunks, metadata filters, hybrid search, reranking, query rewriting, agentic retrieval, citations, semantic cache, freshness via events, evaluation in CI.

## 6. Deployable
RAG pipeline runs inside `buywise-agent`.

## 7. Open decisions
1. ~~Vector store~~ - decided: pgvector + full-text (ADR-011).
2. ~~Chunk size / strategy per document type~~ - decided (ADR-034).
3. Re-indexing location (deferred to implementation).
