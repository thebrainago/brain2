# Tong hop CSV giao dich do EA SP500_* xuat ra (FILE_COMMON) -> CAGR / DD (theo so du dong lenh) / so lenh / swap
import pandas as pd, numpy as np, zipfile, sys, io, json
def tong(zip_path, ngay_cuoi='2026-11-26', von=10000):
    out=[]
    z=zipfile.ZipFile(zip_path)
    for n in z.namelist():
        if not n.endswith('.csv'): continue
        ten=n.replace('\\','/').split('/')[0]
        d=pd.read_csv(io.BytesIO(z.read(n)),encoding='latin1'); x=d[d.entry==1]
        if len(x)==0: out.append(dict(test=ten,lenh=0)); continue
        t=pd.to_datetime(d.time); nam=(pd.Timestamp(ngay_cuoi)-t.iloc[0]).days/365.25
        b=np.r_[von,x.balance_after.values]; pk=np.maximum.accumulate(b)
        out.append(dict(test=ten,tu=str(t.iloc[0].date()),lenh=len(x),thang_pct=round(((x.profit+x.swap)>0).mean()*100,1),
            so_du_cuoi=round(b[-1],0),cagr_pct=round(((max(b[-1],1)/von)**(1/nam)-1)*100,1),dd_dong_pct=round((1-b/pk).max()*100,1),
            swap=round(x.swap.sum(),0),phi=round(x.commission.sum(),0)))
    return out
if __name__=='__main__':
    r=[]; [r.extend(tong(p)) for p in sys.argv[1:]]
    print(pd.DataFrame(r).to_string(index=False)); json.dump(r,open('tong_mt5.json','w'),ensure_ascii=False,indent=1)
