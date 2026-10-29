# Phase 0 - Learning Notes

Revision notes for phase 0 (foundations), plus the design and data work that came before it.
Status: steps 1-4 done; steps 5-7 in progress (this document is updated as they finish).

---

## Part A - Before phase 0

### A1. Design (docs/00-08, ADR log)
- **What we build:** an AI shopping assistant for an electronics store (choose, order, track; staff can take over a chat).
- **Six deployables:** `buywise-web` (Angular + NestJS BFF), `buywise-services` (Spring Boot), `buywise-agent` (Python, LangGraph), `buywise-mcp` (tool servers), `buywise-event-publisher`, `buywise-event-consumers`.
- **ADRs (Architecture Decision Records):** every important choice is written down with context, options, decision and consequences (`docs/adr/ADR_Log.md`). Purpose: anyone can later see *why*, not just *what*.
- **NFRs (non-functional requirements):** targets for how well the system works (latency, availability, scale, security). Production targets are ideal; local targets scale down: volumes / S (S = 40), AI speed x k (k = measured).
- **Design-only vs implemented locally (docs/00 7.4):** backups, DR, replicas, service mesh, connection pooling are explained but not built locally; all code-level techniques are built.
- **Roadmap:** 9 phases (docs/09); thin end-to-end slice first.

**Concept - design before code:** decisions made one at a time with trade-offs are cheaper to change on paper than in code.

### A2. Data (data/, ADR-033)
- **Catalog:** 50 real products (real names, specs, list prices, verified by web search); maker never named (`brand_id` only); unverified tier prices flagged `price_verified: false`; no images.
- **Synthetic people:** 500 customers, 2,000 orders, 100 tickets, 10 stores - Faker with a fixed random seed (same data every run); emails `@example.com`, phones `555-01xx` (reserved, can never reach a real person).
- **Knowledge documents:** 103 files in 11 formats (DOCX, digital PDF, scanned PDF/PNG, HTML, XLSX, CSV, PPTX, EML with attachment, Markdown, TXT) for practising document parsing in phase 3.
- **Eval sets:** RAG questions, router messages, prompt-injection attacks, planted-price checks.

**Concept - designed test data:** good test data contains edge cases on purpose (out of stock, delayed orders, Alaska/Hawaii, two versions of a policy, planted prices that must be stripped).

---

## Part B - Phase 0 (foundations)

Phase 0 builds nothing a customer sees. It prepares what the first chat (phase 1) needs: a database with products and stock, a login server, a gateway to the AI model, and an agreed message format.

### Step 1 - Supporting programs in Docker

**Docker concepts**
| Term | Meaning |
|---|---|
| **Image** | A ready-made package (OS + program), downloaded from a registry, e.g. `pgvector/pgvector:pg17` from Docker Hub |
| **Container** | A running copy of an image, isolated from your Mac, e.g. `buywise-postgres-1` |
| **Registry** | Where images are published: Docker Hub, `quay.io` (Keycloak), `ghcr.io` (GitHub, LiteLLM) |
| **Volume** | Where a container keeps data that must survive the container being removed |
| **Bind mount** | A folder on your Mac connected into a container |
| **Port mapping** | `"5432:5432"` = Mac port : container port, so `localhost:5432` reaches the container |
| **Docker Compose** | Runs several containers together from one file (`compose.yaml`) |

On a Mac, Docker Desktop runs a small Linux virtual machine; all images, containers and volumes live in one large virtual-disk file. Nothing (Postgres, Redis, ...) is installed on the Mac itself.

**The four programs**
| Program | What it is | Our use | Port |
|---|---|---|---|
| **Postgres 17 + pgvector** | Relational database; pgvector adds vector search | Products, stock, later orders, chats, document vectors | 5432 |
| **Redis 7.4** | In-memory key-value server (C, created by Salvatore Sanfilippo, 2009). A server, not a library; each language has a client library (redis-py, ioredis) | Login sessions (keys with expiry), live chat streams (`XADD`/`XRANGE`), counters, rate limits | 6379 |
| **Keycloak 26** | Open-source login server (Red Hat, now CNCF), standards OpenID Connect + OAuth 2.0 | Logins, roles, tokens (JWTs), token exchange; our code never sees passwords | 8080 (9000 = health) |
| **LiteLLM** | AI gateway (BerriAI); one OpenAI-style API in front of many model providers | Model aliases (`buywise-primary`, `buywise-economy`, `bge-m3`), shadow cost per call, budgets, logs | 4000 |

**Ollama** (the AI model runtime) runs directly on the Mac, not in Docker, so it can use the Mac's GPU. LiteLLM reaches it at `host.docker.internal:11434` ("the Mac I'm running on").

**Keycloak vocabulary:** realm (separate space of users/settings: `buywise`), client (an application allowed to use Keycloak), role (permission label: `customer`, `staff`, `staff_lead`, `ops-admin`), token (signed pass, a JWT). Defined as code in `deploy/compose/keycloak/buywise-realm.json`.

**Redis licence note:** BSD until 2024, then source-available (7.4 is under it), Redis 8 added AGPLv3. Valkey (Linux Foundation) is the fully open-source fork and a drop-in replacement.

**compose.yaml keywords**
| Keyword | Meaning |
|---|---|
| `image` | Which package to run |
| `command` | How to start it |
| `environment` | Settings passed in; `${NAME}` is replaced from `.env` |
| `ports` | Mac port : container port |
| `volumes` | Mac path : container path; `:ro` = read-only |
| `healthcheck` | How Docker knows the program is *ready*, not just started |
| `depends_on` | Start order, e.g. wait until Postgres is healthy |
| `profiles` | Service starts only when asked (Flyway: `tools`) |
| `extra_hosts` | Extra hostnames, e.g. `host.docker.internal` |

**compose.yaml vs .env**
| File | Holds | In Git? |
|---|---|---|
| `compose.yaml` | What runs and how it connects (same for everyone) | Yes |
| `.env` | Passwords, keys, machine-specific paths | Never (`.gitignore`) |
| `.env.example` | Template for `.env` with harmless local defaults | Yes |
Principle (Twelve-Factor App): keep config and secrets out of code. Anything committed stays in Git history forever.

**Postgres data location:** `PG_DATA_DIR` in `.env` puts the data files in `/Users/sachin/AI/Production/buywise-data/postgres` (bind mount, outside the repo). The program stays in the container; the data is on a disk you choose. Rules: never edit that folder while Postgres runs; exclude it from Time Machine.

**Health checks:** Postgres `pg_isready`, Redis `redis-cli ping`, Keycloak raw HTTP request (bash `/dev/tcp`) to `/health/ready` on port 9000 (image has no curl), LiteLLM Python call to `/health/liveliness`. Without a health check, Docker reports "healthy" as soon as the process starts.

**make:** a standard tool (`/usr/bin/make`) that runs named command shortcuts from `Makefile`. `make -n <target>` prints the commands without running them; `make help` lists targets.

### Step 2 - Separate databases
- One database and one user per part of the system: `services`, `agent`, `keycloak`, `litellm`.
- Created once by `deploy/compose/postgres/init/01-databases.sh` (runs only on the first start with an empty data folder): `CREATE USER`, `CREATE DATABASE ... OWNER`, `REVOKE ALL ... FROM PUBLIC`; pgvector enabled only in `agent`.
- Isolation test: user `agent` connecting to `services` gets `permission denied ... does not have CONNECT privilege`.
- Why: a bug or attack in one part cannot touch another's data; in production the databases split across a business cluster and an AI cluster by changing connection strings only (ADR-010).

### Step 3 - Tables with Flyway
- **Flyway** (Redgate; open-source Community edition) applies numbered SQL files ("migrations") in order: `V1__catalog.sql`, `V2__inventory.sql` (`V<version>__<description>.sql`, two underscores).
- It records applied files in `flyway.flyway_schema_history` with a checksum; re-running applies only new files ("Schema is up to date").
- **Never edit an applied migration** - Flyway refuses (checksum mismatch). Changes go in a new file (V3, V4, ...).
- `flyway info` = report only (Pending / Success); `flyway migrate` = apply.
- **Schema** = a folder of tables inside a database. One schema per business module (`catalog`, `inventory`); no foreign keys across schemas (that is why `inventory.stock.sku` does not reference `catalog.variants`).
- Same SQL files will be used by Spring Boot from phase 1.

Tables created:
| Schema | Tables |
|---|---|
| catalog | products, variants, price_history, compatibility |
| inventory | stores, stock |

### Step 4 - Loading data by hand
- Copied the JSON files into the container (`docker cp data/seed buywise-postgres-1:/tmp/seed`) - Postgres can only read files inside its container; `/tmp` is wiped when the container is recreated.
- Ran `docs/walkthroughs/load-seed-data.sql` in pgAdmin's Query Tool as `postgres` (reading files needs admin rights).
- SQL techniques: `pg_read_file()` reads a file as text; `::jsonb` converts to JSON; `jsonb_array_elements()` turns an array into rows; `->>` reads a field as text, `->` keeps JSON; a temporary view (`seed_products`) combines six files.
- **Transaction:** `BEGIN ... COMMIT` = all or nothing; on error, `ROLLBACK`.
- Verified counts: products 50, variants 240, price_history 64, compatibility 137, stores 10, stock 2400.
- Not loaded yet on purpose: customers (phase 2, needs field encryption), orders (phase 4), tickets (phase 5), knowledge documents (phase 3, need parsing and embedding).

**Database UI tools:** pgAdmin = official Postgres admin tool (deep tree: server > database > schema > table). Beekeeper Studio = data browser with a flat table list (like MongoDB Compass). Postgres has three levels (database > schema > table) where MongoDB has two (database > collection).

### Step 5 - Chat message contract (in progress)
- One definition in **JSON Schema**: `ui/web/projects/shared/contracts/schemas/chat-events.schema.json`.
- Code is generated from it for both sides: TypeScript for the website, Python (Pydantic) for the agent; nobody edits generated files.
- Every message has `v` (version), `type`, `ts`, `conversationId`, `messageId`, and a type-specific `payload`.
- 13 message types (status updates, reply pieces, completion, failure, product card, staff handoff, tickets, order status, metrics) plus `SendMessageRequest` from the browser with `clientMessageId` (duplicates ignored).
- JSON Schema keywords: `type`, `const`, `required`, `enum`, `additionalProperties: false` (rejects unknown fields and typos).
- _To be completed: 5.2 generated code, 5.3 contract tests._

### Step 6 - Measuring AI speed (k) - _to be completed_
Measured: 16.9 tokens/s locally vs 50 tokens/s production target -> k = 2.96 (`deploy/local/scale.yaml`).

### Step 7 - Glue: Makefile, CI, README - _to be completed_

---

## Part C - Questions asked and answers

| Question | Answer in short |
|---|---|
| Where is Postgres installed? | Nowhere on the Mac: Docker downloaded the `pgvector/pgvector:pg17` image; it runs as a container. |
| Why run the database in Docker? | Same version everywhere (Mac, CI, Kubernetes), isolated from other projects, one-file setup, easy reset, production-like. Costs: Docker must run, slightly slower disk on Mac. |
| What if the data is 100 GB? | Works locally but slower and risky on a laptop. In production the container is only the program; data lives on attached cloud disks (PersistentVolumes) or a managed database service. Our data is about 40 MB. |
| How does production run Postgres? | CloudNativePG on Kubernetes: primary + replicas in pods, data on cloud SSDs, business and AI clusters, apps connect by service name (`business-rw`), PgBouncer pooling, backups to object storage, monitoring, rolling minor upgrades (design only locally). Alternatives: managed services, or VMs. |
| Can Postgres run in Docker with data in my own folder? | Yes - bind mount via `PG_DATA_DIR` (done). No Postgres installation needed. |
| What are `make up` / `make down`? | Shortcuts in `Makefile` for long `docker compose` commands. |
| Is Redis a Python library? | No - a server program; Python/Node use client libraries to talk to it. |
| Is there a Compass-like tool for Postgres? | pgAdmin (official), Beekeeper Studio, TablePlus, Postico, DBeaver. |

---

## Part D - Command cheat sheet

| Task | Command |
|---|---|
| Start everything | `make up` |
| Stop everything (keeps data) | `make down` |
| Status / logs | `make ps` / `make logs` |
| See what a make target runs | `make -n up` |
| Create tables | `make migrate` |
| Flyway report only | `docker compose -f deploy/compose/compose.yaml --env-file deploy/compose/.env run --rm flyway info` |
| Copy seed files into Postgres | `docker cp data/seed buywise-postgres-1:/tmp/seed` |
| psql as admin | `docker exec -it buywise-postgres-1 psql -U postgres -d services` |
| Redis CLI | `docker exec -it buywise-redis-1 redis-cli` |
| Keycloak admin | http://localhost:8080 (admin / admin-local) |
| Keycloak realm info | http://localhost:8080/realms/buywise/.well-known/openid-configuration |
| LiteLLM health / admin UI | http://localhost:4000/health/liveliness, http://localhost:4000/ui (key `sk-buywise-local`) |
| Ask the model via LiteLLM | `curl localhost:4000/v1/chat/completions -H "Authorization: Bearer sk-buywise-local" ...` |
| Regenerate contract code | `make contracts` |
| Run tests | `make test` |

## Part E - Files created in phase 0

| File | Purpose |
|---|---|
| `deploy/compose/compose.yaml` | The local stack |
| `deploy/compose/.env.example` / `.env` | Settings template / your local secrets |
| `deploy/compose/postgres/init/01-databases.sh` | Creates the 4 databases and users |
| `deploy/compose/keycloak/buywise-realm.json` | Realm, roles, clients as code |
| `deploy/compose/litellm/config.yaml` | Model aliases and placeholder shadow prices |
| `services/src/main/resources/db/migration/V1__catalog.sql`, `V2__inventory.sql` | Tables |
| `docs/walkthroughs/load-seed-data.md` / `.sql` | Manual data load (explained / one file) |
| `ui/web/projects/shared/contracts/` | Chat contract: schema, examples, generated TypeScript |
| `agent/buywise_agent/contracts/chat_contract.py` | Generated Python models |
| `agent/tests/contract/test_chat_contract.py` | Contract tests |
| `deploy/scripts/benchmark_k.py` | Measures k |
| `Makefile`, `.github/workflows/ci.yml`, `.editorconfig`, `README.md` | Glue |

## Part F - Problems hit and fixes

| Problem | Cause | Fix |
|---|---|---|
| Postgres container exited (126) on first start | Init script not executable | `chmod +x`, reset the fresh volume |
| `make up` said Keycloak "Healthy" while it was still booting | No health check defined | Added real health checks for Keycloak and LiteLLM |
| `pg_read_file` cannot find `/tmp/seed/...` | Container recreated, `/tmp` wiped | Run `docker cp` again |
| Copying long text from the terminal cuts it off | Terminal scrolling and wrapping | Long text is given as a file + clipboard (`pbcopy`) |
| Generated TypeScript lost event fields | Schema used `allOf` composition | Flattened common fields into each event |
