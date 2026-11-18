# buywise-db

Every script that creates or fills a database lives here, one folder per database (ADR-046).
Keycloak and LiteLLM create their own tables in their own databases; nothing for them here.

## Layout
| Folder | Database | What | Runs how |
|---|---|---|---|
| `cluster/01-databases.sh` | all | Creates the 4 databases (`services`, `agent`, `keycloak`, `litellm`), one user each, `REVOKE ... FROM PUBLIC`, pgvector in `agent` | Automatically, once, on the first Postgres start (compose mounts this folder) |
| `services/migrations/` | `services` | Schemas and tables: V1 catalog, V2 inventory, V3 availability rule, V4 customers + orders | `make migrate` (Flyway container) and on buywise-services start (Gradle packs them into the app) |
| `services/seed/` | `services` | 01 catalog, stores, stock; 02 customers, orders, sales tax - from `data/seed/*.json` | `make seed` (replaces existing seed rows) |
| `agent/migrations/` | `agent` | V1 `rag.chunks` + HNSW vector index | `make migrate` (Flyway container `flyway-agent`) |

## Run order on a fresh machine
```bash
make up        # 1. Postgres starts; cluster/01-databases.sh runs (first start only)
make migrate   # 2. tables in services and agent
make seed      # 3. seed data in services
make ingest    # 4. knowledge chunks in agent (buywise-agent reads docs, writes rag.chunks)
```
`make flyway-info` shows what is applied in both databases.

## Rules
- **Never edit an applied migration** - not even a comment: Flyway checks each file's checksum. A change is a new file (`V5__...sql`).
- Migration names: `V<number>__<description>.sql` (two underscores).
- No foreign keys or joins across schemas (ADR-010).
- Seed scripts are not migrations: they may change, and they `TRUNCATE` first (one transaction, all or nothing).
