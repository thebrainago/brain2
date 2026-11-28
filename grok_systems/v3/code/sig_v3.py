# v3 signal library. decision at bar close i (executed next bar open). +1 long, -1 short. SIMULATED research only.
import numpy as np, pandas as pd
def N(D,c): return np.nan_to_num(D[c].values.astype(float))
def NN(D,c): return D[c].values.astype(float)
def sg(x): return np.sign(x)
def first_per_day(s,D):
    """keep only first signal per (nyday, direction)"""
    key=pd.Series(D.nyday.values)
    out=np.zeros_like(s)
    for d in (1,-1):
        m=pd.Series(s==d); seen=m.groupby(key).cumsum(); out=np.where(m&(seen==1),d,out)
    return out
def fam_sw(D,k,w,mode):
    z=N(D,f'sw{w}z'); s=np.where(np.abs(z)>k,-sg(z) if mode=='fade' else sg(z),0); return s
def fam_dz(D,k,w,mode):
    z=N(D,f'd{w}z'); return np.where(np.abs(z)>k,-sg(z) if mode=='fade' else sg(z),0)
def fam_dz_stretch(D,k,w):
    # delta extreme AGAINST vwap stretch (existing d15_fade)
    z=N(D,f'd{w}z'); v=N(D,'vwap_dev'); return np.where((np.abs(z)>k)&(sg(v)==sg(z))&(np.abs(v)>1.0),-sg(z),0)
def fam_big(D,k,i,w,mode):
    z=N(D,f'g{i}_{w}z'); return np.where(np.abs(z)>k,sg(z) if mode=='mom' else -sg(z),0)
def fam_cvd_div(D,k,w):
    sd=N(D,'cvd_sd')*np.sqrt(w); f=NN(D,'f_c'); c=NN(D,'f_cvd')
    bear=(f>=NN(D,f'fhi{w}'))&((NN(D,f'chi{w}')-c)>k*sd); bull=(f<=NN(D,f'flo{w}'))&((c-NN(D,f'clo{w}'))>k*sd)
    return np.where(bear,-1,np.where(bull,1,0))
def fam_absorb(D,kz,w,kr,mode='fade'):
    z=N(D,f'd{w}z'); r=np.abs(N(D,f'fr{w}')); vr=N(D,f'vr{w}')
    ok=(np.abs(z)>kz)&(r<kr)&(vr>1.0); return np.where(ok,-sg(z) if mode=='fade' else sg(z),0)
def fam_stk(D,k,w,mode):
    v=N(D,f'stk{w}'); return np.where(np.abs(v)>=k,sg(v) if mode=='mom' else -sg(v),0)
def fam_imb(D,k,w,mode):
    v=N(D,f'imb{w}z'); return np.where(np.abs(v)>k,sg(v) if mode=='mom' else -sg(v),0)
def fam_vwapz(D,k):
    z=N(D,'vwap_z'); return np.where(np.abs(z)>k,-sg(z),0)
def fam_vwap_atr(D,k):
    v=N(D,'vwap_dev'); return np.where(np.abs(v)>k,-sg(v),0)
def fam_vwap_cross(D,k):
    v=N(D,'vwap_dev'); pv=np.roll(v,1); return np.where((sg(v)!=sg(pv))&(sg(N(D,'d15'))==sg(v))&(np.abs(N(D,'d15z'))>k),sg(v),0)
def fam_orb_brk(D,orn,buf):
    hi=NN(D,orn+'_hi'); lo=NN(D,orn+'_lo'); c=D.close.values; pc=np.roll(c,1); a=N(D,'atr5')*buf
    s=np.where((c>hi+a)&(pc<=hi+a),1,np.where((c<lo-a)&(pc>=lo-a),-1,0)); s=np.where(np.isfinite(hi),s,0); return first_per_day(s,D)
def fam_orb_fail(D,orn,win):
    hi=NN(D,orn+'_hi'); lo=NN(D,orn+'_lo'); h=D.high.values; l=D.low.values; c=D.close.values
    s=np.where((h>hi)&(c<hi),-1,np.where((l<lo)&(c>lo),1,0)); s=np.where(np.isfinite(hi),s,0); return s
def fam_pd_sweep(D,lvl,flow):
    if lvl=='pd': hi,lo=NN(D,'pdH'),NN(D,'pdL')
    elif lvl=='as': hi,lo=NN(D,'as_hi'),NN(D,'as_lo')
    elif lvl=='day': hi,lo=NN(D,'dH'),NN(D,'dL')
    h=D.high.values; l=D.low.values; c=D.close.values
    s=np.where((h>hi)&(c<hi),-1,np.where((l<lo)&(c>lo),1,0)); s=np.where(np.isfinite(hi),s,0)
    if flow: s=np.where(sg(N(D,'d5'))==-s,0,s)  # require no strong same-direction buying into sweep? (flow: delta not confirming break)
    return s
def fam_pd_brk(D,k):
    hi,lo=NN(D,'pdH'),NN(D,'pdL'); c=D.close.values; pc=np.roll(c,1); a=N(D,'atr5')*k
    s=np.where((c>hi+a)&(pc<=hi+a),1,np.where((c<lo-a)&(pc>=lo-a),-1,0)); s=np.where(np.isfinite(hi),s,0); return first_per_day(s,D)
def fam_va_fail(D,mode):
    vah,val_=NN(D,'vah_p'),NN(D,'val_p'); c=D.close.values; pc=np.roll(c,1)
    s=np.where((pc>vah)&(c<=vah),-1,np.where((pc<val_)&(c>=val_),1,0))
    if mode=='brk': s=np.where((pc<=vah)&(c>vah),1,np.where((pc>=val_)&(c<val_),-1,0))
    return np.where(np.isfinite(vah),s,0)
def fam_poc_rev(D,k):
    p=NN(D,'poc_p'); c=D.close.values; a=N(D,'atr5'); dist=(c-p)/np.where(a>0,a,np.nan); 
    return np.where(np.isfinite(dist)&(np.abs(dist)>k),-sg(dist),0)
def fam_nq_lead(D,k,w,mode):  # cross: aux asset return z vs own return z
    a=N(D,f'ar{w}z'); o=N(D,f'fz{w}z'); ok=D.a_ok.values
    if mode=='catchup': s=np.where((np.abs(a)>k)&(np.abs(o)<k*0.4)&(sg(a)!=-sg(o)),sg(a),0)
    elif mode=='follow': s=np.where(np.abs(a)>k,sg(a),0)
    elif mode=='inverse': s=np.where(np.abs(a)>k,-sg(a),0)
    elif mode=='fadeself': s=np.where((np.abs(o)>k)&(np.abs(a)<k*0.4),-sg(o),0)
    return s*ok
def fam_adz(D,k,w,mode):
    a=N(D,f'ad{w}z'); ok=D.a_ok.values; return np.where(np.abs(a)>k,sg(a) if mode=='follow' else -sg(a),0)*ok
def fam_ema_pull(D):
    c=D.close.values; e=N(D,'ema20'); pc=np.roll(c,1); pe=np.roll(e,1); sl=N(D,'ema55_slope')
    return np.where((sl>0)&(pc<pe)&(c>e),1,np.where((sl<0)&(pc>pe)&(c<e),-1,0))
def fam_open_drive(D,t0,t1,mode):
    """NY-time-of-day: at ny_t==t1, direction of move since t0 (minutes of NY day). one per day."""
    nt=D.ny_t.values; c=D.close.values; o=D.open.values
    # price at t0 open
    k0=pd.Series(np.where(nt==t0,o,np.nan)); k0=k0.groupby(D.nyday.values).transform('max').values
    mv=c-k0; a=N(D,'atr5'); s=np.where((nt==t1)&np.isfinite(mv)&(np.abs(mv)>0.3*a),sg(mv) if mode=='mom' else -sg(mv),0); return s
def fam_ibs(D,k):
    nt=D.ny_t.values; ib=N(D,'ibs_prev'); t=0.1*k; at=(nt==9*60+31)
    return np.where(at&(ib<t),1,np.where(at&(ib>1-t),-1,0))
def fam_placebo(D,k,seed=0):
    rng=np.random.default_rng(seed+int(k)); at=(D.minute.values==0)&(D.hour.values%int(k)==0); return np.where(at,np.where(rng.random(len(D))<0.5,1,-1),0)
def filters(D,s,adx,sess,asset,nonews=True):
    s=np.asarray(s,float).copy(); a=N(D,'adx'); h=D.hour.values
    if adx=='gt20': s=np.where(a>20,s,0)
    elif adx=='lt25': s=np.where(a<25,s,0)
    if sess=='ldny': s=np.where((h>=7)&(h<20),s,0)
    elif sess=='ny': s=np.where((h>=13)&(h<20),s,0)
    elif sess=='ldn': s=np.where((h>=7)&(h<13),s,0)
    elif sess=='asia': s=np.where((h<7),s,0)
    if nonews: s=np.where(D.news.values,0,s)
    return s.astype(np.int8)
def specs(asset):
    """yield (name, fn(D)->raw signal). fut_ok gating applied inside screen."""
    L=[]
    for k in (1.5,1.8,2.2,3.0):
        for w in (15,30):
            for m in ('fade','mom'): L.append((f'sw_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_sw(D,k,w,m)))
    for k in (1.5,2.0,2.5,3.0):
        for w in (5,15,30,60):
            for m in ('fade','mom'): L.append((f'dz_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_dz(D,k,w,m)))
    for k in (2.0,3.0):
        for w in (15,30): L.append((f'dzstr_{w}_{k}',lambda D,k=k,w=w:fam_dz_stretch(D,k,w)))
    for i in (1,2,3):
        for k in (1.5,2.0,2.5):
            for w in (30,60):
                for m in ('mom','fade'): L.append((f'big{i}_{m}_{w}_{k}',lambda D,k=k,i=i,w=w,m=m:fam_big(D,k,i,w,m)))
    for w in (15,30,60):
        for k in (0.5,1.0,2.0): L.append((f'cvddiv_{w}_{k}',lambda D,k=k,w=w:fam_cvd_div(D,k,w)))
    for w in (5,15,30):
        for kz in (1.5,2.0):
            for kr in (0.25,0.5,1.0):
                for m in ('fade','mom'): L.append((f'absorb_{m}_{w}_{kz}_{kr}',lambda D,kz=kz,w=w,kr=kr,m=m:fam_absorb(D,kz,w,kr,m)))
    for w in (5,15,30):
        for k in (2,3,5,8):
            for m in ('mom','fade'): L.append((f'stk_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_stk(D,k,w,m)))
        for k in (1.5,2.0,2.5):
            for m in ('mom','fade'): L.append((f'imb_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_imb(D,k,w,m)))
    for k in (1.5,2.0,2.5,3.0): L.append((f'vwapz_{k}',lambda D,k=k:fam_vwapz(D,k)))
    for k in (1,2,3,4): L.append((f'vwapatr_{k}',lambda D,k=k:fam_vwap_atr(D,k)))
    for k in (1.0,2.0): L.append((f'vwapx_{k}',lambda D,k=k:fam_vwap_cross(D,k)))
    ors=['nyor','nyib'] if asset=='US500' else ['cxor','lnor','nyor']
    for orn in ors:
        for buf in (0.0,0.3): L.append((f'orbbrk_{orn}_{buf}',lambda D,orn=orn,buf=buf:fam_orb_brk(D,orn,buf)))
        L.append((f'orbfail_{orn}',lambda D,orn=orn:fam_orb_fail(D,orn,15)))
    for lvl in ('pd','day')+(('as',) if asset=='XAU' else ()):
        for fl_ in (0,1): L.append((f'sweep_{lvl}_{fl_}',lambda D,lvl=lvl,fl_=fl_:fam_pd_sweep(D,lvl,fl_)))
    for k in (0.0,0.3): L.append((f'pdbrk_{k}',lambda D,k=k:fam_pd_brk(D,k)))
    for m in ('fail','brk'): L.append((f'va_{m}',lambda D,m=m:fam_va_fail(D,m)))
    for k in (1.5,2.5,4.0): L.append((f'pocrev_{k}',lambda D,k=k:fam_poc_rev(D,k)))
    for k in (1.5,2.0,2.5):
        for w in (5,15):
            for m in ('catchup','follow','inverse','fadeself'): L.append((f'xlead_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_nq_lead(D,k,w,m)))
            for m in ('follow','inv'): L.append((f'xdelta_{m}_{w}_{k}',lambda D,k=k,w=w,m=m:fam_adz(D,k,w,m)))
    L.append(('emapull',lambda D:fam_ema_pull(D)))
    t_ny=(9*60+30,9*60+45); 
    if asset=='US500':
        for t0,t1 in [(570,600),(570,585),(570,630)]:
            for m in ('mom','fade'): L.append((f'opendrive_{m}_{t0}_{t1}',lambda D,t0=t0,t1=t1,m=m:fam_open_drive(D,t0,t1,m)))
        for k in (1,2,3): L.append((f'ibs_{k}',lambda D,k=k:fam_ibs(D,k)))
    else:
        for t0,t1 in [(500,530),(500,515),(500,560)]:
            for m in ('mom','fade'): L.append((f'opendrive_{m}_{t0}_{t1}',lambda D,t0=t0,t1=t1,m=m:fam_open_drive(D,t0,t1,m)))
    for k in (2,3,4,6): L.append((f'placebo_{k}',lambda D,k=k:fam_placebo(D,k)))
    return L
GRID_ADX=['none','gt20']; GRID_SESS=['all','ldny','ny','ldn']
