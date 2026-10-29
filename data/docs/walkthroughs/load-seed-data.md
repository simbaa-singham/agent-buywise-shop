# Walkthrough: load the seed data by hand (one-time)

Loads the catalog and inventory data from `data/seed/` into the `services` database using plain SQL in `psql`. No script. Customers, orders and tickets are loaded in later phases, once their tables exist.

**Before you start:** the stack is running (`make up`) and the tables exist (`make migrate`).

## Step 1 - Copy the seed files into the Postgres container
Postgres can only read files that are inside its own container.
```bash
docker cp data/seed buywise-postgres-1:/tmp/seed
```

## Step 2 - Open psql on the `services` database
We connect as the `postgres` admin user because reading files from disk (`pg_read_file`) needs admin rights. The application itself will use the restricted `services` user.
```bash
docker exec -it buywise-postgres-1 psql -U postgres -d services
```
Everything below is typed at the `services=#` prompt.

## Step 3 - Start a transaction and empty the tables
A transaction means nothing is saved until you type `COMMIT;`. If anything looks wrong, type `ROLLBACK;` and nothing changes.
```sql
BEGIN;
TRUNCATE catalog.compatibility, catalog.price_history, catalog.variants, catalog.products,
         inventory.stock, inventory.stores;
```

## Step 4 - Create a helper view over the six product files
The products are split into six JSON files (phones, tablets, ...). This temporary view reads all six and returns one row per product, so the next steps can use `seed_products` like a table. It disappears when you close psql.
```sql
CREATE TEMP VIEW seed_products AS
SELECT p
FROM unnest(ARRAY['phones','tablets','laptops','watches','audio','accessories']) AS f,
     jsonb_array_elements(pg_read_file('/tmp/seed/catalog/' || f || '.json')::jsonb) AS p;

SELECT count(*) FROM seed_products;   -- expect 50
```
How it works: `pg_read_file` reads the file as text, `::jsonb` turns it into JSON, `jsonb_array_elements` turns the JSON array into one row per element.

## Step 5 - Stores (10 rows)
```sql
INSERT INTO inventory.stores
SELECT s->>'store_id', s->>'name', s->>'address', s->>'city', s->>'state', s->>'zip', s->>'timezone',
       (s->>'sales_tax_rate')::numeric, s->'hours', (s->>'same_day_radius_miles')::int
FROM jsonb_array_elements(pg_read_file('/tmp/seed/stores.json')::jsonb) AS s;
```
`->>` reads a field as text; `->` keeps it as JSON (used for `hours`, which is stored as JSON).

## Step 6 - Products (50 rows)
```sql
INSERT INTO catalog.products
  (product_id, brand_id, category, family, model, release_date, availability, specs,
   compatibility_tags, fits_tags, compatibility_note, specs_verified)
SELECT p->>'product_id', p->>'brand_id', p->>'category', p->>'family', p->>'model',
       (p->>'release_date')::date, p->>'availability', p->'specs',
       ARRAY(SELECT jsonb_array_elements_text(coalesce(p->'compatibility_tags', '[]'))),
       ARRAY(SELECT jsonb_array_elements_text(coalesce(p->'fits_tags', '[]'))),
       p->>'compatibility_note', (p->>'specs_verified')::date
FROM seed_products;
```
The tag lists are JSON arrays in the file and Postgres text arrays in the table; `ARRAY(SELECT jsonb_array_elements_text(...))` converts one to the other. Devices have `compatibility_tags`, accessories have `fits_tags`; `coalesce(..., '[]')` handles whichever is missing.

## Step 7 - Variants (240 rows)
Each product has a list of variants (storage x colour). The second `jsonb_array_elements` "unnests" that inner list.
```sql
INSERT INTO catalog.variants (sku, product_id, storage_gb, size, color, list_price, price_verified)
SELECT v->>'sku', p->>'product_id', (v->>'storage_gb')::int, v->>'size', v->>'color',
       (v->>'list_price')::numeric, (v->>'price_verified')::boolean
FROM seed_products, jsonb_array_elements(p->'variants') AS v;
```

## Step 8 - Price history (64 rows)
Only some variants changed price (on 2026-09-09 or 2026-06-25). "launch" in the file means "since launch", stored as NULL.
```sql
INSERT INTO catalog.price_history (sku, list_price, effective_from, effective_to)
SELECT v->>'sku', (h->>'list_price')::numeric,
       nullif(h->>'effective_from', 'launch')::date, (h->>'effective_to')::date
FROM seed_products,
     jsonb_array_elements(p->'variants') AS v,
     jsonb_array_elements(coalesce(v->'price_history', '[]')) AS h;
```

## Step 9 - Compatibility (137 rows)
```sql
INSERT INTO catalog.compatibility (accessory_id, device_id, compatible, note)
SELECT c->>'accessory_id', c->>'device_id', (c->>'compatible')::boolean, c->>'note'
FROM jsonb_array_elements(pg_read_file('/tmp/seed/catalog/compatibility.json')::jsonb) AS c;
```

## Step 10 - Stock (2,400 rows: 240 variants x 10 stores)
```sql
INSERT INTO inventory.stock (sku, store_id, quantity)
SELECT r->>'sku', r->>'store_id', (r->>'quantity')::int
FROM jsonb_array_elements(pg_read_file('/tmp/seed/stock.json')::jsonb) AS r;
```

## Step 11 - Check the counts, then save
```sql
SELECT 'products' AS tbl, count(*) FROM catalog.products UNION ALL
SELECT 'variants', count(*) FROM catalog.variants UNION ALL
SELECT 'price_history', count(*) FROM catalog.price_history UNION ALL
SELECT 'compatibility', count(*) FROM catalog.compatibility UNION ALL
SELECT 'stores', count(*) FROM inventory.stores UNION ALL
SELECT 'stock', count(*) FROM inventory.stock;
```
Expected: products 50, variants 240, price_history 64, compatibility 137, stores 10, stock 2400.

If the numbers match:
```sql
COMMIT;
```
If not: `ROLLBACK;` and tell Claude which step differed.

## Step 12 - Try a real question
"Is the iPhone 18 Pro (256 GB) in stock in Austin?" - the question phase 1 will answer through chat:
```sql
SELECT v.color, v.list_price, s.quantity
FROM catalog.variants v
JOIN inventory.stock s ON s.sku = v.sku
WHERE v.product_id = 'ph-18pro' AND v.storage_gb = 256 AND s.store_id = 'st-aus';
```
Type `\q` to leave psql.
