"""SIMULATED telecom-style subscription dataset. Replace with the Kaggle
'Telco Customer Churn' CSV (same core columns) to use real data."""
import numpy as np, pandas as pd
rng = np.random.default_rng(7); N = 7000
contract = rng.choice(["Month-to-month","One year","Two year"], N, p=[.55,.25,.20])
internet = rng.choice(["Fiber","DSL","None"], N, p=[.42,.35,.23])
tenure = np.where(contract=="Month-to-month", rng.integers(1,40,N), rng.integers(6,72,N))
monthly = np.where(internet=="Fiber", rng.normal(88,12,N), np.where(internet=="DSL", rng.normal(58,10,N), rng.normal(24,5,N))).clip(15,130).round(2)
pay = rng.choice(["Auto-pay","Credit card","Bank transfer","Electronic check"], N, p=[.3,.2,.2,.3])
support_calls = rng.poisson(1.2 + 1.0*(internet=="Fiber"), N)
logit = (-2.3 + 1.6*(contract=="Month-to-month") - 1.0*(contract=="Two year") - 0.035*tenure
         + 0.012*(monthly-60) + 0.35*support_calls + 0.5*(pay=="Electronic check") + 0.4*(internet=="Fiber"))
churn = (rng.random(N) < 1/(1+np.exp(-logit))).astype(int)
df = pd.DataFrame(dict(customer_id=[f"C{100000+i}" for i in range(N)], contract=contract, internet=internet,
     tenure_months=tenure, monthly_charges=monthly, payment_method=pay, support_calls=support_calls, churn=churn))
df["signup_month"] = (pd.Timestamp("2026-08-01") - pd.to_timedelta(df.tenure_months*30, unit="D")).dt.to_period("M").astype(str)
df.to_csv("data/customers.csv", index=False); print(df.shape, df.churn.mean().round(3))
