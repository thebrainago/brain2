# Basket-engine wrapper on v3 tables (same conservative engine as v1/v2).
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,os.environ.get('ENGDIR','/workspace/bt_3m/code')); import engine
V=os.environ.get('V3ROOT','/workspace/bt_3m/v3')
SPEC={'US500':dict(pv=1.0,lev=100.0,EQ0=10000.0,topup=0.0,ttrig=0.0,swl=-1.24,sws=0.17,tdow=4),
      'XAU':dict(pv=100.0,lev=500.0,EQ0=10000.0,topup=20000.0,ttrig=0.3,swl=-83.83,sws=20.64,tdow=2)}
EST={'US500':{'xm':None,'exness_std':0.90,'exness_raw':0.50},'XAU':{'xm':None,'exness_std':0.30,'exness_raw':0.12}}
TB={}
def table(asset,mirror=False):
    k=(asset,mirror)
    if k not in TB:
        D=pd.read_parquet(f'{V}/tbl/{asset}{"_MIRROR" if mirror else ""}.parquet')
        TB[k]=D
    return TB[k]
def arrays(D,sl=None):
    s=slice(None) if sl is None else sl
    return dict(o=D.open.values[s],h=D.high.values[s],l=D.low.values[s],c=D.close.values[s],spr=D.spread_px.values[s],atr=np.nan_to_num(D.atr5.values[s]),roll=D.rollover.values[s],dow=D.dow.values[s].astype(np.int64))
def mgmt_vec(asset,m,sprmul=1.0,slip=0.5):
    P=SPEC[asset]
    return np.array([m['L0'],m['mult'],m['gap'],m['gstep'],m['maxN'],m['btp'],m.get('trim',0),m.get('prune',0),m.get('hedge',0),m.get('hgap',0),m.get('hr',0.5),m.get('htp',5.0),m.get('cd',30),m.get('comp',0),
        P['pv'],P['lev'],P['EQ0'],P['topup'],P['ttrig'],P['swl'],P['sws'],slip,sprmul,m.get('dsig',0),m.get('maxlots',0),m.get('gatr',0.0),P['tdow']],float)
def run(asset,sig,m,sl=None,mirror=False,sprmul=1.0,slip=0.5,cost='xm',D=None):
    D=table(asset,mirror) if D is None else D; A=arrays(D,sl); s=sig if sl is None else sig[sl]
    spr=A['spr'] if cost=='xm' else np.full(len(A['spr']),EST[asset][cost])
    out=engine.run(A['o'],A['h'],A['l'],A['c'],spr,A['atr'],np.ascontiguousarray(s,dtype=np.int64),A['roll'],A['dow'],mgmt_vec(asset,m,sprmul,slip))
    return out
def quick(asset,out,idx):
    P=SPEC[asset]; ec,ew,nl,dep,st=out; cap=P['EQ0']+P['topup']; ex=dep-P['EQ0']; en=ec-ex; ewn=ew-ex
    pk=np.maximum.accumulate(en); dd=float(np.max(pk-ewn)); mon=pd.Series(en,index=idx).groupby(idx.strftime('%Y-%m')).last()
    mn=mon.diff(); mn.iloc[0]=mon.iloc[0]-P['EQ0']
    return dict(net=float(en[-1]-P['EQ0']),dd=dd,dd_pct=dd/cap*100,so=int(st[3]),nb=int(st[0]),wins=int(st[1]),maxlay=int(st[4]),maxlot=float(st[5]),months={k:round(float(v),0) for k,v in mn.items()},topup=float(st[8]-P['EQ0']))
A_END=pd.Timestamp('2026-08-20',tz='UTC')
def periods(D):
    t=D.index; ia=int(np.searchsorted(t,A_END)); n=len(D)
    return dict(A=slice(0,ia),B=slice(ia,n),ALL=slice(0,n))
