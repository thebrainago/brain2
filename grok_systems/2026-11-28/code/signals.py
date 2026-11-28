# Entry-signal factory (decision at bar close i, executed at open i+1 in engine). SIMULATED research only.
import numpy as np, pandas as pd, itertools
def base(D,fam,k):
    z=lambda a: np.nan_to_num(np.asarray(a,float))
    of=D.fut_ok.values
    if fam=='d15_fade': s=np.where((np.abs(z(D.d15z))>k)&(np.sign(z(D.vwap_dev))==np.sign(z(D.d15z)))&(np.abs(z(D.vwap_dev))>1.0),-np.sign(z(D.d15z)),0)*of
    elif fam=='d15_mom': s=np.where(np.abs(z(D.d15z))>k,np.sign(z(D.d15z)),0)*of
    elif fam=='big30': s=np.where(np.abs(z(D.big30z))>k,np.sign(z(D.big30z)),0)*of
    elif fam=='sw_fade': s=np.where(np.abs(z(D.sw15z))>k,-np.sign(z(D.sw15z)),0)*of
    elif fam=='sw_mom': s=np.where(np.abs(z(D.sw15z))>k,np.sign(z(D.sw15z)),0)*of
    elif fam=='cvd_div':
        cz=z(D.cvd30)/np.nanstd(D.cvd30.values); s=np.where((np.abs(cz)>k*0.5)&(np.sign(z(D.fpx30))==-np.sign(cz)),np.sign(cz),0)*of
    elif fam=='vwap_rev': s=np.where(np.abs(z(D.vwap_dev))>k+1,-np.sign(z(D.vwap_dev)),0)*of
    elif fam=='vwap_mom':
        v=z(D.vwap_dev); pv=np.roll(v,1); s=np.where((np.sign(v)!=np.sign(pv))&(np.sign(z(D.d15))==np.sign(v))&(np.abs(z(D.d15z))>k*0.5),np.sign(v),0)*of
    elif fam=='poc_touch': s=np.where(np.abs(z(D.poc_dist))<0.15*k,z(D.ema55_side),0)*of*np.isfinite(D.poc_dist.values)
    elif fam=='ema_pull':
        c=D.close.values; e=z(D.ema20); pc=np.roll(c,1); pe=np.roll(e,1); sl=z(D.ema55_slope)
        s=np.where((sl>0)&(pc<pe)&(c>e),1,np.where((sl<0)&(pc>pe)&(c<e),-1,0))
    elif fam=='ibs':
        ny=D.index.tz_convert('America/New_York'); at=(ny.hour==9)&(ny.minute==31); ib=z(D.ibs_prev); t=0.1*k
        s=np.where(at&(ib<t),1,np.where(at&(ib>1-t),-1,0))
    elif fam=='placebo':
        ny=D.index.tz_convert('America/New_York'); at=(ny.minute==0)&(ny.hour%int(k)==0)
        s=np.where(at,np.where(np.random.default_rng(int(k)).random(len(D))<0.5,1,-1),0)
    return np.asarray(s,float)
def filt(D,s,trend,adx,macro,side,sess,asset):
    s=s.copy(); z=lambda a: np.nan_to_num(np.asarray(a,float))
    if trend=='slope': s=np.where(np.sign(s)==z(D.ema55_slope),s,0)
    elif trend=='side': s=np.where(np.sign(s)==z(D.ema55_side),s,0)
    elif trend=='e200': s=np.where(np.sign(s)==np.sign(z(D.close-D.ema200)),s,0)
    a=z(D.adx)
    if adx=='lt25': s=np.where(a<25,s,0)
    elif adx=='gt20': s=np.where(a>20,s,0)
    if macro=='on':
        if asset=='US500':
            ro=z(D.VIXCLS)<20; s=np.where(((s>0)&ro)|((s<0)&~ro),s,0)
        else:
            up=(z(D.ry5)<0)|(z(D.dxy5)<0); s=np.where(((s>0)&up)|((s<0)&~up),s,0)
    if side=='long': s=np.where(s>0,s,0)
    elif side=='short': s=np.where(s<0,s,0)
    if sess=='ldny': h=D.hour.values; s=np.where((h>=7)&(h<20),s,0)
    s=np.where(D.news.values,0,s)
    return s.astype(np.int64)
FAMS={'d15_fade':[2,3],'d15_mom':[2,3],'big30':[1.5,2.5],'sw_fade':[2,3],'sw_mom':[2,3],'cvd_div':[2,3],'vwap_rev':[1,2],
      'vwap_mom':[1,2],'poc_touch':[1,2],'ema_pull':[1],'ibs':[1,2,3],'placebo':[2,4]}
GRID=dict(trend=['none','slope','side','e200'],adx=['none','lt25','gt20'],macro=['none','on'],side=['both','long','short'],sess=['all','ldny'])
def all_specs():
    for fam,ks in FAMS.items():
        for k in ks:
            for t,a,m,sd,se in itertools.product(*GRID.values()):
                yield dict(fam=fam,k=k,trend=t,adx=a,macro=m,side=sd,sess=se)
def make(D,spec,asset):
    return filt(D,base(D,spec['fam'],spec['k']),spec['trend'],spec['adx'],spec['macro'],spec['side'],spec['sess'],asset)
