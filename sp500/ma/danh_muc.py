# Vong 3 (27/11 toi): tin hieu du lieu lam BO LOC NGU CANH, khong lam diem vao.
#  (a) he so lot theo chieu du lieu (cung chieu x mA, nguoc chieu x mO) cho HYB+AG US500 va tay_v2 US500 (loc p1_union_es)
#  (b) lenh phu giu 30-60' tren cac tin hieu DAT (pha VAH/VAL, CVD phan ky + delta15; vang big30 thang muc fade, big30+delta15)
#  (c) danh muc chung von: HYB+AG US500 + HYB+AG XAU + tay_v2 US500 + tay_v2 XAU (+ lenh phu), tuong quan va DD gop
# Don vi: USD; USC = USD x 100 (tai khoan cent). Khong dat lenh that.
import sys, os, re, json, importlib.util, numpy as np, pandas as pd
from scipy.stats import norm
REPO='/workspace/brain2'; sys.path.insert(0,REPO)
from phong_cach_tay import tin_hieu_data as T
OUT=f'{REPO}/sp500/ket_qua/danh_muc'; os.makedirs(OUT,exist_ok=True); ENG='/workspace/sp500_2711/eng'; os.makedirs(ENG,exist_ok=True)
rng=np.random.default_rng(9); EQ0=10000.0; LOG=[]
def ghi(*a):
    s=' '.join(str(x) for x in a); print(s,flush=True); LOG.append(s)
def nap(src,ten,thay,extra=None,rev='HEAD'):
    # doc ban da commit (HEAD) de khong vuong ban dang sua cua worker khac
    import subprocess; s=subprocess.run(['git','-C',REPO,'show',rev+':'+os.path.relpath(src,REPO)],capture_output=True,text=True,check=True).stdout
    for a,b in thay:
        assert s.count(a)>=1,(ten,a); s=s.replace(a,b)
    if extra: s=re.sub(r"_sys\.path\.insert\(0, str\(_P\(__file__\).*\n",f"_sys.path.insert(0,'{extra}')\n",s)
    p=f'{ENG}/{ten}.py'; open(p,'w').write(s)
    sp=importlib.util.spec_from_file_location(ten,p); m=importlib.util.module_from_spec(sp); sys.modules[ten]=m; sp.loader.exec_module(m); return m
# ---- dong co HYB+AG co mang he so lot LM (chi nhan lot vao/DCA) ----
THAY_HYB=[(",vp,opt,S,flip,",",vp,opt,S,LM,flip,"),("mul=mhi if S[i]>=shi else 1.0","mul=(mhi if S[i]>=shi else 1.0)*LM[i]"),
          ("mul=mhi if (S[i]>=shi or zc[znext]>=chi) else 1.0","mul=(mhi if (S[i]>=shi or zc[znext]>=chi) else 1.0)*LM[i]")]
EH=nap(f'{REPO}/vang/nguon_hyb/sim_ag.py','dm_hyb_es',THAY_HYB)
EG=nap(f'{REPO}/vang/ma/may_hyb.py','dm_hyb_gc',THAY_HYB,f'{REPO}/vang/nguon_hyb')
# ---- dong co tay_v2 co mang ngu canh C va he so (mA, mO) = P[22], P[23] ----
THAY_TAY=[("def run(o, h, l, c, roll, sig, P, i0, i1):","def run(o, h, l, c, roll, sig, C, P, i0, i1):"),
          ("nt = _add(px, lots, side, hg, nt, fill, L0, s, 0.0)","nt = _add(px, lots, side, hg, nt, fill, L0 * (P[22] if C[i] == s else (P[23] if C[i] == -s else 1.0)), s, 0.0)"),
          ("nt = _add(px, lots, side, hg, nt, fill, L0, main_s, 0.0)","nt = _add(px, lots, side, hg, nt, fill, L0 * (P[22] if C[i] == main_s else (P[23] if C[i] == -main_s else 1.0)), main_s, 0.0)")]
ET=nap(f'{REPO}/phong_cach_tay/ma/may_v2.py','dm_tay',THAY_TAY,rev='5f393920')  # ban may_v2 da dung cho p1_union_es (truoc 59672872)
def Ptay(P,mA=1.0,mO=1.0): return np.r_[P[:22],[mA,mO]].astype(np.float64)   # P_v2 moi (59672872) dai 29 -> cat ve 22 cua engine 5f393920
# ================= du lieu =================
sys.path.insert(0,'/workspace/sp500_sys/big/sweep_big'); import sweep_big as B; B.init()
s0=dict(B.SC[0]); mt=s0['meta']; i0E,i1E,bpdE,iOE=int(mt[0]),int(mt[1]),int(mt[2]),int(mt[4])
mE=pd.read_csv('/workspace/sp500_sys/US500Cash_M1.csv',parse_dates=['time']).drop_duplicates('time').reset_index(drop=True)
msE=T.ms_tu_gio_may_chu(mE.time)
GOC=(3,1.3,3.0,1,10,1.0,1,0.0,1.0,1.5)
def hyb_es(LM,spr=0.65,g=GOC,s=None):
    s=s or s0; mm=s['meta']; P=B.mkP(g,int(mm[2]),spr if s is s0 else float(mm[3]))
    r,eq,*_=EH.run(s['o'],s['h'],s['l'],s['c'],s['a5'],s['a15'],s['ah1'],s['m5'],s['c5p'],s['roll'],s['zzlo'],s['zzext'],s['didx'],s['vp'],s['opt'],s['S'],LM,s['fl'],s['d1c'],s['e200'],s['e50'],s['slp'],P,int(mm[0]),int(mm[1]))
    return dict(zip(B.RK,r)),eq
import vang.ma.chay_hyb_vang as V
rawG=V.tai_xm_m1_vn(); dG,vpG=V.dung_dac_trung(rawG); SG=V.diem_S(dG,None)
tG=pd.to_datetime(dG['t']); msG=(tG-pd.Timedelta(hours=7)).values.astype('datetime64[ms]').astype('int64')
def hyb_gc(LM,spr=0.20):
    dd=dG; arr=[dd[k].to_numpy(dtype=np.float64) for k in ["o","h","l","c","a5","a15","ah1"]]
    res,eq,*_=EG.run(*arr,dd["m5end"].to_numpy(),dd["c5p"].to_numpy(dtype=np.float64),dd["roll"].to_numpy(),dd["zz_lo"].to_numpy(dtype=np.float64),dd["zz_ext"].to_numpy(dtype=np.int64),
        dd["didx"].to_numpy(dtype=np.int64),vpG,np.full((len(dd),6),np.nan),SG,LM,np.zeros(len(dd)),dd["d1c"].to_numpy(dtype=np.float64),dd["e200"].to_numpy(dtype=np.float64),
        dd["e50"].to_numpy(dtype=np.float64),dd["slp"].to_numpy(dtype=np.float64),V.P_mac_dinh(spr=spr),400,len(dd))
    return {k:float(res[i]) for i,k in enumerate(["net","real","hreal","sreal","maxdd","minml","minml100","ntick","nhtick","nstp","ndcablk","nddblk","nmlwarn","maxlots","maxhl","blown","nb","ne","maxfl","maxlay","blown100","nth","threal","nhalt"])},eq
# tay_v2 (dung ham cua worker Phan 2, chi doc)
from phong_cach_tay.ma.may import SPEC
from phong_cach_tay.ma.may_v2 import P_v2
from phong_cach_tay.ma.chay_v2 import tai_m1_vn, dung_dac_trung, them_rej_dn, diem_S, diem_S_short, lap_tin
from phong_cach_tay.ma.chay_v2_p1 import ms_m1_tu_t_vn, chieu
from phong_cach_tay.ma.chay_vang_an_toan import loc_delta15
def nap_tay(sym):
    raw=tai_m1_vn(SPEC[sym]["m1"]); d,_=dung_dac_trung(raw); rej=them_rej_dn(d,raw)
    sig0=lap_tin(d,diem_S(d,None),diem_S_short(d,rej),None,"chi_bao","lu"); ms=ms_m1_tu_t_vn(d["t"]); return d,sig0,ms
dTE,sig0TE,msTE=nap_tay("US500"); dTG,sig0TG,msTG=nap_tay("XAU")
FE,_=T.tao("ES",None); FG,_=T.tao("GC",None)
FE=FE.copy(); FE["cvd_d15"]=np.where((FE.cvd_pk.values!=0)&(FE.delta15_giu.values==FE.cvd_pk.values),FE.cvd_pk.values,0.0)
FE["dat_es"]=np.where(FE.vah_val_pha.values!=0,FE.vah_val_pha.values,FE.cvd_d15.values)       # = p1_union_es (theo phut)
FG=FG.copy(); FG["big_thang_muc"]=np.where((FG.big30.values!=0)&(FG.muc_fade.values==-FG.big30.values),FG.big30.values,0.0)
FG["big_d15"]=np.where((FG.big30.values!=0)&(FG.delta15_giu.values==FG.big30.values),FG.big30.values,0.0)
FG["dat_gc"]=np.where(FG.big_thang_muc.values!=0,FG.big_thang_muc.values,FG.big_d15.values)
Me=chieu(FE,msTE,["vah_val_pha","cvd_d15"],tre_ms=60_000,giu_phut=15)
sig_union_es=np.where(Me["vah_val_pha"]!=0,Me["vah_val_pha"],Me["cvd_d15"])        # tay_v2 US500 mac dinh (dung nhu chay_v2_p1)
d15G=chieu(FG,msTG,["delta15_giu"],tre_ms=60_000,giu_phut=15)["delta15_giu"]; sig_d15G=loc_delta15(sig0TG,d15G)
P_TE=P_v2("US500"); P_TG=P_v2("XAU",L0=0.01,K=4,maxL=20,flcap=0.15,hfrac=1.0,dca_max_bars=0,hlot=0.01)
def tay(sym,C,mA=1.0,mO=1.0,spr2=False):
    d,sig,P=(dTE,sig_union_es,P_TE) if sym=="US500" else (dTG,sig_d15G,P_TG)
    P=Ptay(P,mA,mO)
    if spr2: P[10]=P[10]*2
    o,h,l,c=[d[k].to_numpy(np.float64) for k in "ohlc"]
    res,eq,*_=ET.run(o,h,l,c,d.roll.to_numpy(),sig,np.asarray(C,np.float64),P,400,len(d))
    return dict(net=float(res[0]),maxdd=float(res[1]),maxfl=float(res[2]) if len(res)>2 else np.nan,blown=float(res[-1]) if False else None),eq
# ngu canh C (chieu du lieu giu H phut, tu tin hieu DAT moi nhat)
def ngu_canh(F,cot,ms,H): return T.len_m1(F,ms,[cot],tre_ms=120000,giu_phut=H)[cot]
def tom_eq(eq,ms_axis,i0,EQ=EQ0):
    eq=np.asarray(eq); t=ms_axis[i0:i0+len(eq)]; pk=np.maximum.accumulate(eq); dd=float(np.max(pk-eq))
    iO=np.searchsorted(t,pd.Timestamp('2026-10-01').value//10**6)
    return dict(net=round(float(eq[-1]-EQ),2),maxdd=round(dd,2),dd_pct=round(dd/EQ*100,2),IS=round(float(eq[max(iO-1,0)]-EQ),2),OOS=round(float(eq[-1]-eq[max(iO-1,0)]),2))
def cua_so(eq,ms_axis,i0,a_ms,b_ms):
    t=ms_axis[i0:i0+len(eq)]; ia=min(np.searchsorted(t,a_ms),len(eq)-1); ib=min(np.searchsorted(t,b_ms),len(eq)-1); return float(eq[ib]-eq[ia])
# cua so du lieu & 2 nua
def nua(F):
    PH=sorted(F.phien.unique()); a=F.phut_ms.min(); m=F.phut_ms[F.phien==PH[len(PH)//2]].min(); b=F.phut_ms.max(); return a,m,b
WE=nua(FE); WG=nua(FG)
# ================= (a) he so lot =================
A=[]; MULS=[(1.5,0.5),(1.25,0.75),(1.5,1.0),(1.0,0.5),(2.0,0.5)]
for H in (30,60):
    CE_hyb=ngu_canh(FE,"dat_es",msE,H); CE_tay=ngu_canh(FE,"dat_es",msTE,H)
    for mA,mO in [(1.0,1.0)]+MULS:
        LM=np.where(CE_hyb>0,mA,np.where(CE_hyb<0,mO,1.0))
        r,eq=hyb_es(LM); r2,_=hyb_es(LM,spr=1.3); row=dict(he='HYB+AG US500',H=H,mA=mA,mO=mO,**tom_eq(eq,msE,i0E),maxfl=round(r['maxfl'],2),net2x=round(r2['net'],2),
              cs_dl=round(cua_so(eq,msE,i0E,WE[0],WE[2]),2),nua1=round(cua_so(eq,msE,i0E,WE[0],WE[1]),2),nua2=round(cua_so(eq,msE,i0E,WE[1],WE[2]),2),chet=int(r['blown']>=0 or r['blown100']>=0))
        A.append(row); ghi('a',row)
        rt,eqt=tay("US500",CE_tay,mA,mO); rt2,_=tay("US500",CE_tay,mA,mO,True)
        row=dict(he='tay_v2 US500 (p1_union_es)',H=H,mA=mA,mO=mO,**tom_eq(eqt,msTE,400),maxfl=round(rt['maxfl'],2),net2x=round(rt2['net'],2),
                 cs_dl=round(cua_so(eqt,msTE,400,WE[0],WE[2]),2),nua1=round(cua_so(eqt,msTE,400,WE[0],WE[1]),2),nua2=round(cua_so(eqt,msTE,400,WE[1],WE[2]),2))
        A.append(row); ghi('a',row)
A=pd.DataFrame(A); A.to_csv(f'{OUT}/a_he_so_lot.csv',index=False)
# doi chung ngau nhien + lang gieng cho bien the (a) tot nhat moi he (theo cs_dl)
DC=[]
for he in A.he.unique():
    g=A[A.he==he]; goc=g[(g.mA==1)&(g.mO==1)].iloc[0]; best=g[~((g.mA==1)&(g.mO==1))].sort_values('cs_dl',ascending=False).iloc[0]
    H=int(best.H); ms_ax=msE if he.startswith('HYB') else msTE; C=ngu_canh(FE,"dat_es",ms_ax,H)
    # xao tron ngu canh: dich vong theo ngay (giu cau truc), 50 lan
    res=[]
    day=1440
    for k in range(50):
        sh=int(rng.integers(5,60))*day; Cr=np.roll(C,sh)
        if he.startswith('HYB'): r,eq=hyb_es(np.where(Cr>0,best.mA,np.where(Cr<0,best.mO,1.0))); res.append(cua_so(eq,msE,i0E,WE[0],WE[2]))
        else: r,eq=tay("US500",Cr,best.mA,best.mO); res.append(cua_so(eq,msTE,400,WE[0],WE[2]))
    res=np.array(res)
    lg=[]
    if he.startswith('HYB'):
        for i,k in enumerate(B.GK):
            vals=B.GRID[k]; j=vals.index(GOC[i])
            for jj in (j-1,j+1):
                if 0<=jj<len(vals):
                    gg=list(GOC); gg[i]=vals[jj]; a_,eqa=hyb_es(np.ones(len(C)),g=tuple(gg)); b_,eqb=hyb_es(np.where(C>0,best.mA,np.where(C<0,best.mO,1.0)),g=tuple(gg))
                    lg.append(cua_so(eqb,msE,i0E,WE[0],WE[2])-cua_so(eqa,msE,i0E,WE[0],WE[2]))
    else:
        for kw in [dict(K=4),dict(K=6),dict(tp=5.0),dict(tp=8.0),dict(gap=6.5),dict(gap=10.0)]:
            P0=P_v2("US500",**kw)
            def run_(mA,mO,P0=P0):
                o,h,l,c=[dTE[k].to_numpy(np.float64) for k in "ohlc"]; res_,eq_,*_=ET.run(o,h,l,c,dTE.roll.to_numpy(),sig_union_es,C,Ptay(P0,mA,mO),400,len(dTE)); return eq_
            lg.append(cua_so(run_(best.mA,best.mO),msTE,400,WE[0],WE[2])-cua_so(run_(1.0,1.0),msTE,400,WE[0],WE[2]))
    lg=np.array(lg)
    DC.append(dict(he=he,bien=f"H{H} x{best.mA}/{best.mO}",delta_cs_dl=round(best.cs_dl-goc.cs_dl,2),dc_tb=round(float(res.mean()-goc.cs_dl),2),
                   p_xao_tron=round(float((res>=best.cs_dl).mean()),3),lang_gieng_duong=f"{int((lg>0).sum())}/{len(lg)}",lg_trung_vi=round(float(np.median(lg)),2)))
    ghi('a-dc',DC[-1])
pd.DataFrame(DC).to_csv(f'{OUT}/a_doi_chung.csv',index=False)
# ================= (b) lenh phu giu 30-60' =================
def cfd(path):
    c=pd.read_csv(path,parse_dates=['time']).drop_duplicates('time'); ms=T.ms_tu_gio_may_chu(c.time); ok=ms>0; c=c[ok]; ms=ms[ok]; o=np.argsort(ms)
    return ms[o],c.open.values[o],c.high.values[o],c.low.values[o],c.close.values[o],float(np.median(c.spread.values)*0.01)
CF={'ES':cfd('/workspace/sp500_sys/US500Cash_M1.csv'),'GC':cfd('/workspace/sp500_sys/GOLD_i_M1.csv')}
LOT={'ES':(1.0,1.0),'GC':(0.05,100.0)}; TRU={'ES':0.2,'GC':0.05}
def phu(sym,F,cot,H=60,SLk=0.0,spr_mul=1.0,cool=15,dir_override=None,times=None):
    ms,O,Hh,Ll,Cc,spr=CF[sym]; lot,pv=LOT[sym]; phi=spr*spr_mul+2*TRU[sym]
    x=F[cot].values if dir_override is None else dir_override
    idx=np.nonzero(x)[0] if times is None else times
    atr=pd.Series(Hh-Ll).rolling(60,min_periods=20).mean().values
    pnl=np.zeros(len(ms)); tr=[]; busy=-1
    for i in idx:
        st=F.phut_ms.values[i]+60000; j=np.searchsorted(ms,st)
        if j>=len(ms) or ms[j]!=st or j<=busy: continue
        e=j+H
        if e>=len(ms) or ms[e]-ms[j]>(H+30)*60000: continue
        dr=x[i]; en=O[j]; sl=SLk*atr[j] if SLk>0 else np.inf; ex=O[e]; k_ex=e
        for b in range(j,e):
            adv=(en-Ll[b]) if dr>0 else (Hh[b]-en)
            if adv>=sl: ex=en-dr*sl; k_ex=b+1; break
        path=np.r_[(Cc[j:k_ex]-en)*dr,(ex-en)*dr]*lot*pv          # mark-to-market tung nen
        seg=np.diff(np.r_[0.0,path]); pnl[j:j+len(seg)]+=seg[:len(pnl)-j]
        pnl[min(k_ex,len(pnl)-1)]-=phi*lot*pv
        tr.append(((ex-en)*dr-phi)*lot*pv); busy=k_ex
    eq=EQ0+np.cumsum(pnl); return np.array(tr),eq
B_=[]; EQB={}
SIGB={'ES':['vah_val_pha','cvd_d15','dat_es'],'GC':['big_thang_muc','big_d15','dat_gc']}
for sym,F in (('ES',FE),('GC',FG)):
    W=WE if sym=='ES' else WG; ms=CF[sym][0]
    for cot in SIGB[sym]:
        for H in (30,45,60,90):
            for SLk in (0.0,10.0):
                tr,eq=phu(sym,F,cot,H,SLk); tr2,_=phu(sym,F,cot,H,SLk,spr_mul=2.0)
                if len(tr)<3: continue
                pk=np.maximum.accumulate(eq); dd=float(np.max(pk-eq))
                m1=F.phut_ms.values<W[1]
                trA,_=phu(sym,F[m1].reset_index(drop=True),cot,H,SLk); trB,_=phu(sym,F[~m1].reset_index(drop=True),cot,H,SLk)
                row=dict(ma=sym,tin_hieu=cot,H=H,SL_atr=SLk,n=len(tr),tong_usd=round(tr.sum(),2),tb_usd=round(tr.mean(),2),thang=round((tr>0).mean()*100,1),
                         maxdd_usd=round(dd,2),dd_pct=round(dd/EQ0*100,2),tong_2x=round(tr2.sum(),2),nua1=round(trA.sum(),2),nua2=round(trB.sum(),2),
                         sr=round(tr.mean()/tr.std(ddof=1),3) if tr.std(ddof=1)>0 else 0)
                B_.append(row); EQB[(sym,cot,H,SLk)]=eq
    ghi('b xong',sym)
B_=pd.DataFrame(B_)
# doi chung ngau nhien (cung chieu, gio ngau nhien cung khung 30') + DSR cho bien the tot nhat moi tin hieu
def pool(F):
    ny=pd.to_datetime(F.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York'); b=((ny.dt.hour*60+ny.dt.minute)//30).values
    return b,{k:np.nonzero(b==k)[0] for k in np.unique(b)}
srs=B_.sr.values; N=len(B_)
for k_,r in B_.iterrows():
    F=FE if r.ma=='ES' else FG; bk,PL=pool(F); x=F[r.tin_hieu].values; ii=np.nonzero(x)[0]
    if r.H!=60 or r.SL_atr!=0: continue
    res=[]
    for _ in range(100):
        jj=np.array([PL[bk[i]][rng.integers(len(PL[bk[i]]))] for i in ii]); dv=np.zeros(len(F)); dv[jj]=x[ii]
        tr,_=phu(r.ma,F,None,int(r.H),r.SL_atr,dir_override=dv,times=np.unique(jj)); res.append(tr.sum())
    B_.loc[k_,'p_ngau_nhien']=round(float((np.array(res)>=r.tong_usd).mean()),3)
    tr,_=phu(r.ma,F,r.tin_hieu,int(r.H),r.SL_atr); sr=tr.mean()/tr.std(ddof=1); g3=pd.Series(tr).skew(); g4=pd.Series(tr).kurt()+3
    sr0=np.sqrt(np.var(srs))*((1-0.5772)*norm.ppf(1-1/N)+0.5772*norm.ppf(1-1/(N*np.e)))
    B_.loc[k_,'dsr']=round(float(norm.cdf((sr-sr0)*np.sqrt(len(tr)-1)/np.sqrt(max(1-g3*sr+(g4-1)/4*sr**2,1e-9)))),3)
# gap xau nhat khi dang giu 1 lenh: lot x pv x gia x gap
B_['lo_gap10_usd']=np.where(B_.ma=='ES',1.0*1.0*6800*0.10,0.05*100*4000*0.10); B_['lo_gap20_usd']=B_.lo_gap10_usd*2
B_.to_csv(f'{OUT}/b_lenh_phu.csv',index=False); ghi(B_.to_string())
# ================= (c) danh muc chung von =================
def len_truc(eq,ms_axis,i0,T_):
    t=ms_axis[i0:i0+len(eq)]; s=pd.Series(np.asarray(eq)-EQ0,index=t); s=s[~s.index.duplicated()].sort_index(); return s.reindex(T_,method='ffill').fillna(0.0).values
r,eqHE=hyb_es(np.ones(len(msE))); r,eqHG=hyb_gc(np.ones(len(msG)))
rt,eqTE=tay("US500",np.zeros(len(msTE))); rt,eqTG=tay("XAU",np.zeros(len(msTG)))
r2,eqHE2=hyb_es(np.ones(len(msE)),spr=1.3); r2,eqHG2=hyb_gc(np.ones(len(msG)),spr=0.40)
rt2,eqTE2=tay("US500",np.zeros(len(msTE)),spr2=True); rt2,eqTG2=tay("XAU",np.zeros(len(msTG)),spr2=True)
bestB={s:B_[(B_.ma==s)&(B_.H==60)&(B_.SL_atr==0)].sort_values('tong_usd',ascending=False).iloc[0] for s in ('ES','GC')}
eqBE=EQB[('ES',bestB['ES'].tin_hieu,60,0.0)]; eqBG=EQB[('GC',bestB['GC'].tin_hieu,60,0.0)]
T_=np.unique(np.r_[msE[i0E:],msG[400:]]); T_=T_[(T_>=max(msE[i0E],msG[400]))&(T_<=min(msE[-1],msG[-1]))]
TP={'HYB_US500':len_truc(eqHE,msE,i0E,T_),'HYB_XAU':len_truc(eqHG,msG,400,T_),'tay_US500':len_truc(eqTE,msTE,400,T_),'tay_XAU':len_truc(eqTG,msTG,400,T_),
    'phu_US500':len_truc(eqBE,CF['ES'][0],0,T_),'phu_XAU':len_truc(eqBG,CF['GC'][0],0,T_)}
TP2={'HYB_US500':len_truc(eqHE2,msE,i0E,T_),'HYB_XAU':len_truc(eqHG2,msG,400,T_),'tay_US500':len_truc(eqTE2,msTE,400,T_),'tay_XAU':len_truc(eqTG2,msTG,400,T_)}
day=pd.to_datetime(T_,unit='ms').floor('D'); D=pd.DataFrame(TP,index=day).groupby(level=0).last().diff().dropna()
D.corr().round(3).to_csv(f'{OUT}/c_tuong_quan_ngay.csv'); ghi('tuong quan ngay\n',D.corr().round(3).to_string())
iO=np.searchsorted(T_,pd.Timestamp('2026-10-01').value//10**6)
C_=[]
for ten,ks in [('HYB_US500',['HYB_US500']),('HYB_XAU',['HYB_XAU']),('tay_US500',['tay_US500']),('tay_XAU',['tay_XAU']),
               ('HYB_US500+tay_US500',['HYB_US500','tay_US500']),('HYB_US500+tay_US500+tay_XAU',['HYB_US500','tay_US500','tay_XAU']),
               ('ca_4_he',['HYB_US500','HYB_XAU','tay_US500','tay_XAU']),('ca_4_he+lenh_phu',list(TP)),('HYB_US500+tay_US500+lenh_phu_US500',['HYB_US500','tay_US500','phu_US500'])]:
    s=sum(TP[k] for k in ks); eq=EQ0+s; pk=np.maximum.accumulate(eq); dd=float(np.max(pk-eq)); tong_dd=sum(float(np.max(np.maximum.accumulate(EQ0+TP[k])-(EQ0+TP[k]))) for k in ks)
    s2=sum(TP2.get(k,TP[k]) for k in ks)
    dn=pd.Series(s,index=day).groupby(level=0).last().diff().dropna()
    C_.append(dict(danh_muc=ten,net_usd=round(float(s[-1]),2),net_usc=round(float(s[-1])*100),maxdd_usd=round(dd,2),dd_pct=round(dd/EQ0*100,2),tong_dd_rieng=round(tong_dd,2),
                   von_thap_nhat=round(float(eq.min()),2),IS=round(float(s[iO-1]),2),OOS=round(float(s[-1]-s[iO-1]),2),net_2x=round(float(s2[-1]),2),
                   sharpe_ngay=round(float(dn.mean()/dn.std(ddof=1)),3),ngay_lo_te_nhat=round(float(dn.min()),2)))
    ghi('c',C_[-1])
pd.DataFrame(C_).to_csv(f'{OUT}/c_danh_muc.csv',index=False)
json.dump(dict(cua_so_ES=[str(pd.to_datetime(x,unit='ms')) for x in WE],cua_so_GC=[str(pd.to_datetime(x,unit='ms')) for x in WG],truc_chung=[str(pd.to_datetime(T_[0],unit='ms')),str(pd.to_datetime(T_[-1],unit='ms'))],
               lenh_phu_chon={k:dict(v) for k,v in bestB.items()},lot_phu=LOT),open(f'{OUT}/meta.json','w'),indent=1,default=str)
open(f'{OUT}/chay.log','w').write('\n'.join(LOG)); ghi('HET')
