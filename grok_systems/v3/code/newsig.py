import sys,os,json,numpy as np,pandas as pd,multiprocessing as mp,time
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,sig_v3 as S,battery as B
ASSET=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] in ('XAU','US500') else 'XAU'
def ev(c): 
    return c
def cross(cond):
    c=np.asarray(cond,bool); prev=np.r_[False,c[:-1]]; e=c&~prev; return e
def cool(s,n=10):
    out=np.zeros_like(s); last=-10**9
    for i in np.nonzero(s)[0]:
        if i-last>=n: out[i]=s[i]; last=i
    return out
def specs(D):
    C=D.close.values;H=D.high.values;L=D.low.values; g=lambda k: np.nan_to_num(D[k].values); d15=g('d15z'); d30=g('d30z'); atr=np.nan_to_num(D.atrh1.values)+1e-9
    out={}
    def mk(up,dn): return cool((cross(up).astype(np.int64)-cross(dn).astype(np.int64)))
    nh,nl=D.nyor_hi.values,D.nyor_lo.values
    out['orbd_mom']=mk((C>nh)&(d15>0.5),(C<nl)&(d15<-0.5)); out['orbd_fade']=mk((H>nh)&(C<nh)&(d15<-0.5)&~np.isnan(nh),(L<nl)&(C>nl)&(d15>0.5)&~np.isnan(nl))
    out['orbd_fade']=-0*out['orbd_fade']+out['orbd_fade']*0+ (cool(cross((H>nh)&(C<nh)&(d15<-0.5)&~np.isnan(nh)).astype(np.int64)*-1+cross((L<nl)&(C>nl)&(d15>0.5)&~np.isnan(nl)).astype(np.int64)))
    ph,pl=D.pdH.values,D.pdL.values
    out['pd_sweep_flow']=cool(-cross((H>ph)&(C<ph)&(d15<0)).astype(np.int64)+cross((L<pl)&(C>pl)&(d15>0)).astype(np.int64))
    out['pd_break_flow']=mk((C>ph)&(d15>1),(C<pl)&(d15<-1))
    dev=(C-D.poc_p.values)/atr
    for th in (1.2,2.0): out[f'poc_rev_{th}']=cool(-cross((dev>th)&(d15<0)).astype(np.int64)+cross((dev<-th)&(d15>0)).astype(np.int64))
    vz=g('vwap_z')
    for th in (2.2,3.0): out[f'vwapflow_{th}']=cool(-cross((vz>th)&(d15<-0.5)).astype(np.int64)+cross((vz<-th)&(d15>0.5)).astype(np.int64))
    side=D.ema55_side.values; ah,al=D.as_hi.values,D.as_lo.values; lh,ll=D.lnor_hi.values,D.lnor_lo.values
    out['asia_break_trend']=mk((C>ah)&(side>0),(C<al)&(side<0)); out['lnor_break_trend']=mk((C>lh)&(side>0),(C<ll)&(side<0))
    out['asia_fail']=cool(-cross((H>ah)&(C<ah)).astype(np.int64)+cross((L<al)&(C>al)).astype(np.int64))
    vr=g('vr5'); out['volspike_fade']=cool(-cross((vr>3)&(C>D.open.values)&(d15<0)).astype(np.int64)+cross((vr>3)&(C<D.open.values)&(d15>0)).astype(np.int64))
    return {k:np.nan_to_num(v).astype(np.int64) for k,v in out.items()}
G={}
def job(a):
    nm,adx,se,mi=a; D=bt.table(ASSET); 
    if 'sp' not in G: G['sp']=specs(D)
    s=S.filters(D,G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    if (s!=0).sum()<30: return None
    m=BG.mgs.__wrapped__(ASSET)[mi] if False else MG[mi]
    o=bt.run(ASSET,s,m,D=D); q=bt.quick(ASSET,o,D.index); ec,ew,nl,dep,st=o; P=bt.SPEC[ASSET]; ex=dep-P['EQ0']; en=ec-ex-P['EQ0']; ia=int(np.searchsorted(D.index,bt.A_END))
    mv=list(q['months'].values()); return dict(sig=nm,adx=adx,sess=se,mg=mi,net=q['net'],dd=q['dd_pct'],A=float(en[ia-1]),B=float(en[-1]-en[ia-1]),npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'],nsig=int((s!=0).sum()))
if ASSET=='XAU':
    MG=[dict(L0=0.03,mult=1.0,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=0,hedge=0,cd=30),dict(L0=0.03,mult=1.0,gap=4,gstep=1.4,maxN=3,btp=2,trim=0,prune=0,hedge=0,cd=30),dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30)]
else:
    MG=[dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30),dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30),dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30)]
if __name__=='__main__':
    import itertools
    D=bt.table(ASSET); names=list(specs(D).keys()); jobs=list(itertools.product(names,('none','gt20'),('all','ldny','ny'),range(3)))
    t0=time.time()
    with mp.Pool(8) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for r in res if r]); R.to_parquet(f'/workspace/bt_3m/v3/results/newsig_{ASSET}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
