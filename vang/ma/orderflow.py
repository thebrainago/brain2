# -*- coding: utf-8 -*-
"""Backtest lọc order flow Fxaurum (GCZ6) trên cửa sổ ~3 tháng. Chạy: python -m vang.ma.orderflow --thu-muc <đường dẫn csv>."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

from vang.ma import du_lieu, tin_hieu, mo_phong

# 14:00-20:00 VN = 07:00-13:00 UTC = 09:00-15:00 máy chủ XM GMT+2
# Nến GC Fxaurum là UTC.


def tai_gc(thu_muc: Path):
    h1 = thu_muc / "gcz6_1h.csv"
    m1 = thu_muc / "gcz6_1m.csv"
    flow = thu_muc / "gcz6_flow.json"
    big = thu_muc / "gcz6_bigtrades.csv"
    out = {}
    if h1.exists():
        df = pd.read_csv(h1)
        df["time"] = pd.to_datetime(df["open_utc"])
        out["h1"] = df
    if m1.exists():
        df = pd.read_csv(m1)
        df["time"] = pd.to_datetime(df["open_utc"])
        out["m1"] = df
    if flow.exists():
        out["flow"] = json.loads(flow.read_text(encoding="utf-8"))
    if big.exists():
        out["big"] = pd.read_csv(big)
        if "time_utc" in out["big"].columns:
            out["big"]["time"] = pd.to_datetime(out["big"]["time_utc"])
    return out


def do_basis(gc_h1: pd.DataFrame):
    """Basis = GC − CFD, cùng thời điểm. CFD = XM GOLD.i (máy chủ GMT+2 → đổi sang UTC)."""
    cfd, _, _ = du_lieu.tai_khung("H1")
    cfd = cfd.copy()
    cfd["utc"] = pd.to_datetime(cfd["time"]) - pd.Timedelta(hours=2)
    gc = gc_h1.copy()
    gc["utc"] = pd.to_datetime(gc["time"]).dt.tz_localize(None)
    m = pd.merge(
        gc[["utc", "close"]].rename(columns={"close": "gc"}),
        cfd[["utc", "close"]].rename(columns={"close": "cfd"}),
        on="utc", how="inner",
    )
    if m.empty:
        return {"n": 0, "ghi_chu": "Không có đoạn trùng giờ GC và GOLD.i"}
    m["basis"] = m["gc"] - m["cfd"]
    return {
        "n": int(len(m)),
        "tu": str(m["utc"].iloc[0]),
        "den": str(m["utc"].iloc[-1]),
        "basis_trung_vi": float(m["basis"].median()),
        "basis_trung_binh": float(m["basis"].mean()),
        "basis_min": float(m["basis"].min()),
        "basis_max": float(m["basis"].max()),
        "basis_p10": float(m["basis"].quantile(0.1)),
        "basis_p90": float(m["basis"].quantile(0.9)),
    }


def gan_su_kien_len_nen(m1: pd.DataFrame, events: list, col: str, ts_key=0):
    """Đếm sự kiện (time ms hoặc timestamp) theo nến 1 phút."""
    m1 = m1.copy()
    m1[col] = 0
    if not events:
        return m1
    # events: list of list/tuple, phần tử 0 là time_ms
    try:
        ts = []
        sides = []
        for e in events:
            if isinstance(e, dict):
                t = e.get("ms") or e.get("t0") or e.get("firstMs") or e.get("time_ms")
                s = e.get("side", "")
            else:
                t = e[0]
                s = e[1] if len(e) > 1 else ""
            if t is None:
                continue
            ts.append(pd.to_datetime(int(t), unit="ms") if np.asarray(t).ndim == 0 and int(t) > 10**11 else pd.to_datetime(t))
            sides.append(s)
        if not ts:
            return m1
        ev = pd.DataFrame({"time": ts, "side": sides})
        ev["bucket"] = ev["time"].dt.floor("min")
        # chỉ giữ số lượng; chiều: B=+1, S=-1
        ev["dir"] = ev["side"].map({"B": 1, "S": -1}).fillna(0)
        g = ev.groupby("bucket").agg(n=("dir", "size"), d=("dir", "sum"))
        m1 = m1.merge(g, left_on="time", right_index=True, how="left")
        m1[col] = m1["n"].fillna(0).astype(int)
        m1[col + "_dir"] = m1["d"].fillna(0).astype(int)
        m1 = m1.drop(columns=["n", "d"], errors="ignore")
    except Exception as e:
        print("loi gan su kien", col, e, flush=True)
    return m1


def quet_orderflow(thu_muc: Path, out_dir: Path):
    data = tai_gc(thu_muc)
    bao = {"thu_muc": str(thu_muc), "co_file": sorted(p.name for p in thu_muc.glob("*") if p.is_file()) if thu_muc.exists() else []}
    if "h1" not in data and "m1" not in data:
        bao["loi"] = "Chưa có gcz6_1h.csv / gcz6_1m.csv. Đợi keo_fxaurum.py xong rồi chép về."
        print(bao["loi"], flush=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "orderflow_chua_co_data.json").write_text(json.dumps(bao, ensure_ascii=False, indent=2), encoding="utf-8")
        return bao

    if "h1" in data:
        bao["basis"] = do_basis(data["h1"])
        print("BASIS", bao["basis"], flush=True)

    if "m1" not in data:
        bao["ghi_chu_m1"] = "Chưa có nến 1m — chỉ đo được basis từ H1."
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "orderflow_trang_thai.json").write_text(json.dumps(bao, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return bao

    m1 = data["m1"].sort_values("time").reset_index(drop=True)
    # dựng OHLC chuẩn
    df = pd.DataFrame({
        "time": m1["time"],
        "open": m1["open"], "high": m1["high"], "low": m1["low"], "close": m1["close"],
        "spread": 20.0,  # điểm M1 trung vị XM
    })
    # thêm giờ UTC và VN
    t = pd.to_datetime(df["time"])
    if t.dt.tz is not None:
        t = t.dt.tz_convert("UTC").dt.tz_localize(None)
    df["gio"] = t.dt.hour  # UTC
    df["gio_vn"] = (t + pd.Timedelta(hours=7)).dt.hour
    df["thu"] = t.dt.dayofweek
    df["thang"] = t.dt.month
    df["ngay"] = t.dt.day

    if "flow" in data:
        fl = data["flow"]
        m1 = gan_su_kien_len_nen(m1, fl.get("sw") or [], "sweep")
        m1 = gan_su_kien_len_nen(m1, fl.get("ab") or [], "absorp")
        m1 = gan_su_kien_len_nen(m1, fl.get("ice") or [], "ice")
        bao["dem_flow"] = {k: len(fl.get(k) or []) for k in ("sw", "ab", "ice", "cs")}
    if "big" in data:
        bao["dem_big"] = int(len(data["big"]))

    # tín hiệu ORB London theo giờ VN 14-20 (UTC 7-13)
    sig_orb = tin_hieu.tin_vao(df.assign(gio=df["gio_vn"]), "orb_london_anh")  # dùng gio_vn như 'gio'
    # chỉnh: hàm orb dùng cột gio. gán gio = gio_vn
    df2 = df.copy()
    df2["gio"] = df["gio_vn"]
    sig_orb = tin_hieu.tin_vao(df2, "orb_london_anh")
    loc_london = ((df["gio_vn"] >= 14) & (df["gio_vn"] < 20)).astype(np.int8) * 2

    # lọc: chỉ vào khi có sweep cùng chiều trong 5 nến vừa xong
    loc_sw = loc_london.copy()
    if "sweep_dir" in m1.columns:
        roll = m1["sweep_dir"].reindex(df.index).fillna(0).rolling(5, min_periods=1).sum()
        cho_mua = (loc_london == 2) & (roll > 0)
        cho_ban = (loc_london == 2) & (roll < 0)
        loc_sw[:] = 0
        loc_sw[cho_mua] = 1
        loc_sw[cho_ban] = -1

    qt = ("atr_sl20_eod", 2.0, 4.0, 0.0, 0, 1)
    rows = []
    for ten, loc in (
        ("london_khong_loc", loc_london.to_numpy() if hasattr(loc_london, "to_numpy") else loc_london),
        ("london_sweep_5n", loc_sw.to_numpy() if hasattr(loc_sw, "to_numpy") else loc_sw),
    ):
        r = mo_phong.mo_phong_df(df2, sig_orb, np.asarray(loc, dtype=np.int8), qt, tinh_swap=False, khung="M1")
        r.update(vao="orb_london_anh", loc=ten, khung="M1_GC")
        rows.append(r)
        print(f"OF {ten} CAGR={r['cagr']*100:.2f}% DD={r['dd']*100:.2f}% n={r['n_lenh']} PF={r['pf']:.2f} dat={r['dat']}", flush=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_dir / "orderflow_ket_qua.csv", index=False, encoding="utf-8-sig")
    bao["ket_qua"] = rows
    (out_dir / "orderflow_trang_thai.json").write_text(json.dumps(bao, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return bao


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thu-muc", default="", help="Thư mục có gcz6_1m.csv, gcz6_flow.json...")
    args = ap.parse_args()
    candidates = []
    if args.thu_muc:
        candidates.append(Path(args.thu_muc))
    candidates += [
        Path("/workspace/brain2/vang/du_lieu/fxaurum"),
        Path("/workspace/aurume/fxaurum"),
        Path(r"E:/brain2_tmp/vang/fxaurum"),
    ]
    thu = next((p for p in candidates if p.exists() and (p / "gcz6_1h.csv").exists() or (p.exists() and (p / "gcz6_1m.csv").exists())), None)
    if thu is None:
        thu = candidates[0] if args.thu_muc else candidates[0]
        # operator precedence bug avoided: pick first existing with any csv
        for p in candidates:
            if p.exists() and (list(p.glob("gcz6_*.csv")) or list(p.glob("meta*.json"))):
                thu = p
                break
        else:
            thu = Path("/workspace/brain2/vang/du_lieu/fxaurum")
    out = Path(__file__).resolve().parents[1] / "ket_qua"
    quet_orderflow(thu, out)


if __name__ == "__main__":
    # sửa sys.path khi chạy file trực tiếp
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    main()
