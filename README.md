# fastapi_ms

The application layer of **t2s**, a text-to-SQL product: users connect a database, ask
questions in plain English in a chat UI, and get back generated SQL plus its results. This
repo is a uv-workspace monorepo of four FastAPI microservices built with clean architecture,
talking to each other asynchronously over Kafka via a transactional-outbox + Debezium CDC
pipeline.

## Services

| Service | Responsibility |
| --- | --- |
| **UserService** | Accounts, auth (JWT), identity. Source of truth for `User` aggregates. |
| **SubscriptionService** | Plans/billing via Stripe; reacts to user lifecycle events. |
| **DBService** | Stores users' external DB connections and executes generated SQL against them (`POST /api/v1/query`) — the only service that reaches into a user's actual database. |
| **ChatService** | Chat threads/messages; on a user message, streams a live SQL-generation run from the ML inference API (see below) back to the client over SSE and persists the result. |

Each service is independently deployable, has its own Postgres schema, and owns its own
`alembic` migrations.

## How it fits with the rest of t2s

This repo is the *product*; it does not train or host models. The ML side lives in
[`training arena/`](../training%20arena/) (`sqlgen`), which trains a schema-pruner + SQL-generator
model pair offline and serves them online behind a LangGraph inference API
(`prune_schema → generate_sql → execute_sql → present`, with a retry loop on failure).
`ChatService` is the client of that API: `ChatService/src/infrastructure/ml/sse_sql_generator.py`
streams `POST {ML_API}/stream-query` and relays the SSE events straight through to the
frontend. In the other direction, the `execute_sql` node of the inference graph calls back into
**this repo's** `DBService` (`POST /api/v1/query`, bearer-token authenticated) to actually run the
SQL it generated against the user's connected database — closing the loop between the two repos.

Everything here runs on Kubernetes via GitOps out of [`platform/`](../platform/); this repo only
builds and pushes container images (see CI below). `platform/apps/README.md` and
`platform/apps/*/values.yaml` are the deploy-time source of truth for how these four services are
configured in the cluster.

## Architecture

### Workspace layout
The root `pyproject.toml` declares a `[tool.uv.workspace]` with members: `libs/shared_core`,
`libs/shared_infra`, `contracts`, `UserService`, `SubscriptionService`, `DBService`, `ChatService`.
Services declare `shared_core`/`shared_infra`/`contracts` as `{ workspace = true }` sources.

### Clean architecture per service
Each service follows the same four-layer split under `src/`:

- **`domain/`** — aggregates (extending `libs.shared_core.base_aggregate.AggregateRoot`),
  domain events, exceptions, and `ports/` (abstract interfaces for repository, unit-of-work,
  publisher, and service-specific collaborators like `payment` or `sql_generator`). Depends on
  nothing outside itself + `shared_core`.
- **`application/`** — DTOs, a service facade, and one use-case class per business operation
  (`async execute(dto)` over an injected UoW).
- **`infrastructure/`** — concrete adapters: SQLAlchemy async ORM + unit-of-work + repositories,
  the outbox publisher, and external clients (Stripe, the ML inference API's SSE client, etc.).
- **`interfaces/`** — FastAPI routers (`http/api/v1/`) and Kafka consumers
  (`consumers/{kafka_handlers,event_registry}.py`).

`container.py` is a manual DI singleton per service (no DI framework); `main.py` wires the
FastAPI app and starts the Kafka consumer inside `lifespan`.

### Transactional outbox + Debezium CDC
Cross-service events never go through a direct Kafka produce from a request handler. Instead:
1. Aggregates record domain events via `AggregateRoot.record_event(...)`.
2. The unit-of-work inserts each event into that service's `auth.<service>_outbox` table in the
   **same transaction** as the domain write, then commits.
3. Debezium tails the outbox tables via Postgres logical replication and republishes them to
   Kafka topics (`contracts/topics.py`) using the `EventRouter` SMT.
4. The consuming service's `BaseKafkaConsumer` (manual commit, DLQ-on-failure) dispatches by
   `event_type` via its `event_registry.py`.

This guarantees a domain write and its downstream event are never inconsistent, without 2PC.

### Shared code
- **`libs/shared_core/`** — `AggregateRoot`, `DomainEvent`, value objects; pure Python, no infra.
- **`libs/shared_infra/`** — `BaseKafkaConsumer`, structured JSON logging, `/healthz` + `/readyz`
  probes, Prometheus `/metrics`, request-context middleware (shared request-id across logs).
- **`contracts/`** — the cross-service event dataclasses and topic constants both producer and
  consumer import from, so they cannot drift apart.

## Running locally

```bash
cp .env.example .env
docker compose up --build
```
Brings up Postgres, Kafka + Kafka Connect (Debezium), and all four services; each runs its
`alembic upgrade head` on boot and the outbox connectors auto-register.

For a single service against the shared workspace:
```bash
uv sync --all-packages
cd UserService && uv run uvicorn src.main:app --reload --port 8000
```

## CI/CD

`.github/workflows/` runs ruff (lint + format) and pytest on every push, and builds/pushes GHCR
images per service on `main`/tags. `platform/` picks up new image tags via the GitOps flow
described there — this repo never talks to the cluster directly.
