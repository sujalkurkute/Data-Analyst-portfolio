-- Table: txns(txn_id, txn_ts, bank, txn_type, device, user_id, amount, status, is_fraud)

-- Q1. Failure rate by bank, ranked (window function)
SELECT bank, COUNT(*) AS txns,
       ROUND(100.0*SUM(status='FAILED')/COUNT(*),2) AS fail_pct,
       RANK() OVER (ORDER BY 1.0*SUM(status='FAILED')/COUNT(*) DESC) AS fail_rank
FROM txns GROUP BY bank;

-- Q2. Hourly failure profile (find peak-hour congestion)
SELECT CAST(strftime('%H', txn_ts) AS INT) AS hr, COUNT(*) AS txns,
       ROUND(100.0*SUM(status='FAILED')/COUNT(*),2) AS fail_pct
FROM txns GROUP BY hr ORDER BY hr;

-- Q3. Month-over-month volume and growth (CTE + LAG)
WITH m AS (
  SELECT strftime('%Y-%m', txn_ts) AS ym, COUNT(*) AS txns, SUM(amount) AS value
  FROM txns GROUP BY ym)
SELECT ym, txns, ROUND(value,0) AS value,
       ROUND(100.0*(txns - LAG(txns) OVER (ORDER BY ym))/LAG(txns) OVER (ORDER BY ym),2) AS mom_growth_pct
FROM m;

-- Q4. Fraud rate by txn type and amount band
SELECT txn_type,
       CASE WHEN amount<1000 THEN '<1k' WHEN amount<20000 THEN '1k-20k' ELSE '20k+' END AS band,
       COUNT(*) AS txns, SUM(is_fraud) AS fraud,
       ROUND(100.0*SUM(is_fraud)/COUNT(*),3) AS fraud_pct
FROM txns WHERE status='SUCCESS' GROUP BY txn_type, band ORDER BY fraud_pct DESC;

-- Q5. Users with abnormal activity: >3 txns above 20k in a single day
SELECT user_id, date(txn_ts) AS d, COUNT(*) AS big_txns, ROUND(SUM(amount),0) AS total
FROM txns WHERE amount>20000 GROUP BY user_id, d HAVING COUNT(*)>3 ORDER BY big_txns DESC LIMIT 20;

-- Q6. Rolling 7-day failure rate (window frame)
WITH d AS (
  SELECT date(txn_ts) AS d, COUNT(*) AS n, SUM(status='FAILED') AS f FROM txns GROUP BY d)
SELECT d, ROUND(100.0*SUM(f) OVER (ORDER BY d ROWS 6 PRECEDING)/SUM(n) OVER (ORDER BY d ROWS 6 PRECEDING),2) AS fail_pct_7d
FROM d;
