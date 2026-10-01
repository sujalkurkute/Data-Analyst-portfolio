# A/B Test Decision Memo (simulated data)
- Required sample/arm for 1pp MDE at 80% power: 15,973. Actual: 16,500 and 16,500 (adequately powered: True).
- Control 10.82% vs Variant 12.32% -> lift +1.50pp (+13.8% relative).
- z = 4.25, p<0.001, 95% CI for difference: [0.81pp, 2.19pp].
- Revenue/user: control Rs87.1 vs variant Rs101.6 (Welch t-test p<0.001).
- Device split: mobile 10.1% -> 11.1%; desktop 12.4% -> 14.9%.
- **Recommendation: SHIP the variant.**
