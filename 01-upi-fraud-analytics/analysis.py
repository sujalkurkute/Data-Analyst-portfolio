import sqlite3, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid")
df = pd.read_csv("data/upi_transactions.csv", parse_dates=["txn_ts"])
con = sqlite3.connect(":memory:"); df.to_sql("txns", con, index=False)
q = lambda s: pd.read_sql(s, con)
bank = q("""SELECT bank, COUNT(*) txns, ROUND(100.0*SUM(status='FAILED')/COUNT(*),2) fail_pct
            FROM txns GROUP BY bank ORDER BY fail_pct DESC""")
hour = q("""SELECT CAST(strftime('%H',txn_ts) AS INT) hr, COUNT(*) txns,
            ROUND(100.0*SUM(status='FAILED')/COUNT(*),2) fail_pct FROM txns GROUP BY hr ORDER BY hr""")
fraud = q("""SELECT txn_type, CASE WHEN amount<1000 THEN '<1k' WHEN amount<20000 THEN '1k-20k' ELSE '20k+' END band,
             COUNT(*) txns, SUM(is_fraud) fraud, ROUND(100.0*SUM(is_fraud)/COUNT(*),3) fraud_pct
             FROM txns WHERE status='SUCCESS' GROUP BY 1,2 ORDER BY fraud_pct DESC""")
mom = q("""WITH m AS (SELECT strftime('%Y-%m',txn_ts) ym, COUNT(*) txns, SUM(amount) value FROM txns GROUP BY ym)
           SELECT ym, txns, ROUND(value,0) value FROM m""")
for n,d in [("bank_failure",bank),("hourly_failure",hour),("fraud_segments",fraud),("monthly_volume",mom)]:
    d.to_csv(f"outputs/{n}.csv", index=False)   # ready to load into Power BI

fig,ax = plt.subplots(1,2,figsize=(13,4.5))
sns.barplot(data=bank,x="fail_pct",y="bank",ax=ax[0],color="#3b6fb6"); ax[0].set_title("Failure rate by bank (%)")
sns.lineplot(data=hour,x="hr",y="fail_pct",marker="o",ax=ax[1],color="#c0392b"); ax[1].set_title("Failure rate by hour of day (%)")
ax[1].axvspan(18,21,alpha=.12,color="red")
plt.tight_layout(); plt.savefig("outputs/failure_dashboard.png",dpi=140); plt.close()

top = fraud.head(8).copy(); top["seg"]=top.txn_type+" | "+top.band
plt.figure(figsize=(8,4.5)); sns.barplot(data=top,x="fraud_pct",y="seg",color="#8e44ad")
plt.title("Highest-risk segments: fraud rate (%)"); plt.tight_layout(); plt.savefig("outputs/fraud_segments.png",dpi=140); plt.close()

# rule-based risk flag: evaluate precision/recall
night = df.txn_ts.dt.hour.isin([0,1,2,3,4])
rule = ((df.amount>20000)|(df.txn_type=="Collect Request")|night) & (df.status=="SUCCESS")
tp = int((rule & (df.is_fraud==1)).sum()); fp=int((rule&(df.is_fraud==0)).sum()); fn=int(((~rule)&(df.is_fraud==1)).sum())
prec, rec = tp/(tp+fp), tp/(tp+fn)
fr = (df.status=="FAILED").mean()*100
peak = df[df.txn_ts.dt.hour.isin([18,19,20,21])]; off=df[~df.txn_ts.dt.hour.isin([18,19,20,21])]
pk, of = (peak.status=="FAILED").mean()*100, (off.status=="FAILED").mean()*100
excess = ((peak.status=="FAILED").mean()-(off.status=="FAILED").mean())*len(peak)
res = f"""# Results (simulated data, {len(df):,} transactions)
- Overall failure rate: {fr:.2f}%. Worst bank: {bank.iloc[0].bank} ({bank.iloc[0].fail_pct}%); best: {bank.iloc[-1].bank} ({bank.iloc[-1].fail_pct}%).
- Peak hours 18:00-21:59 fail at {pk:.2f}% vs {of:.2f}% off-peak ({pk/of:.2f}x). ~{excess:,.0f} excess failed txns attributable to peak congestion.
- Highest fraud segment: {fraud.iloc[0].txn_type} / {fraud.iloc[0].band} at {fraud.iloc[0].fraud_pct}% fraud.
- Simple rule (amount>20k OR collect request OR 00-05h) flags {rule.mean()*100:.1f}% of txns: precision {prec*100:.1f}%, recall {rec*100:.1f}%.
"""
open("outputs/results.md","w").write(res); print(res)
