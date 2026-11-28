# Basket-style screen: every signal x filter x small mgmt grid on full Jun01-Nov26 window (XM spread, slip .5). PYTHON SIMULATION.
import sys, os, numpy as np, pandas as pd, multiprocessing as mp, time, itertools
sys.path.insert(0,os.path.dirname(__file__)); import bt, sig_v3 as S
ASSET=sys.argv[1]; V=bt.V
def mg():
    L=[]
    if ASSET=='US500':
        for gap,mN,btp in itertools.product([30,60],[3,5],[4,8]): L.append(dict(L0=1.0,mult=1.0,gap=gap,gstep=1.4,maxN=mN,btp=btp,trim=0,prune=0,hedge=0,cd=30))
    else:
        for gap,mN,btp in itertools.product([4,8],[3,5],[2,4]): L.append(dict(L0=0.03,mult=1.0,gap=gap,gstep=1.4,maxN=mN,btp=btp,trim=0,prune=0,hedge=0,cd=30))
    return L
G={}
def init():
    G['D']=bt.table(ASSET); G['specs']=dict(S.specs(ASSET)); G['mg']=mg()
def job(a):
    name,adx,sess=a; D=G['D']
    s=S.filters(D,G['specs'][name](D),adx,sess,ASSET); ok=D.fut_ok.values&(D.a_ok.values if name.startswith(('xlead','xdelta')) else True); s=np.where(ok,s,0).astype(np.int64)
    out=[]
    if (s!=0).sum()<30: return out
    for k,m in enumerate(G['mg']):
        o=bt.run(ASSET,s,m,D=D); q=bt.quick(asset=ASSET,out=o,idx=D.index) if False else bt.quick(ASSET,o,D.index)
        r=dict(sig=name,adx=adx,sess=sess,mg=k,nsig=int((s!=0).sum()),**{kk:vv for kk,vv in q.items() if kk!='months'})
        for mk,mv in q['months'].items(): r['m_'+mk]=mv
        out.append(r)
    return out
if __name__=='__main__':
    t0=time.time(); init()
    jobs=[(n,a,s) for n in G['specs'] for a in S.GRID_ADX for s in S.GRID_SESS]
    print(len(jobs),'sig jobs x',len(G['mg']),flush=True)
    with mp.Pool(int(os.environ.get('NP','8')),initializer=init) as P:
        res=P.map(job,jobs,chunksize=4)
    R=pd.DataFrame([r for rr in res for r in rr]); R.to_parquet(f'{V}/results/bsweep_{ASSET}.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
