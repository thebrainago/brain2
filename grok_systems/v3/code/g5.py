# Round 5 stage1: risk-stop variant grid per system at REF lots. Checkpoint: results/r5/grid_<sys>.csv
import sys,os,itertools,numpy as np,pandas as pd,r5lib as R,bt
names=sys.argv[1:] or list(R.REF)
def ddf(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
for n in names:
    f=f'{R.R5}/grid_{n}.csv'
    if os.path.exists(f): continue
    a,k,p,m=R.S[n]; D=bt.table(a); z=np.zeros(len(D),np.int64); fl2=R.flat_arr(D,mode=2); px=D.close.values; pv=bt.SPEC[a]['pv']; cap=R.CAPA[a]
    t=D.index.values; brk=np.r_[(np.diff(t).astype('timedelta64[m]').astype(int)>300),False]   # last bar before >5h break
    rows=[]
    for fm,hsk,hs,dl,mn in itertools.product((0,2),(0,0.5,1,2),(0,4,6,8,12),(0,3,5),(0,-1)):
        N=None if mn==0 else max(2,m['maxN']-1)
        fl=z if fm==0 else fl2
        kw=dict(hsk=hsk,hs_pct=hs,dl_pct=dl,maxN=N)
        o=R.run2(n,D,fl,**kw); ec,ew,nl=o['ec'],o['ew'],o['nl']
        o2=R.run2(n,D,fl,sprmul=2.0,slip=1.0,**kw)
        exp=np.abs(nl)*px*pv; pk=np.maximum.accumulate(ec)
        g5=float(np.max(pk-(ew-exp*0.05))); wk=np.where(brk)[0]; w5=max(ddf(ec,ew),float(np.max(pk[wk]-(ec[wk]-exp[wk]*0.05)))) if len(wk) else ddf(ec,ew)
        w10=max(ddf(ec,ew),float(np.max(pk[wk]-(ec[wk]-exp[wk]*0.10)))) if len(wk) else ddf(ec,ew)
        mon=pd.Series(ec,index=D.index).resample('MS').last().diff().fillna(ec[0]) if False else None
        rows.append(dict(sys=n,flat=fm,hsk=hsk,hs=hs,dl=dl,minusN=mn,net=ec[-1],dd=ddf(ec,ew)/cap*100,sx2net=o2['ec'][-1],sx2dd=ddf(o2['ec'],o2['ew'])/cap*100,
            gap5=g5/cap*100,wk5=w5/cap*100,wk10=w10/cap*100,maxexp=exp.max()/cap*100,nb=o['st'][0],nhs=o['st'][9],nfl=o['st'][10],ndl=o['st'][11]))
    pd.DataFrame(rows).to_csv(f,index=False); print('done',n,flush=True)
print('G5 DONE')
