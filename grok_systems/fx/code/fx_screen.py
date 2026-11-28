# Stage 1: scalp (SL/TP ATR-multiple) screen of every signal x session x exit-grid, IS vs OOS, flip (mirror) test. Usage: fx_screen.py SYM [SYM..]
import sys,os,itertools,time,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code')
import fxlib as F, fxsig as G
PEER={'AUDUSD#':'NZDUSD#','NZDUSD#':'AUDUSD#','AUDCAD#':'NZDCAD#','NZDCAD#':'AUDCAD#','AUDJPY#':'NZDJPY#','NZDJPY#':'AUDJPY#','AUDCHF#':'NZDCHF#','NZDCHF#':'AUDCHF#','EURAUD#':'EURNZD#','EURNZD#':'EURAUD#','GBPAUD#':'GBPNZD#','GBPNZD#':'GBPAUD#','AUDNZD#':'AUDUSD#',
      'EURUSD#':'GBPUSD#','GBPUSD#':'EURUSD#','USDCAD#':'USDCHF#','USDCHF#':'USDCAD#','EURJPY#':'GBPJPY#','GBPJPY#':'EURJPY#','US100Cash#':'US30Cash#','US30Cash#':'US100Cash#','BRENTCash#':'OILCash#','OILCash#':'BRENTCash#'}
GRID=list(itertools.product((1.0,2.0),(0.5,1.0,2.0),(240,1440)))
def metr(p,pre,d):
    n=len(p); d[pre+'n']=n
    if n==0: d[pre+'e']=np.nan; d[pre+'pf']=np.nan; d[pre+'t']=np.nan; return
    d[pre+'e']=float(p.mean()); w=p[p>0].sum(); ls=-p[p<=0].sum(); d[pre+'pf']=float(w/ls) if ls>0 else 99.0
    d[pre+'t']=float(p.mean()/(p.std(ddof=1)/np.sqrt(n)+1e-12)) if n>2 else np.nan
def screen(sym):
    D=F.table(sym); pe=F.table(PEER[sym]) if sym in PEER and os.path.exists(f'{F.DATA}/{F.fname(PEER[sym])}.npz') else None
    S=G.build(D,pe); o=D.open.values;h=D.high.values;l=D.low.values;c=D.close.values;sp=D.spread_px.values;at=np.nan_to_num(D.atr60.values)
    isI=(D.index<F.IS_END); mon=pd.factorize(D.index.strftime('%Y-%m'),sort=True)[0]; out=[]
    sm={k:G.sess_mask(D,k) for k in G.SESS}
    for nm,s in S.items():
        s=s.astype(np.int64)
        for sk,mk in sm.items():
            ok=mk
            if (s[ok]!=0).sum()<60: continue
            for sl,tp,hold in GRID:
                idx,pn,ex=F.run_seq(s,ok,o,h,l,c,sp,at,sl,tp,hold,0.5)
                if len(idx)<60: continue
                r=dict(sym=sym,sig=nm,sess=sk,sl=sl,tp=tp,hold=hold); metr(pn,'',r); a=isI[idx]; metr(pn[a],'I_',r); metr(pn[~a],'O_',r)
                dd=s[idx]; metr(pn[dd>0],'L_',r); metr(pn[dd<0],'S_',r)
                fl=F.run_flip(idx,s,o,h,l,c,sp,at,sl,tp,hold,0.5); ok2=np.isfinite(fl); x=pn[ok2]; y=fl[ok2]
                if len(x)>10: dm=(x-y)/2; r['flip_z']=float(dm.mean()/(dm.std(ddof=1)/np.sqrt(len(x))+1e-12)); ai=isI[idx][ok2]; r['I_flip_z']=float(dm[ai].mean()/(dm[ai].std(ddof=1)/np.sqrt(max(ai.sum(),2))+1e-12)) if ai.sum()>10 else np.nan
                mm=[pn[mon[idx]==k].sum() for k in range(int(mon.max())+1)]; r['mpos']=int(sum(1 for v in mm if v>0)); r['mn']=len(mm)
                out.append(r)
    R=pd.DataFrame(out); R.to_parquet(f'{F.RES}/screen_{F.fname(sym)}.parquet'); return len(R)
if __name__=='__main__':
    for s in sys.argv[1:]:
        t=time.time(); n=screen(s); print(s,n,round(time.time()-t),flush=True)
