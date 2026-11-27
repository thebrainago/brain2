# Kiem dinh 7 buoc cho bien the orderflow tot nhat cua hyb_of.py so voi goc HYB+AG.
import sys, os, json, numpy as np, pandas as pd
from scipy.stats import norm
import hyb_of as H
B=H.B; s0=H.s0; OUT=H.OUT; rng=np.random.default_rng(7)
SIG={h:H.chieu_len_m1(H.FE,h) for h in (15,30)}
for h in SIG: SIG[h]['tong']=np.clip(SIG[h]['hap']+SIG[h]['cvd']+SIG[h]['big']+SIG[h]['d15'],-1,1)
UV=json.loads(sys.argv[3]) if len(sys.argv)>3 else ['S_big_tru_H15','S_d15_tru_H15','S_tong_tru_H15']
def mask(ten):
    _,k,mode,hh=ten.split('_'); x=SIG[int(hh[1:])][k]
    return np.maximum(x,0) if mode=='cong' else (np.minimum(x,0) if mode=='tru' else x)
def voi(dS):
    s=dict(s0); s['S']=s0['S']+dS; return s
def ngay_pnl(eq):
    t=H.m.time.values[H.i0:H.i0+len(eq)]; e=pd.Series(eq,index=pd.to_datetime(t)).resample('1D').last().dropna()
    return e.diff().dropna()
def sharpe(x): x=np.asarray(x); return float(x.mean()/x.std(ddof=1)) if x.std(ddof=1)>0 else 0.0
def dsr(x,N,sr_var):
    x=np.asarray(x); T=len(x); sr=sharpe(x); g3=pd.Series(x).skew(); g4=pd.Series(x).kurt()+3
    e=0.5772156649; sr0=np.sqrt(sr_var)*((1-e)*norm.ppf(1-1/N)+e*norm.ppf(1-1/(N*np.e)))
    return float(norm.cdf((sr-sr0)*np.sqrt(T-1)/np.sqrt(1-g3*sr+(g4-1)/4*sr**2))), sr, float(sr0)
R={}
goc,eqg=H.tom(s0); R['GOC']=goc
bt=pd.read_csv(os.path.join(OUT,'bien_the.csv'))
# Sharpe ngay cua tat ca bien the (de tinh phuong sai SR giua cac lan thu)
eqs=np.load('/workspace/sp500_2711/hyb_of_eq.npz'); srs=[sharpe(ngay_pnl(eqs[k])) for k in eqs.files]; N=len(eqs.files)
for ten in UV:
    dS=mask(ten); t,eq=H.tom(voi(dS)); r=dict(t)
    # (1) doi chung ngau nhien: chan cung so phut, cung do dai khoi H, vi tri ngau nhien trong gio RTH cac phien ES co du lieu
    hh=int(ten.split('_')[-1][1:]); nz=dS!=0
    rth=np.zeros(len(dS),bool)
    for rr in H.P:
        j=np.searchsorted(H.II,rr.phut_ms.values[0]); e=np.searchsorted(H.II,rr.phut_ms.values[-1]); rth[H.IV[j]:H.IV[min(e,len(H.IV)-1)]]=True
    cand=np.nonzero(rth)[0]; nblk=max(1,int(nz.sum()/hh)); dc=[]
    for it in range(200):
        x=np.zeros(len(dS)); st=rng.choice(cand,nblk,replace=False)
        for a in st: x[a:a+hh]=-1 if 'tru' in ten else 1
        x[~rth]=0; tt,_=H.tom(voi(x)); dc.append(tt['cs_OF']-goc['cs_OF'])
    dc=np.array(dc); d=t['cs_OF']-goc['cs_OF']
    r.update(delta_OF=round(d,2),dc_tb=round(dc.mean(),2),dc_p95=round(np.quantile(dc,0.95),2),p_ngau_nhien=round(float((dc>=d).mean()),3))
    # (2) dao dau tin hieu: chan khi orderflow TANG thay vi giam
    t2,_=H.tom(voi(-dS)); r['dao_dau_delta_OF']=round(t2['cs_OF']-goc['cs_OF'],2)
    # (3) lang gieng: doi 1 tham so sang gia tri ke ben tren luoi sweep_big
    nb=[]
    for i,k in enumerate(B.GK):
        vals=B.GRID[k]; j=vals.index(H.GOC[i]) if H.GOC[i] in vals else None
        if j is None: continue
        for jj in (j-1,j+1):
            if 0<=jj<len(vals):
                g=list(H.GOC); g[i]=vals[jj]; g=tuple(g)
                a,_=H.tom(s0,g); b,_=H.tom(voi(dS),g)
                nb.append(dict(ts=k,gt=vals[jj],goc_net=a['net'],bt_net=b['net'],d_net=round(b['net']-a['net'],2),d_OF=round(b['cs_OF']-a['cs_OF'],2),goc_dd=a['maxdd'],bt_dd=b['maxdd']))
    nb=pd.DataFrame(nb); nb.to_csv(os.path.join(OUT,f'lang_gieng_{ten}.csv'),index=False)
    r.update(lg_n=len(nb),lg_d_OF_duong=int((nb.d_OF>0).sum()),lg_d_net_duong=int((nb.d_net>0).sum()),lg_d_OF_trung_vi=round(float(nb.d_OF.median()),2))
    # (4) DSR: Sharpe ngay toan ky s00 + Sharpe ngay chuoi chenh lech trong cua so OF
    pv=ngay_pnl(eq); pg=ngay_pnl(eqg)
    p,sr,sr0=dsr(pv.values,N,np.var(srs)); r.update(sr_ngay=round(sr,4),sr_goc=round(sharpe(pg.values),4),dsr=round(p,3),sr0=round(sr0,4))
    w=pv.index>=pd.Timestamp(H.m.time.iloc[H.w0]).normalize(); dd=(pv-pg)[w]
    r.update(ngay_OF=int(w.sum()),ngay_chenh_duong=int((dd>0).sum()),ngay_chenh_am=int((dd<0).sum()))
    R[ten]=r; print(ten,r,flush=True)
# (5) stress 11 kich ban: khong co orderflow -> S giu nguyen -> ket qua = goc (chay lai de xac nhan)
g=H.GOC; st=[]
for s in B.SC[1:]:
    mm=s['meta']; rs,_=B.runone(s,B.mkP(g,int(mm[2]),float(mm[3])))
    st.append(dict(kb=str(s['name']),net=round(rs['net'],2),maxdd=round(rs['maxdd'],2),maxfl=round(rs['maxfl'],2),chet=int(rs['blown']>=0 or rs['blown100']>=0)))
st=pd.DataFrame(st); st.to_csv(os.path.join(OUT,'stress_goc.csv'),index=False); print(st.to_string())
R['stress']=dict(song=int((st.chet==0).sum()),te_nhat_net=float(st.net.min()),te_nhat_fl=float(st.maxfl.min()),
                 fl_pct_10k=round(-st.maxfl.min()/100,1),fl_pct_30k=round(-st.maxfl.min()/300,1))
json.dump(R,open(os.path.join(OUT,'kiem_7_buoc.json'),'w'),indent=1,default=float)
