import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.metrics import roc_auc_score
sns.set_theme(style="whitegrid")
df = pd.read_csv("data/customers.csv")
# --- RFM-style segmentation (tenure=Recency proxy/loyalty, support calls=Frequency of friction, charges=Monetary)
df["tenure_band"] = pd.cut(df.tenure_months,[0,6,12,24,100],labels=["0-6","7-12","13-24","25+"])
seg = df.groupby("contract").agg(n=("churn","size"),churn_pct=("churn",lambda s:100*s.mean()),avg_charge=("monthly_charges","mean")).round(2)
ten = df.groupby("tenure_band",observed=True).churn.apply(lambda s:100*(1-s.mean())).round(1)
# --- model baseline
X = pd.get_dummies(df[["contract","internet","payment_method","tenure_months","monthly_charges","support_calls"]],drop_first=True)
Xtr,Xte,ytr,yte = train_test_split(X,df.churn,test_size=.25,random_state=1,stratify=df.churn)
m = LogisticRegression(max_iter=2000).fit((Xtr-Xtr.mean())/Xtr.std(),ytr)
p = m.predict_proba((Xte-Xtr.mean())/Xtr.std())[:,1]; auc = roc_auc_score(yte,p)
coef = pd.Series(m.coef_[0],index=X.columns).sort_values(key=abs,ascending=False).head(6)
# --- revenue impact of a retention campaign on top-decile risk customers
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
oof = cross_val_predict(make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)),X,df.churn,cv=5,method='predict_proba')[:,1]
te = df.copy(); te["risk"]=oof; p_all=oof
top = te.nlargest(int(len(te)*.10),"risk")
cust_saved_rate, cost_per_cust = 0.20, 100     # ASSUMPTIONS (replace with real campaign data): 20% save rate, Rs100 offer cost
breakeven = cost_per_cust/(top.loc[top.churn==1,'monthly_charges'].sum()*12/len(top))
at_risk_rev = top.loc[top.churn==1,"monthly_charges"].sum()*12
saved = at_risk_rev*cust_saved_rate; cost = len(top)*cost_per_cust
fig,ax = plt.subplots(1,3,figsize=(15,4.2))
sns.barplot(x=seg.index,y=seg.churn_pct,ax=ax[0],color="#3b6fb6"); ax[0].set_title("Churn % by contract")
sns.barplot(x=ten.index.astype(str),y=ten.values,ax=ax[1],color="#27ae60"); ax[1].set_title("Retention % by tenure (months)")
coef.sort_values().plot.barh(ax=ax[2],color="#c0392b"); ax[2].set_title("Top churn drivers (std. coef)")
plt.tight_layout(); plt.savefig("outputs/churn_overview.png",dpi=140)
seg.to_csv("outputs/segments.csv"); te.to_csv("outputs/scored_customers.csv",index=False)
res=f"""# Results (simulated data, {len(df):,} customers)
- Overall churn {df.churn.mean()*100:.1f}%. Month-to-month churn {seg.loc['Month-to-month','churn_pct']:.1f}% vs Two-year {seg.loc['Two year','churn_pct']:.1f}%.
- Retention is {ten['0-6']}% in months 0-6 vs {ten['25+']}% at 25+ months.
- Logistic regression baseline AUC = {auc:.3f}. Strongest drivers: {', '.join(coef.index[:4])}.
- Campaign on top-10% risk customers (n={len(top)}): annualised revenue at risk Rs {at_risk_rev:,.0f}; at an ASSUMED {int(cust_saved_rate*100)}% save rate and Rs{cost_per_cust}/customer offer, projected saving Rs {saved:,.0f} vs cost Rs {cost:,.0f} (net Rs {saved-cost:,.0f}). Break-even save rate: {breakeven*100:.1f}%.
"""
open("outputs/results.md","w").write(res); print(res)
