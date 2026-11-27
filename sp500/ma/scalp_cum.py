# Tin hieu DAT o Phan 1 dung lam lenh/cum giu NGAN (1-60 phut) tren gia CFD XM. Khong dat lenh that.
# Cum kieu Anh: 3 lenh cung chieu vao o gia mo 3 nen M1 lien tiep sau tin hieu; moi lenh chot TP rieng, het 5' dong o gia mo. Khong SL.
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0,'/workspace/brain2'); from phong_cach_tay import tin_hieu_data as T
SYM=sys.argv[1]; OUT='/workspace/brain2/sp500/ket_qua/scalp_cum'; os.makedirs(OUT,exist_ok=True); rng=np.random.default_rng(3)
CF={'ES':'/workspace/sp500_sys/US500Cash_M1.csv','GC':'/workspace/sp500_sys/GOLD_i_M1.csv'}[SYM]
TRUOT={'ES':0.2,'GC':0.05}[SYM]; MUL={'ES':1.0,'GC':100.0}[SYM]; TP_TAY={'ES':6.53,'GC':4.00}[SYM]
c=pd.read_csv(CF,parse_dates=['time']).drop_duplicates('time'); ms=T.ms_tu_gio_may_chu(c.time); ok=ms>0; c=c[ok].reset_index(drop=True); ms=ms[ok]
o=np.argsort(ms); ms=ms[o]; c=c.iloc[o].reset_index(drop=True)
O=c.open.values; Hh=c.high.values; Ll=c.low.values; PHI=float(np.median(c.spread.values)*0.01+2*TRUOT)
ATR=pd.Series(Hh-Ll).rolling(60,min_periods=20).mean().values
F,_=T.tao(SYM,None); F=F[F.phut_ms<=ms.max()].reset_index(drop=True)
PH=sorted(F.phien.unique()); nua=np.where(F.phien.isin(set(PH[:len(PH)//2])),1,2)
ny=pd.to_datetime(F.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York'); BUCK=((ny.dt.hour*60+ny.dt.minute)//30).values
def idx_vao(pm):  # chi so nen CFD mo dung luc pm+60s
    j=np.searchsorted(ms,pm+60000); okk=(j<len(ms))&(ms[np.minimum(j,len(ms)-1)]==pm+60000); return np.where(okk,j,-1)
J=idx_vao(F.phut_ms.values)
gb=F.big30_giu.values; gd=F.delta15_giu.values
pr=F.uu_tien.values; prc=np.where((np.abs(pr)>=2)&(np.r_[0,np.abs(pr[:-1])]<2),np.sign(pr),0)
SIGS={'ES':{'vah_val_pha':F.vah_val_pha.values,'cvd_pk+delta15':np.where((F.cvd_pk.values!=0)&(gd==F.cvd_pk.values),F.cvd_pk.values,0),
            'sig_ES (gop 2 luat dat)':F.sig_ES.values,'uu_tien>=2 (moi vuot)':prc,'big30 thang muc_fade':np.where((F.big30.values!=0)&(F.muc_fade.values==-F.big30.values),F.big30.values,0)},
      'GC':{'big30':F.big30.values,'big30+delta15':np.where((F.big30.values!=0)&(gd==F.big30.values),F.big30.values,0),
            'delta15+muc_fade':np.where((F.muc_fade.values!=0)&(gd==F.muc_fade.values),F.muc_fade.values,0),
            'sig_GC (gop 3 luat dat)':F.sig_GC.values,'uu_tien>=2 (moi vuot)':prc,'big30 thang muc_fade':np.where((F.big30.values!=0)&(F.muc_fade.values==-F.big30.values),F.big30.values,0)}}[SYM]
def chon(x,cool=15):
    out=[];last=-1e18;lp=None
    for i in np.nonzero(x)[0]:
        if F.phien.values[i]!=lp: last=-1e18; lp=F.phien.values[i]
        if F.phut_ms.values[i]-last>=cool*60000 and J[i]>=0: out.append(i); last=F.phut_ms.values[i]
    return np.array(out,int)
def mot_lenh(j,dr,H):   # vao o O[j], ra o O[j+H]
    if j+H>=len(O) or ms[j+H]-ms[j]>(H+30)*60000: return np.nan
    return (O[j+H]-O[j])*dr-PHI
def cum(j,dr,tp,T_=5,k=3):
    r=[]
    for q in range(k):
        a=j+q
        if a+T_>=len(O) or ms[a+T_]-ms[a]>(T_+30)*60000: return np.nan
        e=O[a]; done=False
        for b in range(a,a+T_):
            if (dr>0 and Hh[b]>=e+tp) or (dr<0 and Ll[b]<=e-tp): r.append(tp-PHI); done=True; break
        if not done: r.append((O[a+T_]-e)*dr-PHI)
    return float(np.sum(r))
def tk(r):
    r=np.asarray(r,float); r=r[np.isfinite(r)]
    if len(r)<3: return dict(n=len(r))
    w=r[r>0].sum(); l=-r[r<0].sum()
    return dict(n=len(r),tb=round(r.mean(),3),thang=round((r>0).mean()*100,1),pf=round(w/l,2) if l>0 else 99.0,t=round(r.mean()/r.std(ddof=1)*np.sqrt(len(r)),2) if r.std(ddof=1)>0 else 0,usd_1lot=round(r.sum()*MUL,1))
POOL={b:np.nonzero((BUCK==b)&(J>=0))[0] for b in np.unique(BUCK)}
KQ=[]
for ten,x in SIGS.items():
    ii=chon(x); dr=x[ii]
    row=dict(ma=SYM,tin_hieu=ten,n=len(ii))
    for H in (1,2,3,5,10,15,30,60):
        row[f'tb_{H}p']=tk([mot_lenh(J[i],d_,H) for i,d_ in zip(ii,dr)]).get('tb',np.nan)
    for lab,tpf in (('cum3_tp0.5atr',None),('cum3_tp1atr',None),('cum3_tp_tay',TP_TAY)):
        rr=[cum(J[i],d_,tpf if tpf else (0.5 if '0.5' in lab else 1.0)*ATR[J[i]]) for i,d_ in zip(ii,dr)]
        s=tk(rr); row.update({f'{lab}_{k}':v for k,v in s.items() if k!='n'})
        rr=np.array(rr); 
        for h in (1,2): s2=tk(rr[nua[ii]==h]); row[f'{lab}_nua{h}']=s2.get('tb',np.nan)
        # doi chung: cung chieu, gio ngau nhien cung khung 30'
        base=np.nanmean(rr); res=[]
        for _ in range(100):
            jj=[POOL[BUCK[i]][rng.integers(len(POOL[BUCK[i]]))] for i in ii]
            res.append(np.nanmean([cum(J[a],d_,tpf if tpf else (0.5 if '0.5' in lab else 1.0)*ATR[J[a]]) for a,d_ in zip(jj,dr)]))
        row[f'{lab}_p']=round(float(np.mean(np.array(res)>=base)),3)
    KQ.append(row); print(row,flush=True)
pd.DataFrame(KQ).to_csv(f'{OUT}/scalp_{SYM}.csv',index=False)
json.dump(dict(ma=SYM,phi=PHI,tp_tay=TP_TAY,atr60_trung_vi=float(np.nanmedian(ATR))),open(f'{OUT}/meta_{SYM}.json','w'))
