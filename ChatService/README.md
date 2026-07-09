# ChatService

Manages user ⇆ AI chat threads over the Text-to-SQL ML service.

- `POST /api/v1/threads` — create a chat thread (optional title; auto-derived from
  the first question when omitted).
- `POST /api/v1/threads/{thread_id}/messages` — send a question. Persists the user
  turn, proxies the ML service's SSE stream to the caller (`text/event-stream`),
  and stores the assistant's final answer + SQL once the stream completes.

Owns the `chatservice` Postgres schema (`chat_threads`, `chat_messages`).
