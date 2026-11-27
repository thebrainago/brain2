# Vong 4 (27/11 toi): (1) DSR + 4 stress tong hop cho tay_v2 US500 x1.5/x0.5
# (2) stress CHUNG VON that: cac he chay tren cung cu soc gia cung thoi diem, cong equity theo phut, chay = equity chung <= 0
#     danh muc loi (HYB+AG US500 + tay_v2 US500 +/- lenh phu US500) va +tay_v2 XAU ban 11/11 (59672872: loss_close 0.30, adx_th 30, cooldown 240, loc delta15)
# USD; USC = USD x 100. Khong dat lenh that.
import sys, os, json, numpy as np, pandas as pd
from scipy.stats import norm
REPO='/workspace/brain2'
src=open(f'{REPO}/sp500/ma/danh_muc.py').read().split('# ================= (a) he so lot')[0]
exec(src)
b_src=open(f'{REPO}/sp500/ma/danh_muc.py').read().split('# ================= (b) lenh phu giu 30-60\' =================')[1].split('B_=[]')[0]; exec(b_src)   # nap engine + du lieu + ham tay/hyb_es/phu/ngu_canh (khong chay lai (a)(b)(c))
OUT=f'{REPO}/sp500/ket_qua/stress_chung'; os.makedirs(OUT,exist_ok=True); LOG=[]
sys.path.insert(0,'/workspace/sp500_sys/antigrind'); sys.path.insert(0,'/workspace/sp500_sys/hybrid'); import runag
import phong_cach_tay.ma.chay_vang_11 as V11           # ban 59672872 (chi doc)
from phong_cach_tay.ma.chay_v2 import go as go_new, tom_tat
from phong_cach_tay.ma.may_v2 import P_v2 as P_v2_new
z0=np.load('/workspace/sp500_sys/big/sweep_big/scen/s00.npz'); dH=pd.read_pickle('/workspace/sp500_sys/hybrid/m1h.pkl')
msH=(pd.to_datetime(dH.t)-pd.Timedelta(hours=7)).values.astype('datetime64[ms]').astype('int64')
MUL=(1.5,0.5); H_CTX=60
CE_tay=ngu_canh(FE,"dat_es",msTE,H_CTX)
# ---------- he thanh phan, chay tren gia da soc ----------
def hyb_us(fac_fn):
    dd=dH.copy()
    if fac_fn is not None:
        f=fac_fn(msH, np.arange(len(dd)))
        for k in ['o','h','l','c','c5p','zz_lo']: dd[k]=dd[k].values*f
        if getattr(fac_fn,'grind',False):
            for k in ['a5','a15','ah1']: dd[k]=dd[k].values*f
    D=runag.Data(dd,z0['vp'],z0['opt']); P=B.mkP(GOC,1440,0.65)
    r,eq,*_=EH.run(*D.A,D.m5,D.c5p,D.roll,D.zzlo,D.zzext,D.didx,D.vp,D.opt,runag.SB(D.d).astype(np.float64),np.ones(len(dd)),D.fl,D.d1c,D.e200,D.e50,D.slp,P,200,len(dd))
    r=dict(zip(B.RK,r)); return eq, msH[200:200+len(eq)], bool(r['blown']>=0 or r['blown100']>=0)
def tay_us(fac_fn,mA=1.0,mO=1.0):
    d=dTE; o,h,l,c=[d[k].to_numpy(np.float64) for k in "ohlc"]
    if fac_fn is not None:
        f=fac_fn(msTE,np.arange(len(d))); o,h,l,c=o*f,h*f,l*f,c*f
    res,eq,*_=ET.run(o,h,l,c,d.roll.to_numpy(),sig_union_es,CE_tay,Ptay(P_TE,mA,mO),400,len(d))
    return eq, msTE[400:400+len(eq)], bool(res[-1]>0) if False else None, res
# tay XAU 11/11
rawG=tai_m1_vn(SPEC["XAU"]["m1"]); dX,_=dung_dac_trung(rawG)
raw_fX=pd.DataFrame({"time":dX["t"],"open":dX.o,"high":dX.h,"low":dX.l,"close":dX.c,"tick_volume":1.0})
if "tick_volume" in rawG.columns and len(rawG)==len(dX): raw_fX["tick_volume"]=rawG["tick_volume"].to_numpy()
msX=ms_m1_tu_t_vn(dX["t"])
d15X=chieu(FG,msX,["delta15_giu"],tre_ms=60_000,giu_phut=15)["delta15_giu"]
KW11=dict(L0=0.01,K=4,maxL=20,flcap=0.15,hfrac=1.0,hlot=0.01,dca_max_bars=0,loss_close=0.30,adx_th=30,h_boost=0,cooldown=240,max_age=0)
P11=P_v2_new("XAU",**KW11)
def sig_tay_xau(dw,loc=True):
    raww=pd.DataFrame({"time":dw["t"],"open":dw.o,"high":dw.h,"low":dw.l,"close":dw.c,"tick_volume":1.0})
    s=lap_tin(dw,diem_S(dw,None),diem_S_short(dw,them_rej_dn(dw,raww)),None,"chi_bao","lu")
    return loc_delta15(s,d15X) if loc else s
def tay_xau(fac_fn,loc=True,raw=None):
    if raw is None:
        o,h,l,c=[dX[k].to_numpy(np.float64) for k in "ohlc"]
        if fac_fn is not None:
            f=fac_fn(msX,np.arange(len(dX))); o,h,l,c=o*f,h*f,l*f,c*f
        raw=pd.DataFrame({"time":dX["t"],"open":o,"high":h,"low":l,"close":c,"tick_volume":raw_fX.tick_volume.values})
        pk=V11._pack_from_raw(raw,400); ms_=msX
    else:
        pk=V11._pack_from_raw(raw,50); ms_=None
    sig=sig_tay_xau(pk["dw"],loc) if raw is not None and ms_ is not None else sig_tay_xau(pk["dw"],False)
    res,eq,*_=go_new(pk["o"],pk["h"],pk["l"],pk["c"],pk["roll"],sig,P11,pk["i0"],pk["i1"],atr=pk["atr"],slope=pk["slope"],adx=pk["adx"])
    return eq, (ms_[pk["i0"]:pk["i0"]+len(eq)] if ms_ is not None else None), bool(tom_tat('x',res)['blown']), res, pk
def phu_us(fac_fn):
    ms,O,Hh,Ll,Cc,spr=CF['ES']; keep=CF['ES']
    if fac_fn is not None:
        f=fac_fn(ms,np.arange(len(ms))); CF['ES']=(ms,O*f,Hh*f,Ll*f,Cc*f,spr)
    tr,eq=phu('ES',FE,'dat_es',60,0.0); CF['ES']=keep
    return eq, ms, False
# ---------- cu soc theo thoi gian UTC (cung luc cho moi he) ----------
def gap_at(T_ms,g):
    def f(ms,idx): x=np.ones(len(ms)); x[ms>=T_ms]=1+g; return x
    return f
def grind(tot,days,start='2026-06-01'):
    def f(ms,idx):
        tt=pd.to_datetime(ms,unit='ms')+pd.Timedelta(hours=7); i_s=int(np.searchsorted(tt.values,np.datetime64(start)))
        k=np.zeros(len(ms)); k[i_s:]=np.minimum(np.arange(len(ms)-i_s)/(days*1380),1.0); return np.exp(np.log(1-tot)*k)
    f.grind=True; return f
def ghep(curves):
    T_=np.unique(np.concatenate([m for _,m in curves])); lo=max(m[0] for _,m in curves); hi=min(m[-1] for _,m in curves); T_=T_[(T_>=lo)&(T_<=hi)]
    tot=np.zeros(len(T_))
    for eq,m in curves:
        s=pd.Series(np.asarray(eq)-EQ0,index=m); s=s[~s.index.duplicated()]; tot+=s.reindex(T_,method='ffill').fillna(0.0).values
    return T_,tot
def tom_chung(T_,pnl,von=EQ0):
    eq=von+pnl; pk=np.maximum.accumulate(eq); dd=float(np.max(pk-eq)); cham0=np.nonzero(eq<=0)[0]
    return dict(net=round(float(pnl[-1]),2),maxdd=round(dd,2),dd_pct_10k=round(dd/1e4*100,2),dd_pct_30k=round(dd/3e4*100,2),von_thap_nhat=round(float(eq.min()),2),
                chay_10k=bool(len(cham0)>0),luc_chay=str(pd.to_datetime(T_[cham0[0]],unit='ms')+pd.Timedelta(hours=7)) if len(cham0) else '',chay_30k=bool((pnl<=-3e4).any()))
def chi_tiet(r,hes,cur):
    for h,(e,m) in zip(hes,cur):
        e=np.asarray(e); r['net_'+h]=round(float(e[-1]-EQ0),2); r['dd_'+h]=round(float(np.max(np.maximum.accumulate(e)-e)),2)
    return r
def ghi(*a):
    s=' '.join(str(x) for x in a); print(s,flush=True); LOG.append(s)
# ================= (1) tay_v2 US500 x1.5/x0.5: DSR + 4 stress =================
R1=[]
eqs={}
for H in (30,60):
    C=ngu_canh(FE,"dat_es",msTE,H)
    for mA,mO in [(1.0,1.0),(1.5,0.5),(1.25,0.75),(1.5,1.0),(1.0,0.5),(2.0,0.5)]:
        o,h,l,c=[dTE[k].to_numpy(np.float64) for k in "ohlc"]
        res,eq,*_=ET.run(o,h,l,c,dTE.roll.to_numpy(),sig_union_es,C,Ptay(P_TE,mA,mO),400,len(dTE)); eqs[(H,mA,mO)]=eq
def sr_ngay(eq,ms):
    s=pd.Series(np.asarray(eq),index=pd.to_datetime(ms[400:400+len(eq)],unit='ms')).resample('D').last().dropna().diff().dropna(); s=s[s!=0] if False else s
    return s
SRs={k:(lambda s:(s.mean()/s.std(ddof=1),len(s),s.skew(),s.kurt()+3))(sr_ngay(v,msTE)) for k,v in eqs.items()}
srs=np.array([v[0] for v in SRs.values()]); N=len(srs)
sr0=np.sqrt(np.var(srs,ddof=1))*((1-0.5772)*norm.ppf(1-1/N)+0.5772*norm.ppf(1-1/(N*np.e)))
for k,(sr,n,g3,g4) in SRs.items():
    if k[1:]==(1.0,1.0) and k[0]==30: continue
    dsr_=norm.cdf((sr-sr0)*np.sqrt(n-1)/np.sqrt(max(1-g3*sr+(g4-1)/4*sr**2,1e-9)))
    psr=norm.cdf((sr-0)*np.sqrt(n-1)/np.sqrt(max(1-g3*sr+(g4-1)/4*sr**2,1e-9)))
    dsr_cu=V.dsr(V.sharpe_tu_eq(eqs[k],EQ0),len(eqs[k]),n_trials=N)
    R1.append(dict(bien=f"H{k[0]} x{k[1]}/{k[2]}",sharpe_ngay=round(sr,3),n_ngay=n,psr=round(float(psr),3),dsr_ngay=round(float(dsr_),3),sr0_ky_vong_max=round(float(sr0),3),dsr_kieu_cu=round(float(dsr_cu),3)))
    ghi('dsr',R1[-1])
pd.DataFrame(R1).to_csv(f'{OUT}/tay_us_dsr.csv',index=False)
# 4 stress tong hop kieu worker Phan 2 (gap tai day von cua chinh bien the; grind tu 01/06)
R2=[]
o,h,l,c=[dTE[k].to_numpy(np.float64) for k in "ohlc"]; tT=dTE["t"].to_numpy()
for ten,(mA,mO) in [('goc',(1.0,1.0)),('x1.5/0.5',(1.5,0.5))]:
    eq=eqs[(60,mA,mO)]; i_deep=400+int(np.argmin(eq))
    for sn,fac in [('gap-10% tai day von',('gap',0.10)),('gap-20% tai day von',('gap',0.20)),('grind-20%/60ngay',('grind',0.20,60)),('grind-35%/120ngay',('grind',0.35,120))]:
        if fac[0]=='gap': f=np.ones(len(c)); f[i_deep:]=1-fac[1]
        else:
            i_s=int(np.searchsorted(tT,np.datetime64('2026-06-01'))); k=np.zeros(len(c)); k[i_s:]=np.minimum(np.arange(len(c)-i_s)/(fac[2]*1380),1.0); f=np.exp(np.log(1-fac[1])*k)
        res,eq2,*_=ET.run(o*f,h*f,l*f,c*f,dTE.roll.to_numpy(),sig_union_es,CE_tay,Ptay(P_TE,mA,mO),400,len(dTE))
        tt=tom_tat('x',res); R2.append(dict(bien=ten,kich_ban=sn,net=tt['net'],maxdd=tt['maxdd'],dd_pct=tt['dd_pct'],maxfl=tt['maxfl'],chay=tt['blown'],song=(not tt['blown']) and tt['dd_pct']<80))
        ghi('stress4',R2[-1])
pd.DataFrame(R2).to_csv(f'{OUT}/tay_us_stress4.csv',index=False)
# ================= (2) stress chung von =================
# kiem tai lap tung he truoc
eHU,mHU,bHU=hyb_us(None); ghi('tai lap HYB US500', round(float(eHU[-1]-EQ0),2))
eTU,mTU,_,_=tay_us(None); eTUx,_,_,_=tay_us(None,*MUL); ghi('tai lap tay US500', round(float(eTU[-1]-EQ0),2),'x1.5/0.5',round(float(eTUx[-1]-EQ0),2))
eTX,mTX,bTX,rTX,_=tay_xau(None); ghi('tai lap tay XAU 11/11', round(float(eTX[-1]-EQ0),2), tom_tat('x',rTX)['dd_pct'])
ePU,mPU,_=phu_us(None); ghi('tai lap phu US500', round(float(ePU[-1]-EQ0),2))
HE={'HYB_US':lambda f:hyb_us(f)[:3],'tay_US':lambda f:tay_us(f)[:2]+(False,),'tay_US_x':lambda f:tay_us(f,*MUL)[:2]+(False,),
    'phu_US':lambda f:phu_us(f),'tay_XAU11':lambda f:tay_xau(f)[:3]}
GOC_EQ={'HYB_US':(eHU,mHU),'tay_US':(eTU,mTU),'tay_US_x':(eTUx,mTU),'phu_US':(ePU,mPU),'tay_XAU11':(eTX,mTX)}
DM={'LOI':['HYB_US','tay_US'],'LOI_x':['HYB_US','tay_US_x'],'LOI+phu':['HYB_US','tay_US','phu_US'],'LOI_x+phu':['HYB_US','tay_US_x','phu_US'],
    'LOI+tayXAU11':['HYB_US','tay_US','tay_XAU11'],'LOI_x+phu+tayXAU11':['HYB_US','tay_US_x','phu_US','tay_XAU11']}
CACHE={}
def chay_he(he,key,fUS,fX):
    k=(he,key)
    if k not in CACHE: CACHE[k]=HE[he](fX if he=='tay_XAU11' else fUS)
    return CACHE[k]
R3=[]
for dm,hes in DM.items():
    T0,p0=ghep([GOC_EQ[h] for h in hes]); base=tom_chung(T0,p0); R3.append(dict(danh_muc=dm,kich_ban='goc Jun-Nov',**base)); ghi('chung',R3[-1])
    # thoi diem gap: day von chung + day von tung he
    tg={'day_chung':T0[int(np.argmin(p0))]}
    for h in hes: e,m=GOC_EQ[h]; tg['day_'+h]=m[int(np.argmin(e))]
    co_vang='tay_XAU11' in hes
    for g in (0.10,0.20):
        te=None
        for nm,T in tg.items():
            for vdir in ((-1,1) if co_vang else (-1,)):
                fUS=gap_at(T,-g); fX=gap_at(T,vdir*g); key=('gap',g,int(T),vdir)
                cur=[chay_he(h,key if h!='tay_XAU11' else key,fUS,fX)[:2] for h in hes]; blown=[h for h in hes if chay_he(h,key,fUS,fX)[2]]
                T_,p=ghep(cur); r=chi_tiet(tom_chung(T_,p),hes,cur); r.update(danh_muc=dm,kich_ban=f'gap -{int(g*100)}% US500'+(f' / vang {"-" if vdir<0 else "+"}{int(g*100)}%' if co_vang else ''),moc=nm,gio_vn=str(pd.to_datetime(T,unit='ms')+pd.Timedelta(hours=7)),he_tu_chay=','.join(blown))
                if te is None or r['maxdd']>te['maxdd']: te=r
        R3.append(te); ghi('chung',te)
    for tot,days in ((0.20,60),(0.35,120)):
        f=grind(tot,days); key=('grind',tot)
        cur=[chay_he(h,key,f,f)[:2] for h in hes]; blown=[h for h in hes if chay_he(h,key,f,f)[2]]
        T_,p=ghep(cur); r=chi_tiet(tom_chung(T_,p),hes,cur); r.update(danh_muc=dm,kich_ban=f'grind -{int(tot*100)}%/{days} ngay (ca hai ma)',he_tu_chay=','.join(blown)); R3.append(r); ghi('chung',r)
# cua so sap: HYB US500 (M15 cua bo gom, s05..s11) + tay XAU 11/11 (M5 parquet); tay US500 & lenh phu = 0 lenh (khong co du lieu Fxaurum)
L=pd.read_pickle('/workspace/sp500_sys/hybrid/m15_long.pkl')
m5=pd.read_parquet(SPEC["XAU"]["pq"]).reset_index(); m5=m5.rename(columns={m5.columns[0]:'time'}) if 'time' not in m5.columns else m5; m5['time']=pd.to_datetime(m5['time']); m5['tick_volume']=1.0
from phong_cach_tay.ma.chay_vang_an_toan import WIN
WN=list(WIN.items())
for k,(wn,(a,b)) in enumerate(WN):
    s=dict(np.load(f'/workspace/sp500_sys/big/sweep_big/scen/s{k+5:02d}.npz')); mm=s['meta']
    P=B.mkP(GOC,int(mm[2]),float(mm[3]))
    r,eqh,*_=EH.run(s['o'],s['h'],s['l'],s['c'],s['a5'],s['a15'],s['ah1'],s['m5'],s['c5p'],s['roll'],s['zzlo'],s['zzext'],s['didx'],s['vp'],s['opt'],s['S'],np.ones(len(s['o'])),s['fl'],s['d1c'],s['e200'],s['e50'],s['slp'],P,int(mm[0]),int(mm[1]))
    tw=L[(L.t>=a)&(L.t<b)].t.values; assert len(tw)==len(s['o']),(wn,len(tw),len(s['o']))
    mh=(pd.to_datetime(tw)).values.astype('datetime64[ms]').astype('int64')[int(mm[0]):int(mm[0])+len(eqh)]
    w=m5[(m5.time>=a)&(m5.time<b)].copy(); fsc=4000.0/float(w.close.iloc[0])
    for kk in ["open","high","low","close"]: w[kk]*=fsc
    eqx,_,bx,rx,pk=tay_xau(None,raw=w); mx=pk["dw"]["t"].values.astype('datetime64[ms]').astype('int64')[50:50+len(eqx)]
    rh=dict(zip(B.RK,r))
    for dm,hes in DM.items():
        cur=[(eqh,mh)]+([(eqx,mx)] if 'tay_XAU11' in hes else [])
        T_,p=ghep(cur); rr=tom_chung(T_,p); rr.update(danh_muc=dm,kich_ban=wn+' (US500 & vang cung cua so)',he_tu_chay=','.join([n for n,bb in (('HYB_US',rh['blown']>=0),('tay_XAU11',bx)) if bb and (n!='tay_XAU11' or 'tay_XAU11' in hes)]),
                  rieng_HYB_US=round(float(eqh[-1]-EQ0),2),rieng_tayXAU=round(float(eqx[-1]-EQ0),2) if 'tay_XAU11' in hes else None)
        R3.append(rr); ghi('chung',rr)
R3=pd.DataFrame(R3); R3.to_csv(f'{OUT}/chung_von.csv',index=False)
S=[]
for dm in DM:
    g=R3[(R3.danh_muc==dm)&(R3.kich_ban!='goc Jun-Nov')]
    S.append(dict(danh_muc=dm,n=len(g),song_10k=int(((~g.chay_10k)&(g.dd_pct_10k<80)).sum()),song_30k=int(((~g.chay_30k)&(g.dd_pct_30k<80)).sum()),
                  dd_te_nhat=round(float(g.maxdd.max()),2),kb_te_nhat=g.loc[g.maxdd.idxmax(),'kich_ban'],net_te_nhat=round(float(g.net.min()),2),von_thap_nhat=round(float(g.von_thap_nhat.min()),2)))
    ghi('tomtat',S[-1])
pd.DataFrame(S).to_csv(f'{OUT}/chung_von_tomtat.csv',index=False)
open(f'{OUT}/chay.log','w').write('\n'.join(LOG)); ghi('HET')
