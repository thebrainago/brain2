import sys; sys.path.insert(0,'/workspace/bt_3m/v3/code')
import numpy as np, pandas as pd, bt, sig_v3 as S, json
res=[]
def go(asset,name,sigfn,adx,sess,m):
    D=bt.table(asset); s=S.filters(D,sigfn(D),adx,sess,asset); s=np.where(D.fut_ok.values,s,0)
    P=bt.periods(D)
    for pn,sl in P.items():
        out=bt.run(asset,s,m,sl); q=bt.quick(asset,out,D.index[sl]); q.update(name=name,per=pn,nsig=int((s[sl]!=0).sum())); res.append(q)
        print(name,pn,{k:(round(v,1) if isinstance(v,float) else v) for k,v in q.items() if k not in('name','months')},q['months'],flush=True)
us_c1=dict(L0=2.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=1.5,hedge=1,hgap=90,hr=0.5,htp=5.0,cd=30,comp=0,dsig=0,maxlots=0)
us_c3=dict(L0=1.0,mult=1.0,gap=45,gstep=1.4,maxN=3,btp=6,trim=0,prune=1.2,hedge=1,hgap=45*1.5*0+180/1.0,hr=0.5,htp=5.0,cd=30,comp=0,dsig=0,maxlots=0)
xa_c1=dict(L0=0.03,mult=1.0,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=0,hedge=0,hgap=0,hr=0.5,htp=5.0,cd=30,comp=0,dsig=0,maxlots=0)
xa_c3=dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30,comp=0,dsig=0,maxlots=0)
go('US500','us_c1_sw18_adx20_ldny',lambda D:S.fam_sw(D,1.8,15,'fade'),'gt20','ldny',us_c1)
go('US500','us_c3_sw18_adx20_ldny',lambda D:S.fam_sw(D,1.8,15,'fade'),'gt20','ldny',us_c3)
go('XAU','xa_c1_vwap3_adx20_all',lambda D:S.fam_vwap_atr(D,3.0),'gt20','all',xa_c1)
go('XAU','xa_c3_sw18_adx20_ldny',lambda D:S.fam_sw(D,1.8,15,'fade'),'gt20','ldny',xa_c3)
