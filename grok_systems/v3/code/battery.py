# Robustness battery for basket-style candidates (PYTHON SIMULATION).
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); import bt, sig_v3 as S
def drift_D(D,mult):
    """add mult * (linear drift of the window) to engine price path: mult=-1 detrends, -2 reverses trend."""
    D=D.copy(); n=len(D); slope=(D.close.iloc[-1]-D.close.iloc[0])/n; add=mult*slope*np.arange(n)
    for c in ('open','high','low','close'): D[c]=D[c].values+add
    return D
def flip_runs(s,seed):
    rng=np.random.default_rng(seed); runs=np.r_[0,np.nonzero(np.diff(s)!=0)[0]+1]; fl=rng.choice([-1,1],size=len(runs)); rid=np.zeros(len(s),np.int64); rid[runs]=1; rid=np.cumsum(rid)-1
    return (np.abs(s)*fl[rid]).astype(np.int64)
def q(asset,out,idx=None):
    P=bt.SPEC[asset]; ec,ew,nl,dep,st=out; cap=P['EQ0']+P['topup']; ex=dep-P['EQ0']; en=ec-ex; ewn=ew-ex; pk=np.maximum.accumulate(en)
    return dict(net=float(en[-1]-P['EQ0']),dd_pct=float(np.max(pk-ewn)/cap*100),so=int(st[3]),nb=int(st[0]),maxlot=float(st[5]))
def gapdd(asset,out,D,X=0.2):
    P=bt.SPEC[asset]; ec,ew,nl,dep,st=out; cap=P['EQ0']+P['topup']; ex=dep-P['EQ0']; en=ec-ex; pk=np.maximum.accumulate(en); px=D.close.values
    up=np.maximum(-nl,0)*P['pv']*px*X; dn=np.maximum(nl,0)*P['pv']*px*X
    return float(np.max(pk-(en-up))/cap*100),float(np.max(pk-(en-dn))/cap*100)
def battery(asset,s,m,nplace=20,full=True):
    D=bt.table(asset); s=np.asarray(s,dtype=np.int64); r={}
    out=bt.run(asset,s,m,D=D); b=q(asset,out); r.update(b); r['nsig']=int((s!=0).sum())
    qq=bt.quick(asset,out,D.index); r['months']=qq['months']; mv=list(qq['months'].values()); r['npos']=int(sum(1 for v in mv if v>0)); r['minm']=float(min(mv))
    P=bt.periods(D)
    for pn in ('A','B'):
        o=bt.run(asset,s,m,P[pn],D=D); x=q(asset,o); r[pn+'_net']=x['net']; r[pn+'_dd']=x['dd_pct']
    r['gapup'],r['gapdn']=gapdd(asset,out,D)
    smul=3.0 if asset=='US500' else 2.0
    x=q(asset,bt.run(asset,s,m,D=D,sprmul=smul,slip=1.0)); r['sx_net']=x['net']; r['sx_dd']=x['dd_pct']
    for cst in ('exness_raw','exness_std'):
        x=q(asset,bt.run(asset,s,m,D=D,cost=cst)); r[cst+'_net']=x['net']; r[cst+'_dd']=x['dd_pct']
    for nm,mult in (('detr',-1.0),('rev',-2.0)):
        Dd=drift_D(D,mult); x=q(asset,bt.run(asset,s,m,D=Dd)); r[nm+'_net']=x['net']; r[nm+'_dd']=x['dd_pct']; r[nm+'_so']=x['so']
    for nm,sd in (('long',np.where(s>0,s,0)),('short',np.where(s<0,s,0))):
        x=q(asset,bt.run(asset,sd,m,D=D)); r[nm+'_net']=x['net']; r[nm+'_dd']=x['dd_pct']
    nets=[]
    for seed in range(nplace):
        x=q(asset,bt.run(asset,flip_runs(s,seed),m,D=D)); nets.append(x['net'])
    r['placebo_pct']=float((np.array(nets)<b['net']).mean()*100); r['placebo_med']=float(np.median(nets)); r['placebo_max']=float(np.max(nets))
    x=q(asset,bt.run(asset,np.r_[np.zeros(2,np.int64),s[:-2]],m,D=D)); r['delay2_net']=x['net']
    return r
