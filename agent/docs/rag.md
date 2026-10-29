# RAG - Detailed Design

Part of [00_Architecture_Overview.md](../../docs/00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Answer product and store questions from trusted documents, with citations. Live data (price, stock, status) never comes from RAG.

## 2. Technology
| Concern | Choice |
|---|---|
| Parsing | Own parser plugins + common Document model (ADR-039); Docling for PDF layout/tables/OCR; python-docx, openpyxl/pandas, python-pptx, trafilatura, `email`, markdown-it-py |
| Embeddings | `bge-m3` (1024 dims) in every environment, via LiteLLM; `model_version` stored per vector; queries PII-masked before embedding; phase-3 bake-off vs Qwen3-Embedding-0.6B and nomic-embed-text v1.5 on our eval set; model change = blue/green re-index (ADR-040) |
| Store | Postgres + pgvector (HNSW) + full-text, behind a retriever interface (ADR-011); BM25 upgrade: ParadeDB `pg_search`; production reads on a replica |
| Fusion | Reciprocal Rank Fusion |
| Reranker | `bge-reranker-v2-m3` |
| Evaluation | Ragas |

## 3. Ingestion pipeline (ADR-039)
Multi-format parsing system: every format is parsed by a dedicated parser plugin into one common Document model; everything after parsing is format-agnostic.

```
file / upload / email
  -> 1. Detect     real type from magic bytes (not extension); unknown -> quarantine
  -> 2. Parse      parser plugin per format -> Document model
  -> 3. Normalize  Unicode NFKC, whitespace, de-hyphenation, repeated header/footer removal
  -> 4. Validate   empty/garbled text -> OCR retry; low OCR confidence -> flag
  -> 5. Clean      strip prices, stock, availability text (NFR 8)
  -> 6. Chunk      ADR-034 rules applied to Document model structure
  -> 7. Embed + index  pgvector + full-text (ADR-011)
  failures -> quarantine with reason (visible in AI Operations)
```
- Idempotent: content hash per file; unchanged files skipped; parser version recorded so a parser upgrade can trigger re-parse.
- Entry points: drop folder `data/inbox/` and `POST /ingest` (ops-admin upload in AI Operations); both call the same pipeline. Re-indexing also triggered by `catalog-events` and Git changes to `data/knowledge/`.
- Runs in an ingestion worker process inside the `buywise-agent` deployable, separate from the chat API process, so OCR cannot slow chat turns (final location of re-indexing still deferred, docs/00 #3).

**Cleaning rule:** prices, stock and availability text are removed before chunking (NFR 8: live data only from tools); an eval check confirms no answer takes a price from a chunk.

### 3a. Knowledge sources (ADR-033, formats per ADR-039)
| Doc type | Source | Format |
|---|---|---|
| Spec sheets | Generated from catalog seed data (Jinja2 templates) | Markdown |
| Product overviews | Generated from catalog seed data; factual, our own wording | Markdown |
| Store info | Generated from stores seed data | Markdown |
| Compatibility notes | Catalog `compatibility` table + short written notes | Markdown / TXT |
| Policies | Written from the approved outline (`data/knowledge/_outline/policy_outline.md`) | DOCX (shipping v1/v2, privacy), digital PDF (warranty, payment), Markdown |
| Policy update notice | Written | Email (.eml) with DOCX attachment |
| Shipping rates by state, order limits, store hours + holidays | Written / generated | XLSX, CSV |
| Holiday hours notice, printed rate card | Rendered then degraded (skew, noise) | Scanned PDF, PNG |
| Staff training: pickup process | Written | PPTX |
| FAQs (~200) | Written, reviewed | HTML help-centre pages (with boilerplate) |
| How-to / setup guides | Written, reviewed | HTML, Markdown |

Metadata on every doc (front matter, document properties, email headers or a sidecar `.meta.yaml` for formats without metadata): `doc_type`, `product_family`, `model`, `brand_id`, `effective_date`, `version`.

### 3b. Chunking (ADR-034)
Applied to the Document model, so the same rules work for every format. Structure-aware, per doc type; sizes in embedding-model tokens; starting values tuned with Ragas.
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

### 3c. Parser plugins (ADR-039)
| Format | Detection | Parser / libraries | Techniques |
|---|---|---|---|
| Digital PDF | `%PDF` + text layer present | pypdfium2 text layer; Docling layout + TableFormer tables | Reading order (multi-column), table structure, header/footer removal, page provenance |
| Scanned PDF / PNG | `%PDF` without text layer per page, or image | Preprocess (deskew, denoise, binarize) -> OCR (Docling OCR with Tesseract/EasyOCR) | Per-page OCR fallback, OCR confidence scores |
| DOCX | OOXML zip, `word/` part | python-docx | Heading levels from styles, numbered lists, tables, core properties as metadata |
| HTML | `<html` / text/html | trafilatura (boilerplate removal) + DOM walk (BeautifulSoup/lxml) | Strip nav/footer/cookie banners, DOM -> structure, HTML tables |
| XLSX / CSV | OOXML zip `xl/` part / CSV sniffing | openpyxl / pandas | Header-row detection, merged cells, multi-sheet, rows -> records |
| PPTX | OOXML zip `ppt/` part | python-pptx | Slide order, titles, bullets, speaker notes, slide tables |
| Email (.eml) | RFC 5322 headers | Python `email` package | MIME multipart, body extraction, recursive parsing of attachments |
| Markdown / TXT | text sniffing | markdown-it-py | Baseline structure |
| JSON (generated catalog docs) | JSON parse | Template renderer | Structured data -> text |

**Document model** (every parser's output): ordered elements - `heading(level)`, `paragraph`, `list(items)`, `table(rows)`, `record(fields)`, `figure(caption)` - plus document metadata (front matter / properties / email headers). Each element carries **provenance**: PDF page + bounding box, `sheet!row`, slide number, DOM path, or attachment name - used for precise citations.

**Quality:** golden tests per sample file (expected Document model snapshot in CI); parse metrics (pages, elements, OCR confidence, duration) per document.


### 3d. Parsing in production - context for ADR-039
**Common production pattern** (independent of tool): route by format and difficulty (cheap text-layer path for clean digital docs, expensive OCR / layout / vision-model path for scans and complex layouts); convert everything to one intermediate representation; keep provenance; quality checks with automatic retry on a stronger parser and human review for leftovers; asynchronous queue-fed workers, idempotent and retryable, failing into quarantine; parser version recorded so upgrades can trigger re-parse.

**Tool landscape** (as of 2025-26; fast-moving):
| Category | Examples | Typical use |
|---|---|---|
| Open-source multi-format toolkits | Docling, Unstructured | RAG pipelines |
| Text extraction everywhere | Apache Tika | Search and enterprise indexing; weak on structure |
| PDF specialists | PyMuPDF, pdfplumber, Marker, MinerU | High-volume PDF, academic papers |
| Managed cloud document AI | Azure AI Document Intelligence, Textract, Document AI | Scans, forms, compliance-heavy enterprises |
| LLM-era parsing services | LlamaParse, Reducto, Mistral OCR | Fast-moving RAG products |
| Vision-language model parsing | Page images to a VLM (e.g. Docling VLM pipeline) | Complex layouts; costly per page |

Typical preference: an open-source toolkit for most documents, a managed or VLM service only for hard cases, all mapped into one internal model.

**Why our own Document model instead of DoclingDocument:** DoclingDocument is rich (text items, cell-level tables, pictures, groups, header/footer "furniture", page + bounding-box provenance, exporters, chunkers), but its provenance is page-based and spreadsheet rows are not first-class records. Our model natively supports `sheet!row`, slide, DOM path and email-attachment provenance plus `record` elements, and isolates the core pipeline from Docling's schema changes (anti-corruption layer). Docling stays the engine for PDF layout, tables and OCR behind an adapter; other engines (managed document AI, VLM) can be added later as further adapters and routed by difficulty.

## 4. Retrieval pipeline
query understanding -> metadata filters -> hybrid search (dense + keyword) -> RRF -> rerank -> top-k with citations - TBD in detail.

## 5. Techniques (planned)
Multi-format parsing (layout, tables, OCR, boilerplate removal, MIME), chunking strategies, parent-child chunks, metadata filters, hybrid search, reranking, query rewriting, agentic retrieval, citations, semantic cache, freshness via events, evaluation in CI.

## 6. Deployable
RAG pipeline runs inside `buywise-agent`.

## 7. Open decisions
1. ~~Vector store~~ - decided: pgvector + full-text (ADR-011).
2. ~~Chunk size / strategy per document type~~ - decided (ADR-034).
3. Re-indexing location (deferred to implementation).
