import sqlite3, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
sns.set_theme(style="whitegrid")
df = pd.read_csv("data/mandi_prices.csv",parse_dates=["week"]); df["month"]=df.week.dt.month
con=sqlite3.connect(":memory:"); df.to_sql("prices",con,index=False)
vol = pd.read_sql(open("sql/queries.sql").read().split("-- Q2")[0].split("-- Q1")[1].split("\n",1)[1],con)
state = df.groupby(["crop","week"]).modal_price.mean().unstack(0)
seas_idx = (df.groupby(["crop","month"]).modal_price.mean().unstack(0)/df.groupby("crop").modal_price.mean()*100).round(1)
best = seas_idx.idxmax(); worst = seas_idx.idxmin(); spread = (seas_idx.max()-seas_idx.min()).round(1)
prem = (df.groupby(["mandi","crop"]).modal_price.mean().unstack()/df.groupby("crop").modal_price.mean()*100-100).round(1)
corr = df.groupby("crop").apply(lambda g: g.modal_price.corr(g.arrivals_qtl)).round(2)
# charts
fig,ax=plt.subplots(1,2,figsize=(14,4.8))
sns.heatmap(seas_idx.T,annot=True,fmt=".0f",cmap="RdYlGn",center=100,ax=ax[0],cbar=False); ax[0].set_title("Seasonal price index by month (100 = crop avg)")
sns.heatmap(prem,annot=True,fmt=".1f",cmap="RdYlGn",center=0,ax=ax[1],cbar=False); ax[1].set_title("Mandi price premium vs avg (%)")
plt.tight_layout(); plt.savefig("outputs/seasonality_heatmaps.png",dpi=140); plt.close()
dec = seasonal_decompose(state["Onion"],model="multiplicative",period=52)
fig=dec.plot(); fig.set_size_inches(10,7); fig.suptitle("Onion: trend / seasonal / residual",y=1.0); plt.tight_layout(); plt.savefig("outputs/onion_decomposition.png",dpi=130); plt.close()
mn = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
seas_idx.to_csv("outputs/seasonal_index.csv"); prem.to_csv("outputs/mandi_premium.csv"); vol.to_csv("outputs/volatility.csv",index=False)
lines="\n".join(f"- {c}: sell in {mn[best[c]]} (index {seas_idx[c].max():.0f}), avoid {mn[worst[c]]} (index {seas_idx[c].min():.0f}); seasonal swing {spread[c]:.0f} pts; price-arrivals corr {corr[c]}." for c in seas_idx.columns)
res=f"""# Results (simulated data; {len(df):,} rows, {df.week.min().date()} to {df.week.max().date()})
- Most volatile crop (CV): {vol.iloc[0].crop} ({vol.iloc[0].cv_pct}%); least: {vol.iloc[-1].crop} ({vol.iloc[-1].cv_pct}%).
{lines}
- Highest-premium market overall: {prem.mean(axis=1).idxmax()} ({prem.mean(axis=1).max():.1f}% above average).
"""
open("outputs/results.md","w").write(res); print(res)
