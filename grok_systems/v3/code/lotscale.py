# Lot scaling + portfolio optimisation. Step1: cache k=1 curves (base & spread x2) per system -> results/curves/*.pkl (skip if exists)
import sys,os,json,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,portfolio as P
V='/workspace/bt_3m/v3'; CD_=f'{V}/results/curves'; os.makedirs(CD_,exist_ok=True)
X=P.X; mgx=P.mgx; mgu=P.mgu
mgu['u1']=mgu['u1']
SYS=[('x1','XAU','b',X('sw_fade_15_1.8','gt20','ldny'),mgx['nh8']),('x2','XAU','b',X('sw_fade_15_1.8','gt20','ldny'),mgx['c3']),
 ('x4','XAU','b',X('dz_fade_15_2.0','none','ldn'),mgx['nh8']),('x5','XAU','b',X('sw_fade_15_1.8','gt20','all','vwapatr_3',30),mgx['nh8']),
 ('xs1','XAU','s',X('xlead_fadeself_5_2.5','gt20','all','big2_mom_30_2.5',30),(8.0,8.0,90,0.1)),
 ('xs2','XAU','s',X('big3_mom_60_2.0','none','ny','emapull',30),(8.0,13.0,90,0.1)),
 ('u1','US500','b',X('sw_fade_15_1.8','gt20','ldny'),mgu['u1']),('u2','US500','b',X('absorb_fade_5_1.5_1.0','none','ny'),mgu['u2']),
 ('u3','US500','b',X('sw_fade_15_1.8','gt20','ny','absorb_fade_5_1.5_1.0',30),mgu['u3']),('u5','US500','b',X('sw_fade_15_1.8','gt20','ldny'),mgu['c1']),
 ('u6','US500','b',X('dz_mom_5_1.5','none','all'),mgu['u2']),('u7','US500','b',X('sw_fade_15_1.5','none','all'),mgu['u2']),
 ('g1','XAU','b',dict(kind='new',a='pd_break_flow',adx='gt20',sess='ldny'),dict(L0=0.03,mult=1.0,gap=4,gstep=1.4,maxN=3,btp=2,trim=0,prune=0,hedge=0,cd=30)),('g2','XAU','b',dict(kind='new',a='lnor_break_trend',adx='gt20',sess='all'),dict(L0=0.03,mult=1.0,gap=4,gstep=1.4,maxN=3,btp=2,trim=0,prune=0,hedge=0,cd=30)),('u10','US500','b',dict(kind='new',a='orbd_mom',adx='gt20',sess='all'),dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30)),('u11','US500','b',dict(kind='new',a='asia_fail',adx='gt20',sess='ldny'),dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30)),
 ('u8','US500','b',X('stk_fade_15_2','none','ldny'),mgu['u2']),('u9','US500','b',X('imb_mom_15_1.5','none','ldny'),mgu['u3'])]
def curves(name,a,kind,p,m,D,raw):
    s=CD.build_sig(D,a,p,raw); out={}
    if kind=='b':
        Pp=bt.SPEC[a]
        for tag,sm in (('base',1.0),('sx2',2.0)):
            ec,ew,nl,dep,st=bt.run(a,s,m,D=D,sprmul=sm); ex=dep-Pp['EQ0']
            out[tag]=(ec-ex-Pp['EQ0'],ew-ex-Pp['EQ0'])
        out['lot']=m['L0']; out['pf_note']=None
    else:
        sl,tp,hold,lot=m; A=SC.G['A']; one=np.ones(len(D)); ok=np.ones(len(D),bool); pv=bt.SPEC[a]['pv']
        for tag,sm in (('base',1.0),('sx2',2.0)):
            idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr']*sm,one,sl,tp,hold,0.5); usd=pn*lot*pv
            ec=np.zeros(len(D)); ew=np.zeros(len(D)); step=np.zeros(len(D)); stepw=np.zeros(len(D))
            np.add.at(step,ex,usd); ecum=np.cumsum(step); np.add.at(stepw,ex,np.minimum(usd,0)); ewv=ecum-np.cumsum(stepw)*0+0
            ew=ecum+np.minimum(step,0)  # worst realised at exit bar
            out[tag]=(ecum,ew); 
            if tag=='base': out['pf']=float(usd[usd>0].sum()/-usd[usd<=0].sum()); out['n']=len(usd)
        out['lot']=lot
    out['index']=D.index; return out
if __name__=='__main__':
    for asset in ('XAU','US500'):
        D=bt.table(asset); SC.init(asset); raw={}
        for n,a,k,p,m in SYS:
            if a!=asset: continue
            f=f'{CD_}/{n}.pkl'
            if os.path.exists(f): continue
            o=curves(n,a,k,p,m,D,raw); pickle.dump(o,open(f,'wb')); print('saved',n,flush=True)
    print('CURVES DONE',flush=True)
