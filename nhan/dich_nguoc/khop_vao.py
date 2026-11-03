# -*- coding: utf-8 -*-
"""Làn B (dich_phuong_phap): đo tỉ lệ KHỚP ĐIỂM VÀO giữa EA dựng lại và lệnh thật (03/11/2026).
khop % = số lệnh thật có ít nhất một lệnh dựng lại cùng chiều trong ±cua_so phút / tổng lệnh thật (trong vùng có dữ liệu giá).
Ngưỡng: >= 70 % mới được xếp test dài MT5; dưới -> loại.
    python -m nhan.dich_nguoc.khop_vao      -> reports/KHOP_VAO_LAN_B.md + data/khop_vao.json
"""
from __future__ import annotations
import bisect, json
from pathlib import Path

NGUONG = 70.0
GOC = Path(__file__).resolve().parents[2]


def ty_le_khop(that: list[tuple[float, int]], dung: list[tuple[float, int]], cua_so_giay: float = 3600) -> float | None:
    """that/dung: [(epoch giây, chiều +1/-1)]. Trả % lệnh thật được khớp, None nếu không có lệnh thật."""
    if not that:
        return None
    theo = {1: sorted(t for t, c in dung if c == 1), -1: sorted(t for t, c in dung if c == -1)}
    n = 0
    for t, c in that:
        a = theo.get(c, [])
        i = bisect.bisect_left(a, t - cua_so_giay)
        if i < len(a) and a[i] <= t + cua_so_giay:
            n += 1
    return round(100.0 * n / len(that), 2)


def cong_lich_su(dd_pct, cagr_pct, that: bool = True) -> tuple[bool, str]:
    """Cổng làn B (Anh 03/11): CHỈ dựng lại hệ khi lịch sử THẬT đã kiểm chứng đạt DD<80 % và CAGR>10 %/năm
    (CAGR thấp được nâng lot tuyến tính nếu DD còn chỗ: tồn tại k để k·DD<80 và CAGR_k>10). Không lịch sử / trượt -> không dựng."""
    if not that or dd_pct is None or cagr_pct is None:
        return False, "không có lịch sử thật kiểm chứng"
    if dd_pct >= 80:
        return False, "DD lịch sử >= 80 %"
    if cagr_pct > 10:
        return True, "đạt"
    if cagr_pct <= 0:
        return False, "lịch sử lỗ"
    k = 79.9 / max(dd_pct, 1e-9)
    return ((1 + cagr_pct / 100) ** k - 1 > 0.10, "đạt sau nâng lot k<=%.2f" % k)


def dat(khop: float | None) -> bool:
    return khop is not None and khop >= NGUONG


# (tín hiệu, EA dựng lại, kiểu mô phỏng, cặp, tham số) — UV1/UV2 trong reports/DICH_NGUOC_TOP10.md
UNG_VIEN = [("2330430", "BRAIN_DN_LuoiHedgeTP", "luoi_tp", "GBPUSD", {"buoc": 35, "tp": 35, "max_lenh": 60, "dong_ro_khi": 6}),
            ("2262642", "BRAIN_DN_RoDCAHedge", "ro_dca", "AUDCAD", {"buoc": 15, "tp": 11, "max_lenh": 140})]


def main() -> None:
    import pandas as pd
    from nhan.dich_nguoc import backtest_luoi as BL, doc_lich_su as DL
    ra = []
    ls = {}
    for x in (GOC / "data/cong_khai/tin_hieu.jsonl").read_text(encoding="utf-8").splitlines():
        if x.strip():
            r = json.loads(x); ls[str(r["id"])] = r
    for sid, ea, kieu, cap, ts in UNG_VIEN:
        h = ls.get(sid, {})
        ok, ly = cong_lich_su(h.get("dd_pct"), h.get("cagr_pct"), h.get("that_demo") == "that")
        if not ok:
            ra.append({"tin_hieu": sid, "ea": ea, "cap": cap, "khop_pct": None, "lich_su_dat": False,
                       "ghi_chu": "KHÔNG DỰNG: cổng lịch sử — %s" % ly}); continue
        df = DL.doc(str(GOC / ("data/cong_khai/csv/%s.history.csv" % sid)))
        df = df[df["symbol"].str.startswith(cap)]
        g = BL.doc_dai(cap.lower())
        if g is None:
            f = Path(BL.FX) / ("%s_h1_tick_ba_ny7.csv" % cap.lower())
            g = BL.doc(str(f)) if f.exists() else None
        rec = {"tin_hieu": sid, "ea": ea, "cap": cap, "lich_su_dat": True,
               "lich_su": "CAGR %.2f%%/năm, DD %.2f%% (%s)" % (h["cagr_pct"], h["dd_pct"], ly)}
        if g is None or df.empty:
            rec.update({"khop_pct": None, "ghi_chu": "CHƯA ĐO ĐƯỢC: thiếu giá hoặc lệnh"}); ra.append(rec); continue
        # giờ lệnh MQL5 = giờ máy chủ; giá NY+7 ~ cùng giờ máy chủ phổ biến (GMT+2/+3) — sai lệch giờ nằm trong cửa sổ ±1 h
        tu, den = df["mo_luc"].min() - pd.Timedelta(days=3), df["mo_luc"].max()
        gg = g[(g.index >= tu) & (g.index <= den)]
        if len(gg) < 100:
            rec.update({"khop_pct": None, "ghi_chu": "CHƯA ĐO ĐƯỢC: dữ liệu giá không phủ giai đoạn lệnh thật (%s–%s)" % (tu.date(), den.date())}); ra.append(rec); continue
        vao: list = []
        BL.chay(gg, kieu, 1e-4, ts["buoc"], ts["tp"], 1.0, 7.5, max_lenh=ts["max_lenh"], dong_ro_khi=ts.get("dong_ro_khi", 6), ghi_vao=vao)
        dung = [(gg.index[i].timestamp(), c) for i, c in vao]
        that = [(r.mo_luc.timestamp(), 1 if r.chieu == "buy" else -1) for r in df[df["mo_luc"] >= gg.index[0]].itertuples()]
        k = ty_le_khop(that, dung)
        rec.update({"khop_pct": k, "dat": dat(k), "so_lenh_that": len(that), "so_lenh_dung": len(dung),
                    "giai_doan": "%s–%s" % (gg.index[0].date(), gg.index[-1].date()), "ghi_chu": "MÔ PHỎNG Python (nến H1), cửa sổ ±1 h"})
        ra.append(rec)
    (GOC / "data/khop_vao.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Làn B — khớp điểm vào EA dựng lại vs lệnh thật (03/11/2026)", "", "Ngưỡng: >= %.0f %% mới xếp test dài; dưới -> loại." % NGUONG, "",
         "| Tín hiệu | EA | Cặp | Khớp % | Đạt | Lệnh thật | Lệnh dựng | Giai đoạn | Ghi chú |", "|---|---|---|---|---|---|---|---|---|"]
    for r in ra:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (r["tin_hieu"], r["ea"], r["cap"],
                 "CHƯA ĐO ĐƯỢC" if r["khop_pct"] is None else str(r["khop_pct"]).replace(".", ","), "có" if r.get("dat") else "không",
                 r.get("so_lenh_that", "—"), r.get("so_lenh_dung", "—"), r.get("giai_doan", "—"), r["ghi_chu"]))
    (GOC / "reports/KHOP_VAO_LAN_B.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(ra)


if __name__ == "__main__":
    main()
