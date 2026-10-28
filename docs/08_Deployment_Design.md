# Deployment - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Environments
local (Docker Compose) -> dev -> staging -> prod (Kubernetes) - TBD.

## 2. Packaging
One container image per deployable (web, bff, gateway, each service, agent, rag-indexer).

## 3. Runtime
- Local: Docker Compose (Postgres, Redis, Kafka, Keycloak, Ollama + all modules).
- Prod: Kubernetes + Helm; health checks, autoscaling, secrets.

## 4. CI/CD
GitHub Actions: build, unit tests, contract tests, evals, image build, deploy - TBD.

## 5. Deployment steps
TBD.

## 6. Open decisions
1. Target platform (local K8s vs managed cloud).
2. Secrets management.
