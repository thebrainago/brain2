# Aggregate stage-2 results: selection on IS only, OOS check, placebo null rate by group.
import sys,glob,numpy as np,pandas as pd
RES='/workspace/bt_3m/fx/results'
def load(tag):
    fs=sorted(glob.glob(f'{RES}/{tag}_*.parquet')); R=pd.concat([pd.read_parquet(f) for f in fs]) if fs else pd.DataFrame()
    if len(R): R['cI']=R.netI/R.ddI.clip(lower=1); R['cO']=R.netO/R.ddO.clip(lower=1); R['grp']=R.sym.map(grp)
    return R
AUD={'AUDUSD#','AUDJPY#','AUDNZD#','AUDCAD#','AUDCHF#','EURAUD#','GBPAUD#'}; NZD={'NZDUSD#','NZDCAD#','NZDJPY#','NZDCHF#','EURNZD#','GBPNZD#'}
def grp(s):
    if s in AUD: return 'AUD'
    if s in NZD: return 'NZD'
    return 'FXother' if s.endswith('#') and 'Cash' not in s and 'SILVER' not in s else 'CFD'
def passes(R,minI=3.0,minO=1.0):
    q=R[R.nb>=R.apply(lambda r:15 if r.sig.startswith('L_') else 60,axis=1)] if len(R) else R
    sel=q[(q.netI>0)&(q.cI>=minI)]; ok=sel[(sel.netO>0)&(sel.cO>=minO)]
    return q,sel,ok
if __name__=='__main__':
    R=load('bask'); q,sel,ok=passes(R)
    print('configs',len(q),'IS>0 %.3f OOS>0 %.3f both %.4f'%((q.netI>0).mean(),(q.netO>0).mean(),((q.netI>0)&(q.netO>0)).mean()))
    print('IS-selected (netI>0 & calmarI>=3):',len(sel),'-> OOS pass (netO>0 & calmarO>=1):',len(ok))
    print(q.groupby('grp').apply(lambda g: pd.Series(dict(n=len(g),isp=(g.netI>0).mean(),oop=(g.netO>0).mean(),both=((g.netI>0)&(g.netO>0)).mean()))).round(3))
    P=load('pl0')
    if len(P):
        qp,selp,okp=passes(P); print('PLACEBO configs',len(qp),'IS>0 %.3f OOS>0 %.3f both %.4f'%((qp.netI>0).mean(),(qp.netO>0).mean(),((qp.netI>0)&(qp.netO>0)).mean()),'IS-sel',len(selp),'OOS pass',len(okp))
    pd.set_option('display.width',250)
    print(ok.sort_values('cO',ascending=False)[['sym','sig','sess','gk','bk','maxN','nb','netI','ddI','netO','ddO','cI','cO','mpos','mn']].head(25).to_string())
