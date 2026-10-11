# -*- coding: utf-8 -*-
"""P6 (11/10/2026): HIEU CHUAN nguong LOAI SOM nhanh (P5) - CHI DO, khong chay lai mo phong, khong doi GIU/BO.

Luat goc cua chu du an (uoc luong): mo phong maxDD > 65 % HOAC lai mo phong < 10 %/nam -> loai som truoc MT5.
Quet luoi nguong (DD_MAX x LAI_MIN) tren 3 bo so DA CO:
  (a) 15 o MT5 sach (p1_ket_qua.json): dap an tester vs luoi_duong (8 bien the/o) va v3 cu (2 bien the/o).
      Dem: GIET OAN = o MT5 co lai bi loai; LOT = o MT5 lo khong bi loai.
  (b) chuoi CHI NHIEU (p4_ket_qua.json): phan B (luoi 72 o, chon o tot nhat 60 % dau, kiem 40 % sau),
      R2 (o tot nhat x 8 bien the tren 40 % sau), phan A (duong ong vong_thu_nghiem tren .mq5, phan kiem 30 %).
      Moi lan 'khong bi loai' tren nhieu la LOT GIA (khong co loi the that nao).
  (c) luoi that vs nhieu cung cau truc, phi P3 (swap theo thang) - g07/g08 theo nam; + 6 he Breakout P3
      (p3_so_sanh.txt, EURUSD 2016-2021).
MO PHONG - khong phai tien. Chay: python3 hieu_chuan/p6_hieu_chuan_loai_som.py -> p6_ket_qua.json
"""
import json
import math
from pathlib import Path

HC = Path(__file__).resolve().parent
VON = 10_000.0
BAR_NAM_H1 = 24 * 260
DD_LUOI = (30, 40, 50, 60, 65, 70, 80)
LAI_LUOI = (0, 2, 5, 8, 10, 15)


def loai(lai, dd, dd_max, lai_min):
    return dd > dd_max or lai < lai_min


def lai_nam_tu_usd(lai_usd, nam, von=VON):
    cuoi = von + lai_usd
    if cuoi <= 0:
        return -100.0
    return ((cuoi / von) ** (1.0 / nam) - 1.0) * 100.0


def ti(k, n):
    return {"k": k, "n": n, "ti_le": round(k / n, 4) if n else None}


# ------------------------------------------------------------------ (a) 15 o MT5
def do_a(p1):
    ra = {}
    for dc in ("duong", "v3"):
        bang = {}
        for dm in DD_LUOI:
            for lm in LAI_LUOI:
                gk = gn = lk = ln = 0          # bien the
                o_gk = set()
                o_lot = set()
                for o in p1["o"]:
                    t = o["tester"]
                    lai_mt5 = t["lai_nam_pct"] > 0
                    for v in o[dc].values():
                        bl = loai(v["lai_nam_pct"], v["maxdd_pct"], dm, lm)
                        if lai_mt5:
                            gn += 1
                            if bl:
                                gk += 1
                                o_gk.add(o["o"])
                        else:
                            ln += 1
                            if not bl:
                                lk += 1
                                o_lot.add(o["o"])
                bang[f"{dm}|{lm}"] = {"giet_oan": ti(gk, gn), "lot": ti(lk, ln),
                                      "o_giet_oan": sorted(o_gk), "o_lot": sorted(o_lot)}
        ra[dc] = bang
    # do lech mo phong - MT5 (diem %/nam), o MT5 lai
    lech = {}
    for dc in ("duong", "v3"):
        xs = [v["lai_nam_pct"] - o["tester"]["lai_nam_pct"] for o in p1["o"] for v in o[dc].values()]
        xs_lai = [v["lai_nam_pct"] - o["tester"]["lai_nam_pct"] for o in p1["o"]
                  if o["tester"]["lai_nam_pct"] > 0 for v in o[dc].values()]
        lech[dc] = {"tb_moi_o": round(sum(xs) / len(xs), 2), "max_moi_o": round(max(xs), 2),
                    "tb_o_mt5_lai": round(sum(xs_lai) / len(xs_lai), 2),
                    "max_o_mt5_lai": round(max(xs_lai), 2)}
    ra["lech_mo_phong_tru_mt5_diem_pct_nam"] = lech
    ra["mt5_dd_max_pct"] = max(o["tester"]["maxdd_pct"] for o in p1["o"])
    ra["lai_mt5_o_lai"] = {o["o"]: o["tester"]["lai_nam_pct"] for o in p1["o"] if o["tester"]["lai_nam_pct"] > 0}
    return ra


# ------------------------------------------------------------------ (b) nhieu
def mau_nhieu(p4):
    """Tra ve {ten_bo: [(lai_nam_pct, dd_pct), ...]} - moi phan tu la 1 lan 'chon' tren gia chi nhieu."""
    n_b = int(p4["cau_hinh"]["n_B"])
    nam_tu, nam_kiem = 0.6 * n_b / BAR_NAM_H1, 0.4 * n_b / BAR_NAM_H1
    n_a = int(p4["cau_hinh"]["n_A"])
    nam_a = 0.3 * n_a / BAR_NAM_H1
    bo = {}
    for mh in ("rw", "garch"):
        for dc in ("duong", "v3"):
            for phan, nam in (("tot_tu", nam_tu), ("tot_kiem", nam_kiem), ("bua_kiem", nam_kiem)):
                bo.setdefault(f"B_{dc}_{phan}", []).extend(
                    (lai_nam_tu_usd(r[dc][phan]["lai"], nam), r[dc][phan]["maxdd_pct"])
                    for r in p4.get(f"B_{mh}_dong", []))
        for r in p4.get(f"R2_{mh}_dong", []):
            bo.setdefault("R2_duong_8_bien_the", []).extend(
                (lai_nam_tu_usd(v["lai"], nam_kiem), v["maxdd_pct"]) for v in r["bien_the"].values())
        for r in p4.get(f"A_{mh}_dong", []):
            if r.get("bo_qua") or r.get("loi_file") or r.get("maxdd") is None:
                continue
            lai = (math.exp(float(r["loi_log_kiem"]) / nam_a) - 1.0) * 100.0
            bo.setdefault(f"A_ea_{r['loai']}", []).append((lai, float(r["maxdd"])))
    return bo, {"nam_tu_B": nam_tu, "nam_kiem_B": nam_kiem, "nam_kiem_A": round(nam_a, 3)}


def do_b(p4):
    bo, nam = mau_nhieu(p4)
    ra = {"nam": nam, "n": {k: len(v) for k, v in bo.items()}, "lot_gia": {}}
    for k, xs in bo.items():
        ra["lot_gia"][k] = {f"{dm}|{lm}": ti(sum(not loai(l, d, dm, lm) for l, d in xs), len(xs))
                            for dm in DD_LUOI for lm in LAI_LUOI}
        ra["lot_gia"][k]["chi_luat_chu_80|0"] = ti(sum(l > 0 and d < 80 for l, d in xs), len(xs))
    return ra


# ------------------------------------------------------------------ (c) luoi that vs nhieu (phi P3)
def do_c():
    ra = {}
    g8 = json.loads((HC / "g08_ket_qua.json").read_text(encoding="utf-8"))
    g7 = json.loads((HC / "g07_ket_qua.json").read_text(encoding="utf-8"))
    nhom = {"that": [], "nhieu": []}
    for r in g8["chay"]:
        if r.get("swap_tk", 0) == 0 and r.get("seed") is None:
            continue  # ban khong swap / spread thap: bo, chi giu ban co phi P3
        nhom["nhieu" if r.get("seed") is not None else "that"].append(
            (float(r["lai_nam_pct"]), float(r["maxdd_pct"]), r.get("bt"), r.get("ma")))
    nhom7 = {"that": [], "nhieu": []}
    for r in g7["chay"]:
        if not r.get("swap") and r.get("seed") is None:
            continue
        nhom7["nhieu" if r.get("seed") is not None else "that"].append(
            (float(r["lai_nam_pct"]), float(r["maxdd_pct"]), None, r.get("ma")))
    for ten, g in (("g08_quan_tri_ro_AUDCAD_EURGBP", nhom), ("g07_luoi_5_tai_san", nhom7)):
        ra[ten] = {"n_that": len(g["that"]), "n_nhieu": len(g["nhieu"]),
                   "dd_max_that": round(max(x[1] for x in g["that"]), 1) if g["that"] else None,
                   "dd_max_nhieu": round(max(x[1] for x in g["nhieu"]), 1) if g["nhieu"] else None,
                   "lot": {f"{dm}|{lm}": {"that": ti(sum(not loai(x[0], x[1], dm, lm) for x in g["that"]), len(g["that"])),
                                          "nhieu": ti(sum(not loai(x[0], x[1], dm, lm) for x in g["nhieu"]), len(g["nhieu"]))}
                           for dm in DD_LUOI for lm in LAI_LUOI}}
    # 6 he Breakout P3 (phan kiem EURUSD 2016-2021 ~ 0,3 x 18,6 nam), so lay tu p3_so_sanh.txt / P3_KET_QUA.md
    nam = 0.3 * 18.6
    he = {"Breakout5(-2-2) luoi": ((37663 / 1e4) ** (1 / nam) - 1, 95.4, "DD > 80 %, 7 lan stop-out"),
          "Breakout2/3 ro hedge": ((9115 / 1e4) ** (1 / nam) - 1, 10.7, "lo"),
          "Breakout2-2 ro hedge": ((8762 / 1e4) ** (1 / nam) - 1, 17.6, "lo"),
          "Breakout1 lenh don": (math.exp(-0.408 / nam) - 1, 35.5, "lo"),
          "Template lenh don": (math.exp(-0.421 / nam) - 1, 35.2, "lo")}
    ra["breakout_p3"] = {k: {"lai_nam_pct": round(v[0] * 100, 2), "maxdd_pct": v[1], "ket_luan_cong": v[2],
                             "loai_65_10": loai(v[0] * 100, v[1], 65, 10),
                             "loai_50_3": loai(v[0] * 100, v[1], 50, 3)} for k, v in he.items()}
    return ra


def main():
    p1 = json.loads((HC / "p1_ket_qua.json").read_text(encoding="utf-8"))
    p4 = json.loads((HC / "p4_ket_qua.json").read_text(encoding="utf-8"))
    ra = {"nhan": "MO PHONG - hieu chuan nguong loai som (chi NHAN); khong phai tien, khong doi GIU/BO",
          "luoi_dd": DD_LUOI, "luoi_lai": LAI_LUOI,
          "a_15_o_mt5": do_a(p1), "b_nhieu": do_b(p4), "c_luoi_phi_p3": do_c()}
    (HC / "p6_ket_qua.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")

    a = ra["a_15_o_mt5"]
    print("(a) 15 o MT5 - lech mo phong-MT5:", a["lech_mo_phong_tru_mt5_diem_pct_nam"],
          "DD MT5 max", a["mt5_dd_max_pct"], "o MT5 lai", a["lai_mt5_o_lai"])
    for dc in ("duong", "v3"):
        print(f"  {dc}: lai_min -> giet_oan k/n (o) | lot k/n (o)   [DD khong doi ket qua o day: DD<=33%]")
        for lm in LAI_LUOI:
            x = a[dc][f"65|{lm}"]
            print(f"    {lm:>3}%: giet {x['giet_oan']['k']}/{x['giet_oan']['n']} {x['o_giet_oan']} | "
                  f"lot {x['lot']['k']}/{x['lot']['n']} {x['o_lot']}")
    b = ra["b_nhieu"]
    print("(b) nhieu - ti le LOT GIA (khong bi loai). n:", b["n"], b["nam"])
    for k in b["lot_gia"]:
        print("  ", k)
        for dm in DD_LUOI:
            print("     DD", dm, " ".join(f"{lm}%:{b['lot_gia'][k][f'{dm}|{lm}']['ti_le']}" for lm in LAI_LUOI))
        print("     luat chu (lai>0, DD<80):", b["lot_gia"][k]["chi_luat_chu_80|0"])
    c = ra["c_luoi_phi_p3"]
    for k in ("g08_quan_tri_ro_AUDCAD_EURGBP", "g07_luoi_5_tai_san"):
        x = c[k]
        print("(c)", k, "n", x["n_that"], x["n_nhieu"], "DDmax", x["dd_max_that"], x["dd_max_nhieu"])
        for key in ("65|10", "65|5", "65|3", "65|0", "50|3", "50|0", "80|0"):
            if key in x["lot"]:
                print("    ", key, x["lot"][key])
    for k, v in c["breakout_p3"].items():
        print("   ", k, v)


if __name__ == "__main__":
    main()
