-- Migration 005: Create expenses table
-- Created: 2024-01-01

CREATE TABLE IF NOT EXISTS expenses (
    id CHAR(36) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT DEFAULT NULL,
    date TIMESTAMP NOT NULL,
    payment_method ENUM('cash', 'debit', 'credit') NOT NULL,
    is_installment BOOLEAN DEFAULT FALSE,
    total_installments INT DEFAULT NULL,
    installment_number INT DEFAULT NULL,
    family_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    category_id CHAR(36) NOT NULL,
    credit_card_id CHAR(36) DEFAULT NULL,
    debt_id CHAR(36) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_expenses_family_id (family_id),
    KEY idx_expenses_user_id (user_id),
    KEY idx_expenses_category_id (category_id),
    KEY idx_expenses_date (date),
    KEY idx_expenses_payment_method (payment_method),
    CONSTRAINT fk_expenses_family FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    CONSTRAINT fk_expenses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_expenses_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    CONSTRAINT fk_expenses_credit_card FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id) ON DELETE SET NULL,
    CONSTRAINT fk_expenses_debt FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
