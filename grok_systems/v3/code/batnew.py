import sys,os,json,numpy as np,pandas as pd,multiprocessing as mp
sys.argv=[sys.argv[0],sys.argv[1]]
import newsig as N, bt, battery as B, sig_v3 as S
ASSET=N.ASSET
C={'XAU':[('pd_break_flow','none','all',1),('pd_break_flow','gt20','ldny',1),('lnor_break_trend','gt20','all',1),('lnor_break_trend','gt20','all',0),('asia_break_trend','none','ny',2),('pd_sweep_flow','none','ldny',2),('lnor_break_trend','gt20','ldny',1)],
   'US500':[('orbd_mom','none','all',2),('orbd_mom','gt20','all',1),('orbd_mom','none','ldny',2),('asia_fail','gt20','ldny',2),('poc_rev_2.0','none','all',2)]}[ASSET]
def job(c):
    nm,adx,se,mi=c; D=bt.table(ASSET)
    if 'sp' not in N.G: N.G['sp']=N.specs(D)
    s=S.filters(D,N.G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    r=B.battery(ASSET,s,N.MG[mi]); r.update(sig=nm,adx=adx,sess=se,mg=mi); return r
if __name__=='__main__':
    with mp.Pool(7) as P: res=P.map(job,C,chunksize=1)
    R=pd.DataFrame(res); R['months']=R.months.apply(json.dumps); R.to_parquet(f'/workspace/bt_3m/v3/results/batnew_{ASSET}.parquet')
    pd.set_option('display.width',300); print(R[['sig','adx','sess','mg','net','dd_pct','A_net','B_net','npos','minm','sx_net','exness_raw_net','detr_net','rev_net','long_net','short_net','placebo_pct','placebo_med','gapup','delay2_net','nb']].round(0).to_string())
