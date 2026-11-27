# Giai doan A: tin hieu orderflow tu tick ESZ6 (Fxaurum) da gom theo phut tren may nha (keo_tick_esz6.py).
# Dung lai delta / CVD / big trade / hap thu / ho so khoi luong (POC, VAH, VAL) / VWAP tu tick co chieu chu dong.
# Danh gia: lai gop diem ES sau H phut (dong muon nhat 15:59 NY), tru phi 1,0 diem/lenh; tach 2 nua so phien.
import glob, os, sys, json, numpy as np, pandas as pd
D=sys.argv[1] if len(sys.argv)>1 else '/workspace/sp500_2711/tick_esz6'
PHI=1.0; HS=[5,15,30,60,999]
def doc():
    S=[]
    for f in sorted(glob.glob(os.path.join(D,'phut_*.csv'))):
        ten=os.path.basename(f)[5:13]; x=pd.read_csv(f)
        if len(x)<300: continue
        x['t']=pd.to_datetime(x.phut_ms,unit='ms',utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
        x['p']=x.t.dt.hour*60+x.t.dt.minute
        hs=pd.read_csv(os.path.join(D,f'hoso_{ten}.csv')) if os.path.exists(os.path.join(D,f'hoso_{ten}.csv')) else None
        S.append((ten,x,hs))
    return S
def vung_gia_tri(hs):
    if hs is None or len(hs)==0: return None
    v=(hs.vol_mua+hs.vol_ban).values; g=hs.gia.values; i=int(np.argmax(v)); tot=v.sum(); lo=hi=i; acc=v[i]
    while acc<0.7*tot:
        a=v[lo-1] if lo>0 else -1; b=v[hi+1] if hi<len(v)-1 else -1
        if b>=a: hi+=1; acc+=v[hi]
        else: lo-=1; acc+=v[lo]
    return dict(poc=g[i],val=g[lo],vah=g[hi])
def tin_hieu(x,vg_truoc,nguong):
    r=x[(x.p>=570)&(x.p<960)].reset_index(drop=True)
    if len(r)<300: return r,{}
    d=(r.vol_mua-r.vol_ban).values; cvd=np.cumsum(d); c=r.c.values; h=r.h.values; l=r.l.values; o=r.o.values; v=r.vol.values
    bd=(r.lon_mua-r.lon_ban).values; tp=(h+l+c)/3; vw=np.cumsum(tp*v)/np.cumsum(v)
    sd=np.sqrt(np.maximum(np.cumsum(v*(tp-vw)**2)/np.cumsum(v),1e-9))
    rng=pd.Series(h-l).rolling(30,min_periods=10).median().values; vmed=pd.Series(v).rolling(30,min_periods=10).median().values
    p=r.p.values; S={k:[] for k in ['cvd_phan_ky','hap_thu','big_15p_theo','big_15p_nguoc','vah_val_fade','vah_val_pha','vwap2sd_fade','delta_mo_cua_30p','cvd_theo_60p']}
    big15=pd.Series(bd).rolling(15).sum().values
    for i in range(30,len(r)-1):
        if p[i]>=950: break
        hh=h[i-30:i].max(); ll=l[i-30:i].min()
        if c[i]>=hh and cvd[i]<cvd[i-30:i].max(): S['cvd_phan_ky'].append((i,-1))
        if c[i]<=ll and cvd[i]>cvd[i-30:i].min(): S['cvd_phan_ky'].append((i,1))
        if v[i]>2*vmed[i] and abs(d[i])>0.2*v[i] and abs(c[i]-o[i])<=0.25*rng[i]: S['hap_thu'].append((i,-int(np.sign(d[i]))))
        if abs(big15[i])>nguong['big15']: S['big_15p_theo'].append((i,int(np.sign(big15[i])))); S['big_15p_nguoc'].append((i,-int(np.sign(big15[i]))))
        if vg_truoc:
            if l[i]<=vg_truoc['val']<c[i-1] : S['vah_val_fade'].append((i,1))
            if h[i]>=vg_truoc['vah']>c[i-1]: S['vah_val_fade'].append((i,-1))
            if c[i]>vg_truoc['vah']>=c[i-1]: S['vah_val_pha'].append((i,1))
            if c[i]<vg_truoc['val']<=c[i-1]: S['vah_val_pha'].append((i,-1))
        if c[i]>vw[i]+2*sd[i]: S['vwap2sd_fade'].append((i,-1))
        if c[i]<vw[i]-2*sd[i]: S['vwap2sd_fade'].append((i,1))
        if p[i]==600: S['delta_mo_cua_30p'].append((i,int(np.sign(cvd[i]))))
        if i>=60 and p[i]%30==0: S['cvd_theo_60p'].append((i,int(np.sign(cvd[i]-cvd[i-60]))))
    # nghi 15 phut giua 2 tin hieu cung loai
    for k in S:
        out=[];last=-99
        for i,s in S[k]:
            if s!=0 and i-last>=15: out.append((i,s)); last=i
        S[k]=out
    return r,S
def danh_gia(S):
    rows=[]
    vg=None; nguong={'big15':None}
    # nguong big trade: phan vi 90 cua |big15| tren cac phien TRUOC (lay mau tu 5 phien dau)
    allb=[]
    for ten,x,hs in S[:5]:
        r=x[(x.p>=570)&(x.p<960)]; allb+=list(np.abs(pd.Series((r.lon_mua-r.lon_ban).values).rolling(15).sum().dropna().values))
    nguong['big15']=float(np.percentile(allb,90)) if allb else 50
    lenh=[]
    for j,(ten,x,hs) in enumerate(S):
        r,T=tin_hieu(x,vg,nguong); vg=vung_gia_tri(hs)
        if not T: continue
        c=r.c.values; last=len(r)-1
        for k,L in T.items():
            for i,s in L:
                for H in HS:
                    e=min(i+H,last); lenh.append(dict(ngay=ten,nua=0 if j<len(S)//2 else 1,loai=k,H=H,chieu=s,i=i,p=int(r.p[i]),t=r.t[i],lai=s*(c[e]-c[i])-PHI))
    return pd.DataFrame(lenh),nguong
if __name__=='__main__':
    S=doc(); print('so phien',len(S),S[0][0] if S else '',S[-1][0] if S else '')
    L,ng=danh_gia(S)
    if len(L)==0: sys.exit()
    g=L.groupby(['loai','H']).lai.agg(['count','mean','std']); g['t']=g['mean']/(g['std']/np.sqrt(g['count']))
    g2=L.groupby(['loai','H','nua']).lai.mean().unstack()
    g=g.join(g2.rename(columns={0:'nua1',1:'nua2'}))
    pd.set_option('display.width',200); print(g.round(2).to_string())
    os.makedirs('/workspace/brain2/sp500/ket_qua',exist_ok=True)
    g.round(3).reset_index().to_csv('/workspace/brain2/sp500/ket_qua/of_tin_hieu_esz6.csv',index=False)
    L.to_parquet('/workspace/sp500_2711/of_lenh.parquet')
    json.dump(dict(so_phien=len(S),nguong=ng),open('/workspace/sp500_2711/of_meta.json','w'))
