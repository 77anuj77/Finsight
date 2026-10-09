-- FinSight - PostgreSQL Indexes
-- Additional indexes for performance optimization and query planning

-- ============================================================
-- GranularIndexes for Transactions Table (complements schema.sql)
-- ============================================================

-- Composite index for filtering by user, category, and date range
-- Most common query: "Get all transactions for a user in a category with date range"
CREATE INDEX IF NOT EXISTS idx_tx_user_category_date_range
    ON transactions(user_id, category_id, transacted_at)
    WHERE transacted_at >= date_trunc('month', CURRENT_DATE - INTERVAL '6 months');

-- Index for searching transactions by flag status
CREATE INDEX IF NOT EXISTS idx_tx_flags_recent
    ON transactions(flag_status, transacted_at DESC)
    WHERE flag_status IN ('SUSPICIOUS', 'REJECTED', 'CONFIRMED');

-- Index for transactions without a payee (new payees)
CREATE INDEX IF NOT EXISTS idx_tx_no_payee
    ON transactions(user_id, transacted_at DESC)
    WHERE payee IS NULL OR payee = '';

-- Index for source type filtering
CREATE INDEX IF NOT EXISTS idx_tx_source_type
    ON transactions(source, transacted_at DESC)
    WHERE source IN ('MANUAL', 'IMPORT', 'AUTO');

-- Index for transaction type filtering by user and month
CREATE INDEX IF NOT EXISTS idx_tx_month_user_type
    ON transactions(date_trunc('month', transacted_at), user_id, type)
    WHERE transacted_at >= date_trunc('month', CURRENT_DATE - INTERVAL '3 months');


-- ============================================================
-- Indexes for Accounts Table
-- ============================================================

-- Composite index for user account inventory queries
CREATE INDEX IF NOT EXISTS idx_accounts_user_type_active
    ON accounts(user_id, type, is_active);

-- Index for balance lookups (account equity valutation)
CREATE INDEX IF NOT EXISTS idx_accounts_user_balance
    ON accounts(user_id, balance DESC);

-- Index for account name search
CREATE INDEX IF NOT EXISTS idx_accounts_user_name
    ON accounts(user_id, LOWER(name));


-- ============================================================
-- Indexes for Budgets Table
-- ============================================================

-- Composite index for budget vs actual queries per month
CREATE INDEX IF NOT EXISTS idx_budgets_month_utilization
    ON budgets(month DESC, user_id)
    WHERE month >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '6 months'));

-- Index for budget expiration warnings
CREATE INDEX IF NOT EXISTS idx_budgets_month_deadline
    ON budgets(deadline, status)
    WHERE deadline BETWEEN (NOW() - INTERVAL '30 days') AND (NOW() + INTERVAL '12 months');


-- ============================================================
-- Indexes for Savings Goals Table
-- ============================================================

-- Index for goal tracking by status
CREATE INDEX IF NOT EXISTS idx_savings_goals_user_status_deadline
    ON savings_goals(user_id, status, deadline DESC)
    WHERE status = 'ACTIVE';

-- Index for active goals sorted by completion percentage
CREATE INDEX IF NOT EXISTS idx_savings_goals_user_completion
    ON savings_goals(user_id, (current_amount::FLOAT / target_amount * 100) DESC);


-- ============================================================
-- Indexes for Transfers Table
-- ============================================================

-- Index for transfer history queries by source and destination
CREATE INDEX IF NOT EXISTS idx_transfers_user_accounts
    ON transfers(from_account_id, to_account_id);

-- Index for transfer velocity analysis (recent transfers)
CREATE INDEX IF NOT EXISTS idx_transfers_created_at_user_id
    ON transfers(user_id, from_account_id, created_at DESC)
    WHERE created_at >= NOW() - INTERVAL '1 month';


-- ============================================================
-- Indexes for Audit Logs Table
-- ============================================================

-- Composite index for user audit trail
CREATE INDEX IF NOT EXISTS idx_audit_user_datetime
    ON audit_logs(user_id, created_at DESC);

-- Index for action type statistics
CREATE INDEX IF NOT EXISTS idx_audit_action_datetime
    ON audit_logs(action, created_at DESC)
    WHERE created_at >= date_trunc('month', CURRENT_DATE);

-- Index for IP-based security monitoring
CREATE INDEX IF NOT EXISTS idx_audit_ip
    ON audit_logs(ip, created_at DESC)
    WHERE created_at >= NOW() - INTERVAL '7 days';


-- ============================================================
-- Partial Indexes for Analytics Queries
-- ============================================================

-- Transaction analytics for current month only (reduces vertex queries)
CREATE INDEX IF NOT EXISTS idx_tx_analytics_month
    ON transactions(user_id, date_trunc('month', transacted_at), transacted_at DESC)
    WHERE transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '6 months'));

-- Transactions flagged for review (performance for fraud detection)
CREATE INDEX IF NOT EXISTS idx_tx_fraud_review
    ON transactions(user_id, flag_status, transacted_at DESC)
    WHERE flag_status IN ('SUSPICIOUS', 'REJECTED', 'CONFIRMED');

-- High-value transactions for income/expense analysis
CREATE INDEX IF NOT EXISTS idx_tx_high_value
    ON transactions(user_id, amount, transacted_at DESC)
    WHERE amount > 1000
      AND transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '12 months'));

-- Category-specific transaction history (aggregation)
CREATE INDEX IF NOT EXISTS idx_tx_category_month
    ON transactions(category_id, date_trunc('month', transacted_at), amount DESC);


-- ============================================================
-- Indexes for User Statistics (Materialized Views)
-- ============================================================

-- Materialized view for fast monthly rollups
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_users AS
SELECT
    t.user_id,
    date_trunc('month', t.transacted_at) AS month_key,
    COUNT(*) AS txn_count,
    SUM(CASE WHEN t.type = 'INCOME' THEN t.amount ELSE 0 END) AS income_amt,
    SUM(CASE WHEN t.type = 'EXPENSE' THEN t.amount ELSE 0 END) AS expense_amt,
    SUM(CASE WHEN t.type = 'TRANSFER' THEN t.amount ELSE 0 END) AS transfers_amt
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.is_active = true
GROUP BY t.user_id, date_trunc('month', t.transacted_at);

-- Materialized view refresh schedule (auto-refresh for analytics)
CREATE OR REPLACE FUNCTION refresh_mv_monthly_users()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_users;
END;
$$ LANGUAGE plpgsql;

-- Trigger to refresh on high volume (optional)
-- CREATE EVENT TRIGGER mv_on_commit
--     AFTER INSERT OR UPDATE OR DELETE ON transactions
--     EXECUTE PROCEDURE refresh_mv_monthly_users();


-- ============================================================
-- Indexes for Performance Monitoring
-- ============================================================

-- Query plan hint for indexed queries
-- EXPLAIN ANALYZE SELECT * FROM transactions
-- JOIN accounts ON transactions.account_id = accounts.id
-- WHERE accounts.user_id = 'uuid'
-- AND transactions.transacted_at >= date_trunc('day', NOW() - INTERVAL '30 days');

-- Statistics update suggestion for PostgreSQL autovacuum
-- VACUUM ANALYZE transactions;
-- VACUUM ANALYZE accounts;
-- VACUUM ANALYZE audit_logs;


-- ============================================================
-- End of indexes.sql
-- ============================================================