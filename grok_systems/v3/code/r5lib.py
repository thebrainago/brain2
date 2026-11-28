# Round 5 library: engine2 (risk stops) wrapper, signal cache, flat-array builder, curve generator.
import sys,os,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,'/workspace/bt_3m/code')
import engine2 as E2, bt, scalp as SC, cands as CD, lotscale as LS
V='/workspace/bt_3m/v3'; R5=f'{V}/results/r5'; os.makedirs(R5,exist_ok=True)
CAPA={'XAU':30000.,'US500':10000.}
REF={'g5':0.04,'g6':0.06,'u13':3.0,'u14':3.0,'g3':0.06,'g4':0.09,'u12':3.0,'x1':0.09,'x2':0.10,'x4':0.07,'g1':0.12,'g2':0.12,'u1':2.6,'u2':0.2,'u6':1.4,'u7':3.0,'u10':2.5,'u11':2.0}
S={n:(a,k,p,m) for n,a,k,p,m in LS.SYS}
_mx=dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30); _mu=dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30)
S['g3']=('XAU','b',dict(kind='new2',a='pw_break_flow',adx='gt20',sess='ldny'),_mx)
S['g4']=('XAU','b',dict(kind='new2',a='basis_mom',adx='gt20',sess='ldny'),_mx)
_mx2=dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30)
S['g5']=('XAU','b',dict(kind='new3',a='ad15z_fade2.0',adx='none',sess='ny'),_mx2)
S['g6']=('XAU','b',dict(kind='new3',a='sw30z_fade2.0',adx='gt20',sess='all'),_mx2)
S['u13']=('US500','b',dict(kind='new3',a='imb15z_mom2.0',adx='gt20',sess='all'),dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30))
S['u14']=('US500','b',dict(kind='new3',a='g3_15z_fade3.0',adx='none',sess='all'),_mu)
S['u12']=('US500','b',dict(kind='new2',a='rnd_break_50',adx='none',sess='ny'),_mu)
def flat_arr(D,fh=21,mode=1,hol=('2026-07-03','2026-09-07','2026-11-26')):
    t=D.index.tz_convert('Europe/Athens'); dow=t.dayofweek.values; h=t.hour.values
    fl=((dow==4)&(h>=fh)).astype(np.int64)
    for d in hol:
        dd=pd.Timestamp(d); day=t.normalize().tz_localize(None)
        fl[(day==dd)]=1
        prev=dd-pd.Timedelta(days=1); fl[(day==prev)&(h>=fh)]=1
    return fl*mode
_SIG={}
def sig(name,D):
    f=f'{R5}/sig_{name}.npy'
    if name in _SIG: return _SIG[name]
    if os.path.exists(f): s=np.load(f)
    else:
        a,k,p,m=S[name]; SC.init(a); s=CD.build_sig(D,a,p,{}); np.save(f,s)
    _SIG[name]=s; return s
def run2(name,D,fl,sprmul=1.0,slip=0.5,mo=None,hsk=0.0,hs_pct=0.0,dl_pct=0.0,maxN=None,maxlots=0.0,lot=None):
    """USD stops (hs_pct/dl_pct, % of asset capital at REF lot) are converted to base-lot USD (divide by scale)."""
    a,k,p,m=S[name]; m=dict(m if mo is None else mo)
    if maxN: m['maxN']=maxN
    if maxlots: m['maxlots']=maxlots
    P=bt.SPEC[a]; s=(lot or REF[name])/m['L0']; cap=CAPA[a]
    v=bt.mgmt_vec(a,m,sprmul,slip); v=np.r_[v,hsk,hs_pct/100*cap/s,dl_pct/100*cap/s]
    A=bt.arrays(D); sg=sig(name,D)
    spr=A['spr']
    out=E2.run(A['o'],A['h'],A['l'],A['c'],spr,A['atr'],np.ascontiguousarray(sg,dtype=np.int64),A['roll'],A['dow'],fl,v)
    ec,ew,nl,dep,st=out; ex=dep-P['EQ0']
    return dict(ec=(ec-ex-P['EQ0'])*s,ew=(ew-ex-P['EQ0'])*s,nl=nl*s,st=st,s=s,cap=cap)
