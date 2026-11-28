import pandas as pd,numpy as np,json
P={'PortA':['A_x1_009','A_x2_010','A_u1_10','A_u7_10'],'PortB':['B_x1_005','B_x4_007','B_xs1_057','B_xs2_100','B_u1_26','B_u2_02','B_u6_28','B_u7_50'],
   'PortC':['A_x1_009','A_x2_010','C_x4_004','B_xs1_057','C_xs2_060','B_u1_26','B_u2_02','B_u6_28','C_u7_30'],
   'PortB_half_est':None}
CAPS={'x':30000.,'u':10000.}
out={}
E={}
def load(n): 
    if n not in E: E[n]=pd.read_parquet(f'eq_v3b_{n}.parquet')
    return E[n]
for name,L in P.items():
    if not L: continue
    dfs=[load(n) for n in L]; idx=dfs[0].index
    for d in dfs[1:]: idx=idx.union(d.index)
    ec=sum(d.ec.reindex(idx).ffill().fillna(0) for d in dfs); ew=sum(d.ew.reindex(idx).ffill().fillna(0) for d in dfs)
    cap=sum(CAPS[c] for c in {n[2] if n[0] in 'ABC S'.replace(' ','') and n[1]=='_' else n[0] for n in L})
    cap=30000*any('_x' in n for n in L)+10000*any('_u' in n for n in L)
    pk=np.maximum.accumulate(ec.values); dd=float(np.max(pk-ew.values)); i=int(np.argmax(pk-ew.values))
    mon=ec.groupby(idx.strftime('%Y-%m')).last(); mn=mon.diff(); mn.iloc[0]=mon.iloc[0]
    a=pd.Timestamp('2026-08-20',tz='UTC'); iA=idx.searchsorted(a)
    out[name]=dict(cap=cap,net=float(ec.iloc[-1]),dd_abs=dd,dd_pct_cap=dd/cap*100,dd_time=str(idx[i]),A=float(ec.iloc[iA-1]),B=float(ec.iloc[-1]-ec.iloc[iA-1]),months=[round(float(v)) for v in mn],sum_component_dd=sum(float(np.max(np.maximum.accumulate(d.ec.values)-d.ew.values)) for d in dfs))
    # half lot (linear) estimate
    ec2=ec*0.5; ew2=ew*0.5; out[name]['half_dd_pct']=float(np.max(np.maximum.accumulate(ec2.values)-ew2.values))/cap*100; out[name]['half_net']=float(ec2.iloc[-1])
    print(name,{k:(round(v,1) if isinstance(v,float) else v) for k,v in out[name].items()})
json.dump(out,open('joint_mt5.json','w'),indent=1)
