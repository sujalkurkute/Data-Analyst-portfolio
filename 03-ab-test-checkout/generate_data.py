"""SIMULATED checkout A/B test: control = 3-step checkout, variant = 1-page checkout."""
import numpy as np, pandas as pd
rng = np.random.default_rng(11)
n_per = 16500
rows=[]
for grp,p in [("control",0.112),("variant",0.1215)]:
    dev = rng.choice(["mobile","desktop"], n_per, p=[.68,.32])
    p_i = np.where(dev=="mobile", p*0.92, p*1.18)
    conv = (rng.random(n_per) < p_i).astype(int)
    aov = np.where(conv==1, rng.lognormal(6.6,.45,n_per).round(0), 0)
    rows.append(pd.DataFrame(dict(user_id=[f"{grp[0]}{i}" for i in range(n_per)],group=grp,device=dev,converted=conv,order_value=aov)))
pd.concat(rows).to_csv("data/ab_test.csv",index=False)
