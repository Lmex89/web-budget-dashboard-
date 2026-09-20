-- Migration 013: Create monthly budgets and per-category budget limits
-- Created: 2026-09-14
--
-- Budgets are family-scoped and unique per (family_id, year, month).
-- Per-category limits live in budget_categories and are soft-deleted like
-- every other tenant-owned table.

CREATE TABLE IF NOT EXISTS budgets (
    id CHAR(36) NOT NULL,
    family_id CHAR(36) NOT NULL,
    year INT NOT NULL,
    month TINYINT NOT NULL,
    total_budget DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_budgets_family_period (family_id, year, month),
    CONSTRAINT fk_budgets_family FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS budget_categories (
    id CHAR(36) NOT NULL,
    budget_id CHAR(36) NOT NULL,
    category_id CHAR(36) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_budget_categories_budget_category (budget_id, category_id),
    KEY idx_budget_categories_category_id (category_id),
    CONSTRAINT fk_budget_categories_budget FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
    CONSTRAINT fk_budget_categories_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
