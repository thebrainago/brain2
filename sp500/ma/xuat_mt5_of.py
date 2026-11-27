# Xuat ung vien giai doan B ra MT5: CSV lenh vao (gio server) + .set BRAIN_XuLiLenh (VAO_CSV) + .ini cho p6 (model 4 tick that).
import sys, os, json, pandas as pd
sys.path.insert(0,'/workspace/brain2/sp500/ma')
import ghep_of as G
OUT='/workspace/sp500_2711/mt5_of'; os.makedirs(OUT,exist_ok=True)
def xuat(ten,loai,dao,q,tu='2026.08.20',den='2026.11.27'):
    ev=G.lenh_vao(loai,dao)
    b=pd.DataFrame({'thoi_gian':[G.idx[e.chi_so].strftime('%Y.%m.%d %H:%M:%S') for e in ev],'ma':'US500Cash#','chieu':[e.chieu for e in ev],
                    'gia':[round(e.gia,2) for e in ev],'nguon':loai,'lot':[q['lot0']]*len(ev)})
    b.to_csv(f'{OUT}/of_{ten}.csv',index=False,lineterminator='\r\n')
    v={'InpVao':4,'InpTF':5,'InpFileCsv':f'of_{ten}.csv','InpCsvChung':'true','InpCsvMa':'','InpCsvTreGiay':600,'InpXuatGia':'false',
       'InpChieuKhongTin':0,'InpChoNen':0,'InpLot0':q['lot0'],
       'InpNhoi':1 if (q.get('dca_toi_da',0)>0 and q.get('dca_buoc_pct')) else 0,'InpBuocGia':0.0,'InpBuocATR':0.0,'InpBuocPct':float(q.get('dca_buoc_pct') or 0),
       'InpGianBuoc':1.0,'InpKieuLot':0 if q.get('dca_he_so_lot',1.0)==1.0 else 2,'InpHeSoLot':q.get('dca_he_so_lot',1.0),'InpMaxTang':q.get('dca_toi_da',0)+1,
       'InpTPGia':float(q.get('tp_gia') or 0),'InpTPATR':0.0,'InpTPPct':0.0,
       'InpTrailKichGia':0.0,'InpTrailKichATR':0.0,'InpTrailKhoangGia':0.0,'InpTrailKhoangATR':0.0,
       'InpTrailKichPct':float(q.get('trail_kich_pct',0)),'InpTrailKhoangPct':float(q.get('trail_khoang_pct',0)),'InpGiuToiDaNen':int(q.get('giu_toi_da_nen',0)),
       'InpHedgeKhiLoPct':float(q.get('hedge_khi_lo_pct',0)),'InpHedgeTiLe':1.0,'InpMoKhoaGia':0.0,'InpMoKhoaATR':0.0,'InpMoKhoaPct':float(q.get('mo_khoa_pct',0)),
       'InpKhoaLaiKhongMoc':'true','InpGoTien':float(q.get('go_tien') or 0),'InpHedgeMaxLan':3,'InpMarginMin':0.0,'InpCatLoPct':0.0,
       'InpGioCamTu':23,'InpGioCamDen':2,'InpSpreadMaxGia':0.0,'InpMagic':2711900,'InpFileLog':f'of_{ten}_log.csv','InpLogChung':'true'}
    open(f'{OUT}/of_{ten}.set','w').write('\r\n'.join(f'{k}={x}' for k,x in v.items())+'\r\n')
    open(f'{OUT}/sp500_of_{ten}.ini','w').write('\r\n'.join(['[Tester]','Expert=sp500\\BRAIN_XuLiLenh.ex5',f'ExpertParameters=of_{ten}.set','Symbol=US500Cash#','Period=M5','Model=4',
        f'FromDate={tu}',f'ToDate={den}','Deposit=10000','Currency=USD','Leverage=500','Optimization=0','ShutdownTerminal=1',''])) 
    return len(b)
if __name__=='__main__':
    ds=json.load(open(sys.argv[1]))
    for d in ds: print(d['ten'],xuat(d['ten'],d['loai'],d['dao'],d['ql']))
