# Round 5 portfolio evaluator with risk-stop policies. Uses engine2 at actual lots (linear in lot) + scalp curves.
import sys,os,pickle,itertools,numpy as np,pandas as pd,r5lib as R,bt,lotscale as LS
V=R.V; IDX=None
Dt={a:bt.table(a) for a in ('XAU','US500')}
idx=Dt['XAU'].index.union(Dt['US500'].index); n=len(idx)
A_END=pd.Timestamp('2026-08-20',tz='UTC'); iA=int(idx.searchsorted(A_END))
mon=idx.strftime('%Y-%m'); mcodes=pd.factorize(mon)[0]; mlast=np.r_[np.nonzero(np.diff(mcodes))[0],n-1]
tt=idx.values; BRK=np.nonzero(np.r_[(np.diff(tt).astype('timedelta64[m]').astype(int)>300),False])[0]
def al(s,ix): return pd.Series(s,index=ix).reindex(idx).ffill().fillna(0).values
PX={a:al(Dt[a].close.values,Dt[a].index) for a in Dt}
FL={}
for a in Dt: FL[a]={m:(np.zeros(len(Dt[a]),np.int64) if m==0 else R.flat_arr(Dt[a],mode=m)) for m in (0,1,2)}
SCV={}
for k in ('xs1','xs2'):
    SCV[k]=(pickle.load(open(f'{LS.CD_}/{k}.pkl','rb')),pickle.load(open(f'{LS.CD_}/{k}_x.pkl','rb')))
CAP={'XAU':30000.,'US500':10000.}
POL0=dict(flat=0,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
def sysc(k,lot,pol):
    """return dict ec,ew,sec,sew (sx2+slip1),nl,px-asset on union idx scaled to lot"""
    a=R.S[k][0]
    if k in SCV:
        o,x=SCV[k]; f=lot/o['lot']
        return dict(a=a,ec=f*al(o['base'][0],o['index']),ew=f*al(o['base'][1],o['index']),sec=f*al(x['sx2s'][0],x['index']),sew=f*al(x['sx2s'][1],x['index']),nl=np.zeros(n))
    D=Dt[a]; m=R.S[k][3]; N=None if not pol.get('minusN') else max(2,m['maxN']-1)
    kw=dict(hsk=pol['hsk'],hs_pct=pol['hs'],dl_pct=pol['dl'],maxN=N,lot=lot); fl=FL[a][pol['flat']]
    o=R.run2(k,D,fl,**kw); o2=R.run2(k,D,fl,sprmul=2.0,slip=1.0,**kw)
    return dict(a=a,ec=al(o['ec'],D.index),ew=al(o['ew'],D.index),sec=al(o2['ec'],D.index),sew=al(o2['ew'],D.index),nl=al(o['nl'],D.index),st=o['st'])
def ddf(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
def evalport(lots,pol,cap=None,perpol=None,full=False):
    perpol=perpol or {}; C={k:sysc(k,l,perpol.get(k,pol)) for k,l in lots.items()}
    cap=cap or sum(CAP[a] for a in {c['a'] for c in C.values()})
    ec=sum(c['ec'] for c in C.values()); ew=sum(c['ew'] for c in C.values()); sec=sum(c['sec'] for c in C.values()); sew=sum(c['sew'] for c in C.values())
    r=dict(net=float(ec[-1]),dd=ddf(ec,ew)/cap*100,sx_net=float(sec[-1]),sx_dd=ddf(sec,sew)/cap*100,A=float(ec[iA-1]),B=float(ec[-1]-ec[iA-1]))
    m=ec[mlast]; mn=np.diff(np.r_[0,m]); r['months']=[round(float(x)) for x in mn]; r['npos']=int((mn>0).sum())
    pk=np.maximum.accumulate(ec); pvs={'XAU':100.0,'US500':1.0}
    # gap models: exposure (|net lots|) * px * pv * X; worst direction per asset
    for X in (0.05,0.10):
        for tag,pts in (('gap',None),('wk',BRK)):
            best=0.0; assets=sorted({c['a'] for c in C.values()})
            up={a:np.zeros(n) for a in assets}; dn={a:np.zeros(n) for a in assets}
            for k,c in C.items():
                a=c['a']; e=c['nl']*PX[a]*pvs[a]*X; up[a]+=np.maximum(-e,0); dn[a]+=np.maximum(e,0)
            for combo in itertools.product((0,1),repeat=len(assets)):
                loss=sum((up if cc==0 else dn)[a] for a,cc in zip(assets,combo))
                if pts is None: v=float(np.max(pk-(ew-loss)))
                else: v=max(ddf(ec,ew),float(np.max(pk[pts]-(ec[pts]-loss[pts]))))
                best=max(best,v)
            r[f'{tag}{int(X*100)}']=best/cap*100
    r['cap']=cap
    if full: r['ec']=ec; r['ew']=ew; r['C']=C
    return r
