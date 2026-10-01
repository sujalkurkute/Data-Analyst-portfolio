-- Table: students(student_id, branch, gender, cgpa, internships, projects, certifications, dsa_score, placed, package_lpa)
-- Q1 placement rate and avg/median-ish package by branch
SELECT branch, COUNT(*) students, ROUND(100.0*AVG(placed),1) placed_pct, ROUND(AVG(package_lpa),2) avg_lpa, ROUND(MAX(package_lpa),2) max_lpa
FROM students GROUP BY branch ORDER BY placed_pct DESC;
-- Q2 impact of internships
SELECT internships, COUNT(*) n, ROUND(100.0*AVG(placed),1) placed_pct, ROUND(AVG(package_lpa),2) avg_lpa FROM students GROUP BY internships ORDER BY internships;
-- Q3 CGPA band funnel
SELECT CASE WHEN cgpa<6.5 THEN '<6.5' WHEN cgpa<7.5 THEN '6.5-7.5' WHEN cgpa<8.5 THEN '7.5-8.5' ELSE '8.5+' END band,
       COUNT(*) n, ROUND(100.0*AVG(placed),1) placed_pct, ROUND(AVG(package_lpa),2) avg_lpa FROM students GROUP BY band ORDER BY band;
-- Q4 top 10 packages with rank within branch
SELECT * FROM (SELECT student_id, branch, package_lpa, DENSE_RANK() OVER (PARTITION BY branch ORDER BY package_lpa DESC) r FROM students WHERE placed=1) WHERE r<=3 ORDER BY branch, r;
