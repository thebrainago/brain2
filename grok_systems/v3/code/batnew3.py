import sys,os,json,numpy as np,pandas as pd,multiprocessing as mp
a=sys.argv[1]; sys.argv=[sys.argv[0],a]
import newsig3 as N2, newsig as N, bt, battery as B, sig_v3 as S
ASSET=N2.ASSET
C={'XAU':[('imb15z_fade2.0','gt20','all',0),('imb15z_fade2.0','gt20','all',1),('ad15z_fade2.0','none','ny',2),('sw30z_fade2.0','gt20','all',2),('g2_15z_mom3.0','gt20','all',2),('fz15z_mom3.0','none','ldny',2),('sw30z_mom3.0','none','all',2),('fz15z_fade2.0','none','ldny',0)],
   'US500':[('imb15z_mom2.0','gt20','all',0),('imb15z_mom2.0','gt20','all',1),('sw30z_fade2.0','none','all',0),('g3_15z_fade3.0','none','all',2),('hl60_break_flow','gt20','ldny',1),('g3_15z_fade2.0','none','ny',2)]}[ASSET]
def job(c):
    nm,adx,se,mi=c; D=bt.table(ASSET)
    if 'sp' not in N2.G: N2.G['sp']=N2.specs3(D)
    s=S.filters(D,N2.G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    r=B.battery(ASSET,s,N.MG[mi]); r.update(sig=nm,adx=adx,sess=se,mg=mi); return r
if __name__=='__main__':
    with mp.Pool(4) as P: res=P.map(job,C,chunksize=1)
    R=pd.DataFrame(res); R['months']=R.months.apply(json.dumps); R.to_parquet(f'/workspace/bt_3m/v3/results/batnew3_{ASSET}.parquet')
    pd.set_option('display.width',300); print(R[['sig','adx','sess','mg','net','dd_pct','A_net','B_net','npos','minm','sx_net','exness_raw_net','detr_net','rev_net','long_net','short_net','placebo_pct','gapup','delay2_net','nb']].round(0).to_string())
