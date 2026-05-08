\connect fastapi_ms

-- ─── Schema usage ─────────────────────────────────────────────────────────────
GRANT USAGE ON SCHEMA auth TO user_service_role;
GRANT USAGE ON SCHEMA auth TO subscription_service_role;
GRANT USAGE ON SCHEMA auth TO debezium_role;

-- ─── User Service: owns users + users_outbox only ─────────────────────────────
GRANT SELECT, INSERT, UPDATE, DELETE
    ON auth.users
    TO user_service_role;

GRANT SELECT, INSERT, UPDATE, DELETE
    ON auth.users_outbox
    TO user_service_role;

-- ─── Subscription Service: owns subscriptions + subscriptions_outbox only ─────
GRANT SELECT, INSERT, UPDATE, DELETE
    ON auth.subscriptions
    TO subscription_service_role;

GRANT SELECT, INSERT, UPDATE, DELETE
    ON auth.subscriptions_outbox
    TO subscription_service_role;

-- ─── Debezium: needs SELECT on outbox tables + replication permissions ─────────
GRANT SELECT ON auth.users_outbox          TO debezium_role;
GRANT SELECT ON auth.subscriptions_outbox  TO debezium_role;

-- Debezium needs SELECT on the tables it watches for schema discovery
GRANT SELECT ON auth.users          TO debezium_role;
GRANT SELECT ON auth.subscriptions  TO debezium_role;

-- Allow debezium to create publications
GRANT CREATE ON DATABASE fastapi_ms TO debezium_role;

-- ─── Logical replication publications ─────────────────────────────────────────
-- Each Debezium connector gets its own publication scoped to its outbox table.

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_publication WHERE pubname = 'dbz_publication_user'
    ) THEN
        CREATE PUBLICATION dbz_publication_user
            FOR TABLE auth.users_outbox;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_publication WHERE pubname = 'dbz_publication_subscription'
    ) THEN
        CREATE PUBLICATION dbz_publication_subscription
            FOR TABLE auth.subscriptions_outbox;
    END IF;
END $$;