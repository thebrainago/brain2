# Gom tick GCZ6 (Fxaurum aggTrades da xuat boi worker vang, chi doc) thanh dac trung phut + ho so khoi luong theo phien Globex.
# Phien = ngay giao dich CME: 18:00 NY hom truoc -> 17:00 NY. Lon = qty >= NGUONG_LON hop dong (GC 1 hd = 100 oz ~ 0,35-0,45 trieu USD).
import sys, os, pandas as pd, numpy as np
SRC=sys.argv[1]; OUT=sys.argv[2]; LON=int(sys.argv[3]) if len(sys.argv)>3 else 5
os.makedirs(OUT,exist_ok=True)
phut=[]; hs={}
for ch in pd.read_csv(SRC,usecols=['time_ms','price','qty','side'],chunksize=2_000_000):
    ch=ch.dropna(); ch['m']=(ch.time_ms//60000)*60000
    ch['b']=np.where(ch.side=='B',ch.qty,0.0); ch['s']=np.where(ch.side=='S',ch.qty,0.0)
    big=ch.qty>=LON; ch['lb']=np.where(big,ch.b,0.0); ch['ls']=np.where(big,ch.s,0.0)
    g=ch.groupby('m'); a=g.agg(o=('price','first'),h=('price','max'),l=('price','min'),c=('price','last'),vol=('qty','sum'),
        vol_mua=('b','sum'),vol_ban=('s','sum'),so_lenh=('qty','size'),lon_mua=('lb','sum'),lon_ban=('ls','sum'),max_qty=('qty','max'))
    phut.append(a)
    ny=pd.to_datetime(ch.time_ms,unit='ms',utc=True).dt.tz_convert('America/New_York')
    ngay=(ny+pd.Timedelta(hours=6)).dt.strftime('%Y%m%d')    # 18:00 NY -> ngay ke tiep
    for (d,p),v in ch.groupby([ngay.values,ch.price.round(1).values])[['b','s']].sum().iterrows():
        x=hs.setdefault(d,{}); y=x.setdefault(p,[0.0,0.0]); y[0]+=v.b; y[1]+=v.s
    print('chunk',len(ch),flush=True)
P=pd.concat(phut); P=P.groupby(level=0).agg(dict(o='first',h='max',l='min',c='last',vol='sum',vol_mua='sum',vol_ban='sum',so_lenh='sum',lon_mua='sum',lon_ban='sum',max_qty='max'))
P.index.name='phut_ms'; P.to_csv(os.path.join(OUT,'gc_phut.csv'))
rows=[(d,p,v[0],v[1]) for d,x in hs.items() for p,v in x.items()]
pd.DataFrame(rows,columns=['ngay','gia','vol_mua','vol_ban']).sort_values(['ngay','gia']).to_csv(os.path.join(OUT,'gc_hoso.csv'),index=False)
print('HET',len(P),len(hs),flush=True)
