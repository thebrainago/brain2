"""Hybrid features (all values known at the close of bar i-1, stored at index i): RSI14(M5), session VWAP z, BB(M15,20,2) z,
US cash session, M5 rejection candle, ATR regime; options levels (ES 18-26/11 -> CFD); generic so it also runs on M15 bars (stress)."""
import numpy as np, pandas as pd, json, sys
sys.path.insert(0,'/workspace/sp500_sys'); sys.path.insert(0,'/workspace/backtests/rapid_hedge')
from prep import atr, known
from song_zigzag_atr import zigzag
def rsi(c,n=14):
    d=np.diff(c,prepend=c[0]); up=pd.Series(np.maximum(d,0)).ewm(alpha=1/n,adjust=False).mean(); dn=pd.Series(np.maximum(-d,0)).ewm(alpha=1/n,adjust=False).mean()
    return (100-100/(1+up/dn.replace(0,1e-9))).values
def us_session(t):
    # US cash 09:30-16:00 ET -> UTC+7: 20:30-03:00 during US DST (to 01/11/2026), 21:30-04:00 after
    t=pd.to_datetime(t); dst=(t<pd.Timestamp('2026-11-01 14:00'))&(t>=pd.Timestamp('2026-03-08 14:00')) | ((t.year<2026)&(t.month>=4)&(t.month<=10))
    m=t.hour*60+t.minute; o=np.where(dst,20*60+30,21*60+30); rel=(m-o)%1440
    return (rel<390).astype(np.int8), (rel<120).astype(np.int8)
def build(m, bar_min=1, srv_shift_h=5):
    """m: DataFrame time(server naive),open,high,low,close,tick_volume (bar_min minutes)."""
    m=m.copy(); m['time']=m.time+pd.Timedelta(hours=srv_shift_h); m=m.drop_duplicates('time').reset_index(drop=True)
    g=m.set_index('time'); t=m.time; r={}
    for fr in ['5min','15min','60min']:
        if bar_min>=int(fr[:-3]) and fr!='60min': x=g[['open','high','low','close']].copy()
        else: x=g.resample(fr).agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
        x['atr']=atr(x); r[fr]=x
    d=pd.DataFrame(dict(t=t,o=m.open.values,h=m.high.values,l=m.low.values,c=m.close.values))
    f=f'{bar_min}min'
    for nm,fr in [('a5','5min'),('a15','15min'),('ah1','60min')]:
        d[nm]=known(t,r[fr].index,r[fr].atr.values,fr if bar_min<int(fr[:-3]) else f)
    x5=r['5min']; fr5='5min' if bar_min<5 else f
    d['m5end']=((t.dt.floor('5min')!=t.dt.floor('5min').shift(-1)).values) if bar_min<5 else True
    d['c5p']=known(t,x5.index,x5.close.shift(1).values,fr5)
    d=d.bfill()
    sd=(t-pd.Timedelta(hours=srv_shift_h)).dt.date; d['roll']=(sd!=sd.shift(1)).values; d.loc[0,'roll']=False
    # zigzag M15 k=2
    x=r['15min']; p=zigzag(x.high.values,x.low.values,x.atr.values,2.0); tt=d.t.values; n=len(d)
    lo=np.full(n,np.nan); ex=np.full(n,np.nan); f15='15min'
    for q in p:
        if q['loai']!=-1: continue
        a=np.searchsorted(tt,np.datetime64(x.index[q['xn']]+pd.Timedelta(f15))); e=np.searchsorted(tt,np.datetime64(x.index[q['idx']]))
        if a<n: lo[a]=q['gia']; ex[a]=e
    d['zz_lo']=pd.Series(lo).ffill().values; d['zz_ext']=pd.Series(ex).ffill().fillna(0).astype(np.int64).values
    # ---- indicators (value at close of bar, then shifted by 1 => known before bar i opens)
    I=pd.DataFrame(index=d.index)
    I['rsi5']=known(t,x5.index,rsi(x5.close.values),fr5)
    tp=(m.high+m.low+m.close)/3; v=m.tick_volume.clip(lower=1).astype(float); day=pd.Series(sd.values)
    cv=(tp*v).groupby(day).cumsum(); cw=v.groupby(day).cumsum(); vw=cv/cw
    var=((v*tp*tp).groupby(day).cumsum()/cw-vw*vw).clip(lower=0); sdv=np.sqrt(var)
    I['vwz']=((m.close-vw)/sdv.replace(0,np.nan)).clip(-6,6).fillna(0).values
    x15=r['15min']; mid=x15.close.rolling(20).mean(); sd15=x15.close.rolling(20).std()
    midk=known(t,x15.index,mid.values,'15min' if bar_min<15 else f); sdk=known(t,x15.index,sd15.values,'15min' if bar_min<15 else f)
    I['bbz']=((d.c-midk)/sdk).clip(-6,6).fillna(0).values
    rng=(x5.high-x5.low).replace(0,np.nan); rej=(((np.minimum(x5.open,x5.close)-x5.low)/rng>=0.5)&(x5.close>=x5.low+0.6*rng)).astype(float).values
    I['rej']=known(t,x5.index,rej,fr5)
    I['us'],I['usopen']=us_session(d.t.values)
    w=int(5*1440/bar_min); I['reg']=(d.a15/d.a15.rolling(w,min_periods=50).median()).fillna(1).values
    I=I.shift(1).bfill()
    for k in I: d[k]=I[k].values
    d['sday']=sd.values
    return d
def options_levels(d,path='/workspace/sp500_sys/hybrid/levels.jsonl',path2='/workspace/sp500_sys/hybrid/levels_v2.jsonl'):
    """per-bar array [n,6] CFD prices: put_wall, max_pain, gamma_flip, dte0 put_wall, top-2 OI cluster strikes; valid 24h after snapshot."""
    tt=d.t.values; c=d.c.values; rows=[]
    for x in open(path):
        j=json.loads(x); es=j['symbols'].get('ES',{})
        if not es.get('ok'): continue
        ts=pd.Timestamp(j['ts']); i=np.searchsorted(tt,np.datetime64(ts))-1
        if i<0 or i>=len(d): continue
        basis=es['spot']-c[i]
        rows.append((ts,[es.get('put_wall'),es.get('max_pain'),es.get('gamma_flip'),(es.get('dte0') or {}).get('put_wall'),None,None],basis))
    v2={}
    for x in open(path2):
        j=json.loads(x)
        if j.get('name')!='ES': continue
        cl=sorted(j.get('oi_clusters') or [],key=lambda z:-z['oi'])[:2]; v2[pd.Timestamp(j['ts'])]=[z['k'] for z in cl]
    v2k=sorted(v2)
    arr=np.full((len(d),6),np.nan); src=[]
    for ts,L,b in rows:
        k=np.searchsorted(np.array(v2k,dtype='datetime64[ns]'),np.datetime64(ts),side='right')-1
        if k>=0 and (ts-v2k[k])<pd.Timedelta('6h'): L[4:6]=(v2[v2k[k]]+[None,None])[:2]
        src.append((ts,[np.nan if q is None else q-b for q in L]))
    for a,(ts,L) in enumerate(src):
        i0=np.searchsorted(tt,np.datetime64(ts)); i1=np.searchsorted(tt,np.datetime64(src[a+1][0] if a+1<len(src) and src[a+1][0]-ts<pd.Timedelta('24h') else ts+pd.Timedelta('24h')))
        arr[i0:i1]=L
    return arr,len(src),(src[0][0],src[-1][0]) if src else None
if __name__=='__main__':
    m=pd.read_csv('/workspace/backtests/rapid_hedge/data/US500Cash_M1.csv',parse_dates=['time'])
    d=build(m,1)
    # ES VP from previous step
    vp=np.load('/workspace/sp500_sys/out/vp.npy'); old=pd.read_pickle('/workspace/sp500_sys/out/m1.pkl')
    assert len(old)==len(d); d['didx']=old.didx.values
    opt,nsnap,rng=options_levels(d); np.save('opt.npy',opt); print('options snapshots',nsnap,rng,'bars with opt',(~np.isnan(opt[:,0])).sum())
    d.to_pickle('m1h.pkl'); print(d[['rsi5','vwz','bbz','rej','us','reg']].describe().round(2).to_string())
