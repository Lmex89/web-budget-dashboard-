-- Migration 014: Add composite indexes including deleted_at for soft-delete filtering
-- Created: 2026-09-19
--
-- Every query filters on `deleted_at IS NULL`. Adding this column to composite
-- indexes allows the database to efficiently filter soft-deleted rows without
-- scanning the entire table.

-- Expenses: family + deleted_at + date (most common query pattern)
ALTER TABLE expenses
    ADD INDEX idx_expenses_family_deleted_date (family_id, deleted_at, date);

-- Expenses: family + deleted_at + category (category filtering)
ALTER TABLE expenses
    ADD INDEX idx_expenses_family_deleted_category (family_id, deleted_at, category_id);

-- Categories: family + deleted_at + name
ALTER TABLE categories
    ADD INDEX idx_categories_family_deleted_name (family_id, deleted_at, name);

-- Credit cards: family + deleted_at + name
ALTER TABLE credit_cards
    ADD INDEX idx_credit_cards_family_deleted_name (family_id, deleted_at, name);

-- Debts: family + deleted_at + status
ALTER TABLE debts
    ADD INDEX idx_debts_family_deleted_status (family_id, deleted_at, status);

-- Users: family + deleted_at + role
ALTER TABLE users
    ADD INDEX idx_users_family_deleted_role (family_id, deleted_at, role);

-- Budgets: family + deleted_at + year + month
ALTER TABLE budgets
    ADD INDEX idx_budgets_family_deleted_period (family_id, deleted_at, year, month);
