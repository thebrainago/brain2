# -*- coding: utf-8 -*-
"""Dựng tín hiệu từ tick/flow/big-trade GCZ6. Không lookahead: tín hiệu gắn vào nến chứa sự kiện."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

CHI_PHI_MOT_CHIEU_GIA = 0.105  # 10.5 pts * 0.01 (nửa spread 20 + trượt 0.5)
CHI_PHI_RT_GIA = 0.21          # vòng tròn, 1 lot CFD
POINT = 0.01
TICK_USD = 1.0  # 1 point = $1 / 1.00 lot


def tai_nen_cfd_va_basis(thu_gc: Path, xm_m1: Path) -> pd.DataFrame:
    """Ghép nến 1m GC (UTC) với GOLD.i# (máy chủ Europe/Athens) → giá CFD + basis từng phút."""
    gc = pd.read_csv(thu_gc / "gcz6_1m.csv")
    gc["time"] = pd.to_datetime(gc["open_utc"], utc=True)
    gc = gc.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    xm = pd.read_csv(xm_m1)
    xm["time"] = (
        pd.to_datetime(xm["time"])
        .dt.tz_localize("Europe/Athens", ambiguous="infer", nonexistent="shift_forward")
        .dt.tz_convert("UTC")
    )
    xm = xm.rename(columns={
        "open": "cfd_open", "high": "cfd_high", "low": "cfd_low",
        "close": "cfd_close", "spread": "spread_xm",
    })
    m = pd.merge(
        gc[["time", "open", "high", "low", "close", "volume", "open_ms"]],
        xm[["time", "cfd_open", "cfd_high", "cfd_low", "cfd_close", "spread_xm", "tick_volume"]],
        on="time", how="left",
    )
    m["basis"] = m["close"] - m["cfd_close"]
    # điền basis: ffill/bfill rồi dùng GC - basis cho phút thiếu CFD
    m["basis"] = m["basis"].ffill().bfill()
    thieu = m["cfd_close"].isna()
    m.loc[thieu, "cfd_close"] = m.loc[thieu, "close"] - m.loc[thieu, "basis"]
    m.loc[thieu, "cfd_open"] = m.loc[thieu, "open"] - m.loc[thieu, "basis"]
    m.loc[thieu, "cfd_high"] = m.loc[thieu, "high"] - m.loc[thieu, "basis"]
    m.loc[thieu, "cfd_low"] = m.loc[thieu, "low"] - m.loc[thieu, "basis"]
    m["spread"] = m["spread_xm"].fillna(20.0)
    m["gio"] = m["time"].dt.tz_convert("Europe/Athens").dt.hour
    return m


def dung_vwap_poc(m: pd.DataFrame) -> pd.DataFrame:
    """VWAP / POC phiên COMEX: 18:00 America/New_York → 17:00 hôm sau."""
    m = m.copy()
    ny = m["time"].dt.tz_convert("America/New_York")
    # phiên bắt đầu 18:00 NY: dịch 6 giờ để cut date
    m["phien"] = (ny - pd.Timedelta(hours=18)).dt.strftime("%Y-%m-%d")
    typ = m["close"].astype(float)
    vol = m["volume"].astype(float).clip(lower=0)
    tp = typ * vol
    m["vwap"] = tp.groupby(m["phien"]).cumsum() / vol.groupby(m["phien"]).cumsum().replace(0, np.nan)
    # POC phiên: giá (làm tròn 0.1) có tổng volume lớn nhất tới nến hiện tại — dùng POC đóng phiên trước (không lookahead)
    px_r = (m["close"] / 0.1).round() * 0.1
    poc_cuoi = {}
    poc = np.full(len(m), np.nan)
    # POC cả phiên tại cuối ngày, gắn sang phiên sau
    for ph, g in m.groupby("phien", sort=False):
        idx = g.index.to_numpy()
        # volume theo bin giá trong phiên
        bins = (g["close"] / 0.1).round() * 0.1
        vol_bin = g.assign(_b=bins).groupby("_b")["volume"].sum()
        if len(vol_bin) and vol_bin.max() > 0:
            poc_cuoi[ph] = float(vol_bin.idxmax())
        poc[idx] = poc_cuoi.get(ph, np.nan)
    m["poc_phien"] = poc
    # POC phiên trước (dùng làm mức)
    phien_unique = m["phien"].unique()
    prev = {}
    last = np.nan
    for p in phien_unique:
        prev[p] = last
        last = poc_cuoi.get(p, last)
    m["poc_truoc"] = m["phien"].map(prev)
    return m


def tin_vwap_poc(m: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tín hiệu cắt VWAP / bật từ POC phiên trước. Gắn vào nến đóng."""
    m = dung_vwap_poc(m)
    c = m["cfd_close"].to_numpy()
    o = m["cfd_open"].to_numpy()
    vwap = m["vwap"].to_numpy()
    poc = m["poc_truoc"].to_numpy()
    ev = {}

    # cắt lên / xuống VWAP
    lenh = []
    for i in range(1, len(m)):
        if not np.isfinite(vwap[i - 1]) or not np.isfinite(vwap[i]):
            continue
        if c[i - 1] < vwap[i - 1] and c[i] >= vwap[i]:
            lenh.append((m["time"].iloc[i], 1, float(c[i]), "vwap_cat_len"))
        elif c[i - 1] > vwap[i - 1] and c[i] <= vwap[i]:
            lenh.append((m["time"].iloc[i], -1, float(c[i]), "vwap_cat_xuong"))
    ev["vwap_cat"] = _df_ev(lenh)

    # từ chối VWAP: đi xuyên rồi đóng lại cùng phía nến trước
    lenh = []
    h = m["cfd_high"].to_numpy()
    l = m["cfd_low"].to_numpy()
    for i in range(1, len(m)):
        if not np.isfinite(vwap[i]):
            continue
        if l[i] <= vwap[i] <= c[i] and c[i - 1] > vwap[i]:
            lenh.append((m["time"].iloc[i], 1, float(c[i]), "vwap_tu_choi_duoi"))
        elif h[i] >= vwap[i] >= c[i] and c[i - 1] < vwap[i]:
            lenh.append((m["time"].iloc[i], -1, float(c[i]), "vwap_tu_choi_tren"))
    ev["vwap_tu_choi"] = _df_ev(lenh)

    # chạm POC phiên trước rồi đóng về hướng bật
    lenh = []
    for i in range(1, len(m)):
        if not np.isfinite(poc[i]):
            continue
        if l[i] <= poc[i] <= h[i]:
            if c[i] > poc[i] and c[i] >= o[i]:
                lenh.append((m["time"].iloc[i], 1, float(c[i]), "poc_bat_len"))
            elif c[i] < poc[i] and c[i] <= o[i]:
                lenh.append((m["time"].iloc[i], -1, float(c[i]), "poc_bat_xuong"))
    ev["poc_bat"] = _df_ev(lenh)
    return ev, m


def _df_ev(rows):
    if not rows:
        return pd.DataFrame(columns=["time", "huong", "gia", "loai"])
    return pd.DataFrame(rows, columns=["time", "huong", "gia", "loai"])


def cum_big_trade(big: pd.DataFrame, min_vol=20, cua_so_ms=60_000, n_min=3, band=0.5) -> pd.DataFrame:
    """Cụm big-trade cùng chiều, trong cửa sổ, gần cùng giá. Mốc = lệnh cuối cụm."""
    df = big.copy()
    if "time_ms" not in df.columns and "time" in df.columns:
        df["time_ms"] = (pd.to_datetime(df["time"], utc=True).astype("int64") // 10**6)
    df = df[df["vol"] >= min_vol].sort_values("time_ms").reset_index(drop=True)
    if df.empty:
        return _df_ev([])
    t = df["time_ms"].to_numpy()
    side = df["side"].to_numpy()
    vol = df["vol"].to_numpy()
    # giá đại diện
    if "last_px" in df.columns:
        px = df["last_px"].to_numpy()
    elif "first_px" in df.columns:
        px = df["first_px"].to_numpy()
    else:
        px = np.zeros(len(df))
    used = np.zeros(len(df), dtype=bool)
    rows = []
    for i in range(len(df)):
        if used[i]:
            continue
        hu = 1 if side[i] == "B" else -1
        members = [i]
        tong = float(vol[i])
        j = i + 1
        while j < len(df) and t[j] - t[i] <= cua_so_ms:
            if (not used[j]) and side[j] == side[i] and abs(px[j] - px[i]) <= band:
                members.append(j)
                tong += float(vol[j])
            j += 1
        if len(members) >= n_min or tong >= min_vol * n_min:
            for k in members:
                used[k] = True
            kcuoi = members[-1]
            tm = pd.to_datetime(int(t[kcuoi]), unit="ms", utc=True)
            rows.append((tm, hu, float(px[kcuoi]), f"cum_v{min_vol}_w{cua_so_ms//1000}_n{len(members)}_s{int(tong)}"))
    return _df_ev(rows)


def quet_dao_1m(m: pd.DataFrame, n=30) -> pd.DataFrame:
    """Quét đỉnh/đáy N nến rồi đóng trở lại trong biên — đảo chiều."""
    h = m["cfd_high"].to_numpy()
    l = m["cfd_low"].to_numpy()
    c = m["cfd_close"].to_numpy()
    rows = []
    for i in range(n, len(m)):
        mx = h[i - n:i].max()
        mn = l[i - n:i].min()
        if h[i] > mx and c[i] <= mx:
            rows.append((m["time"].iloc[i], -1, float(c[i]), f"quet_dinh_{n}"))
        if l[i] < mn and c[i] >= mn:
            rows.append((m["time"].iloc[i], 1, float(c[i]), f"quet_day_{n}"))
    return _df_ev(rows)


def su_kien_flow(flow: dict, loai: str, min_vol=5) -> pd.DataFrame:
    """Sweep / absorption / iceberg / cum-sweep từ flowRecs, lọc size."""
    rows = []
    if loai == "sw":
        for e in flow.get("sw") or []:
            # [ms, side, n?, px0, px1, vol, ...]
            vol = e[5] if len(e) > 5 else 0
            nlv = e[2] if len(e) > 2 else 0
            if vol < min_vol and nlv < min_vol:
                continue
            hu = 1 if e[1] == "S" else -1  # quét bid (S) → kỳ vọng đảo lên
            tm = pd.to_datetime(int(e[0]), unit="ms", utc=True)
            rows.append((tm, hu, float(e[3]), "sw_dao"))
    elif loai == "cs":
        for e in flow.get("cs") or []:
            vol = e[4] if len(e) > 4 else 1
            if vol < 2 and (e[2] if len(e) > 2 else 0) < 2:
                # giữ cs vì đã là cumulative (hiếm hơn)
                pass
            hu = 1 if e[1] == "S" else -1
            tm = pd.to_datetime(int(e[0]), unit="ms", utc=True)
            px = float(e[3]) if len(e) > 3 else np.nan
            rows.append((tm, hu, px, "cs_dao"))
    elif loai == "ab":
        for e in flow.get("ab") or []:
            vol = e.get("vol", 0)
            cnt = e.get("count", 0)
            if vol < min_vol and cnt < 4:
                continue
            # hấp thụ lệnh S (bán chủ động) → hỗ trợ mua
            hu = 1 if e.get("side") == "S" else -1
            tm = pd.to_datetime(int(e["ms"]), unit="ms", utc=True)
            rows.append((tm, hu, float(e.get("price") or 0), "ab"))
    elif loai == "ice":
        for e in flow.get("ice") or []:
            if (e.get("hidden") or 0) < 3 and (e.get("filled") or 0) < 8:
                continue
            hu = 1 if e.get("side") == "B" else -1  # iceberg mua = hỗ trợ
            tm = pd.to_datetime(int(e.get("lastMs") or e.get("firstMs")), unit="ms", utc=True)
            rows.append((tm, hu, float(e.get("price") or 0), "ice"))
    return _df_ev(rows)


def dung_footprint_1m(tick_csv: Path, m: pd.DataFrame) -> pd.DataFrame:
    """Từ tick aggTrades: delta, CVD, POC nến. Gộp theo phút UTC. CVD cộng dồn theo thời gian."""
    usecols = ["time_ms", "price", "qty", "side"]
    parts = []
    poc_parts = []
    for ch in pd.read_csv(tick_csv, usecols=usecols, chunksize=1_000_000):
        ch = ch.dropna(subset=["time_ms", "price", "qty"])
        ch["buy"] = np.where(ch["side"] == "B", ch["qty"], 0.0)
        ch["sell"] = np.where(ch["side"] == "S", ch["qty"], 0.0)
        ch["phut_ms"] = (ch["time_ms"].astype("int64") // 60_000) * 60_000
        ch["pxq"] = ch["price"] * ch["qty"]
        g = ch.groupby("phut_ms", sort=True).agg(
            buy=("buy", "sum"), sell=("sell", "sum"),
            vol=("qty", "sum"), pxq=("pxq", "sum"),
        )
        parts.append(g.reset_index())
        ch["bin"] = (ch["price"] / 0.1).round() * 0.1
        bv = ch.groupby(["phut_ms", "bin"], sort=False)["qty"].sum().reset_index()
        poc_parts.append(bv)
    fp = pd.concat(parts, ignore_index=True).groupby("phut_ms", sort=True).sum()
    fp["delta"] = fp["buy"] - fp["sell"]
    fp["cvd"] = fp["delta"].cumsum()
    fp["vwap_nen"] = fp["pxq"] / fp["vol"].replace(0, np.nan)
    poc_all = pd.concat(poc_parts, ignore_index=True).groupby(["phut_ms", "bin"], sort=False)["qty"].sum().reset_index()
    idx = poc_all.groupby("phut_ms")["qty"].idxmax()
    poc = poc_all.loc[idx, ["phut_ms", "bin"]].rename(columns={"bin": "poc_nen"})
    fp = fp.reset_index().merge(poc, on="phut_ms", how="left").rename(columns={"phut_ms": "open_ms"})
    out = m.merge(fp[["open_ms", "buy", "sell", "delta", "cvd", "vol", "vwap_nen", "poc_nen"]], on="open_ms", how="left", suffixes=("", "_tick"))
    out["delta"] = out["delta"].fillna(0.0)
    out["cvd"] = out["cvd"].ffill().fillna(0.0)
    return out


def tin_cvd_phan_ky(m_fp: pd.DataFrame, n=30) -> pd.DataFrame:
    """Phân kỳ CVD: giá đỉnh mới, CVD không — bán; giá đáy mới, CVD không — mua."""
    if "cvd" not in m_fp.columns:
        return _df_ev([])
    h = m_fp["cfd_high"].to_numpy()
    l = m_fp["cfd_low"].to_numpy()
    cvd = m_fp["cvd"].to_numpy()
    c = m_fp["cfd_close"].to_numpy()
    rows = []
    for i in range(n, len(m_fp)):
        if not np.isfinite(cvd[i]):
            continue
        if h[i] >= np.nanmax(h[i - n:i]) and cvd[i] < np.nanmax(cvd[i - n:i]):
            rows.append((m_fp["time"].iloc[i], -1, float(c[i]), f"cvd_div_dinh_{n}"))
        if l[i] <= np.nanmin(l[i - n:i]) and cvd[i] > np.nanmin(cvd[i - n:i]):
            rows.append((m_fp["time"].iloc[i], 1, float(c[i]), f"cvd_div_day_{n}"))
    return _df_ev(rows)


def tin_delta_chao(m_fp: pd.DataFrame, k=2.0) -> pd.DataFrame:
    """Delta nến vượt k * σ(20) cùng chiều đóng cửa."""
    if "delta" not in m_fp.columns:
        return _df_ev([])
    d = m_fp["delta"].to_numpy()
    c = m_fp["cfd_close"].to_numpy()
    o = m_fp["cfd_open"].to_numpy()
    s = pd.Series(d).rolling(20, min_periods=10).std().to_numpy()
    rows = []
    for i in range(20, len(m_fp)):
        if not np.isfinite(s[i]) or s[i] <= 0:
            continue
        if d[i] >= k * s[i] and c[i] >= o[i]:
            rows.append((m_fp["time"].iloc[i], 1, float(c[i]), "delta_mua"))
        elif d[i] <= -k * s[i] and c[i] <= o[i]:
            rows.append((m_fp["time"].iloc[i], -1, float(c[i]), "delta_ban"))
    return _df_ev(rows)
