import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
sns.set_theme(style="whitegrid")
df = pd.read_csv("data/ab_test.csv")
# 1) Pre-test sample size: baseline 11%, MDE = +1pp absolute, alpha .05, power .80
p1, mde, a, pw = 0.11, 0.01, 0.05, 0.80
p2 = p1+mde; za, zb = stats.norm.ppf(1-a/2), stats.norm.ppf(pw)
n_req = int(np.ceil(((za+zb)**2*(p1*(1-p1)+p2*(1-p2)))/mde**2))
# 2) Two-proportion z-test
c, v = df[df.group=="control"], df[df.group=="variant"]
x = np.array([v.converted.sum(), c.converted.sum()]); n = np.array([len(v),len(c)])
pc, pv = x[1]/n[1], x[0]/n[0]; pp = x.sum()/n.sum()
z = (pv-pc)/np.sqrt(pp*(1-pp)*(1/n[0]+1/n[1])); pval = 2*(1-stats.norm.cdf(abs(z)))
se = np.sqrt(pv*(1-pv)/n[0]+pc*(1-pc)/n[1]); lo,hi = (pv-pc)-1.96*se,(pv-pc)+1.96*se
# 3) Revenue per user (Welch t-test) and segment check
rt = stats.ttest_ind(v.order_value, c.order_value, equal_var=False)
seg = df.groupby(["device","group"]).converted.mean().unstack()*100
# 4) Chart
fig,ax = plt.subplots(1,2,figsize=(11,4))
ax[0].bar(["Control","Variant"],[pc*100,pv*100],yerr=[1.96*np.sqrt(pc*(1-pc)/n[1])*100,1.96*np.sqrt(pv*(1-pv)/n[0])*100],color=["#95a5a6","#27ae60"],capsize=6)
ax[0].set_title("Conversion rate (%) with 95% CI")
seg.plot.bar(ax=ax[1],color=["#95a5a6","#27ae60"]); ax[1].set_title("Conversion % by device"); ax[1].tick_params(axis="x",rotation=0)
plt.tight_layout(); plt.savefig("outputs/ab_result.png",dpi=140)
decision = "SHIP the variant" if (pval<0.05 and lo>0) else "DO NOT ship / keep testing"
res=f"""# A/B Test Decision Memo (simulated data)
- Required sample/arm for 1pp MDE at 80% power: {n_req:,}. Actual: {n[0]:,} and {n[1]:,} (adequately powered: {n.min()>=n_req}).
- Control {pc*100:.2f}% vs Variant {pv*100:.2f}% -> lift {(pv-pc)*100:+.2f}pp ({(pv/pc-1)*100:+.1f}% relative).
- z = {z:.2f}, {"p<0.001" if pval<0.001 else f"p = {pval:.4f}"}, 95% CI for difference: [{lo*100:.2f}pp, {hi*100:.2f}pp].
- Revenue/user: control Rs{c.order_value.mean():.1f} vs variant Rs{v.order_value.mean():.1f} (Welch t-test {"p<0.001" if rt.pvalue<0.001 else f"p = {rt.pvalue:.3f}"}).
- Device split: mobile {seg.loc['mobile','control']:.1f}% -> {seg.loc['mobile','variant']:.1f}%; desktop {seg.loc['desktop','control']:.1f}% -> {seg.loc['desktop','variant']:.1f}%.
- **Recommendation: {decision}.**
"""
open("outputs/decision_memo.md","w").write(res); print(res)
