# Strict robustness battery for one basket config (PYTHON SIMULATION, base lot 1.0, USD per 1 lot).
import sys,os,json,zlib,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code')
import fxlib as F, fxsig as G
from fx_screen import PEER
def drift(D,mult):
    D=D.copy(); n=len(D); slope=(D.close.iloc[-1]-D.close.iloc[0])/n; add=mult*slope*np.arange(n)
    for c in ('open','high','low','close'): D[c]=D[c].values+add
    return D
def getsig(sym,sig,sess,D=None):
    D=F.table(sym) if D is None else D; pe=F.table(PEER[sym]) if sym in PEER and os.path.exists(f'{F.DATA}/{F.fname(PEER[sym])}.npz') else None
    S=G.build(D,pe); s=S[sig].astype(np.int64); return np.where(G.sess_mask(D,sess),s,0)
def one(D,s,I,med,gk,bk,maxN,sprmul=1.0,slip=0.5,swap=True,fl=None):
    o=F.run_basket(D,s,I['pv'],I['swl'] if swap else 0,I['sws'] if swap else 0,fl=fl,gap=gk*med,gatr=gk,btp=bk*med,maxN=maxN,sprmul=sprmul,slip=slip)
    return o
def stats(o,D,iso):
    ec,ew,nl,dep,st=o; en=ec-1e7; ewn=ew-1e7; pk=np.maximum.accumulate(en); dd=float(np.max(pk-ewn))
    def part(a,b):
        e=en[a:b]; w=ewn[a:b]; base=en[a-1] if a>0 else 0.0; p=np.maximum.accumulate(np.r_[base,e])[1:]; return float(e[-1]-base),float(np.max(p-w))
    nI,dI=part(1,iso); nO,dO=part(iso,len(en)); mon=pd.Series(en,index=D.index).groupby(D.index.strftime('%Y-%m')).last(); mm=mon.diff(); mm.iloc[0]=mon.iloc[0]
    return dict(net=float(en[-1]),dd=dd,nb=int(st[0]),wins=int(st[1]),maxlot=float(st[5]),netI=nI,ddI=dI,netO=nO,ddO=dO,mpos=int((mm>0).sum()),mn=len(mm),minm=float(mm.min()),months={k:round(float(v)) for k,v in mm.items()})
def battery(sym,sig,sess,gk,bk,maxN,nplace=40):
    D=F.table(sym); I=F.info(sym); iso=int(np.searchsorted(D.index,F.IS_END)); med=float(D.atr60.iloc[:iso].median()); fl=F.flat_arr(D); s=getsig(sym,sig,sess,D); r=dict(sym=sym,sig=sig,sess=sess,gk=gk,bk=bk,maxN=maxN,med=med,pv=I['pv'],swl=I['swl'],sws=I['sws'])
    o=one(D,s,I,med,gk,bk,maxN,fl=fl); r['base']=stats(o,D,iso)
    ec,ew,nl,dep,st=o; en=ec-1e7; pk=np.maximum.accumulate(en); px=D.close.values
    for X in (0.03,0.05): r[f'gapdd{int(X*100)}_up']=float(np.max(pk-(en-np.maximum(-nl,0)*I['pv']*px*X))); r[f'gapdd{int(X*100)}_dn']=float(np.max(pk-(en-np.maximum(nl,0)*I['pv']*px*X)))
    for nm,kw in (('spr2',dict(sprmul=2.0,slip=1.0)),('spr3',dict(sprmul=3.0,slip=1.0)),('noswap',dict(swap=False))):
        r[nm]=stats(one(D,s,I,med,gk,bk,maxN,fl=fl,**kw),D,iso)
    r['delay2']=stats(one(D,np.r_[np.zeros(2,np.int64),s[:-2]],I,med,gk,bk,maxN,fl=fl),D,iso)
    for nm,mu in (('detr',-1.0),('rev',-2.0)):
        r[nm]=stats(one(drift(D,mu),s,I,med,gk,bk,maxN,fl=fl),D,iso)
    r['long']=stats(one(D,np.where(s>0,s,0),I,med,gk,bk,maxN,fl=fl),D,iso); r['short']=stats(one(D,np.where(s<0,s,0),I,med,gk,bk,maxN,fl=fl),D,iso)
    nets=[]; nz=np.nonzero(s)[0]
    for seed in range(nplace):
        rg=np.random.default_rng(seed); sp=s.copy(); sp[nz]=s[nz]*rg.choice([-1,1],size=len(nz)); nets.append(stats(one(D,sp,I,med,gk,bk,maxN,fl=fl),D,iso)['net'])
    nets=np.array(nets); r['placebo_pct']=float((nets<r['base']['net']).mean()*100); r['placebo_med']=float(np.median(nets)); r['placebo_max']=float(nets.max())
    return r
if __name__=='__main__':
    sym,sig,sess,gk,bk,mN=sys.argv[1:7]; r=battery(sym,sig,sess,float(gk),float(bk),int(mN))
    out=f'{F.RES}/bat_{F.fname(sym)}_{sig}_{sess}_{gk}_{bk}_{mN}.json'; json.dump(r,open(out,'w'),indent=1)
    b=r['base']
    print(sym,sig,sess,'net %.0f dd %.0f nb %d | IS %.0f/%.0f OOS %.0f/%.0f | mpos %d/%d'%(b['net'],b['dd'],b['nb'],b['netI'],b['ddI'],b['netO'],b['ddO'],b['mpos'],b['mn']))
    for k in ('spr2','spr3','noswap','delay2','detr','rev','long','short'): print(' ',k,'net %.0f dd %.0f nb %d'%(r[k]['net'],r[k]['dd'],r[k]['nb']))
    print('  placebo pct %.0f med %.0f max %.0f'%(r['placebo_pct'],r['placebo_med'],r['placebo_max']),'gap5 up/dn %.0f/%.0f'%(r['gapdd5_up'],r['gapdd5_dn']))
