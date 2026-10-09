-- FinSight - PostgreSQL Database Schema
-- Complete DDL for all 8 tables with constraints and relationships

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for fresh setup)
-- Commented out to allow safe migration development
-- DROP TABLE IF EXISTS transactions CASCADE;
-- DROP TABLE IF EXISTS savings_goals CASCADE;
-- DROP TABLE IF EXISTS transfers CASCADE;
-- DROP TABLE IF EXISTS budgets CASCADE;
-- DROP TABLE IF EXISTS accounts CASCADE;
-- DROP TABLE IF EXISTS audit_logs CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- 1. USERS Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    -- Primary key: UUID type
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- identification: email (unique constraint)
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    -- personal info
    full_name VARCHAR(120) NOT NULL,

    -- role: USER, ADMIN, SUPER_ADMIN (enum-like constraint)
    role VARCHAR(20) NOT NULL
        CHECK (role IN ('USER', 'ADMIN', 'SUPER_ADMIN'))
        DEFAULT 'USER',

    -- currency settings
    currency CHAR(3) DEFAULT 'INR',

    -- financial settings
    monthly_income NUMERIC(12,2) DEFAULT 0
        CHECK (monthly_income >= 0),

    -- account status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index on email for fast lookups
CREATE INDEX idx_users_email ON users(email);

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 2. ACCOUNTS Table
-- ============================================================
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to users
    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    -- account details
    name VARCHAR(80) NOT NULL,
    type VARCHAR(20) NOT NULL
        CHECK (type IN ('CASH', 'BANK', 'UPI', 'CARD')),

    -- balance (NUMERIC(14,2) - never FLOAT)
    balance NUMERIC(14,2) DEFAULT 0
        CHECK (balance >= 0),

    -- currency info
    currency CHAR(3) DEFAULT 'INR',

    -- status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),

    -- prevent duplicate names per user
    UNIQUE(user_id, name, type)
);

-- Primary index for account lookups
CREATE INDEX idx_accounts_user ON accounts(user_id, is_active);


-- ============================================================
-- 3. CATEGORIES Table
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(60) UNIQUE NOT NULL,
    kind VARCHAR(10) NOT NULL
        CHECK (kind IN ('INCOME', 'EXPENSE')),
    is_default BOOLEAN DEFAULT true,
    sort_order INT DEFAULT 0,
    notes TEXT
);

-- Insert default categories
INSERT INTO categories (id, name, kind, is_default, sort_order) VALUES
    (1, 'Food & Dining', 'INCOME', false, 1),
    (2, 'Food & Dining', 'EXPENSE', true, 1),
    (3, 'Transportation', 'INCOME', false, 2),
    (4, 'Transportation', 'EXPENSE', true, 2),
    (5, 'Housing', 'INCOME', false, 3),
    (6, 'Housing', 'EXPENSE', true, 3),
    (7, 'Education', 'INCOME', false, 4),
    (8, 'Education', 'EXPENSE', true, 4),
    (9, 'Entertainment', 'INCOME', false, 5),
    (10, 'Entertainment', 'EXPENSE', true, 5),
    (11, 'Health', 'INCOME', false, 6),
    (12, 'Health', 'EXPENSE', true, 6),
    (13, 'Savings', 'INCOME', false, 7),
    (14, 'Savings', 'EXPENSE', false, 8),
    (15, 'Shopping', 'EXPENSE', true, 9),
    (16, 'Subscriptions', 'EXPENSE', true, 10),
    (17, 'Gifts & Donations', 'EXPENSE', true, 11),
    (18, 'Other', 'EXPENSE', true, 12);

-- Income categories (negative spending = income)
INSERT INTO categories (id, name, kind, is_default, sort_order) VALUES
    (101, 'Salary', 'INCOME', true, 0),
    (102, 'Freelance', 'INCOME', true, 1),
    (103, 'Investment', 'INCOME', true, 2),
    (104, 'Allowance', 'INCOME', true, 3),
    (105, 'Other Income', 'INCOME', true, 4);


-- ============================================================
-- 4. TRANSACTIONS Table (core transaction ledger)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys with cascade delete
    account_id UUID NOT NULL
        REFERENCES accounts(id) ON DELETE CASCADE,

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    category_id SMALLINT NOT NULL
        REFERENCES categories(id) ON DELETE RESTRICT,

    -- transaction type enforcement
    type VARCHAR(10) NOT NULL
        CHECK (type IN ('INCOME', 'EXPENSE', 'TRANSFER')),

    -- amount with validation (must be positive)
    amount NUMERIC(14,2) NOT NULL
        CHECK (amount > 0),

    -- payee name (nullable for income)
    payee VARCHAR(120) DEFAULT NULL,

    -- transaction datetime
    transacted_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- optional notes
    notes TEXT DEFAULT NULL,

    -- flag status for fraud detection
    flag_status VARCHAR(15) DEFAULT 'NORMAL'
        CHECK (flag_status IN ('NORMAL', 'SUSPICIOUS', 'REJECTED', 'CONFIRMED')),

    -- source (manual, import, auto)
    source VARCHAR(10) DEFAULT 'MANUAL'
        CHECK (source IN ('MANUAL', 'IMPORT', 'AUTO')),

    -- MongoDB GridFS reference for receipt image
    receipt_ref VARCHAR(120) DEFAULT NULL,

    -- timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    -- constraint: from must differ to from/to account in transfers
    UNIQUE(account_id, transacted_at, amount, PAYEE, category_id)
);

-- ============================================================
-- CRITICAL INDEXES for query performance
-- ============================================================

-- Main query path: user_id + date DESC
CREATE INDEX idx_tx_user_date ON transactions(user_id, transacted_at DESC);

-- Account lookups
CREATE INDEX idx_tx_account ON transactions(account_id);

-- Category filtering
CREATE INDEX idx_tx_category ON transactions(category_id);

-- Flag status filtering (for suspicious transactions)
CREATE INDEX idx_tx_flag ON transactions(flag_status);

-- Partial index for monthly analytics (only current and future months)
-- Usage: WHERE transacted_at >= date_trunc('month', CURRENT_DATE - INTERVAL '6 months')
CREATE INDEX idx_tx_month ON transactions (user_id, date_trunc('month', transacted_at))
WHERE transacted_at >= date_trunc('month', CURRENT_DATE - INTERVAL '6 months');

-- Composite index for common filter combinations
CREATE INDEX idx_tx_user_category_date
    ON transactions(user_id, category_id, transacted_at DESC);

-- Range index for date queries
CREATE INDEX idx_tx_transacted_at ON transactions(transacted_at DESC);

-- ============================================================
-- 5. BUDGETS Table
-- ============================================================
CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    category_id SMALLINT NOT NULL
        REFERENCES categories(id) ON DELETE RESTRICT,

    month DATE NOT NULL
        CHECK (month = date_trunc('month', month))  -- enforce first-day-of-month

    -- budget limit amount
    limit_amount NUMERIC(14,2) NOT NULL
        CHECK (limit_amount > 0),

    created_at TIMESTAMPTZ DEFAULT now(),

    -- prevent duplicate budgets per user/category/month
    UNIQUE(user_id, category_id, month)
);

-- Index for budget utilization queries
CREATE INDEX idx_budgets_user_month ON budgets(user_id, month);
CREATE INDEX idx_budgets_category_month ON budgets(category_id, month);


-- ============================================================
-- 6. SAVINGS_GOALS Table
-- ============================================================
CREATE TABLE IF NOT EXISTS savings_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(80) NOT NULL,

    -- goal amount (target)
    target_amount NUMERIC(14,2) NOT NULL
        CHECK (target_amount > 0),

    -- current amount saved
    current_amount NUMERIC(14,2) DEFAULT 0
        CHECK (current_amount >= 0),

    -- auto-sweep percentage of income (0-100)
    auto_sweep_pct NUMERIC(5,2) DEFAULT 0
        CHECK (auto_sweep_pct BETWEEN 0 AND 100),

    -- optional deadline
    deadline DATE DEFAULT NULL,

    -- goal status
    status VARCHAR(15) DEFAULT 'ACTIVE'

        -- constraints for status
        CHECK (status IN ('ACTIVE', 'ACHIEVED', 'PAUSED')),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 7. TRANSFERS Table (for account-to-account transfers)
-- ============================================================
CREATE TABLE IF NOT EXISTS transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- both accounts reference the same user via foreign keys
    from_account_id UUID NOT NULL
        REFERENCES accounts(id) ON DELETE CASCADE,

    to_account_id UUID NOT NULL
        REFERENCES accounts(id) ON DELETE CASCADE,

    amount NUMERIC(14,2) NOT NULL
        CHECK (amount > 0),

    transferred_at TIMESTAMPTZ DEFAULT now(),
    notes TEXT DEFAULT NULL,

    -- constraint: cannot transfer to same account
    CONSTRAINT chk_not_same_account CHECK (from_account_id <> to_account_id),

    -- constraint: both accounts must belong to same user
    CONSTRAINT chk_same_user
        CHECK (
            (SELECT user_id FROM accounts WHERE id = from_account_id) =
            (SELECT user_id FROM accounts WHERE id = to_account_id)
        )
);

-- Index for transfer queries
CREATE INDEX idx_transfers_from_account ON transfers(from_account_id);

CREATE INDEX idx_transfers_to_account ON transfers(to_account_id);

CREATE INDEX idx_transfers_user_from_to
    ON transfers(from_account_id, to_account_id);


-- ============================================================
-- 8. AUDIT_LOGS Table
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,

    user_id UUID DEFAULT NULL,

    -- audit action
    action VARCHAR(60) NOT NULL
        -- e.g., USER_LOGIN, TX_CREATE, BUDGET_UPDATE, ADMIN_USER_ACTION
        CHECK (action IN ('USER_LOGIN', 'USER_LOGOUT', 'TX_CREATE', 'TX_UPDATE', 'TX_DELETE', 'ACCOUNT_CREATE', 'ACCOUNT_UPDATE', 'ACCOUNT_DELETE',
                          'BUDGET_CREATE', 'BUDGET_UPDATE', 'BUDGET_DELETE', 'GOAL_CREATE', 'GOAL_UPDATE', 'GOAL_DELETE',
                          'TRANSFER_CREATE', 'TRANSFER_DELETE', 'AUTH_TOKEN_GENERATE', 'AUTH_TOKEN_REFRESH',
                          'PASSWORD_CHANGE', 'ROLE_CHANGE', 'ACCOUNT_LOCK', 'USER_DELETE')),

    -- what entity changed
    entity_type VARCHAR(40) NOT NULL,
    entity_id UUID DEFAULT NULL,

    -- before/after JSONB values
    old_value JSONB DEFAULT NULL,
    new_value JSONB DEFAULT NULL,

    -- client IP (nullable)
    ip INET DEFAULT NULL,

    -- timestamp
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for audit log queries (by user, then recent first)
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);

-- Index for action-type queries
CREATE INDEX idx_audit_action ON audit_logs(action);

-- Index for entity queries
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- Index for time-range queries
CREATE INDEX idx_audit_created_at ON audit_logs(created_at DESC);

-- ============================================================
-- PASSWORD POLICY TABLE (optional, for future extension)
-- ============================================================

-- Table to track failed login attempts (for rate limiting)
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id BIGSERIAL PRIMARY KEY,
    ip INET NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    username VARCHAR(255) DEFAULT NULL,

    -- constraint: attempt within last X minutes
    CONSTRAINT chk_recent_attempt
        CHECK (created_at >= date_trunc('month', CURRENT_DATE))
);

CREATE INDEX idx_failed_login_ip ON failed_login_attempts(ip, created_at DESC);

-- Table for rate-limited actions
CREATE TABLE IF NOT EXISTS rate_limit_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID DEFAULT NULL,
    ip INET DEFAULT NULL,
    action VARCHAR(50) NOT NULL,
    count INT NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,

    -- constraint: remove old entries periodically via scheduled job
    CONSTRAINT chk_valid_window CHECK (window_end >= window_start)
);

CREATE INDEX idx_rate_limit_user_action ON rate_limit_entries(user_id, action, window_start);


-- ============================================================
-- End of schema.sql
-- See procedures.sql, views.sql, indexes.sql for additional objects
-- ============================================================