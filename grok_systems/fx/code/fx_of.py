# Exploratory order-flow study: CME FX futures (6A,6E,6B,6C,6J), SI, CL aggressor-side flow (Sierra scid, UTC) vs XM CFD forward returns. Liquid window only.
import sys,os,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code'); import fxlib as F
M={'6AZ6.CME':('AUDUSD#',1,'2026-09-14'),'6EZ6.CME':('EURUSD#',1,'2026-09-14'),'6BZ6.CME':('GBPUSD#',1,'2026-09-14'),'6CZ6.CME':('USDCAD#',-1,'2026-09-14'),'6JZ6.CME':('USDJPY#',-1,'2026-09-14'),'SIZ6.COMEX':('SILVER.i#',1,'2026-08-25'),'CLF7.NYMEX':('OILCash#',1,'2026-09-14')}
rows=[]
for fx,(cfd,sgn,start) in M.items():
    p=f'{F.FX}/data/of/{fx}_1m.csv.gz'
    if not os.path.exists(p) or not os.path.exists(f'{F.DATA}/{F.fname(cfd)}.npz'): print('skip',fx); continue
    A=pd.read_csv(p,index_col=0); A.index=pd.to_datetime(A.index,unit='s',utc=True); A=A[A.index>=pd.Timestamp(start,tz='UTC')]
    D=F.table(cfd); full=pd.date_range(D.index[0].floor('min'),D.index[-1],freq='1min',tz='UTC')
    c=D.close.reindex(full).ffill(); sp=D.spread_px.reindex(full).ffill(); pip=float(F.info(cfd)['point'])*10
    A=A.reindex(full).fillna({'b':0,'s':0,'bb':0,'bs':0,'ntr':0}); A=A[A.index>=pd.Timestamp(start,tz='UTC')]
    feats={}
    dl=(A.b-A.s)*sgn; bd=(A.bb-A.bs)*sgn; tot=(A.b+A.s)
    for w in (5,15,60):
        sd=dl.rolling(w).sum(); ss=bd.rolling(w).sum(); vv=tot.rolling(w).sum()
        feats[f'delta{w}']=sd/(sd.rolling(3000,min_periods=500).std()+1e-9); feats[f'imb{w}']=sd/(vv+1); feats[f'big{w}']=ss/(ss.rolling(3000,min_periods=500).std()+1e-9)
    cc=c.reindex(A.index)
    for h in (15,60):
        # forward return from NEXT minute open proxy (close of t) to close t+1+h ; non-overlapping sampling
        fr=(c.shift(-(h+1))-c.shift(-1)).reindex(A.index)/pip
        for fn,fv in feats.items():
            d=pd.DataFrame({'f':fv,'r':fr}).dropna(); d=d.iloc[::h]
            if len(d)<200: continue
            ic=d.f.rank().corr(d.r.rank()); n=len(d); t=ic*np.sqrt((n-2)/(1-ic**2))
            hi=d[d.f>2.0]; lo=d[d.f<-2.0]; cond=(hi.r.mean()-lo.r.mean())/2 if len(hi)>20 and len(lo)>20 else np.nan   # mean pips following flow z>2 minus z<-2 (momentum direction, gross)
            rows.append(dict(fut=fx,cfd=cfd,feat=fn,h=h,n=n,ic=ic,t=t,mom_pips=cond,nhi=len(hi),nlo=len(lo),spread_pips=float(sp.median()/pip),days=int(A.index.normalize().nunique())))
R=pd.DataFrame(rows); R.to_csv(f'{F.RES}/of_ic.csv',index=False)
pd.set_option('display.width',220)
print(R.sort_values('t',key=abs,ascending=False).head(25).to_string())
print('n tests',len(R),' |t|>2:',(R.t.abs()>2).sum(),' expected by chance ~',round(0.05*len(R),1),' |t|>3:',(R.t.abs()>3).sum())
