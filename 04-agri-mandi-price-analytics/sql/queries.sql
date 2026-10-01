-- Table: prices(week, crop, mandi, modal_price, arrivals_qtl)
-- Q1 volatility (coefficient of variation) per crop  [SQLite lacks STDDEV; computed via variance formula]
SELECT crop, ROUND(AVG(modal_price),0) avg_price,
       ROUND(100.0*SQRT(AVG(modal_price*modal_price)-AVG(modal_price)*AVG(modal_price))/AVG(modal_price),1) cv_pct
FROM prices GROUP BY crop ORDER BY cv_pct DESC;
-- Q2 best month to sell, per crop (avg price by calendar month, ranked)
SELECT crop, CAST(strftime('%m',week) AS INT) m, ROUND(AVG(modal_price),0) avg_price,
       RANK() OVER (PARTITION BY crop ORDER BY AVG(modal_price) DESC) rk
FROM prices GROUP BY crop, m;
-- Q3 mandi price premium vs state average
SELECT mandi, crop, ROUND(100.0*(AVG(modal_price)/(SELECT AVG(modal_price) FROM prices p2 WHERE p2.crop=prices.crop)-1),1) premium_pct
FROM prices GROUP BY mandi, crop;
-- Q4 arrivals vs price relationship: weeks with top-quartile arrivals
SELECT crop, ROUND(AVG(modal_price),0) avg_price_high_arrivals FROM prices p
WHERE arrivals_qtl >= (SELECT arrivals_qtl FROM prices q WHERE q.crop=p.crop ORDER BY arrivals_qtl DESC LIMIT 1 OFFSET (SELECT COUNT(*)/4 FROM prices q2 WHERE q2.crop=p.crop))
GROUP BY crop;
