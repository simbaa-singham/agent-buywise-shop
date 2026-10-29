# services - Learning Notes

What the services module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### Flyway - creating tables in a controlled way (step 3)
- **Flyway** (Redgate; open-source Community edition) applies numbered SQL files ("migrations") in order: `src/main/resources/db/migration/V1__catalog.sql`, `V2__inventory.sql`. Name format: `V<version>__<description>.sql` (two underscores).
- It records applied files in `flyway.flyway_schema_history` with a **checksum** (fingerprint); re-running applies only new files ("Schema is up to date").
- **Never edit an applied migration** - Flyway refuses on checksum mismatch. Changes go in a new file (V3, V4, ...). "Undo" migrations are a paid feature; fixes are always new forward migrations.
- `flyway info` = report only (Pending / Success); `flyway migrate` = apply.
- Locally Flyway runs as a one-off container (`profiles: ["tools"]` in the deploy compose file); from phase 1 Spring Boot runs the **same files** on startup.
- Alternatives: Liquibase (Java), Alembic (Python/SQLAlchemy), Prisma Migrate and Atlas (Node / schema-as-code).

### Schemas
- A **schema** is a folder of tables inside a database. One schema per business module: `catalog`, `inventory` (later `customer`, `order`, `helpdesk`).
- **No foreign keys across schemas** (ADR-010): modules stay independent. That is why `inventory.stock.sku` does not reference `catalog.variants`.
- Postgres has three levels (database > schema > table); MongoDB has two (database > collection).

### Tables created
| Schema | Table | Holds |
|---|---|---|
| catalog | products | Each model (specs as JSON, compatibility tags, `brand_id`, no image) |
| catalog | variants | Storage x colour, list price, `price_verified` |
| catalog | price_history | Earlier prices (price at time of order is honored) |
| catalog | compatibility | Which accessory fits which device |
| inventory | stores | The 10 stores (address, tax rate, hours) |
| inventory | stock | Quantity per variant per store |

Table rules seen in SQL: `PRIMARY KEY`, `REFERENCES` (foreign key within a schema), `CHECK (list_price > 0)`, `NOT NULL`, `DEFAULT`, `jsonb` (JSON column), `text[]` (array column), identity column for `price_history.id`.

### Commands
| Task | Command |
|---|---|
| Apply migrations | `make migrate` |
| Applied / pending report | `make flyway-info` |
