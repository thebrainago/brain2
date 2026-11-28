import sys,os,json,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,lotscale as LS
V=LS.V; DDT=0.17; SXT=0.25
CAP={'XAU':30000.,'US500':10000.}; STEP={'XAU':0.01,'US500':0.1}
S={n:(a,k,p,m) for n,a,k,p,m in LS.SYS}
cv={n:pickle.load(open(f'{LS.CD_}/{n}.pkl','rb')) for n in S}
idx=cv['x1']['index'].union(cv['u1']['index']); n=len(idx)
A_END=pd.Timestamp('2026-08-20',tz='UTC'); iA=int(idx.searchsorted(A_END))
mon=idx.strftime('%Y-%m'); mcodes=pd.factorize(mon)[0]; mlast=np.r_[np.nonzero(np.diff(mcodes))[0],n-1]
def al(s,ix): return pd.Series(s,index=ix).reindex(idx).ffill().fillna(0).values
C={}
for k,o in cv.items():
    ix=o['index']; C[k]=dict(ec=al(o['base'][0],ix),ew=al(o['base'][1],ix),sec=al(o['sx2'][0],ix),sew=al(o['sx2'][1],ix),lot0=o['lot'],pf=o.get('pf'))
F=10
def red(a,fn):
    m=(len(a)//F)*F; return fn(a[:m].reshape(-1,F),axis=1)
CR={k:dict(ec=red(c['ec'],np.max),ew=red(c['ew'],np.min),sec=red(c['sec'],np.max),sew=red(c['sew'],np.min)) for k,c in C.items()}
def aggr(ks,kv,sl=slice(None)):
    return [sum(kv[i]*CR[k][f][sl] for i,k in enumerate(ks)) for f in ('ec','ew','sec','sew')]
def agg(ks,kv,sl=slice(None)):
    ec=sum(kv[i]*C[k]['ec'][sl] for i,k in enumerate(ks)); ew=sum(kv[i]*C[k]['ew'][sl] for i,k in enumerate(ks))
    sec=sum(kv[i]*C[k]['sec'][sl] for i,k in enumerate(ks)); sew=sum(kv[i]*C[k]['sew'][sl] for i,k in enumerate(ks))
    return ec,ew,sec,sew
def dd(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
def evalp(ks,kv,cap):
    ec,ew,sec,sew=agg(ks,kv); d=dd(ec,ew); sd=dd(sec,sew)
    m=ec[mlast]; mn=np.diff(np.r_[0,m]); dly=pd.Series(ec,index=idx).resample('1D').last().diff().dropna()
    pfd=float(dly[dly>0].sum()/-dly[dly<0].sum()) if (dly<0).any() else 99
    return dict(net=float(ec[-1]),dd=d,dd_pct=d/cap*100,sx_net=float(sec[-1]),sx_dd_pct=sd/cap*100,A=float(ec[iA-1]),B=float(ec[-1]-ec[iA-1]),months=[round(float(x)) for x in mn],npos=int((mn>0).sum()),pf_daily=round(pfd,2),sharpe=round(float(dly.mean()/dly.std()*np.sqrt(252)),2))
def capof(ks): return sum(CAP[a] for a in {S[k][0] for k in ks})
def feasible(ks,kv,cap):
    ec,ew,sec,sew=agg(ks,kv); return dd(ec,ew)<=DDT*cap and dd(sec,sew)<=SXT*cap
LCAP={'x1':0.12,'x2':0.12,'x4':0.12,'x5':0.12,'xs1':1.0,'xs2':1.0,'u1':5.0,'u2':5.0,'u3':8.0,'u5':5.0,'u6':5.0,'u7':5.0,'u8':5.0,'u9':5.0}
def optimise(ks,sl=None,cap=None):
    cap=cap or capof(ks); sl_=slice(None) if sl is None else (sl if isinstance(sl,slice) else slice(0,sl))
    mx=np.array([LCAP[k]/C[k]['lot0'] for k in ks])
    def ok(kv):
        ec,ew,sec,sew=aggr(ks,kv,sl_); return dd(ec,ew)<=DDT*cap and dd(sec,sew)<=SXT*cap
    def net(kv): return aggr(ks,kv,sl_)[0][-1]
    # risk-parity start: weight_i ~ 1/dd_i
    d1=np.array([dd(*[CR[k][f][sl_] for f in ('ec','ew')]) for k in ks]); w=1.0/np.maximum(d1,1e-6); w=w/w.max()*mx.min()
    lo,hi=0.0,1e4
    for _ in range(40):
        m=(lo+hi)/2; kv=np.minimum(w*m,mx)
        if ok(kv): lo=m
        else: hi=m
    kv=np.minimum(w*lo,mx)
    inc=0.05
    for rnd in range(30):
        imp=False
        for i in range(len(ks)):
            for dlt in (inc,-inc):
                t=kv.copy(); t[i]=min(mx[i],max(0,t[i]+dlt*mx[i]))
                if ok(t) and net(t)>net(kv)+1e-6: kv=t; imp=True
        # trade-off move: shrink i, grow j
        for i in range(len(ks)):
            for j in range(len(ks)):
                if i==j: continue
                t=kv.copy(); t[i]=max(0,t[i]-inc*mx[i]); t[j]=min(mx[j],t[j]+inc*mx[j])
                if ok(t) and net(t)>net(kv)+1e-6: kv=t; imp=True
        if not imp:
            if inc<0.01: break
            inc/=2
    return kv,cap
def roundk(ks,kv):
    out=[]
    for k,x in zip(ks,kv):
        a=S[k][0]; lot=x*C[k]['lot0']; lot=round(lot/STEP[a])*STEP[a]; out.append(lot/C[k]['lot0'])
    return np.array(out)
def single(k):
    a=S[k][0]; cap=CAP[a]; ec,ew,sec,sew=agg([k],[1.0]); d1=dd(ec,ew); s1=dd(sec,sew)
    km=min(DDT*cap/d1,SXT*cap/s1,LCAP[k]/C[k]['lot0']); km=roundk([k],[km])[0]
    if km*d1>DDT*cap*1.0001 or km*s1>SXT*cap*1.0001: km=roundk([k],[km-STEP[a]/C[k]['lot0']])[0]
    r=evalp([k],[km],cap); r.update(sys=k,asset=a,lot=round(km*C[k]['lot0'],3),mult=round(km,2),cap=cap,pf=C[k]['pf']); return r
if __name__=='__main__':
    res=dict(single=[],port=[])
    for k in S: res['single'].append(single(k)); r=res['single'][-1]; print(k,r['lot'],round(r['net']),round(r['dd_pct'],1),round(r['sx_dd_pct'],1),r['A'].__round__(),round(r['B']),r['npos'],flush=True)
    sets={'GOLD_all':['x1','x2','x4','x5','xs1','xs2'],'GOLD_core':['x1','x4','xs1','xs2'],'US_all':['u1','u2','u3','u6','u7','u8','u9'],'US_core':['u1','u2','u6','u7'],
          'CROSS_all':['x1','x2','x4','x5','xs1','xs2','u1','u2','u3','u6','u7','u8','u9'],'CROSS_core':['x1','x4','xs1','xs2','u1','u2','u6','u7'],'CROSS_x1_u1':['x1','u1'],'CROSS_sw_only':['x1','x2','u1','u7']}
    for name,ks in sets.items():
        kv,cap=optimise(ks); kv=roundk(ks,kv)
        g=0
        while not feasible(ks,kv,cap) and g<500:
            g+=1; i=int(np.argmax([kv[j]*C[ks[j]]['lot0']*(1 if S[ks[j]][0]=='XAU' else 0.1) for j in range(len(ks))])); kv[i]=max(0,kv[i]-STEP[S[ks[i]][0]]/C[ks[i]]['lot0'])
        r=evalp(ks,kv,cap); r.update(name=name,cap=cap,lots={k:round(float(x*C[k]['lot0']),3) for k,x in zip(ks,kv)})
        # OOS: optimise on A only, test on B
        iAs=slice(0,iA); 
        kvA,_=optimise(ks,sl=iA//F,cap=cap); kvA=roundk(ks,kvA)
        ecB,ewB,secB,sewB=agg(ks,kvA,slice(iA,n)); 
        r['oos']=dict(lotsA={k:round(float(x*C[k]['lot0']),3) for k,x in zip(ks,kvA)},B_net=float(ecB[-1]-ecB[0]),B_dd_pct=dd(ecB,ewB)/cap*100,B_sx_dd_pct=dd(secB,sewB)/cap*100)
        kvB,_=optimise(ks,sl=slice(iA//F,None),cap=cap); kvB=roundk(ks,kvB)
        ecA,ewA,secA,sewA=agg(ks,kvB,slice(0,iA))
        r['oos2']=dict(lotsB={k:round(float(x*C[k]['lot0']),3) for k,x in zip(ks,kvB)},A_net=float(ecA[-1]),A_dd_pct=dd(ecA,ewA)/cap*100)
        # safe tier: half lots
        r['safe']=evalp(ks,kv*0.5,cap)
        res['port'].append(r); print(name,r['lots'],round(r['net']),round(r['dd_pct'],1),round(r['sx_dd_pct'],1),'A',round(r['A']),'B',round(r['B']),r['npos'],'| OOS A->B',round(r['oos']['B_net']),round(r['oos']['B_dd_pct'],1),'B->A',round(r['oos2']['A_net']),round(r['oos2']['A_dd_pct'],1),flush=True)
        json.dump(res,open(f'{V}/results/opt_results.json','w'),indent=1,default=float)
    print('OPT DONE')
