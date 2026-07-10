# ChatService

Manages user ⇆ AI chat threads over the Text-to-SQL ML service. Each thread is
bound to one DBService database connection.

- `POST /api/v1/threads` — create a chat thread. Requires `connection_id`
  (optional `title`, auto-derived from the first question when omitted). The
  connection's ownership is validated **synchronously** against DBService
  (`GET /connections/{id}`, forwarding the caller's JWT).
- `GET /api/v1/threads` — list the caller's threads (newest activity first).
- `GET /api/v1/threads/{thread_id}/messages` — list a thread's messages.
- `POST /api/v1/threads/{thread_id}/messages` — send a question (body: `question`
  only). Persists the user turn, resolves the DB schema from the local replica,
  proxies the ML service's SSE stream to the caller (`text/event-stream`), and
  stores the assistant's final answer + SQL once the stream completes.

## Connection schema replica (async, via DBService outbox → CDC → Kafka)

ChatService does **not** fetch the schema on the hot path. It runs a Kafka
consumer (group `chat_service_group`) on `dbservice.dbconnection` and maintains a
local replica table `chat_connections(connection_id, owner_id, title, engine,
schema)`. DBService publishes `DatabaseConnectionRegistered` on register and
`ConnectionSchemaExtracted` once the schema is extracted (asynchronously, in a
background task). `send-message` reads the schema from this replica; if it hasn't
arrived yet the request returns `409` (`SchemaUnavailable`).

Owns the `chatservice` Postgres schema (`chat_threads`, `chat_messages`,
`chat_connections`). `chat_service_role` is a Kafka consumer only — no
REPLICATION grant, no outbox.
