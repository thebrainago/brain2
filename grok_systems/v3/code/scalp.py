# SL/TP scalp simulator on M1 (adverse-first, gap-through, XM spread + 0.5 spread slip on stops). PYTHON SIMULATION.
import sys, os, numpy as np, pandas as pd, multiprocessing as mp, time, itertools
from numba import njit
sys.path.insert(0,os.path.dirname(__file__)); import sig_v3 as S
V=os.environ.get('V3ROOT','/workspace/bt_3m/v3')
@njit(cache=True)
def sim_one(i,d,o,h,l,c,spr,atr,sl_m,tp_m,hold,slip):
    """enter at open[i+1]; returns (pnl_in_atr, exit_idx). long fills ask=o+spr(+slip), short fills bid=o-slip."""
    j=i+1; n=len(c)
    if j>=n or atr[j]<=0: return np.nan,j
    a=atr[j]; s=spr[j]
    if d>0:
        e=o[j]+s+slip*s; sl=e-sl_m*a; tp=e+tp_m*a
    else:
        e=o[j]-slip*s; sl=e+sl_m*a; tp=e-tp_m*a
    last=min(n-1,j+hold-1)
    for k in range(j,last+1):
        sk=spr[k]
        if d>0:
            # bid-based bars: long SL triggers when bid<=sl ; TP when bid>=tp
            if (o[k]<=sl) : return (o[k]-slip*sk-e)/a,k
            if l[k]<=sl: return (sl-slip*sk-e)/a,k
            if o[k]>=tp: return (o[k]-e)/a,k
            if h[k]>=tp: return (tp-e)/a,k
        else:
            # short exits at ask=bid+spr : SL when ask>=sl ; TP when ask<=tp
            if o[k]+sk>=sl: return (e-(o[k]+sk+slip*sk))/a,k
            if h[k]+sk>=sl: return (e-(sl+slip*sk))/a,k
            if o[k]+sk<=tp: return (e-(o[k]+sk))/a,k
            if l[k]+sk<=tp: return (e-tp)/a,k
    # time exit at close
    sk=spr[last]
    if d>0: return (c[last]-e)/a,last
    return (e-(c[last]+sk))/a,last
@njit(cache=True)
def run_seq(s,ok,o,h,l,c,spr,atr,sl_m,tp_m,hold,slip):
    n=len(c); idx=np.empty(n,np.int64); pn=np.empty(n); ex=np.empty(n,np.int64); k=0; free=0
    for i in range(n-1):
        if i<free or s[i]==0 or not ok[i]: continue
        p,e=sim_one(i,s[i],o,h,l,c,spr,atr,sl_m,tp_m,hold,slip)
        if np.isnan(p): continue
        idx[k]=i; pn[k]=p; ex[k]=e; k+=1; free=e+1
    return idx[:k],pn[:k],ex[:k]
@njit(cache=True)
def run_flip(idx,s,o,h,l,c,spr,atr,sl_m,tp_m,hold,slip):
    out=np.empty(len(idx))
    for q in range(len(idx)):
        i=idx[q]; p,e=sim_one(i,-s[i],o,h,l,c,spr,atr,sl_m,tp_m,hold,slip); out[q]=p
    return out
G={}
def init(asset):
    D=pd.read_parquet(f'{V}/tbl/{asset}.parquet'); G['D']=D; G['asset']=asset
    G['A']=dict(o=D.open.values,h=D.high.values,l=D.low.values,c=D.close.values,spr=D.spread_px.values,atr=np.nan_to_num(D.atr5.values))
    G['isA']=(D.index<pd.Timestamp('2026-08-20',tz='UTC')); G['mon']=pd.factorize(D.month.values,sort=True)[0]; G['specs']=dict(S.specs(asset))
GRID=list(itertools.product((0.5,1.0,1.5,2.0),(0.5,1.0,1.5,2.0,3.0),(30,90)))
def metr(p,pre,d):
    n=len(p); d[pre+'n']=n
    if n==0: d[pre+'e']=np.nan; d[pre+'pf']=np.nan; d[pre+'w']=np.nan; return
    d[pre+'e']=float(p.mean()); w=p[p>0].sum(); ls=-p[p<=0].sum(); d[pre+'pf']=float(w/ls) if ls>0 else 99.0; d[pre+'w']=float((p>0).mean())
def job(a):
    name,adx,sess=a; D=G['D']; A=G['A']; asset=G['asset']
    s=S.filters(D,G['specs'][name](D),adx,sess,asset).astype(np.int64); ok=D.fut_ok.values&(D.a_ok.values if name.startswith(('xlead','xdelta')) else True)
    if (s[ok]!=0).sum()<30: return []
    out=[]
    for sl,tp,hold in GRID:
        idx,pn,ex=run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5)
        if len(idx)<40: continue
        r=dict(sig=name,adx=adx,sess=sess,sl=sl,tp=tp,hold=hold); metr(pn,'',r)
        pa=G['isA'][idx]; metr(pn[pa],'A_',r); metr(pn[~pa],'B_',r)
        dd=s[idx]; metr(pn[dd>0],'L_',r); metr(pn[dd<0],'S_',r)
        mon=G['mon'][idx]; mm=[pn[mon==k].sum() for k in range(int(G['mon'].max())+1)]; r['mpos']=int(sum(1 for v in mm if v>0)); r['mn']=len(mm)
        for k,v in enumerate(mm): r[f'm{k}']=float(v)
        fl=run_flip(idx,s,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5); ok2=np.isfinite(fl)
        x=pn[ok2]; y=fl[ok2]; nn=len(x)
        if nn>10:
            dm=(x-y)/2; z=dm.mean()/(dm.std(ddof=1)/np.sqrt(nn)+1e-12); r['flip_z']=float(z); r['t']=float(x.mean()/(x.std(ddof=1)/np.sqrt(nn)+1e-12))
        out.append(r)
    return out
if __name__=='__main__':
    asset=sys.argv[1]; init(asset); t0=time.time()
    jobs=[(n,a,s) for n in G['specs'] for a in S.GRID_ADX for s in S.GRID_SESS]
    sub=os.environ.get('SUB'); 
    print(asset,len(jobs),'jobs x',len(GRID),flush=True)
    with mp.Pool(int(os.environ.get('NP','8')),initializer=init,initargs=(asset,)) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for rr in res for r in rr]); R.to_parquet(f'{V}/results/scalp_{asset}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
