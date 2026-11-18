-- catalog module: availability is the product's sale status only (ADR-043). Stock lives in inventory.
-- Preorder ship date is release_date. Existing free-text values ("preorder (...)") are normalized first
-- so the constraint can be added on databases that were already seeded.
UPDATE catalog.products SET availability = 'preorder' WHERE availability LIKE 'preorder%';

ALTER TABLE catalog.products
    ADD CONSTRAINT products_availability_check
    CHECK (availability IN ('available', 'preorder', 'discontinued'));
