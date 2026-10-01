# Results (simulated data, 200,000 transactions)
- Overall failure rate: 3.57%. Worst bank: Yes Bank (5.82%); best: ICICI (1.89%).
- Peak hours 18:00-21:59 fail at 4.90% vs 3.00% off-peak (1.63x). ~1,147 excess failed txns attributable to peak congestion.
- Highest fraud segment: Collect Request / 1k-20k at 0.599% fraud.
- Simple rule (amount>20k OR collect request OR 00-05h) flags 10.0% of txns: precision 0.4%, recall 37.0%.
