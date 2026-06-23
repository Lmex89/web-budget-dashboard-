-- Migration 009: Add deleted_at column to all tables for soft delete

ALTER TABLE families ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER updated_at;
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER updated_at;
ALTER TABLE categories ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER created_at;
ALTER TABLE credit_cards ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER updated_at;
ALTER TABLE expenses ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER updated_at;
ALTER TABLE installments ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER created_at;
ALTER TABLE debts ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER updated_at;
ALTER TABLE audit_logs ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER created_at;
