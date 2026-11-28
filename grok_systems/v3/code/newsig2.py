import sys,os,json,itertools,time,numpy as np,pandas as pd,multiprocessing as mp
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import newsig as N, bt, sig_v3 as S
ASSET=N.ASSET
def cross(c): c=np.asarray(c,bool); return c&~np.r_[False,c[:-1]]
def specs2(D):
    C=D.close.values;H=D.high.values;L=D.low.values;O=D.open.values; g=lambda k: np.nan_to_num(D[k].values); d15=g('d15z'); d30=g('d30z'); side=D.ema55_side.values
    cool=N.cool; out={}
    def mk(up,dn): return cool(cross(up).astype(np.int64)-cross(dn).astype(np.int64))
    def fade(hi,lo): return cool(-cross(hi).astype(np.int64)+cross(lo).astype(np.int64))
    step=50.0; R=np.round(np.r_[C[0],C[:-1]]/step)*step
    for st in (25.0,50.0):
        R=np.round(np.r_[C[0],C[:-1]]/st)*st
        out[f'rnd_sweep_{int(st)}']=fade((H>R)&(C<R)&(d15<0)&(np.r_[C[0],C[:-1]]<R),(L<R)&(C>R)&(d15>0)&(np.r_[C[0],C[:-1]]>R))
        out[f'rnd_break_{int(st)}']=mk((C>R)&(np.r_[C[0],C[:-1]]<=R)&(d15>0.5),(C<R)&(np.r_[C[0],C[:-1]]>=R)&(d15<-0.5))
    # prior-week high/low (UTC week)
    wk=D.index.to_period('W'); gh=pd.Series(H,index=D.index).groupby(wk).max(); gl=pd.Series(L,index=D.index).groupby(wk).min()
    pwh=pd.Series(wk).map(gh.shift(1)).values; pwl=pd.Series(wk).map(gl.shift(1)).values
    out['pw_break_flow']=mk((C>pwh)&(d15>0.5),(C<pwl)&(d15<-0.5)); out['pw_sweep_flow']=fade((H>pwh)&(C<pwh)&(d15<0),(L<pwl)&(C>pwl)&(d15>0))
    # cvd divergence: new 60-min price extreme but cvd60 below its previous 60-min extreme
    hi60=pd.Series(H).rolling(60).max().shift(1).values; lo60=pd.Series(L).rolling(60).min().shift(1).values
    cv=pd.Series(g('cvd60')); cvhi=cv.rolling(60).max().shift(1).values; cvlo=cv.rolling(60).min().shift(1).values
    out['div_fade']=fade((H>hi60)&(cv.values<cvhi*0.9+0.1*cvlo)&(d15<0),(L<lo60)&(cv.values>cvlo*0.9+0.1*cvhi)&(d15>0))
    out['div_mom']=mk((H>hi60)&(cv.values>=cvhi)&(d15>0.5),(L<lo60)&(cv.values<=cvlo)&(d15<-0.5))
    # squeeze breakout (ATR5 low percentile over 500 bars) with 30m high/low break + flow
    a5=pd.Series(g('atr5')); pr=a5.rolling(500).rank(pct=True).shift(1).values; h30=D.hi30.shift(1).values; l30=D.lo30.shift(1).values
    sq=pr<0.25
    out['squeeze_break']=mk(sq&(C>h30)&(d15>0.3),sq&(C<l30)&(d15<-0.3))
    # trend pullback with flow: ema55 side + pullback through ema20 + flow resumes
    e20=D.ema20.values
    out['pb_flow']=mk((side>0)&(C>e20)&(np.r_[C[0],C[:-1]]<=np.r_[e20[0],e20[:-1]])&(d15>0),(side<0)&(C<e20)&(np.r_[C[0],C[:-1]]>=np.r_[e20[0],e20[:-1]])&(d15<0))
    # basis z (futures-CFD basis) extreme -> fade CFD vs vwap_cfd
    bs=pd.Series(g('basis')); z=((bs-bs.rolling(600).mean())/(bs.rolling(600).std()+1e-9)).fillna(0).values
    out['basis_rev']=fade((z>2.0)&(d15<0),(z<-2.0)&(d15>0)); out['basis_mom']=mk((z>2.0)&(d15>0.5),(z<-2.0)&(d15<-0.5))
    # day-extension fail: late-session break of today's high/low that fails
    out['day_ext_fail']=fade((H>D.dH.shift(1).values)&(C<D.dH.shift(1).values)&(d15<0),(L<D.dL.shift(1).values)&(C>D.dL.shift(1).values)&(d15>0))
    # ibs of prior day: bias continuation at London open
    ib=D.ibs_prev.values; hr=D.hour.values; first=(hr==8)&(np.r_[0,hr[:-1]]!=8)
    out['ibs_rev']=cool(first*(ib<0.2)*1-(first*(ib>0.8)*1))
    return {k:np.nan_to_num(v).astype(np.int64) for k,v in out.items()}
G={}
def job(a):
    nm,adx,se,mi=a; D=bt.table(ASSET)
    if 'sp' not in G: G['sp']=specs2(D)
    s=S.filters(D,G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    if (s!=0).sum()<30: return None
    m=N.MG[mi]; o=bt.run(ASSET,s,m,D=D); q=bt.quick(ASSET,o,D.index); ec,ew,nl,dep,st=o; P=bt.SPEC[ASSET]; ex=dep-P['EQ0']; en=ec-ex-P['EQ0']; ia=int(np.searchsorted(D.index,bt.A_END))
    mv=list(q['months'].values()); return dict(sig=nm,adx=adx,sess=se,mg=mi,net=q['net'],dd=q['dd_pct'],A=float(en[ia-1]),B=float(en[-1]-en[ia-1]),npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'],nsig=int((s!=0).sum()))
if __name__=='__main__':
    D=bt.table(ASSET); names=list(specs2(D).keys()); jobs=list(itertools.product(names,('none','gt20'),('all','ldny','ny'),range(3)))
    t0=time.time()
    with mp.Pool(4) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for r in res if r]); R.to_parquet(f'/workspace/bt_3m/v3/results/newsig2_{ASSET}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
