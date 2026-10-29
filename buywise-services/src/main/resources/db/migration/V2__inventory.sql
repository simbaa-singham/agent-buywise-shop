-- inventory module (ADR-014, ADR-010). Stores live here: they are stock locations.
-- stock.sku deliberately has no foreign key to catalog.variants: no cross-schema foreign keys.
CREATE SCHEMA IF NOT EXISTS inventory;

CREATE TABLE inventory.stores (
    store_id              text PRIMARY KEY,
    name                  text         NOT NULL,
    address               text         NOT NULL,
    city                  text         NOT NULL,
    state                 char(2)      NOT NULL,
    zip                   text         NOT NULL,
    timezone              text         NOT NULL,
    sales_tax_rate        numeric(6,5) NOT NULL,
    hours                 jsonb        NOT NULL,
    same_day_radius_miles integer      NOT NULL
);

CREATE TABLE inventory.stock (
    sku      text    NOT NULL,
    store_id text    NOT NULL REFERENCES inventory.stores (store_id),
    quantity integer NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (sku, store_id)
);
CREATE INDEX stock_store_idx ON inventory.stock (store_id);
