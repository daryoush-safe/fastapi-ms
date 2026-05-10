\connect fastapi_ms

-- ─── User Service role ────────────────────────────────────────────────────────
DO $$ BEGIN
    -- Add REPLICATION here
    CREATE ROLE user_service_role WITH LOGIN PASSWORD 'user_service_pass' REPLICATION;
EXCEPTION WHEN duplicate_object THEN
    ALTER ROLE user_service_role WITH REPLICATION; -- Ensure it has it if already exists
END $$;

-- ─── Subscription Service role ────────────────────────────────────────────────
DO $$ BEGIN
    -- Add REPLICATION here
    CREATE ROLE subscription_service_role WITH LOGIN PASSWORD 'subscription_service_pass' REPLICATION;
EXCEPTION WHEN duplicate_object THEN
    ALTER ROLE subscription_service_role WITH REPLICATION;
END $$;

-- (Keep Debezium role as it was)
DO $$ BEGIN
    CREATE ROLE debezium_role WITH LOGIN PASSWORD 'debezium_pass' REPLICATION;
EXCEPTION WHEN duplicate_object THEN
    RAISE NOTICE 'Role debezium_role already exists, skipping.';
END $$;