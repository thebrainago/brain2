# Giai doan B: tin hieu orderflow ESZ6 -> LenhVao tren nen M5 US500Cash# XM -> he xu ly lenh (nhan/tai_khoan.chay_tk:
# TP ro, DCA nghich, nhoi thuan, hedge khoa/go, giu toi da). Tieu chi: lai rong > 0 va DD < 80 %.
import sys, os, json, itertools, numpy as np, pandas as pd
sys.path.insert(0,'/workspace/brain2')
from nhan import tai_khoan as T
XM='/workspace/sp500_2711/mt5/c6/xuat_nen/sp500_xm_m5_US500Cash#.csv'
L=pd.read_parquet('/workspace/sp500_2711/of_lenh.parquet'); L=L[L.H==5]
x=pd.read_csv(XM); x['t']=pd.to_datetime(x.time,format='%Y.%m.%d %H:%M'); x=x[x.t>='2026-08-17'].set_index('t')[['open','high','low','close']]
hs=T.ho_so_phi('US500Cash#'); hs.swap_mua_diem=-110.0; hs.swap_ban_diem=0.0   # 5,77 %/nam ~ 1,1 diem gia/dem/lot; ban lay 0 (than trong)
idx=x.index
# doi chung: cung so lenh, thoi diem lay ngau nhien tu cac phut co tin hieu, chieu ngau nhien / luon mua
_rng=np.random.default_rng(7); _pool=L.drop_duplicates('t')
_n=int(L.groupby('loai').size().median())
for ten,ch in (('doi_chung_ngau_nhien',None),('doi_chung_luon_mua',1)):
    smp=_pool.sample(n=min(_n,len(_pool)),random_state=11).copy(); smp['loai']=ten
    smp['chieu']=_rng.choice([-1,1],len(smp)) if ch is None else 1
    L=pd.concat([L,smp],ignore_index=True)
NGAY=sorted(L.ngay.unique()); MOC=pd.Timestamp(NGAY[len(NGAY)//2])   # tach 2 nua so phien
def lenh_vao(loai,dao=False):
    ev=[]
    for r in L[L.loai==loai].itertuples():
        t_sv=(pd.Timestamp(r.t)+pd.Timedelta(minutes=1)).tz_localize('America/New_York').tz_convert('Europe/Athens').tz_localize(None)
        k=idx.searchsorted(t_sv)
        if k>=len(idx) or (idx[k]-t_sv)>pd.Timedelta(minutes=5): continue
        ev.append(T.LenhVao(loai,int(k),float(x.open.iloc[k]),-r.chieu if dao else r.chieu))
    return ev
QL=[]
for lot0,tp,(buoc,nmax,hso),(hedge,go),giu,nhoi_thuan in itertools.product([1.0,3.0],[3.0,6.0,12.0],
        [(None,0,1.0),(0.0015,3,1.0),(0.0015,5,1.5),(0.003,5,2.0)],[(0.0,None),(3.0,0.0),(8.0,0.0)],[12,78,0],[False]):
    QL.append(dict(lot0=lot0,tp_gia=tp,dca_buoc_pct=buoc,dca_toi_da=nmax,dca_he_so_lot=hso,hedge_khi_lo_pct=hedge,go_tien=go,mo_khoa_pct=0.001 if hedge else 0.0,giu_toi_da_nen=giu))
# trailing ro (nhoi thuan chi co trong EA BRAIN_XuLiLenh, chay_tk Python chua co -> do tren MT5)
for lot0,kich,kh,giu in itertools.product([1.0,3.0],[0.001,0.002],[0.0005,0.001],[12,78,0]):
    QL.append(dict(lot0=lot0,tp_gia=None,tp_pct=None,trail_kich_pct=kich,trail_khoang_pct=kh,dca_buoc_pct=None,dca_toi_da=0,dca_he_so_lot=1.0,giu_toi_da_nen=giu))
def chay(loai,dao,q):
    q=dict(q)
    ql=T.QuanLi(**q); ev=lenh_vao(loai,dao)
    if not ev: return None
    k=T.chay_tk(x,ev,ql,tk=T.ho_so_tai_khoan(von=10000),phi=hs)
    nua={}
    for ten,m in (('n1',x.index<MOC),('n2',x.index>=MOC)):
        xi=x[m]; off=int(np.argmax(m)) if ten=='n2' else 0
        e2=[T.LenhVao(e.nguon,e.chi_so-off,e.gia,e.chieu) for e in ev if 0<=e.chi_so-off<len(xi)]
        kk=T.chay_tk(xi,e2,ql,tk=T.ho_so_tai_khoan(von=10000),phi=hs) if e2 else None
        nua[ten]=(float(kk['lai_tien']),float(kk['sut_giam_pct'])) if kk else (0.0,0.0)
    return dict(lai_n1=nua['n1'][0],dd_n1=nua['n1'][1],lai_n2=nua['n2'][0],dd_n2=nua['n2'][1],loai=loai,dao=dao,ql={a:b for a,b in q.items()},lenh_vao=len(ev),lai=float(k['lai_tien']),dd=float(k['sut_giam_pct']),
                so_lenh=int(k['so_lenh']),stop_out=int(k['so_stop_out']),so_khoa=int(k['so_khoa']),so_go=int(k['so_go']),phi_spread=float(k['phi']['spread']),phi_swap=float(k['phi']['swap']))
if __name__=='__main__':
    import multiprocessing as mp
    viec=[(loai,dao,q) for loai in sorted(L.loai.unique()) for dao in (False,True) for q in QL]
    print('so lan chay',len(viec),flush=True)
    with mp.Pool(6) as P: out=[r for r in P.starmap(chay,viec,chunksize=8) if r]
    D=pd.DataFrame(out); D.to_json('/workspace/sp500_2711/ghep_of.json',orient='records')
    D['dat']=(D.lai>0)&(D.dd<80)&(D.stop_out==0)
    D['dat_2_nua']=D.dat&(D.lai_n1>0)&(D.lai_n2>0)&(D.dd_n1<80)&(D.dd_n2<80)
    print(D.groupby(['loai','dao']).agg(n=('lai','size'),dat=('dat','sum'),dat_2_nua=('dat_2_nua','sum'),lai_max=('lai','max'),lai_tb=('lai','mean')).round(1).to_string())
    print(D.sort_values('lai',ascending=False).head(15)[['loai','dao','ql','lenh_vao','lai','dd','lai_n1','lai_n2','so_lenh','so_khoa','so_go']].to_string())
