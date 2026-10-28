# Data and Databases - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose
Data ownership, storage choices and data model.

## 2. Stores
| Store | Use |
|---|---|
| PostgreSQL | Business data (schema per service), conversations, agent checkpoints, vectors (pgvector) |
| Redis | Semantic cache, rate limits, OTP codes |
| Kafka | Event log (see 06) |

## 3. Data ownership
Each service owns its schema; no cross-service joins; other services read via API or events.

## 4. Data model (initial)
- customer: `customers`
- catalog: `products`, `variants`, `compatibility`
- inventory: `inventory`, `reservations`
- order: `carts`, `cart_items`, `orders`, `order_items`, `shipments`, `pickups`
- helpdesk: `tickets`
- agent: `conversations`, `messages`, checkpoints
- knowledge: `documents`, `chunks` (with embeddings)

## 5. Open decisions
1. Schema per service vs database per service.
2. Backup, retention and PII policy.
