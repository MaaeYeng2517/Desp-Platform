-- Database schema initialization for the Data Engineering Platform.
--
-- Creates the three layers of the Medallion Architecture:
--   raw       -> Bronze data loaded verbatim from source systems
--   staging   -> Cleaned / standardised data (Silver equivalent in the warehouse)
--   mart      -> Business-ready aggregated data (Gold)

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

-- ---------------------------------------------------------------------------
-- raw.sales — raw, immutable copy of source records
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS raw.sales;

CREATE TABLE raw.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INT           NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    loaded_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- staging.sales — cleaned, validated data (Silver layer in the warehouse)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS staging.sales;

CREATE TABLE staging.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INT           NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    total_amount     NUMERIC(14,2) NOT NULL
);

-- ---------------------------------------------------------------------------
-- mart.sales — business-ready fact table (Gold layer in the warehouse)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.sales;

CREATE TABLE mart.sales (
    transaction_id   VARCHAR(50) PRIMARY KEY,
    transaction_date DATE          NOT NULL,
    customer_id      VARCHAR(50)   NOT NULL,
    product_id       VARCHAR(50)   NOT NULL,
    quantity         INT           NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL,
    total_amount     NUMERIC(14,2) NOT NULL
);

-- ---------------------------------------------------------------------------
-- mart.sales_daily — daily aggregation (materialised by gold_sales.sql)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.sales_daily;
