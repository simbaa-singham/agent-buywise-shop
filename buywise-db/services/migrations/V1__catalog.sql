-- catalog module (ADR-014, ADR-010: schema per module, no cross-schema foreign keys)
CREATE SCHEMA IF NOT EXISTS catalog;

CREATE TABLE catalog.products (
    product_id         text PRIMARY KEY,
    brand_id           text        NOT NULL,          -- opaque id, never displayed (ADR-033)
    category           text        NOT NULL CHECK (category IN ('phone','tablet','laptop','watch','audio','accessory')),
    family             text        NOT NULL,
    model              text        NOT NULL,
    release_date       date,
    availability       text        NOT NULL DEFAULT 'available',
    specs              jsonb       NOT NULL DEFAULT '{}'::jsonb,
    compatibility_tags text[]      NOT NULL DEFAULT '{}', -- device side (e.g. usb-c, magsafe, case:ph-18pro)
    fits_tags          text[]      NOT NULL DEFAULT '{}', -- accessory side
    compatibility_note text,
    specs_verified     date        NOT NULL,
    image              text                              -- always NULL: placeholders only (ADR-033)
);

CREATE TABLE catalog.variants (
    sku            text PRIMARY KEY,
    product_id     text          NOT NULL REFERENCES catalog.products (product_id),
    storage_gb     integer,
    size           text,
    color          text          NOT NULL,
    list_price     numeric(10,2) NOT NULL CHECK (list_price > 0),
    price_verified boolean       NOT NULL
);
CREATE INDEX variants_product_idx ON catalog.variants (product_id);

-- Price at time of order is honored (pricing policy); history kept for older orders
CREATE TABLE catalog.price_history (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku            text          NOT NULL REFERENCES catalog.variants (sku),
    list_price     numeric(10,2) NOT NULL,
    effective_from date,                                 -- NULL = since launch
    effective_to   date                                  -- NULL = current
);
CREATE INDEX price_history_sku_idx ON catalog.price_history (sku);

CREATE TABLE catalog.compatibility (
    accessory_id text    NOT NULL REFERENCES catalog.products (product_id),
    device_id    text    NOT NULL REFERENCES catalog.products (product_id),
    compatible   boolean NOT NULL,
    note         text,
    PRIMARY KEY (accessory_id, device_id)
);
