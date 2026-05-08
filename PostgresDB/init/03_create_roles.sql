\connect fastapi_ms

-- ─── User Service role ────────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE ROLE user_service_role WITH LOGIN PASSWORD 'user_service_pass';
EXCEPTION WHEN duplicate_object THEN
    RAISE NOTICE 'Role user_service_role already exists, skipping.';
END $$;

-- ─── Subscription Service role ────────────────────────────────────────────────
DO $$ BEGIN
    CREATE ROLE subscription_service_role WITH LOGIN PASSWORD 'subscription_service_pass';
EXCEPTION WHEN duplicate_object THEN
    RAISE NOTICE 'Role subscription_service_role already exists, skipping.';
END $$;

-- ─── Debezium role (needs replication + login) ────────────────────────────────
DO $$ BEGIN
    CREATE ROLE debezium_role WITH
        LOGIN
        PASSWORD 'debezium_pass'
        REPLICATION;
EXCEPTION WHEN duplicate_object THEN
    RAISE NOTICE 'Role debezium_role already exists, skipping.';
END $$;