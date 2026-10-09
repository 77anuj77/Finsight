-- FinSight - PostgreSQL Views for Analytics & Reporting
-- Advanced SQL queries: joins, aggregations, window functions, CTEs

-- ============================================================
-- View: v_monthly_summary
-- Per user/month summary: income, expense, savings, net balance
-- ============================================================
CREATE OR REPLACE VIEW v_monthly_summary AS
SELECT
    t.user_id,
    date_trunc('month', t.transacted_at) AS month_key,
    COUNT(*) AS transaction_count,

    -- Income totals
    SUM(CASE WHEN t.type = 'INCOME' THEN t.amount ELSE 0 END) AS total_income,

    -- Expense totals
    SUM(CASE WHEN t.type = 'EXPENSE' THEN t.amount ELSE 0 END) AS total_expense,

    -- Transfer totals (entrances + exits)
    SUM(CASE WHEN t.type = 'TRANSFER' THEN t.amount ELSE 0 END) AS total_transfers,

    -- Net balance (income - expenses + transfers)
    (SUM(CASE WHEN t.type = 'INCOME' THEN t.amount
              WHEN t.type = 'EXPENSE' THEN -t.amount
              WHEN t.type = 'TRANSFER' THEN 0 END)
    ) AS net_balance,

    -- Average daily spend (for breach prediction)
    (SUM(CASE WHEN t.type = 'EXPENSE' AND transacted_at >= date_trunc('month', NOW())
                 THEN t.amount ELSE 0 END)::NUMERIC(14,2) /
       NULLIF(EXTRACT(DAY FROM (NOW() - date_trunc('month', NOW()))), 0)
    ) AS avg_daily_spend

    -- Note: Jul relieve transfers balance calculation
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '5' MONTH))
GROUP BY t.user_id, date_trunc('month', t.transacted_at);


-- ============================================================
-- View: v_budget_vs_actual
-- Budget utilization % and breach status per category/month
-- ============================================================
CREATE OR REPLACE VIEW v_budget_vs_actual AS
WITH monthly_expenses AS (
    SELECT
        t.user_id,
        t.category_id,
        date_trunc('month', t.transacted_at) AS month_key,
        SUM(t.amount) AS total_expense
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE t.type = 'EXPENSE'
      AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '5' MONTH))
    GROUP BY 1, 2, 3
),
budgets AS (
    SELECT
        b.user_id,
        b.category_id,
        b.month AS month_key,
        b.limit_amount
    FROM budgets b
    WHERE b.month >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '5' MONTH))
)
SELECT
    b.user_id,
    b.category_id,
    b.month_key,
    b.limit_amount AS budget_limit,
    e.total_expense AS actual_spend,
    CASE
        WHEN e.total_expense IS NULL THEN 0
        WHEN b.limit_amount = 0 THEN 100
        ELSE (e.total_expense / b.limit_amount) * 100
    END AS utilization_pct,
    CASE
        WHEN e.total_expense > b.limit_amount THEN 'BREACHED'
        WHEN e.total_expense > b.limit_amount * 0.8 THEN 'WARNING'
        WHEN e.total_expense > 0 THEN 'ON_TRACK'
        ELSE 'NO_BUDGET'
    END AS status,
    CASE
        WHEN e.total_expense IS NULL THEN 0
        WHEN b.limit_amount = 0 THEN 0
        ELSE (e.total_expense - b.limit_amount)
    END AS variance
FROM budgets b
LEFT JOIN monthly_expenses e ON
    b.user_id = e.user_id
    AND b.category_id = e.category_id
    AND b.month_key = e.month_key
WHERE b.limit_amount > 0;


-- ============================================================
-- View: v_top_payees
-- Highest spending categories based on payee displays
-- ============================================================
CREATE OR REPLACE VIEW v_top_payees AS
WITH payee_totals AS (
    SELECT
        t.user_id,
        t.payee,
        t.category_id,
        SUM(t.amount) AS total_amount,
        COUNT(*) AS transaction_count
    FROM transactions t
    WHERE t.type = 'EXPENSE'
      AND t.flag_status != 'REJECTED'
      AND t.payee IS NOT NULL
      AND t.payee != ''
      AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '5' MONTH))
    GROUP BY 1, 2, 3
),
category_averages AS (
    SELECT
        t.user_id,
        c.name AS category_name,
        c.id AS category_id,
        AVG(t.amount) AS avg_category_amount,
        SUM(t.amount) AS total_category_amount
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    WHERE t.type = 'EXPENSE'
      AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '5' MONTH))
    GROUP BY 1, 2, 3
)
SELECT
    pt.user_id,
    c.name AS category_name,
    c.id AS category_id,
    pt.payee AS payee_name,
    pt.total_amount AS total_spent,
    pt.transaction_count,
    ROUND((pt.total_amount / NULLIF(ca.avg_category_amount, 0)) * 100, 2) AS category_utilization_pct,
    pt.payee
FROM payee_totals pt
JOIN category_averages ca
    ON pt.user_id = ca.user_id
   AND pt.category_id = ca.category_id
ORDER BY
    pt.user_id,
    pt.total_amount DESC;


-- ============================================================
-- View: v_account_summary
-- Summary of all accounts for net worth calculation
-- ============================================================
CREATE OR REPLACE VIEW v_account_summary AS
SELECT
    a.user_id,
    COUNT(*) AS total_accounts,
    SUM(a.balance) AS total_net_worth,
    SUM(CASE WHEN a.type = 'BANK' THEN a.balance ELSE 0 END) AS total_bank_balance,
    SUM(CASE WHEN a.type = 'CASH' THEN a.balance ELSE 0 END) AS total_cash_balance,
    SUM(CASE WHEN a.type = 'UPI' THEN a.balance ELSE 0 END) AS total_upi_balance,
    SUM(CASE WHEN a.type = 'CARD' THEN a.balance ELSE 0 END) AS total_card_balance,
    AVG(a.balance) AS avg_account_balance
FROM accounts a
WHERE a.is_active = true
GROUP BY a.user_id;


-- ============================================================
-- View: v_savings_goal_progress
-- Progress toward savings goals with percentage completion
-- ============================================================
CREATE OR REPLACE VIEW v_savings_goal_progress AS
SELECT
    sg.user_id,
    sg.name AS goal_name,
    sg.target_amount,
    sg.current_amount,
    sg.auto_sweep_pct,
    sg.deadline,
    sg.status,
    ROUND(((sg.current_amount::FLOAT / sg.target_amount) * 100), 2) AS progress_pct,
    CASE
        WHEN sg.current_amount >= sg.target_amount THEN 'ACHIEVED'
        WHEN sg.deadline < CURRENT_DATE AND sg.status = 'ACTIVE' THEN 'OVERDUE'
        WHEN sg.deadline < CURRENT_DATE + INTERVAL '30 days' THEN 'WEEKS_REMAINING'
        ELSE 'ACTIVE'
    END AS goal_status_category,
    (sg.target_amount - sg.current_amount) AS remaining_amount,
    CASE
        WHEN sg.auto_sweep_pct > 0 AND sg.status = 'ACTIVE' THEN TRUE
        ELSE FALSE
    END AS auto_sweep_enabled
FROM savings_goals sg
WHERE sg.status IN ('ACTIVE', 'ACHIEVED');


-- ============================================================
-- View: v_transaction_flags
-- List of all suspicious transactions that need review
-- ============================================================
CREATE OR REPLACE VIEW v_transaction_flags AS
SELECT
    t.id,
    t.user_id,
    t.account_id,
    t.type,
    t.amount,
    t.transacted_at,
    c.name AS category_name,
    t.payee,
    t.notes,
    t.flag_status,
    t.source,
    -- Risk score calculation (rule-based)
    CASE
        WHEN t.flag_status IN ('SUSPICIOUS', 'REJECTED', 'CONFIRMED') THEN 100
        WHEN t.amount > 10000 THEN 70
        WHEN t.payee IS NULL OR t.payee = '' THEN 80
        WHEN t.transacted_at > NOW() - INTERVAL '2 hours' THEN 65
        ELSE 30
    END AS risk_score_formatted
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.flag_status IN ('NORMAL', 'SUSPICIOUS', 'CONFIRMED', 'REJECTED')
  AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '1' MONTH))
ORDER BY
    t.flag_status ASC,
    t.transacted_at DESC;


-- ============================================================
-- View: v_dashboard_stats (consolidated for frontend)
-- Single aggregated view for dashboards
-- ============================================================
CREATE OR REPLACE VIEW v_dashboard_stats AS
WITH user_transactions AS (
    SELECT
        t.user_id,
        COUNT(*) AS total_transactions,
        SUM(CASE WHEN t.type = 'INCOME' THEN t.amount ELSE 0 END) AS total_income,
        SUM(CASE WHEN t.type = 'EXPENSE' THEN t.amount ELSE 0 END) AS total_expense,
        SUM(CASE WHEN t.type = 'TRANSFER' THEN t.amount ELSE 0 END) AS total_transfers,
        (SUM(CASE WHEN t.type = 'INCOME' THEN t.amount
                  WHEN t.type = 'EXPENSE' THEN -t.amount
                  ELSE 0 END)) AS net_balance
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.user_id = current_setting('app.current_user_id', TRUE)::UUID
      AND t.transacted_at >= date_trunc('month', NOW())
    GROUP BY t.user_id
),
user_budgets AS (
    SELECT
        b.user_id,
        COUNT(*) AS total_budgets,
        SUM(b.limit_amount) AS total_budget_limit
    FROM budgets b
    WHERE b.user_id = current_setting('app.current_user_id', TRUE)::UUID
      AND b.month >= date_trunc('month', NOW())
    GROUP BY b.user_id
),
monthly_summary AS (
    SELECT
        t.user_id,
        AVG(t.amount) AS avg_transaction_amount,
        MAX(t.amount) AS max_transaction_amount
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.user_id = current_setting('app.current_user_id', TRUE)::UUID
      AND t.transacted_at >= date_trunc('month', NOW())
    GROUP BY t.user_id
)
SELECT
    ut.user_id,
    COALESCE(ut.total_transactions, 0) AS transaction_count,
    COALESCE(ut.total_income, 0) AS income_this_month,
    COALESCE(ut.total_expense, 0) AS expense_this_month,
    COALESCE(ut.net_balance, 0) AS net_balance_this_month,
    COALESCE(ub.total_budgets, 0) AS budget_count,
    COALESCE(ub.total_budget_limit, 0) AS total_budget_limit,
    COALESCE(ms.avg_transaction_amount, 0) AS avg_transaction_value
FROM user_transactions ut
LEFT JOIN user_budgets ub ON ut.user_id = ub.user_id
LEFT JOIN monthly_summary ms ON ut.user_id = ms.user_id;


-- ============================================================
-- View: v_anomaly_high_value_txns
-- Transactions significantly above user's historical average
-- ============================================================
CREATE OR REPLACE VIEW v_anomaly_high_value_txns AS
WITH user_stats AS (
    SELECT
        t.user_id,
        AVG(t.amount) AS avg_amount,
        STDDEV(t.amount) AS std_amount
    FROM transactions t
    WHERE t.type IN ('EXPENSE', 'TRANSFER')
      AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '3' MONTH))
    GROUP BY t.user_id
)
SELECT
    t.*,
    (u.avg_amount + (u.std_amount * 3)) AS anomaly_threshold,
    CASE
        WHEN t.amount > (u.avg_amount + (u.std_amount * 3)) THEN TRUE
        ELSE FALSE
    END AS is_anomaly
FROM transactions t
JOIN user_stats u ON t.user_id = u.user_id
WHERE t.amount > 0
  AND t.transacted_at >= date_trunc('month', DATE_SUB(NOW(), INTERVAL '1' MONTH))
ORDER BY t.amount DESC;


-- ============================================================
-- End of views.sql
-- ============================================================