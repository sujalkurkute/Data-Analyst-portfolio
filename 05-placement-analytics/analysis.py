import sqlite3, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
sns.set_theme(style="whitegrid")
df=pd.read_csv("data/placements.csv"); con=sqlite3.connect(":memory:"); df.to_sql("students",con,index=False)
q=lambda i: pd.read_sql(open("sql/queries.sql").read().split("-- Q")[i].split("\n",1)[1],con)
br,intern,band = q(1),q(2),q(3)
for n,d in [("by_branch",br),("by_internships",intern),("by_cgpa_band",band)]: d.to_csv(f"outputs/{n}.csv",index=False)
pl=df[df.placed==1]
# hypothesis tests
t_int = stats.ttest_ind(pl[pl.internships>=2].package_lpa, pl[pl.internships==0].package_lpa, equal_var=False)
anova = stats.f_oneway(*[g.package_lpa.values for _,g in pl.groupby("branch")])
ct = pd.crosstab(df.gender, df.placed); chi = stats.chi2_contingency(ct)
r_cgpa = stats.pointbiserialr(df.placed, df.cgpa)
gap = pl[pl.gender=="M"].package_lpa.mean()-pl[pl.gender=="F"].package_lpa.mean()
# driver model
feats=["cgpa","internships","projects","certifications","dsa_score"]
Z=StandardScaler().fit_transform(df[feats]); lr=LogisticRegression(max_iter=1000).fit(Z,df.placed)
imp=pd.Series(lr.coef_[0],index=feats).sort_values()
fig,ax=plt.subplots(1,3,figsize=(16,4.3))
sns.barplot(data=br,x="placed_pct",y="branch",ax=ax[0],color="#3b6fb6"); ax[0].set_title("Placement rate by branch (%)")
sns.boxplot(data=pl,x="internships",y="package_lpa",ax=ax[1],color="#27ae60"); ax[1].set_title("Package (LPA) by internships")
imp.plot.barh(ax=ax[2],color="#c0392b"); ax[2].set_title("What drives placement (std. coef)")
plt.tight_layout(); plt.savefig("outputs/placement_overview.png",dpi=140)
p=lambda v: "<0.001" if v<0.001 else f"{v:.3f}"
res=f"""# Results (simulated data, {len(df):,} students)
- Overall placement rate {df.placed.mean()*100:.1f}%; average package Rs {pl.package_lpa.mean():.2f} LPA.
- Best branch by placement: {br.iloc[0].branch} ({br.iloc[0].placed_pct}%); lowest: {br.iloc[-1].branch} ({br.iloc[-1].placed_pct}%). ANOVA on package across branches: F={anova.statistic:.1f}, p={p(anova.pvalue)}.
- Students with 2+ internships earn Rs {pl[pl.internships>=2].package_lpa.mean():.2f} LPA vs Rs {pl[pl.internships==0].package_lpa.mean():.2f} LPA with none (Welch t-test p={p(t_int.pvalue)}).
- CGPA vs placement point-biserial r = {r_cgpa.statistic:.2f} (p={p(r_cgpa.pvalue)}).
- Gender vs placement chi-square p = {p(chi[1])}; package gap M-F among placed = Rs {gap:.2f} LPA.
- Strongest standardized driver: {imp.abs().idxmax()}.
"""
res=res.replace("p=<","p<"); open("outputs/results.md","w").write(res); print(res)
