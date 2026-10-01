-- Table: customers(customer_id, contract, internet, tenure_months, monthly_charges, payment_method, support_calls, churn, signup_month)
-- Q1 churn by contract
SELECT contract, COUNT(*) n, ROUND(100.0*AVG(churn),1) churn_pct FROM customers GROUP BY contract;
-- Q2 revenue at risk by segment
SELECT internet, contract, ROUND(SUM(CASE WHEN churn=1 THEN monthly_charges END),0) monthly_rev_lost
FROM customers GROUP BY internet, contract ORDER BY monthly_rev_lost DESC;
-- Q3 tenure bucket retention
SELECT CASE WHEN tenure_months<=6 THEN '0-6' WHEN tenure_months<=12 THEN '7-12' WHEN tenure_months<=24 THEN '13-24' ELSE '25+' END bucket,
       COUNT(*) n, ROUND(100.0*(1-AVG(churn)),1) retention_pct FROM customers GROUP BY bucket;
-- Q4 signup cohort retention
SELECT signup_month, COUNT(*) n, ROUND(100.0*(1-AVG(churn)),1) retention_pct FROM customers GROUP BY signup_month ORDER BY signup_month;
