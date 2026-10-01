"""SIMULATED weekly mandi modal prices (Rs/quintal), 2023-2026, Maharashtra markets.
Real source to swap in: Agmarknet (agmarknet.gov.in) / data.gov.in 'Current daily price of commodities' - keep same columns."""
import numpy as np, pandas as pd
rng = np.random.default_rng(3)
weeks = pd.date_range("2023-01-01","2026-08-30",freq="W")
crops = {"Onion":(1800,.35,0.28,2),"Tomato":(1600,.55,0.40,7),"Soybean":(4600,.08,0.06,10),"Cotton":(6800,.06,0.05,11),"Tur":(7400,.10,0.09,1)}
mandis = {"Pune":1.04,"Nashik":0.97,"Lasalgaon":0.93,"Nagpur":1.02,"Solapur":0.99}
rows=[]
for crop,(base,seas_amp,vol,peak_m) in crops.items():
    t=np.arange(len(weeks)); trend = base*(1+0.0004*t)
    seas = 1 + seas_amp*np.cos(2*np.pi*(weeks.month.values-peak_m)/12)
    shock = np.exp(np.cumsum(rng.normal(0,vol/6,len(weeks))) - 0.5*np.arange(len(weeks))*(vol/6)**2*0.2)
    shock = shock/np.mean(shock)
    for mandi,f in mandis.items():
        noise = rng.normal(1,0.03,len(weeks))
        price = (trend*seas*shock*f*noise).round(0)
        arr = (rng.lognormal(7.0,.25,len(weeks))*(1.25-0.25*seas/ seas.max())).round(0)
        rows.append(pd.DataFrame(dict(week=weeks,crop=crop,mandi=mandi,modal_price=price,arrivals_qtl=arr)))
pd.concat(rows).to_csv("data/mandi_prices.csv",index=False)
