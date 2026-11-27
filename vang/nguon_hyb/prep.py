"""Prep US500Cash# M1 (XM demo, server UTC+2 -> UTC+7), ATRs, M15 zigzag(k=2 ATR15) anchor, ES daily VP levels -> CFD."""
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/workspace/backtests/rapid_hedge')
from prep import atr, known
from song_zigzag_atr import zigzag
D='/workspace/backtests/rapid_hedge/data/'
def load():
    m=pd.read_csv(D+'US500Cash_M1.csv',parse_dates=['time']); m['time']=m.time+pd.Timedelta(hours=5)
    m=m.drop_duplicates('time').reset_index(drop=True); g=m.set_index('time'); t=m.time
    r={}
    for fr in ['5min','15min','60min']:
        x=g.resample(fr).agg({'open':'first','high':'max','low':'min','close':'last'}).dropna(); x['atr']=atr(x); r[fr]=x
    d=pd.DataFrame(dict(t=t,o=m.open,h=m.high,l=m.low,c=m.close,sprd=m.spread/100.0))
    d['a5']=known(t,r['5min'].index,r['5min'].atr.values,'5min')
    d['a15']=known(t,r['15min'].index,r['15min'].atr.values,'15min')
    d['ah1']=known(t,r['60min'].index,r['60min'].atr.values,'60min')
    f5=t.dt.floor('5min'); d['m5end']=(f5!=f5.shift(-1)).values
    d['c5p']=known(t,r['5min'].index,r['5min'].close.shift(1).values,'5min')
    d=d.bfill()
    sd=(t-pd.Timedelta(hours=5)).dt.date; d['sday']=sd; d['roll']=(sd!=sd.shift(1)).values; d.loc[0,'roll']=False
    # --- M15 zigzag k=2 (ATR15), pivots usable from the close of the confirming M15 bar
    x=r['15min']; p=zigzag(x.high.values,x.low.values,x.atr.values,2.0)
    tt=d.t.values; n=len(d)
    lo_px=np.full(n,np.nan); lo_ext=np.full(n,-1,np.int64)
    for q in p:
        if q['loai']!=-1: continue
        conf=x.index[q['xn']]+pd.Timedelta('15min')           # usable from this time
        ext=x.index[q['idx']]
        a=np.searchsorted(tt,np.datetime64(conf)); e=np.searchsorted(tt,np.datetime64(ext))
        if a<n: lo_px[a]=q['gia']; lo_ext[a]=e
    d['zz_lo']=pd.Series(lo_px).ffill().values; d['zz_ext']=pd.Series(np.where(lo_ext>=0,lo_ext,np.nan)).ffill().fillna(0).astype(np.int64).values
    # --- ES daily volume profile (Sierra scid, 30/03-20/11) -> CFD via daily basis (ES vwap - XM vol-weighted typical price)
    es=pd.read_csv('/workspace/us500bt/es_profile_daily.csv',parse_dates=['date']).set_index('date')
    m['sday']=(m.time-pd.Timedelta(hours=5)).dt.normalize(); m['tp']=(m.high+m.low+m.close)/3
    xv=m.groupby('sday').apply(lambda z:(z.tp*z.tick_volume).sum()/z.tick_volume.sum())
    b=(es.vwap-xv.reindex(es.index)).dropna(); basis=b.rolling(5,min_periods=1).median()
    lv=pd.DataFrame({k:es[k].reindex(basis.index)-basis for k in ['val','poc','vah','low']})
    # levels of the 3 prior sessions, available from the next server day
    days=sorted(d.sday.unique()); arr=np.full((len(days),12),np.nan); di={dd:i for i,dd in enumerate(days)}
    lvd=[(pd.Timestamp(k).date(),v) for k,v in lv.iterrows()]
    for i,dd in enumerate(days):
        prev=[v for k,v in lvd if k<dd][-3:]
        vals=[x_ for v in prev for x_ in (v.val,v.poc,v.vah,v.low)]
        arr[i,:len(vals)]=vals
    d['didx']=d.sday.map(di).astype(np.int64)
    return d,arr,float(basis.median())
if __name__=='__main__':
    d,arr,bm=load(); print(d.head(), d.tail(2), bm, np.isnan(arr).all(1).sum(), len(arr))
    d.to_pickle('out/m1.pkl'); np.save('out/vp.npy',arr)
