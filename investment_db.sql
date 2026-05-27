-- 1. Create Brinson Attribution View
CREATE VIEW view_brinson_attribution AS
WITH base_data AS (
    SELECT
        h.date,
        a.sector,
        h.weight_portfolio AS w_p,
        m.daily_return AS r_p,
        -- Dynamically calculate benchmark return (SPY)
        (SELECT daily_return FROM fact_marketdata
         WHERE security_id = 'SPY_INDEX' AND valuation_date = h.date) AS r_b_total
    FROM fact_holdings h
    JOIN fact_marketdata m ON h.date = m.valuation_date AND h.ticker = m.security_id
    JOIN dim_assets a ON h.ticker = a.ticker
),
sector_agg AS (
    SELECT
        date,
        sector,
        SUM(w_p) AS w_p_s,
        SUM(w_p * r_p) / NULLIF(SUM(w_p), 0) AS r_p_s,
        MAX(r_b_total) AS r_b_s,
        -- Here you can adjust the benchmark weight w_b_s based on actual business logic
        -- Temporarily set to 1 / total number of sectors, or join a benchmark components table
        0.25 AS w_b_s
    FROM base_data
    GROUP BY date, sector
)
SELECT *,
    (w_p_s - w_b_s) * r_b_s AS allocation_effect,
    w_b_s * (r_p_s - r_b_s) AS selection_effect,
    (w_p_s * r_p_s) - (w_b_s * r_b_s) AS total_excess_return
FROM sector_agg;


----------------------------------------------------------------------------------------------------------
-- 2. Create Risk Metrics and Peer Comparison View
CREATE OR REPLACE VIEW view_performance_risk_metrics AS
WITH daily_port_ret AS (
    -- Step 1: Calculate daily portfolio returns (includes only your holdings)
    SELECT
        h.date,
        SUM(h.weight_portfolio * m.daily_return) AS port_ret
    FROM fact_holdings h
    JOIN fact_marketdata m ON h.date = m.valuation_date AND h.ticker = m.security_id
    GROUP BY h.date
),
daily_bench_peer AS (
    -- Step 2: Extract daily returns for benchmark and peers (directly from market data)
    SELECT
        valuation_date AS date,
        MAX(CASE WHEN security_id = 'SPY_INDEX' THEN daily_return END) AS bench_ret,
        MAX(CASE WHEN security_id = 'QQQ_PEER' THEN daily_return END) AS qqq_ret,
        MAX(CASE WHEN security_id = 'IVV_PEER' THEN daily_return END) AS ivv_ret
    FROM fact_marketdata
    GROUP BY valuation_date
)
-- Step 3: Align portfolio returns with benchmark/peer returns by date
SELECT
    p.date,
    p.port_ret,
    b.bench_ret,
    b.qqq_ret,
    b.ivv_ret,
    -- Calculate rolling annualized return (past 252 days)
    AVG(p.port_ret) OVER (ORDER BY p.date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) * 252 AS ann_port_ret,
    -- Calculate rolling volatility
    STDDEV(p.port_ret) OVER (ORDER BY p.date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) * SQRT(252) AS volatility
FROM daily_port_ret p
LEFT JOIN daily_bench_peer b ON p.date = b.date;