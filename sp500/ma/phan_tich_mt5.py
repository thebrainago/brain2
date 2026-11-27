import pandas as pd, numpy as np, glob, re, sys, json
thu=sys.argv[1]; out=[]
for f in sorted(glob.glob(f'{thu}/sp500_batday*.csv')):
    d=pd.read_csv(f, encoding='latin1'); d['t']=pd.to_datetime(d.time)
    x=d[d.entry==1]
    if len(x)==0: continue
    b=np.r_[10000, x.balance_after.values]; pk=np.maximum.accumulate(b); dd=(1-b/pk).max()
    t0=pd.Timestamp(sys.argv[2]); t1=pd.Timestamp('2026-11-26'); nam=(t1-t0).days/365.25
    cagr=(b[-1]/1e4)**(1/nam)-1 if b[-1]>0 else -1
    m=re.search(r'_k([\d.]+)_s([\d.]+)_L(\d+)_f(\d)',f)
    out.append(dict(k=float(m[1]),stop=float(m[2]),L=int(m[3]),loc=int(m[4]),lenh=len(x),thang=round((x.profit>0).mean()*100,1),
        cuoi=round(b[-1],0),cagr=round(cagr*100,1),dd_dong=round(dd*100,1),swap=round(x.swap.sum(),0),phi=round(x.commission.sum(),0)))
df=pd.DataFrame(out).sort_values('cagr',ascending=False); print(df.to_string(index=False)); df.to_csv(f'{thu}_tong.csv',index=False)
