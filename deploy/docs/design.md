# Deployment - Detailed Design

Part of [00_Architecture_Overview.md](../../docs/00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Principle
Production-grade design and configuration, run locally at small scale. Scale changes only through configuration (Helm values), never code.

**Scale-down rule (docs/00 section 7.1):** `values-local.yaml` holds the scale factor `S = 40` and the measured LLM hardware factor `k`. Local limits (replica concurrency caps, Envoy rate limits, agent admission queue, LLM timeouts, global USD budget) are derived from production values using `S` and `k`; `k` is measured by a benchmark script (production model tokens/s vs local model tokens/s) during setup.

## 2. Environments
| Environment | Runtime | Use |
|---|---|---|
| local-dev | Docker Compose, 1 instance each (includes LiteLLM) | Fast inner loop |
| local-k8s | kind cluster (1 control plane + 2 workers) | Production-shaped runs, load tests, failure demos |
| production (design only) | Managed Kubernetes | Documented sizing, not deployed |

## 3. Deployables and local replicas
| Deployable | local-k8s replicas | Production design |
|---|---|---|
| `buywise-web` | 2 (SSE served from conversation Redis Streams, no sticky sessions, ADR-029) | 3+, autoscaled |
| `buywise-services` | 2 | 3+, autoscaled |
| `buywise-agent` | 2 (stateless with Postgres checkpointer) | 3+, autoscaled |
| `buywise-mcp` | 2 (all domain servers in one Deployment) | 2+; optionally `order` as its own Deployment from the same image (ADR-031) |
| `buywise-event-publisher` | 1 | 2 |
| `buywise-event-consumers` | 1 | 2+ (per partitions) |

## 4. Platform components (local-k8s)
| Component | Local | Production design |
|---|---|---|
| Edge | Envoy Gateway (Gateway API) | Envoy Gateway, multiple replicas |
| Postgres | CloudNativePG, 1 cluster, 1 instance, hosting all databases (ADR-010) | Business cluster (primary + synchronous replica) and AI cluster (primary + read replica for RAG) |
| Connection pooling | Not needed (few connections) | PgBouncer via CloudNativePG `Pooler` in front of each cluster; apps connect to the pooler service, not to Postgres directly (design only) |
| Kafka | Strimzi, KRaft, 1 broker | 3 brokers |
| Redis | 1 | HA |
| Keycloak | 1 | HA |
| Observability | OTel Collector, Prometheus, Grafana, Tempo, Loki (logs) | Same + Langfuse, sized up |
| Backup storage | Not run locally (design only, ADR-035) | Object storage for CloudNativePG backups + WAL archive; immutable off-site copy |
| Model gateway | LiteLLM proxy, 1 replica; shadow price table; points at Ollama | LiteLLM, 2+ replicas; points at vLLM or hosted API |
| LLM | Ollama on the local machine (host GPU), reached only via LiteLLM | vLLM or hosted API |
| Service-to-service security | JWT | Service mesh (mTLS) - future option |

**Local Postgres data location (local-dev):** set `PG_DATA_DIR` in `deploy/compose/.env` to keep the data files in a host folder outside the repo (bind mount, e.g. `../buywise-data/postgres`); unset uses the Docker volume `pgdata`. Production keeps data on dedicated attached disks (PersistentVolumes / managed disks), never inside the container.

## 4a. Not run locally (local machine: 8 cores, 16 GB RAM) - production design only
| Item | Reason | Local impact |
|---|---|---|
| Postgres 2nd instance (synchronous replica) | Memory | No Postgres failover test; RPO 0 is design only. Restore test from MinIO backups still runs |
| Langfuse v3 (+ ClickHouse, Redis, object storage, web, worker) | ~3-5 GB memory | LLM traces via OTel -> Tempo; per-call data in `llm_calls` and AI Operations (ADR-027) |
| Service mesh (mTLS) | Memory; already a future option | JWT between services |
| External secrets manager (Vault + External Secrets) | Memory | Kubernetes secrets locally (deploy/docs/design.md open decision 1 still decides production) |
| Schema registry | Memory; event schema format still open | Revisit if the event format decision requires a registry |
| Database backups, WAL archive, PITR, restore drills (MinIO) | Production-scale operation (design only, ADR-035) | No local backups; local data is reproducible via `make seed` / `make ingest` |
| Disaster recovery environment, multi-zone | Production-scale operation (design only) | Single local cluster |
| GitHub Actions deploy to local-k8s (self-hosted runner) | Runner on the local machine costs memory and adds risk | CI builds/tests in GitHub; deploy to kind is a local script |

## 4b. Local usage model
- Not everything runs at once. Run only the subset needed for the task, e.g. UI work: `buywise-web` (Angular + BFF) plus what it calls; agent work: agent + MCP + LiteLLM + Ollama + Postgres.
- local-dev (Docker Compose, or apps run directly) and local-k8s (kind) are used at different times, never together.
- local-k8s is used for deployment, scaling and failure-scenario work; it runs the components that scenario needs.
- Local model stays `qwen2.5:7b` on Ollama.

## 5. Packaging
- One container image per deployable; one Helm chart per deployable.
- `values-local.yaml` (small) and `values-prod.yaml` (production sizing).

## 6. Production practices demonstrated
- Readiness/liveness probes, resource limits, graceful shutdown.
- Rolling deploys with zero downtime.
- Kill a pod during a k6 load test; no failed requests.
- PodDisruptionBudgets; HPA scaling 2 -> 3.

## 7. CI/CD
GitHub Actions: build, unit tests, contract tests, evals, image build, deploy to local-k8s - TBD.

## 8. Deployment steps
TBD.

## 9. Open decisions
1. Secrets management (Kubernetes secrets vs external secrets manager) - kept open by architect 2026-10-28; decide later. Locally: Kubernetes secrets.
2. ~~Local machine resources~~ - decided 2026-10-28: run task-based subsets, never the whole stack at once (section 4b); items in section 4a not run locally. Notes kept for reference: Langfuse v3 footprint (ClickHouse, Redis, object storage, web + worker; verify current requirements) - options: full stack in an opt-in observability profile, drop Langfuse (ADR-027 `llm_calls` + Grafana/Tempo), or a lighter tool (e.g. Arize Phoenix); and 2 Postgres instances for the failover test (docs/00 section 7.2 #6).
