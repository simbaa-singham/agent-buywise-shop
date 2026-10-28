# Eventing (Kafka) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Decouple side effects from business transactions (notifications, staff console updates, projections, RAG freshness).

## 2. Deployables
| Deployable | Role |
|---|---|
| `buywise-event-publisher` | Publishes committed business events from `buywise-services` to Kafka |
| `buywise-event-consumers` | Consumes events and performs async reactions; calls `buywise-services` REST when business data must change |

## 3. Topics (initial)
| Topic | Source | Consumers |
|---|---|---|
| `order-events` | order module | notifications, staff console, audit |
| `inventory-events` | inventory module | projections |
| `catalog-events` | catalog module | RAG re-indexing |
| `payment-events` | payment module | order status update |
| `conversation-events` | agent / helpdesk | staff console, analytics |

## 4. Patterns
- Events recorded in the same DB transaction as the state change (Spring Modulith Event Publication Registry / outbox).
- Idempotent consumers (event id + processed-events table).
- Keys by aggregate id (order_id, variant_id) for ordering.
- Consumer groups spread partitions across replicas.

## 5. Deferred decisions (decide at implementation)
1. Publishing mechanism: polling outbox relay vs Debezium CDC.
2. RAG re-indexing location: agent vs event consumers.

## 6. Open decisions
1. Event schema format: JSON Schema vs Avro + schema registry.
2. Partitions, retention, dead-letter topics.
