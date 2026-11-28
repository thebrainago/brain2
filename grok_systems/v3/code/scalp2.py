# Round 6: SL/TP scalp pass over basket-only families (newsig1-4). PYTHON SIMULATION, results in ATR units.
import sys,os,itertools,time,numpy as np,pandas as pd,multiprocessing as mp
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import newsig as N, scalp as SC, sig_v3 as S, bt
ASSET=N.ASSET; G={}
def init():
    SC.init(ASSET); D=SC.G['D']
    import newsig2 as N2, newsig3 as N3, newsig4 as N4
    sp={}
    for pre,f in (('n1',N.specs),('n2',N2.specs2),('n3',N3.specs3),('n4',N4.specs4)):
        for k,v in f(D).items(): sp[f'{pre}:{k}']=v
    G['sp']=sp
def job(a):
    if 'sp' not in G: init()
    name,adx,sess=a; D=SC.G['D']; A=SC.G['A']
    s=S.filters(D,G['sp'][name],adx,sess,ASSET).astype(np.int64); ok=D.fut_ok.values
    if (s[ok]!=0).sum()<40: return []
    out=[]
    for sl,tp,hold in SC.GRID:
        idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5)
        if len(idx)<40: continue
        r=dict(sig=name,adx=adx,sess=sess,sl=sl,tp=tp,hold=hold); SC.metr(pn,'',r)
        pa=SC.G['isA'][idx]; SC.metr(pn[pa],'A_',r); SC.metr(pn[~pa],'B_',r)
        mon=SC.G['mon'][idx]; mm=[pn[mon==k].sum() for k in range(int(SC.G['mon'].max())+1)]; r['mpos']=int(sum(v>0 for v in mm))
        r['t']=float(pn.mean()/(pn.std(ddof=1)/np.sqrt(len(pn))+1e-12))
        if r['e']>0 and r['A_e']>0 and r['B_e']>0:
            fl=SC.run_flip(idx,s,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5); x=pn[np.isfinite(fl)]; y=fl[np.isfinite(fl)]
            dm=(x-y)/2; r['flip_z']=float(dm.mean()/(dm.std(ddof=1)/np.sqrt(len(dm))+1e-12))
            i2,p2,_=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr']*2,A['atr'],sl,tp,hold,0.5); r['sx2_e']=float(p2.mean()) if len(p2) else np.nan
            sd=np.r_[np.zeros(2,np.int64),s[:-2]]; i3,p3,_=SC.run_seq(sd,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],sl,tp,hold,0.5); r['d2_e']=float(p3.mean()) if len(p3) else np.nan
        out.append(r)
    return out
if __name__=='__main__':
    init(); jobs=list(itertools.product(G['sp'].keys(),('none','gt20'),('all','ldny','ny'))); t0=time.time(); print(ASSET,len(jobs),flush=True)
    with mp.Pool(int(os.environ.get('NP','2'))) as P: res=P.map(job,jobs,chunksize=2)
    R=pd.DataFrame([r for rr in res for r in rr]); R.to_parquet(f'/workspace/bt_3m/v3/results/r6/scalp2_{ASSET}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
