-- Migration 006: Create installments table
-- Created: 2024-01-01

CREATE TABLE IF NOT EXISTS installments (
    id CHAR(36) NOT NULL,
    expense_id CHAR(36) NOT NULL,
    credit_card_id CHAR(36) DEFAULT NULL,
    installment_number INT NOT NULL,
    total_installments INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    due_date TIMESTAMP NOT NULL,
    status ENUM('pending', 'paid', 'overdue') DEFAULT 'pending',
    paid_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_installments_expense_id (expense_id),
    KEY idx_installments_credit_card_id (credit_card_id),
    KEY idx_installments_due_date (due_date),
    CONSTRAINT fk_installments_expense FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    CONSTRAINT fk_installments_credit_card FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
