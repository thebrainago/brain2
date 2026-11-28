import sys,os,json,numpy as np,pandas as pd,multiprocessing as mp
a=sys.argv[1]; sys.argv=[sys.argv[0],a]
import newsig4 as N4, newsig as N, bt, battery as B, sig_v3 as S
ASSET=N4.ASSET; TOP=int(os.environ.get('TOP','12'))
def cands():
    R=pd.read_parquet(f'/workspace/bt_3m/v3/results/newsig4_{ASSET}.parquet'); R['score']=R[['A','B']].min(axis=1)
    q=R[(R.A>0)&(R.B>0)&(R.npos>=5)&(R.dd<20)&(R.so==0)].sort_values('score',ascending=False).drop_duplicates('sig').head(TOP)
    return [tuple(x) for x in q[['sig','adx','sess','mg']].values]
def job(c):
    nm,adx,se,mi=c; D=bt.table(ASSET)
    if 'sp' not in N4.G: N4.G['sp']=N4.specs4(D)
    s=S.filters(D,N4.G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    r=B.battery(ASSET,s,N.MG[int(mi)]); r.update(sig=nm,adx=adx,sess=se,mg=int(mi)); return r
if __name__=='__main__':
    C=cands(); print(ASSET,C,flush=True)
    with mp.Pool(int(os.environ.get('NP','3'))) as P: res=P.map(job,C,chunksize=1)
    R=pd.DataFrame(res); R['months']=R.months.apply(json.dumps); R.to_parquet(f'/workspace/bt_3m/v3/results/r6/batnew4_{ASSET}.parquet')
    pd.set_option('display.width',300); print(R[['sig','adx','sess','mg','net','dd_pct','A_net','B_net','npos','sx_net','detr_net','rev_net','long_net','short_net','placebo_pct','placebo_med','delay2_net','gapup','nb']].round(0).to_string())
