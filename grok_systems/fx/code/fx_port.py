# Portfolio impact of an FX candidate on the proxy Gold+SP500 book (v5_G30 set, 12 systems, M1 equity at their own lots), window 2026-06-01..2026-11-27.
import sys,json,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code'); import fxlib as F, fx_battery as B
R4='/workspace/bt_3m/v3/r4'; import glob
names=[f for f in sorted(glob.glob(f'{R4}/eq_v5_G30_*.parquet'))]
ecs=[pd.read_parquet(f) for f in names]; idx=ecs[0].index
for d in ecs[1:]: idx=idx.union(d.index)
bec=sum(d.ec.reindex(idx).ffill().fillna(0) for d in ecs); bew=sum(d.ew.reindex(idx).ffill().fillna(0) for d in ecs)
def curve(sym,sig,sess,gk,bk,mN,lot):
    D=F.table(sym); I=F.info(sym); iso=int(np.searchsorted(D.index,F.IS_END)); med=float(D.atr60.iloc[:iso].median()); s=B.getsig(sym,sig,sess,D)
    o=B.one(D,s,I,med,gk,bk,mN,fl=F.flat_arr(D)); ec,ew,nl,dep,st=o
    e=pd.DataFrame({'ec':(ec-1e7)*lot,'ew':(ew-1e7)*lot},index=D.index); return e
def dd(ec,ew): pk=np.maximum.accumulate(ec); return float(np.max(pk-ew))
cap=100000.
print('proxy book (v5_G30, 12 sys): net %.0f dd %.0f (%.1f%% of 100k)'%(bec.iloc[-1]-bec.iloc[0],dd(bec.values,bew.values),dd(bec.values,bew.values)/cap*100))
out=[]
for cfg in (('NZDJPY#','L_ibs_240','ldn',1.0,2.0,3),('EURAUD#','L_z240_50_2.0','ny',2.0,1.0,3)):
    e=curve(*cfg,1.0); e=e[e.index>=idx[0]]; e=e.reindex(idx,method='ffill').fillna(0); e=e-e.iloc[0]
    dday=lambda s: s.groupby(s.index.floor('1D')).last().diff().dropna()
    cb=dday(bec).corr(dday(e.ec)); fxdd=dd(e.ec.values,e.ew.values)
    lot=0.05*cap/max(fxdd,1)    # lot so that the FX sleeve alone has DD=5% of 100k
    J_ec=bec+e.ec*lot; J_ew=bew+e.ew*lot
    r=dict(cfg=cfg,corr_daily=float(cb),fx_net_lot1=float(e.ec.iloc[-1]),fx_dd_lot1=fxdd,lot_for_5pct=lot,fx_net_scaled=float(e.ec.iloc[-1]*lot),book_dd=dd(bec.values,bew.values),joint_dd=dd(J_ec.values,J_ew.values),joint_net=float(J_ec.iloc[-1]-J_ec.iloc[0]),book_net=float(bec.iloc[-1]-bec.iloc[0]))
    r['cent100_lot_std']=float(5.0/max(fxdd,1)); r['cent100_net_6m']=float(e.ec.iloc[-1]*5.0/max(fxdd,1)); out.append(r); print({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
json.dump(out,open(f'{F.RES}/port_fx.json','w'),indent=1,default=str)
