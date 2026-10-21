# -*- coding: utf-8 -*-
"""du_lieu_dai.py - GOP + KIEM TRA du lieu gia dai (21/10/2026, Grok Bot). Chay o noi co tep tho (may nha sau khi tai).

Uu tien nguon tren moi nen M1: MT5 XM (gio server san) > histdata (EST co dinh -> server). Ra:
  data/du_lieu_dai/m5/<MA>_m5_server.csv     (time,open,high,low,close,tick_volume) - git bo qua
  data/du_lieu_dai/du_lieu_dai.json          (ban do ma -> tep, dung qua BRAIN_ONG_DAN_DU_LIEU cho nhan.ong_dan/vong2)
  reports/du_lieu_dai/PHU_SONG.json + .md    (do phu theo nam, lo hong, lech gia so voi nen MT5 that 2023-2026) - commit duoc
Gio server XM = gio New York + 7 (GMT+2 mua dong / GMT+3 mua he, doi cung ngay DST My).
"""
from __future__ import annotations

import argparse
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parent.parent
THU = GOC / "data" / "du_lieu_dai"
RA = GOC / "reports" / "du_lieu_dai"
KQ_MT5 = GOC / "reports" / "ong_dan" / "ket_qua_mt5"
SYM_MT5 = {"XAUUSD": "GOLDmicro"}


def est_sang_server(t: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """histdata: EST co dinh (UTC-5 quanh nam) -> UTC -> New York (co DST) -> +7h = gio server XM."""
    utc = (t + pd.Timedelta(hours=5)).tz_localize("UTC")
    return utc.tz_convert("America/New_York").tz_localize(None) + pd.Timedelta(hours=7)


def doc_histdata_zip(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        n = next(x for x in z.namelist() if x.endswith(".csv"))
        x = pd.read_csv(io.BytesIO(z.read(n)), sep=";", header=None, names=["t", "open", "high", "low", "close", "v"])
    x.index = est_sang_server(pd.DatetimeIndex(pd.to_datetime(x["t"], format="%Y%m%d %H%M%S")))
    return x[["open", "high", "low", "close"]].astype(float)


def doc_mt5_m1(d: Path) -> pd.DataFrame:
    ph = [pd.read_csv(f, parse_dates=["time"], index_col="time") for f in sorted(d.glob("M1_*.csv.gz"))]
    if not ph:
        return pd.DataFrame(columns=["open", "high", "low", "close"])
    return pd.concat(ph)[["open", "high", "low", "close"]].astype(float)


def gop(m1_uu_tien: pd.DataFrame, m1_phu: pd.DataFrame) -> pd.DataFrame:
    """Nen nao co o nguon uu tien thi lay nguon do; phu chi lap cho trong."""
    x = pd.concat([m1_uu_tien, m1_phu[~m1_phu.index.isin(m1_uu_tien.index)]]) if len(m1_phu) else m1_uu_tien
    return x[~x.index.duplicated(keep="first")].sort_index()


def sang_khung(m1: pd.DataFrame, khung: str = "5min") -> pd.DataFrame:
    g = m1.resample(khung, label="left", closed="left")
    return pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last(),
                         "tick_volume": g["close"].count()}).dropna()


def phu_song(m5: pd.DataFrame) -> dict:
    """Do phu theo nam: % gio ngay thuong (T2 01:00..T6 22:00 server) co nen; lo hong > 4 gio trong tuan."""
    if not len(m5):
        return {}
    h = m5["close"].resample("1h").count()
    tuan = h[(h.index.dayofweek < 4) | ((h.index.dayofweek == 4) & (h.index.hour < 22))]
    tuan = tuan[~((tuan.index.dayofweek == 0) & (tuan.index.hour < 1))]
    tuan = tuan[~((tuan.index.month == 1) & (tuan.index.day == 1)) & ~((tuan.index.month == 12) & (tuan.index.day == 25))]
    ra = {}
    for y, s in tuan.groupby(tuan.index.year):
        co = (s > 0).to_numpy()
        lo, dem = 0, 0
        for v in co:
            dem = 0 if v else dem + 1
            lo += int(dem == 5)
        ra[str(y)] = {"phu_pct": round(100 * co.mean(), 1), "lo_hong_4h": lo}
    return ra


def lech_mt5(h1: pd.DataFrame, ma: str, thu_muc: Path = KQ_MT5) -> dict | None:
    """So H1 dai voi nen H1 cua lan chay MT5 that (XM, 2023-12..2026-10): lech close (diem) va do lech gio tot nhat."""
    sym = SYM_MT5.get(ma, ma + "micro")
    best = None
    try:
        from nhan.vong2 import ung_vien_dat
        ten = [r["ten"] for r in ung_vien_dat() if r["symbol"] == sym]
    except Exception:
        ten = []
    for t in ten:
        f = thu_muc / (t + "_vao.csv_gia.csv")
        if not f.exists():
            continue
        g = pd.read_csv(f)
        g.index = pd.to_datetime(g["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
        if len(g) > 2 and (g.index[1] - g.index[0]) == pd.Timedelta(hours=1):
            best = g; break
    if best is None:
        return None
    so = best["close"].astype(str).str.split(".").str[-1].str.len().max()
    diem = 10.0 ** (-int(so))
    ra = {}
    for lech in (-2, -1, 0, 1, 2):
        a = h1["close"].shift(lech, freq="1h")
        c = a.reindex(best.index).dropna()
        if len(c) < 100:
            continue
        d = (c - best["close"].reindex(c.index)).abs() / diem
        ra[lech] = (float(d.median()), float(d.quantile(0.95)), len(c))
    if not ra:
        return None
    k = min(ra, key=lambda z: ra[z][0])
    return {"lech_gio_tot": k, "lech_close_p50_diem": round(ra[0][0], 1) if 0 in ra else None,
            "lech_close_p95_diem": round(ra[0][1], 1) if 0 in ra else None, "so_nen_chung": ra[k][2],
            "ghi_chu": "lệch giờ tốt nhất ≠ 0 → sai múi giờ" if k != 0 else "múi giờ khớp"}


def dung(ma: list[str], thu: Path = THU) -> dict:
    (thu / "m5").mkdir(parents=True, exist_ok=True); RA.mkdir(parents=True, exist_ok=True)
    ban_do, bc = {}, {}
    mt5_goc = sorted((thu / "mt5").glob("*")) if (thu / "mt5").exists() else []
    for m in ma:
        a = pd.concat([doc_mt5_m1(s / m) for s in mt5_goc if (s / m).exists()] or [pd.DataFrame()])
        hz = sorted((thu / "histdata").glob("%s_M1_*.zip" % m))
        b = pd.concat([doc_histdata_zip(f) for f in hz]) if hz else pd.DataFrame(columns=["open", "high", "low", "close"])
        if not len(a) and not len(b):
            bc[m] = {"trang_thai": "CHƯA CÓ DỮ LIỆU"}; continue
        m1 = gop(a.sort_index() if len(a) else a, b.sort_index())
        m5 = sang_khung(m1)
        out = thu / "m5" / ("%s_m5_server.csv" % m.lower())
        m5.to_csv(out, index_label="time", float_format="%.6f")
        ban_do[m] = str(out)
        h1 = sang_khung(m1, "1h")
        bc[m] = {"tu": str(m5.index[0]), "den": str(m5.index[-1]), "so_m5": int(len(m5)),
                 "nguon_m1": {"mt5_xm": int(len(a)), "histdata": int(len(b))}, "theo_nam": phu_song(m5),
                 "doi_chieu_mt5": lech_mt5(h1, m)}
        del a, b, m1, m5, h1
    (thu / "du_lieu_dai.json").write_text(json.dumps(ban_do, indent=1), encoding="utf-8")
    (RA / "PHU_SONG.json").write_text(json.dumps(bc, ensure_ascii=False, indent=1), encoding="utf-8")
    (RA / "PHU_SONG.md").write_text(ghi_md(bc), encoding="utf-8")
    return bc


def ghi_md(bc: dict) -> str:
    L = ["# Độ phủ dữ liệu dài (tự sinh bởi `python -m nhan.du_lieu_dai --dung`)", "",
         "| Mã | Từ | Đến | Nến M1 MT5 XM | Nến M1 histdata | Năm phủ ≥ 95 % | Năm phủ thấp | Lệch close vs MT5 p50/p95 (điểm) | Lệch giờ |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m, r in bc.items():
        if "tu" not in r:
            L.append("| %s | %s ||||||||" % (m, r.get("trang_thai"))); continue
        tn = r["theo_nam"]
        tot = [y for y, v in tn.items() if v["phu_pct"] >= 95]
        thap = ["%s (%.0f%%)" % (y, v["phu_pct"]) for y, v in tn.items() if v["phu_pct"] < 95]
        dc = r.get("doi_chieu_mt5") or {}
        L.append("| %s | %s | %s | %d | %d | %s | %s | %s / %s | %s |" % (
            m, r["tu"][:10], r["den"][:10], r["nguon_m1"]["mt5_xm"], r["nguon_m1"]["histdata"],
            ("%s–%s (%d)" % (tot[0], tot[-1], len(tot))) if tot else "—", ", ".join(thap) or "—",
            dc.get("lech_close_p50_diem", "CHƯA ĐO ĐƯỢC"), dc.get("lech_close_p95_diem", "—"), dc.get("lech_gio_tot", "—")))
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    from nhan.tai_du_lieu import MA
    ap = argparse.ArgumentParser()
    ap.add_argument("--dung", action="store_true")
    ap.add_argument("--ma", nargs="*", default=MA)
    a = ap.parse_args(argv)
    if a.dung:
        bc = dung(a.ma)
        for m, r in bc.items():
            print(m, r.get("tu", r.get("trang_thai")), r.get("den", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
