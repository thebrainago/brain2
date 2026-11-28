# Stage 2: DCA-basket (engine2, no SL, basket TP, Friday flatten, swap) over all signals x session x mgmt grid; IS/OOS from one run's equity curve.
import sys,os,itertools,time,zlib,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/fx/code')
import fxlib as F, fxsig as G
from fx_screen import PEER
GR2=list(itertools.product((1.0,2.0,4.0),(1.0,2.0,4.0),(3,5)))
GR=list(itertools.product((0.5,1.0),(0.25,0.5,1.0),(3,5)))   # gap_k(ATR60), btp_k(ATR60), maxN
SESSN=('all','asia','ldn','ny'); PL=int(os.environ.get('PLACEBO','-1')); TAG='bask' if PL==-1 else ('mir' if PL==-2 else f'pl{PL}')
def part(en,ew,a,b):
    e=en[a:b]; w=ew[a:b]; base=en[a-1] if a>0 else 0.0
    pk=np.maximum.accumulate(np.r_[base,e])[1:]; return float(e[-1]-base),float(np.max(pk-w))
def run_sym(sym):
    D=F.table(sym); I=F.info(sym); pe=F.table(PEER[sym]) if sym in PEER and os.path.exists(f'{F.DATA}/{F.fname(PEER[sym])}.npz') else None
    S=G.build(D,pe); iso=int(np.searchsorted(D.index,F.IS_END)); n=len(D); med=float(D.atr60.iloc[:iso].median()); fl=F.flat_arr(D)
    mon=pd.factorize(D.index.strftime('%Y-%m'),sort=True)[0]; last=np.r_[np.nonzero(np.diff(mon))[0],n-1]; out=[]
    sm={k:G.sess_mask(D,k) for k in SESSN}
    for nm,s in S.items():
        s=s.astype(np.int64)
        if PL==-2: s=-s
        if PL>=0:
            rg=np.random.default_rng(PL*7919+zlib.crc32(nm.encode())%1000); nz=np.nonzero(s)[0]; s=s.copy(); s[nz]=s[nz]*rg.choice([-1,1],size=len(nz))
        for sk in SESSN:
            s2=np.where(sm[sk],s,0)
            if (s2!=0).sum()<(25 if nm.startswith("L_") else 60): continue
            for gk,bk,mN in (GR2 if nm.startswith('L_') else GR):
                o=F.run_basket(D,s2,I['pv'],I['swl'],I['sws'],fl=fl,gap=gk*med,gatr=gk,btp=bk*med,maxN=mN)
                ec,ew,nl,dep,st=o; en=ec-1e7; ewn=ew-1e7
                nI,dI=part(en,ewn,1,iso); nO,dO=part(en,ewn,iso,n); cum=en[last]; mm=np.diff(np.r_[0,cum])
                out.append(dict(sym=sym,sig=nm,sess=sk,gk=gk,bk=bk,maxN=mN,nb=int(st[0]),wins=int(st[1]),maxlot=float(st[5]),netI=nI,ddI=dI,netO=nO,ddO=dO,mpos=int((mm>0).sum()),mn=len(mm),minm=float(mm.min()),net=nI+nO))
    R=pd.DataFrame(out); R['pv']=I['pv']; R['med']=med; R.to_parquet(f'{F.RES}/{TAG}_{F.fname(sym)}.parquet'); return len(R)
if __name__=='__main__':
    for s in sys.argv[1:]:
        t=time.time(); print(s,run_sym(s),round(time.time()-t),flush=True)
