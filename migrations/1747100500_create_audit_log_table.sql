CREATE TABLE IF NOT EXISTS audit_log (
    id_audit_log SERIAL PRIMARY KEY,
    username VARCHAR(255),
    method VARCHAR(20) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    status_code INTEGER NOT NULL,
    ip_address VARCHAR(100),
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ROLLBACK
-- DROP TABLE IF EXISTS audit_log;
