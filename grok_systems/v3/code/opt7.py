# Round 6 combination search: universe of passed systems (policy W), 5-min downsampled unit curves,
# greedy correlation-aware selection + constrained lot optimisation, A->B and B->A OOS lot tuning, 3 scenarios + manual.
import sys,os,json,pickle,itertools,numpy as np,pandas as pd
sys.argv=[sys.argv[0],'XAU']
import r5lib as R,p5,opt5 as O
V=R.V; OUT=f'{V}/results/r6'
for k,key in (('xs8','pair_n1_pd_break_flow__n2_pw_break_flow'),('xs9','pair_n4_g3_60z_mom3.0__v3_big3_mom_60_2.0'),('xs10','pair_v3_sw_fade_15_1.8__v3_big3_mom_60_2.0'),('xs3','g1_30z_fade2.0'),('xs4','imb15z_fade3.0'),('xs5','basis_rev'),('xs6','g3_60z_mom3.0'),('xs7','day_ext_fail')):
    o=pickle.load(open(f'{OUT}/curves/sc_XAU_{key}.pkl','rb')); p5.SCV[k]=(o,o); R.S[k]=('XAU','s',None,None)
O.LC.update({'gp1':.10,'gp2':.10,'gp3':.08,'up1':3.0,'up2':3.0,'up3':2.0,'xs8':1.0,'xs9':1.0,'xs10':1.0,'g3':.08,'g5':.06,'g7':.08,'xs3':1.0,'xs4':1.0,'xs5':1.0,'xs6':1.0,'xs7':1.0,'u12':4.0,'u13':4.0,'u15':3.0,'u16':3.0,'u17':3.0,'u18':3.0,'u19':3.0})
UNIV=['x1','x4','g1','g2','g3','g5','g7','xs1','xs2','xs3','xs4','xs5','xs6','xs7','u1','u2','u6','u7','u10','u11','u12','u13','u15','u16','u17','u18','u19','gp1','gp2','gp3','up1','up2','up3','xs8','xs9','xs10']
W=dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
n=len(p5.idx); BS=5; nb=n//BS; cut=nb*BS
def ds_last(x): return x[:cut].reshape(nb,BS)[:,-1]
def ds_min(x): return x[:cut].reshape(nb,BS).min(1)
def ds_max(x): return x[:cut].reshape(nb,BS).max(1)
iA=p5.iA//BS; brk=np.unique(np.minimum(p5.BRK//BS,nb-1))
import bt,scalp as SC,cands as CD,lotscale as LS
def scalp_expo(k):
    """USD exposure per unit lot path (dir*lot0*pv*px) while a scalp is open; scalps are NOT gap-immune (gap jumps SL)."""
    D=bt.table('XAU'); SC.init('XAU'); A=SC.G['A']; one=np.ones(len(D)); ok=D.fut_ok.values
    if k in ('xs1','xs2'):
        sy=[x for x in LS.SYS if x[0]==k][0]; s=CD.build_sig(D,'XAU',sy[3],{}); sl,tp,h,lot=sy[4]; ok=np.ones(len(D),bool)
    else:
        o=p5.SCV[k][0]; s=o['sig']; c=o['cfg']; sl,tp,h,lot=c['sl'],c['tp'],c['hold'],o['lot']
    idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],one,sl,tp,h,0.5)
    pos=np.zeros(len(D)+1)
    np.add.at(pos,idx+1,s[idx]*lot); np.add.at(pos,ex+1,-s[idx]*lot); pos=np.cumsum(pos)[:-1]
    return p5.al(pos*100.0*D.close.values,D.index)
UF=f'{OUT}/U6.pkl'
U=pickle.load(open(UF,'rb')) if os.path.exists(UF) else {}
for k in [k for k in UNIV if k not in U]:
    u=O.unit(k,W)
    if k.startswith('xs'): u['e']=scalp_expo(k)
    U[k]=dict(a=u['a'],lot0=u['lot0'],ec=ds_last(u['ec']),ew=ds_min(u['ew']),sec=ds_last(u['sec']),sew=ds_min(u['sew']),emx=ds_max(u['e']),emn=ds_min(u['e']))
pickle.dump(U,open(UF,'wb'))
CAP={'XAU':30000.,'US500':10000.}; STEP={'XAU':0.01,'US500':0.1}
day=pd.factorize(p5.idx[:cut:BS].strftime('%Y-%m-%d'))[0]
def daily(x): s=pd.Series(x).groupby(day).last().values; return np.diff(np.r_[0,s])
class P6:
    def __init__(s,ks,sl=None):
        s.ks=ks; s.sl=sl or slice(0,nb); s.U=[U[k] for k in ks]; s.assets=sorted({u['a'] for u in s.U}); s.cap=sum(CAP[a] for a in s.assets)
        s.mx=np.array([O.LC[k]/u['lot0'] for k,u in zip(ks,s.U)])
    def agg(s,kv):
        sl=s.sl; f=lambda key: sum(w*u[key][sl] for w,u in zip(kv,s.U))
        ec=f('ec'); ew=f('ew'); sec=f('sec'); sew=f('sew'); b=ec[0]; ec=ec-b; ew=ew-b; b2=sec[0]; sec=sec-b2; sew=sew-b2
        E={a:(sum(w*u['emx'][sl] for w,u in zip(kv,s.U) if u['a']==a),sum(w*u['emn'][sl] for w,u in zip(kv,s.U) if u['a']==a)) for a in s.assets}
        return ec,ew,sec,sew,E
    def met(s,kv):
        ec,ew,sec,sew,E=s.agg(kv); pk=np.maximum.accumulate(ec); dd=lambda a,b: float(np.max(np.maximum.accumulate(a)-b))
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
def lots(P,kv): return {k:round(float(f*u['lot0']),3) for k,f,u in zip(P.ks,kv,P.U) if f*u['lot0']>1e-4}
def greedy(cands,maxk=20):
    """correlation-aware forward selection on daily PnL Sharpe with inverse-DD weights."""
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
SCEN={'conservative':(10,15,30),'balanced':(15,22,50),'aggressive':(19,28,100)}
if __name__=='__main__':
    res={}
    C=pd.DataFrame({k:daily(U[k]['ec']) for k in UNIV}).corr().round(2); C.to_csv(f'{OUT}/corr_daily.csv')
    sel,hist=greedy(UNIV); res['greedy']=dict(sel=sel,hist=hist); print('greedy',hist,flush=True)
    sets={'GREEDY':sel,'ALL':UNIV,'MANUAL':['xs1','xs2','xs3','xs4','xs5','xs6','xs7','xs8','xs9','xs10']}
    for sn,ks in sets.items():
        for sc,(DDT,SXT,GT) in SCEN.items():
            if sn=='MANUAL' and sc!='conservative': continue
            P=P6(ks); kv=optimise(P,DDT,SXT,GT); m=P.met(kv)
            PA=P6(ks,slice(0,iA)); PB=P6(ks,slice(iA,nb))
            kA=optimise(PA,DDT,SXT,GT); kB=optimise(PB,DDT,SXT,GT)
            oosB=PB.met(kA); oosA=PA.met(kB)
            kf=(kA+kB)/2; lo,hi=0.0,1.5
            for _ in range(20):
                mm=(lo+hi)/2; t=P.met(kf*mm)
                if t['dd']<=DDT and t['sx_dd']<=SXT and t['gap5']<=GT: lo=mm
                else: hi=mm
            kf=kf*lo; kr=np.array([np.floor(f*u['lot0']/STEP[u['a']]+1e-9)*STEP[u['a']]/u['lot0'] for f,u in zip(kf,P.U)])
            rob=dict(lots=lots(P,kr),full=P.met(kr),A=PA.met(kr),B=PB.met(kr),half=P.met(kr*0.5))
            print('   ROBUST(mean A/B-tuned, rounded) net',round(rob['full']['net']),'dd',round(rob['full']['dd'],1),'sx',round(rob['full']['sx_dd'],1),'gap5',round(rob['full']['gap5'],1),'A',round(rob['A']['net']),'B',round(rob['B']['net']),rob['lots'],flush=True)
            r=dict(robust=rob,lots=lots(P,kv),full=m,A_tuned_lots=lots(P,kA),B_oos_of_A=oosB,B_tuned_lots=lots(P,kB),A_oos_of_B=oosA,half=P.met(kv*0.5))
            res[f'{sn}_{sc}']=r
            print(sn,sc,'net',round(m['net']),'dd',round(m['dd'],1),'sx',round(m['sx_dd'],1),'gap5',round(m['gap5'],1),'| OOS B(A-lots) net',round(oosB['net']),'dd',round(oosB['dd'],1),'| OOS A(B-lots) net',round(oosA['net']),'dd',round(oosA['dd'],1),'| lots',r['lots'],flush=True)
            json.dump(res,open(f'{OUT}/opt7.json','w'),indent=1,default=float)
