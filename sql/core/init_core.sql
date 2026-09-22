-- Core schema for the Data Core Platform API.
--
-- This schema is separate from the existing raw/staging/mart
-- Medallion Architecture schemas. It stores metadata about
-- datasets, files, quality rules, and audit logs managed
-- through the FastAPI API.
--
-- Run: psql -h localhost -U dataeng -d datawarehouse -f sql/core/init_core.sql

CREATE SCHEMA IF NOT EXISTS core;

-- ---------------------------------------------------------------------------
-- core.datasets — registered datasets managed via the API
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS core.audit_logs;
DROP TABLE IF EXISTS core.quality_results;
DROP TABLE IF EXISTS core.quality_rules;
DROP TABLE IF EXISTS core.metadata;
DROP TABLE IF EXISTS core.files;
DROP TABLE IF EXISTS core.datasets;

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

-- ---------------------------------------------------------------------------
-- core.files — file metadata for uploaded/processed files
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- core.metadata — schema definitions extracted or defined for datasets
-- ---------------------------------------------------------------------------
CREATE TABLE core.metadata (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id       UUID NOT NULL REFERENCES core.datasets(id) ON DELETE CASCADE,
    schema_definition JSONB NOT NULL,
    column_count     INTEGER NOT NULL,
    file_format      VARCHAR(50) DEFAULT 'csv',
    delimiter        VARCHAR(10) DEFAULT ',',
    has_header       VARCHAR(5) DEFAULT 'true',
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- core.quality_rules — configurable quality rules per dataset
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- core.quality_results — results of executed quality checks
-- ---------------------------------------------------------------------------
CREATE TABLE core.quality_results (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID NOT NULL,
    rule_id      UUID REFERENCES core.quality_rules(id),
    rule_name    VARCHAR(255) NOT NULL,
    status       VARCHAR(20) NOT NULL,
    passed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    error_message TEXT,
    executed_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- core.audit_logs — audit trail of all API actions
-- ---------------------------------------------------------------------------
CREATE TABLE core.audit_logs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID REFERENCES core.datasets(id),
    action       VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id  VARCHAR(255),
    user         VARCHAR(255) NOT NULL DEFAULT 'system',
    status       VARCHAR(20) NOT NULL,
    details      JSONB,
    ip_address   VARCHAR(50),
    timestamp    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
CREATE INDEX idx_datasets_status ON core.datasets(status);
CREATE INDEX idx_files_dataset ON core.files(dataset_id);
CREATE INDEX idx_files_status ON core.files(status);
CREATE INDEX idx_quality_results_dataset ON core.quality_results(dataset_id, executed_at DESC);
CREATE INDEX idx_audit_logs_timestamp ON core.audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_dataset ON core.audit_logs(dataset_id);
CREATE INDEX idx_audit_logs_action ON core.audit_logs(action);
