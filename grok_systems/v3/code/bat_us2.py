import sys, os, numpy as np, pandas as pd, multiprocessing as mp, itertools, time, json
sys.path.insert(0,os.path.dirname(__file__)); import bt, sig_v3 as S, battery as B, scalp as SC, cands as CD
ASSET=sys.argv[1]; V=bt.V
def progs():
    L=[]
    if ASSET=='XAU':
        singles=[('sw_fade_15_1.8','gt20','ldny'),('vwapatr_3','gt20','all'),('big3_mom_60_2.0','none','ny'),('big3_mom_30_2.0','none','ny'),('imb_fade_15_1.5','gt20','ldn'),('dz_fade_15_2.0','none','ldn'),
                 ('xlead_fadeself_5_2.5','gt20','ldn'),('absorb_mom_30_2.0_0.5','none','ny'),('sw_fade_15_2.2','gt20','ldn'),('sweep_pd_0','none','ldny'),('sweep_as_0','none','ldn'),('emapull','none','ny'),('cvddiv_15_2.0','gt20','all')]
        pairs=[('xlead_fadeself_5_2.5','big2_mom_30_2.5','gt20','all'),('xlead_fadeself_5_2.5','big2_mom_30_2.5','none','all'),('absorb_mom_30_2.0_0.5','emapull','none','ny'),('big3_mom_60_2.0','xlead_fadeself_5_2.5','gt20','ny'),
               ('big3_mom_60_2.0','emapull','none','ny'),('big3_mom_60_2.0','absorb_mom_30_2.0_0.5','none','ny'),('big3_mom_30_2.0','emapull','none','ny'),('sw_fade_15_1.8','vwapatr_3','gt20','all'),('sw_fade_15_1.8','big3_mom_60_2.0','none','all'),('sw_fade_15_1.8','imb_fade_15_1.5','gt20','ldn')]
    else:
        singles=[('stk_fade_15_2','none','ldny'),('stk_fade_30_2','none','ldny'),('stk_fade_15_3','gt20','ldny'),('imb_mom_15_1.5','none','ldny'),('imb_mom_30_1.5','none','all'),('stk_mom_30_3','gt20','all'),('sw_fade_15_1.5','none','all'),('dz_mom_5_1.5','none','all'),('dz_mom_5_2.0','none','all'),('stk_fade_5_2','gt20','ldny'),('big1_mom_30_1.5','none','ldny')]
        pairs=[('sw_fade_15_1.8','stk_fade_15_2','none','ldny'),('stk_fade_15_2','absorb_fade_5_1.5_1.0','none','ldny'),('stk_fade_15_2','dz_mom_5_1.5','none','all'),('imb_mom_15_1.5','stk_fade_15_2','none','ldny'),('sw_fade_15_1.8','dz_mom_5_1.5','none','all')]
    for a,adx,se in singles: L.append(dict(kind='single',a=a,adx=adx,sess=se))
    for a,b,adx,se in pairs:
        for W in (10,30): L.append(dict(kind='pair',a=a,b=b,W=W,adx=adx,sess=se))
    return L
def mgs():
    if ASSET=='XAU':
        return [dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30),
                dict(L0=0.03,mult=1.0,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=0,hedge=0,cd=30),
                dict(L0=0.03,mult=1.0,gap=4,gstep=1.4,maxN=3,btp=2,trim=0,prune=0,hedge=0,cd=30),
                dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30)]
    return [dict(L0=1.0,mult=1.0,gap=45,gstep=1.4,maxN=3,btp=6,trim=0,prune=1.2,hedge=1,hgap=180,hr=0.5,htp=5.0,cd=30),
            dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30),
            dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30),
            dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30)]
G={}
def init():
    SC.init(ASSET); G['raw']={}
def job(a):
    pi,mi=a; p=PROGS[pi]; D=bt.table(ASSET); s=CD.build_sig(D,ASSET,p,G['raw'])
    if (s!=0).sum()<30: return None
    r=B.battery(ASSET,s,MG[mi]); r.update(prog=json.dumps(p),mg=mi); return r
PROGS=progs(); MG=mgs()
if __name__=='__main__':
    t0=time.time(); jobs=[(i,j) for i in range(len(PROGS)) for j in range(len(MG))]; print(len(jobs),flush=True)
    with mp.Pool(int(os.environ.get('NP','8')),initializer=init) as P: res=P.map(job,jobs,chunksize=1)
    R=pd.DataFrame([r for r in res if r]); R['months']=R.months.apply(json.dumps); R.to_parquet(f'{V}/results/battery_{ASSET}b.parquet'); print('done',len(R),round(time.time()-t0))
