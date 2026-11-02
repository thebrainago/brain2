# -*- coding: utf-8 -*-
"""Đọc lịch sử lệnh: MT4 statement HTML, MT5 report HTML, MQL5 signal CSV, Myfxbook CSV, CSV chung.
Kết quả: DataFrame chuẩn [mo_luc, dong_luc, chieu(buy/sell), lot, symbol, gia_mo, gia_dong, sl, tp, loi_nhuan]."""
from __future__ import annotations
import io, re
import pandas as pd

COT = ["mo_luc", "dong_luc", "chieu", "lot", "symbol", "gia_mo", "gia_dong", "sl", "tp", "loi_nhuan"]
# ánh xạ tên cột (chữ thường, bỏ khoảng trắng) -> cột chuẩn; cột lặp (Time/Price lần 2) xử lý theo thứ tự
BIET = {"opentime": "mo_luc", "opendate": "mo_luc", "time": "mo_luc", "closetime": "dong_luc", "closedate": "dong_luc",
        "type": "chieu", "action": "chieu", "direction": "chieu", "size": "lot", "lots": "lot", "volume": "lot",
        "item": "symbol", "symbol": "symbol", "openprice": "gia_mo", "price": "gia_mo", "closeprice": "gia_dong",
        "s/l": "sl", "sl": "sl", "t/p": "tp", "tp": "tp", "profit": "loi_nhuan"}


def _chuan(df: pd.DataFrame) -> pd.DataFrame:
    ten, da = [], set()
    for c in df.columns:
        k = re.sub(r"[\s_]+", "", str(c).strip().lower()).split(".")[0]
        m = BIET.get(k)
        if m in da:      # lần thứ hai của Time/Price -> đóng
            m = {"mo_luc": "dong_luc", "gia_mo": "gia_dong"}.get(m)
        if m in da:
            m = None
        ten.append(m or f"_{c}"); da.add(m)
    df = df.copy(); df.columns = ten
    for c in COT:
        if c not in df: df[c] = None
    df = df[COT]
    df["chieu"] = df["chieu"].astype(str).str.lower().str.extract(r"(buy|sell)", expand=False)
    df = df[df["chieu"].notna()].copy()
    for c in ("mo_luc", "dong_luc"):
        df[c] = pd.to_datetime(df[c].astype(str).str.replace(".", "-", regex=False), errors="coerce")
    for c in ("lot", "gia_mo", "gia_dong", "sl", "tp", "loi_nhuan"):
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(" ", "").str.replace(",", ""), errors="coerce")
    df["symbol"] = df["symbol"].astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    df = df.dropna(subset=["mo_luc", "lot", "gia_mo"])
    return df.sort_values("mo_luc").reset_index(drop=True)


def doc(duong_dan_hoac_chuoi: str) -> pd.DataFrame:
    s = duong_dan_hoac_chuoi
    if "\n" not in s:
        raw = open(s, "rb").read()
        s = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    if "<table" in s.lower():
        bang = pd.read_html(io.StringIO(s), header=None)
        tot = None
        for b in bang:
            # tìm hàng tiêu đề có "Type" và ("Size" hoặc "Volume")
            for i in range(min(len(b), 60)):
                hang = [str(x) for x in b.iloc[i].tolist()]
                hl = [h.lower() for h in hang]
                if "type" in hl and ("size" in hl or "volume" in hl):
                    d = b.iloc[i + 1:].copy(); d.columns = [h if h != "nan" else f"c{j}" for j, h in enumerate(hang)]
                    d = _chuan(d)
                    if tot is None or len(d) > len(tot): tot = d
                    break
        if tot is None:
            raise ValueError("Không tìm thấy bảng lệnh trong HTML")
        return tot
    sep = ";" if s.splitlines()[0].count(";") > s.splitlines()[0].count(",") else ","
    if "\t" in s.splitlines()[0]: sep = "\t"
    return _chuan(pd.read_csv(io.StringIO(s), sep=sep))
