# Build MT5 entries CSV (EA CSV mode) for an FX basket candidate over the OOS window + python expectation via engine_export (no weekend flat, same as EA r0).
import sys,json,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code'); sys.path.insert(0,'/workspace/bt_3m/code')
import fxlib as F, fx_battery as B, engine2x as EE
def prep(sym,sig,sess,gk,bk,mN,name,lot=1.0):
    D=F.table(sym); I=F.info(sym); iso=int(np.searchsorted(D.index,F.IS_END)); med=float(D.atr60.iloc[:iso].median()); s=B.getsig(sym,sig,sess,D)
    P=F.mvec(I['pv'],I['swl'],I['sws'],L0=lot,gap=gk*med,gatr=gk,btp=bk*med,maxN=mN)
    fl=F.flat_arr(D)
    sl=slice(iso,None); d=D.iloc[sl]
    out=EE.run(d.open.values,d.high.values,d.low.values,d.close.values,d.spread_px.values,np.nan_to_num(d.atr60.values),np.ascontiguousarray(s[sl],dtype=np.int64),d.rollover.values,d.dow.values.astype(np.int64),fl[sl],P)
    opn=out[0]; ix=np.nonzero(opn)[0]; t=d.index[ix]; srv=t.tz_convert('Europe/Athens').tz_localize(None)
    df=pd.DataFrame({'thoi_gian':srv.strftime('%Y.%m.%d %H:%M:%S'),'ma':sym,'chieu':opn[ix],'gia':d.open.values[ix].round(3),'nguon':name,'lot':lot})
    df.to_csv(f'{F.FX}/mt5/{name}_mt5.csv',index=False,lineterminator='\n')
    ec=out[1]-1e7; ew=out[2]-1e7; pk=np.maximum.accumulate(ec)
    exp=dict(name=name,sym=sym,entries=len(df),py_net=float(ec[-1]),py_dd=float(np.max(pk-ew)),py_nb=int(out[5][0]),med=med,gk=gk,bk=bk,maxN=mN)
    print(exp); return exp,df
if __name__=='__main__':
    import os; os.makedirs(f'{F.FX}/mt5',exist_ok=True)
    e,df=prep('NZDJPY#','L_ibs_240','ldn',1.0,2.0,3,'fx_nzdjpy_ibs240_ldn'); json.dump(e,open(f'{F.FX}/mt5/exp_nzdjpy.json','w'))
    print(df.head(3))
