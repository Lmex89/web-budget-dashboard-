-- Migration 004: Create credit_cards table
-- Created: 2024-01-01

CREATE TABLE IF NOT EXISTS credit_cards (
    id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    last_four_digits VARCHAR(4) DEFAULT NULL,
    `limit` DECIMAL(15,2) NOT NULL,
    closing_day INT NOT NULL,
    due_day INT NOT NULL,
    current_balance DECIMAL(15,2) DEFAULT 0,
    family_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_credit_cards_family_id (family_id),
    CONSTRAINT fk_credit_cards_family FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
