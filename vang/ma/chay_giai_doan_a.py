# -*- coding: utf-8 -*-
"""Giai đoạn A: event-study tín hiệu Fxaurum GCZ6 trên CFD XM GOLD.i# (basis từng phút)."""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vang.ma.tin_hieu_data import (
    tai_nen_cfd_va_basis, tin_vwap_poc, cum_big_trade, quet_dao_1m,
    su_kien_flow, dung_footprint_1m, tin_cvd_phan_ky, tin_delta_chao,
    CHI_PHI_RT_GIA,
)

GC_CAND = [
    Path("/workspace/brain2/vang/du_lieu/fxaurum"),
    Path(r"E:\brain2_tmp\vang\fxaurum"),
]
XM_CAND = [
    Path("/workspace/backtests/rapid_hedge/data/GOLD_i_M1.csv"),
    Path(r"E:\backtests\rapid_hedge\data\GOLD_i_M1.csv"),
]
OUT_BAO = ROOT / "vang" / "bao_cao"
OUT_KQ = ROOT / "vang" / "ket_qua"
HORIZ = (5, 15, 60)


def _tim(cands):
    for p in cands:
        if p.exists():
            return p
    return None


def event_study(m: pd.DataFrame, ev: pd.DataFrame, ten: str) -> dict:
    if ev is None or ev.empty:
        return {"tin_hieu": ten, "n": 0}
    t = m["time"].to_numpy()
    o = m["cfd_open"].to_numpy()
    c = m["cfd_close"].to_numpy()
    # map sự kiện → nến chứa (searchsorted)
    ev = ev.sort_values("time").reset_index(drop=True)
    idx = np.searchsorted(t, ev["time"].to_numpy(), side="right") - 1
    ok = (idx >= 0) & (idx < len(m) - max(HORIZ) - 1)
    idx = idx[ok]
    hu = ev["huong"].to_numpy()[ok]
    if len(idx) == 0:
        return {"tin_hieu": ten, "n": 0}
    # vào ở open nến kế, tránh lookahead
    vao = idx + 1
    d = {"tin_hieu": ten, "n": int(len(vao))}
    for h in HORIZ:
        ra = vao + h
        raw = hu * (c[ra] - o[vao])
        net = raw - CHI_PHI_RT_GIA  # trừ chi phí vòng tròn (spread+trượt) theo giá CFD
        thang = net > 0
        tt = float(net[thang].sum()) if thang.any() else 0.0
        tth = float(net[~thang].sum()) if (~thang).any() else 0.0
        pf = (tt / abs(tth)) if tth < 0 else (99.0 if tt > 0 else 0.0)
        d[f"hit_{h}"] = float(thang.mean())
        d[f"tb_r_{h}"] = float(net.mean())
        d[f"med_r_{h}"] = float(np.median(net))
        d[f"pf_{h}"] = float(pf)
        d[f"tong_r_{h}"] = float(net.sum())
        d[f"usd_1lot_{h}"] = float(net.sum() * 100.0)  # 1.00 lot, $100 / $1 giá
    return d


def loc_sang_m1(m: pd.DataFrame, ev: pd.DataFrame) -> np.ndarray:
    """Mảng huong +1/-1/0 trên từng nến (tín hiệu trong nến, dùng nến đó làm loc)."""
    loc = np.zeros(len(m), dtype=np.int8)
    if ev is None or ev.empty:
        return loc
    t = m["time"].to_numpy()
    idx = np.searchsorted(t, ev["time"].to_numpy(), side="right") - 1
    hu = ev["huong"].to_numpy()
    for i, h in zip(idx, hu):
        if 0 <= i < len(loc) and loc[i] == 0:
            loc[i] = np.int8(h)
    return loc


def main():
    t0 = time.time()
    thu = _tim(GC_CAND)
    xm = _tim(XM_CAND)
    if thu is None or xm is None:
        raise SystemExit(f"Thiếu dữ liệu thu={thu} xm={xm}")
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)
    print("GC", thu, "XM", xm, flush=True)
    m = tai_nen_cfd_va_basis(thu, xm)
    print("nen", len(m), m["time"].iloc[0], m["time"].iloc[-1],
          "basis med", float(m["basis"].median()), flush=True)
    # basis tóm tắt theo tuần
    wk = m.assign(week=m["time"].dt.strftime("%Y-%W")).groupby("week")["basis"].agg(["median", "std", "count"])
    wk.to_csv(OUT_KQ / "basis_tuan.csv")

    flow = {}
    fp = thu / "gcz6_flow.json"
    if fp.exists():
        flow = json.loads(fp.read_text(encoding="utf-8"))
    big = pd.read_csv(thu / "gcz6_bigtrades.csv") if (thu / "gcz6_bigtrades.csv").exists() else pd.DataFrame()

    evs = {}
    evs["cum20_60s"] = cum_big_trade(big, min_vol=20, cua_so_ms=60_000, n_min=3, band=0.5)
    evs["cum50_60s"] = cum_big_trade(big, min_vol=50, cua_so_ms=60_000, n_min=2, band=0.8)
    evs["cum20_5s"] = cum_big_trade(big, min_vol=20, cua_so_ms=5_000, n_min=3, band=0.5)
    evs["quet_dao_30"] = quet_dao_1m(m, 30)
    evs["quet_dao_60"] = quet_dao_1m(m, 60)
    ev_vwap, m2 = tin_vwap_poc(m)
    m = m2
    evs.update(ev_vwap)
    evs["sw_dao_v5"] = su_kien_flow(flow, "sw", min_vol=5)
    evs["cs_dao"] = su_kien_flow(flow, "cs", min_vol=2)
    evs["ab_v8"] = su_kien_flow(flow, "ab", min_vol=8)
    evs["ice_an"] = su_kien_flow(flow, "ice", min_vol=3)

    tick = thu / "gcz6_ticks.csv"
    co_tick = tick.exists() and tick.stat().st_size > 10_000_000  # >10MB coi như đã có dữ liệu thật
    meta_tick = {"co_tick": bool(co_tick), "size_mb": tick.stat().st_size / 1024**2 if tick.exists() else 0}
    if co_tick:
        print("footprint từ tick", meta_tick, flush=True)
        m = dung_footprint_1m(tick, m)
        evs["cvd_div_30"] = tin_cvd_phan_ky(m, 30)
        evs["delta_chao_2"] = tin_delta_chao(m, 2.0)
        # lưu footprint gọn
        cols = [c for c in ["time", "open_ms", "buy", "sell", "delta", "cvd", "poc_nen", "vwap_nen"] if c in m.columns]
        m[cols].to_csv(OUT_KQ / "footprint_1m.csv", index=False)
    else:
        print("chưa có tick đủ, bỏ CVD/delta (sẽ chạy lại khi xuất xong)", meta_tick, flush=True)

    hang = []
    for ten, ev in evs.items():
        print("study", ten, "n", 0 if ev is None else len(ev), flush=True)
        hang.append(event_study(m, ev, ten))
        # lưu loc
        loc = loc_sang_m1(m, ev)
        evs[ten] = ev  # keep

    bang = pd.DataFrame(hang)
    bang.to_csv(OUT_KQ / "event_study.csv", index=False)

    # quy tắc vào đơn giản (cộng tín hiệu cùng chiều trên 1 nến)
    # chọn các họ có PF_15 > 1 và n>=30 nếu có
    tot = None
    for ten, ev in evs.items():
        loc = loc_sang_m1(m, ev)
        tot = loc.astype(np.int16) if tot is None else tot + loc.astype(np.int16)
    m["diem_data"] = tot
    # rule: điểm >= 2 theo chiều
    ev_rule = []
    for i in range(len(m)):
        if tot[i] >= 2:
            ev_rule.append((m["time"].iloc[i], 1, float(m["cfd_close"].iloc[i]), "rule_diem_ge2"))
        elif tot[i] <= -2:
            ev_rule.append((m["time"].iloc[i], -1, float(m["cfd_close"].iloc[i]), "rule_diem_ge2"))
    ev_r = pd.DataFrame(ev_rule, columns=["time", "huong", "gia", "loai"]) if ev_rule else pd.DataFrame()
    r_rule = event_study(m, ev_r, "rule_diem_ge2")
    hang.append(r_rule)
    # quy tắc chỉ họ có PF 15p > 1 (sau phí)
    tot2 = np.zeros(len(m), dtype=np.int16)
    for ten in ("cum50_60s", "vwap_tu_choi", "sw_dao_v5"):
        evx = evs.get(ten)
        if evx is not None and not evx.empty:
            tot2 = tot2 + loc_sang_m1(m, evx).astype(np.int16)
    ev_r2 = []
    for i in range(len(m)):
        if tot2[i] >= 1:
            ev_r2.append((m["time"].iloc[i], 1, float(m["cfd_close"].iloc[i]), "rule_pf15_tot"))
        elif tot2[i] <= -1:
            ev_r2.append((m["time"].iloc[i], -1, float(m["cfd_close"].iloc[i]), "rule_pf15_tot"))
    ev_r2 = pd.DataFrame(ev_r2, columns=["time", "huong", "gia", "loai"]) if ev_r2 else pd.DataFrame()
    hang.append(event_study(m, ev_r2, "rule_pf15_tot"))
    bang = pd.DataFrame(hang)
    bang.to_csv(OUT_KQ / "event_study.csv", index=False)

    # lưu điểm để giai đoạn B
    np.savez_compressed(OUT_KQ / "diem_data_m1.npz",
                        time=m["time"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy().astype("datetime64[ns]"),
                        diem=tot, close=m["cfd_close"].to_numpy(), open=m["cfd_open"].to_numpy())

    # viết báo cáo
    def fmt(row):
        if row["n"] == 0:
            return f"| {row['tin_hieu']} | 0 | — | — | — |"
        return (f"| {row['tin_hieu']} | {int(row['n'])} | "
                f"{row.get('hit_5',0)*100:.1f}% / {row.get('pf_5',0):.2f} / {row.get('usd_1lot_5',0):.0f} | "
                f"{row.get('hit_15',0)*100:.1f}% / {row.get('pf_15',0):.2f} / {row.get('usd_1lot_15',0):.0f} | "
                f"{row.get('hit_60',0)*100:.1f}% / {row.get('pf_60',0):.2f} / {row.get('usd_1lot_60',0):.0f} |")

    # cửa sổ flow
    def _rng(name, ev):
        if ev is None or ev.empty:
            return f"{name}: không có"
        return f"{name}: {ev['time'].min()} → {ev['time'].max()} (n={len(ev)})"

    lines = [
        "# Giai đoạn A — event-study tín hiệu dữ liệu GCZ6 (vàng XM)",
        "",
        "Đo lúc (Asia/Saigon, UTC+7). Giá CFD = GC − basis từng phút (GOLD.i# đổi Europe/Athens → UTC). "
        "Vào tại **mở nến 1m kế** sau sự kiện. Chi phí vòng tròn 0,21 giá (20 pts spread M1 + 0,5 trượt mỗi phía). "
        "USD quy 1,00 lot (100 USD / 1,00 giá). Tiêu chí: lãi ròng > 0, DD sẽ đo ở giai đoạn B.",
        "",
        f"- Nến 1m GC: {m['time'].iloc[0]} → {m['time'].iloc[-1]} ({len(m)} nến).",
        f"- Basis trung vị toàn cửa sổ: {float(m['basis'].median()):.2f} (giảm dần ~56 tháng 8 xuống ~0 tháng 11; "
        f"thay đổi basis 15 phút std {float((m['basis'].shift(-15)-m['basis']).std()):.2f}).",
        f"- Tick footprint: {'CÓ' if co_tick else 'CHƯA (đang xuất aggTrades, không gọi syncTicks/syncHistory)'}"
        f" ({meta_tick['size_mb']:.1f} MB).",
        "",
        "## Bảng event-study (hit / PF / USD 1 lot)",
        "",
        "| Tín hiệu | n | 5 phút | 15 phút | 60 phút |",
        "|---|---:|---|---|---|",
    ]
    # sort by pf_15
    bang2 = bang.copy()
    if "pf_15" in bang2.columns:
        bang2 = bang2.sort_values(["n", "pf_15"], ascending=[False, False])
    for _, r in bang2.iterrows():
        lines.append(fmt(r))
    lines += [
        "",
        "## Phạm vi từng họ",
        "",
        "- Big-trade / quét 1m / VWAP / POC: gần như cả cửa sổ GC (20/08–27/11/2026).",
        "- flowRecs (sweep/absorption/iceberg): chỉ kho local ~18–27/11/2026 (không gọi sync).",
        "",
        "## OptionsDb",
        "",
        "Tìm thấy tại `E:\\GrokWork\\FxaurumRithmic\\OptionsDb\\COMEX.GCZ6` (junction từ `%LOCALAPPDATA%\\FxaurumRithmic\\OptionsDb`), "
        "9,59 GB, chủ yếu 19–20/11/2026 (bbo.fxop rất lớn; core.fxop vài MB). "
        "`optionRecordStatus`: recorder đang tắt, không symbol. "
        "`optionHistory` không `expirations` trả rỗng hoặc timeout. "
        "Chưa suy ra được tường/GEX/max pain (sẽ đọc lại qua API với expiry sau khi xuất tick xong).",
        "",
        "## Quy tắc vào đơn giản",
        "",
        "Cộng hướng các tín hiệu trên cùng nến; vào khi |điểm| ≥ 2. Kết quả dòng `rule_diem_ge2` trong bảng.",
        "",
        f"Chạy trong {time.time()-t0:.1f} giây.",
    ]
    (OUT_BAO / "GIAI_DOAN_A.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("XONG A", bang.to_string(index=False), flush=True)
    print("bao cao", OUT_BAO / "GIAI_DOAN_A.md", flush=True)


if __name__ == "__main__":
    main()
