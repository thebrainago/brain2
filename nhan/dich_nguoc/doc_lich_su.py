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
    tho = df["chieu"].astype(str).str.lower()
    df["chieu"] = tho.str.extract(r"(buy|sell)", expand=False)
    df.loc[tho.str.contains(r"stop|limit", regex=True), "chieu"] = None     # lệnh chờ (đã hủy/khớp) không phải vị thế
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
    dau = s.lstrip("\ufeff").splitlines()[0]
    if dau.startswith("Time;") and ";Direction;" in dau:
        return doc_deal_mql5(s)
    sep = ";" if s.splitlines()[0].count(";") > s.splitlines()[0].count(",") else ","
    if "\t" in s.splitlines()[0]: sep = "\t"
    return _chuan(pd.read_csv(io.StringIO(s), sep=sep))


def _so(x):
    return pd.to_numeric(pd.Series(x).astype(str).str.replace(r"[\s,]", "", regex=True).replace({"": None, "nan": None}), errors="coerce").fillna(0.0)


def _doc_tho(s: str) -> pd.DataFrame:
    s = s.lstrip("\ufeff")
    return pd.read_csv(io.StringIO(s), sep=";", dtype=str, keep_default_na=False, header=None, skiprows=1)


def doc_deal_mql5(s: str) -> pd.DataFrame:
    """CSV tín hiệu MQL5 dạng DEAL: Time;Symbol;Type;Direction;Volume;Price;Commission;Swap;Profit;Comment.
    Ghép In/Out theo FIFO cho từng symbol + chiều vị thế (deal Out ngược chiều với vị thế)."""
    d = _doc_tho(s).iloc[:, :10]
    d.columns = ["t", "sym", "typ", "dir", "vol", "gia", "com", "swap", "lai", "cmt"]
    d = d[d["dir"].str.lower().isin(["in", "out", "inout"])].copy()
    d["t"] = pd.to_datetime(d["t"].str.replace(".", "-", regex=False), errors="coerce")
    for c in ("vol", "gia", "com", "swap", "lai"):
        d[c] = _so(d[c]).values
    d = d.dropna(subset=["t"]).iloc[::-1].reset_index(drop=True)     # file mới -> cũ; đảo lại
    d = d.sort_values("t", kind="stable")
    mo: dict = {}; ra = []
    for r in d.itertuples():
        sym = re.sub(r"[^A-Z0-9]", "", r.sym.upper()); typ = r.typ.lower()
        if r.dir.lower() == "in":
            mo.setdefault((sym, typ), []).append({"mo_luc": r.t, "chieu": typ, "lot": r.vol, "con": r.vol, "symbol": sym,
                                                  "gia_mo": r.gia, "loi_nhuan": r.com + r.swap, "dong": []})
            continue
        vt = "buy" if typ == "sell" else "sell"; q = mo.get((sym, vt), []); con = r.vol
        while con > 1e-9 and q:
            x = q[0]; k = min(con, x["con"]); x["con"] -= k; con -= k
            x["dong"].append((r.t, r.gia, k)); x["loi_nhuan"] += (r.lai + r.com + r.swap) * k / max(r.vol, 1e-12)
            if x["con"] <= 1e-9:
                q.pop(0); v = sum(z[2] for z in x["dong"])
                ra.append({"mo_luc": x["mo_luc"], "dong_luc": x["dong"][-1][0], "chieu": x["chieu"], "lot": x["lot"],
                           "symbol": sym, "gia_mo": x["gia_mo"], "gia_dong": sum(z[1] * z[2] for z in x["dong"]) / v,
                           "sl": None, "tp": None, "loi_nhuan": x["loi_nhuan"]})
    df = pd.DataFrame(ra, columns=COT)
    return df.sort_values("mo_luc").reset_index(drop=True)


def doc_von(duong_dan: str) -> pd.DataFrame:
    """Nạp/rút (Balance) và Credit trong CSV tín hiệu MQL5 (cả hai dạng). Trả [luc, loai, so_tien]."""
    raw = open(duong_dan, "rb").read().decode("utf-8", "replace").lstrip("\ufeff")
    dau = raw.splitlines()[0]; d = _doc_tho(raw)
    if ";Direction;" in dau:
        m = d[d[2].str.lower().isin(["balance", "credit"])]; loai = m[2]; tien = m[8]
    else:
        m = d[d[1].str.lower().isin(["balance", "credit"])]; loai = m[1]
        tien = m.apply(lambda r: next((v for v in reversed(r.tolist()) if re.search(r"\d", str(v))
                                       and not re.match(r"\d{4}\.\d\d\.\d\d", str(v))), "0"), axis=1)
    return pd.DataFrame({"luc": pd.to_datetime(m[0].str.replace(".", "-", regex=False)), "loai": loai.str.lower(),
                         "so_tien": _so(tien).values}).sort_values("luc").reset_index(drop=True)
