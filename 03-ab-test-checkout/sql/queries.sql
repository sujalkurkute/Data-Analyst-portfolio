-- Table: ab(user_id, group, device, converted, order_value)
SELECT "group", COUNT(*) users, SUM(converted) conversions, ROUND(100.0*AVG(converted),2) conv_pct,
       ROUND(SUM(order_value)*1.0/COUNT(*),2) revenue_per_user FROM ab GROUP BY "group";
SELECT device, "group", COUNT(*) users, ROUND(100.0*AVG(converted),2) conv_pct FROM ab GROUP BY device, "group";
