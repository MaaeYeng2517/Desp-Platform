-- Atlas desired state for the Data Engineering Workflow Platform.
-- Database-scoped because the project uses multiple PostgreSQL schemas.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE raw.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INTEGER       NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    loaded_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INTEGER       NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    total_amount     NUMERIC(14,2) NOT NULL
);

CREATE TABLE mart.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INTEGER       NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    total_amount     NUMERIC(14,2) NOT NULL
);

CREATE TABLE mart.sales_daily (
    transaction_date   DATE PRIMARY KEY,
    transaction_count  BIGINT        NOT NULL,
    units_sold         BIGINT        NOT NULL,
    revenue            NUMERIC(14,2) NOT NULL
);

CREATE TABLE core.datasets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    source_type VARCHAR(50) NOT NULL,
    source_path VARCHAR(500),
    status      VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_by  VARCHAR(255) NOT NULL DEFAULT 'system',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE core.files (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID NOT NULL REFERENCES core.datasets(id) ON DELETE CASCADE,
    filename     VARCHAR(500) NOT NULL,
    file_path    VARCHAR(500) NOT NULL,
    bucket       VARCHAR(100) NOT NULL,
    object_name  VARCHAR(500) NOT NULL,
    file_size    INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    row_count    INTEGER,
    column_names JSONB,
    checksum     VARCHAR(255),
    uploaded_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       VARCHAR(50) NOT NULL DEFAULT 'uploaded'
);

CREATE TABLE core.metadata (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id        UUID NOT NULL REFERENCES core.datasets(id) ON DELETE CASCADE,
    schema_definition JSONB NOT NULL,
    column_count      INTEGER NOT NULL,
    file_format       VARCHAR(50) DEFAULT 'csv',
    delimiter         VARCHAR(10) DEFAULT ',',
    has_header        VARCHAR(5) DEFAULT 'true',
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE core.quality_rules (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id  UUID NOT NULL REFERENCES core.datasets(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    rule_type   VARCHAR(50) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    rule_config JSONB NOT NULL,
    is_active   VARCHAR(5) DEFAULT 'true',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE core.quality_results (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id    UUID NOT NULL,
    rule_id       UUID REFERENCES core.quality_rules(id),
    rule_name     VARCHAR(255) NOT NULL,
    status        VARCHAR(20) NOT NULL,
    passed_count  INTEGER DEFAULT 0,
    failed_count  INTEGER DEFAULT 0,
    error_message TEXT,
    executed_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE core.audit_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id    UUID REFERENCES core.datasets(id),
    action        VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id   VARCHAR(255),
    "user"        VARCHAR(255) NOT NULL DEFAULT 'system',
    status        VARCHAR(20) NOT NULL,
    details       JSONB,
    ip_address    VARCHAR(50),
    timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_status ON core.datasets(status);
CREATE INDEX idx_files_dataset ON core.files(dataset_id);
CREATE INDEX idx_files_status ON core.files(status);
CREATE INDEX idx_quality_results_dataset ON core.quality_results(dataset_id, executed_at DESC);
CREATE INDEX idx_audit_logs_timestamp ON core.audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_dataset ON core.audit_logs(dataset_id);
CREATE INDEX idx_audit_logs_action ON core.audit_logs(action);
