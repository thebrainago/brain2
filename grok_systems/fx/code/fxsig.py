# Causal mean-reversion / fade signal families for FX & CFD M1 tables. Signal at M1 index i uses only completed bars up to t_i; engine fills at open[i+1].
import numpy as np, pandas as pd
def htf(D,tf):
    r=D[['open','high','low','close']].resample(f'{tf}min').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    r.index=r.index+pd.Timedelta(minutes=tf); return r        # available at bar END
def m1(s,D): return s.reindex(D.index,method='ffill')
def ev(long_c,short_c):
    L=long_c.fillna(False).values.astype(bool); S=short_c.fillna(False).values.astype(bool)
    L=L&~np.r_[False,L[:-1]]; S=S&~np.r_[False,S[:-1]]
    return (L.astype(np.int8)-S.astype(np.int8))
def rsi(c,n):
    d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return 100-100/(1+up/(dn+1e-18))
def build(D,peer=None):
    """returns dict name-> int8 array (+1 long / -1 short, event-type). fade/MR family only."""
    S={}
    H={tf:htf(D,tf) for tf in (5,15,60)}
    for tf in (5,15,60):
        c=H[tf].close
        for N in (30,100):
            mu=c.rolling(N).mean(); sd=c.rolling(N).std(); z=m1((c-mu)/sd,D)
            for th in (2.0,2.5,3.0): S[f'z{tf}_{N}_{th}']=ev(z<-th,z>th)
    for tf in (15,60):
        h=H[tf]; c=h.close; r2=rsi(c,2); tr=c.ewm(span=200,adjust=False).mean()
        for lo,hi in ((5,95),(10,90)):
            a=m1(r2,D); t=m1((c>tr).astype(float),D).fillna(0).astype(bool)
            S[f'rsi2_{tf}_{lo}']=ev(a<lo,a>hi)
            S[f'rsi2t_{tf}_{lo}']=ev((a<lo)&t,(a>hi)&~t)       # pull-back with trend filter (EMA200)
        ib=(h.close-h.low)/(h.high-h.low).replace(0,np.nan); big=(h.high-h.low)>=(h.high-h.low).rolling(50).mean()
        for th in (0.05,0.1):
            i_=m1(ib,D); b=m1(big.astype(float),D).fillna(0).astype(bool)
            S[f'ibs_{tf}_{th}']=ev((i_<th)&b,(i_>1-th)&b)
    # long-horizon family (H4 / D1): multi-day mean reversion, swap-sensitive
    for tf in (240,1440):
        h=D[['open','high','low','close']].resample(f'{tf}min',origin='start_day').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna(); h.index=h.index+pd.Timedelta(minutes=tf); c=h.close
        for N in (20,50):
            z=m1((c-c.rolling(N).mean())/c.rolling(N).std(),D)
            for th in (2.0,2.5): S[f'L_z{tf}_{N}_{th}']=ev(z<-th,z>th)
        r2=m1(rsi(c,2),D); trd=m1((c>c.ewm(span=100,adjust=False).mean()).astype(float),D).fillna(0).astype(bool)
        S[f'L_rsi2_{tf}']=ev(r2<5,r2>95); S[f'L_rsi2t_{tf}']=ev((r2<5)&trd,(r2>95)&~trd)
        ib=m1((h.close-h.low)/(h.high-h.low).replace(0,np.nan),D); S[f'L_ibs_{tf}']=ev(ib<0.1,ib>0.9)
    # Asia range (UTC 00-06) fade at London/NY (UTC 07-14)
    day=D.index.normalize(); ah=D.high.where(D.utch<6).groupby(day).transform('max'); al=D.low.where(D.utch<6).groupby(day).transform('min')
    win=pd.Series((D.utch.values>=7)&(D.utch.values<14),index=D.index); atr=D.atr5; c=D.close
    for k in (0.5,1.0):
        S[f'asia_brkfade_{k}']=ev(win&(c<al-k*atr),win&(c>ah+k*atr))
    pe_hi=(D.high>ah+0.5*atr).where(win,False).groupby(day).cummax(); pe_lo=(D.low<al-0.5*atr).where(win,False).groupby(day).cummax()
    S['asia_failback']=ev(win&pe_lo&(c>al),win&pe_hi&(c<ah))
    if peer is not None:
        T=np.log(D.close.resample('5min').last().dropna()); P=np.log(peer.close.resample('5min').last().dropna()); P=P.reindex(T.index,method='ffill')
        for W in (864,2880):                                   # 3d, 10d of M5 bars
            mT=T.rolling(W).mean(); mP=P.rolling(W).mean(); cv=(T*P).rolling(W).mean()-mT*mP; vr=(P*P).rolling(W).mean()-mP*mP; b=cv/vr
            res=T-b*P; z=(res-res.rolling(W).mean())/res.rolling(W).std(); z.index=z.index+pd.Timedelta(minutes=5); z=m1(z,D)
            for th in (2.0,2.5,3.0): S[f'resid_{W}_{th}']=ev(z<-th,z>th)
    return S
SESS={'all':(0,24),'asia':(0,7),'ldn':(7,12),'ny':(12,20)}
def sess_mask(D,name):
    a,b=SESS[name]; return ((D.utch.values>=a)&(D.utch.values<b))
