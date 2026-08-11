-- Migration 011: Replace is_admin with role enum
-- Created: 2026-08-10

ALTER TABLE users
    ADD COLUMN role ENUM('admin', 'member', 'viewer') NOT NULL DEFAULT 'member' AFTER is_active;

UPDATE users
SET role = CASE
    WHEN is_admin = TRUE THEN 'admin'
    ELSE 'member'
END;

ALTER TABLE users
    DROP COLUMN is_admin;
