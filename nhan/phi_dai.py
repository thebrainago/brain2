# -*- coding: utf-8 -*-
"""phi_dai.py - MO HINH PHI XM MICRO cho backtest DAI (21/10/2026, Grok Bot).

spread(t) = spread_gio_XM[gio server]  x  he_so_nam[nam]
  * spread_gio_XM : DO THAT tren tai khoan XM (reports/phi_san/XMGlobal-MT5_10/spread_gio.csv, tick 10/2026) - da co trong
                    nhan.tai_khoan.ho_so_phi.
  * he_so_nam     : median spread nam y / median spread nam moc (nam day du moi nhat cua cung nguon), gio 02..22 server.
                    Nguon uu tien: tick XM tu MT5 (mt5tools/tai_lich_su_mt5.py, tick_spread.csv) > Dukascopy bid/ask mau
                    (nhan.tai_du_lieu). Nam khong co nguon -> lay he so nam co do som nhat, nhan 'NGOẠI SUY'.
swap: diem/lot/dem tu ma.csv XM (DO 06/10/2026) - swap LICH SU theo lai suat tung nam CHƯA ĐO ĐƯỢC (dung muc hien tai).
hoa hong: 0 USD/lot (DO: tong cot hoa_hong cua moi deal trong reports/ong_dan/ket_qua_mt5/*_lenh_mt5.csv).
Ra: config/phi_xm_micro.json (commit duoc, khong co khoa / mat khau).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parent.parent
CFG = GOC / "config" / "phi_xm_micro.json"
THU = GOC / "data" / "du_lieu_dai"
PHI_SAN = GOC / "reports" / "phi_san" / "XMGlobal-MT5_10"
GIO_DUNG = range(2, 23)


def he_so_tu_bang(sp: pd.DataFrame) -> dict:
    """sp: cot nam, gio, spread (moi dong 1 mau). -> {nam: he so} so voi nam moc (nam moi nhat co >= 20 mau)."""
    sp = sp[sp["gio"].isin(GIO_DUNG) & (sp["spread"] > 0)]
    if sp.empty:
        return {}
    med = sp.groupby("nam")["spread"].median()
    dem = sp.groupby("nam")["spread"].count()
    ok = med[dem >= 20]
    if ok.empty:
        return {}
    moc = ok.index.max()
    return {int(y): round(float(v / ok[moc]), 3) for y, v in ok.items()}


def bang_mt5(ma: str, thu: Path = THU) -> pd.DataFrame:
    ph = []
    for f in (thu / "mt5").glob("*/%s/tick_spread.csv" % ma) if (thu / "mt5").exists() else []:
        x = pd.read_csv(f).dropna(subset=["p50"])
        x = x[x["gio"] >= 0]
        ph.append(pd.DataFrame({"nam": pd.to_datetime(x["ngay"]).dt.year, "gio": x["gio"], "spread": x["p50"]}))
    return pd.concat(ph) if ph else pd.DataFrame(columns=["nam", "gio", "spread"])


def bang_duka(ma: str, thu: Path = THU) -> pd.DataFrame:
    from nhan import tai_du_lieu as TD
    d = thu / "duka" / ma
    ra = []
    for fb in sorted(d.glob("*_BID_m1.bi5")) if d.exists() else []:
        fa = Path(str(fb).replace("_BID_", "_ASK_"))
        if not fa.exists():
            continue
        ngay = dt.date.fromisoformat(fb.name[:10])
        hs = TD.he_so_dk(ma)
        b = {r[0]: r[4] for r in TD.doc_bi5_nen(fb.read_bytes(), ngay, hs)}
        a = {r[0]: r[4] for r in TD.doc_bi5_nen(fa.read_bytes(), ngay, hs)}
        for t, pb in b.items():
            if t in a and a[t] > pb:
                ts = pd.Timestamp(t, tz="UTC").tz_convert("America/New_York").tz_localize(None) + pd.Timedelta(hours=7)
                ra.append((ts.year, ts.hour, a[t] - pb))
    return pd.DataFrame(ra, columns=["nam", "gio", "spread"])


def he_so_nam(ma: str, nam_tu: int = 2004, nam_den: int | None = None, thu: Path = THU) -> tuple[dict, dict]:
    nam_den = nam_den or dt.date.today().year
    xm, dk = he_so_tu_bang(bang_mt5(ma, thu)), he_so_tu_bang(bang_duka(ma, thu))
    hs, ng = {}, {}
    for y in range(nam_tu, nam_den + 1):
        if y in xm:
            hs[y], ng[y] = xm[y], "TICK_XM"
        elif y in dk:
            # noi Dukascopy vao thang do XM: chia cho he so Duka cua nam XM som nhat co ca 2 nguon
            chung = sorted(set(xm) & set(dk))
            k = (xm[chung[0]] / dk[chung[0]]) if chung else 1.0
            hs[y], ng[y] = round(dk[y] * k, 3), "DUKASCOPY" + ("" if chung else " (chưa nối được với XM)")
    if hs:
        som = min(hs)
        for y in range(nam_tu, nam_den + 1):
            if y not in hs:
                hs[y], ng[y] = hs[som] if y < som else hs[max(k for k in hs if k < y)], "NGOẠI SUY"
    return hs, ng


def hoa_hong_do(thu_muc: Path = GOC / "reports" / "ong_dan" / "ket_qua_mt5") -> dict:
    s, n = 0.0, 0
    for f in thu_muc.glob("*_lenh_mt5.csv"):
        b = pd.read_csv(f, sep=";", usecols=["hoa_hong"])
        s += float(b["hoa_hong"].astype(float).abs().sum()); n += len(b)
    return {"tong_usd": round(s, 4), "so_deal": n}


def swap_xm(p: Path = PHI_SAN / "ma.csv") -> dict:
    if not p.exists():
        return {}
    return {r["goc"]: {"symbol": r["symbol"], "swap_mode": r["swap_mode"], "swap_mua_diem": float(r["swap_mua"]),
                       "swap_ban_diem": float(r["swap_ban"]), "ngay_x3": r["ngay_x3"], "spread_p50_gia": float(r["spread_p50_gia"] or 0),
                       "spread_p90_gia": float(r["spread_p90_gia"] or 0)} for r in csv.DictReader(open(p, encoding="utf-8"))}


def lam(ma: list[str]) -> dict:
    hh = hoa_hong_do(); sw = swap_xm()
    ra = {"_nhan": "spread giờ = ĐO (tick XM 10/2026); hệ số năm theo nguồn ghi ở nguon_nam; swap = ĐO 06/10/2026 (lịch sử CHƯA ĐO ĐƯỢC); "
                   "hoa hồng = ĐO", "_hoa_hong_lot": 0.0 if hh["tong_usd"] == 0 else None, "_hoa_hong_do": hh,
          "_luc": dt.datetime.now().isoformat(timespec="seconds")}
    for m in ma:
        hs, ng = he_so_nam(m)
        r = dict(sw.get(m, {"swap": "CHƯA ĐO ĐƯỢC"}))
        r["spread_nam"] = {str(k): v for k, v in hs.items()} if hs else {}
        r["nguon_nam"] = {str(k): v for k, v in ng.items()} if ng else {"*": "CHƯA ĐO ĐƯỢC (hệ số 1.0)"}
        ra[m] = r
    CFG.write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    return ra


def doc(p: Path = CFG) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def mang_he_so(idx: pd.DatetimeIndex, spread_nam: dict) -> np.ndarray:
    """He so spread cho tung nen theo nam; nam ngoai bang -> nam gan nhat; bang rong -> 1."""
    if not spread_nam:
        return np.ones(len(idx))
    k = sorted(int(x) for x in spread_nam)
    y = np.clip(idx.year.to_numpy(), k[0], k[-1])
    m = {int(a): float(b) for a, b in spread_nam.items()}
    return np.array([m.get(int(v), m[max(x for x in k if x <= v)]) for v in y], float)


if __name__ == "__main__":
    from nhan.tai_du_lieu import MA
    r = lam(MA)
    print(json.dumps({k: (v.get("nguon_nam") if isinstance(v, dict) else v) for k, v in r.items()}, ensure_ascii=False)[:2000])
