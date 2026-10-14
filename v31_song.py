# -*- coding: utf-8 -*-
"""Vòng 31 (A) — thống kê thời gian sóng, xác suất đi tiếp theo mức/thời gian hồi, sóng sau/sóng trước,
theo phiên và ngày trong tuần. ZigZag-ATR không nhìn trước. MÔ TẢ (không phải phép thử giao dịch, không tính Holm)."""
import json
import numpy as np, pandas as pd
from nhan.song_zigzag_atr import song
from v30 import nap, TEP_M5

GIO_NEN = {"H1": 1, "H4": 4, "D1": 24}
MUC = [0, 0.382, 0.5, 0.618, 0.786, 1.0, 1.5, 99]
TG = [0, 0.5, 1.0, 2.0, 99]  # số nến hồi / số nến đẩy


def phien(h):  # giờ server NY+7
    return "A" if 1 <= h < 9 else ("AU" if 9 <= h < 16 else ("MY" if 16 <= h < 23 else "KHAC"))


def pv(x):
    x = np.asarray(pd.Series(x).dropna(), float)
    return {"n": int(len(x)), **({f"p{q}": round(float(np.percentile(x, q)), 3) for q in (50, 70, 90)} if len(x) else {})}


def mot(ts, kh, k=2.0):
    w, _, _ = song(nap(ts, kh), k)
    w["gio"] = w.nen * GIO_NEN[kh]
    r = {"thoi_gian_gio": {"day": pv(w[w.loai == "day"].gio), "hoi": pv(w[w.loai == "hoi"].gio)},
         "so_nen": {"day": pv(w[w.loai == "day"].nen), "hoi": pv(w[w.loai == "hoi"].nen)}}
    tri = []
    for j in range(len(w) - 2):
        if w.loai[j] == "day" and w.loai[j + 1] == "hoi":
            tri.append(dict(r=w.diem[j + 1] / w.diem[j], tgr=w.nen[j + 1] / max(w.nen[j], 1),
                            di_tiep=bool(w.diem[j + 2] > w.diem[j + 1]), sau_truoc=w.diem[j + 2] / w.diem[j]))
    t = pd.DataFrame(tri)
    if len(t):
        t["mr"] = pd.cut(t.r, MUC, right=False); t["mt"] = pd.cut(t.tgr, TG, right=False)
        r["di_tiep_theo_muc_hoi"] = {str(k): {"n": int(len(g)), "p_di_tiep": round(g.di_tiep.mean(), 3)} for k, g in t.groupby("mr", observed=True)}
        r["di_tiep_theo_tg_hoi"] = {str(k): {"n": int(len(g)), "p_di_tiep": round(g.di_tiep.mean(), 3)} for k, g in t.groupby("mt", observed=True)}
        r["p_di_tiep_chung"] = round(t.di_tiep.mean(), 3)
        r["song_sau_tren_song_truoc_cung_chieu"] = pv(t.sau_truoc)
    r["song_ke_tren_song_truoc"] = pv(w.diem.values[1:] / w.diem.values[:-1])
    t0 = pd.to_datetime(w.t0)
    if kh == "H1":
        w["ph"] = [phien(x.hour) for x in t0]
        r["theo_phien"] = {p: {"n": int(len(g)), "atr_p50": round(g.atr.median(), 3), "gio_p50": float(g.gio.median())} for p, g in w.groupby("ph")}
    w["thu"] = [x.dayofweek for x in t0]
    r["theo_thu"] = {int(d): {"n": int(len(g)), "atr_p50": round(g.atr.median(), 3), "pct_p50": round(g.pct.median(), 3)} for d, g in w.groupby("thu")}
    return r


if __name__ == "__main__":
    out = {f"{ts}|{kh}": mot(ts, kh) for ts in TEP_M5 for kh in ("H1", "H4", "D1")}
    json.dump(out, open("reports/song_thong_ke.json", "w"), ensure_ascii=False, indent=1, default=str)
    L = ["# Thống kê thời gian sóng & xác suất đi tiếp (vòng 31-A, ZigZag 2 ATR, MÔ TẢ)", "",
         "Đi tiếp = sóng kế theo chiều sóng đẩy vượt đỉnh/đáy sóng đẩy. Mức hồi = sóng hồi/sóng đẩy. Thời gian hồi = số nến hồi/số nến đẩy.",
         "Đẩy/hồi theo MA200. H1/H4 2024–2026 HistData; D1 Yahoo 2004–2026. Phiên theo giờ server NY+7 (Á 1–9h, Âu 9–16h, Mỹ 16–23h). Thứ: 0 = thứ Hai.", "",
         "| Tài sản|Khung | Đẩy giờ p50/p70/p90 | Hồi giờ p50/p70/p90 | P đi tiếp chung | P đi tiếp theo mức hồi [<.382 / .382–.5 / .5–.618 / .618–.786 / .786–1 / 1–1.5 / >1.5] | P đi tiếp theo TG hồi [<0.5 / 0.5–1 / 1–2 / >2] | Sóng sau/trước cùng chiều p50/p70/p90 |",
         "|---|---|---|---|---|---|---|"]
    def g(d): return f"{d.get('p50')} / {d.get('p70')} / {d.get('p90')}"
    for key, r in out.items():
        m = r.get("di_tiep_theo_muc_hoi", {}); tt = r.get("di_tiep_theo_tg_hoi", {})
        fm = " / ".join(f"{v['p_di_tiep']}({v['n']})" for v in m.values()) or "CHƯA ĐO ĐƯỢC"
        ft = " / ".join(f"{v['p_di_tiep']}({v['n']})" for v in tt.values()) or "CHƯA ĐO ĐƯỢC"
        L.append(f"| {key} | {g(r['thoi_gian_gio']['day'])} | {g(r['thoi_gian_gio']['hoi'])} | {r.get('p_di_tiep_chung')} | {fm} | {ft} | {g(r.get('song_sau_tren_song_truoc_cung_chieu', {}))} |")
    L += ["", "Số trong ngoặc = số mẫu; khoảng rỗng bị bỏ khỏi chuỗi. Theo phiên/thứ: xem `reports/song_thong_ke.json` (`theo_phien`, `theo_thu`).", "",
          "## Theo phiên (H1, biên độ ATR p50 / số sóng)", "", "| Tài sản | Á | Âu | Mỹ |", "|---|---|---|---|"]
    for ts in TEP_M5:
        p = out[f"{ts}|H1"].get("theo_phien", {})
        L.append(f"| {ts} | " + " | ".join(f"{p.get(x, {}).get('atr_p50')} ({p.get(x, {}).get('n')})" for x in ("A", "AU", "MY")) + " |")
    L += ["", "## Theo thứ (D1, biên độ % p50 / số sóng)", "", "| Tài sản | T2 | T3 | T4 | T5 | T6 |", "|---|---|---|---|---|---|"]
    for ts in TEP_M5:
        p = out[f"{ts}|D1"].get("theo_thu", {})
        L.append(f"| {ts} | " + " | ".join(f"{p.get(d, {}).get('pct_p50')} ({p.get(d, {}).get('n')})" for d in range(5)) + " |")
    open("reports/song_thong_ke.md", "w").write("\n".join(L) + "\n")
