-- Migration 010: Change date column from TIMESTAMP to DATETIME
-- TIMESTAMP auto-converts based on session timezone, causing date shifts.
-- DATETIME stores values as-is without timezone conversion.

ALTER TABLE expenses MODIFY date DATETIME NOT NULL;

ALTER TABLE installments MODIFY due_date DATETIME NOT NULL;
