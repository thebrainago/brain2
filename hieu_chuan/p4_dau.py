#!/usr/bin/env python3
"""P4 phu (yeu cau chu du an 10/10 khuya): DONG DAU mo phong vs MT5, va luat LOAI SOM.

    python hieu_chuan/p4_dau.py     # doc hieu_chuan/p1_ket_qua.json (+ p4_ket_qua.json neu co)

Chu du an quan tam DAU (ca hai lai hoac ca hai lo = on; nguoc dau = nguy hiem), khong quan tam
do lon. Doc 15 o P1 (MO PHONG vs TESTER MT5) va dem dong dau / nguoc dau cho tung dong co, tung
bien the (spread 1,5/2,5 pip x thu tu gia trong nen). Roi do 3 luat loai som de xuat tren 15 o
va tren chuoi NHIEU cua P4 (phan B: o tot nhat cua luot quet luoi). Chi do - khong doi cong.
"""
from __future__ import annotations

import json
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]


def dau(x: float, eps: float = 0.0) -> int:
    return 1 if x > eps else (-1 if x < -eps else 0)


def phan_tich_p1(k: dict) -> dict:
    o_ra, tong = [], {"v3": [0, 0, 0], "duong": [0, 0, 0]}   # [dong, nguoc, so bien the]
    for o in k["o"]:
        t = o["tester"]["lai_nam_pct"]
        v3 = [o["v3"][s]["lai_nam_pct"] for s in ("1.5", "2.5")]
        du = [v["lai_nam_pct"] for v in o["duong"].values()]
        dd_du = [v["maxdd_pct"] for v in o["duong"].values()]
        r = {"o": o["o"], "ma": o["ma"], "tia": o["tia"], "tester_lai": t,
             "tester_dd": o["tester"]["maxdd_pct"],
             "v3_min": min(v3), "v3_max": max(v3), "duong_min": min(du), "duong_max": max(du),
             "duong_dd_max": max(dd_du), "v3_dd": o["v3"]["1.5"]["maxdd_pct"]}
        for ten, xs in (("v3", v3), ("duong", du)):
            dong = sum(dau(x) == dau(t) for x in xs)
            nguoc = sum(dau(x) == -dau(t) for x in xs)
            tong[ten][0] += dong
            tong[ten][1] += nguoc
            tong[ten][2] += len(xs)
            r[f"{ten}_dau"] = ("DONG" if dong == len(xs) else
                               "NGUOC" if nguoc == len(xs) else "LUNG_CHUNG")
            # nguoc dau theo huong LAC QUAN (mo phong lai, tester lo) hay bi quan
            r[f"{ten}_nguoc_lac_quan"] = sum(x > 0 > t for x in xs)
        o_ra.append(r)
    tom = {}
    for ten in ("v3", "duong"):
        d, n_, m = tong[ten]
        tom[ten] = {
            "bien_the_dong_dau": f"{d}/{m}", "bien_the_nguoc_dau": f"{n_}/{m}",
            "o_dong_dau_moi_bien_the": sum(r[f"{ten}_dau"] == "DONG" for r in o_ra),
            "o_nguoc_dau_moi_bien_the": sum(r[f"{ten}_dau"] == "NGUOC" for r in o_ra),
            "o_lung_chung": [r["o"] for r in o_ra if r[f"{ten}_dau"] == "LUNG_CHUNG"],
            "o_co_nguoc_dau": [r["o"] for r in o_ra if r[f"{ten}_nguoc_lac_quan"]
                               or r[f"{ten}_dau"] != "DONG"],
            "nguoc_dau_deu_lac_quan": all(
                r[f"{ten}_nguoc_lac_quan"] > 0 for r in o_ra if r[f"{ten}_dau"] != "DONG"),
        }
    return {"o": o_ra, "tom_tat": tom}


def luat_p1(o_ra: list[dict]) -> dict:
    """Do luat loai som tren 15 o: luat giu o -> o do co tester LAI khong?"""
    def _do(ten, giu):
        g = [r for r in o_ra if giu(r)]
        return {"luat": ten, "giu": [r["o"] for r in g],
                "giu_ma_tester_lo (nguoc dau lot qua)": [r["o"] for r in g if r["tester_lai"] <= 0],
                "loai_ma_tester_lai (chan oan)": [r["o"] for r in o_ra
                                                  if not giu(r) and r["tester_lai"] > 0]}
    return {
        "R0_v3_lai_gt_0 (khong luat)": _do("v3 lai > 0 (spread 1,5)", lambda r: r["v3_max"] > 0),
        "R1_v3_lai_ge_10": _do("v3 lai >= 10 %/nam o MOI spread", lambda r: r["v3_min"] >= 10),
        "R2_duong_xau_nhat_gt_0": _do("luoi_duong lai > 0 o thu tu/spread XAU NHAT",
                                      lambda r: r["duong_min"] > 0),
        "R2b_duong_tot_nhat_gt_0": _do("luoi_duong lai > 0 o bien the TOT NHAT",
                                       lambda r: r["duong_max"] > 0),
        "R3_dd_le_60": _do("maxDD mo phong <= 60 % (duong, moi bien the)",
                           lambda r: r["duong_dd_max"] <= 60),
    }


def luat_nhieu(p4: dict) -> dict:
    """Tren chuoi NHIEU (P4 phan B): moi 'dat' ngoai mau la duong tinh gia. Luat loai som
    con de lot bao nhieu? Lai/nam = lai kiem / von / so nam kiem."""
    ra = {}
    nb = int(p4["cau_hinh"]["n_B"])
    nam_kiem = (nb - int(nb * 0.6)) / (24 * 365.25)   # gio lich (chuoi gia lap chay 24/7)
    for mh in ("rw", "garch"):
        rows = p4.get(f"B_{mh}_dong")
        if not rows:
            continue
        for e in ("duong", "v3"):
            n = len(rows)
            dat = [r[e] for r in rows if r[e]["tot_kiem_dat"]]
            lai_nam = [d["tot_kiem"]["lai"] / 1e4 / nam_kiem * 100 for d in dat]
            tu_dd = [r[e]["tot_tu"]["maxdd_pct"] for r in rows]
            # trong mau: o tot nhat co DD > 60 % -> ngoai mau co chay / DD >= 80 % khong?
            cao = [r[e] for r in rows if r[e]["tot_tu"]["maxdd_pct"] > 60]
            thap = [r[e] for r in rows if r[e]["tot_tu"]["maxdd_pct"] <= 60]

            def _hong(d):
                k = d["tot_kiem"]
                return k["chay"] or k["maxdd_pct"] >= 80

            ra[f"{mh}_{e}"] = {
                "n_chuoi": n, "o_tot_dat_25_09_ngoai_mau": len(dat),
                "con_lot_neu_bat_lai_ge_10pct_nam": sum(x >= 10 for x in lai_nam),
                "lai_nam_pct_cua_ca_dat_trung_vi": (round(sorted(lai_nam)[len(lai_nam) // 2], 2)
                                                    if lai_nam else None),
                "trong_mau_dd_gt_60": len(cao),
                "trong_mau_dd_gt_60_ngoai_mau_hong": sum(_hong(d) for d in cao),
                "trong_mau_dd_le_60_ngoai_mau_hong": sum(_hong(d) for d in thap),
                "trong_mau_dd_le_60": len(thap),
                "trong_mau_dd_trung_vi": round(sorted(tu_dd)[n // 2], 2) if n else None,
            }
    return ra


def nhieu_A(p4: dict) -> dict:
    """Ti le co che CHAY tren chuoi NHIEU (phan A, duong ong vong that) qua tung cong."""
    ra = {}
    for mh in ("rw", "garch"):
        a = p4.get(f"A_{mh}")
        if not a:
            continue
        for nhom in ("tat_ca", "loai_luoi", "loai_hedge", "loai_le"):
            if nhom in a:
                b = a[nhom]
                ra[f"{mh}_{nhom}"] = {k: f"{b[k]['k']}/{b[k]['n']}" for k in (
                    "giu_cong_brain2", "nhan_25_09", "placebo_p05_rieng", "n25_va_placebo_p05")}
        ra[f"{mh}_cap_chuoi_co_it_nhat_1_nhan_25_09"] = (
            f"{a['cap_chuoi']['co_it_nhat_1_nhan_25_09']['k']}/{a['cap_chuoi']['co_it_nhat_1_nhan_25_09']['n']}")
    return ra


def de_xuat(p1_luat: dict, p4: dict | None) -> dict:
    """Luat loai som DE XUAT: moi luat ghi bang chung tu 15 o MT5 VA tu nhieu (hoac CHUA DO DUOC).
    KHONG doi cong duyet - chi de xuat."""
    def _r2(mh):
        r = (p4 or {}).get(f"R2_{mh}")
        if not r:
            return "CHUA DO DUOC"
        a = r["goc_gan_open_2pip_dat_25_09"]
        b = r["R2_va_moi_bien_the_dat_25_09"]
        return f"nhieu {mh}: dat 25/09 {a['k']}/{a['n']} -> them R2 {b['k']}/{b['n']}"

    def _plac(mh):
        a = (p4 or {}).get(f"A_{mh}", {}).get("loai_luoi")
        if not a:
            return "CHUA DO DUOC"
        return (f"nhieu {mh} (luoi EA): dat 25/09 {a['nhan_25_09']['k']}/{a['nhan_25_09']['n']} -> "
                f"them placebo p<=0,05 {a['n25_va_placebo_p05']['k']}/{a['n25_va_placebo_p05']['n']}")

    r2 = p1_luat["R2_duong_xau_nhat_gt_0"]
    r1 = p1_luat["R1_v3_lai_ge_10"]
    return {
        "nhan": "DE XUAT - khong doi cong; so la MO PHONG",
        "D1_R2_xau_nhat_gt_0 (chong NGUOC DAU voi MT5)": {
            "luat": "luoi: chay luoi_duong 4 thu tu gia x spread 1,5/2,5; lai o bien the XAU NHAT phai > 0",
            "15_o_MT5": f"giu {r2['giu']}, lot nguoc dau {r2['giu_ma_tester_lo (nguoc dau lot qua)']}, "
                        f"chan oan {r2['loai_ma_tester_lai (chan oan)']}",
            "nhieu": [_r2("rw"), _r2("garch")]},
        "D2_placebo_cung_cau_truc (chong NHIEU)": {
            "luat": "luoi/hedge dat 25/09 con phai thang placebo cung cau truc p <= 0,05 (cong brain2 da co)",
            "15_o_MT5": "CHUA DO DUOC (15 o la ThamSo khong co tin hieu vao -> khong co placebo chieu)",
            "nhieu": [_plac("rw"), _plac("garch")]},
        "khong_de_xuat_R1_lai_ge_10": {
            "15_o_MT5": f"van lot o {r1['giu_ma_tester_lo (nguoc dau lot qua)']} (v3)",
            "nhieu": [f"{mh}: {v['con_lot_neu_bat_lai_ge_10pct_nam']}/{v['o_tot_dat_25_09_ngoai_mau']} ca dat van lot"
                      for mh, v in (luat_nhieu(p4).items() if p4 else [])]},
        "khong_de_xuat_R3_dd_le_60": "15 o: khong loai o nao (maxDD tester <= 33 %); nhieu: xem luat_nhieu "
                                     "trong_mau_dd_* - khong nhat quan giua dong co",
    }


def main() -> int:
    k = json.loads((GOC / "hieu_chuan" / "p1_ket_qua.json").read_text(encoding="utf-8"))
    p1 = phan_tich_p1(k)
    ra = {"nhan": "MO PHONG vs TESTER MT5 (15 o P1) + MO PHONG tren gia NHIEU (P4) - khong phai tien",
          "dau_p1": p1, "luat_p1": luat_p1(p1["o"])}
    f4 = GOC / "hieu_chuan" / "p4_ket_qua.json"
    p4 = json.loads(f4.read_text(encoding="utf-8")) if f4.exists() else None
    if p4:
        ra["luat_nhieu"] = luat_nhieu(p4)
        ra["nhieu_A"] = nhieu_A(p4)
        ra["R2_nhieu"] = {mh: p4.get(f"R2_{mh}", "CHUA DO DUOC") for mh in ("rw", "garch")}
    else:
        ra["luat_nhieu"] = "CHUA DO DUOC (chua co p4_ket_qua.json)"
    ra["de_xuat_loai_som"] = de_xuat(ra["luat_p1"], p4)
    (GOC / "hieu_chuan" / "p4_dau.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    print(json.dumps({x: y for x, y in ra.items() if x != "dau_p1"} | {"tom_tat": p1["tom_tat"]},
                     ensure_ascii=False, indent=1))
    for r in p1["o"]:
        print(r["o"], r["ma"], "tia" if r["tia"] else "   ", f"tester {r['tester_lai']:+.1f}",
              f"v3 {r['v3_min']:+.1f}..{r['v3_max']:+.1f} [{r['v3_dau']}]",
              f"duong {r['duong_min']:+.1f}..{r['duong_max']:+.1f} [{r['duong_dau']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
