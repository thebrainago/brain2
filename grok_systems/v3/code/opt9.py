# Round 8 (t157u): re-tune scenarios directly on the 100 USD cent-lot grid (step 0.01 cent lot = 0.0001 std lot),
# then verify on MT5 deals (scaled). Systems whose optimal lot < 0.01 cent lot are dropped automatically.
import sys,os,json,numpy as np
sys.path.insert(0,'/workspace/bt_3m/v3/code'); sys.path.insert(0,'/workspace/bt_3m/v3/r4')
os.chdir('/workspace/bt_3m/v3/code')
import opt8 as O8
from opt8 import *
os.chdir('/workspace/bt_3m/v3/r4')
import joint5 as J
from joint7 import RUN
V='/workspace/bt_3m/v3'; CAP=100.0; GS=1e-4   # std-lot grid = 0.01 cent lot
Oj=json.load(open(f'{V}/results/r6/opt8.json'))
def cl(k,f,u): return round(f*u['lot0']/GS*0.01,2)   # cent lots
def kv_from_cent(P,cent):  # cent-lot dict -> kv
    return np.array([cent.get(k,0.0)*0.01/u['lot0'] for k,u in zip(P.ks,P.U)])
def floor_grid(P,kv): return np.array([np.floor(f*u['lot0']/GS+1e-9)*GS/u['lot0'] for f,u in zip(kv,P.U)])
def climb(P,kv,ok):
    net=lambda x: float(P.agg(x)[0][-1]); kv=kv.copy(); imp=True
    while imp:
        imp=False
        for i,u in enumerate(P.U):
            t=kv.copy(); t[i]+=GS/u['lot0']
            if t[i]<=P.mx[i]+1e-12 and ok(t) and net(t)>net(kv)+1e-9: kv=t; imp=True
    return kv
def mt5(cent,lab):
    std={k:v*0.01 for k,v in cent.items() if v>0}
    names=[RUN[k][0] for k in std]; sc={RUN[k][0]:std[k]/RUN[k][1] for k in std}
    r=J.joint(names,sc,lab,cap=CAP); h=J.joint(names,{n:v*0.5 for n,v in sc.items()},lab,cap=CAP)
    r['half']=dict(net=h['net'],dd_pct=h['dd_pct']); return r
def tune(mode,univ,sel,scen):
    LC=scale_lc(univ,CAP); DDT,SXT,GT=SCEN[scen]; Po=P(sel,CAP,LC)
    PA=P(sel,CAP,LC,slice(0,iA)); PB=P(sel,CAP,LC,slice(iA,nb))
    kA=optimise(PA,DDT,SXT,GT); kB=optimise(PB,DDT,SXT,GT); kf=(kA+kB)/2
    okf=lambda t: (lambda m: m['dd']<=DDT and m['sx_dd']<=SXT and m['gap5']<=GT)(Po.met(t))
    lo,hi=0.0,1.5
    for _ in range(20):
        mm=(lo+hi)/2
        if okf(kf*mm): lo=mm
        else: hi=mm
    kv=floor_grid(Po,kf*lo); kv=climb(Po,kv,okf)
    return Po,kv
def finish(Po,kv,lab,ddmax=19.5):
    cent={k:round(f*u['lot0']/GS*0.01,2) for k,f,u in zip(Po.ks,kv,Po.U) if f*u['lot0']>=0.5*GS}
    r=mt5(cent,lab); s=1.0
    while r['dd_pct']>ddmax and s>0.5:   # trim on grid if MT5 DD above limit
        s-=0.02; c2={k:np.floor(v*s/0.01+1e-9)*0.01 for k,v in cent.items()}; c2={k:round(v,2) for k,v in c2.items() if v>=0.01}
        r=mt5(c2,lab); cent=c2
    kvf=kv_from_cent(Po,cent); m=Po.met(kvf)
    return dict(cent=cent,mt5=r,py=m,trim=s)
if __name__=='__main__':
    out={}
    for mode,univ,key in [('JOINT',UNIV,'JOINT_100k'),('XAU',XAU_U,'XAU_100k'),('US500',US_U,'US500_100k')]:
        sel=Oj[key]['greedy']['sel']
        for scen in ['conservative','balanced','aggressive']:
            Po,kv=tune(mode,univ,sel,scen); res=finish(Po,kv,f'{mode}_{scen}_cent')
            dropped=[k for k in sel if k not in res['cent']]
            res['dropped']=dropped; res['sel']=sel; out[f'{mode}_{scen}']=res
            r=res['mt5']; print(mode,scen,'n',len(res['cent']),'/',len(sel),'net$',round(r['net'],1),'dd',round(r['dd_pct'],1),'m+',r['npos'],'gap5',round(res['py']['gap5'],1),'sx2',round(res['py']['sx_dd'],1),'cent',res['cent'],'dropped',dropped,flush=True)
        # manual (gold systems only) conservative; US500 has none
    for mode,univ in [('JOINT',UNIV),('XAU',XAU_U)]:
        man=[k for k in MANUAL]; Po=P(man,CAP,scale_lc(univ,CAP)); DDT,SXT,GT=SCEN['conservative']
        kA=optimise(P(man,CAP,scale_lc(univ,CAP),slice(0,iA)),DDT,SXT,GT); kB=optimise(P(man,CAP,scale_lc(univ,CAP),slice(iA,nb)),DDT,SXT,GT)
        okf=lambda t: (lambda m: m['dd']<=DDT and m['sx_dd']<=SXT and m['gap5']<=GT)(Po.met(t))
        kf=(kA+kB)/2; lo,hi=0.0,1.5
        for _ in range(20):
            mm=(lo+hi)/2
            if okf(kf*mm): lo=mm
            else: hi=mm
        kv=climb(Po,floor_grid(Po,kf*lo),okf); res=finish(Po,kv,f'{mode}_manual_cent'); res['dropped']=[k for k in man if k not in res['cent']]; res['sel']=man
        out[f'{mode}_manual']=res
        r=res['mt5']; print(mode,'manual n',len(res['cent']),'net$',round(r['net'],1),'dd',round(r['dd_pct'],1),'gap5',round(res['py']['gap5'],1),'sx2',round(res['py']['sx_dd'],1),res['cent'],flush=True)
    json.dump(out,open(f'{V}/results/r6/opt9.json','w'),indent=1,default=float); print('WROTE')
