# Dong co mo phong US500 (XM US500Cash) - phi: spread + swap; ket qua theo ngay
import os
from cau_hinh import TAM, NGUON_M5
import pandas as pd, numpy as np
R = pd.read_parquet(os.path.join(TAM,'rth_m5.parquet'))
D = pd.read_parquet(os.path.join(TAM,'ngay.parquet'))
NB = 78
days = D.index
pos = {d: i for i, d in enumerate(days)}
O = np.full((len(days), NB), np.nan); H = O.copy(); L_ = O.copy(); C = O.copy()
R = R[pd.to_datetime(R['ngay']).isin(days)]
di = pd.to_datetime(R['ngay']).map(pos).values
bi = ((R['phut'].values - 570) // 5).astype(int)
O[di, bi] = R.open.values; H[di, bi] = R.high.values; L_[di, bi] = R.low.values; C[di, bi] = R.close.values
# lap nen thieu bang close truoc
for A in (O, H, L_, C):
    df = pd.DataFrame(A).ffill(axis=1).bfill(axis=1); A[:] = df.values
c = D.c.values; o = D.o.values; h = D.h.values; l = D.l.values

SPREAD = 0.8          # diem, khu hoi (XM US500Cash do ~0,6-0,77) + truot
SWAP_MUA_NAM = 0.0577 # phi giu lenh mua / nam (XM do 13/09/2026)
SWAP_BAN_NAM = 0.0    # XM tra +0,67%/nam cho lenh ban; than trong lay 0

def sma(x, n): return pd.Series(x).rolling(n).mean().values
def atr(n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    return pd.Series(tr).rolling(n).mean().values
def adx(n=14):
    up = np.r_[0, np.diff(h)]; dn = np.r_[0, -np.diff(l)]
    pdm = np.where((up > dn) & (up > 0), up, 0); ndm = np.where((dn > up) & (dn > 0), dn, 0)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    a = lambda x: pd.Series(x).ewm(alpha=1/n, adjust=False).mean().values
    trs = a(tr); pdi = 100*a(pdm)/trs; ndi = 100*a(ndm)/trs
    dx = 100*np.abs(pdi-ndi)/(pdi+ndi+1e-9)
    return a(dx), pdi, ndi
def rsi(x, n):
    d = np.diff(x, prepend=x[0]); u = np.clip(d, 0, None); v = np.clip(-d, 0, None)
    a = lambda z: pd.Series(z).ewm(alpha=1/n, adjust=False).mean().values
    return 100 - 100/(1 + a(u)/(a(v)+1e-12))
def lui(x, k=1): return np.r_[np.full(k, np.nan), x[:-k]]   # gia tri biet truoc phien

ATR = lui(atr()); ADX, PDI, NDI = [lui(z) for z in adx()]
SMA = {n: lui(sma(c, n)) for n in (20, 50, 100, 200)}
SMA_SLOPE = {n: lui(sma(c, n)) > lui(sma(c, n), 21) for n in (50, 100, 200)}
PREVC = lui(c)

def che_do(f):
    """+1 tang, -1 giam, 0 dung ngoai. Chi dung du lieu den het phien truoc."""
    pc = PREVC
    if f == 'none': return np.ones(len(c))

    if f.startswith('slope'):
        n = int(f[5:]); return np.where(SMA_SLOPE[n], 1, -1)
    if f.startswith('adx') and f[3:].isdigit():
        t = int(f[3:]); return np.where(ADX > t, np.where(PDI > NDI, 1, -1), 0)
    if f == 'sma200+adx20':
        a = np.where(pc > SMA[200], 1, -1); b = np.where(ADX > 20, np.where(PDI > NDI, 1, -1), 0)
        return np.where(a == b, a, 0)
    if f.startswith('sma') and f[3:].isdigit():
        n = int(f[3:]); return np.where(pc > SMA[n], 1, -1)
    if f == 'sma50&slope200':
        a = np.where(pc > SMA[50], 1, -1); b = np.where(SMA_SLOPE[200], 1, -1)
        return np.where(a == b, a, 0)
    raise ValueError(f)

def ket_qua(r, mae, don_bay, nam=None):
    """r, mae: loi nhuan/ngay & bat loi xau nhat trong ngay tren 1 don vi phoi nhiem (da tru phi)."""
    eq = 1.0; dinh = 1.0; dd = 0.0
    for x, m in zip(r, mae):
        thap = eq*(1 + don_bay*m)
        if thap <= 0: return {'cagr': -1.0, 'dd': 1.0, 'chay': True}
        dd = max(dd, 1 - thap/dinh)
        eq *= (1 + don_bay*x)
        if eq <= 0: return {'cagr': -1.0, 'dd': 1.0, 'chay': True}
        dinh = max(dinh, eq); dd = max(dd, 1 - eq/dinh)
    nam = nam or (days[-1] - days[0]).days/365.25
    return {'cagr': eq**(1/nam) - 1, 'dd': dd, 'chay': False}
