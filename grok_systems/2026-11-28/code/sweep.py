# Heavy parallel sweep (8 procs). ALL RESULTS ARE PYTHON-SIMULATED, not MT5.
import sys, os, json, itertools, time, numpy as np, pandas as pd, multiprocessing as mp
sys.path.insert(0,os.path.dirname(__file__)); import engine, signals
from scipy.stats import norm, skew, kurtosis
B='/workspace/bt_3m'; R=f'{B}/results'; os.makedirs(R,exist_ok=True)
ASSET=sys.argv[1]; STAGE=sys.argv[2]
SPEC={'US500':dict(file='US500_1m_features_utc.parquet',pv=1.0,lev=100.0,EQ0=10000.0,topup=0.0,ttrig=0.0,swl=-1.24,sws=0.17,tdow=4),
      'XAU':dict(file='XAU_1m_features_utc.parquet',pv=100.0,lev=500.0,EQ0=10000.0,topup=20000.0,ttrig=0.3,swl=-83.83,sws=20.64,tdow=2)}[ASSET]
CAP=SPEC['EQ0']+SPEC['topup']
D=None; A=None; FOLD=None; DAYIDX=None; SIGC={}
def init():
    global D,A,FOLD,DAYIDX
    D=pd.read_parquet(f'{B}/{SPEC["file"]}')
    A=dict(o=D.open.values,h=D.high.values,l=D.low.values,c=D.close.values,spr=D.spread_px.values,atr=D.atr5.fillna(0).values,
           roll=D.rollover.values,dow=D.dow.values.astype(np.int64))
    t=D.index; FOLD=np.searchsorted(t,[pd.Timestamp('2026-10-01',tz='UTC'),pd.Timestamp('2026-11-01',tz='UTC')])
    nyd=D.nyday.values; DAYIDX=np.r_[np.nonzero(nyd[1:]!=nyd[:-1])[0],len(D)-1]
def mgmt_vec(m,sprmul=1.0,slip=0.5):
    return np.array([m['L0'],m['mult'],m['gap'],m['gstep'],m['maxN'],m['btp'],m['trim'],m['prune'],m['hedge'],m['hgap'],m['hr'],m['htp'],m['cd'],m['comp'],
        SPEC['pv'],SPEC['lev'],SPEC['EQ0'],SPEC['topup'],SPEC['ttrig'],SPEC['swl'],SPEC['sws'],slip,sprmul,m['dsig'],m['maxlots'],m.get('gatr',0.0),SPEC['tdow']],float)
def metrics(out,sig_n):
    ec,ew,nl,dep,st=out; extra=dep-SPEC['EQ0']; en=ec-extra; ewn=ew-extra
    peak=np.maximum.accumulate(en); ddu=np.max(peak-ewn); ddp=float(st[6])
    f=[0,FOLD[0],FOLD[1],len(ec)-1]; fp=[float(en[f[j+1]]-en[f[j]]) for j in range(3)]
    fdd=[float(np.max(np.maximum.accumulate(en[f[j]:f[j+1]+1])-ewn[f[j]:f[j+1]+1])/CAP) for j in range(3)]
    de=en[DAYIDX]; r=np.diff(de)/np.maximum(de[:-1],1); sr=float(np.mean(r)/np.std(r)*np.sqrt(252)) if np.std(r)>0 else 0.0
    px=A['c']; g={}
    for X in (0.05,0.10,0.20):
        up=np.maximum(-nl,0)*SPEC['pv']*px*X; dn=np.maximum(nl,0)*SPEC['pv']*px*X
        g[f'gapup{int(X*100)}_dd']=float(np.max(peak-(en-up))/CAP); g[f'gapdn{int(X*100)}_dd']=float(np.max(peak-(en-dn))/CAP)
    return dict(net=float(en[-1]-SPEC['EQ0']),dd_pct_peak=ddp*100,dd_usd=float(ddu),dd_cap_pct=float(ddu/CAP*100),baskets=int(st[0]),basket_wins=int(st[1]),orders=int(st[2]),
                stopouts=int(st[3]),max_layers=int(st[4]),max_lots=float(st[5]),topup_used=float(st[8]-SPEC['EQ0']),f1=fp[0],f2=fp[1],f3=fp[2],
                f1_dd=fdd[0]*100,f2_dd=fdd[1]*100,f3_dd=fdd[2]*100,sharpe=sr,skew=float(skew(r)) if len(r)>3 else 0,kurt=float(kurtosis(r,fisher=False)) if len(r)>3 else 3,ndays=len(r),**g)
def getsig(spec):
    key=json.dumps(spec,sort_keys=True)
    if key not in SIGC:
        if len(SIGC)>400: SIGC.clear()
        SIGC[key]=signals.make(D,spec,ASSET)
    return SIGC[key]
def run1(job):
    spec,m,sprmul,slip,delay=job
    s=getsig(spec)
    if delay: s=np.r_[np.zeros(delay,np.int64),s[:-delay]]
    out=engine.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],mgmt_vec(m,sprmul,slip))
    return dict(spec=spec,m=m,sprmul=sprmul,slip=slip,delay=delay,**metrics(out,int((s!=0).sum())))
def MG_small():
    if ASSET=='US500':
        for g,mult,maxN,btp,hed in itertools.product([10,25],[1.0,1.5],[4,8],[2,6],[0,1]):
            yield dict(L0=0.3,mult=mult,gap=g,gstep=1.2,maxN=maxN,btp=btp,trim=0,prune=0,hedge=hed,hgap=g*2,hr=0.7,htp=5,cd=30,comp=0,dsig=0,maxlots=0)
    else:
        for g,mult,maxN,btp,hed in itertools.product([5,12],[1.0,1.5],[4,8],[1,3],[0,1]):
            yield dict(L0=0.02,mult=mult,gap=g,gstep=1.2,maxN=maxN,btp=btp,trim=0,prune=0,hedge=hed,hgap=g*2,hr=0.7,htp=2,cd=30,comp=0,dsig=0,maxlots=0)
def MG_full():
    if ASSET=='US500':
        G=dict(L0=[0.1,0.3,0.6,1.0],mult=[1.0,1.5,2.0],gap=[6,12,25,45],gstep=[1.0,1.4],maxN=[3,5,8],btp=[1,3,6],trim=[0,6],prune=[0,1.5],
               hedge=[0,1],hgap=[2.5],hr=[0.5,1.0],comp=[0,1],dsig=[0])
    else:
        G=dict(L0=[0.01,0.02,0.04,0.08],mult=[1.0,1.5,2.0],gap=[3,6,12,24],gstep=[1.0,1.4],maxN=[3,5,8],btp=[0.5,1.5,3],trim=[0,3],prune=[0,1.5],
               hedge=[0,1],hgap=[2.5],hr=[0.5,1.0],comp=[0,1],dsig=[0])
    for v in itertools.product(*G.values()):
        m=dict(zip(G.keys(),v))
        if m['hedge']==0 and m['hr']!=0.5: continue
        m['hgap']=m['hgap']*m['gap']*max(1,m['maxN']//2); m['htp']=5.0 if ASSET=='US500' else 2.0; m['cd']=30; m['maxlots']=0
        yield m
def pool_map(jobs,fn,tag):
    t=time.time(); res=[]
    with mp.Pool(8,initializer=init) as P:
        for i,r in enumerate(P.imap_unordered(fn,jobs,chunksize=64)):
            res.append(r)
            if i%20000==0: print(tag,i,round(time.time()-t),flush=True)
    print(tag,'done',len(res),round(time.time()-t),'s',flush=True); return res
def flat(rs):
    rows=[]
    for r in rs:
        d={**{'s_'+k:v for k,v in r['spec'].items()},**{'m_'+k:v for k,v in r['m'].items()},**{k:v for k,v in r.items() if k not in('spec','m')}}; rows.append(d)
    return pd.DataFrame(rows)
if __name__=='__main__':
    if STAGE=='A':
        jobs=[(s,m,1.0,0.5,0) for s in signals.all_specs() for m in MG_small()]
        print('jobs',len(jobs),flush=True)
        df=flat(pool_map(jobs,run1,'A')); df.to_parquet(f'{R}/{ASSET}_stageA.parquet')
    elif STAGE=='B':
        A_=pd.read_parquet(f'{R}/{ASSET}_stageA.parquet'); sc=[c for c in A_.columns if c.startswith('s_')]
        A_['ok']=(A_.net>0)&(A_.dd_cap_pct<80)&(A_.stopouts==0)&(A_.f1>0)&(A_.f2>0)&(A_.f3>0)
        agg=A_.groupby(sc).agg(ok_rate=('ok','mean'),med_net=('net','median'),best=('net','max'),med_dd=('dd_cap_pct','median')).reset_index()
        agg=agg[agg.s_fam!='placebo'].sort_values(['ok_rate','med_net'],ascending=False)
        top=agg.head(int(sys.argv[3]) if len(sys.argv)>3 else 40); top.to_csv(f'{R}/{ASSET}_stageA_top_signals.csv',index=False)
        specs=[{k[2:]:(v.item() if hasattr(v,'item') else v) for k,v in row.items() if k.startswith('s_')} for _,row in top.iterrows()]
        specs+= [dict(specs[0],fam='placebo',k=kk) for kk in (2,4)]
        MG=list(MG_full()); jobs=[(s,m,1.0,0.5,0) for s in specs for m in MG]
        print('jobs',len(jobs),flush=True)
        os.makedirs(f'{R}/{ASSET}_stageB_parts',exist_ok=True); buf=[]; part=0; t=time.time()
        with mp.Pool(8,initializer=init) as P:
            for i,r in enumerate(P.imap_unordered(run1,jobs,chunksize=256)):
                buf.append(r)
                if len(buf)>=100000:
                    flat(buf).to_parquet(f'{R}/{ASSET}_stageB_parts/p{part:03d}.parquet'); part+=1; buf=[]
                    print('B',i,round(time.time()-t),flush=True)
        if buf: flat(buf).to_parquet(f'{R}/{ASSET}_stageB_parts/p{part:03d}.parquet')
        print('B done',len(jobs),round(time.time()-t),flush=True)
