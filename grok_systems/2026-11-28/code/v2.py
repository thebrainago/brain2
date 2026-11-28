# Improvement pass v2 — SAME conservative engine (engine.py). ALL NUMBERS = PYTHON CONSERVATIVE SIMULATION, NOT MT5.
import sys, os, json, itertools, time, numpy as np, pandas as pd, multiprocessing as mp
ASSET=sys.argv[1]; MODE=sys.argv[2]
sys.argv=[sys.argv[0],ASSET,'V2']; sys.path.insert(0,os.path.dirname(__file__))
import sweep as S, engine, signals
NPROC=int(os.environ.get('NPROC','6'))
B=S.B; R=S.R; OUT=f'{R}/mt5_ready_v2'; os.makedirs(OUT,exist_ok=True)
M=None; MA=None; SC={}
def ld(f):
    D=pd.read_parquet(f'{B}/{f}'); A=dict(o=D.open.values,h=D.high.values,l=D.low.values,c=D.close.values,spr=D.spread_px.values,atr=D.atr5.fillna(0).values,roll=D.rollover.values,dow=D.dow.values.astype(np.int64)); return D,A
def init():
    global M,MA
    S.init(); M,MA=ld(S.SPEC['file'].replace('.parquet','_MIRROR.parquet'))
def mk(D,sp):
    s=signals.base(D,sp['fam'],sp['k'])
    a=np.nan_to_num(D.adx.values)
    if sp['adx']>0: s=np.where(a>sp['adx'],s,0)
    elif sp['adx']<0: s=np.where(a<-sp['adx'],s,0)
    s=signals.filt(D,s,sp.get('trend','none'),'none','none',sp.get('side','both'),sp['sess'],ASSET); return s
def sig(which,sp):
    k=(which,json.dumps(sp,sort_keys=True))
    if k not in SC:
        if len(SC)>40: SC.clear()
        SC[k]=mk(S.D if which=='o' else M,sp)
    return SC[k]
def spr_override(A,mode):
    # ESTIMATED broker costs (price units, commission folded into spread equivalent). XM = actual M1 spread column.
    if mode=='xm': return A['spr']
    est={'US500':{'exness_std':0.90,'exness_raw':0.50},'XAU':{'exness_std':0.30,'exness_raw':0.12}}[ASSET][mode]
    return np.full(len(A['spr']),est)
def ev(A,s,m,sprm=1.0,slip=0.5,cost='xm'):
    sp=spr_override(A,cost)
    return engine.run(A['o'],A['h'],A['l'],A['c'],sp,A['atr'],s,A['roll'],A['dow'],S.mgmt_vec(m,sprm,slip))
def q(out):
    ec,ew,nl,dep,st=out; ex=dep-S.SPEC['EQ0']; en=ec-ex; ewn=ew-ex; pk=np.maximum.accumulate(en)
    return dict(net=float(en[-1]-S.SPEC['EQ0']),dd=float(np.max(pk-ewn)/S.CAP*100),so=int(st[3]))
STRESS_SPR=3.0 if ASSET=='US500' else 2.0
def job(j):
    sp,m=j; s=sig('o',sp); base=S.metrics(ev(S.A,s,m),0)
    r=dict(sp=sp,m=m,**base)
    x=q(ev(S.A,s,m,STRESS_SPR,1.0)); r.update(sx_net=x['net'],sx_dd=x['dd'],sx_so=x['so'])
    sm=sig('m',sp); x=q(ev(MA,sm,m)); r.update(mir_net=x['net'],mir_dd=x['dd'],mir_so=x['so'])
    return r
def flat(rs):
    return pd.DataFrame([{**{'s_'+k:v for k,v in r['sp'].items()},**{'m_'+k:v for k,v in r['m'].items()},**{k:v for k,v in r.items() if k not in('sp','m')}} for r in rs])
def grid():
    if ASSET=='US500':
        for z,adx,ses in itertools.product([1.8,2.0,2.2,2.5],[15,20,25],['ldny']):
            sp=dict(fam='sw_fade',k=z,adx=adx,sess=ses,side='both',trend='none')
            for L0,gap,gs,mN,mult,btp,pr,hr,hgm,comp in itertools.product([1.0,1.5,2.0,2.5],[45,60],[1.4],[3],[1.0],[6,8,10,12,15],[0,1.2,1.5,2.0,2.5],[0,0.3,0.5,0.75,1.0],[1.5,2.5,4.0],[0,1]):
                if hr==0 and hgm!=2.5: continue
                yield sp,dict(L0=L0,mult=mult,gap=gap,gstep=gs,maxN=mN,btp=btp,trim=0,prune=pr,hedge=1 if hr>0 else 0,hgap=hgm*gap*max(1,mN//2),hr=max(hr,0.5),htp=5.0,cd=30,comp=comp,dsig=0,maxlots=0)
    else:
        fams=[('sw_fade',1.8),('sw_fade',2.0),('sw_fade',2.5),('vwap_rev',1),('vwap_rev',2),('d15_fade',2),('d15_fade',3),('ema_pull',1),('big30',1.5),('big30',2.5)]
        for (f,k),adx,tr,ses in itertools.product(fams,[0,20,-25],['none','slope'],['all','ldny']):
            sp=dict(fam=f,k=k,adx=adx,sess=ses,side='both',trend=tr)
            for L0,mult,gap,mN,btp,trim,pr,hed,cap in itertools.product([0.01,0.03],[1.0,1.3],[6,12,24,36],[2,3,4],[1,2,3],[0,3],[0,1.5],[(0,0.5),(1,0.5),(1,1.0)],[0,1]):
                lc=0.0
                if cap: lc=round(L0*(1+mult+mult**2)*1.0,2)  # net exposure cap ~ 3 base layers
                yield sp,dict(L0=L0,mult=mult,gap=gap,gstep=1.4,maxN=mN,btp=btp,trim=trim,prune=pr,hedge=hed[0],hgap=1.5*gap*max(1,mN//2),hr=hed[1],htp=2.0,cd=30,comp=0,dsig=0,maxlots=lc)
if __name__=='__main__' and MODE=='sweep':
    J=list(grid()); print('jobs',len(J),flush=True); t=time.time(); buf=[]; part=0
    os.makedirs(f'{R}/v2_{ASSET}_parts',exist_ok=True)
    with mp.Pool(NPROC,initializer=init) as P:
        for i,r in enumerate(P.imap(job,J,chunksize=128)):
            buf.append(r)
            if len(buf)>=50000:
                flat(buf).to_parquet(f'{R}/v2_{ASSET}_parts/p{part:03d}.parquet'); part+=1; buf=[]; print(i,round(time.time()-t),flush=True)
    if buf: flat(buf).to_parquet(f'{R}/v2_{ASSET}_parts/p{part:03d}.parquet')
    print('done',round(time.time()-t),flush=True)
