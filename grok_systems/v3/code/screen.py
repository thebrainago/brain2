# Event-level screen: forward net returns (ATR units) of every signal x filter, periods A(Jun1-Aug19) / B(Aug20-Nov26), mirror, flip-placebo.
import sys, os, numpy as np, pandas as pd, multiprocessing as mp, itertools, time
from numba import njit
sys.path.insert(0,os.path.dirname(__file__)); import sig_v3 as S
V='/workspace/bt_3m/v3'; ASSET=sys.argv[1]
HS=(5,15,30,60,120); CD=15
@njit(cache=True)
def pick(s,ok,cd):
    n=len(s); out=np.empty(n,np.int64); k=0; last=-10**9
    for i in range(n-1):
        if s[i]!=0 and ok[i] and i-last>=cd:
            out[k]=i; k+=1; last=i
    return out[:k]
@njit(cache=True)
def fwd(idx,s,o,c,spr,atr,H,cost):
    m=len(idx); r=np.full(m,np.nan)
    for q in range(m):
        i=idx[q]; j=i+1; e=j+H-1
        if e>=len(c) or atr[j]<=0 or np.isnan(atr[j]): continue
        r[q]=(s[i]*(c[e]-o[j])-cost*spr[j])/atr[j]
    return r
G={}
def load():
    for nm,f in (('o',f'{V}/tbl/{ASSET}.parquet'),('m',f'{V}/tbl/{ASSET}_MIRROR.parquet')):
        D=pd.read_parquet(f); A=dict(o=D.open.values,c=D.close.values,spr=D.spread_px.values,atr=np.nan_to_num(D.atr5.values),fut=D.fut_ok.values,aok=D.a_ok.values)
        t=D.index; A['A']=(t<pd.Timestamp('2026-08-20',tz='UTC')); A['mon']=pd.factorize(D.month.values,sort=True)[0]; A['nm']=int(A['mon'].max())+1; G[nm]=(D,A)
    G['specs']=dict(S.specs(ASSET))
rng=np.random.default_rng(1)
def stats(idx,s,A,H,cost=1.5):
    r=fwd(idx,s.astype(np.float64),A['o'],A['c'],A['spr'],A['atr'],H,cost); ok=np.isfinite(r); 
    return idx[ok],r[ok]
def summ(x,pre,d):
    n=len(x)
    d[pre+'n']=n
    d[pre+'m']=float(x.mean()) if n else np.nan
    d[pre+'t']=float(x.mean()/(x.std(ddof=1)/np.sqrt(n))) if n>5 and x.std()>0 else 0.0
    d[pre+'w']=float((x>0).mean()) if n else np.nan
def job(a):
    name,adx,sess=a; D,A=G['o']; fn=G['specs'][name]
    out=dict(sig=name,adx=adx,sess=sess)
    raw=fn(D); s=S.filters(D,raw,adx,sess,ASSET); ok=A['fut']&(A['aok'] if name.startswith(('xlead','xdelta')) else True)
    idx=pick(s.astype(np.int8),ok,CD)
    if len(idx)<20: out['n']=len(idx); return out
    out['n']=len(idx); sd=s[idx].astype(float)
    out['frac_long']=float((sd>0).mean())
    for H in HS:
        ii,r=stats(idx,s,A,H)
        if len(ii)<10: continue
        pa=A['A'][ii]; 
        summ(r,f'h{H}_',out); summ(r[pa],f'h{H}_A_',out); summ(r[~pa],f'h{H}_B_',out)
        dd=s[ii]; summ(r[dd>0],f'h{H}_L_',out); summ(r[dd<0],f'h{H}_S_',out)
        mon=A['mon'][ii]; mm=[r[mon==k].mean() for k in range(A['nm']) if (mon==k).sum()>=5]; out[f'h{H}_mpos']=int(sum(1 for v in mm if v>0)); out[f'h{H}_mn']=len(mm)
        if H in (30,):
            # flip placebo p-value (direction randomisation) on mean
            M=2000 if len(r)<3000 else 500; sgn=rng.choice([-1.0,1.0],size=(len(r),M)); 
            # r already includes cost; reconstruct gross to flip: gross=r+cost*spr/atr
            j=ii+1; cc=1.5*A['spr'][j]/A['atr'][j]; gross=r+cc; null=((gross[:,None]*sgn)-cc[:,None]).mean(0); out['h30_p']=float((null>=r.mean()).mean())
    # mirror
    Dm,Am=G['m']; rm=fn(Dm); sm=S.filters(Dm,rm,adx,sess,ASSET); okm=Am['fut']&(Am['aok'] if name.startswith(('xlead','xdelta')) else True)
    im=pick(sm.astype(np.int8),okm,CD)
    if len(im)>=10:
        for H in (30,):
            ii,r=stats(im,sm,Am,H); 
            if len(ii)>=10: summ(r,'mir30_',out)
    return out
if __name__=='__main__':
    load(); t0=time.time()
    jobs=[(n,a,s) for n in G['specs'] for a in S.GRID_ADX for s in S.GRID_SESS]
    print(ASSET,len(jobs),'jobs',flush=True)
    with mp.Pool(int(os.environ.get('NP','8'))) as P:
        res=P.map(job,jobs,chunksize=8)
    R=pd.DataFrame(res); R.to_parquet(f'{V}/results/screen_{ASSET}.parquet'); print('done',len(R),round(time.time()-t0))
