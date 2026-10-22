# -*- coding: utf-8 -*-
"""xuong_tin_hieu.py - CAC KIEU TIN HIEU TO HOP cua XUONG (22/10/2026, Claude).

Moi to hop o day la mot CHUOI tin hieu {-1,0,+1} (su kien o nen i, vao lenh o open nen i+1) - tuc la **MOT chuoi lenh vao
+ MOT bo quan li**, nen xuat duoc thanh CSV lenh vao va MT5 (EA BRAIN_XuLiLenh che do VAO_CSV) xac nhan duoc nhu moi the khac.

Kieu (khoa "kieu" cua `tin_hieu` cua the), moi kieu nhan cac tin hieu con la dict tin_hieu cua the khac:
  dao            {nguon}                       dao chieu (ban khi he goc mua). Phat hien he vao sai chieu.
  bo_phieu       {nguon: [..], k, cua_so}      K-trong-N: vao khi >= k tin hieu con CUNG chieu trong `cua_so` nen va khong
                                               tin hieu con nao nguoc chieu; chi phat khi co mot su kien MOI cung chieu.
  chuyen_che_do  {a, b | None, che_do}         dung A khi che do thi truong BAT, dung B khi TAT (b None -> TAT = khong vao).
                                               Y tuong "nao dieu phoi" cua EA31337 (chon chien luoc theo bien dong / xu huong /
                                               phien / thu trong tuan), nhung quy ve mot chuoi lenh.
  khoang_cach    {nguon, toi_thieu}            bo bot lenh cung chieu lien tiep gan nhau (it hon `toi_thieu` nen) - bo loc "thua".
  su_kien        {luc: [ISO..], chieu: [+-1..]} chuoi su kien DONG BANG theo thoi diem (khong phu thuoc chi bao): lenh vao that cua mot
                                               he da chay (CSV lenh MT5), hoac tin hieu thay the dich vong dung de PHAN RA dong gop.
Che do thi truong (`che_do`): {"ten": "bien_dong"|"xu_huong"|"gio"|"thu"|"khoang", ...}. TAT CA chi dung du lieu den het nen i
(nhan qua), khong nhin truoc.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

KIEU = ("dao", "bo_phieu", "chuyen_che_do", "khoang_cach", "su_kien")
TEN_CHE_DO = ("bien_dong", "xu_huong", "gio", "thu", "khoang")


def _atr(df: pd.DataFrame, n: int) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean()


def mat_na_che_do(df: pd.DataFrame, cd: dict) -> np.ndarray:
    """-> bool[len(df)]: che do thi truong BAT tai nen i (biet het nen i). NaN -> False."""
    ten = cd.get("ten")
    if ten == "bien_dong":
        # ATR(n)/gia xep hang phan vi trong `cua_so` nen gan nhat; BAT khi >= q (bien dong cao) hoac <= q neu cao=False
        a = (_atr(df, int(cd.get("n", 14))) / df["close"]).to_numpy()
        w = int(cd.get("cua_so", 500))
        q = float(cd.get("q", 0.5))
        hang = pd.Series(a).rolling(w, min_periods=max(50, w // 5)).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True).to_numpy()
        m = hang >= q if cd.get("cao", True) else hang <= q
        return np.where(np.isnan(hang), False, m)
    if ten == "xu_huong":
        # |close - SMA(n)| / ATR(14) >= x : dang chay xu huong (BAT) ; cao=False -> di ngang
        nn = int(cd.get("n", 100))
        s = df["close"].rolling(nn, min_periods=nn).mean()
        z = ((df["close"] - s).abs() / _atr(df, 14)).to_numpy()
        m = z >= float(cd.get("x", 2.0)) if cd.get("cao", True) else z < float(cd.get("x", 2.0))
        return np.where(np.isnan(z), False, m)
    if ten == "gio":
        g = (pd.DatetimeIndex(df.index).hour.to_numpy() + 1) % 24          # gio cua nen KE TIEP (cho khop `bo_loc_gio`)
        tu, den = int(cd.get("tu", 8)), int(cd.get("den", 17))
        return (g >= tu) & (g < den) if tu < den else (g >= tu) | (g < den)
    if ten == "thu":
        ds = [int(x) for x in cd.get("ds", [0, 1, 2, 3, 4])]
        return np.isin(pd.DatetimeIndex(df.index).dayofweek.to_numpy(), ds)
    if ten == "khoang":
        # vi tri cua gia trong kenh `n` nen (0..1): BAT khi tu <= vi tri <= den
        nn = int(cd.get("n", 200))
        hi = df["high"].rolling(nn, min_periods=nn).max()
        lo = df["low"].rolling(nn, min_periods=nn).min()
        v = ((df["close"] - lo) / (hi - lo).replace(0, np.nan)).to_numpy()
        m = (v >= float(cd.get("tu", 0.0))) & (v <= float(cd.get("den", 1.0)))
        return np.where(np.isnan(v), False, m)
    raise ValueError("che do thi truong la: %s (nhan %r)" % (", ".join(TEN_CHE_DO), ten))


def _huong_gan_nhat(s: np.ndarray, cua_so: int) -> np.ndarray:
    """Chieu su kien khac 0 gan nhat tai moi nen, het han sau `cua_so` nen (0 neu khong co)."""
    s = np.sign(np.asarray(s, float))
    idx = np.where(s != 0, np.arange(len(s)), -1)
    idx = np.maximum.accumulate(idx) if len(idx) else idx
    h = np.where(idx >= 0, s[np.maximum(idx, 0)], 0.0)
    return np.where(np.arange(len(s)) - idx <= cua_so, h, 0.0)


def bo_phieu(chuoi: list[np.ndarray], k: int, cua_so: int = 3) -> np.ndarray:
    """K-trong-N: tai nen i co su kien MOI (it nhat mot tin hieu con phat chieu d tai i), va trong `cua_so` nen
    >= k tin hieu con co chieu gan nhat = d, khong tin hieu con nao co chieu gan nhat = -d -> phat d."""
    n = len(chuoi[0])
    moi = np.sign(np.asarray(chuoi, float))                                # (N, n) su kien tai nen
    hg = np.asarray([_huong_gan_nhat(c, cua_so) for c in chuoi])           # (N, n)
    dung = (hg > 0).sum(axis=0)
    sai = (hg < 0).sum(axis=0)
    ra = np.zeros(n, int)
    ra[(dung >= k) & (sai == 0) & (moi > 0).any(axis=0)] = 1
    ra[(sai >= k) & (dung == 0) & (moi < 0).any(axis=0)] = -1
    return ra


def khoang_cach(s: np.ndarray, toi_thieu: int) -> np.ndarray:
    """Giu su kien dau, bo su kien CUNG CHIEU xuat hien chua du `toi_thieu` nen sau su kien da giu truoc."""
    s = np.asarray(s, int).copy()
    cuoi, chieu = -10**9, 0
    for i in np.nonzero(s)[0]:
        if s[i] == chieu and i - cuoi < toi_thieu:
            s[i] = 0
        else:
            cuoi, chieu = i, int(s[i])
    return s


def tu_su_kien(luc, chieu, index: pd.DatetimeIndex) -> np.ndarray:
    """Su kien (thoi diem, chieu) -> chuoi tin hieu tren `index`: su kien roi vao nen DONG gan nhat truoc/tai no (nhan qua).
    Su kien truoc nen dau tien bi bo; nhieu su kien cung nen: su kien cuoi thang."""
    s = np.zeros(len(index), int)
    vt = index.get_indexer(pd.DatetimeIndex(pd.to_datetime(list(luc))), method="pad")
    for i, c in zip(vt, chieu):
        if i >= 0:
            s[i] = int(np.sign(c))
    return s


def thay_the_dich_vong(s: np.ndarray, index: pd.DatetimeIndex, lech: int) -> dict:
    """Tin hieu THAY THE: dich vong chuoi su kien `s` di `lech` nen (giu so lenh, ti le mua/ban, cum su kien; mat quan he voi gia)
    -> the `su_kien` dong bang. Dung de do 'quan li tu no co lai khong khi tin hieu vao khong con y nghia'."""
    r = np.roll(np.asarray(s, int), int(lech))
    i = np.nonzero(r)[0]
    return {"kieu": "su_kien", "luc": [str(index[k]) for k in i], "chieu": [int(r[k]) for k in i], "n": int(len(s))}


def tin_hieu(th: dict, df: pd.DataFrame, ma: str, con) -> np.ndarray:
    """`con(th_con, df, ma) -> np.ndarray` tinh tin hieu cua mot the con (do `ong_dan.tin_hieu` truyen vao)."""
    k = th["kieu"]
    if k == "dao":
        return -np.asarray(con(th["nguon"], df, ma), int)
    if k == "bo_phieu":
        ch = [np.asarray(con(x, df, ma), int) for x in th["nguon"]]
        return bo_phieu(ch, int(th.get("k", 2)), int(th.get("cua_so", 3)))
    if k == "chuyen_che_do":
        m = mat_na_che_do(df, th["che_do"])
        sa = np.asarray(con(th["a"], df, ma), int)
        if th.get("b") is None:
            return np.where(m, sa, 0).astype(int)
        sb = np.asarray(con(th["b"], df, ma), int)
        return np.where(m, sa, sb).astype(int)
    if k == "khoang_cach":
        return khoang_cach(np.asarray(con(th["nguon"], df, ma), int), int(th.get("toi_thieu", 6)))
    if k == "su_kien":
        return tu_su_kien(th["luc"], th["chieu"], pd.DatetimeIndex(df.index))
    raise ValueError("kieu tin hieu xuong la: %s (nhan %r)" % (", ".join(KIEU), k))


def mo_ta(th: dict) -> str:
    """Mot dong tieng Viet cho nguoi doc."""
    k = th.get("kieu")
    if k == "dao":
        return "đảo chiều của (%s)" % mo_ta(th["nguon"])
    if k == "bo_phieu":
        return "%d/%d bỏ phiếu: %s" % (int(th.get("k", 2)), len(th["nguon"]), " + ".join(mo_ta(x) for x in th["nguon"]))
    if k == "chuyen_che_do":
        cd = th["che_do"]
        return "chế độ %s %s: (%s) khi BẬT, %s khi TẮT" % (cd.get("ten"), {kk: v for kk, v in cd.items() if kk != "ten"},
                                                              mo_ta(th["a"]), mo_ta(th["b"]) if th.get("b") else "không vào")
    if k == "khoang_cach":
        return "giãn lệnh ≥ %s nến của (%s)" % (th.get("toi_thieu", 6), mo_ta(th["nguon"]))
    if k == "su_kien":
        return "%d sự kiện đóng băng" % len(th.get("luc") or [])
    if k == "to_hop":
        bl = th.get("bo_loc") or []
        return "%s%s%s" % (mo_ta(th["nguon"]), (" + lọc " + ",".join((x.get("tham") or {}).get("kieu", "?") for x in bl)) if bl else "",
                           (" + B: " + mo_ta(th["nguon_b"])) if th.get("nguon_b") else "")
    if k == "brain":
        return "BRAIN %s" % (th.get("tham") or {}).get("kieu")
    return str(k)
