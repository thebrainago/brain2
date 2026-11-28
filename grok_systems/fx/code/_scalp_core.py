import numpy as np
from numba import njit
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
