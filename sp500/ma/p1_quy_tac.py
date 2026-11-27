# PHAN 1 (XAU + SP500): do hieu qua tung quy tac du lieu (big trade, wall/gamma, delta/footprint/hap thu, VWAP, ho so khoi luong, flowRecs)
# tren du lieu Fxaurum (ESZ6, GCZ6), vao/ra tren gia CFD XM (US500Cash / GOLD.i M1, gio may chu = NY+7) => da quy doi basis.
# Su kien tinh xong cuoi phut futures m; vao o gia MO cua nen CFD bat dau m+1 phut; ra o gia MO nen CFD sau H phut. Tru phi vong tron.
# Nguong (phan vi) chi hieu chinh tren NUA DAU so phien. Doi chung ngau nhien: cung so lenh, gio ngau nhien trong cung khung gio, chieu ngau nhien.
import sys, os, glob, json, numpy as np, pandas as pd
SYM=sys.argv[1]            # ES | GC
OUT=sys.argv[2] if len(sys.argv)>2 else '/workspace/brain2/sp500/ket_qua/p1'
os.makedirs(OUT,exist_ok=True); rng=np.random.default_rng(11)
HS=[5,15,30,60]; HCH=60; COOL=15
# ---------------- du lieu ----------------
if SYM=='ES':
    D='/workspace/sp500_2711/tick_esz6'; fr=[]; PRO={}
    for f in sorted(glob.glob(D+'/phut_*.csv')):
        x=pd.read_csv(f); ten=os.path.basename(f)[5:13]
        if len(x)<300: continue
        x['phien']=ten; fr.append(x)
        h=D+f'/hoso_{ten}.csv'
        if os.path.exists(h): PRO[ten]=pd.read_csv(h)
    F=pd.concat(fr).drop_duplicates('phut_ms').sort_values('phut_ms').reset_index(drop=True)
    CF='/workspace/sp500_sys/US500Cash_M1.csv'; DIEM=0.01; TRUOT=0.2; MUL=1.0   # USD / 1 lot / 1 diem
else:
    D='/workspace/sp500_2711/gc_tick'; F=pd.read_csv(D+'/gc_phut.csv').sort_values('phut_ms').reset_index(drop=True)
    ny=pd.to_datetime(F.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York')
    F['phien']=(ny+pd.Timedelta(hours=6)).dt.strftime('%Y%m%d').values
    hs=pd.read_csv(D+'/gc_hoso.csv',dtype={'ngay':str}); PRO={k:v for k,v in hs.groupby('ngay')}
    CF='/workspace/sp500_sys/GOLD_i_M1.csv'; DIEM=0.01; TRUOT=0.05; MUL=100.0
ny=pd.to_datetime(F.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York')
F['p']=(ny.dt.hour*60+ny.dt.minute).values
c=pd.read_csv(CF,parse_dates=['time']).drop_duplicates('time')
cms=((c.time-pd.Timedelta(hours=7)).dt.tz_localize('America/New_York',ambiguous='NaT',nonexistent='NaT').dt.tz_convert('UTC').dt.tz_localize(None)
     .values.astype('datetime64[ms]').astype('int64'))
ok=cms>0; c=c[ok]; cms=cms[ok]
CO=pd.Series(c.open.values,index=cms); CO=CO[~CO.index.duplicated()]; CC=pd.Series(c.close.values,index=cms); CC=CC[~CC.index.duplicated()]
PHI=float(np.median(c.spread.values)*DIEM+2*TRUOT)
F=F[F.phut_ms<=cms.max()].reset_index(drop=True)
PH=sorted(F.phien.unique()); half=set(PH[:len(PH)//2])
F['nua']=np.where(F.phien.isin(half),1,2)
# basis = futures - CFD (cung phut, gia dong)
F['basis']=F.c.values-CC.reindex(F.phut_ms.values).values
# ---------------- dac trung ----------------
F['d']=F.vol_mua-F.vol_ban; F['bd']=F.lon_mua-F.lon_ban
def theo_phien(col,fn): return F.groupby('phien')[col].transform(fn)
F['cvd']=theo_phien('d','cumsum')
F['d15']=theo_phien('d',lambda s:s.rolling(15,min_periods=15).sum())
F['b30']=theo_phien('bd',lambda s:s.rolling(30,min_periods=30).sum())
tp=(F.h+F.l+F.c)/3; F['tpv']=tp*F.vol; F['tp2v']=tp*tp*F.vol
cv=theo_phien('vol','cumsum'); F['vwap']=theo_phien('tpv','cumsum')/cv
F['vsd']=np.sqrt(np.maximum(theo_phien('tp2v','cumsum')/cv-F.vwap**2,1e-9))
F['rng']=F.h-F.l; F['rmed']=F.groupby('phien')['rng'].transform(lambda s:s.rolling(30,min_periods=10).median())
F['vmed']=theo_phien('vol',lambda s:s.rolling(30,min_periods=10).median())
F['hh30']=theo_phien('h',lambda s:s.shift(1).rolling(30,min_periods=30).max()); F['ll30']=theo_phien('l',lambda s:s.shift(1).rolling(30,min_periods=30).min())
F['cmax30']=theo_phien('cvd',lambda s:s.shift(1).rolling(30,min_periods=30).max()); F['cmin30']=theo_phien('cvd',lambda s:s.shift(1).rolling(30,min_periods=30).min())
F['atr']=theo_phien('rng',lambda s:s.rolling(60,min_periods=20).mean())
H1=F[F.nua==1]
Q=dict(b30=float(np.nanquantile(np.abs(H1.b30),0.95)),d15=float(np.nanquantile(np.abs(H1.d15),0.90)))
# vung gia tri phien truoc
def va(hs):
    hs=hs.sort_values('gia'); v=(hs.vol_mua+hs.vol_ban).values; g=hs.gia.values
    if len(v)<5: return None
    i=int(np.argmax(v)); tot=v.sum(); lo=hi=i; acc=v[i]
    while acc<0.7*tot:
        a=v[lo-1] if lo>0 else -1; b=v[hi+1] if hi<len(v)-1 else -1
        if b>=a: hi+=1; acc+=v[hi]
        else: lo-=1; acc+=v[lo]
    return g[i],g[hi],g[lo]
VA={}; prev=None
for ph in PH:
    if prev is not None and prev in PRO:
        r=va(PRO[prev]);
        if r: VA[ph]=r
    prev=ph
F['poc']=F.phien.map(lambda k:VA.get(k,(np.nan,)*3)[0]); F['vah']=F.phien.map(lambda k:VA.get(k,(np.nan,)*3)[1]); F['val']=F.phien.map(lambda k:VA.get(k,(np.nan,)*3)[2])
# wall tu levels_v2 (1 tuan 20-26/11) - snapshot moi nhat truoc phut m
W=[json.loads(l) for l in open('/workspace/sp500_sys/hyb/levels_v2.jsonl')]
W=[w for w in W if w.get('name')==SYM]
if W:
    wt=np.array([pd.Timestamp(w['ts']).tz_localize('Asia/Saigon').tz_convert('UTC').value//10**6 for w in W]); o=np.argsort(wt); wt=wt[o]; W=[W[i] for i in o]
    j=np.searchsorted(wt,F.phut_ms.values,side='right')-1; okw=(j>=0)&(F.phut_ms.values-wt[np.maximum(j,0)]<6*3600*1000)
    F['cw']=np.where(okw,[W[k].get('call_wall_above') or np.nan for k in np.maximum(j,0)],np.nan).astype(float)
    F['pw']=np.where(okw,[W[k].get('put_wall_below') or np.nan for k in np.maximum(j,0)],np.nan).astype(float)
    F['am']=np.where(okw,[1.0 if W[k].get('regime')=='negative_gamma' else 0.0 for k in np.maximum(j,0)],np.nan)
    OIK=[sorted([c_['k'] for c_ in (W[k].get('oi_clusters') or [])][:3]) for k in range(len(W))]
    for q_ in range(3): F[f'oi{q_}']=np.where(okw,[ (OIK[k][q_] if len(OIK[k])>q_ else np.nan) for k in np.maximum(j,0)],np.nan).astype(float)
else:
    F['cw']=F['pw']=F['am']=np.nan
    for q_ in range(3): F[f'oi{q_}']=np.nan
# flowRecs GC (sw/ab/ice/cs), chi ~18-27/11
FL={}
if SYM=='GC':
    j=json.load(open('/workspace/brain2/vang/du_lieu/fxaurum/gcz6_flow.json'))
    for k in ['sw','ab','ice','cs']:
        R_=[]
        for r in j[k]:
            if isinstance(r,dict): R_.append((r.get('ms',r.get('lastMs')),r['side'],r.get('vol',r.get('filled',1))))
            else: R_.append((r[0],r[1],r[2]))
        a=pd.DataFrame(R_,columns=['ms','side','q']); a['m']=(a.ms//60000)*60000+60000   # tinh xong cuoi phut -> gan phut sau
        a['sg']=np.where(a.side=='B',1,-1)*a.q; FL[k]=a.groupby('m').sg.sum()
# ---------------- tin hieu co ban: mang chieu theo phut ----------------
n=len(F); S={}
def z(): return np.zeros(n)
cl=F.c.values; hh=F.h.values; ll=F.l.values; op=F.o.values
x=z(); x[F.b30.values>Q['b30']]=1; x[F.b30.values<-Q['b30']]=-1; S['big30_theo']=x; S['big30_nguoc']=-x
x=z(); x[F.d15.values>Q['d15']]=1; x[F.d15.values<-Q['d15']]=-1; S['delta15_theo']=x; S['delta15_nguoc']=-x
x=z(); x[(cl>=F.hh30.values)&(F.cvd.values<F.cmax30.values)]=-1; x[(cl<=F.ll30.values)&(F.cvd.values>F.cmin30.values)]=1; S['cvd_phan_ky']=x
x=z(); m_=(F.vol.values>2*F.vmed.values)&(np.abs(F.d.values)>0.2*F.vol.values)&(np.abs(cl-op)<=0.25*F.rmed.values); x[m_]=-np.sign(F.d.values[m_]); S['hap_thu']=x
up=F.vwap.values+2*F.vsd.values; dn=F.vwap.values-2*F.vsd.values
x=z(); x[hh>=up]=-1; x[ll<=dn]=1; S['vwap2sd_fade']=x; S['vwap2sd_pha']=-x
pc=np.r_[np.nan,cl[:-1]]; vw=F.vwap.values
x=z(); x[(pc<vw)&(cl>vw)]=1; x[(pc>vw)&(cl<vw)]=-1; S['vwap_cat_theo']=x
vah=F.vah.values; val=F.val.values; poc=F.poc.values
x=z(); x[(hh>=vah)&(cl<vah)]=-1; x[(ll<=val)&(cl>val)]=1; S['vah_val_fade']=x
x=z(); x[(pc<=vah)&(cl>vah)]=1; x[(pc>=val)&(cl<val)]=-1; S['vah_val_pha']=x
x=z(); x[(ll<=poc)&(hh>=poc)&(pc>poc)]=1; x[(ll<=poc)&(hh>=poc)&(pc<poc)]=-1; S['poc_cham_bat']=x
cw=F.cw.values; pw=F.pw.values; am=F.am.values
x=z(); x[(hh>=cw)&(cl<cw)]=-1; x[(ll<=pw)&(cl>pw)]=1; S['wall_cham_fade']=x
x=z(); x[(pc<=cw)&(cl>cw)]=1; x[(pc>=pw)&(cl<pw)]=-1; S['wall_pha_theo']=x
x=z()
for q_ in range(3):
    lv=F[f'oi{q_}'].values; t_=(ll<=lv)&(hh>=lv)
    x[t_&(pc>lv)]=1; x[t_&(pc<lv)]=-1
S['oi_cum_cham_bat']=x
x=z(); g=np.nan_to_num(am)==1; ra=np.abs(cl-op)>F.rmed.values
x[g&ra]=np.sign(cl-op)[g&ra]; S['gamma_am_theo_nen_manh']=x
for k,sr in FL.items():
    v=sr.reindex(F.phut_ms.values).fillna(0).values; thr=np.quantile(np.abs(v[v!=0]),0.9) if (v!=0).any() else np.inf
    x=z(); x[v>thr]=1; x[v<-thr]=-1; S[f'flow_{k}_theo']=x; S[f'flow_{k}_nguoc']=-x
# ---------------- do ----------------
pm=F.phut_ms.values; IDX=CO.index.values; OV=CO.values
def gia(ms):
    j=np.searchsorted(IDX,ms); ok=(j<len(IDX))&(IDX[np.minimum(j,len(IDX)-1)]==ms); return np.where(ok,OV[np.minimum(j,len(IDX)-1)],np.nan)
E0=gia(pm+60000); EH={H:gia(pm+60000*(1+H)) for H in HS}
def chon(x):
    """lay su kien: chieu khac 0, cach nhau >= COOL phut trong cung phien (chi khi doi tu 0 -> !=0 hoac sau cooldown)"""
    idx=np.nonzero(x)[0]; out=[]; last=-10**9; lp=None
    for i in idx:
        if F.phien.values[i]!=lp: last=-10**9; lp=F.phien.values[i]
        if pm[i]-last>=COOL*60000: out.append(i); last=pm[i]
    return np.array(out,int)
def thong_ke(ii,dirs,H=HCH):
    r=(EH[H][ii]-E0[ii])*dirs-PHI; r=r[np.isfinite(r)]
    if len(r)<3: return dict(n=len(r))
    w=r[r>0].sum(); l=-r[r<0].sum()
    return dict(n=len(r),thang=round(float((r>0).mean()*100),1),tb=round(float(r.mean()),3),pf=round(float(w/l),2) if l>0 else 99.0,
                t=round(float(r.mean()/r.std(ddof=1)*np.sqrt(len(r))),2) if r.std(ddof=1)>0 else 0.0,tong_usd_1lot=round(float(r.sum()*MUL),1))
# khung gio hop le cho doi chung (cung phut-trong-ngay voi su kien)
BUCK=F.p.values//30; POOL={b:np.nonzero(BUCK==b)[0] for b in np.unique(BUCK)}
def doi_chung(ii,dirs,ngan=200):
    """tra ve (p chieu ngau nhien, p giu nguyen chieu cua tin hieu nhung gio ngau nhien -> loai tru loi nho xu huong chung)"""
    base=thong_ke(ii,dirs)['tb'] if len(ii)>=3 else np.nan
    bk=BUCK[ii]; r1=[]; r2=[]
    for _ in range(ngan):
        jj=np.array([POOL[b][rng.integers(len(POOL[b]))] for b in bk])
        for dd,out in ((rng.choice([-1,1],len(ii)),r1),(dirs,r2)):
            r=(EH[HCH][jj]-E0[jj])*dd-PHI; r=r[np.isfinite(r)]; out.append(r.mean() if len(r) else np.nan)
    return float(np.nanmean(np.array(r1)>=base)), float(np.nanmean(np.array(r2)>=base))
BANG=[]; EV={}
def danh_gia(ten,x,nhom):
    ii=chon(x); dirs=x[ii]; EV[ten]=(ii,dirs)
    row=dict(ma=SYM,quy_tac=ten,nhom=nhom,n=len(ii))
    for H in HS:
        s=thong_ke(ii,dirs,H); row[f'tb_{H}p']=s.get('tb',np.nan)
    s=thong_ke(ii,dirs,HCH); row.update({k+'_60p':v for k,v in s.items() if k!='n'})
    for h in (1,2):
        m=F.nua.values[ii]==h; s=thong_ke(ii[m],dirs[m]); row[f'n_nua{h}']=int(m.sum()); row[f'tb60_nua{h}']=s.get('tb',np.nan)
    if len(ii)>=5: p1_,p2_=doi_chung(ii,dirs); row['p_ngau_nhien']=round(p1_,3); row['p_cung_chieu']=round(p2_,3)
    BANG.append(row); print(row,flush=True)
NHOM={'big30':'big trade','delta15':'delta/footprint','cvd':'delta/footprint','hap_thu':'hap thu','vwap':'VWAP','vah':'ho so KL','poc':'ho so KL','wall':'wall/gamma','gamma':'wall/gamma','oi_':'wall/gamma','flow':'flowRecs Fxaurum'}
for k,x in S.items(): danh_gia(k,x,next(v for kk,v in NHOM.items() if k.startswith(kk)))
# ---------------- to hop (c): A va B cung chieu trong 15 phut ----------------
def giu(x,H=15):
    y=pd.Series(np.where(x!=0,x,np.nan)).groupby(F.phien.values).transform(lambda s:s.ffill(limit=H)).fillna(0).values; return y
G={k:giu(v) for k,v in S.items()}
co_ban=[k for k in S if not k.endswith('_nguoc') and not k.endswith('_pha') and k!='vwap2sd_pha']
for a in co_ban:
    for b in co_ban:
        if a>=b: continue
        x=np.where((S[a]!=0)&(G[b]==S[a]),S[a],0.0)
        if (x!=0).sum()>=8: danh_gia(f'{a} + {b}',x,'to hop')
        x=np.where((S[a]!=0)&(G[b]==-S[a]),S[a],0.0)
        if (x!=0).sum()>=8: danh_gia(f'{a} NGUOC {b}',x,'xung dot')

# ---------------- (d) diem uu tien khi tin hieu bat dong ----------------
BASE=[k for k in co_ban if len(EV[k][0])>=10]
W={}
for k in BASE:
    ii,dd=EV[k]; m=F.nua.values[ii]==1; st=thong_ke(ii[m],dd[m])
    t=st.get('t',0.0) if st.get('n',0)>=10 else 0.0
    W[k]=float(np.sign(t)*min(abs(t),3)/3) if abs(t)>=1.0 else 0.0
DIEM_=sum(W[k]*G[k] for k in BASE)
for th in (0.3,0.6,1.0):
    x=np.where(np.abs(DIEM_)>=th,np.sign(DIEM_),0.0); x=np.where(np.r_[0,np.abs(np.diff(x))]>0,x,0.0)
    danh_gia(f'DIEM_trong_so>={th}',x,'diem uu tien')

# ---------------- (d) luat uu tien khi bat dong: big trade 30' > delta 15' > muc gia (VA/POC/VWAP/wall) ----------------
KICH=['vah_val_fade','vah_val_pha','poc_cham_bat','vwap2sd_fade','wall_cham_fade','wall_pha_theo','oi_cum_cham_bat','cvd_phan_ky','hap_thu']
trig=np.zeros(n,bool); lvdir=np.zeros(n)
for k in KICH:
    m_=S[k]!=0; trig|=m_; lvdir=np.where((lvdir==0)&m_,S[k],lvdir)
gb=G['big30_theo']; gd=G['delta15_theo']
for ten_,x in [('UU_TIEN_big>delta>muc',np.where(trig,np.where(gb!=0,gb,np.where(gd!=0,gd,np.where(S['vah_val_pha']!=0,S['vah_val_pha'],0))),0)),
               ('UU_TIEN_chi_khi_big_xac_nhan',np.where(trig&(gb!=0),gb,0)),
               ('UU_TIEN_muc_chi_khi_big_khong_nguoc',np.where(trig&(gb*lvdir>=0)&(gd*lvdir>=0),lvdir,0)),
               ('UU_TIEN_big+delta_cung_chieu',np.where(trig&(gb!=0)&(gb==gd),gb,0))]:
    danh_gia(ten_,x.astype(float),'luat uu tien')
# bang xung dot: su kien muc gia (vung/wall) xep theo big30 & delta15 dang giu
XD=[]
for lv in ['vah_val_fade','vah_val_pha','poc_cham_bat','wall_cham_fade','wall_pha_theo','cvd_phan_ky','hap_thu']:
    ii,dd=EV[lv]
    if len(ii)<5: continue
    for ten_b,arr_b in [('big30',G['big30_theo']),('delta15',G['delta15_theo'])]:
        rel=np.sign(arr_b[ii])*dd
        for lab,mk in [('cung_chieu',rel>0),('nguoc_chieu',rel<0),('khong_co',rel==0)]:
            st=thong_ke(ii[mk],dd[mk]); row=dict(ma=SYM,su_kien=lv,loc=ten_b,quan_he=lab,**st)
            for h in (1,2):
                mm=mk&(F.nua.values[ii]==h); s2=thong_ke(ii[mm],dd[mm]); row[f'n_nua{h}']=int(mm.sum()); row[f'tb_nua{h}']=s2.get('tb',np.nan)
            XD.append(row)
pd.DataFrame(XD).to_csv(os.path.join(OUT,f'xung_dot_{SYM}.csv'),index=False)
df=pd.DataFrame(BANG); df.to_csv(os.path.join(OUT,f'quy_tac_{SYM}.csv'),index=False)
json.dump(dict(ma=SYM,phien=len(PH),tu=PH[0],den=PH[-1],phi_vong_tron=PHI,nguong=Q,trong_so_diem=W,basis_trung_vi=float(np.nanmedian(F.basis)),
               phut=len(F),ngay_wall=sorted(set(pd.to_datetime(F.phut_ms[F.cw.notna()],unit='ms').dt.strftime('%Y-%m-%d')))),
          open(os.path.join(OUT,f'meta_{SYM}.json'),'w'),indent=1,default=float)
print('HET',SYM)
