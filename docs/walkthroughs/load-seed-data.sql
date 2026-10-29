-- One-time manual load of catalog + inventory seed data into the services database.
-- Explained step by step in docs/walkthroughs/load-seed-data.md.
-- Before running: docker cp data/seed buywise-postgres-1:/tmp/seed
-- Run in pgAdmin Query Tool on the "services" database as user postgres (F5 runs the whole file).
-- Everything runs in one transaction: if any statement fails, nothing is saved (then run ROLLBACK;).
BEGIN;

TRUNCATE catalog.compatibility, catalog.price_history, catalog.variants, catalog.products,
         inventory.stock, inventory.stores;

CREATE TEMP VIEW seed_products AS
SELECT p
FROM unnest(ARRAY['phones','tablets','laptops','watches','audio','accessories']) AS f,
     jsonb_array_elements(pg_read_file('/tmp/seed/catalog/' || f || '.json')::jsonb) AS p;

-- Stores (10)
INSERT INTO inventory.stores
SELECT s->>'store_id', s->>'name', s->>'address', s->>'city', s->>'state', s->>'zip', s->>'timezone',
       (s->>'sales_tax_rate')::numeric, s->'hours', (s->>'same_day_radius_miles')::int
FROM jsonb_array_elements(pg_read_file('/tmp/seed/stores.json')::jsonb) AS s;

-- Products (50)
INSERT INTO catalog.products
  (product_id, brand_id, category, family, model, release_date, availability, specs,
   compatibility_tags, fits_tags, compatibility_note, specs_verified)
SELECT p->>'product_id', p->>'brand_id', p->>'category', p->>'family', p->>'model',
       (p->>'release_date')::date, p->>'availability', p->'specs',
       ARRAY(SELECT jsonb_array_elements_text(coalesce(p->'compatibility_tags', '[]'))),
       ARRAY(SELECT jsonb_array_elements_text(coalesce(p->'fits_tags', '[]'))),
       p->>'compatibility_note', (p->>'specs_verified')::date
FROM seed_products;

-- Variants (240)
INSERT INTO catalog.variants (sku, product_id, storage_gb, size, color, list_price, price_verified)
SELECT v->>'sku', p->>'product_id', (v->>'storage_gb')::int, v->>'size', v->>'color',
       (v->>'list_price')::numeric, (v->>'price_verified')::boolean
FROM seed_products, jsonb_array_elements(p->'variants') AS v;

-- Price history (64)
INSERT INTO catalog.price_history (sku, list_price, effective_from, effective_to)
SELECT v->>'sku', (h->>'list_price')::numeric,
       nullif(h->>'effective_from', 'launch')::date, (h->>'effective_to')::date
FROM seed_products,
     jsonb_array_elements(p->'variants') AS v,
     jsonb_array_elements(coalesce(v->'price_history', '[]')) AS h;

-- Compatibility (137)
INSERT INTO catalog.compatibility (accessory_id, device_id, compatible, note)
SELECT c->>'accessory_id', c->>'device_id', (c->>'compatible')::boolean, c->>'note'
FROM jsonb_array_elements(pg_read_file('/tmp/seed/catalog/compatibility.json')::jsonb) AS c;

-- Stock (2400 = 240 variants x 10 stores)
INSERT INTO inventory.stock (sku, store_id, quantity)
SELECT r->>'sku', r->>'store_id', (r->>'quantity')::int
FROM jsonb_array_elements(pg_read_file('/tmp/seed/stock.json')::jsonb) AS r;

COMMIT;

-- Check: expect products 50, variants 240, price_history 64, compatibility 137, stores 10, stock 2400
SELECT 'products' AS tbl, count(*) FROM catalog.products UNION ALL
SELECT 'variants', count(*) FROM catalog.variants UNION ALL
SELECT 'price_history', count(*) FROM catalog.price_history UNION ALL
SELECT 'compatibility', count(*) FROM catalog.compatibility UNION ALL
SELECT 'stores', count(*) FROM inventory.stores UNION ALL
SELECT 'stock', count(*) FROM inventory.stock;
