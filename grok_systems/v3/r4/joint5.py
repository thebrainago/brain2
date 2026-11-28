import sys,os,glob,json,numpy as np,pandas as pd
sys.path.insert(0,'.'); import mt5eq as M
EQ={}
def eq(nm):
    if nm in EQ: return EQ[nm]
    f=f'eq_{nm}.parquet'
    if os.path.exists(f): EQ[nm]=pd.read_parquet(f); return EQ[nm]
    a='XAU' if any(f'_{k}_' in nm for k in ('x1','x4','g1','g2','g3','g4','xs1','xs2')) else 'US500'
    w,c,b=M.recon(f'deals/{nm}.csv',a); d=pd.DataFrame({'ew':w,'ec':c}); d.to_parquet(f); EQ[nm]=d; return d
CAP={'x':30000.,'u':10000.}
def isx(nm): return any(f'_{k}_' in nm for k in ('x1','x4','g1','g2','g3','g4','xs1','xs2'))
def joint(names,scale=None,lab=''):
    scale=scale or {}; dfs=[(eq(n),scale.get(n,1.0)) for n in names]; idx=dfs[0][0].index
    for d,_ in dfs[1:]: idx=idx.union(d.index)
    ec=sum(s*d.ec.reindex(idx).ffill().fillna(0) for d,s in dfs); ew=sum(s*d.ew.reindex(idx).ffill().fillna(0) for d,s in dfs)
    cap=30000*any(isx(n) for n in names)+10000*any(not isx(n) for n in names)
    pk=np.maximum.accumulate(ec.values); ddv=pk-ew.values; dd=float(ddv.max()); i=int(ddv.argmax())
    mon=ec.groupby(idx.strftime('%Y-%m')).last(); mn=mon.diff(); mn.iloc[0]=mon.iloc[0]; iA=idx.searchsorted(pd.Timestamp('2026-08-20',tz='UTC'))
    comp=sum(s*float(np.max(np.maximum.accumulate(d.ec.values)-d.ew.values)) for d,s in dfs)
    return dict(label=lab,cap=cap,net=float(ec.iloc[-1]),dd_abs=dd,dd_pct=dd/cap*100,dd_time=str(idx[i]),A=float(ec.iloc[iA-1]),B=float(ec.iloc[-1]-ec.iloc[iA-1]),months=[round(float(v)) for v in mn],npos=int((mn>0).sum()),sum_comp_dd=comp,n=len(names))
if __name__=='__main__':
    have={os.path.basename(f)[:-4] for f in glob.glob('deals/v5_*.csv')}
    P={'NEW4':[n for n in have if n.startswith('v5_N4_')],'PortD_G30':[n for n in have if n.startswith('v5_G30_')],'PortD_G40':[n for n in have if n.startswith('v5_G40_')]}
    P['PortD_G30+new']=P['PortD_G30']+[n for n in have if n.startswith('v5_n_')]
    out={}
    for k,v in P.items():
        if not v: continue
        r=joint(sorted(v),lab=k); h=joint(sorted(v),{n:0.5 for n in v},lab=k+'_half'); r['half']=dict(net=h['net'],dd_pct=h['dd_pct'],dd_abs=h['dd_abs']); r['jobs']=sorted(v); out[k]=r
        print(k,len(v),{x:(round(y,1) if isinstance(y,float) else y) for x,y in r.items() if x not in('jobs','dd_time')},flush=True)
    json.dump(out,open('joint5.json','w'),indent=1)
