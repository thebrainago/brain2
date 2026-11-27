# DD tha noi (equity) cua IBS tinh tu danh sach lenh MT5 (model 2, 10 nam, L5) + nen M5 XM:
# moi lenh: lot = L*von/gia_vao; von noi = von dong + lot*(gia thap nhat cua nen - gia vao) - spread; swap lay ty le tu MT5.
import sys, json, numpy as np, pandas as pd
xm=pd.read_csv(sys.argv[1]); xm['t']=pd.to_datetime(xm.time,format='%Y.%m.%d %H:%M'); xm=xm.set_index('t')
m=pd.read_csv(sys.argv[2]); m['t']=pd.to_datetime(m.time,format='%Y.%m.%d %H:%M')
vao=m[m.entry==0].reset_index(drop=True); ra=m[m.entry==1].reset_index(drop=True)
L0=5.0; tr=[]
for a,b in zip(vao.itertuples(),ra.itertuples()):
    tr.append(dict(t0=a.t,t1=b.t,p0=a.price,p1=b.price,v=a.volume,sw_lot=b.swap/a.volume))
kq={}
CHUNK=[('2017','2018'),('2019','2020'),('2021','2022'),('2023','2024'),('2025','2026'),('2017','2026')]
for L in (3,5,8):
    for c0,c1 in CHUNK:
        eq=10000.0; dinh=eq; dd=0; ddb=0; dinhb=eq; n=0
        for t in tr:
            if not (c0<=str(t['t0'].year)<=c1): continue
            lot=np.floor(L*eq/t['p0']*100)/100; n+=1
            g=xm.loc[t['t0']:t['t1']]
            thap=g.low.min(); spr=0.7*lot   # ~0,7 diem khu hoi
            noi=eq+lot*(thap-t['p0'])-spr
            dd=max(dd,1-noi/dinh)
            eq=eq+lot*(t['p1']-t['p0'])+lot*t['sw_lot']*1.0
            dinh=max(dinh,eq); dd=max(dd,1-eq/dinh); dinhb=max(dinhb,eq); ddb=max(ddb,1-eq/dinhb)
        nam=(min(pd.Timestamp(f'{c1}-12-31'),pd.Timestamp('2026-11-26'))-pd.Timestamp(f'{c0}-01-01')).days/365.25
        kq[f'L{L}_{c0}_{c1}']=dict(lenh=n,von_cuoi=round(eq,2),lai_pct=round((eq/1e4-1)*100,1),cagr=round(((eq/1e4)**(1/nam)-1)*100,1),dd_noi=round(dd*100,1),dd_dong=round(ddb*100,1))
        print(L,c0,c1,kq[f'L{L}_{c0}_{c1}'])
json.dump(kq,open('/workspace/brain2/sp500/ket_qua/ibs_dd_noi_m5_xm.json','w'),ensure_ascii=False,indent=1)
