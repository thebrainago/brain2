# -*- coding: utf-8 -*-
"""P5 (11/10/2026): do luat LOAI SOM nhanh cua chu du an tren 15 o MT5 (P1) - CHI DO, khong chay lai mo phong.

Luat de xuat (chu du an 11/10): mo phong maxDD > 65 % HOAC lai mo phong < 10 %/nam -> loai som truoc MT5.
Doc `p1_ket_qua.json` (mo phong v3 = luoi.chay, duong = luoi_duong) + dap an tester trong cung file.
Dem: luat giet bao nhieu o MT5 CO LAI (sai loai), giu bao nhieu o MT5 LO (lot luoi).
MO PHONG so voi TESTER MT5 - khong phai tien that. 15 o / 6 thang / 2 ma: uoc luong, khong phai quy luat 100 %.
Chay: python3 hieu_chuan/p5_loai_som.py  -> hieu_chuan/p5_ket_qua.json
"""
import json
from pathlib import Path

HC = Path(__file__).resolve().parent
DD_MAX, LAI_MIN = 65.0, 10.0


def loai(lai, dd, dd_max=DD_MAX, lai_min=LAI_MIN):
    return dd > dd_max or lai < lai_min


def main():
    d = json.loads((HC / "p1_ket_qua.json").read_text(encoding="utf-8"))
    ra = {"luat": f"loai neu maxDD mo phong > {DD_MAX:g}% hoac lai mo phong < {LAI_MIN:g}%/nam",
          "nhan": "MO PHONG vs TESTER MT5, 15 o, 6 thang 2019, AUDCAD/NZDCAD - uoc luong", "dong_co": {}}
    for ten in ("v3", "duong"):
        dem = {"bien_the": 0, "mt5_lai_bi_loai": 0, "mt5_lai_duoc_giu": 0,
               "mt5_lo_bi_loai": 0, "mt5_lo_lot_qua": 0, "mt5_dang_10pc_bi_loai": 0, "chi_tiet_sai": []}
        for o in d["o"]:
            t = o["tester"]
            mt5_lai = t["lai_nam_pct"] > 0
            mt5_dang = t["lai_nam_pct"] >= LAI_MIN and t["maxdd_pct"] <= DD_MAX
            for k, v in o[ten].items():
                dem["bien_the"] += 1
                bl = loai(v["lai_nam_pct"], v["maxdd_pct"])
                if mt5_lai:
                    dem["mt5_lai_bi_loai" if bl else "mt5_lai_duoc_giu"] += 1
                else:
                    dem["mt5_lo_bi_loai" if bl else "mt5_lo_lot_qua"] += 1
                if mt5_dang and bl:
                    dem["mt5_dang_10pc_bi_loai"] += 1
                if bl == mt5_lai or (not bl and not mt5_lai):
                    dem["chi_tiet_sai"].append(
                        {"o": o["o"], "bien_the": k, "mo_phong_lai": round(v["lai_nam_pct"], 2),
                         "mo_phong_dd": round(v["maxdd_pct"], 2), "mt5_lai": t["lai_nam_pct"],
                         "mt5_dd": t["maxdd_pct"], "loi": "giet o MT5 lai" if bl else "lot o MT5 lo"})
        ra["dong_co"][ten] = dem
    (HC / "p5_ket_qua.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    for ten, dem in ra["dong_co"].items():
        print(ten, {k: v for k, v in dem.items() if k != "chi_tiet_sai"})
        for x in dem["chi_tiet_sai"]:
            print("   ", x)


if __name__ == "__main__":
    main()
