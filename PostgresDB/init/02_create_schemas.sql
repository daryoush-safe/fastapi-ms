\connect fastapi_ms

-- Single schema shared by both services.
-- Tables are namespaced by prefix (users_*, subscriptions_*).
CREATE SCHEMA IF NOT EXISTS auth;

-- Enable pgcrypto for UUID generation at DB level if needed
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Enum types ───────────────────────────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE auth.outboxstatus_user AS ENUM ('pending', 'processed', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE auth.outboxstatus_subscription AS ENUM ('pending', 'processed', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── User Service tables ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS auth.users (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email            VARCHAR     NOT NULL UNIQUE,
    username         VARCHAR     NOT NULL,
    hashed_password  VARCHAR     NOT NULL,
    is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON auth.users (email);

CREATE TABLE IF NOT EXISTS auth.users_outbox (
    id              UUID                      PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id    VARCHAR                   NOT NULL,
    aggregate_type  VARCHAR                   NOT NULL,
    event_type      VARCHAR                   NOT NULL,
    payload         TEXT                      NOT NULL,
    status          auth.outboxstatus_user    NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ               NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_users_outbox_status_created_at
    ON auth.users_outbox (status, created_at);

-- ─── Subscription Service tables ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS auth.subscriptions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR     NOT NULL,
    subscription_type   VARCHAR,
    is_active           BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_subscriptions_email ON auth.subscriptions (email);

CREATE TABLE IF NOT EXISTS auth.subscriptions_outbox (
    id              UUID                            PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id    VARCHAR                         NOT NULL,
    aggregate_type  VARCHAR                         NOT NULL,
    event_type      VARCHAR                         NOT NULL,
    payload         TEXT                            NOT NULL,
    status          auth.outboxstatus_subscription  NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_subscriptions_outbox_status_created_at
    ON auth.subscriptions_outbox (status, created_at);