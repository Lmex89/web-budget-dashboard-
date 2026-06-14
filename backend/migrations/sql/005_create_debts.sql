-- Migration 007: Create debts table
-- Created: 2024-01-01

CREATE TABLE IF NOT EXISTS debts (
    id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT NULL,
    original_amount DECIMAL(15,2) NOT NULL,
    remaining_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    type ENUM('owed_to_us', 'we_owe', 'family_loan') NOT NULL,
    status ENUM('active', 'paid', 'defaulted') DEFAULT 'active',
    counterparty_name VARCHAR(255) DEFAULT NULL,
    family_id CHAR(36) NOT NULL,
    created_by_user_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_debts_family_id (family_id),
    KEY idx_debts_created_by_user_id (created_by_user_id),
    KEY idx_debts_status (status),
    CONSTRAINT fk_debts_family FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    CONSTRAINT fk_debts_created_by FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
