#!/usr/bin/env python3
"""Kiểm chất lượng kho dữ liệu chuẩn -> reports/chat_luong_du_lieu_chuan.md.

Theo mã/năm: % phút thiếu trong giờ giao dịch, số gap > 30 phút, gap dài nhất, giá nhảy bất thường,
spread âm. "Giờ giao dịch" xác định từ CHÍNH dữ liệu: ô (thứ, giờ UTC) có tick ở >= 50 % số tuần
trong năm; ngày có < 20 % số phút trung vị coi là ngày nghỉ/ngắn (đếm riêng, không tính thiếu).
So khớp D1 (UTC) với Yahoo (đóng cửa, lệch %) và M1 EURUSD với mẫu tick Exness 2024-01.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import du_lieu_chuan as D

YAHOO = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X",
         "NZDUSD": "NZDUSD=X", "USDCAD": "CAD=X", "USDCHF": "CHF=X", "EURJPY": "EURJPY=X",
         "EURGBP": "EURGBP=X", "GBPJPY": "GBPJPY=X", "XAUUSD": "GC=F", "XAGUSD": "SI=F",
         "LIGHT.CMD": "CL=F", "BRENT.CMD": "BZ=F", "USA500.IDX": "^GSPC", "USATECH.IDX": "^NDX",
         "DEU.IDX": "^GDAXI", "GBR.IDX": "^FTSE", "JPN.IDX": "^N225"}
EXNESS = Path("/tmp/ex/Exness_EURUSD_2024_01.csv")
RA = Path(__file__).with_name("reports") / "chat_luong_du_lieu_chuan.md"


def kiem_nam(m1: pd.DataFrame) -> dict:
    idx = m1.index
    ngay = idx.normalize()
    phut_ngay = pd.Series(1, index=idx).groupby(ngay).size()
    nguong = 0.2 * phut_ngay.median()
    ngay_ngan = set(phut_ngay[phut_ngay < nguong].index)
    tuan = idx.to_period("W").astype(str)
    o = pd.DataFrame({"wd": idx.weekday, "h": idx.hour, "tuan": tuan}).drop_duplicates()
    so_tuan = len(set(tuan))
    ty_le = o.groupby(["wd", "h"]).size() / so_tuan
    o_mo = set(ty_le[ty_le >= 0.5].index)
    # lưới phút kỳ vọng
    ngay_tot = [d for d in phut_ngay.index if d not in ngay_ngan]
    if not ngay_tot:
        return {}
    luoi = pd.date_range(min(ngay_tot), max(ngay_tot) + pd.Timedelta(days=1), freq="1min", inclusive="left")
    luoi = luoi[luoi.normalize().isin(ngay_tot)]
    k = pd.MultiIndex.from_arrays([luoi.weekday, luoi.hour])
    luoi = luoi[k.isin(list(o_mo))]
    co = luoi.isin(idx)
    thieu_pct = 100 * (1 - co.mean()) if len(luoi) else float("nan")
    # gap trong giờ mở
    thieu = pd.Series(~co, index=luoi)
    nhom = (thieu != thieu.shift()).cumsum()
    do_dai = thieu[thieu].groupby(nhom[thieu]).size()
    mid = (m1["bid_c"] + m1["ask_c"]) / 2
    r = np.log(mid).diff().dropna()
    mad = (r - r.median()).abs().median() * 1.4826
    nhay = r[(r.abs() > 15 * mad) & (r.abs() > 0.005)]
    return {"so_phut": len(m1), "ngay_ngan": len(ngay_ngan), "thieu_pct": thieu_pct,
            "gap30": int((do_dai > 30).sum()), "gap_max": int(do_dai.max()) if len(do_dai) else 0,
            "nhay": len(nhay), "nhay_max_pct": 100 * float(r.abs().max()),
            "spread_am": int((m1["spread_min"] < 0).sum()),
            "ask_lt_bid_ohlc": int(((m1["ask_l"] < m1["bid_l"]) | (m1["ask_h"] < m1["bid_h"])).sum()),
            "spread_tv": float(m1["spread_tb"].median()), "tick_tb": float(m1["so_tick"].mean()),
            "dau": idx[0], "cuoi": idx[-1]}


def so_yahoo(ma: str) -> dict:
    try:
        import yfinance as yf
        d1 = D.doc(ma, "D1")
        y = yf.download(YAHOO[ma], start=str(d1.index[0].date()), progress=False, auto_adjust=False)
        if y.empty:
            return {"loi": "Yahoo rỗng"}
        yc = y["Close"].squeeze()
        yc.index = pd.to_datetime(yc.index).tz_localize(None)
        dc = d1["close"].copy()
        dc.index = dc.index.tz_localize(None)
        j = pd.concat([dc.rename("d"), yc.rename("y")], axis=1).dropna()
        j = j[j.index.weekday < 5]
        lech = (j["d"] / j["y"] - 1).abs() * 100
        rr = np.log(j).diff().dropna()
        return {"n": len(j), "lech_tv": lech.median(), "lech_p95": lech.quantile(0.95),
                "tuong_quan_ln": rr["d"].corr(rr["y"]),
                "ty_le_tv": float((j["d"] / j["y"]).median())}
    except Exception as e:  # noqa: BLE001
        return {"loi": f"{type(e).__name__}: {e}"[:120]}


def so_exness() -> dict:
    if not EXNESS.exists():
        return {"loi": "không có file mẫu Exness"}
    try:
        m = D.doc("EURUSD", "M1", "2024-01-01", "2024-01-31", gia="tat_ca")
    except FileNotFoundError:
        return {"loi": "chưa có EURUSD 2024-01 trong kho chuẩn"}
    e = pd.read_csv(EXNESS, usecols=["Timestamp", "Bid", "Ask"])
    e.index = pd.to_datetime(e.pop("Timestamp"), utc=True)
    g = e.groupby(e.index.floor("1min"))
    em = pd.DataFrame({"c": (g["Bid"].last() + g["Ask"].last()) / 2,
                       "sp": (e["Ask"] - e["Bid"]).groupby(e.index.floor("1min")).mean(), "n": g.size()})
    j = pd.concat([m[["mid_c", "spread_tb", "so_tick"]], em], axis=1).dropna()
    lech_pip = ((j["mid_c"] - j["c"]).abs() * 1e4)
    return {"n_phut": len(j), "phut_duka": len(m), "phut_exness": len(em),
            "lech_close_pip_tv": lech_pip.median(), "lech_close_pip_p99": lech_pip.quantile(0.99),
            "spread_duka_pip_tv": j["spread_tb"].median() * 1e4, "spread_exness_pip_tv": j["sp"].median() * 1e4,
            "tick_duka_tb": j["so_tick"].mean(), "tick_exness_tb": j["n"].mean(),
            "tq_ln_m1": np.log(j["mid_c"]).diff().corr(np.log(j["c"]).diff())}


def main():
    dong = [f"# Chất lượng kho dữ liệu chuẩn (Dukascopy tick → M1)\n",
            f"Sinh lúc {dt.datetime.now():%Y-%m-%d %H:%M} (giờ Bangkok) bởi `kiem_chat_luong_du_lieu_chuan.py`. "
            "Chỉ là số đo trên dữ liệu đã có trong kho lúc chạy; mã/năm chưa tải ghi CHƯA ĐO ĐƯỢC.\n",
            "Định nghĩa: *thiếu %* = phút không có tick trong các ô (thứ, giờ UTC) mà ≥ 50 % số tuần của năm có tick, "
            "bỏ các ngày < 20 % số phút trung vị (ngày nghỉ/ngắn, đếm ở cột *ngày ngắn*). *Gap* = chuỗi phút thiếu liên tiếp "
            "> 30 phút trong giờ mở. *Nhảy* = |log-return M1 mid| > 15×MAD và > 0,5 %. *Spread âm* = phút có ask < bid ở một tick.\n"]
    import tai_dukascopy_tick_m1 as T
    ma_co = set(D.ds_ma())
    for ma in T.MA:
        dong.append(f"\n## {ma}\n")
        if ma not in ma_co:
            dong.append("CHƯA ĐO ĐƯỢC (chưa tải).\n")
            continue
        m1 = D._doc_m1(ma, None, None)
        dong.append("| năm | phút | đầu | cuối | ngày ngắn | thiếu % | gap>30' | gap dài nhất (phút) | nhảy | nhảy max % | spread âm | spread trung vị | tick/phút |\n"
                    "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for nam, g in m1.groupby(m1.index.year):
            k = kiem_nam(g)
            if not k:
                continue
            dong.append(f"| {nam} | {k['so_phut']} | {k['dau']:%m-%d %H:%M} | {k['cuoi']:%m-%d %H:%M} | {k['ngay_ngan']} | "
                        f"{k['thieu_pct']:.2f} | {k['gap30']} | {k['gap_max']} | {k['nhay']} | {k['nhay_max_pct']:.2f} | "
                        f"{k['spread_am']} | {k['spread_tv']:.5g} | {k['tick_tb']:.1f} |\n")
        y = so_yahoo(ma)
        if "loi" in y:
            dong.append(f"\nSo Yahoo ({YAHOO[ma]}): CHƯA ĐO ĐƯỢC ({y['loi']}).\n")
        else:
            dong.append(f"\nSo D1 với Yahoo `{YAHOO[ma]}` ({y['n']} ngày chung): lệch close trung vị {y['lech_tv']:.3f} %, "
                        f"p95 {y['lech_p95']:.3f} %, tương quan log-return ngày {y['tuong_quan_ln']:.4f}, "
                        f"tỉ lệ Duka/Yahoo trung vị {y['ty_le_tv']:.4f}. (D1 Duka cắt 00:00 UTC; Yahoo theo giờ sàn/futures "
                        "nên lệch phần lớn do giờ chốt và hợp đồng, không phải lỗi giá.)\n")
    e = so_exness()
    dong.append("\n## So khớp EURUSD M1 với mẫu tick Exness (2024-01)\n")
    if "loi" in e:
        dong.append(f"CHƯA ĐO ĐƯỢC ({e['loi']}).\n")
    else:
        dong.append(f"Phút chung {e['n_phut']} (Duka {e['phut_duka']}, Exness {e['phut_exness']}). Lệch close mid: trung vị "
                    f"{e['lech_close_pip_tv']:.2f} pip, p99 {e['lech_close_pip_p99']:.2f} pip; tương quan log-return M1 "
                    f"{e['tq_ln_m1']:.4f}. Spread trung vị Duka {e['spread_duka_pip_tv']:.2f} pip vs Exness "
                    f"{e['spread_exness_pip_tv']:.2f} pip; tick/phút Duka {e['tick_duka_tb']:.1f} vs Exness {e['tick_exness_tb']:.1f}.\n")
    RA.write_text("".join(dong), encoding="utf-8")
    print(RA)


if __name__ == "__main__":
    main()
