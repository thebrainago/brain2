# Round 6: untried signal families (coverage gaps). PYTHON SIMULATION screen.
import sys,os,json,itertools,time,numpy as np,pandas as pd,multiprocessing as mp
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import newsig as N, newsig2 as N2, bt, sig_v3 as S
ASSET=N.ASSET; cross=N2.cross; cool=N.cool
def first_per_day(s,day):
    out=np.zeros_like(s); seen=set()
    for i in np.nonzero(s)[0]:
        k=(day[i],int(np.sign(s[i])))
        if k not in seen: seen.add(k); out[i]=s[i]
    return out
def specs4(D):
    C=D.close.values;H=D.high.values;L=D.low.values;O=D.open.values; g=lambda k: np.nan_to_num(D[k].values); out={}
    d15=g('d15z'); atr=np.nan_to_num(D.atrh1.values)+1e-9; a5=np.nan_to_num(D.atr5.values)+1e-9; day=D.nyday.values
    def mk(up,dn): return cool(cross(up).astype(np.int64)-cross(dn).astype(np.int64))
    # 1 naked prior-day POC first touch (fade = reject, break = through with flow)
    p=D.poc_p.values; dh=D.dH.values; dl=D.dL.values; naked=(p<dh)==False; nk=~((dl<=p)&(dh>=p))  # not yet touched today (excl current bar)
    tu=(H>=p)&(L<=p)&nk&~np.isnan(p)
    frm_above=C>p
    out['npoc_fade']=cool(np.where(tu&(np.r_[C[0],C[:-1]]>p)&(d15>0),1,np.where(tu&(np.r_[C[0],C[:-1]]<p)&(d15<0),-1,0)))
    out['npoc_break']=cool(np.where(tu&(np.r_[C[0],C[:-1]]>p)&(C<p)&(d15<-0.5),-1,np.where(tu&(np.r_[C[0],C[:-1]]<p)&(C>p)&(d15>0.5),1,0)))
    # 2 value-area 80% rule: re-enter prior VA from outside after open outside -> toward other side
    vah=D.vah_p.values; val=D.val_p.values; dopen=pd.Series(O).groupby(day).transform('first').values
    oa=dopen>vah; ob=dopen<val; inva=(C<vah)&(C>val)
    out['va80_mom']=first_per_day(mk(ob&inva&(d15>0),oa&inva&(d15<0)),day); out['va80_fade']=-out['va80_mom']
    # 3 gap vs prior close at day open
    pdC=D.pdC.values; gp=(dopen-pdC)/atr; isopen=pd.Series(np.arange(len(C))).groupby(day).transform('first').values==np.arange(len(C))
    for k in (1.0,2.0):
        s=np.where(isopen&(gp>k),-1,np.where(isopen&(gp<-k),1,0)); s=np.r_[np.zeros(5,np.int64),s[:-5]]
        out[f'gapfill_{k}']=s; out[f'gapgo_{k}']=-s
    # 4 narrow-range prior day -> break pdH/pdL with flow
    dd=D.groupby('nyday').agg(H=('high','max'),L=('low','min')); rg=(dd.H-dd.L); nr=(rg<0.7*rg.rolling(10,min_periods=5).mean()).shift(1)
    isnr=pd.Series(day).map(nr).fillna(False).values.astype(bool); ph=D.pdH.values; pl=D.pdL.values
    out['nr_break']=first_per_day(mk(isnr&(C>ph)&(d15>0.5),isnr&(C<pl)&(d15<-0.5)),day); out['nr_fail']=first_per_day(cool(-cross(isnr&(H>ph)&(C<ph)).astype(np.int64)+cross(isnr&(L<pl)&(C>pl)).astype(np.int64)),day)
    # 5 weekend/holiday gap at first bar after break >300min
    ts=(D.index.asi8//60_000_000_000) if D.index.asi8[1]-D.index.asi8[0]>1e9 else D.index.asi8//60_000_000; brk=np.r_[False,np.diff(ts)>300]; gw=(O-np.r_[C[0],C[:-1]])/atr
    for k in (0.5,1.0):
        s=np.where(brk&(gw>k),-1,np.where(brk&(gw<-k),1,0)); s=np.r_[np.zeros(3,np.int64),s[:-3]]; out[f'wkgap_fade_{k}']=s; out[f'wkgap_go_{k}']=-s
    # 6 fixed time-of-day anchors: direction of prior 60m at anchor -> mom/fade
    lon=D.index.tz_convert('Europe/London'); lt=lon.hour.values*60+lon.minute.values; nt=D.ny_t.values
    r60=C-pd.Series(C).shift(60).values; r60n=np.nan_to_num(r60/atr)
    anchors={'ldnfix':(lt==15*60),'ldnam':(lt==10*60+30),'nyclose':(nt==15*60),'nymid':(nt==12*60),'asia':(nt==20*60),'nyopen30':(nt==10*60)}
    for an,msk in anchors.items():
        s=np.where(msk&(r60n>0.5),1,np.where(msk&(r60n<-0.5),-1,0)); out[f'tod_{an}_mom']=s; out[f'tod_{an}_fade']=-s
    # 7 range-expansion bar with flow
    rng=H-L; ra=pd.Series(rng).rolling(60).mean().shift(1).values+1e-9
    for k in (3.0,5.0):
        up=(rng>k*ra)&(C>O); dn=(rng>k*ra)&(C<O); out[f'rexp_mom_{int(k)}']=mk(up&(d15>0),dn&(d15<0)); out[f'rexp_fade_{int(k)}']=-out[f'rexp_mom_{int(k)}']
    # 8 volume climax at 60-bar extreme
    hi60=D.hi60.values; lo60=D.lo60.values; vr=g('vr15')
    for k in (2.0,3.0):
        out[f'vclimax_fade_{int(k)}']=cool(-cross((vr>k)&(H>=hi60)).astype(np.int64)+cross((vr>k)&(L<=lo60)).astype(np.int64)); out[f'vclimax_mom_{int(k)}']=-out[f'vclimax_fade_{int(k)}']
    # 9 whale cluster at extremes
    w3=g('g3_30z')
    out['whale_ext_fade']=cool(-cross((w3>2)&(H>=hi60)).astype(np.int64)+cross((w3<-2)&(L<=lo60)).astype(np.int64))
    out['whale_ext_absorb']=cool(-cross((w3<-2)&(H>=hi60)).astype(np.int64)+cross((w3>2)&(L<=lo60)).astype(np.int64))
    # 10 longer/shorter window z extremes (extensions)
    for nm in ('g1_30z','g1_60z','g2_30z','g2_60z','g3_60z','imb30z','imb5z','ar5z','ar30z','fz5z','fz30z','ad5z','ad30z'):
        z=g(nm)
        for th in (2.0,3.0): out[f'{nm}_mom{th}']=mk(z>th,z<-th); out[f'{nm}_fade{th}']=mk(z<-th,z>th)
    # 11 trend-day VWAP pullback: price held one side of VWAP whole session so far, touches VWAP with flow resuming
    vc=D.vwap_cfd.values; side=np.sign(C-vc); fa=pd.Series((side>0).astype(float)).groupby(day).cumsum().values; fb=pd.Series((side<0).astype(float)).groupby(day).cumsum().values; nn=pd.Series(np.ones(len(C))).groupby(day).cumsum().values; ab=fa/nn>0.9; be=fb/nn>0.9
    elapsed=pd.Series(np.ones(len(C))).groupby(day).cumsum().values>120
    tch=np.abs(C-vc)<0.3*a5
    out['vwap_trend_pb']=first_per_day(np.where(np.r_[False,ab[:-1]]&elapsed&tch&(d15>0),1,np.where(np.r_[False,be[:-1]]&elapsed&tch&(d15<0),-1,0)),day)
    # 12 NY initial balance (XAU had none) break/fail
    ih=D.nyib_hi.values; il=D.nyib_lo.values
    out['nyib_break_flow']=first_per_day(mk((C>ih)&(d15>0.5),(C<il)&(d15<-0.5)),day); out['nyib_fail']=first_per_day(cool(-cross((H>ih)&(C<ih)&(d15<0)).astype(np.int64)+cross((L<il)&(C>il)&(d15>0)).astype(np.int64)),day)
    # 13 CVD trend vs price (60m): price flat but CVD trending -> follow CVD
    c60=pd.Series(g('cvd60')); cz=np.nan_to_num((c60/c60.rolling(1440,min_periods=300).std()).values); pr=np.nan_to_num((C-pd.Series(C).shift(60).values)/atr)
    out['cvd_lead']=mk((cz>2)&(np.abs(pr)<0.3),(cz<-2)&(np.abs(pr)<0.3)); out['cvd_lead_fade']=-out['cvd_lead']
    return {k:np.nan_to_num(v).astype(np.int64) for k,v in out.items()}
G={}
def job(a):
    nm,adx,se,mi=a; D=bt.table(ASSET)
    if 'sp' not in G: G['sp']=specs4(D)
    s=S.filters(D,G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    if (s!=0).sum()<30: return None
    m=N.MG[mi]; o=bt.run(ASSET,s,m,D=D); q=bt.quick(ASSET,o,D.index); ec,ew,nl,dep,st=o; P=bt.SPEC[ASSET]; ex=dep-P['EQ0']; en=ec-ex-P['EQ0']; ia=int(np.searchsorted(D.index,bt.A_END))
    mv=list(q['months'].values()); return dict(sig=nm,adx=adx,sess=se,mg=mi,net=q['net'],dd=q['dd_pct'],A=float(en[ia-1]),B=float(en[-1]-en[ia-1]),npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'],nsig=int((s!=0).sum()))
if __name__=='__main__':
    D=bt.table(ASSET); sp=specs4(D); names=list(sp.keys()); print(ASSET,'specs',len(names),{k:int((v!=0).sum()) for k,v in list(sp.items())[:12]},flush=True)
    jobs=list(itertools.product(names,('none','gt20'),('all','ldny','ny'),range(3)))
    t0=time.time()
    with mp.Pool(int(os.environ.get('NP','4'))) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for r in res if r]); R.to_parquet(f'/workspace/bt_3m/v3/results/newsig4_{ASSET}.parquet'); print('done',len(R),len(jobs),round(time.time()-t0),flush=True)
