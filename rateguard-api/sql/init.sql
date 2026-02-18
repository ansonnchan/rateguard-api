-- Bootstrap table for API usage and rate-limit event auditing.
CREATE TABLE IF NOT EXISTS request_logs (
    id BIGSERIAL PRIMARY KEY,
    api_key TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
