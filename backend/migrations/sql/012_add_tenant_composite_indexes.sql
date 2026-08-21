-- Migration 012: Multi-tenant composite indexes for family-scoped access
-- Created: 2026-08-21
--
-- Strengthens shared-schema tenant isolation and query performance by
-- adding composite indexes that lead with `family_id`. Every tenant-owned
-- query filters on `family_id` first, so these indexes serve the common
-- access paths. The existing single-column `idx_*_family_id` indexes are
-- kept (MariaDB may still use them for foreign-key checks).

-- Expenses: family + date (list/dashboard), family + category (filtering)
ALTER TABLE expenses
    ADD INDEX idx_expenses_family_date (family_id, date),
    ADD INDEX idx_expenses_family_category (family_id, category_id);

-- Categories: family + name (uniqueness check, listing by name)
ALTER TABLE categories
    ADD INDEX idx_categories_family_name (family_id, name);

-- Credit cards: family + name (uniqueness check, listing)
ALTER TABLE credit_cards
    ADD INDEX idx_credit_cards_family_name (family_id, name);

-- Debts: family + status (list by status placeholder)
ALTER TABLE debts
    ADD INDEX idx_debts_family_status (family_id, status);

-- Users: family + role (family member listing, role-based lookups)
ALTER TABLE users
    ADD INDEX idx_users_family_role (family_id, role);
