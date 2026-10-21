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


def hieu_chinh(phu: pd.DataFrame, chuan: pd.DataFrame, lech_gio=range(-3, 4)) -> dict:
    """Hieu chinh nguon phu theo nguon chuan tren doan chung (H1): lech gio (gio) lam lech close nho nhat,
    roi lech gia = median(chuan - phu) sau khi dich gio. Khong du doan chung (< 200 nen H1) -> khong chinh."""
    hp, hc = sang_khung(phu, "1h")["close"], sang_khung(chuan, "1h")["close"]
    tot = None
    for k in lech_gio:
        x = hp.shift(k, freq="1h")
        c = x.index.intersection(hc.index)
        if len(c) < 200:
            continue
        d = float((hc[c] - x[c]).abs().median())
        if tot is None or d < tot[1]:
            tot = (k, d, c)
    if tot is None:
        return {"lech_gio": 0, "lech_gia": 0.0, "so_nen_chung": 0, "da_chinh": False}
    k, _, c = tot
    x = hp.shift(k, freq="1h")
    lg = float((hc[c] - x[c]).median())
    sau = float((hc[c] - (x[c] + lg)).abs().median())
    return {"lech_gio": int(k), "lech_gia": lg, "so_nen_chung": int(len(c)), "lech_sau_chinh_p50": sau, "da_chinh": True}


def ap_hieu_chinh(df: pd.DataFrame, hc: dict) -> pd.DataFrame:
    if not hc.get("da_chinh"):
        return df
    x = df + hc["lech_gia"]
    x.index = df.index + pd.Timedelta(hours=hc["lech_gio"])
    return x


def la_xm(ten_server: str) -> bool:
    return "XM" in ten_server.upper()


def nguon_theo_nam(nguon: pd.Series) -> dict:
    """nguon: Series (index thoi gian M5, gia tri ten nguon) -> {nam: {nguon: % nen}}."""
    ra = {}
    for y, s in nguon.groupby(nguon.index.year):
        v = s.value_counts(normalize=True)
        ra[str(y)] = {k: round(100 * float(p), 1) for k, p in v.items()}
    return ra


def gop_nhieu(nguon: list[tuple[str, pd.DataFrame]]) -> tuple[pd.DataFrame, pd.Series, dict]:
    """nguon: [(ten, m1)] theo thu tu UU TIEN (XM truoc). Nguon sau duoc hieu chinh (gio + gia) theo phan da gop, chi lap
    cho trong. Tra (m1, ten nguon moi nen, hieu chinh)."""
    m1, ten, hcs = None, None, {}
    for t, df in nguon:
        if df is None or not len(df):
            continue
        df = df.sort_index()
        if m1 is None:
            m1, ten = df, pd.Series(t, index=df.index); hcs[t] = {"chuan": True}; continue
        hc = hieu_chinh(df, m1); hcs[t] = hc
        df = ap_hieu_chinh(df, hc)
        moi = df[~df.index.isin(m1.index)]
        m1 = pd.concat([m1, moi]).sort_index()
        ten = pd.concat([ten, pd.Series(t, index=moi.index)]).sort_index()
    if m1 is None:
        return pd.DataFrame(columns=["open", "high", "low", "close"]), pd.Series(dtype=str), {}
    m1 = m1[~m1.index.duplicated(keep="first")]; ten = ten[~ten.index.duplicated(keep="first")]
    return m1, ten, hcs


def dung(ma: list[str], thu: Path = THU) -> dict:
    (thu / "m5").mkdir(parents=True, exist_ok=True); RA.mkdir(parents=True, exist_ok=True)
    ban_do, bc = {}, {}
    sv = sorted((thu / "mt5").glob("*")) if (thu / "mt5").exists() else []
    sv = sorted(sv, key=lambda p: (not la_xm(p.name), p.name))          # XM uu tien
    for m in ma:
        ds = [("MT5:" + s.name, doc_mt5_m1(s / m)) for s in sv if (s / m).exists()]
        hz = sorted((thu / "histdata").glob("%s_M1_*.zip" % m))
        if hz:
            ds.append(("histdata", pd.concat([doc_histdata_zip(f) for f in hz])))
        m1, ten, hcs = gop_nhieu(ds)
        if not len(m1):
            bc[m] = {"trang_thai": "CHƯA CÓ DỮ LIỆU"}; continue
        m5 = sang_khung(m1)
        t5 = ten.groupby(ten.index.floor("5min")).first().reindex(m5.index)
        out = thu / "m5" / ("%s_m5_server.csv" % m.lower())
        m5.to_csv(out, index_label="time", float_format="%.6f")
        ban_do[m] = str(out)
        h1 = sang_khung(m1, "1h")
        bc[m] = {"tu": str(m5.index[0]), "den": str(m5.index[-1]), "so_m5": int(len(m5)),
                 "nguon_m1": {t: int(len(d)) for t, d in ds}, "hieu_chinh": hcs, "nguon_theo_nam": nguon_theo_nam(t5.dropna()),
                 "theo_nam": phu_song(m5), "doi_chieu_mt5": lech_mt5(h1, m)}
        del ds, m1, m5, h1
    (thu / "du_lieu_dai.json").write_text(json.dumps(ban_do, indent=1), encoding="utf-8")
    (RA / "PHU_SONG.json").write_text(json.dumps(bc, ensure_ascii=False, indent=1), encoding="utf-8")
    (RA / "PHU_SONG.md").write_text(ghi_md(bc), encoding="utf-8")
    return bc


def ghi_md(bc: dict) -> str:
    L = ["# Độ phủ dữ liệu dài (tự sinh bởi `python -m nhan.du_lieu_dai --dung`)", "",
         "| Mã | Từ | Đến | Nến M1 theo nguồn | Hiệu chỉnh (giờ / giá) | Năm phủ ≥ 95 % | Năm phủ thấp | Lệch close vs MT5 p50/p95 (điểm) | Lệch giờ |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m, r in bc.items():
        if "tu" not in r:
            L.append("| %s | %s ||||||||" % (m, r.get("trang_thai"))); continue
        tn = r["theo_nam"]
        tot = [y for y, v in tn.items() if v["phu_pct"] >= 95]
        thap = ["%s (%.0f%%)" % (y, v["phu_pct"]) for y, v in tn.items() if v["phu_pct"] < 95]
        dc = r.get("doi_chieu_mt5") or {}
        hc = "; ".join("%s %+d h / %+.5g" % (t, h["lech_gio"], h["lech_gia"]) for t, h in r.get("hieu_chinh", {}).items()
                       if h.get("da_chinh")) or "—"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s |" % (
            m, r["tu"][:10], r["den"][:10], ", ".join("%s: %d" % kv for kv in r["nguon_m1"].items()), hc,
            ("%s–%s (%d)" % (tot[0], tot[-1], len(tot))) if tot else "—", ", ".join(thap) or "—",
            dc.get("lech_close_p50_diem", "CHƯA ĐO ĐƯỢC"), dc.get("lech_close_p95_diem", "—"), dc.get("lech_gio_tot", "—")))
    L += ["", "## Nguồn theo năm (% nến M5)", "", "| Mã | Năm: nguồn % |", "|---|---|"]
    for m, r in bc.items():
        if r.get("nguon_theo_nam"):
            L.append("| %s | %s |" % (m, "; ".join("%s: %s" % (y, ", ".join("%s %.0f%%" % kv for kv in v.items()))
                                                   for y, v in r["nguon_theo_nam"].items())))
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
