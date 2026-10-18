# -*- coding: utf-8 -*-
"""nguon_lenh.py - BIEN MOI NGUON LENH THANH DONG `LenhVao` cho `nhan/tai_khoan.chay_tk` (18/10/2026).

Ba duong, KHONG chay ma tai ve:
  1. NOI BO: tin hieu cua EA BRAIN da hoan thien (`ea_demo/BRAIN_XuLiLenh.mq5` InpVao = MRZ / RSI / Donchian) viet lai
     dung cong thuc cua EA (nen DA DONG cua khung, vao o open nen ke tiep) -> dua sang MT5 khop 1-1 bang file .set.
  2. SPEC DSL: ma MQL4/MQL5/Pine -> `nhan/doc_ma.doc_chien_luoc` (bo dich KHONG can LLM da co) -> spec -> `ngu_phap.sinh_tu_spec`.
  3. LLM (`nhan/cau_llm.py`) cho ma kho -> spec cung dinh dang (chi khi co khoa trong bien moi truong).
Moi tin hieu `s[i]` BIET TAI CLOSE nen i; lenh vao o OPEN nen i+1 (khong nhin truoc). Bo loc (`bo_loc_*`) tra mang bool
cung chi so, AND voi tin hieu.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nhan.tai_khoan import LenhVao

KHUNG_PHUT = {"M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}


def doi_khung(df: pd.DataFrame, khung: str) -> pd.DataFrame:
    """Gop nen (gio SERVER) len khung lon hon. H1 -> H4 (moc 0/4/8.. gio server), D1 (theo ngay server)."""
    if khung in ("H1", None, ""):
        return df
    luat = {"H4": "4h", "D1": "1D", "H2": "2h", "M30": "30min"}[khung]
    g = df.resample(luat, label="left", closed="left")
    x = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last()})
    return x.dropna()


def _sma(x: pd.Series, n: int) -> pd.Series:
    return x.rolling(n, min_periods=n).mean()


def rsi(c: pd.Series, n: int = 14) -> pd.Series:
    """RSI kieu Wilder (nhu iRSI cua MT5)."""
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def tin_hieu_brain(df: pd.DataFrame, kieu: str, n: int = 50, nguong_z: float = 2.0, rsi_thap: float = 30.0,
                   rsi_cao: float = 70.0, rsi_n: int = 14) -> np.ndarray:
    """Dung `TinHieu()` cua BRAIN_XuLiLenh. kieu: MRZ | RSI | DONCHIAN | KHONG (+1 luon mua)."""
    c = df["close"]
    if kieu == "MRZ":
        m, s = _sma(c, n), c.rolling(n, min_periods=n).std(ddof=0)      # iStdDev MODE_SMA = do lech chuan quan the
        z = (c - m) / s.replace(0, np.nan)
        return np.where(z < -nguong_z, 1, np.where(z > nguong_z, -1, 0)).astype(int)
    if kieu == "RSI":
        r = rsi(c, rsi_n)
        return np.where(r < rsi_thap, 1, np.where(r > rsi_cao, -1, 0)).astype(int)
    if kieu == "DONCHIAN":
        hh = df["high"].shift(1).rolling(n, min_periods=n).max()
        ll = df["low"].shift(1).rolling(n, min_periods=n).min()
        return np.where(c > hh, 1, np.where(c < ll, -1, 0)).astype(int)
    if kieu == "KHONG":
        return np.ones(len(df), dtype=int)
    raise ValueError("kieu tin hieu la: %s" % kieu)


def tin_hieu_spec(specs: list[dict], df: pd.DataFrame) -> np.ndarray:
    """Cac spec DSL (moi chieu mot spec, tu `doc_ma.doc_chien_luoc`) -> s[i] in {-1,0,1}. Hai chieu cung bat -> 0."""
    from nhan import ngu_phap as NP
    tong = np.zeros(len(df))
    for sp in specs:
        x = np.asarray(NP.sinh_tu_spec(sp, df), float)
        tong += np.sign(np.nan_to_num(x))
    return np.sign(tong).astype(int)


# ---------------------------------------------------------------- BO LOC (vai tro "bo_loc")
def bo_loc_xu_huong(df: pd.DataFrame, n: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """(cho_mua, cho_ban): mua chi khi close > SMA(n), ban chi khi close < SMA(n)."""
    m = _sma(df["close"], n)
    c = df["close"]
    return (c > m).to_numpy(), (c < m).to_numpy()


def bo_loc_gio(df: pd.DataFrame, tu: int, den: int) -> np.ndarray:
    """Chi cho vao lenh khi gio SERVER cua nen KE TIEP trong [tu, den) (vong qua 0h duoc)."""
    g = (pd.DatetimeIndex(df.index).hour.to_numpy() + 1) % 24
    return (g >= tu) & (g < den) if tu < den else (g >= tu) | (g < den)


def bo_loc_bien_dong(df: pd.DataFrame, n: int = 14, tran_pct: float = 1.0) -> np.ndarray:
    """Bo vao lenh khi ATR(n)/gia > tran_pct % (thi truong dang chay manh - DCA nguy hiem)."""
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(n, min_periods=n).mean()
    return (atr / c * 100.0 <= tran_pct).fillna(False).to_numpy()


def ap_loc(s: np.ndarray, cho_mua=None, cho_ban=None, cho_ca=None) -> np.ndarray:
    s = np.asarray(s, int).copy()
    if cho_ca is not None:
        s[~np.asarray(cho_ca, bool)] = 0
    if cho_mua is not None:
        s[(s > 0) & ~np.asarray(cho_mua, bool)] = 0
    if cho_ban is not None:
        s[(s < 0) & ~np.asarray(cho_ban, bool)] = 0
    return s


def lenh_vao(df: pd.DataFrame, s: np.ndarray, nguon: str, ma: str = "", truc: pd.DatetimeIndex | None = None,
             chi_mua: bool = False, chi_ban: bool = False) -> list[LenhVao]:
    """s[i] != 0 -> LenhVao o OPEN nen i+1 (cua `df`). `truc` = truc thoi gian chung cua tai khoan (nhieu ma / khung):
    chi_so doi sang vi tri tren truc (nen dau tien >= thoi diem mo nen i+1)."""
    s = np.asarray(s, int)
    o = df["open"].to_numpy(float)
    i = np.nonzero(s[:-1] != 0)[0]
    if chi_mua:
        i = i[s[i] > 0]
    if chi_ban:
        i = i[s[i] < 0]
    j = i + 1
    if truc is not None:
        vt = truc.get_indexer(df.index[j], method="bfill")
        ok = vt >= 0
        return [LenhVao(nguon, int(p), float(o[k]), int(s[k - 1]), ma) for p, k in zip(vt[ok], j[ok])]
    return [LenhVao(nguon, int(k), float(o[k]), int(s[k - 1]), ma) for k in j]
