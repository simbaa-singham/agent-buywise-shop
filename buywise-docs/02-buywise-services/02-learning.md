# buywise-services - Learning Notes

What the buywise-services module taught us, phase by phase. Index of all phases: [buywise-docs/11-learning/01-phase-0-foundations.md](../11-learning/01-phase-0-foundations.md).

---

## Phase 0

### Flyway - creating tables in a controlled way (step 3)
- **Flyway** (Redgate; open-source Community edition) applies numbered SQL files ("migrations") in order: `buywise-db/services/01-ddl/V1__catalog.sql` (moved from `src/main/resources/db/migration/` on 2026-11-18, ADR-046), `V2__inventory.sql`. Name format: `V<version>__<description>.sql` (two underscores).
- It records applied files in `flyway.flyway_schema_history` with a **checksum** (fingerprint); re-running applies only new files ("Schema is up to date").
- **Never edit an applied migration** - Flyway refuses on checksum mismatch. Changes go in a new file (V3, V4, ...). "Undo" migrations are a paid feature; fixes are always new forward migrations.
- `flyway info` = report only (Pending / Success); `flyway migrate` = apply.
- Locally Flyway runs as a one-off container (`profiles: ["tools"]` in the deploy compose file); from phase 1 Spring Boot runs the **same files** on startup.
- Alternatives: Liquibase (Java), Alembic (Python/SQLAlchemy), Prisma Migrate and Atlas (Node / schema-as-code).

### Schemas
- A **schema** is a folder of tables inside a database. One schema per business module: `catalog`, `inventory`, `customers`, `orders` (later `helpdesk`).
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

## Phase M step 4b - Spring Security resource server (2026-11-25, ADR-050)
- **Starter:** `spring-boot-starter-security-oauth2-resource-server` (Spring Boot 4 name; the old `spring-boot-starter-oauth2-resource-server` still exists).
- **`shared/SecurityConfig`:** `NimbusJwtDecoder` with Keycloak's key URL (`buywise.security.jwks-uri`, or issuer + `/protocol/openid-connect/certs`) and validators for issuer (`buywise.security.issuer`) + audience `buywise-services`. Authorities: scopes -> `SCOPE_x`, Keycloak `realm_access.roles` -> `ROLE_x`. Rules: health open; products `SCOPE_catalog:read`; stores/stock `SCOPE_inventory:read`; order reads and quote `SCOPE_orders:read` + `ROLE_customer`; place/cancel `SCOPE_orders:write` + `ROLE_customer`; `/api/customers/me` `ROLE_customer`; everything else denied. Stateless, no CSRF (no cookies).
- **`shared/CurrentCustomer`:** the customer is the token's `customer_id` claim (403 if missing) - controllers take `@AuthenticationPrincipal Jwt`, the `X-Customer-Id` header is gone.
- **Customers API:** `/api/customers/{id}` and `?email=` (any caller could read any customer) replaced by `/api/customers/me`.
- **`shared/AuditFilter`:** one JSON line per `/api/` request to logger `buywise.audit`: method, path, status, sub, customer_id, azp.
- **Two URLs for Keycloak:** the issuer is what tokens name (public URL); keys can be fetched from another address (inside Docker, `http://keycloak:8080/...`). Same split in production (internal key fetch, public issuer).
