# FX/CFD research library (PYTHON SIMULATION). Data: XM Ultra Low '#' M1 BID bars + per-bar spread (MT5 export, server time Europe/Athens).
import sys,os,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/code'); sys.path.insert(0,'/workspace/bt_3m/fx/code')
import engine2 as E2
from _scalp_core import run_seq, run_flip
FX='/workspace/bt_3m/fx'; DATA=f'{FX}/data/m1'; RES=f'{FX}/results'
os.makedirs(RES,exist_ok=True)
IS_END=pd.Timestamp('2026-06-01',tz='UTC')   # IS: 2025-06-02..2026-05-31 ; OOS: 2026-06-01..2026-11-27 (same window as Gold/SP500 books)
def fname(sym): return sym.replace('#','_h').replace('.','_')
_INFO=None
def info(sym):
    global _INFO
    if _INFO is None: _INFO=pd.read_csv(f'{FX}/data/symbols_xm.csv').set_index('symbol')
    r=_INFO.loc[sym]; pv=float(r.tick_value)/float(r.tick_size)           # USD per 1.0 price unit per 1 lot (current FX rate)
    sw_unit=float(r.point)/float(r.tick_size)*float(r.tick_value)          # USD per swap point per lot
    return dict(pv=pv,swl=float(r.swap_long)*sw_unit,sws=float(r.swap_short)*sw_unit,swap3=int(r.swap3),point=float(r.point),contract=float(r.contract),vmin=float(r.vmin),vstep=float(r.vstep))
_TB={}
def table(sym):
    if sym in _TB: return _TB[sym]
    z=np.load(f'{DATA}/{fname(sym)}.npz'); pt=float(z['point'][0])
    idx=pd.to_datetime(z['t'].astype('int64'),unit='s').tz_localize('Europe/Athens',ambiguous='NaT',nonexistent='NaT')
    D=pd.DataFrame({'open':z['o']*pt,'high':z['h']*pt,'low':z['l']*pt,'close':z['c']*pt,'spread_px':z['sp']*pt,'tv':z['tv']},index=idx)
    D=D[D.index.notna()]; ath=D.index; D.index=D.index.tz_convert('UTC')
    D['dow']=ath.dayofweek.values[ath.notna()] if False else pd.DatetimeIndex(ath).dayofweek.values
    d=pd.DatetimeIndex(ath).normalize(); D['rollover']=np.r_[False,d[1:]!=d[:-1]]; D['hour']=pd.DatetimeIndex(ath).hour.values   # server (Athens) hour
    D['utch']=D.index.hour.values
    m5=D[['open','high','low','close']].resample('5min').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    tr=pd.concat([m5.high-m5.low,(m5.high-m5.close.shift()).abs(),(m5.low-m5.close.shift()).abs()],axis=1).max(axis=1)
    a=tr.ewm(alpha=1/14,adjust=False).mean().shift(1); a.index=a.index+pd.Timedelta(minutes=5)
    D['atr5']=a.reindex(D.index,method='ffill').values
    h1=D[['open','high','low','close']].resample('60min').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    tr=pd.concat([h1.high-h1.low,(h1.high-h1.close.shift()).abs(),(h1.low-h1.close.shift()).abs()],axis=1).max(axis=1)
    a=tr.ewm(alpha=1/14,adjust=False).mean().shift(1); a.index=a.index+pd.Timedelta(minutes=60)
    D['atr60']=a.reindex(D.index,method='ffill').values
    D=D[D.atr60.notna()&D.atr5.notna()]; _TB[sym]=D; return D
def flat_arr(D,fh=21):
    return (((D.dow.values==4)&(D.hour.values>=fh))).astype(np.int64)   # flatten all baskets Fri >=21:00 server
def mvec(pv,swl,sws,L0=1.0,mult=1.0,gap=0.0,gstep=1.4,maxN=4,btp=0.0,cd=30,gatr=1.0,sprmul=1.0,slip=0.5,tdow=2,EQ0=1e7,lev=1000.0):
    return np.array([L0,mult,gap,gstep,maxN,btp,0,0,0,0,0.5,5.0,cd,0,pv,lev,EQ0,0,0,swl,sws,slip,sprmul,0,0,gatr,tdow,0,0,0],float)
def run_basket(D,sig,pv,swl,sws,sl=slice(None),fl=None,**kw):
    fl=flat_arr(D) if fl is None else fl
    o=D.open.values[sl];h=D.high.values[sl];l=D.low.values[sl];c=D.close.values[sl]
    P=mvec(pv,swl,sws,**kw)
    return E2.run(o,h,l,c,D.spread_px.values[sl],np.nan_to_num(D.atr60.values[sl]),np.ascontiguousarray(sig[sl],dtype=np.int64),D.rollover.values[sl],D.dow.values[sl].astype(np.int64),np.ascontiguousarray(fl[sl]),P)
def basket_stats(out,EQ0=1e7):
    ec,ew,nl,dep,st=out; en=ec-EQ0; ewn=ew-EQ0; pk=np.maximum.accumulate(en)
    return dict(net=float(en[-1]),dd=float(np.max(pk-ewn)),nb=int(st[0]),wins=int(st[1]),maxlay=int(st[4]),maxlot=float(st[5]))
