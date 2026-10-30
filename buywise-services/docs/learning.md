# buywise-services - Learning Notes

What the buywise-services module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

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

**V3 - changing a table that already has data (2026-10-30, ADR-043).** `catalog.products.availability` was free text; V3 limits it to `available | preorder | discontinued`. Applied migrations are never edited (Flyway checks a checksum of each applied file and would refuse to run); a change is always a new file. V3 first `UPDATE`s existing rows (the free-text `preorder (...)` value) so the new `CHECK` constraint can be added on an already-seeded database; on a fresh database the `UPDATE` touches nothing. Test: setting `availability = 'availble'` now fails with `violates check constraint "products_availability_check"`.

### Commands
| Task | Command |
|---|---|
| Apply migrations | `make migrate` |
| Applied / pending report | `make flyway-info` |

## Local end-to-end build (2026-10-30)
- **What:** one Spring Boot 4.1 app, one package per module (`catalog`, `inventory`, `customers`, `orders`); `ModularityTest` fails the build if a module reaches into another's internals (Spring Modulith).
- **Data access:** `JdbcClient` mapping rows straight into Java records (no JPA) - small, explicit SQL.
- **Orders:** prices always from the catalog; pickup takes stock off the shelf (`UPDATE ... WHERE quantity >= ?`), cancel puts it back; `POST /api/orders/quote` prices without saving.
- **Who is asking:** `X-Customer-Id` header; an order of another customer answers 404 (no hint it exists).
- **Build:** Gradle Kotlin DSL + version catalog (ADR-041); `make -C buywise-services build` / `run`.
- **Try:** `curl "localhost:8081/api/products?q=iphone+18+pro"`, `curl -H 'X-Customer-Id: cu-demo' localhost:8081/api/orders`.
