import sys,os,json,itertools,time,numpy as np,pandas as pd,multiprocessing as mp
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import newsig as N, newsig2 as N2, bt, sig_v3 as S
ASSET=N.ASSET; cross=N2.cross
def specs3(D):
    C=D.close.values;H=D.high.values;L=D.low.values;O=D.open.values; g=lambda k: np.nan_to_num(D[k].values); cool=N.cool; out={}
    d15=g('d15z'); hr=D.hour.values; mi=D.minute.values
    def mk(up,dn): return cool(cross(up).astype(np.int64)-cross(dn).astype(np.int64))
    for nm in ('g1_15z','g2_15z','g3_15z','sw30z','fz15z','ar15z','ad15z','imb15z'):
        z=g(nm)
        for th in (2.0,3.0):
            out[f'{nm}_mom{th}']=mk(z>th,z<-th); out[f'{nm}_fade{th}']=mk(z<-th,z>th)
    # news drift / fade 10 min after news bar
    nw=D.news.values.astype(bool); lag=np.r_[np.zeros(10,bool),nw[:-10]]; ret10=C-pd.Series(C).shift(10).values
    out['news_mom']=mk(lag&(ret10>0)&(d15>0),lag&(ret10<0)&(d15<0)); out['news_fade']=mk(lag&(ret10<0)&(d15>0),lag&(ret10>0)&(d15<0))
    # session open drives: first 30 min of London (08:00-08:30 utc-ish via hour) direction continuation at +30m / fade
    sess=((hr==8)&(mi==30))|((hr==13)&(mi==0)); r30=C-pd.Series(O).shift(30).values
    out['open_drive']=cool(sess*np.sign(np.nan_to_num(r30))*(np.abs(d15)>0.5)).astype(np.int64); out['open_fade']=-out['open_drive']
    vc=D.vwap_cfd.values; px=C; out['vwap_cross_flow']=mk((px>vc)&(np.r_[px[0],px[:-1]]<=np.r_[vc[0],vc[:-1]])&(d15>0.5),(px<vc)&(np.r_[px[0],px[:-1]]>=np.r_[vc[0],vc[:-1]])&(d15<-0.5))
    hi60=pd.Series(H).rolling(60).max().shift(1).values; lo60=pd.Series(L).rolling(60).min().shift(1).values
    out['hl60_break_flow']=mk((C>hi60)&(d15>0.5),(C<lo60)&(d15<-0.5)); out['hl60_sweep_flow']=cool(-cross((H>hi60)&(C<hi60)&(d15<0)).astype(np.int64)+cross((L<lo60)&(C>lo60)&(d15>0)).astype(np.int64))
    return {k:np.nan_to_num(v).astype(np.int64) for k,v in out.items()}
G={}
def job(a):
    nm,adx,se,mi=a; D=bt.table(ASSET)
    if 'sp' not in G: G['sp']=specs3(D)
    s=S.filters(D,G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    if (s!=0).sum()<30: return None
    m=N.MG[mi]; o=bt.run(ASSET,s,m,D=D); q=bt.quick(ASSET,o,D.index); ec,ew,nl,dep,st=o; P=bt.SPEC[ASSET]; ex=dep-P['EQ0']; en=ec-ex-P['EQ0']; ia=int(np.searchsorted(D.index,bt.A_END))
    mv=list(q['months'].values()); return dict(sig=nm,adx=adx,sess=se,mg=mi,net=q['net'],dd=q['dd_pct'],A=float(en[ia-1]),B=float(en[-1]-en[ia-1]),npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'],nsig=int((s!=0).sum()))
if __name__=='__main__':
    D=bt.table(ASSET); names=list(specs3(D).keys()); jobs=list(itertools.product(names,('none','gt20'),('all','ldny','ny'),range(3)))
    t0=time.time()
    with mp.Pool(4) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for r in res if r]); R.to_parquet(f'/workspace/bt_3m/v3/results/newsig3_{ASSET}.parquet'); print('done',len(R),len(jobs),round(time.time()-t0),flush=True)
