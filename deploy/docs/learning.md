# deploy - Learning Notes

What the deploy module taught us, phase by phase. Index of all phases: [docs/learning/Phase-0.md](../../docs/learning/Phase-0.md).

---

## Phase 0

### Docker concepts
| Term | Meaning |
|---|---|
| **Image** | A ready-made package (OS + program), downloaded from a registry, e.g. `pgvector/pgvector:pg17` from Docker Hub |
| **Container** | A running copy of an image, isolated from your Mac, e.g. `buywise-postgres-1` |
| **Registry** | Where images are published: Docker Hub, `quay.io` (Keycloak), `ghcr.io` (GitHub, LiteLLM) |
| **Volume** | Where a container keeps data that must survive the container being removed |
| **Bind mount** | A folder on your Mac connected into a container |
| **Port mapping** | `"5432:5432"` = Mac port : container port, so `localhost:5432` reaches the container |
| **Docker Compose** | Runs several containers together from one file (`compose/compose.yaml`) |

On a Mac, Docker Desktop runs a small Linux virtual machine; images, containers and volumes live in one large virtual-disk file (`~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`). Nothing (Postgres, Redis, ...) is installed on the Mac itself. Ollama is the exception: it runs on the Mac so it can use the GPU.

### The four supporting programs
| Program | What it is | Our use | Port |
|---|---|---|---|
| **Postgres 17 + pgvector** | Relational database; pgvector adds vector search | Products, stock, later orders, chats, document vectors | 5432 |
| **Redis 7.4** | In-memory key-value **server** (C; Salvatore Sanfilippo, 2009). Not a library: each language uses a client library (redis-py, ioredis) | Login sessions (keys with expiry), live chat streams (`XADD`/`XRANGE`), counters, rate limits | 6379 |
| **Keycloak 26** | Open-source login server (Red Hat, now CNCF); standards OpenID Connect + OAuth 2.0 | Logins, roles, tokens (JWTs), token exchange; our code never sees passwords | 8080 (9000 = health) |
| **LiteLLM** | AI gateway (BerriAI); one OpenAI-style API in front of many model providers | Model aliases (`buywise-primary`, `buywise-economy`, `bge-m3`), shadow cost per call, budgets, logs | 4000 |

- **Keycloak vocabulary:** realm (separate space of users/settings: `buywise`), client (an application allowed to use Keycloak), role (`customer`, `staff`, `staff_lead`, `ops-admin`), token (signed pass, a JWT). Defined as code in `compose/keycloak/buywise-realm.json`.
- **LiteLLM:** code always sends the OpenAI request format; LiteLLM translates for the real model (Ollama locally, hosted or vLLM in production). Changing model = config change in `compose/litellm/config.yaml`.
- **Redis licence:** BSD until 2024, then source-available (7.4), Redis 8 added AGPLv3. Valkey (Linux Foundation) is the fully open-source drop-in fork.
- **Ollama** is reached from containers at `host.docker.internal:11434` ("the Mac I'm running on").

### compose.yaml keywords
| Keyword | Meaning |
|---|---|
| `image` | Which package to run |
| `command` | How to start it |
| `environment` | Settings passed in; `${NAME}` is replaced from `.env` |
| `ports` | Mac port : container port |
| `volumes` | Mac path : container path; `:ro` = read-only |
| `healthcheck` | How Docker knows the program is *ready*, not just started |
| `depends_on` | Start order, e.g. wait until Postgres is healthy |
| `profiles` | Service starts only when asked (Flyway: `tools`) |
| `extra_hosts` | Extra hostnames, e.g. `host.docker.internal` |

### compose.yaml vs .env
| File | Holds | In Git? |
|---|---|---|
| `compose/compose.yaml` | What runs and how it connects (same for everyone) | Yes |
| `compose/.env` | Passwords, keys, machine-specific paths | Never (`.gitignore`) |
| `compose/.env.example` | Template for `.env` with harmless local defaults | Yes |

Principle (Twelve-Factor App): keep config and secrets out of code. Anything committed stays in Git history forever. Production equivalents: Helm charts (what runs) and a secrets manager (secrets).

### Postgres data location
`PG_DATA_DIR` in `.env` puts the data files in `/Users/sachin/AI/Production/buywise-data/postgres` (bind mount, outside the repo). The program runs in the container; the data sits on a disk you choose. No Postgres installation on the Mac. Rules: never edit that folder while Postgres runs; exclude it from Time Machine.

### Health checks
| Service | Check | Note |
|---|---|---|
| Postgres | `pg_isready` | Built-in tool |
| Redis | `redis-cli ping` -> `PONG` | Built-in tool |
| Keycloak | bash raw HTTP request (`/dev/tcp`) to `/health/ready` on port 9000 | Image has no curl; health is on the management port |
| LiteLLM | `python3` call to `/health/liveliness` | Image has Python |

Without a health check, Docker reports a container as ready as soon as the process starts (Keycloak needs ~20-30 s more).

### Separate databases (step 2)
- `compose/postgres/init/01-databases.sh` runs once, on the first start with an empty data folder: one database + one user per part (`services`, `agent`, `keycloak`, `litellm`), `REVOKE ALL ... FROM PUBLIC`, pgvector only in `agent`.
- Isolation test: user `agent` connecting to `services` -> `permission denied ... does not have CONNECT privilege`.
- Why: a bug or attack in one part cannot touch another's data; production splits them across a business and an AI cluster by connection string only (ADR-010).

### make
`make` (`/usr/bin/make`) runs named command shortcuts from a `Makefile`. Each module has its own Makefile; the root Makefile delegates (`make up` -> `make -C deploy up`). `make -n <target>` prints commands without running them; `make help` lists targets.

### Measuring AI speed - k (step 6)
`make k` sends the same prompt 5 times through LiteLLM and measures tokens/second. Locally 16.9 tokens/s vs 50 tokens/s production target -> **k = 2.96** (written to `local/scale.yaml`). Local AI deadlines and latency targets are multiplied by k; non-AI targets stay the same as production.

### Production comparison (Q&A)
| Question | Answer |
|---|---|
| Why run the database in Docker? | Same version everywhere (Mac, CI, Kubernetes), isolated, one-file setup, easy reset, production-like. Costs: Docker must run; slightly slower disk on Mac. |
| What if the data is 100 GB? | Works locally but slower and risky on a laptop. In production the container is only the program; data lives on attached cloud disks (PersistentVolumes) or a managed database service. |
| How does production run Postgres? | CloudNativePG on Kubernetes: primary + replicas in pods, data on cloud SSDs, business and AI clusters, apps connect by service name (`business-rw`), PgBouncer pooling, backups to object storage, monitoring, rolling minor upgrades. Alternatives: managed services, or VMs. (Design only locally.) |

### Problems hit and fixes
| Problem | Cause | Fix |
|---|---|---|
| Postgres container exited (126) on first start | Init script not executable | `chmod +x`, reset the fresh volume |
| `make up` reported Keycloak ready while it was still booting | No health check defined | Added real health checks for Keycloak and LiteLLM |

### Commands
| Task | Command |
|---|---|
| Start / stop / status / logs | `make up` / `make down` / `make ps` / `make logs` |
| See what a target runs | `make -n up` |
| psql as admin | `docker exec -it buywise-postgres-1 psql -U postgres -d services` |
| Redis CLI | `docker exec -it buywise-redis-1 redis-cli` |
| Keycloak admin | http://localhost:8080 (admin / admin-local) |
| Keycloak realm info | http://localhost:8080/realms/buywise/.well-known/openid-configuration |
| LiteLLM health / admin UI | http://localhost:4000/health/liveliness, http://localhost:4000/ui (key `sk-buywise-local`) |
| Measure k | `make k` |
