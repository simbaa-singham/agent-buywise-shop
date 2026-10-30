# data - Learning Notes

What the data module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Before phase 0 - creating the data (ADR-033, ADR-039)
- **Catalog:** 50 real products (real names, specs, list prices, verified by web search); maker never named (`brand_id` only); unverified tier prices flagged `price_verified: false`; unconfirmed specs left empty rather than invented; no images.
- **Synthetic people:** 500 customers, 2,000 orders, 100 tickets, 10 stores - Faker with a fixed random seed (same data every run). Emails `@example.com` and phones `555-01xx` are reserved and can never reach a real person.
- **Knowledge documents:** 103 files in 11 formats (DOCX, digital PDF, scanned PDF/PNG, HTML, XLSX, CSV, PPTX, EML with attachment, Markdown, TXT) to practise document parsing (phase 3).
- **Eval sets:** RAG questions, router messages, prompt-injection attacks, planted-price checks.
- **Facts vs text:** specs and prices are facts (usable); a maker's written descriptions and images are copyrighted (we write our own wording, use placeholders).

**Concept - designed test data:** good test data contains edge cases on purpose (out of stock, delayed orders, Alaska/Hawaii, two versions of a policy, planted prices that must be stripped).

---

## Phase 0

### Loading data by hand (step 4)
- No loading script: a one-time manual load, explained in [walkthroughs/load-seed-data.md](walkthroughs/load-seed-data.md) and run as one file, [walkthroughs/load-seed-data.sql](walkthroughs/load-seed-data.sql), in pgAdmin's Query Tool as `postgres`.
- First copy the files into the container: `docker cp data/seed buywise-postgres-1:/tmp/seed` (Postgres can only read files inside its container; `/tmp` is wiped when the container is recreated).
- Reading files needs admin rights, so the load runs as `postgres`; applications use their restricted users.

**SQL techniques used**
| Technique | Meaning |
|---|---|
| `pg_read_file('/tmp/seed/stores.json')` | Read a file as text |
| `::jsonb` | Convert text to JSON |
| `jsonb_array_elements(...)` | Turn a JSON array into one row per element |
| `->>` / `->` | Read a field as text / keep it as JSON |
| `ARRAY(SELECT jsonb_array_elements_text(...))` | JSON array -> Postgres text array |
| `nullif(x, 'launch')` | Turn a value into NULL |
| `CREATE TEMP VIEW` | Reusable query for this session only (combines six product files) |
| `BEGIN ... COMMIT` / `ROLLBACK` | Transaction: all or nothing |

Verified counts: products 50, variants 240, price_history 64, compatibility 137, stores 10, stock 2400.

**Not loaded yet, on purpose:** customers and staff (phase 2: contact fields need encryption, ADR-036), orders (phase 4), tickets (phase 5), knowledge documents (phase 3: parsed and embedded by the ingestion pipeline). Each later load: new Flyway migration -> `make migrate` -> manual SQL load.

### Database UI tools
| Tool | Use |
|---|---|
| pgAdmin | Official Postgres admin tool; deep tree (server > database > schema > table); good for running scripts |
| Beekeeper Studio | Data browser with a flat table list (like MongoDB Compass); good for looking at data |
| TablePlus, Postico, DBeaver | Alternatives |

Connection: host `localhost`, port `5432`, user `postgres`, password `postgres-local`, database `services`.

### Problems hit and fixes
| Problem | Cause | Fix |
|---|---|---|
| `pg_read_file` cannot find `/tmp/seed/...` | Container recreated, `/tmp` wiped | Run `docker cp` again |
| Copying long SQL from the terminal cut it off | Terminal scrolling/wrapping | Long text is provided as a file + clipboard (`pbcopy`) |
| `make data` shows 13 changed documents (PDF, DOCX, XLSX, PPTX, EML) although content is the same | Generators embed run-time values: email MIME boundaries are random, PDFs/Office files store creation time and IDs | Open: discard with `git checkout -- data/knowledge`; fix later by fixing those values in the generators. Seed data, catalog and evals are byte-identical |

### Commands
| Task | Command |
|---|---|
| Create the generator environment (uv, from tools/uv.lock, ADR-042) | `make data-tools` |
| Regenerate all data files | `make data` (needs `make data-tools` once) |
| Copy seed files into Postgres | `docker cp data/seed buywise-postgres-1:/tmp/seed` |
