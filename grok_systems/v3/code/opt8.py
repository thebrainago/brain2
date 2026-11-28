# Round 7: recompute scenarios at joint 100k, plus Gold-only and US500-only at 100k and 50k.
# Reuses r6 unit curves (U6.pkl, policy W / weekend hedge-lock). Lot caps scale with capital so
# DD / spread×2 / gap-5% constraints bind first. Lot steps: XAU 0.01, US500 0.1.
import sys,os,json,pickle,itertools,copy,numpy as np,pandas as pd
sys.argv=[sys.argv[0],'XAU']
import r5lib as R,p5,opt5 as O
V=R.V; OUT=f'{V}/results/r6'
UNIV=['x1','x4','g1','g2','g3','g5','g7','xs1','xs2','xs3','xs4','xs5','xs6','xs7','u1','u2','u6','u7','u10','u11','u12','u13','u15','u16','u17','u18','u19','gp1','gp2','gp3','up1','up2','up3','xs8','xs9','xs10']
XAU_U=[k for k in UNIV if not k.startswith('u')]
US_U=[k for k in UNIV if k.startswith('u')]
MANUAL=['xs1','xs2','xs3','xs4','xs5','xs6','xs7','xs8','xs9','xs10']
BASE_LC=dict(O.LC)
BASE_LC.update({'gp1':.10,'gp2':.10,'gp3':.08,'up1':3.0,'up2':3.0,'up3':2.0,'xs8':1.0,'xs9':1.0,'xs10':1.0,'g3':.08,'g5':.06,'g7':.08,'xs3':1.0,'xs4':1.0,'xs5':1.0,'xs6':1.0,'xs7':1.0,'u12':4.0,'u13':4.0,'u15':3.0,'u16':3.0,'u17':3.0,'u18':3.0,'u19':3.0})
# fill any missing from conservative defaults
for k in UNIV:
    if k not in BASE_LC:
        BASE_LC[k]=0.12 if k[0] in 'xg' else 3.0
UF=f'{OUT}/U6.pkl'
U=pickle.load(open(UF,'rb'))
assert set(UNIV)<=set(U), set(UNIV)-set(U)
n=len(p5.idx); BS=5; nb=n//BS; cut=nb*BS
iA=p5.iA//BS
STEP={'XAU':0.01,'US500':0.1}
ORIG_CAP={'XAU':30000.,'US500':10000.}
day=pd.factorize(p5.idx[:cut:BS].strftime('%Y-%m-%d'))[0]
def daily(x): s=pd.Series(x).groupby(day).last().values; return np.diff(np.r_[0,s])
SCEN={'conservative':(10,15,30),'balanced':(15,22,50),'aggressive':(19,28,100)}
class P:
    def __init__(s,ks,cap,LC,sl=None):
        s.ks=ks; s.sl=sl or slice(0,nb); s.U=[U[k] for k in ks]; s.assets=sorted({u['a'] for u in s.U}); s.cap=float(cap)
        s.LC=LC; s.mx=np.array([LC[k]/u['lot0'] for k,u in zip(ks,s.U)])
    def agg(s,kv):
        sl=s.sl; f=lambda key: sum(w*u[key][sl] for w,u in zip(kv,s.U))
        ec=f('ec'); ew=f('ew'); sec=f('sec'); sew=f('sew'); b=ec[0]; ec=ec-b; ew=ew-b; b2=sec[0]; sec=sec-b2; sew=sew-b2
        E={a:(sum(w*u['emx'][sl] for w,u in zip(kv,s.U) if u['a']==a),sum(w*u['emn'][sl] for w,u in zip(kv,s.U) if u['a']==a)) for a in s.assets}
        return ec,ew,sec,sew,E
    def met(s,kv):
        ec,ew,sec,sew,E=s.agg(kv); pk=np.maximum.accumulate(ec)
        dd=lambda a,b: float(np.max(np.maximum.accumulate(a)-b))
        r=dict(net=float(ec[-1]),dd=dd(ec,ew)/s.cap*100,sx_net=float(sec[-1]),sx_dd=dd(sec,sew)/s.cap*100)
        g=0
        for combo in itertools.product((0,1),repeat=len(s.assets)):
            loss=sum((np.maximum(-E[a][1],0) if c==0 else np.maximum(E[a][0],0)) for a,c in zip(s.assets,combo))*0.05
            g=max(g,float(np.max(pk-(ew-loss))))
        r['gap5']=g/s.cap*100
        return r
def optimise(P,DDT,SXT,GT,mn=None,rounds=10):
    mn=np.zeros(len(P.ks)) if mn is None else mn
    def ok(kv):
        m=P.met(kv); return m['dd']<=DDT and m['sx_dd']<=SXT and m['gap5']<=GT
    net=lambda kv: float(P.agg(kv)[0][-1])
    d1=np.array([float(np.max(np.maximum.accumulate(u['ec'][P.sl])-u['ew'][P.sl]))+1 for u in P.U]); w=1.0/d1; w=w/w.max()*P.mx.min()
    lo,hi=0.0,1e3
    for _ in range(25):
        m=(lo+hi)/2; kv=np.maximum(np.minimum(w*m,P.mx),mn)
        if ok(kv): lo=m
        else: hi=m
    kv=np.maximum(np.minimum(w*lo,P.mx),mn); inc=0.2
    for rnd in range(rounds):
        imp=False
        for i in range(len(kv)):
            for dl in (inc,-inc):
                t=kv.copy(); t[i]=min(P.mx[i],max(mn[i],t[i]+dl*P.mx[i]))
                if ok(t) and net(t)>net(kv)+1e-6: kv=t; imp=True
        if not imp:
            if inc<0.02: break
            inc/=2
    return kv
def lots(P,kv):
    out={}
    for k,f,u in zip(P.ks,kv,P.U):
        lot=float(f*u['lot0'])
        if lot>1e-4: out[k]=round(lot,3)
    return out
def round_kv(P,kf):
    return np.array([np.floor(f*u['lot0']/STEP[u['a']]+1e-9)*STEP[u['a']]/u['lot0'] for f,u in zip(kf,P.U)])
def greedy(cands,maxk=20):
    D={k:daily(U[k]['ec'])/max(1,float(np.max(np.maximum.accumulate(U[k]['ec'])-U[k]['ew']))) for k in cands}
    sel=[]; best=-1; hist=[]
    while len(sel)<maxk:
        sc={}
        for k in cands:
            if k in sel: continue
            x=sum(D[j] for j in sel+[k]); sc[k]=x.mean()/(x.std()+1e-12)*np.sqrt(252)
        if not sc: break
        k=max(sc,key=sc.get)
        if sc[k]<best*1.005: break
        sel.append(k); best=sc[k]; hist.append((k,round(sc[k],2)))
    return sel,hist
def scale_lc(univ,cap):
    assets={U[k]['a'] for k in univ}
    orig=sum(ORIG_CAP[a] for a in assets)
    return {k:BASE_LC[k]*cap/orig for k in univ}
def run_mode(name,univ,cap,sel,include_manual=True):
    LC=scale_lc(univ,cap)
    out=dict(name=name,cap=cap,univ=univ,lc={k:round(v,4) for k,v in LC.items()},greedy=dict(sel=sel))
    sets={'GREEDY':sel,'ALL':univ}
    if include_manual and all(U[k]['a']=='XAU' for k in MANUAL if k in univ):
        man=[k for k in MANUAL if k in univ]
        if man: sets['MANUAL']=man
    for sn,ks in sets.items():
        for sc,(DDT,SXT,GT) in SCEN.items():
            if sn=='MANUAL' and sc!='conservative': continue
            Po=P(ks,cap,LC); kv=optimise(Po,DDT,SXT,GT); m=Po.met(kv)
            PA=P(ks,cap,LC,slice(0,iA)); PB=P(ks,cap,LC,slice(iA,nb))
            kA=optimise(PA,DDT,SXT,GT); kB=optimise(PB,DDT,SXT,GT)
            oosB=PB.met(kA); oosA=PA.met(kB)
            kf=(kA+kB)/2; lo,hi=0.0,1.5
            for _ in range(20):
                mm=(lo+hi)/2; t=Po.met(kf*mm)
                if t['dd']<=DDT and t['sx_dd']<=SXT and t['gap5']<=GT: lo=mm
                else: hi=mm
            kr=round_kv(Po,kf*lo)
            rob=dict(lots=lots(Po,kr),full=Po.met(kr),A=PA.met(kr),B=PB.met(kr),half=Po.met(kr*0.5))
            # flag systems sitting on the lot cap
            atcap=[k for k,f,u in zip(Po.ks,kr,Po.U) if f>=0.99*LC[k]/u['lot0'] and f*u['lot0']>1e-4]
            rob['at_lc']=atcap
            print(f'{name} {sn} {sc} ROBUST net {round(rob["full"]["net"])} dd {round(rob["full"]["dd"],1)} sx {round(rob["full"]["sx_dd"],1)} gap5 {round(rob["full"]["gap5"],1)} A {round(rob["A"]["net"])} B {round(rob["B"]["net"])} lots {rob["lots"]} at_lc={atcap}',flush=True)
            out[f'{sn}_{sc}']=dict(robust=rob,lots=lots(Po,kv),full=m,A_tuned_lots=lots(Po,kA),B_oos_of_A=oosB,B_tuned_lots=lots(Po,kB),A_oos_of_B=oosA,half=Po.met(kv*0.5))
    return out
if __name__=='__main__':
    res={}
    print('greedy joint…',flush=True)
    selJ,hJ=greedy(UNIV); print('JOINT greedy',hJ,flush=True)
    selX,hX=greedy(XAU_U); print('XAU greedy',hX,flush=True)
    selU,hU=greedy(US_U); print('US500 greedy',hU,flush=True)
    res['JOINT_100k']=run_mode('JOINT_100k',UNIV,100000,selJ,include_manual=True)
    res['JOINT_100k']['greedy']['hist']=hJ
    # MANUAL on joint 100k uses gold-only systems but the account is 100k (user request)
    res['XAU_100k']=run_mode('XAU_100k',XAU_U,100000,selX,include_manual=True)
    res['XAU_100k']['greedy']['hist']=hX
    res['XAU_50k']=run_mode('XAU_50k',XAU_U,50000,selX,include_manual=True)
    res['XAU_50k']['greedy']['hist']=hX
    res['US500_100k']=run_mode('US500_100k',US_U,100000,selU,include_manual=False)
    res['US500_100k']['greedy']['hist']=hU
    res['US500_50k']=run_mode('US500_50k',US_U,50000,selU,include_manual=False)
    res['US500_50k']['greedy']['hist']=hU
    json.dump(res,open(f'{OUT}/opt8.json','w'),indent=1,default=float)
    print('WROTE',f'{OUT}/opt8.json',flush=True)
