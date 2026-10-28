# Deployment - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Principle
Production-grade design and configuration, run locally at small scale. Scale changes only through configuration (Helm values), never code.

## 2. Environments
| Environment | Runtime | Use |
|---|---|---|
| local-dev | Docker Compose, 1 instance each | Fast inner loop |
| local-k8s | kind cluster (1 control plane + 2 workers) | Production-shaped runs, load tests, failure demos |
| production (design only) | Managed Kubernetes | Documented sizing, not deployed |

## 3. Deployables and local replicas
| Deployable | local-k8s replicas | Production design |
|---|---|---|
| `buywise-web` | 2 (SSE streams + Redis pub/sub across pods, no sticky sessions) | 3+, autoscaled |
| `buywise-services` | 2 | 3+, autoscaled |
| `buywise-agent` | 2 (stateless with Postgres checkpointer) | 3+, autoscaled |
| `buywise-mcp` | 2 | 2+ |
| `buywise-event-publisher` | 1 | 2 |
| `buywise-event-consumers` | 1 | 2+ (per partitions) |

## 4. Platform components (local-k8s)
| Component | Local | Production design |
|---|---|---|
| Edge | Envoy Gateway (Gateway API) | Envoy Gateway, multiple replicas |
| Postgres | CloudNativePG, 1 instance | Primary + replica |
| Kafka | Strimzi, KRaft, 1 broker | 3 brokers |
| Redis | 1 | HA |
| Keycloak | 1 | HA |
| Observability | OTel Collector, Prometheus, Grafana, Tempo, Langfuse | Same, sized up |
| LLM | Ollama on the Mac host (Apple GPU) | Model gateway -> vLLM or hosted API |
| Service-to-service security | JWT | Service mesh (mTLS) - future option |

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
1. Secrets management (Kubernetes secrets vs external secrets manager).
2. Mac resources for the full local-k8s profile.
