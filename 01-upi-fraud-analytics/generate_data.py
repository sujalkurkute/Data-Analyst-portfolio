"""Generate a SIMULATED UPI transaction dataset (no real customer data).
Swap in real/anonymised data with the same columns to reuse the whole pipeline."""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)
N = 200_000
banks = ["SBI","HDFC","ICICI","Axis","PNB","BoB","Kotak","Yes Bank","IndusInd","Canara"]
bank_fail = dict(zip(banks,[0.045,0.018,0.016,0.020,0.040,0.035,0.019,0.050,0.028,0.038]))
types = ["P2P","P2M","Bill Pay","Recharge","Collect Request"]
type_p = [0.38,0.34,0.12,0.09,0.07]
ts = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 180*24*3600, N), unit="s")
# peak hours bias
hour_w = np.array([1,1,1,1,1,2,3,5,7,8,7,7,8,7,6,6,7,9,11,12,10,7,4,2],float); hour_w/=hour_w.sum()
hours = rng.choice(24, N, p=hour_w)
ts = ts.normalize() + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(rng.integers(0,3600,N), unit="s")
df = pd.DataFrame({
  "txn_id": np.arange(1, N+1),
  "txn_ts": ts,
  "bank": rng.choice(banks, N, p=[.22,.17,.14,.11,.07,.06,.07,.04,.04,.08]),
  "txn_type": rng.choice(types, N, p=type_p),
  "device": rng.choice(["Android","iOS","Web"], N, p=[.72,.24,.04]),
  "user_id": rng.integers(1, 40_000, N),
})
amt = rng.lognormal(6.0, 1.1, N).round(2)
df["amount"] = np.clip(amt, 1, 100000)
# status probabilities
p_fail = df.bank.map(bank_fail).values.copy()
h = df.txn_ts.dt.hour.values
p_fail *= np.where(np.isin(h,[18,19,20,21]), 1.6, 1.0)          # peak-hour congestion
p_fail *= np.where(df.txn_type=="Collect Request", 1.3, 1.0)
df["status"] = np.where(rng.random(N) < p_fail, "FAILED", "SUCCESS")
# fraud: higher for large amounts, night, collect requests, new-ish users
p_fraud = 0.0008 + 0.004*(df.amount>20000) + 0.0025*np.isin(h,[0,1,2,3,4]) + 0.004*(df.txn_type=="Collect Request")
df["is_fraud"] = ((rng.random(N) < p_fraud) & (df.status=="SUCCESS")).astype(int)
df.to_csv("data/upi_transactions.csv", index=False)
print(df.shape, df.is_fraud.mean().round(4), (df.status=="FAILED").mean().round(4))
