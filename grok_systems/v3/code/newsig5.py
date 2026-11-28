# Round 6b: remaining coverage cells (inverse trend-pullback, IBS momentum) + confluence pairs of passed-system signals (A and B same direction within 30 bars).
import sys,os,itertools,time,numpy as np,pandas as pd,multiprocessing as mp
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import newsig as N, newsig2 as N2, newsig3 as N3, newsig4 as N4, bt, sig_v3 as S, combo as CB
ASSET=N.ASSET; cool=N.cool
POOL={'XAU':['v3:sw_fade_15_1.8','v3:dz_fade_15_2.0','n1:pd_break_flow','n1:lnor_break_trend','n2:pw_break_flow','n3:ad15z_fade2.0','n4:imb30z_fade2.0','n4:g1_30z_fade2.0','n3:imb15z_fade3.0','n2:basis_rev','n4:g3_60z_mom3.0','n2:day_ext_fail','v3:big3_mom_60_2.0','v3:emapull'],
      'US500':['v3:sw_fade_15_1.8','v3:absorb_fade_5_1.5_1.0','v3:dz_mom_5_1.5','v3:sw_fade_15_1.5','n1:orbd_mom','n1:asia_fail','n2:rnd_break_50','n3:imb15z_mom2.0','n4:fz5z_fade2.0','n4:vclimax_fade_3','n4:vclimax_mom_2','n4:fz30z_fade2.0','n4:g2_60z_mom2.0','v3:emapull']}[ASSET]
def specs5(D):
    v3=dict(S.specs(ASSET)); raw={}
    def get(k):
        if k in raw: return raw[k]
        p,n=k.split(':')
        if p=='v3': x=np.asarray(v3[n](D),dtype=np.int64)
        else:
            if p not in raw: raw[p]={'n1':N.specs,'n2':N2.specs2,'n3':N3.specs3,'n4':N4.specs4}[p](D)
            x=raw[p][n]
        raw[k]=np.sign(np.nan_to_num(x)).astype(np.int64); return raw[k]
    out={}
    out['emapull_fade']=-cool(np.asarray(v3['emapull'](D),dtype=np.int64)); out['pb_flow_fade']=-get('n2:pb_flow'); out['vwap_trend_pb_fade']=-get('n4:vwap_trend_pb')
    for k in (1,2,3): out[f'ibs_mom_{k}']=-np.asarray(S.fam_ibs(D,k),dtype=np.int64)
    for a,b in itertools.combinations(POOL,2):
        out[f'pair:{a}+{b}']=CB.combine(get(a).astype(np.int8),get(b).astype(np.int8),30).astype(np.int64)
    return {k:np.nan_to_num(v).astype(np.int64) for k,v in out.items()}
G={}
def job(a):
    nm,adx,se,mi=a; D=bt.table(ASSET)
    if 'sp' not in G: G['sp']=specs5(D)
    s=S.filters(D,G['sp'][nm],adx,se,ASSET); s=np.where(D.fut_ok.values,s,0).astype(np.int64)
    if (s!=0).sum()<30: return None
    m=N.MG[mi]; o=bt.run(ASSET,s,m,D=D); q=bt.quick(ASSET,o,D.index); ec,ew,nl,dep,st=o; P=bt.SPEC[ASSET]; ex=dep-P['EQ0']; en=ec-ex-P['EQ0']; ia=int(np.searchsorted(D.index,bt.A_END))
    mv=list(q['months'].values()); return dict(sig=nm,adx=adx,sess=se,mg=mi,net=q['net'],dd=q['dd_pct'],A=float(en[ia-1]),B=float(en[-1]-en[ia-1]),npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'],nsig=int((s!=0).sum()))
if __name__=='__main__':
    D=bt.table(ASSET); sp=specs5(D); names=list(sp.keys()); print(ASSET,'specs',len(names),flush=True)
    jobs=list(itertools.product(names,('none','gt20'),('all','ldny','ny'),range(3)))
    t0=time.time()
    with mp.Pool(int(os.environ.get('NP','3'))) as P: res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for r in res if r]); R.to_parquet(f'/workspace/bt_3m/v3/results/newsig5_{ASSET}.parquet'); print('done',len(R),len(jobs),round(time.time()-t0),flush=True)
