# Round 5: gap-aware lot optimisation under policy (weekend hedge-lock etc.), linear-scaled unit curves from engine2.
import sys,os,json,itertools,numpy as np,pandas as pd,p5,r5lib as R
PVS={'XAU':100.0,'US500':1.0}; CAPX=p5.CAP; STEP={'XAU':0.01,'US500':0.1}
LC={'x1':0.12,'x2':0.12,'x4':0.12,'g1':0.12,'g2':0.12,'xs1':1.0,'xs2':1.0,'u1':5.0,'u2':5.0,'u6':1.4,'u7':5.0,'u10':2.5,'u11':2.0}
UNIT={}
def unit(k,pol):
    key=(k,tuple(sorted(pol.items())))
    if key not in UNIT:
        lot=R.REF.get(k,1.0) if k not in p5.SCV else p5.SCV[k][0]['lot']
        c=p5.sysc(k,lot,pol); c['lot0']=lot; c['px']=p5.PX[c['a']]; c['e']=c['nl']*c['px']*PVS[c['a']]
        UNIT[key]=c
    return UNIT[key]
def ddf(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
class Port:
    def __init__(s,ks,pol,perpol=None):
        s.ks=ks; s.U=[unit(k,(perpol or {}).get(k,pol)) for k in ks]; s.assets=sorted({u['a'] for u in s.U}); s.cap=sum(CAPX[a] for a in s.assets)
        s.mx=np.array([LC[k]/u['lot0'] for k,u in zip(ks,s.U)])
    def agg(s,kv):
        ec=sum(f*u['ec'] for f,u in zip(kv,s.U)); ew=sum(f*u['ew'] for f,u in zip(kv,s.U)); sec=sum(f*u['sec'] for f,u in zip(kv,s.U)); sew=sum(f*u['sew'] for f,u in zip(kv,s.U))
        E={a:sum(f*u['e'] for f,u in zip(kv,s.U) if u['a']==a) for a in s.assets}
        return ec,ew,sec,sew,E
    def met(s,kv,full=False):
        ec,ew,sec,sew,E=s.agg(kv); pk=np.maximum.accumulate(ec); cap=s.cap; r=dict(net=float(ec[-1]),dd=ddf(ec,ew)/cap*100,sx_net=float(sec[-1]),sx_dd=ddf(sec,sew)/cap*100)
        for X in (0.05,0.10):
            b=0;bw=0;ba={a:0 for a in s.assets}
            for combo in itertools.product((0,1),repeat=len(s.assets)):
                loss=sum((np.maximum(-E[a],0) if c==0 else np.maximum(E[a],0)) for a,c in zip(s.assets,combo))*X
                b=max(b,float(np.max(pk-(ew-loss)))); bw=max(bw,float(np.max(pk[p5.BRK]-(ec[p5.BRK]-loss[p5.BRK]))))
            r[f'gap{int(X*100)}']=b/cap*100; r[f'wk{int(X*100)}']=max(r['dd'],bw/cap*100)
            for a in s.assets:   # single-asset shock only
                l1=np.maximum(np.abs(E[a]),0)*X; ba[a]=float(np.max(pk-(ew-l1)))/cap*100
            r[f'gap{int(X*100)}_asset']={a:round(v,1) for a,v in ba.items()}
        if full:
            m=ec[p5.mlast]; mn=np.diff(np.r_[0,m]); r['months']=[round(float(x)) for x in mn]; r['npos']=int((mn>0).sum()); r['A']=float(ec[p5.iA-1]); r['B']=float(ec[-1]-ec[p5.iA-1])
        return r
def optimise(P,DDT=0.17,SXT=0.25,GT=0.30,WT=0.25,use_gap=True,F=1,mn=None):
    mn=np.zeros(len(P.ks)) if mn is None else mn
    def ok(kv):
        ec,ew,sec,sew,E=P.agg(kv)
        if ddf(ec,ew)>DDT*P.cap or ddf(sec,sew)>SXT*P.cap: return False
        if not use_gap: return True
        pk=np.maximum.accumulate(ec)
        for combo in itertools.product((0,1),repeat=len(P.assets)):
            loss=sum((np.maximum(-E[a],0) if c==0 else np.maximum(E[a],0)) for a,c in zip(P.assets,combo))*0.05
            if np.max(pk-(ew-loss))>GT*P.cap: return False
            wl=loss*2
            if np.max(pk[p5.BRK]-(ec[p5.BRK]-wl[p5.BRK]))>WT*P.cap: return False
        return True
    net=lambda kv: float(P.agg(kv)[0][-1])
    d1=np.array([ddf(u['ec'],u['ew']) for u in P.U]); w=1.0/np.maximum(d1,1e-6); w=w/w.max()*P.mx.min()
    lo,hi=0.0,1e3
    for _ in range(30):
        m=(lo+hi)/2; kv=np.maximum(np.minimum(w*m,P.mx),mn)
        if ok(kv): lo=m
        else: hi=m
    kv=np.maximum(np.minimum(w*lo,P.mx),mn); inc=0.1
    for rnd in range(14):
        imp=False
        for i in range(len(kv)):
            for dl in (inc,-inc):
                t=kv.copy(); t[i]=min(P.mx[i],max(mn[i],t[i]+dl*P.mx[i]))
                if ok(t) and net(t)>net(kv)+1e-6: kv=t; imp=True
        for i in range(len(kv)):
            for j in range(len(kv)):
                if i==j: continue
                t=kv.copy(); t[i]=max(mn[i],t[i]-inc*P.mx[i]); t[j]=min(P.mx[j],t[j]+inc*P.mx[j])
                if ok(t) and net(t)>net(kv)+1e-6: kv=t; imp=True
        if not imp:
            if inc<0.01: break
            inc/=2
    # round to lot steps (floor to stay feasible)
    out=[]
    for k,f,u in zip(P.ks,kv,P.U):
        a=u['a']; lot=f*u['lot0']; lot=np.floor(lot/STEP[a]+1e-9)*STEP[a]; out.append(lot/u['lot0'])
    kv=np.array(out); g=0
    while not ok(kv) and g<200:
        g+=1; i=int(np.argmax([kv[j]*u['lot0']*(1 if u['a']=='XAU' else 0.1) for j,u in enumerate(P.U)])); kv[i]=max(mn[i]*0,kv[i]-STEP[P.U[i]['a']]/P.U[i]['lot0'])
    return kv
