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

# Round 6 basket finalists (newsig4)
_m0u=dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30)
S['g7']=('XAU','b',dict(kind='new4',a='imb30z_fade2.0',adx='gt20',sess='all'),_mx2)
S['u15']=('US500','b',dict(kind='new4',a='fz5z_fade2.0',adx='none',sess='ny'),_m0u)
S['u16']=('US500','b',dict(kind='new4',a='vclimax_fade_3',adx='none',sess='ldny'),_mu)
S['u17']=('US500','b',dict(kind='new4',a='vclimax_mom_2',adx='none',sess='ny'),_mu)
S['u18']=('US500','b',dict(kind='new4',a='fz30z_fade2.0',adx='none',sess='all'),_mu)
S['u19']=('US500','b',dict(kind='new4',a='g2_60z_mom2.0',adx='none',sess='all'),_mu)
REF.update({'g7':0.06,'u15':2.0,'u16':2.0,'u17':2.0,'u18':2.0,'u19':2.0})

# Round 6b confluence-pair baskets (newsig5)
S['gp1']=('XAU','b',dict(kind='new5',a='pair:n2:pw_break_flow+v3:emapull',adx='none',sess='all'),_mx2)
S['gp2']=('XAU','b',dict(kind='new5',a='pair:v3:sw_fade_15_1.8+v3:dz_fade_15_2.0',adx='gt20',sess='all'),_mx2)
S['gp3']=('XAU','b',dict(kind='new5',a='pair:v3:dz_fade_15_2.0+n4:imb30z_fade2.0',adx='gt20',sess='all'),_mx2)
S['up1']=('US500','b',dict(kind='new5',a='pair:v3:sw_fade_15_1.8+v3:sw_fade_15_1.5',adx='none',sess='all'),_mu)
S['up2']=('US500','b',dict(kind='new5',a='pair:v3:dz_mom_5_1.5+n2:rnd_break_50',adx='none',sess='ny'),_mu)
S['up3']=('US500','b',dict(kind='new5',a='pair:v3:sw_fade_15_1.5+n4:vclimax_fade_3',adx='none',sess='ldny'),_mu)
REF.update({'gp1':0.06,'gp2':0.06,'gp3':0.06,'up1':2.0,'up2':2.0,'up3':1.5})
