"""SIMULATED campus placement data (1,200 students, 2024-2026 batches). Replace with your college data (anonymised) using the same columns."""
import numpy as np, pandas as pd
rng = np.random.default_rng(22); N=1200
branch = rng.choice(["AI&DS","CS","IT","ENTC","Mech","Civil"],N,p=[.17,.25,.2,.18,.12,.08])
cgpa = np.clip(rng.normal(7.4,0.9,N),5,10).round(2)
internships = rng.choice([0,1,2,3],N,p=[.35,.35,.2,.1])
projects = rng.integers(0,6,N)
certs = rng.integers(0,5,N)
dsa = np.clip(rng.normal(55+8*(np.isin(branch,["AI&DS","CS","IT"])),18,N),0,100).round(0)
gender = rng.choice(["F","M"],N,p=[.38,.62])
core = np.isin(branch,["AI&DS","CS","IT"])
logit = -5.6 + 0.55*cgpa + 0.55*internships + 0.12*projects + 0.05*dsa/10*10/10 + 0.18*certs + 0.7*core
placed = (rng.random(N) < 1/(1+np.exp(-logit))).astype(int)
base = 3.2 + 0.35*(cgpa-7) + 0.8*internships + 0.015*dsa + 1.6*core + rng.normal(0,0.9,N)
package = np.where(placed==1, np.clip(base,2.5,30).round(2), np.nan)
pd.DataFrame(dict(student_id=range(1,N+1),branch=branch,gender=gender,cgpa=cgpa,internships=internships,projects=projects,certifications=certs,dsa_score=dsa,placed=placed,package_lpa=package)).to_csv("data/placements.csv",index=False)
