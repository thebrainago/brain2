# -*- coding: utf-8 -*-
"""Vong 7 (A): doc o tu `tv_chay.py`, ap TIEU CHI DANG KY TRUOC (reports/vong7_tien_dang_ky_A.md).
p mot phia tu Sharpe ngoai mau, Holm tren MOI o da chay. MO PHONG."""
from __future__ import annotations

import collections
import json
import math
import sys


def p_mot_phia(t: float) -> float:
    return 0.5 * math.erfc(t / math.sqrt(2))


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    thu_tu = sorted(range(m), key=lambda i: ps[i])
    ra = [1.0] * m
    cao = 0.0
    for r, i in enumerate(thu_tu):
        cao = max(cao, min(1.0, (m - r) * ps[i]))
        ra[i] = cao
    return ra


def main(duong: str, ra: str | None = None) -> dict:
    o = [json.loads(x) for x in open(duong)]
    m = len(o)
    ps = []
    for x in o:
        t = (x.get("nm") or {}).get("t")
        ps.append(p_mot_phia(t) if isinstance(t, (int, float)) else 1.0)
    ph = holm(ps)
    for x, p, q in zip(o, ps, ph):
        x["p"], x["p_holm"] = p, q
        nm, tm = x.get("nm") or {}, x.get("tm") or {}
        x["nhan_cong"] = bool(nm and nm["loi_pct"] > 0 and nm["maxdd_pct"] < 80
                              and x.get("lenh_nm", 0) >= 20)
        x["qua_buoc1"] = bool(x["nhan_cong"] and tm and tm["loi_pct"] > 0 and q < 0.05)
    tom = {"so_o": m, "loi": sum(1 for x in o if "loi" in x), "bo_ro": sum(1 for x in o if "bo" in x),
           "nhan_cong": sum(x["nhan_cong"] for x in o),
           "nhan_cong_va_tm_lai": sum(1 for x in o if x["nhan_cong"] and (x.get("tm") or {}).get("loi_pct", -1) > 0),
           "qua_buoc1": sum(x["qua_buoc1"] for x in o),
           "p_min": min(ps), "p_holm_min": min(ph)}
    theo_manh = collections.defaultdict(lambda: [0, 0, 0.0])
    for x in o:
        if "nm" in x:
            d = theo_manh[x["manh"]]
            d[0] += 1
            d[1] += x["nhan_cong"]
            d[2] += x["nm"]["loi_pct"]
    tom["theo_manh"] = {k: {"o": v[0], "nhan_cong": v[1], "nm_tb_pct": round(v[2] / v[0], 3)}
                        for k, v in sorted(theo_manh.items(), key=lambda kv: -kv[1][2] / kv[1][0])}
    tot = sorted([x for x in o if "nm" in x], key=lambda x: x["p"])[:15]
    tom["tot_nhat_p"] = [{k: x.get(k) for k in ("ea", "cap", "khung", "manh", "p", "p_holm",
                                                 "lenh_nm", "nhan_cong")} | {
        "nm": x["nm"], "tm": x["tm"]} for x in tot]
    for x in tom["tot_nhat_p"]:
        x["ea"] = x["ea"].split("/")[-1]
    if ra:
        json.dump(tom, open(ra, "w"), ensure_ascii=False, indent=1)
    return tom


if __name__ == "__main__":
    t = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({k: v for k, v in t.items() if k != "tot_nhat_p"}, ensure_ascii=False, indent=1))
    for x in t["tot_nhat_p"]:
        print(x["ea"][:40], x["cap"], x["khung"], x["manh"], "p=%.2e holm=%.3f" % (x["p"], x["p_holm"]),
              "NM", x["nm"]["loi_pct"], x["nm"]["maxdd_pct"], x["lenh_nm"], "TM", x["tm"]["loi_pct"])
