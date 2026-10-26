# -*- coding: utf-8 -*-
"""xuong_toi_uu.py - TOI UU THAM SO SAU cho mot cau hinh (22/10/2026, Claude).

Hien tai ong dan thu 16 mau NGAU NHIEN o lot co dinh moi the; vong 2 quet luoi tho ~90 diem. Xuong lam khac o BON diem:
  1. SO SANH O RUI RO NGANG NHAU: lot khong phai chieu tim kiem; moi ung vien tot duoc keo lot toi sut giam muc tieu
     (`xuong_may.May.chuan_lot`) roi so `lai %/nam o do`. Giam mot chieu tim kiem, va dung cau hoi cua chu du an.
  2. DA DO PHAN GIAI (successive halving): sang loc tren lat cat IS ngan o lot tham chieu (rat re), giu 40 %, do lai tren
     IS day du, giu top, roi MOI keo lot. Tiet kiem ~3 lan so voi do day du moi diem.
  3. TIM CUC BO (pattern search): tu diem tot nhat do ±1 nac tung chieu, di chuyen khi tot hon, den khi het tot hon / het ngan sach.
  4. CAO NGUYEN + BEN THEO DOAN: ung vien chot phai co hang xom (±1 nac) van giu >= 70 % diem va lai duong tren cac doan lien tiep
     cua IS; diem chot = lai@DD x (0,4 + 0,6 x cao nguyen). OOS chi de GHI NHAN, khong de chon.
Chi tim trong vung tham so ma EA MT5 chay duoc (`xuong_may.TRUONG_QL_MT5`) de ket qua Python xac nhan duoc bang MT5.
Tiep tuc duoc: moi phep do luu theo khoa; chay lai cung the / cung hat khong do lai phep da co.
Moi so la MÔ PHỎNG; so OOS la NHAN.
"""
from __future__ import annotations

import json
import random
import time

from nhan import xuong_may as XM

#: Luoi quan li MIN HON `ong_dan.KHONG_GIAN_QL` / `vong2.LUOI_QL`. Lot khong co o day (duoc keo theo sut giam muc tieu).
LUOI_QL = {
    "tp_pct": [0.0008, 0.0012, 0.0018, 0.0025, 0.0035, 0.005, 0.008],
    "dca_buoc_pct": [0.002, 0.003, 0.004, 0.006, 0.008, 0.012, 0.018],
    "dca_toi_da": [0, 2, 3, 4, 6, 8, 10],
    "dca_he_so_lot": [1.0, 1.15, 1.3, 1.5, 1.75, 2.0],
    "hedge_khi_lo_pct": [0.0, 5.0, 10.0, 15.0, 20.0, 30.0],
    "hedge_ti_le": [0.5, 1.0, 1.5],
    "mo_khoa_pct": [0.002, 0.005, 0.01],
    "trail_kich_pct": [0.0, 0.002, 0.004],
    "trail_khoang_pct": [0.001, 0.002],
}
HE_SO_N = [0.5, 0.75, 1.0, 1.25, 1.5]
MACDINH_QL = {"tp_pct": 0.003, "dca_toi_da": 0, "hedge_khi_lo_pct": 0.0, "trail_kich_pct": 0.0}


def _gan(v, ds):
    return min(range(len(ds)), key=lambda i: abs(ds[i] - v)) if v is not None else 0


def khong_gian(t: dict, thu0: dict, cho_ma: list[str] | None = None, cho_khung: list[str] | None = None,
               chi_ql: bool = False) -> dict[str, list]:
    """Cac chieu tim kiem: 'ql.*' (quan li), 'th.*' (khoang tin hieu cua the), 'he_so_n' (spec DSL), 'ma', 'khung'.
    Gia tri hien tai cua `thu0` luon nam tren luoi (chen vao neu lech) de diem xuat phat la mot diem luoi."""
    chieu = {}
    q0 = XM.chuan_hoa_ql(thu0.get("ql"))
    for k, v in LUOI_QL.items():
        vs = set(v)
        if q0.get(k) is not None:
            vs.add(float(q0[k]) if isinstance(q0[k], (int, float)) else q0[k])
        chieu["ql." + k] = sorted(vs)
    if not chi_ql:
        for k, v in ((t.get("tin_hieu") or {}).get("khoang") or {}).items():
            if isinstance(v, list) and len(v) > 1:
                vs = set(v) | ({(thu0.get("tham") or {})[k]} if k in (thu0.get("tham") or {}) else set())
                chieu["th." + k] = sorted(vs)
        if (t.get("tin_hieu") or {}).get("kieu") == "spec":
            chieu["he_so_n"] = list(HE_SO_N)
        if cho_ma and len(cho_ma) > 1:
            chieu["ma"] = list(dict.fromkeys([thu0["ma"]] + list(cho_ma)))
        if cho_khung and len(cho_khung) > 1:
            chieu["khung"] = list(dict.fromkeys([thu0["khung"]] + list(cho_khung)))
    return chieu


def toa_tu_thu(kg: dict, thu: dict) -> tuple:
    q = XM.chuan_hoa_ql(thu.get("ql"))
    ra = []
    for k, vs in kg.items():
        if k.startswith("ql."):
            v = q.get(k[3:], 0.0 if k[3:] in ("hedge_khi_lo_pct", "trail_kich_pct", "dca_toi_da") else None)
            ra.append(_gan(v, vs) if isinstance(vs[0], (int, float)) else (vs.index(v) if v in vs else 0))
        elif k.startswith("th."):
            ra.append(_gan((thu.get("tham") or {}).get(k[3:]), vs))
        elif k == "he_so_n":
            ra.append(_gan(float(thu.get("he_so_n", 1.0)), vs))
        else:
            ra.append(vs.index(thu[k]) if thu.get(k) in vs else 0)
    return tuple(ra)


def thu_tu_toa(kg: dict, toa: tuple, goc: dict) -> dict:
    thu = {**goc, "ql": dict(XM.chuan_hoa_ql(goc.get("ql"))), "tham": dict(goc.get("tham") or {})}
    for (k, vs), i in zip(kg.items(), toa):
        if k.startswith("ql."):
            thu["ql"][k[3:]] = vs[i]
        elif k.startswith("th."):
            thu["tham"][k[3:]] = vs[i]
        elif k == "he_so_n":
            thu["he_so_n"] = vs[i]
        else:
            thu[k] = vs[i]
    thu["ql"] = XM.chuan_hoa_ql(thu["ql"])
    return thu


def hang_xom(kg: dict, toa: tuple):
    for j, vs in enumerate(kg.values()):
        for d in (-1, 1):
            x = list(toa)
            x[j] += d
            if 0 <= x[j] < len(vs):
                yield tuple(x)


def chuan_hoa_thu(thu: dict) -> dict:
    return {**thu, "ql": XM.chuan_hoa_ql(thu.get("ql")), "tham": dict(thu.get("tham") or {})}


def khoa_thu(thu: dict) -> str:
    return json.dumps({k: thu.get(k) for k in ("ma", "khung", "tham", "he_so_n")} | {"ql": XM.chuan_hoa_ql(thu.get("ql"))},
                      sort_keys=True, default=str)


def toi_uu(may: XM.May, t: dict, thu0: dict, ngan_sach: int = 60, hat: int = 1, cho_ma: list[str] | None = None,
           cho_khung: list[str] | None = None, chi_ql: bool = False, so_chot: int = 3, in_ra=print) -> dict:
    """Tim cau hinh tot nhat quanh `thu0` cho the `t`. `ngan_sach` = so diem khac nhau di vao rung A (sang loc re).
    -> {"tot_nhat": {...}, "xep_hang": [...], "goc": {...}, "so_phep_do", "giay", "nhan"} hoac {"loi": ...}."""
    t0, chay0 = time.time(), may.so_chay
    thu0 = chuan_hoa_thu(thu0)
    rng = random.Random("%s|%s" % (t["id"], hat))
    kg = khong_gian(t, thu0, cho_ma, cho_khung, chi_ql)
    g0 = toa_tu_thu(kg, thu0)
    cuoi = may.cuoi_is
    A, B = (0.0, 0.45 * cuoi), (0.0, cuoi)

    def lo(thus, doan):
        return may.chay_lo([(t, x, doan, may.lot_ref) for x in thus])

    # ---- 1. tap diem khoi dau: goc + hang xom goc + ngau nhien
    diem_a = [g0] + list(hang_xom(kg, g0))
    thu_het = {g0}
    n_thu = 0
    while len(diem_a) < ngan_sach and n_thu < ngan_sach * 20:
        n_thu += 1
        x = tuple(rng.randrange(len(vs)) for vs in kg.values())
        if x not in thu_het and x not in diem_a:
            diem_a.append(x)
    diem_a = diem_a[:max(ngan_sach, len(kg) * 2 + 1)]
    thu_a = [thu_tu_toa(kg, x, thu0) for x in diem_a]
    # chuan hoa -> bo trung (hai toa do khac nhau co the cho cung ql sau chuan hoa)
    thay, ds = set(), []
    for x, th in zip(diem_a, thu_a):
        k = khoa_thu(th)
        if k not in thay:
            thay.add(k)
            ds.append((x, th))
    # ---- 2. rung A (lat cat ngan, lot tham chieu) -> giu 40 %
    ra_a = lo([th for _, th in ds], A)
    sa = sorted(zip(ds, ra_a), key=lambda z: -XM.diem_tho(z[1]))
    if all(r.get("loi") for _, r in sa):
        return {"loi": sa[0][1]["loi"], "so_phep_do": may.so_chay - chay0}
    giu = [x for (x, th), r in sa[:max(6, int(len(sa) * 0.4))]]
    if g0 not in giu:
        giu.append(g0)                                              # luon do lai diem goc o rung B (de so sanh)
    # ---- 3. rung B (IS day du, lot tham chieu)
    diem_b = {}

    def do_b(toas):
        moi = [x for x in toas if x not in diem_b]
        rs = lo([thu_tu_toa(kg, x, thu0) for x in moi], B)
        for x, r in zip(moi, rs):
            diem_b[x] = XM.diem_tho(r)
    do_b(giu)
    # ---- 4. tim cuc bo tu diem tot nhat
    nguong_ps = max(12, ngan_sach // 2)
    da_mo, buoc = set(), 0
    while buoc < nguong_ps:
        ung = sorted((x for x in diem_b if x not in da_mo), key=lambda x: -diem_b[x])
        if not ung or diem_b[ung[0]] <= 0:
            break
        da_mo.add(ung[0])
        xom = [x for x in hang_xom(kg, ung[0]) if x not in diem_b]
        do_b(xom)
        buoc += max(1, len(xom))
    # ---- 5. chot: top `so_chot` khac nhau -> keo lot -> cao nguyen -> diem chot
    top = sorted(diem_b, key=lambda x: -diem_b[x])
    chot, thay = [], set()
    for x in top:
        th = thu_tu_toa(kg, x, thu0)
        k = khoa_thu(th)
        if k in thay:
            continue
        thay.add(k)
        chot.append((x, th))
        if len(chot) >= so_chot:
            break
    xep = []
    for x, th in chot:
        cl = may.chuan_lot(t, th)
        d = may.diem(cl)
        cn = cao_nguyen(may, t, kg, x, thu0, diem_b, B)
        ben = may.ben_theo_doan(t, th, cl["lot"]) if cl["tinh_trang"] in ("vua", "tran_lot") else None
        fct = 0.4 + 0.6 * (cn if cn is not None else 0.0)
        xep.append({"thu": th, "lot": cl["lot"], "tinh_trang": cl["tinh_trang"], "lai_o_dd": cl["lai_o_dd"], "diem": d,
                    "diem_chot": d * fct if d > 0 else d, "cao_nguyen": cn, "ben": ben, "is": cl["r"],
                    "diem_tho_B": round(diem_b[x], 3)})
    xep.sort(key=lambda z: -z["diem_chot"])
    tot = xep[0] if xep else None
    goc = None
    if tot:
        cl0 = may.chuan_lot(t, thu0)
        goc = {"thu": thu0, "lot": cl0["lot"], "tinh_trang": cl0["tinh_trang"], "lai_o_dd": cl0["lai_o_dd"], "is": cl0["r"],
               "diem": may.diem(cl0)}
        lot = tot["lot"]
        tot["oos"] = may.oos_(t, tot["thu"], lot) if tot["tinh_trang"] in ("vua", "tran_lot") else None
        tot["toan"] = may.toan(t, tot["thu"], lot) if tot["tinh_trang"] in ("vua", "tran_lot") else None
        if goc["tinh_trang"] in ("vua", "tran_lot"):
            goc["oos"] = may.oos_(t, thu0, goc["lot"])
        # LOT KHUYEN NGHI: keo tren TOAN KY toi `dd_khuyen_nghi` (de chua bien so: sut giam OOS thuong xau hon IS) - chi de DAT LOT,
        # khong dung de chon cau hinh. Day moi la con so dung voi cau hoi "lai bao nhieu o sut giam <= 80 %".
        kn = may.chuan_lot(t, tot["thu"], (0.0, 1.0), dd=may.dd_khuyen_nghi)
        tot["khuyen_nghi"] = {"lot": kn["lot"], "lai_pct_nam": kn["lai_o_dd"], "tinh_trang": kn["tinh_trang"],
                              "sut_giam_pct": (kn["r"] or {}).get("sut_giam_pct"), "dd_muc_tieu": may.dd_khuyen_nghi}
    in_ra("xuong toi_uu %-34s %3d phep do %5.1fs | goc lai@DD %s -> tot %s (lot %s, cao nguyen %s)" % (
        t["id"][:34], may.so_chay - chay0, time.time() - t0, (goc or {}).get("lai_o_dd"), (tot or {}).get("lai_o_dd"),
        (tot or {}).get("lot"), (tot or {}).get("cao_nguyen")))
    return {"tot_nhat": tot, "xep_hang": xep, "goc": goc, "so_chieu": len(kg), "so_diem_A": len(ds),
            "so_phep_do": may.so_chay - chay0, "giay": round(time.time() - t0, 1), "dd_muc_tieu": may.dd,
            "nhan": "MÔ PHỎNG (Python, lot thật, sụt giảm kéo về mục tiêu); OOS chỉ là NHÃN"}


def cao_nguyen(may: XM.May, t: dict, kg: dict, toa: tuple, thu0: dict, diem_b: dict, doan: tuple) -> float | None:
    """Ti le hang xom (±1 nac) con giu >= 70 % diem tho cua chinh no (rung B) va khong stop-out. None neu diem <= 0 / khong co hang xom."""
    d0 = diem_b.get(toa)
    if d0 is None or d0 <= 0:
        return None
    xom = list(hang_xom(kg, toa))
    if not xom:
        return None
    moi = [x for x in xom if x not in diem_b]
    if moi:
        rs = may.chay_lo([(t, thu_tu_toa(kg, x, thu0), doan, may.lot_ref) for x in moi])
        for x, r in zip(moi, rs):
            diem_b[x] = XM.diem_tho(r)
    return round(sum(1 for x in xom if diem_b[x] >= 0.7 * d0) / len(xom), 2)


def the_ung_vien_moi(t: dict, ket: dict, hau_to: str = "xo") -> dict | None:
    """Ket qua toi uu -> {"thu": ..., "kq": ...} theo DANG `ong_dan.buoc_toi_uu` (de `buoc_loc` / `sinh_mt5` doc duoc `tot_nhat`):
    thu cua cau hinh tot nhat voi lot da keo, kq = ket qua TOAN KY o lot do (nhu `ong_dan.danh_gia`)."""
    tot = (ket or {}).get("tot_nhat")
    if not tot or tot.get("tinh_trang") not in ("vua", "tran_lot"):
        return None
    thu = dict(tot["thu"])
    thu["ql"] = dict(thu["ql"], lot_tren_1000=tot["lot"])
    return {"thu": thu, "lot": tot["lot"], "diem": tot["diem"]}
