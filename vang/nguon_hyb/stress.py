import numpy as np, pandas as pd, json, sys
import runh
from runh import Data
L=pd.read_pickle('m15_long.pkl')
WIN={'Q4-2018 (-20%)':('2018-09-25','2019-02-28'),'Covid 02-04/2020 (-34%)':('2020-02-10','2020-07-31'),
     '2022 H1 bear (-24%)':('2021-12-28','2022-07-31'),'2022 08-10 leg (-19%)':('2022-08-12','2022-12-15'),
     '08-10/2023 (-10%)':('2023-07-25','2023-12-15'),'07-08/2024 (-8.5%)':('2024-07-10','2024-09-30'),
     '02-04/2025 (-19%)':('2025-02-15','2025-07-15')}
PX=['o','h','l','c','a5','a15','ah1','c5p','zz_lo']
def scaled(d,f):
    d=d.copy()
    for k in PX: d[k]=d[k]*f
    return d
def run_cfg(D,cfg,S,extra):
    c=dict(cfg); c.update(extra); r,x=D.go(c,1,len(D.d),S); return r,x
def summarize(name,r,x,D):
    t=D.d.t.values; bl=x['bl']
    return dict(scenario=name,net=r['net'],maxfl=r['maxfl'],maxdd=r['maxdd'],minml1000=r['minml'],minml100=r['minml100'],
                blown1000=bool(r['blown']>=0),stopout100=bool(r['blown100']>=0),maxlay=int(r['maxlay']),maxlots=r['maxlots'],maxhl=r['maxhl'],
                ddblock_bars=int(r['nddblk']),open_at_end=bool(len(x['bc']) and x['bc'][-1]<0))
def crash_runs(configs,spr=0.65,ddb=3000.):
    rows=[]
    for wn,(a,b) in WIN.items():
        w=L[(L.t>=a)&(L.t<b)].reset_index(drop=True)
        w['zz_ext']=(w.zz_ext-L.index[L.t>=a][0]).clip(lower=0)
        f=7200.0/w.c.iloc[0]; w=scaled(w,f)
        D=Data(w,np.full((1,12),np.nan),np.full((len(w),6),np.nan))
        for cn,(cfg,Sf) in configs.items():
            S=Sf(w)
            r,x=run_cfg(D,cfg,S,dict(spr=spr,hexp=16,deadw=192,ddb=ddb))
            s=summarize(wn,r,x,D); s['cfg']=cn; s['scale']=round(f,3); rows.append(s)
    return rows
def m1_variant(D0,fn):
    d=D0.d.copy(); fn(d); return Data(d,D0.vp,D0.opt)
def synth_runs(configs,ddb=3000.):
    D0=runh.load_m1(); d0=D0.d; T=d0.t.values; rows=[]
    # time of MAIN's deepest float in Nov (basket 19/11): use equity minimum
    r,x=D0.go({},200,len(T)); i_deep=200+int(np.argmin(x['eq'])); print('deep point',T[i_deep])
    i_fresh=int(np.searchsorted(T,np.datetime64('2026-11-24 22:00')))
    def gap(g,i):
        def f(d):
            for k in ['o','h','l','c','c5p','zz_lo']: d.loc[i:,k]=d.loc[i:,k]*(1-g)
        return f
    def flash(g,i,down=30,up=120):
        def f(d):
            n=len(d); prof=np.ones(n); prof[i:i+down]=1-g*np.linspace(0,1,down); prof[i+down:i+down+up]=1-g*np.linspace(1,0,up)
            for k in ['o','h','l','c']: d[k]=d[k]*prof
            d['l']=np.minimum(d.l,d[['o','c']].min(1)); d['h']=np.maximum(d.h,d[['o','c']].max(1))
        return f
    def grind(tot,days,start='2026-06-01'):
        def f(d):
            i0=int(np.searchsorted(T,np.datetime64(start))); n=len(d); k=np.zeros(n)
            span=days*1380; k[i0:]=np.minimum(np.arange(n-i0)/span,1.0)
            fac=np.exp(np.log(1-tot)*k)
            for kk in ['o','h','l','c','c5p','zz_lo']: d[kk]=d[kk]*fac
            for kk in ['a5','a15','ah1']: d[kk]=d[kk]*fac
        return f
    S=[(f'gap -{int(g*100)}% (basket đang sâu)',gap(g,i_deep)) for g in (0.05,0.10,0.20)]
    S+=[(f'gap -{int(g*100)}% (basket mới)',gap(g,i_fresh)) for g in (0.05,0.10,0.20)]
    S+=[(f'flash -{int(g*100)}% 30p rồi hồi 2h (lúc sâu)',flash(g,i_deep)) for g in (0.05,0.10)]
    S+=[('grind -20% trong 60 ngày (từ 01/06)',grind(0.20,60)),('grind -35% trong 120 ngày (từ 01/06)',grind(0.35,120))]
    for sn,fn in S:
        D=m1_variant(D0,fn)
        for cn,(cfg,Sf) in configs.items():
            r,x=D.go(dict(cfg,ddb=ddb),200,len(T),Sf(D.d)); s=summarize(sn,r,x,D); s['cfg']=cn; rows.append(s)
    for cn,(cfg,Sf) in configs.items():
        r,x=D0.go(dict(cfg,spr=1.95,ddb=ddb),200,len(T),Sf(d0)); s=summarize('spread x3 (1.95), dữ liệu thật 06-11/2026',r,x,D0); s['cfg']=cn; rows.append(s)
    return rows
