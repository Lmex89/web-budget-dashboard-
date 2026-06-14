-- Migration 003: Create categories table
-- Created: 2024-01-01

CREATE TABLE IF NOT EXISTS categories (
    id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT NULL,
    icon VARCHAR(50) DEFAULT NULL,
    family_id CHAR(36) NOT NULL,
    parent_id CHAR(36) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_category_family_name_parent (family_id, name, parent_id),
    KEY idx_categories_family_id (family_id),
    KEY idx_categories_parent_id (parent_id),
    CONSTRAINT fk_categories_family FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
