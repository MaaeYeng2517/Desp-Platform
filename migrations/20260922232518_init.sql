-- Create extension "pgcrypto"
CREATE EXTENSION "pgcrypto" WITH SCHEMA "public" VERSION "1.3";
-- Add new schema named "core"
CREATE SCHEMA "core";
-- Add new schema named "mart"
CREATE SCHEMA "mart";
-- Add new schema named "raw"
CREATE SCHEMA "raw";
-- Add new schema named "staging"
CREATE SCHEMA "staging";
-- Create "datasets" table
CREATE TABLE "core"."datasets" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "name" character varying(255) NOT NULL,
  "description" text NULL,
  "source_type" character varying(50) NOT NULL,
  "source_path" character varying(500) NULL,
  "status" character varying(50) NOT NULL DEFAULT 'draft',
  "created_by" character varying(255) NOT NULL DEFAULT 'system',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "datasets_name_key" UNIQUE ("name")
);
-- Create index "idx_datasets_status" to table: "datasets"
CREATE INDEX "idx_datasets_status" ON "core"."datasets" ("status");
-- Create "sales" table
CREATE TABLE "mart"."sales" (
  "transaction_id" character varying(50) NOT NULL,
  "transaction_date" date NOT NULL,
  "customer_id" character varying(50) NOT NULL,
  "product_id" character varying(50) NOT NULL,
  "quantity" integer NOT NULL,
  "unit_price" numeric(12,2) NOT NULL,
  "total_amount" numeric(14,2) NOT NULL,
  PRIMARY KEY ("transaction_id")
);
-- Create "sales_daily" table
CREATE TABLE "mart"."sales_daily" (
  "transaction_date" date NOT NULL,
  "transaction_count" bigint NOT NULL,
  "units_sold" bigint NOT NULL,
  "revenue" numeric(14,2) NOT NULL,
  PRIMARY KEY ("transaction_date")
);
-- Create "sales" table
CREATE TABLE "raw"."sales" (
  "transaction_id" character varying(50) NOT NULL,
  "transaction_date" date NOT NULL,
  "customer_id" character varying(50) NOT NULL,
  "product_id" character varying(50) NOT NULL,
  "quantity" integer NOT NULL,
  "unit_price" numeric(12,2) NOT NULL,
  "loaded_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("transaction_id")
);
-- Create "sales" table
CREATE TABLE "staging"."sales" (
  "transaction_id" character varying(50) NOT NULL,
  "transaction_date" date NOT NULL,
  "customer_id" character varying(50) NOT NULL,
  "product_id" character varying(50) NOT NULL,
  "quantity" integer NOT NULL,
  "unit_price" numeric(12,2) NOT NULL,
  "total_amount" numeric(14,2) NOT NULL,
  PRIMARY KEY ("transaction_id")
);
-- Create "audit_logs" table
CREATE TABLE "core"."audit_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "dataset_id" uuid NULL,
  "action" character varying(100) NOT NULL,
  "resource_type" character varying(100) NOT NULL,
  "resource_id" character varying(255) NULL,
  "user" character varying(255) NOT NULL DEFAULT 'system',
  "status" character varying(20) NOT NULL,
  "details" jsonb NULL,
  "ip_address" character varying(50) NULL,
  "timestamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "audit_logs_dataset_id_fkey" FOREIGN KEY ("dataset_id") REFERENCES "core"."datasets" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "idx_audit_logs_action" to table: "audit_logs"
CREATE INDEX "idx_audit_logs_action" ON "core"."audit_logs" ("action");
-- Create index "idx_audit_logs_dataset" to table: "audit_logs"
CREATE INDEX "idx_audit_logs_dataset" ON "core"."audit_logs" ("dataset_id");
-- Create index "idx_audit_logs_timestamp" to table: "audit_logs"
CREATE INDEX "idx_audit_logs_timestamp" ON "core"."audit_logs" ("timestamp" DESC);
-- Create "files" table
CREATE TABLE "core"."files" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "dataset_id" uuid NOT NULL,
  "filename" character varying(500) NOT NULL,
  "file_path" character varying(500) NOT NULL,
  "bucket" character varying(100) NOT NULL,
  "object_name" character varying(500) NOT NULL,
  "file_size" integer NOT NULL,
  "content_type" character varying(100) NOT NULL,
  "row_count" integer NULL,
  "column_names" jsonb NULL,
  "checksum" character varying(255) NULL,
  "uploaded_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "status" character varying(50) NOT NULL DEFAULT 'uploaded',
  PRIMARY KEY ("id"),
  CONSTRAINT "files_dataset_id_fkey" FOREIGN KEY ("dataset_id") REFERENCES "core"."datasets" ("id") ON UPDATE NO ACTION ON DELETE CASCADE
);
-- Create index "idx_files_dataset" to table: "files"
CREATE INDEX "idx_files_dataset" ON "core"."files" ("dataset_id");
-- Create index "idx_files_status" to table: "files"
CREATE INDEX "idx_files_status" ON "core"."files" ("status");
-- Create "metadata" table
CREATE TABLE "core"."metadata" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "dataset_id" uuid NOT NULL,
  "schema_definition" jsonb NOT NULL,
  "column_count" integer NOT NULL,
  "file_format" character varying(50) NULL DEFAULT 'csv',
  "delimiter" character varying(10) NULL DEFAULT ',',
  "has_header" character varying(5) NULL DEFAULT 'true',
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "metadata_dataset_id_fkey" FOREIGN KEY ("dataset_id") REFERENCES "core"."datasets" ("id") ON UPDATE NO ACTION ON DELETE CASCADE
);
-- Create "quality_rules" table
CREATE TABLE "core"."quality_rules" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "dataset_id" uuid NOT NULL,
  "name" character varying(255) NOT NULL,
  "rule_type" character varying(50) NOT NULL,
  "column_name" character varying(255) NOT NULL,
  "rule_config" jsonb NOT NULL,
  "is_active" character varying(5) NULL DEFAULT 'true',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "quality_rules_dataset_id_fkey" FOREIGN KEY ("dataset_id") REFERENCES "core"."datasets" ("id") ON UPDATE NO ACTION ON DELETE CASCADE
);
-- Create "quality_results" table
CREATE TABLE "core"."quality_results" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "dataset_id" uuid NOT NULL,
  "rule_id" uuid NULL,
  "rule_name" character varying(255) NOT NULL,
  "status" character varying(20) NOT NULL,
  "passed_count" integer NULL DEFAULT 0,
  "failed_count" integer NULL DEFAULT 0,
  "error_message" text NULL,
  "executed_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "quality_results_rule_id_fkey" FOREIGN KEY ("rule_id") REFERENCES "core"."quality_rules" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create index "idx_quality_results_dataset" to table: "quality_results"
CREATE INDEX "idx_quality_results_dataset" ON "core"."quality_results" ("dataset_id", "executed_at" DESC);
