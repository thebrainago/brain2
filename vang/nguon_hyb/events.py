import numpy as np, pandas as pd, sys, json
from numba import njit
sys.path.insert(0,'/workspace/sp500_sys')
from sim import PCT, FIB
d=pd.read_pickle('m1h.pkl'); vp=np.load('/workspace/sp500_sys/out/vp.npy'); opt=np.load('opt.npy')
o,h,l,c,a15=[d[k].values for k in ['o','h','l','c','a15']]; zx=d.zz_ext.values; zlo=d.zz_lo.values; n=len(d)
@njit(cache=True)
def hruns(h,zx):
    n=len(h); out=np.zeros(n); last=-1; hr=0.0
    for i in range(1,n):
        if zx[i]!=last:
            last=zx[i]; hr=0.0
            for j in range(zx[i],i):
                if h[j]>hr: hr=h[j]
        elif h[i-1]>hr: hr=h[i-1]
        out[i]=hr
    return out
@njit(cache=True)
def label(o,h,l,a,idx,up,dn,hor,spr):
    y=np.zeros(len(idx)); mae=np.zeros(len(idx))
    for k in range(len(idx)):
        i=idx[k]; e=o[i]+spr; tu=e+up*a[i-1]; td=e-dn*a[i-1]; y[k]=0; mn=0.0
        for j in range(i,min(i+hor,len(o))):
            if l[j]-e<mn: mn=l[j]-e
            if l[j]<=td: y[k]=0; break
            if h[j]>=tu: y[k]=1; break
        mae[k]=mn/a[i-1]
    return y,mae
if __name__=='__main__':
    hr=hruns(h,zx); d['hrun']=hr; d[['hrun']].to_pickle('hrun.pkl')
    m5=d.m5end.values
    idx=np.where(np.r_[False,m5[:-1]])[0]; idx=idx[(idx>300)&(idx<n-300)]
    a=a15[idx-1]; dep=(hr[idx]-o[idx])/a
    idx=idx[dep>=2.68]; a=a15[idx-1]; dep=(hr[idx]-o[idx])/a
    F=pd.DataFrame(dict(i=idx,t=d.t.values[idx],depth=dep))
    def near(levels,px,aa,tol=0.4): return np.any(np.abs(levels-px)<=tol*aa)
    fp=[];ff=[];fv=[];fo=[]
    for k,i in enumerate(idx):
        H=hr[i]; Lo=zlo[i]; aa=a[k]; px=o[i]
        fp.append(near(H-PCT*aa,px,aa)); leg=H-Lo
        ff.append(near(H-FIB*leg,px,aa) if leg>0 else False)
        v=vp[d.didx.values[i]]; v=v[~np.isnan(v)]; fv.append(near(v,px,aa) if len(v) else False)
        q=opt[i]; q=q[~np.isnan(q)]; fo.append(near(q,px,aa) if len(q) else False)
    F['z_pct']=fp; F['z_fib']=ff; F['z_vp']=fv; F['z_opt']=fo
    F['has_opt']=~np.isnan(opt[idx,0])
    for k in ['rsi5','vwz','bbz','rej','us','usopen','reg']: F[k]=d[k].values[idx]
    F['rsi30']=F.rsi5<30; F['vw2']=F.vwz<-2; F['vw1']=(F.vwz<-1)&(F.vwz>=-2); F['bb2']=F.bbz<-2; F['regH']=F.reg>1.5; F['regL']=F.reg<0.8
    F['deep70']=F.depth>=4.55; F['deep90']=F.depth>=8.48
    y,mae=label(o,h,l,a15,idx,1.0,2.0,288,0.65); F['y']=y; F['mae']=mae
    F.to_pickle('events.pkl'); print(len(F), F.y.mean().round(3)); print(F.groupby('has_opt').size())
