# Kiem 7 buoc: luat uu tien du lieu (big30 > delta15 > muc) lam DIEM VAO va CONG DCA trong HYB+AG, US500 (ES) va XAU (GC).
# Dong co: ban va cua sim_ag (US500) / vang/ma/may_hyb (XAU) - chi them mang SD rieng cho dieu kien DCA (thay S[i]>=sd bang SD[i]>=sd).
# Khong dat lenh that. Chay: python3 uu_tien_hyb.py ES|GC [so_lan_doi_chung]
import sys, os, re, json, importlib.util, numpy as np, pandas as pd
from scipy.stats import norm
REPO='/workspace/brain2'; sys.path.insert(0,REPO)
from phong_cach_tay import tin_hieu_data as T
SYM=sys.argv[1]; NDC=int(sys.argv[2]) if len(sys.argv)>2 else 100
OUT=f'{REPO}/sp500/ket_qua/uu_tien_hyb'; os.makedirs(OUT,exist_ok=True); rng=np.random.default_rng(5)
ENG='/workspace/sp500_2711/eng'; os.makedirs(ENG,exist_ok=True)
def va_dong_co(src,ten,extra_path):
    s=open(src).read()
    s=s.replace(",vp,opt,S,flip,",",vp,opt,S,SD,flip,"); assert s.count("elif S[i]>=sd:")==1; s=s.replace("elif S[i]>=sd:","elif SD[i]>=sd:")
    s=re.sub(r"_sys\.path\.insert\(0, str\(_P\(__file__\).*\n",f"_sys.path.insert(0,'{extra_path}')\n",s)
    p=f'{ENG}/{ten}.py'; open(p,'w').write(s)
    spec=importlib.util.spec_from_file_location(ten,p); m=importlib.util.module_from_spec(spec); sys.modules[ten]=m; spec.loader.exec_module(m); return m
# ---------------- du lieu theo ma ----------------
if SYM=='ES':
    sys.path.insert(0,'/workspace/sp500_sys/big/sweep_big'); import sweep_big as B
    E=va_dong_co(f'{REPO}/vang/nguon_hyb/sim_ag.py','cong_es','/workspace/sp500_sys'); B.init()
    s0=dict(B.SC[0]); meta=s0['meta']; i0,i1,bpd,iO=int(meta[0]),int(meta[1]),int(meta[2]),int(meta[4])
    m=pd.read_csv('/workspace/sp500_sys/US500Cash_M1.csv',parse_dates=['time']).drop_duplicates('time').reset_index(drop=True)
    assert len(m)==len(s0['o']); ms=T.ms_tu_gio_may_chu(m.time); tgian=m.time
    GOC=(3,1.3,3.0,1,10,1.0,1,0.0,1.0,1.5)
    def P_(g=GOC,spr=0.65,bpd_=bpd): return B.mkP(g,bpd_,spr)
    def chay(s,S,SD,P):
        mm=s['meta']; r,eq,*_=E.run(s['o'],s['h'],s['l'],s['c'],s['a5'],s['a15'],s['ah1'],s['m5'],s['c5p'],s['roll'],s['zzlo'],s['zzext'],s['didx'],s['vp'],s['opt'],S,SD,s['fl'],s['d1c'],s['e200'],s['e50'],s['slp'],P,int(mm[0]),int(mm[1]))
        return dict(zip(B.RK,r)),eq
    BASE=s0; S0=s0['S']
    LANG=[]
    for i,k in enumerate(B.GK):
        vals=B.GRID[k]; j=vals.index(GOC[i])
        for jj in (j-1,j+1):
            if 0<=jj<len(vals): g=list(GOC); g[i]=vals[jj]; LANG.append((f'{k}={vals[jj]}',P_(tuple(g))))
    def stress(S_fn):
        out=[]
        for s in B.SC[1:]:
            mm=s['meta']; P=B.mkP(GOC,int(mm[2]),float(mm[3])); S=s['S']; r,_=chay(s,S,S,P)   # stress khong co du lieu -> trung tinh
            out.append(dict(kb=str(s['name']),net=round(r['net'],2),maxdd=round(r['maxdd'],2),maxfl=round(r['maxfl'],2),chet=int(r['blown']>=0 or r['blown100']>=0)))
        return out
    EQ0=10000.0
else:
    sys.path.insert(0,f'{REPO}/vang/nguon_hyb')
    import vang.ma.chay_hyb_vang as V
    E=va_dong_co(f'{REPO}/vang/ma/may_hyb.py','cong_gc',f'{REPO}/vang/nguon_hyb')
    raw=V.tai_xm_m1_vn(); d,vp=V.dung_dac_trung(raw); S0=V.diem_S(d,None); opt0=np.full((len(d),6),np.nan)
    tgian=pd.to_datetime(d['t']); ms=(tgian-pd.Timedelta(hours=7)).values.astype('datetime64[ms]').astype('int64')   # d.t = UTC+7
    i0=400; i1=len(d); iO=int(np.searchsorted(tgian.values,np.datetime64('2026-10-01')))
    def P_(spr=0.20,**kw): return V.P_mac_dinh(spr=spr,**kw)
    def chay_d(dd,vp_,S,SD,P,a=i0,b=None):
        b=b or len(dd)
        arr=[dd[k].to_numpy(dtype=np.float64) for k in ["o","h","l","c","a5","a15","ah1"]]
        res,eqc,*_=E.run(*arr,dd["m5end"].to_numpy(),dd["c5p"].to_numpy(dtype=np.float64),dd["roll"].to_numpy(),dd["zz_lo"].to_numpy(dtype=np.float64),
            dd["zz_ext"].to_numpy(dtype=np.int64),dd["didx"].to_numpy(dtype=np.int64),vp_,np.full((len(dd),6),np.nan),S,SD,np.zeros(len(dd)),
            dd["d1c"].to_numpy(dtype=np.float64),dd["e200"].to_numpy(dtype=np.float64),dd["e50"].to_numpy(dtype=np.float64),dd["slp"].to_numpy(dtype=np.float64),P,a,b)
        names=["net","real","hreal","sreal","maxdd","minml","minml100","ntick","nhtick","nstp","ndcablk","nddblk","nmlwarn","maxlots","maxhl","blown","nb","ne","maxfl","maxlay","blown100","nth","threal","nhalt"]
        return {k:float(res[i]) for i,k in enumerate(names)},eqc
    def chay(s,S,SD,P): return chay_d(d,vp,S,SD,P)
    BASE=None
    LANG=[(k,P_(**kw)) for k,kw in [('coef=1.15',dict(coef=1.15)),('coef=1.5',dict(coef=1.5)),('G=2',dict(G=2.0)),('G=4',dict(G=4.0)),
                                     ('th=1.0',dict(th=1.0)),('th=2.0',dict(th=2.0)),('K=2',dict(K=2)),('K=5',dict(K=5))]]
    EQ0=10000.0
# ---------------- tin hieu ----------------
F,M=T.tao(SYM,ms)
gb=M['big30_giu']; pr=M['uu_tien']
adj=np.where(pr>=2,1.0,np.where(pr<=-2,-1.0,0.0))
BIEN={'GOC':(S0,S0),
      'VAO_UU_TIEN':(S0+adj,S0+adj),
      'VAO_CHI_CONG':(S0+np.maximum(adj,0),S0+np.maximum(adj,0)),
      'CHAN_DCA_big_nguoc':(S0,np.where(gb<0,-99.0,S0)),
      'CA_HAI':(S0+adj,np.where(gb<0,-99.0,S0+adj))}
P0=P_()
t_utc=pd.to_datetime(ms,unit='ms')
co_dl=(M['big30_giu']!=0)|(M['delta15_giu']!=0)
k_dl=np.nonzero(co_dl)[0]; w0=int(k_dl.min()); w1=len(S0)-1
# chia doi cua so co du lieu theo so phien
PH=sorted(F.phien.unique()); mid_ms=F.phut_ms[F.phien==PH[len(PH)//2]].min(); wm=int(np.searchsorted(ms,mid_ms)) if SYM=='ES' else int(np.searchsorted(np.sort(ms),mid_ms))
def tom(S,SD,P=P0):
    r,eq=chay(BASE,S,SD,P); a=i0
    e=lambda i: float(eq[min(max(i-a,0),len(eq)-1)])
    pk=np.maximum.accumulate(eq)
    return dict(net=round(r['net'],2),maxdd=round(r['maxdd'],2),dd_pct=round(r['maxdd']/EQ0*100,2),maxfl=round(r['maxfl'],2),
                IS=round(e(iO-1)-EQ0,2),OOS=round(e(len(S0)-1)-e(iO-1),2),cs_du_lieu=round(e(w1)-e(w0),2),nua1=round(e(wm)-e(w0),2),nua2=round(e(w1)-e(wm),2),
                nb=int(r['nb']),chan_dca=int(r['ndcablk']),chet=int(r['blown']>=0 or r['blown100']>=0)),eq
def ngay(eq):
    t=tgian.values[i0:i0+len(eq)]; return pd.Series(eq,index=pd.to_datetime(t)).resample('1D').last().dropna().diff().dropna()
def sh(x): x=np.asarray(x); return float(x.mean()/x.std(ddof=1)) if len(x)>2 and x.std(ddof=1)>0 else 0.0
KQ=[]; EQ={}
for ten,(S,SD) in BIEN.items():
    t,eq=tom(S,SD); P2=P0.copy()
    if SYM=='ES': P2=P_(spr=1.3)
    else: P2=P_(spr=0.40)
    t2,_=tom(S,SD,P2); t.update(net2x=t2['net'],maxdd2x=t2['maxdd'])
    EQ[ten]=eq; KQ.append(dict(bien=ten,**t)); print(ten,t,flush=True)
goc=KQ[0]
# doi chung ngau nhien: cung so phut chan/cong, dat ngau nhien trong cac phut co du lieu (giu khoi lien tiep 15')
def ngau(ten):
    S,SD=BIEN[ten]; dS=S-S0; dD=(SD<-50)&(S0>-50)
    pool=k_dl; res=[]
    for _ in range(NDC):
        S_=S0.copy(); SD_=S0.copy()
        for arr,src in ((S_,dS),(None,dD)):
            pass
        nblk=max(1,int((dS!=0).sum()/15)); st=rng.choice(pool,nblk,replace=False); sg=rng.choice([-1,1],nblk)
        if (dS!=0).any():
            for a,s_ in zip(st,sg):
                if ten=='VAO_CHI_CONG': s_=1
                S_[a:a+15]=S0[a:a+15]+s_
        SDr=S_.copy()
        if dD.any():
            nb2=max(1,int(dD.sum()/15)); st2=rng.choice(pool,nb2,replace=False)
            for a in st2: SDr[a:a+15]=-99.0
        t,_=tom(S_,SDr); res.append(t['cs_du_lieu'])
    return np.array(res)
for row in KQ[1:]:
    ten=row['bien']; dc=ngau(ten); d_=row['cs_du_lieu']-goc['cs_du_lieu']
    row.update(delta_du_lieu=round(d_,2),dc_tb=round(float(dc.mean()-goc['cs_du_lieu']),2),p_ngau_nhien=round(float((dc>=row['cs_du_lieu']).mean()),3))
    # lang gieng
    nb=[]
    for lt,PL in LANG:
        a,_=tom(*BIEN['GOC'],PL); b,_=tom(*BIEN[ten],PL); nb.append(dict(ten=lt,goc=a['net'],bien=b['net'],d=round(b['net']-a['net'],2),goc_dd=a['maxdd'],bien_dd=b['maxdd']))
    nb=pd.DataFrame(nb); nb.to_csv(f'{OUT}/lang_gieng_{SYM}_{ten}.csv',index=False)
    row.update(lg_duong=f"{int((nb.d>0).sum())}/{len(nb)}",lg_d_tv=round(float(nb.d.median()),2))
    # DSR (Sharpe ngay)
    srs=[sh(ngay(EQ[k])) for k in EQ]; x=ngay(EQ[ten]).values; sr=sh(x); g3=pd.Series(x).skew(); g4=pd.Series(x).kurt()+3; N=len(EQ)+len(LANG)
    sr0=np.sqrt(np.var(srs)+1e-12)*((1-0.5772)*norm.ppf(1-1/N)+0.5772*norm.ppf(1-1/(N*np.e)))
    row.update(sr_ngay=round(sr,4),sr_goc=round(sh(ngay(EQ['GOC']).values),4),dsr=round(float(norm.cdf((sr-sr0)*np.sqrt(len(x)-1)/np.sqrt(max(1-g3*sr+(g4-1)/4*sr**2,1e-9)))),3))
    print(ten,{k:row[k] for k in ['delta_du_lieu','dc_tb','p_ngau_nhien','lg_duong','dsr']},flush=True)
pd.DataFrame(KQ).to_csv(f'{OUT}/bien_the_{SYM}.csv',index=False)
# stress
ST=[]
if SYM=='ES':
    for r in stress(None): ST.append(dict(bien='tat_ca (khong co du lieu => trung tinh)',**r))
else:
    i_deep=i0+int(np.argmin(EQ['GOC'])); t_=tgian.values
    def gap(g,i):
        def f(dx):
            for k in ["o","h","l","c","c5p","zz_lo"]: dx.loc[i:,k]=dx.loc[i:,k]*(1-g)
        return f
    def grind(tot,days,start="2026-06-01"):
        def f(dx):
            i_s=int(np.searchsorted(t_,np.datetime64(start))); n=len(dx); k=np.zeros(n); k[i_s:]=np.minimum(np.arange(n-i_s)/(days*1380),1.0)
            fac=np.exp(np.log(1-tot)*k)
            for kk in ["o","h","l","c","c5p","zz_lo","a5","a15","ah1"]: dx[kk]=dx[kk]*fac
        return f
    for sn,fn in [("gap-10% tai day von",gap(0.10,i_deep)),("gap-20% tai day von",gap(0.20,i_deep)),("grind-20%/60ngay",grind(0.20,60)),("grind-35%/120ngay",grind(0.35,120))]:
        d2=d.copy(); fn(d2)
        for ten,(S,SD) in BIEN.items():
            r,_=chay_d(d2,vp,S,SD,P0); ST.append(dict(bien=ten,kb=sn,net=round(r['net'],2),maxdd=round(r['maxdd'],2),maxfl=round(r['maxfl'],2),chet=int(r['blown']>=0 or r['blown100']>=0 or r['maxdd']>=0.8*EQ0)))
    m5=pd.read_parquet(V.M5_PQ).reset_index()
    if "time" not in m5.columns: m5=m5.rename(columns={m5.columns[0]:"time"})
    m5["time"]=pd.to_datetime(m5["time"]); m15=m5.set_index("time").resample("15min").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna(); m15["tick_volume"]=1.0; m15=m15.reset_index()
    for wn,(a,b) in V.WIN.items():
        w=m15[(m15.time>=a)&(m15.time<b)].copy(); f=4000.0/float(w.close.iloc[0])
        for k in ["open","high","low","close"]: w[k]=w[k]*f
        dw,vpw=V.dung_dac_trung(w); Sw=V.diem_S(dw,None); P=P0.copy(); P[14]=64; P[44]=64; P[49]=5*92; P[52]=92
        r,_=chay_d(dw,vpw,Sw,Sw,P,50,len(dw))
        ST.append(dict(bien='tat_ca (khong co du lieu => trung tinh)',kb=wn,net=round(r['net'],2),maxdd=round(r['maxdd'],2),maxfl=round(r['maxfl'],2),chet=int(r['blown']>=0 or r['blown100']>=0 or r['maxdd']>=0.8*EQ0)))
st=pd.DataFrame(ST); st.to_csv(f'{OUT}/stress_{SYM}.csv',index=False); print(st.to_string())
json.dump(dict(ma=SYM,w0=str(tgian.iloc[w0]),wm=str(tgian.iloc[min(wm,len(tgian)-1)]),phut_co_du_lieu=int(co_dl.sum()),oos_tu='2026-10-01',ndc=NDC),open(f'{OUT}/meta_{SYM}.json','w'),indent=1)
print('HET',SYM)
