# Confluence ('bo dong pha'): AND of 2 signals from different families within W bars, scalp SL/TP evaluation + uplift vs components.
import sys, os, numpy as np, pandas as pd, multiprocessing as mp, time, itertools
sys.path.insert(0,os.path.dirname(__file__)); import sig_v3 as S, scalp as SC
V=SC.V
POOL={'XAU':['big3_mom_60_2.0','big3_mom_30_2.0','imb_fade_15_1.5','dz_fade_15_2.0','xlead_fadeself_5_2.5','absorb_mom_30_2.0_0.5','sw_fade_15_1.8','sw_fade_15_2.2','vwapatr_3','sweep_pd_0','sweep_as_0','emapull','va_fail','orbbrk_cxor_0.0','orbbrk_nyor_0.0','cvddiv_15_2.0','stk_mom_15_5','dz_mom_30_2.0','absorb_fade_30_1.5_0.5','big1_fade_30_2.0','xlead_catchup_5_2.5','pdbrk_0.0','vwapz_2.5','opendrive_mom_500_530','big2_mom_30_2.5'],
      'US500':['sw_fade_15_1.8','big2_fade_30_1.5','big2_fade_60_2.0','cvddiv_30_1.0','big1_mom_30_2.0','absorb_fade_5_1.5_1.0','absorb_mom_5_1.5_0.5','vwapz_2.5','vwapatr_3','sweep_pd_0','sweep_day_0','orbfail_nyor','orbbrk_nyor_0.0','va_fail','dz_fade_15_2.0','dz_mom_15_1.5','imb_fade_15_1.5','xlead_catchup_5_2.5','xlead_fadeself_5_2.5','pocrev_2.5','emapull','opendrive_fade_570_600','ibs_2','big3_fade_60_2.0','stk_fade_15_5']}
FAM=lambda n:n.split('_')[0]
G={}
def init(asset):
    SC.init(asset); G['raw']={}
    for n in POOL[asset]:
        if n not in SC.G['specs']: print('missing',n); continue
        G['raw'][n]=np.asarray(SC.G['specs'][n](SC.G['D']),dtype=np.int8)
def rollany(x,W):
    return pd.Series(x).rolling(W,min_periods=1).max().values>0
def combine(sa,sb,W):
    pa=sa==1; na=sa==-1; pb=sb==1; nb=sb==-1
    rpb=rollany(pb,W); rnb=rollany(nb,W); rpa=rollany(pa,W); rna=rollany(na,W)
    long_=(pa&rpb&~rnb)|(pb&rpa&~rna); short_=(na&rnb&~rpb)|(nb&rna&~rpa)
    return np.where(long_&~short_,1,np.where(short_&~long_,-1,0)).astype(np.int8)
SG=[(1.0,1.0,30),(1.0,2.0,30),(2.0,2.0,30),(2.0,3.0,30),(1.5,1.5,90),(2.0,3.0,90),(1.0,1.0,90),(2.0,2.0,90)]
def stat(s,ok,sl,tp,hold):
    A=SC.G['A']; idx,pn,ex=SC.run_seq(s.astype(np.int64),ok,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5)
    return idx,pn
def job(a):
    na,nb,W=a; D=SC.G['D']; asset=SC.G['asset']; A=SC.G['A']; out=[]
    ok=D.fut_ok.values
    if (na.startswith('xlead') or nb.startswith('xlead')): ok=ok&D.a_ok.values
    sc=combine(G['raw'][na],G['raw'][nb],W)
    for adx in S.GRID_ADX:
        for sess in S.GRID_SESS:
            s=S.filters(D,sc,adx,sess,asset); 
            if (s[ok]!=0).sum()<25: continue
            sa=S.filters(D,G['raw'][na],adx,sess,asset); sb=S.filters(D,G['raw'][nb],adx,sess,asset)
            for sl,tp,hold in SG:
                idx,pn=stat(s,ok,sl,tp,hold)
                if len(idx)<50: continue
                r=dict(a=na,b=nb,W=W,adx=adx,sess=sess,sl=sl,tp=tp,hold=hold); SC.metr(pn,'',r)
                pa=SC.G['isA'][idx]; SC.metr(pn[pa],'A_',r); SC.metr(pn[~pa],'B_',r); dd=s[idx]; SC.metr(pn[dd>0],'L_',r); SC.metr(pn[dd<0],'S_',r)
                mon=SC.G['mon'][idx]; mm=[pn[mon==k].sum() for k in range(int(SC.G['mon'].max())+1)]; r['mpos']=int(sum(1 for v in mm if v>0))
                fl=SC.run_flip(idx,s.astype(np.int64),A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5); x=pn[np.isfinite(fl)]; y=fl[np.isfinite(fl)]
                dm=(x-y)/2; r['flip_z']=float(dm.mean()/(dm.std(ddof=1)/np.sqrt(len(x))+1e-12)); r['t']=float(x.mean()/(x.std(ddof=1)/np.sqrt(len(x))+1e-12))
                # components alone, same filter/sltp
                for nm,sx in (('ea',sa),('eb',sb)):
                    okx=ok; i2,p2=stat(sx,okx,sl,tp,hold); r[nm]=float(p2.mean()) if len(p2) else np.nan; r[nm+'_n']=len(p2)
                out.append(r)
    return out
if __name__=='__main__':
    asset=sys.argv[1]; init(asset); t0=time.time()
    names=[n for n in POOL[asset] if n in G['raw']]
    jobs=[(a,b,W) for a,b in itertools.combinations(names,2) if FAM(a)!=FAM(b) for W in (10,30)]
    print(asset,len(jobs),'combo jobs',flush=True)
    with mp.Pool(int(os.environ.get('NP','8')),initializer=init,initargs=(asset,)) as P: res=P.map(job,jobs,chunksize=2)
    R=pd.DataFrame([r for rr in res for r in rr]); R.to_parquet(f'{V}/results/combo_{asset}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
