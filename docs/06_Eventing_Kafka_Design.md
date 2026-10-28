# Eventing (Kafka) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose
Decouple services and drive asynchronous reactions (notifications, RAG freshness, staff console updates).

## 2. Topics (initial)
| Topic | Producer | Consumers |
|---|---|---|
| `order-events` | order-service | notifications, helpdesk, analytics |
| `inventory-events` | inventory-service | catalog/availability views |
| `catalog-events` | catalog-service | RAG indexer |
| `conversation-events` | agent / helpdesk | staff console, analytics |

## 3. Patterns
- Transactional outbox in each producing service.
- Idempotent consumers (event id + processed-events table).
- Keys by aggregate id (order_id, variant_id) for ordering.

## 4. Open decisions
1. Event schema format: JSON Schema vs Avro + schema registry.
2. Partitions, retention, dead-letter topics.
