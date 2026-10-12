# -*- coding: utf-8 -*-
"""Vong 8: do manh loc spread S theo cap (X, X+S) - tieu chi reports/vong8_tien_dang_ky_spread.md.
MO PHONG.   python tv_spread_s.py o.jsonl [ra.json]"""
from __future__ import annotations

import json
import math
import statistics as ST
import sys

import tv_phan_tich as PT


def sign_test(duong: int, am: int) -> float:
    n = duong + am
    if n == 0:
        return 1.0
    k = min(duong, am)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def do_s(o: list[dict]) -> dict:
    bang = {(x["ea"], x["cap"], x["manh"]): x for x in o if "nm" in x}
    ch, loc = [], []
    for (ea, cap, manh), x in bang.items():
        if "S" in manh or len(manh.replace("goc", "")) > 2:
            continue
        ten_s = "".join(sorted(("" if manh == "goc" else manh) + "S", key="ATSPD".index))
        y = bang.get((ea, cap, ten_s))
        if not y:
            continue
        ch.append(y["nm"]["loi_pct"] - x["nm"]["loi_pct"])
        loc.append(x["so_lenh"] - y["so_lenh"])
    du, am = sum(d > 1e-9 for d in ch), sum(d < -1e-9 for d in ch)
    p = sign_test(du, am)
    tv = ST.median(ch) if ch else 0.0
    return {"so_cap": len(ch), "lenh_bi_loc_tong": sum(loc), "lenh_bi_loc_tb": round(ST.mean(loc), 2) if loc else 0,
            "cap_co_lenh_bi_loc": sum(1 for v in loc if v > 0),
            "chenh_nm_trung_vi_pct": round(tv, 4), "chenh_nm_tb_pct": round(ST.mean(ch), 4) if ch else 0,
            "cai_thien": du, "te_hon": am, "bang": len(ch) - du - am, "sign_p": p,
            "ket_luan": "S co ich" if (tv > 0 and p < 0.05) else "khong chung minh duoc S co ich"}


def main(duong, ra=None):
    o = [json.loads(x) for x in open(duong)]
    tom = PT.main(duong)
    tom.pop("tot_nhat_p", None)
    tom["S"] = do_s(o)
    if ra:
        json.dump(tom, open(ra, "w"), ensure_ascii=False, indent=1)
    return tom


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:]), ensure_ascii=False, indent=1))
