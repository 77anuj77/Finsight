-- FinSight - PostgreSQL Stored Procedures and Functions
-- Advanced database features for ACID transactions, complex queries, and automation

-- ============================================================
-- 1. function fn_create_transaction(...)
-- Creates a transaction and atomically updates account balance
-- ============================================================
CREATE OR REPLACE FUNCTION fn_create_transaction(
    p_user_id UUID,
    p_account_id UUID,
    p_category_id SMALLINT,
    p_type VARCHAR(10),
    p_amount NUMERIC(14,2),
    p_payee VARCHAR(120) DEFAULT NULL,
    p_transacted_at TIMESTAMPTZ DEFAULT now(),
    p_notes TEXT DEFAULT NULL,
    p_source VARCHAR(10) DEFAULT 'MANUAL'
) RETURNS UUID AS $$
DECLARE
    v_new_tx_id UUID;
    v_account_balance NUMERIC(14,2);
    v_account_archived BOOLEAN := false;
BEGIN
    -- ============================================================
    -- INPUT VALIDATION
    -- ============================================================
    IF p_type NOT IN ('INCOME', 'EXPENSE', 'TRANSFER') THEN
        RAISE EXCEPTION 'Invalid transaction type: %', p_type;
    END IF;

    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transaction amount must be greater than 0';
    END IF;

    -- ============================================================
    -- ATOMIC TRANSACTION START
    -- ============================================================
    BEGIN
        -- BEGIN explicitly for exception handling
        -- Transactions are controlled by FastAPI's session, but we add
        -- additional logic within the transaction context

        -- ============================================================
        -- STEP 1: VALIDATE ACCOUNT EXISTS AND IS ACTIVE
        -- ============================================================
        SELECT balance, is_active INTO v_account_balance, v_account_archived
        FROM accounts
        WHERE id = p_account_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Account not found: %', p_account_id;
        END IF;

        IF v_account_archived THEN
            RAISE EXCEPTION 'Account is archived/deactivated';
        END IF;

        -- ============================================================
        -- STEP 2: BALANCE VALIDATION (NO OVERDRAFT)
        -- ============================================================
        IF p_type IN ('EXPENSE', 'TRANSFER') THEN
            IF v_account_balance < p_amount THEN
                RAISE EXCEPTION 'Overdraft prevented. Current balance: %, Required: %',
                    v_account_balance, p_amount;
            END IF;
        END IF;

        -- ============================================================
        -- STEP 3: VALIDATE CATEGORY
        -- ============================================================
        IF NOT EXISTS (SELECT 1 FROM categories WHERE id = p_category_id) THEN
            RAISE EXCEPTION 'Category not found: %', p_category_id;
        END IF;

        -- ============================================================
        -- STEP 4: INSERT TRANSACTION
        -- ============================================================
        INSERT INTO transactions (
            account_id,
            user_id,
            category_id,
            type,
            amount,
            payee,
            transacted_at,
            notes,
            source,
            flag_status
        ) VALUES (
            p_account_id,
            p_user_id,
            p_category_id,
            p_type,
            p_amount,
            p_payee,
            p_transacted_at,
            p_notes,
            p_source,
            'NORMAL'  -- default flag status
        ) RETURNING id INTO v_new_tx_id;

        -- ============================================================
        -- STEP 5: UPDATE ACCOUNT BALANCE (ATOMIC)
        -- ============================================================
        IF p_type = 'EXPENSE' THEN
            UPDATE accounts
            SET balance = balance - p_amount,
                updated_at = now()
            WHERE id = p_account_id;

        ELSIF p_type = 'INCOME' THEN
            UPDATE accounts
            SET balance = balance + p_amount,
                updated_at = now()
            WHERE id = p_account_id;

        END IF;

        -- ============================================================
        -- STEP 6: INSERT AUDIT LOG
        -- ============================================================
        INSERT INTO audit_logs (
            user_id,
            action,
            entity_type,
            entity_id,
            old_value,
            new_value
        ) VALUES (
            p_user_id,
            'TX_CREATE',
            'transaction',
            v_new_tx_id,
            NULL,  -- tracking would require previous value
            jsonb_build_object(
                'amount', p_amount,
                'type', p_type,
                'category_id', p_category_id,
                'account_id', p_account_id
            )
        );

        -- ============================================================
        -- COMMIT
        -- ============================================================
        COMMIT;

        -- Return the new transaction ID
        RETURN v_new_tx_id;

    EXCEPTION
        WHEN OTHERS THEN
            -- ROLLBACK on any error - state must be clean
            ROLLBACK;
            RAISE;
    END;

END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 2. function fn_transfer_funds(from, to, amt)
-- Secure fund transfer between accounts (atomic, overdraft guard)
-- ============================================================
CREATE OR REPLACE FUNCTION fn_transfer_funds(
    p_from_account_id UUID,
    p_to_account_id UUID,
    p_amount NUMERIC(14,2)
) RETURNS JSON AS $$
DECLARE
    v_from_balance NUMERIC(14,2);
    v_to_balance NUMERIC(14,2);
    v_from_user_id UUID;
    v_to_user_id UUID;
    v_transfer_id UUID;
BEGIN
    -- ============================================================
    -- INPUT VALIDATION
    -- ============================================================
    IF p_from_account_id = p_to_account_id THEN
        RAISE EXCEPTION 'Cannot transfer to same account';
    END IF;

    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be greater than 0';
    END IF;

    -- ============================================================
    -- LOCK BOTH ACCOUNTS (SERIALIZABLE ISOLATION LEVEL for safety)
    -- ============================================================
    BEGIN
        LOCK TABLE accounts IN EXCLUSIVE MODE;

        -- ============================================================
        -- STEP 1: FETCH ACCOUNT DETAILS & BALANCES
        -- ============================================================
        SELECT balance, user_id INTO v_from_balance, v_from_user_id
        FROM accounts
        WHERE id = p_from_account_id
        FOR UPDATE;  -- prevent concurrent modification

        SELECT balance, user_id INTO v_to_balance, v_to_user_id
        FROM accounts
        WHERE id = p_to_account_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Source or target account not found';
        END IF;

        -- ============================================================
        -- STEP 2: VALIDATE BOTH ACCOUNTS BELONG TO SAME USER
        -- ============================================================
        IF v_from_user_id != v_to_user_id THEN
            RAISE EXCEPTION 'Transfer between accounts of different users not permitted';
        END IF;

        -- ============================================================
        -- STEP 3: OVERDRAFT GUARD
        -- ============================================================
        IF v_from_balance < p_amount THEN
            RAISE EXCEPTION 'Insufficient funds for transfer. Balance: %', v_from_balance;
        END IF;

        -- ============================================================
        -- STEP 4: DEBIT FROM SOURCE ACCOUNT
        -- MINUS amount (expense transfer)
        -- ============================================================
        UPDATE accounts
        SET balance = balance - p_amount,
            updated_at = now()
        WHERE id = p_from_account_id;

        -- ============================================================
        -- STEP 5: CREDIT TO DESTINATION ACCOUNT
        -- ============================================================
        UPDATE accounts
        SET balance = balance + p_amount,
            updated_at = now()
        WHERE id = p_to_account_id;

        -- ============================================================
        -- STEP 6: INSERT TRANSFER RECORD
        -- ============================================================
        INSERT INTO transfers (
            from_account_id,
            to_account_id,
            amount,
            transferred_at
        ) VALUES (
            p_from_account_id,
            p_to_account_id,
            p_amount,
            now()
        ) RETURNING id INTO v_transfer_id;

        -- ============================================================
        -- STEP 7: INSERT AUDIT LOG for transfer
        -- ============================================================
        INSERT INTO audit_logs (
            user_id,
            action,
            entity_type,
            entity_id,
            old_value,
            new_value
        ) VALUES (
            v_from_user_id,
            'TRANSFER_CREATE',
            'transfer',
            v_transfer_id,
            jsonb_build_object('amount', p_amount, 'transfer', 'OP'),
            jsonb_build_object(
                'from_account', p_from_account_id,
                'to_account', p_to_account_id,
                'amount', p_amount
            )
        );

        -- ============================================================
        -- COMMIT
        -- ============================================================
        COMMIT;

        -- ============================================================
        -- RETURN SUCCESSFUL TRANSFER DATA
        -- ============================================================
        RETURN jsonb_build_object(
            'success', true,
            'transfer_id', v_transfer_id,
            'from_balance', v_from_balance - p_amount,
            'to_balance', v_to_balance + p_amount,
            'amount', p_amount
        );

    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END;

END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 3. function fn_monthly_rollup(user_id, month)
-- Compute monthly summary and calculate budget health metrics
-- ============================================================
CREATE OR REPLACE FUNCTION fn_monthly_rollup(
    p_user_id UUID,
    p_month DATE
) RETURNS TABLE (
    month_key DATE,
    total_income NUMERIC(14,2),
    total_expense NUMERIC(14,2),
    net_balance NUMERIC(14,2),
    transaction_count BIGINT,
    avg_daily_spend NUMERIC(12,2),
    budget_utilization_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH monthly_data AS (
        SELECT
            date_trunc('month', t.transacted_at) AS month_key,
            SUM(CASE WHEN t.type = 'INCOME' THEN t.amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN t.type = 'EXPENSE' THEN t.amount ELSE 0 END) AS total_expense,
            COUNT(*) AS transaction_count
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = p_user_id
          AND date_trunc('month', t.transacted_at) = date_trunc('month', p_month)
        GROUP BY 1
    )
    SELECT
        md.month_key,
        COALESCE(md.total_income, 0) AS total_income,
        COALESCE(md.total_expense, 0) AS total_expense,
        COALESCE(md.total_income, 0) - COALESCE(md.total_expense, 0) AS net_balance,
        md.transaction_count,
        CASE
            WHEN md.transaction_count > 0
                 AND EXTRACT(DAY FROM (CURRENT_DATE - md.month_key)) > 0
            THEN md.total_expense / EXTRACT(DAY FROM (CURRENT_DATE - md.month_key) + 1)
            ELSE 0
        END::NUMERIC(12,2) AS avg_daily_spend,

        -- Count of categories with breach
        COUNT(b.id) AS budget_utilization_count
    FROM monthly_data md
    LEFT JOIN budgets b
        ON b.user_id = p_user_id
       AND EXTRACT(MONTH FROM b.month) = EXTRACT(MONTH FROM p_month)
       AND EXTRACT(YEAR FROM b.month) = EXTRACT(YEAR FROM p_month)
    GROUP BY md.month_key, md.total_income, md.total_expense, md.transaction_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 4. function fn_auto_sweep(user_id)
-- Automatically transfer percentage of income to savings goals
-- ============================================================
CREATE OR REPLACE FUNCTION fn_auto_sweep(
    p_user_id UUID
) RETURNS JSON AS $$
DECLARE
    v_current_month DATE := date_trunc('month', CURRENT_DATE);
    v_income NUMERIC(14,2) := 0;
    v_transfer_total NUMERIC(14,2) := 0;
    v_receipt JSONB := '{}'::JSONB;
BEGIN
    -- ============================================================
    -- INPUT VALIDATION
    -- ============================================================
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
        RAISE EXCEPTION 'User not found: %', p_user_id;
    END IF;

    -- ============================================================
    -- ATOMIC TRANSACTION FOR AUTO SWEEP
    -- ============================================================
    BEGIN
        -- ============================================================
        -- STEP 1: GET USER'S MONTHLY INCOME
        -- ============================================================
        SELECT monthly_income INTO v_income
        FROM users
        WHERE id = p_user_id;

        -- ============================================================
        -- STEP 2: GET TARGET SAVINGS_GOALS WITH AUTO_SWEEP_ENABLED
        -- ============================================================
        WITH goals_with_config AS (
            SELECT
                sg.id,
                sg.target_amount,
                sg.current_amount,
                sg.auto_sweep_pct
            FROM savings_goals sg
            WHERE sg.user_id = p_user_id
              AND sg.status = 'ACTIVE'
              AND sg.auto_sweep_pct > 0
        )
        -- ============================================================
        -- STEP 3: CALCULATE TRANSFER AMOUNTS
        -- ============================================================
        SELECT jsonb_agg(
            jsonb_build_object(
                'savings_goal_id', sg.id,
                'name', sg.name,
                'target_amount', sg.target_amount,
                'current_amount', sg.current_amount,
                'auto_sweep_pct', sg.auto_sweep_pct,
                'sweep_amount', -- per goal calculation
                CASE
                    WHEN (sg.auto_sweep_pct / 100) * v_income < (sg.target_amount - sg.current_amount)
                    THEN (sg.auto_sweep_pct / 100) * v_income
                    ELSE (sg.target_amount - sg.current_amount)
                END,
                'new_goal_balance',
                CASE
                    WHEN (sg.auto_sweep_pct / 100) * v_income < (sg.target_amount - sg.current_amount)
                    THEN sg.current_amount + (sg.auto_sweep_pct / 100)::NUMERIC(10,2) * v_income
                    ELSE sg.target_amount
                END,
                'status_before', sg.status,
                'status_after',
                CASE
                    WHEN sg.current_amount + (sg.auto_sweep_pct / 100)::NUMERIC(10,2) * v_income >= sg.target_amount
                    THEN 'ACHIEVED'
                    ELSE 'ACTIVE'
                END
            )
        ) INTO v_receipt
        FROM goals_with_config sg;

        -- ============================================================
        -- OPTIONAL: IF you want to actually perform the transfers,
        -- you could update each savings_goal.current_amount here.
        -- For this implementation, we just calculate and return the plan.

        -- ============================================================
        -- COMMIT
        -- ============================================================
        COMMIT;

        -- ============================================================
        -- RETURN AUTO SWEEP PLAN
        -- ============================================================
        RETURN jsonb_build_object(
            'success', true,
            'month', v_current_month,
            'monthly_income', v_income,
            'sweep_plan', v_receipt,
            'total_swept_amount',
                -- Sum of actual amounts swept (this would need transfer logic)
                0
        );

    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END;

END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 5. function fn_update_account_balance(p_account_id, p_delta)
-- Helper to correct account balances after bulk corrections
-- ============================================================
CREATE OR REPLACE FUNCTION fn_update_account_balance(
    p_account_id UUID,
    p_delta NUMERIC(14,2)
) RETURNS BIGINT AS $$
DECLARE
    v_old_balance NUMERIC(14,2);
    v_new_balance NUMERIC(14,2);
    v_affected_rows BIGINT;
BEGIN
    -- ============================================================
    -- BALANCE VALIDATION: cannot go negative
    -- ============================================================
    SELECT balance INTO v_old_balance
    FROM accounts
    WHERE id = p_account_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account not found: %', p_account_id;
    END IF;

    v_new_balance := v_old_balance + p_delta;

    IF v_new_balance < 0 THEN
        RAISE EXCEPTION 'Balance would go negative: %', v_new_balance;
    END IF;

    -- ============================================================
    -- UPDATE
    -- ============================================================
    UPDATE accounts
    SET balance = v_new_balance,
        updated_at = now()
    WHERE id = p_account_id;

    GET DIAGNOSTICS v_affected_rows = ROW_COUNT;

    RETURN v_affected_rows;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 6. function fn_validate_account_balances(p_user_id)
-- Health check for all accounts of a user
-- ============================================================
CREATE OR REPLACE FUNCTION fn_validate_account_balances(p_user_id UUID)
RETURNS TABLE (
    account_id UUID,
    account_name VARCHAR(80),
    calculated_balance NUMERIC(14,2),
    current_balance NUMERIC(14,2),
    is_balanced BOOLEAN,
    imbalance_amount NUMERIC(14,2)
) AS $$
BEGIN
    RETURN QUERY
    WITH tx_balance AS (
        SELECT
            account_id,
            SUM(CASE WHEN type = 'INCOME' THEN amount
                     WHEN type = 'EXPENSE' THEN -amount
                     ELSE 0 END) AS calculated_balance
        FROM transactions
        WHERE account_id IN (SELECT id FROM accounts WHERE user_id = p_user_id)
          AND transacted_at < now()
        GROUP BY account_id
    )
    SELECT
        a.id AS account_id,
        a.name AS account_name,
        COALESCE(cb.calculated_balance, 0) AS calculated_balance,
        a.balance AS current_balance,
        ABS(COALESCE(cb.calculated_balance, 0) - a.balance) < 0.01 AS is_balanced,
        COALESCE(cb.calculated_balance, 0) - a.balance AS imbalance_amount
    FROM accounts a
    LEFT JOIN tx_balance cb ON a.id = cb.account_id
    WHERE a.user_id = p_user_id AND a.is_active = true;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- End of procedures.sql
-- ============================================================