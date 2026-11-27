# Giai doan B: cam tin hieu orderflow ESZ6 (Fxaurum, tick co chieu chu dong) vao diem vao S va vung (vp) cua dong co HYB+AG
# (sim_ag.run, cau hinh goc sweep_big.mkP K3 coef1.3 G3 snap1 maxL10 tp1 1.0 refill1 bx0 hr1.0 th1.5).
# Gio may chu XM = gio New York + 7h (kiem bang tuong quan loi suat phut ES vs US500: 0.995/0.997).
# Tin hieu tinh xong o cuoi phut ES t, chi duoc dung tu thanh M1 bat dau >= t+2 phut (tranh nhin truoc). Ngoai RTH = 0 (trung tinh).
import sys, os, glob, json, numpy as np, pandas as pd
SB='/workspace/sp500_sys/big/sweep_big'; sys.path.insert(0,SB)
import sweep_big as B
D=sys.argv[1] if len(sys.argv)>1 else '/workspace/sp500_2711/tick_esz6'
OUT=sys.argv[2] if len(sys.argv)>2 else '/workspace/brain2/sp500/ket_qua/hyb_of'
os.makedirs(OUT,exist_ok=True)
GOC=(3,1.3,3.0,1,10,1.0,1,0.0,1.0,1.5)
B.init(); s0=dict(B.SC[0]); meta=s0['meta']; i0,i1,bpd,iO=int(meta[0]),int(meta[1]),int(meta[2]),int(meta[4])
m=pd.read_csv('/workspace/sp500_sys/US500Cash_M1.csv',parse_dates=['time']).drop_duplicates('time').reset_index(drop=True)
assert len(m)==len(s0['o']) and np.abs(m.open.values-s0['o']).max()<1e-9
ny=(m.time-pd.Timedelta(hours=7))                                  # gio NY (naive)
ny_ms=(ny.dt.tz_localize('America/New_York',ambiguous='NaT',nonexistent='NaT').dt.tz_convert('UTC').dt.tz_localize(None).values.astype('datetime64[ms]').astype('int64'))
P=[]
for f in sorted(glob.glob(os.path.join(D,'phut_*.csv'))):
    x=pd.read_csv(f); ten=os.path.basename(f)[5:13]
    x['t']=pd.to_datetime(x.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
    x['p']=x.t.dt.hour*60+x.t.dt.minute; r=x[(x.p>=570)&(x.p<960)].reset_index(drop=True)
    if len(r)<300: continue
    r['ngay']=ten; P.append(r)
NG=[r.ngay[0] for r in P]; print('phien ES',len(NG),NG[0],NG[-1])
def dac_trung(r,nguong):
    d=(r.vol_mua-r.vol_ban).values; cvd=np.cumsum(d); c=r.c.values; h=r.h.values; l=r.l.values; o=r.o.values; v=r.vol.values
    bd=(r.lon_mua-r.lon_ban).values; big15=pd.Series(bd).rolling(15,min_periods=15).sum().values
    d15=pd.Series(d).rolling(15,min_periods=15).sum().values
    rng=pd.Series(h-l).rolling(30,min_periods=10).median().values; vmed=pd.Series(v).rolling(30,min_periods=10).median().values
    n=len(r); F={k:np.zeros(n) for k in ['hap','cvd','big','d15']}
    for i in range(30,n):
        hh=h[i-30:i].max(); ll=l[i-30:i].min()
        if c[i]>=hh and cvd[i]<cvd[i-30:i].max(): F['cvd'][i]=-1
        if c[i]<=ll and cvd[i]>cvd[i-30:i].min(): F['cvd'][i]=1
        if v[i]>2*vmed[i] and abs(d[i])>0.2*v[i] and abs(c[i]-o[i])<=0.25*rng[i]: F['hap'][i]=-np.sign(d[i])
        if big15[i]==big15[i] and abs(big15[i])>nguong['big']: F['big'][i]=np.sign(big15[i])
        if d15[i]==d15[i] and abs(d15[i])>nguong['d15']: F['d15'][i]=np.sign(d15[i])
    return F
h1=P[:len(P)//2]   # nguong = phan vi 80% tren NUA DAU so phien
def q(fn): return float(np.nanquantile(np.abs(np.concatenate([fn(r) for r in h1])),0.8))
NGU=dict(big=q(lambda r:pd.Series((r.lon_mua-r.lon_ban).values).rolling(15).sum().values),
         d15=q(lambda r:pd.Series((r.vol_mua-r.vol_ban).values).rolling(15).sum().values))
print('nguong',NGU)
idx=pd.Series(np.arange(len(m)),index=ny_ms); idx=idx[~idx.index.duplicated()]
II=idx.index.values; IV=idx.values
def chieu_len_m1(FE,H):
    out={k:np.zeros(len(m)) for k in ['hap','cvd','big','d15']}
    for (r,F) in FE:
        t_ms=r.phut_ms.values+120000
        for k in out:
            for i in np.nonzero(F[k])[0]:
                st=t_ms[i]; j=np.searchsorted(II,st)
                if j>=len(II): continue
                e=np.searchsorted(II,st+H*60000)
                if e<=j: continue
                out[k][IV[j]:IV[e-1]+1]=F[k][i]
    return out
FE=[(r,dac_trung(r,NGU)) for r in P]
def vung(ten):
    f=os.path.join(D,f'hoso_{ten}.csv')
    if not os.path.exists(f): return None
    hs=pd.read_csv(f).sort_values('gia'); v=(hs.vol_mua+hs.vol_ban).values; g=hs.gia.values
    if len(v)==0: return None
    i=int(np.argmax(v)); tot=v.sum(); lo=hi=i; acc=v[i]
    while acc<0.7*tot:
        a=v[lo-1] if lo>0 else -1; b=v[hi+1] if hi<len(v)-1 else -1
        if b>=a: hi+=1; acc+=v[hi]
        else: lo-=1; acc+=v[lo]
    return np.array([g[i],g[hi],g[lo]])
cs=pd.Series(s0['c'],index=ny_ms); cs=cs[~cs.index.duplicated()]
VZ={}; BS={}
for r in P:
    lv=vung(r.ngay[0])
    if lv is None: continue
    tail=r[r.p>=930]; us=cs.reindex(tail.phut_ms.values+60000).values
    dd=us-tail.c.values; bs=np.nanmedian(dd) if np.isfinite(dd).any() else np.nan
    if bs==bs: VZ[r.ngay[0]]=(lv+bs, pd.Timestamp(r.ngay[0]+' 16:00').tz_localize('America/New_York').value//10**6); BS[r.ngay[0]]=float(bs)
didx=s0['didx']; vp=s0['vp']; nd=vp.shape[0]
dstart=np.array([int(ny_ms[np.argmax(didx==d)]) if (didx==d).any() else -1 for d in range(nd)])
def vp_moi(cot):
    extra=np.full((nd,len(cot)),np.nan); keys=sorted(VZ,key=lambda k:VZ[k][1])
    for d in range(nd):
        tr=[k for k in keys if VZ[k][1]<=dstart[d]]
        if tr and dstart[d]-VZ[tr[-1]][1]<4*86400000: extra[d]=VZ[tr[-1]][0][cot]
    return np.hstack([vp,extra])
def i_cua(ten,hm='09:30'): return int(np.searchsorted(ny_ms,pd.Timestamp(f'{ten[:4]}-{ten[4:6]}-{ten[6:]} {hm}').tz_localize('America/New_York').value//10**6))
w0=i_cua(NG[0]); wm=i_cua(NG[len(NG)//2]); w1=i1-1
def chay(s,g=GOC,spr=0.65): return B.runone(s,B.mkP(g,bpd,spr))
def tom(s,g=GOC):
    r,eq=chay(s,g); r2,_=chay(s,g,1.3); k=iO-i0
    e=lambda i: float(eq[min(max(i-i0,0),len(eq)-1)])
    return dict(net=round(r['net'],2),maxdd=round(r['maxdd'],2),maxfl=round(r['maxfl'],2),IS=round(float(eq[k-1]-1e4),2),OOS=round(float(eq[-1]-eq[k-1]),2),
                cs_OF=round(e(w1)-e(w0),2),nua1=round(e(wm)-e(w0),2),nua2=round(e(w1)-e(wm),2),net2x=round(r2['net'],2),maxdd2x=round(r2['maxdd'],2),
                nb=int(r['nb']),blown=int(r['blown']>=0 or r['blown100']>=0)), eq
if __name__=='__main__':
    goc,eqg=tom(s0); print('GOC',goc)
    KQ=[dict(bien='GOC',**goc)]; EQ={'GOC':eqg}
    SIG={H:chieu_len_m1(FE,H) for H in (15,30)}
    for H in (15,30):
        sg=SIG[H]; sg['tong']=np.clip(sg['hap']+sg['cvd']+sg['big']+sg['d15'],-1,1)
        for k in ['hap','cvd','big','d15','tong']:
            for mode in ['cong','tru','ca2']:
                x=sg[k]; dS=np.maximum(x,0) if mode=='cong' else (np.minimum(x,0) if mode=='tru' else x)
                s=dict(s0); s['S']=s0['S']+dS; t,eq=tom(s); ten=f'S_{k}_{mode}_H{H}'
                KQ.append(dict(bien=ten,phut_khac0=int((dS!=0).sum()),**t)); EQ[ten]=eq; print(ten,t,flush=True)
    for cot,ten in [([0],'Z_poc'),([0,1,2],'Z_poc_vah_val')]:
        s=dict(s0); s['vp']=vp_moi(cot); t,eq=tom(s); KQ.append(dict(bien=ten,**t)); EQ[ten]=eq; print(ten,t)
    pd.DataFrame(KQ).to_csv(os.path.join(OUT,'bien_the.csv'),index=False)
    np.savez_compressed('/workspace/sp500_2711/hyb_of_eq.npz',**EQ)
    json.dump(dict(phien=NG,nguong=NGU,w0=w0,wm=wm,w1=w1,iO=iO,ngay_vung=len(VZ),co_so=BS),open(os.path.join(OUT,'meta.json'),'w'),indent=1)
