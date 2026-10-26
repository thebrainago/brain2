# -*- coding: utf-8 -*-
"""xuong.py - XUONG TO HOP (22/10/2026, Claude): tu cac he dat -> boc tach -> sinh to hop -> sang loc -> toi uu sau -> dang ky.

Chu du an: "tiep tuc xay code de xu ly cac he dat: toi uu tham so, boc tach co che de dung cho chien luoc khac, ket hop them tham so va
phuong phap, ket hop cheo cac he pass voi nhau (+ cach tao va xay to hop)". Thiet ke: `tai_lieu/XUONG.md`.

DONG CHAY (mot lan `chay`):
  0. NAP CHA      cac the dat (trang thai DAT_LOC / DAT_CUOI ...) lay `tot_nhat.thu` -> keo lot toi sut giam muc tieu -> PHAN RA
                  (tin hieu hay quan li ganh?) -> tach NGUYEN TU vao kho (`xuong_tach`).
  1. SINH         cac toan tu (`xuong_toan_tu`) sinh ung vien; bo trung; bo cai da co trong cache ong dan.
  2. SANG A       lat cat IS 45 % o lot tham chieu (re) -> giu 35 %.   3. SANG B  IS day du -> giu top.
  4. KEO LOT      moi ung vien con lai keo lot toi sut giam muc tieu (rui ro ngang nhau) -> xep theo lai@DD.
  5. TOI UU SAU   top N: `xuong_toi_uu` (halving + pattern search + cao nguyen); OOS chi de ghi nhan.
  6. DANG KY      ung vien dat: ghi vao cache ong dan (buoc `toi_uu`, `tot_nhat` o lot khuyen nghi tren TOAN KY) de `ong_dan loc` ->
                  `sinh_mt5` dua len MT5 xac nhan nhu moi the khac. Bao cao: `reports/xuong/XUONG.md`.
Moi so la MÔ PHỎNG Python (lot that, ky quy, stop-out, phi san neu co `reports/phi_san/` - khong thi PHÍ TẠM). MT5 moi la phan xu cuoi.

Chay:  python -m nhan.xuong chay [--phut 30] [--song-song 4] [--dd 60] [--toan-tu cay_quan_li,bo_phieu] [--khong-ghi]
       python -m nhan.xuong cha          (chi nap cha + phan ra + nguyen tu)
       python -m nhan.xuong toi-uu ID    (toi uu sau mot the, in ket qua)
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np

from nhan import kho_co_che as KHO
from nhan import ong_dan as OD
from nhan import xuong_danh_muc as DM
from nhan import xuong_may as XM
from nhan import xuong_tach as TA
from nhan import xuong_toan_tu as TT
from nhan import xuong_toi_uu as TU

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "reports" / "xuong"
TEP_LUU = GOC / "data" / "xuong" / "xuong.sqlite"
CHA_TRANG_THAI = ("DAT_LOC", "DAT_CUOI")


# ------------------------------------------------------------------------------------------------- bang thong ke toan tu
def _tk(tep: Path | None):
    if not tep:
        return None
    Path(tep).parent.mkdir(parents=True, exist_ok=True)
    cn = sqlite3.connect(str(tep), timeout=60)
    cn.execute("CREATE TABLE IF NOT EXISTS toan_tu (ten TEXT PRIMARY KEY, so_sinh INT DEFAULT 0, so_qua_a INT DEFAULT 0, "
               "so_qua_b INT DEFAULT 0, so_chot INT DEFAULT 0)")
    cn.execute("CREATE TABLE IF NOT EXISTS cha (khoa TEXT PRIMARY KEY, json TEXT)")
    cn.execute("CREATE TABLE IF NOT EXISTS tac_vu (khoa TEXT PRIMARY KEY, json TEXT)")
    cn.commit()
    return cn


def trong_so_toan_tu(cn_tk, ten_list: list[str]) -> dict[str, float]:
    """Trong so de chia ngan sach giua cac toan tu: (so_chot + 1) / (so_sinh + 8) (lam tron cong - toan tu moi van duoc thu)."""
    w = {}
    for ten in ten_list:
        r = cn_tk.execute("SELECT so_sinh, so_chot FROM toan_tu WHERE ten=?", (ten,)).fetchone() if cn_tk else None
        w[ten] = ((r[1] if r else 0) + 1.0) / ((r[0] if r else 0) + 8.0)
    return w


def ghi_toan_tu(cn_tk, ten: str, **d) -> None:
    if not cn_tk:
        return
    cn_tk.execute("INSERT OR IGNORE INTO toan_tu (ten) VALUES (?)", (ten,))
    for k, v in d.items():
        cn_tk.execute("UPDATE toan_tu SET %s = %s + ? WHERE ten=?" % (k, k), (int(v), ten))
    cn_tk.commit()


# ------------------------------------------------------------------------------------------------- nap cha
def doc_cha_tu_db(cn, trang_thai=CHA_TRANG_THAI, cha_id: list[str] | None = None, gan_dat: bool = False) -> list[tuple[dict, dict, dict]]:
    """[(the, thu_tot_nhat, kq_tot_nhat)] cua cac the dat. `gan_dat`: them the co lai > 5 %/nam, khong stop-out (chua qua loc)."""
    ra = []
    for t, buoc, tt, kq in OD.cac_the(cn):
        tot = (kq or {}).get("tot_nhat") or {}
        thu, r = tot.get("thu") or {}, tot.get("kq") or {}
        if not thu.get("ma") or r.get("loi"):
            continue
        if cha_id:
            if t["id"] not in cha_id:
                continue
        elif tt not in trang_thai:
            if not (gan_dat and float(r.get("lai_pct_nam") or 0) > 5 and not r.get("so_stop_out") and not r.get("chay")):
                continue
        ra.append((t, thu, r))
    return ra


def _tac_vu_cha(args):
    """Cong nhan: keo lot + phan ra cho mot cha. args = (t, thu, so_mau, hat)."""
    may = XM._MAY_CN
    t, thu, so_mau, hat = args
    cl = may.chuan_lot(t, thu)
    if cl["tinh_trang"] not in ("vua", "tran_lot"):
        return {"id": t["id"], "tinh_trang": cl["tinh_trang"], "diem": may.diem(cl), "lot": cl["lot"], "phan_ra": None}
    ket = TA.phan_ra(may, t, thu, cl["lot"], so_mau=so_mau, hat=hat)
    return {"id": t["id"], "tinh_trang": cl["tinh_trang"], "diem": cl["lai_o_dd"], "lot": cl["lot"], "r": cl["r"], "phan_ra": ket}


def nap_cha(cn, may: XM.May, cn_tk, trang_thai=CHA_TRANG_THAI, cha_id=None, gan_dat=False, so_mau: int = 6, hat: int = 1,
            ghi_nguyen_tu: bool = True, in_ra=print) -> list[TT.Cha]:
    ds = doc_cha_tu_db(cn, trang_thai, cha_id, gan_dat)
    in_ra("xuong: %d he cha (trang thai %s%s)" % (len(ds), "/".join(trang_thai), ", + gan dat" if gan_dat else ""))
    viec = [(t, thu, so_mau, hat) for t, thu, _ in ds]
    khoa = lambda t, thu: XM._kh("cha", t["id"], XM.chuan_hoa_ql(thu.get("ql")), thu["ma"], thu["khung"], thu.get("tham"), may.dd, may.cfg.get("von"),
                                 may.cfg.get("san_phi"))                                                       # noqa: E731
    kq = []
    cho = []
    for (t, thu, _r), v in zip(ds, viec):
        c = cn_tk.execute("SELECT json FROM cha WHERE khoa=?", (khoa(t, thu),)).fetchone() if cn_tk else None
        if c:
            kq.append(json.loads(c[0]))
        else:
            cho.append(v)
            kq.append(None)
    if cho:
        pool = getattr(may, "_pool", None)
        res = list(pool.map(_tac_vu_cha, cho)) if pool is not None and len(cho) > 1 else [_tac_vu_cha_local(may, v) for v in cho]
        it = iter(res)
        for i, (t, thu, _r) in enumerate(ds):
            if kq[i] is None:
                kq[i] = next(it)
                if cn_tk:
                    cn_tk.execute("INSERT OR REPLACE INTO cha VALUES (?,?)", (khoa(t, thu), json.dumps(kq[i], default=str)))
        if cn_tk:
            cn_tk.commit()
    cha = []
    atoms = []
    for (t, thu, r), k in zip(ds, kq):
        pr = k.get("phan_ra") or {}
        c = TT.Cha(t, thu, diem=float(k.get("diem") or 0.0), nhan=pr.get("nhan"))
        c.k = k
        cha.append(c)
        if ghi_nguyen_tu and pr and k.get("tinh_trang") in ("vua", "tran_lot"):
            atoms += TA.nguyen_tu(t, thu, pr, k.get("r"))
    if atoms and ghi_nguyen_tu:
        moi = KHO.them(atoms)
        in_ra("xuong: tach %d nguyen tu vao kho co che (%d moi)" % (len(atoms), moi))
    return cha


def _tac_vu_cha_local(may, v):
    XM._MAY_CN, truoc = may, XM._MAY_CN
    try:
        return _tac_vu_cha(v)
    finally:
        XM._MAY_CN = truoc


# ------------------------------------------------------------------------------------------------- tac vu toi uu / keo lot (cong nhan)
def _tac_vu_chot(args):
    """Cong nhan: keo lot + toi uu sau mot ung vien. args = (t, thu, ngan_sach, hat, chi_ql, cho_ma, cho_khung)."""
    may = XM._MAY_CN
    t, thu, ngan_sach, hat, chi_ql, cho_ma, cho_khung = args
    try:
        return TU.toi_uu(may, t, thu, ngan_sach=ngan_sach, hat=hat, chi_ql=chi_ql, cho_ma=cho_ma, cho_khung=cho_khung, in_ra=lambda *a: None)
    except Exception as e:  # noqa: BLE001
        return {"loi": "%s: %s" % (type(e).__name__, str(e)[:200])}


def _tac_vu_keo_lot(args):
    may = XM._MAY_CN
    t, thu = args
    cl = may.chuan_lot(t, thu)
    return {"lot": cl["lot"], "lai_o_dd": cl["lai_o_dd"], "tinh_trang": cl["tinh_trang"], "diem": may.diem(cl),
            "is": cl["r"] if cl["tinh_trang"] != "loi" else {"loi": cl["r"].get("loi")}}


def _ap_tac_vu(may: XM.May, ham, viec: list):
    pool = getattr(may, "_pool", None)
    if pool is not None and len(viec) > 1:
        return list(pool.map(ham, viec))
    ra = []
    for v in viec:
        XM._MAY_CN, truoc = may, XM._MAY_CN
        try:
            ra.append(ham(v))
        finally:
            XM._MAY_CN = truoc
    return ra


# ------------------------------------------------------------------------------------------------- dang ky vao ong dan
def dang_ky(cn, t: dict, tot: dict, may: XM.May, cfg: dict, nhan_xuong: dict) -> dict | None:
    """Ghi ung vien vao cache ong dan o buoc `toi_uu`, `tot_nhat` = phep thu o LOT KHUYEN NGHI do tren TOAN KY bang `ong_dan.danh_gia`
    (cung dang ket qua `buoc_toi_uu`) de `ong_dan loc` / `sinh_mt5` doc duoc. -> kq ong_dan hoac None."""
    kn = tot.get("khuyen_nghi") or {}
    if kn.get("tinh_trang") not in ("vua", "tran_lot") or not kn.get("lot"):
        return None
    thu = {k: v for k, v in tot["thu"].items() if k in ("ma", "khung", "tham", "ql")}
    thu["ql"] = dict(XM.chuan_hoa_ql(thu["ql"]), lot_tren_1000=kn["lot"])
    the = {k: v for k, v in t.items() if not k.startswith("_")}
    r = OD.danh_gia(XM.May.the_cua(the, tot["thu"]), thu, cfg)
    if r.get("loi"):
        return None
    with cn:
        OD._luu(cn, the, "toi_uu", "DA_TOI_UU", {"tot_nhat": {"thu": thu, "kq": r}, "so_thu": 1, "xuong": nhan_xuong})
        OD._ghi_nk(cn, "xuong", the["id"], json.dumps(nhan_xuong, ensure_ascii=False, default=str)[:900])
    return r


# ------------------------------------------------------------------------------------------------- chay
def chay(cn, cfg: dict | None = None, *, trang_thai=CHA_TRANG_THAI, cha_id=None, gan_dat: bool = False, toan_tu: list[str] | None = None,
         tran: int = 24, phut: float = 30.0, song_song: int = 1, dd: float = 60.0, hat: int = 1, so_toi_uu: int = 5,
         ngan_sach_toi_uu: int = 40, tep_luu: Path | None = TEP_LUU, ghi: bool = True, ra: Path | None = None, in_ra=print) -> dict:
    cfg = cfg or OD.cau_hinh()
    t0 = time.time()
    han = t0 + phut * 60
    may = XM.May(cfg, dd_muc_tieu=dd, tep_luu=tep_luu, dd_khuyen_nghi=dd)
    cn_tk = _tk(tep_luu)
    toan_tu = [x for x in (toan_tu or list(TT.TEN_TOAN_TU)) if x in TT.TOAN_TU]
    rng = random.Random(hat)
    may.mo_song_song(song_song)
    ket = {"ngay": time.strftime("%Y-%m-%d %H:%M"), "dd_muc_tieu": dd, "toan_tu": {}, "chot": []}
    try:
        cha = nap_cha(cn, may, cn_tk, trang_thai, cha_id, gan_dat, hat=hat, ghi_nguyen_tu=ghi, in_ra=in_ra)
        ket["so_cha"] = len(cha)
        ket["cha"] = [{"id": c.id, "ma": c.ma, "khung": c.khung, "lai_o_dd": round(c.diem, 2), "nhan": c.nhan} for c in cha]
        if len(cha) < 1:
            ket["ly_do"] = "khong co he cha"
            return ket
        # nguyen tu quan li da dang tu kho (do xuong ghi) + tu cha
        ql_atoms = [{"ql": c.ql, "tu": c.id, "nhan": c.nhan} for c in cha if c.diem > 0]
        ql_atoms = TA.da_dang(ql_atoms, 16) if ql_atoms else []
        tai_san = [(m_, kh) for m_ in OD.ma_co_du_lieu(cfg) for kh in (cfg.get("khung") or ["H1"])][:60]
        # ---- 1. sinh
        w = trong_so_toan_tu(cn_tk, toan_tu)
        tong_w = sum(w.values()) or 1.0
        ung, da_co = [], {r[0] for r in cn.execute("SELECT id FROM the")}
        for ten in toan_tu:
            tran_ten = max(4, int(round(tran * len(toan_tu) * w[ten] / tong_w)))
            xs = TT.sinh(ten, cha, rng, tran_ten, **({"atoms": ql_atoms} if ten == "cay_quan_li" else {"tai_san": rng.sample(tai_san, min(8, len(tai_san)))} if ten == "chuyen_ma" else {}))
            xs = [x for x in xs if x["id"] not in da_co]
            for x in xs:
                x["_toan_tu"] = ten
            ung += xs
            ket["toan_tu"][ten] = {"sinh": len(xs)}
            ghi_toan_tu(cn_tk, ten, so_sinh=len(xs))
        thay, uniq = set(), []
        for x in ung:
            if x["id"] not in thay:
                thay.add(x["id"])
                uniq.append(x)
        ung = uniq
        in_ra("xuong: sinh %d ung vien (%s)" % (len(ung), ", ".join("%s %d" % (k, v["sinh"]) for k, v in ket["toan_tu"].items())))
        if not ung:
            return ket
        # ---- 2/3. sang A, B (chay_lo song song min)
        A, B = (0.0, 0.45 * may.cuoi_is), (0.0, may.cuoi_is)
        ra_a = may.chay_lo([(x, x["_thu"], A, may.lot_ref) for x in ung])
        sa = sorted(zip(ung, ra_a), key=lambda z: -XM.diem_tho(z[1]))
        giu_a = [x for x, r in sa[:max(8, int(len(sa) * 0.35))] if XM.diem_tho(r) > -50]
        for x, r in sa:
            if x in giu_a:
                ghi_toan_tu(cn_tk, x["_toan_tu"], so_qua_a=1)
                ket["toan_tu"][x["_toan_tu"]]["qua_A"] = ket["toan_tu"][x["_toan_tu"]].get("qua_A", 0) + 1
        in_ra("xuong: sang A giu %d / %d (%.0fs)" % (len(giu_a), len(ung), time.time() - t0))
        if time.time() > han or not giu_a:
            return ket
        ra_b = may.chay_lo([(x, x["_thu"], B, may.lot_ref) for x in giu_a])
        sb = sorted(zip(giu_a, ra_b), key=lambda z: -XM.diem_tho(z[1]))
        giu_b = [x for x, r in sb[:max(6, so_toi_uu * 3)] if XM.diem_tho(r) > 0]
        for x in giu_b:
            ghi_toan_tu(cn_tk, x["_toan_tu"], so_qua_b=1)
            ket["toan_tu"][x["_toan_tu"]]["qua_B"] = ket["toan_tu"][x["_toan_tu"]].get("qua_B", 0) + 1
        in_ra("xuong: sang B giu %d (%.0fs)" % (len(giu_b), time.time() - t0))
        if time.time() > han or not giu_b:
            return ket
        # ---- 4. keo lot
        kl = _ap_tac_vu(may, _tac_vu_keo_lot, [(x, x["_thu"]) for x in giu_b])
        xep = sorted(zip(giu_b, kl), key=lambda z: -z[1]["diem"])
        top = [(x, k) for x, k in xep if k["tinh_trang"] in ("vua", "tran_lot") and k["diem"] > 0][:so_toi_uu]
        in_ra("xuong: keo lot -> %d ung vien co lai o DD %s%% (%.0fs)" % (len(top), dd, time.time() - t0))
        # ---- 5. toi uu sau
        if top and time.time() < han:
            kqs = _ap_tac_vu(may, _tac_vu_chot, [(x, x["_thu"], ngan_sach_toi_uu, hat, True, None, None) for x, _ in top])
        else:
            kqs = []
        # ---- 6. dang ky + bao cao
        goc_cha = {c.id: c for c in cha}
        for (x, k), kq in zip(top, kqs):
            tot = (kq or {}).get("tot_nhat")
            if not tot or kq.get("loi"):
                ket["chot"].append({"id": x["id"], "toan_tu": x["_toan_tu"], "loi": (kq or {}).get("loi", "khong chot duoc")})
                continue
            cha_diem = max([goc_cha[i].diem for i in x["xuong"]["cha"] if i in goc_cha], default=0.0)
            nhan_x = {"toan_tu": x["_toan_tu"], "cha": x["xuong"]["cha"], "mo_ta": x["xuong"]["mo_ta"], "lai_o_dd": tot["lai_o_dd"],
                      "dd_muc_tieu": dd, "cha_tot_nhat_lai_o_dd": round(cha_diem, 2),
                      "oos": {a: (tot.get("oos") or {}).get(a) for a in ("lai_pct_nam", "sut_giam_pct")},
                      "cao_nguyen": tot.get("cao_nguyen"), "khuyen_nghi": tot.get("khuyen_nghi"), "nhan": "MÔ PHỎNG"}
            dk = None
            if ghi:
                dk = dang_ky(cn, x, tot, may, cfg, nhan_x)
            ghi_toan_tu(cn_tk, x["_toan_tu"], so_chot=1)
            ket["toan_tu"][x["_toan_tu"]]["chot"] = ket["toan_tu"][x["_toan_tu"]].get("chot", 0) + 1
            ket["chot"].append(dict(nhan_x, id=x["id"], ten=x["ten"], thu=tot["thu"], lot=tot["lot"], ben=tot.get("ben"),
                                    dang_ky=bool(dk), lai_toan_ky=(dk or {}).get("lai_pct_nam"), dd_toan_ky=(dk or {}).get("sut_giam_pct"),
                                    goc=(kq.get("goc") or {}).get("lai_o_dd")))
        ket["danh_muc"] = _danh_muc_tu_chot(cn, cfg, cha, ket["chot"], dd, in_ra)
        ket["giay"] = round(time.time() - t0, 1)
        ket["so_phep_do"] = may.so_chay
        return ket
    finally:
        may.dong()
        if ghi:
            ghi_bao_cao(ket, ra)


def _danh_muc_tu_chot(cn, cfg: dict, cha: list, chot: list, dd: float, in_ra=print) -> dict | None:
    """Ghep CHEO: cac cha + cac ung vien vua chot (deu o lot khuyen nghi) -> bang lot danh muc (Python, xap xi)."""
    ung = []
    for c in cha:
        if c.diem > 0 and getattr(c, "k", {}).get("lot"):
            ung.append((c.t, c.thu, float(c.k["lot"])))
    for x in chot:
        if x.get("dang_ky") and x.get("thu") and (x.get("khuyen_nghi") or {}).get("lot"):
            ung.append(({"id": x["id"], "tin_hieu": None, "_chot": True}, x["thu"], float(x["khuyen_nghi"]["lot"])))
    if len(ung) < 2:
        return None
    ung2 = []
    for t, thu, lot in ung:
        if t.get("_chot"):
            rows = [x for x in OD.cac_the(cn) if x[0]["id"] == t["id"]]
            if not rows:
                continue
            t = rows[0][0]
        ung2.append((t, thu, lot))
    may = XM.May(cfg, dd_muc_tieu=dd, giu_duong_von=True, dd_khuyen_nghi=dd)
    d = DM.danh_muc(may, ung2, dd_muc=dd)
    if d.get("thanh_vien"):
        in_ra("xuong: danh muc %d the, lai %.1f%%/nam o DD %.1f%% (rieng tot nhat %.1f)" % (
            len(d["thanh_vien"]), d["lai_pct_nam"], d["sut_giam_pct"], d["lai_tot_nhat_rieng"]))
    return d


def ghi_bao_cao(ket: dict, ra: Path | None = None) -> Path:
    d = Path(ra or RA)
    d.mkdir(parents=True, exist_ok=True)
    (d / "ket_qua.json").write_text(json.dumps(ket, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    l = ["# XƯỞNG TỔ HỢP — %s" % ket.get("ngay", ""), "",
         "Mọi số là **MÔ PHỎNG** Python (lot thật, ký quỹ, stop-out, phí sàn nếu có `reports/phi_san/`, không thì PHÍ TẠM). "
         "Mỗi ứng viên được kéo lot tới **sụt giảm mục tiêu %s %%** trên IS (70 %% đầu) để so sánh ở rủi ro ngang nhau; "
         "OOS (30 %% cuối) chỉ là NHÃN. Muốn biết thật: MT5 (`ong_dan sinh_mt5`).\n" % ket.get("dd_muc_tieu"),
         "**Cha:** %s hệ. **Giây:** %s. **Phép đo engine:** %s." % (ket.get("so_cha"), ket.get("giay"), ket.get("so_phep_do")), ""]
    if ket.get("cha"):
        from collections import Counter
        c = Counter(x.get("nhan") or "?" for x in ket["cha"])
        l += ["## Cha: ai gánh, tín hiệu hay quản lí?", "", "| Nhãn | Số hệ |", "|---|---|"] + ["| %s | %d |" % kv for kv in c.most_common()] + [""]
    if ket.get("toan_tu"):
        l += ["## Toán tử", "", "| Toán tử | Sinh | Qua A | Qua B | Chốt |", "|---|---|---|---|---|"]
        for k, v in ket["toan_tu"].items():
            l.append("| %s | %s | %s | %s | %s |" % (k, v.get("sinh", 0), v.get("qua_A", 0), v.get("qua_B", 0), v.get("chot", 0)))
        l.append("")
    dm = ket.get("danh_muc")
    if dm and dm.get("thanh_vien"):
        l += ["## Danh mục chạy cùng lúc (ghép chéo)", "",
              "Lãi **%s %%/năm** ở sụt giảm **%s %%** (hệ riêng tốt nhất: %s %%), tương quan ngày tối đa %s, %s năm. Hệ số lot chung %s. *%s*" % (
                  dm["lai_pct_nam"], dm["sut_giam_pct"], dm["lai_tot_nhat_rieng"], dm["tuong_quan_max"], dm["so_nam"], dm["he_so_lot_chung"], dm["nhan"]),
              "", "| Thẻ | Lot/1000 vốn | Lãi riêng @DD |", "|---|---|---|"]
        l += ["| %s | %s | %s |" % (x["id"], x["lot"], x["lai_rieng_o_dd"]) for x in dm["thanh_vien"]] + [""]
    elif dm and dm.get("loi"):
        l += ["## Danh mục", "", dm["loi"], ""]
    if ket.get("chot"):
        l += ["## Chốt", "", "| # | Toán tử | Mô tả | Lãi %/năm @DD mục tiêu | Cha tốt nhất | OOS lãi/DD | Cao nguyên | Lot khuyến nghị: lãi · DD (toàn kỳ) | Đăng ký |",
              "|---|---|---|---|---|---|---|---|---|"]
        for i, c in enumerate(ket["chot"], 1):
            if c.get("loi"):
                l.append("| %d | %s | %s | LỖI: %s | | | | | |" % (i, c["toan_tu"], c["id"], c["loi"]))
                continue
            o = c.get("oos") or {}
            kn = c.get("khuyen_nghi") or {}
            l.append("| %d | %s | %s | %s | %s | %s / %s | %s | lot %s: %s%% · %s%% | %s |" % (
                i, c["toan_tu"], (c.get("mo_ta") or "")[:90], c.get("lai_o_dd"), c.get("cha_tot_nhat_lai_o_dd"), o.get("lai_pct_nam"),
                o.get("sut_giam_pct"), c.get("cao_nguyen"), kn.get("lot"), kn.get("lai_pct_nam"), kn.get("sut_giam_pct"),
                "có" if c.get("dang_ky") else "không"))
        l += ["", "Đăng ký = đã ghi vào cache ống dẫn (bước `toi_uu`); chạy `python ong_dan.py loc` rồi `python ong_dan.py sinh_mt5` để đưa lên MT5."]
    p = d / "XUONG.md"
    p.write_text("\n".join(l) + "\n", encoding="utf-8")
    return p


# ------------------------------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sp = ap.add_subparsers(dest="lenh")
    c = sp.add_parser("chay")
    c.add_argument("--phut", type=float, default=30.0)
    c.add_argument("--song-song", type=int, default=1)
    c.add_argument("--dd", type=float, default=60.0)
    c.add_argument("--tran", type=int, default=24, help="so ung vien trung binh moi toan tu")
    c.add_argument("--toan-tu", default="")
    c.add_argument("--hat", type=int, default=1)
    c.add_argument("--so-toi-uu", type=int, default=5)
    c.add_argument("--ngan-sach-toi-uu", type=int, default=40)
    c.add_argument("--cha-id", default="")
    c.add_argument("--gan-dat", action="store_true")
    c.add_argument("--khong-ghi", action="store_true")
    h = sp.add_parser("cha")
    h.add_argument("--song-song", type=int, default=1)
    h.add_argument("--dd", type=float, default=60.0)
    h.add_argument("--gan-dat", action="store_true")
    o = sp.add_parser("toi-uu")
    o.add_argument("id")
    o.add_argument("--dd", type=float, default=60.0)
    o.add_argument("--ngan-sach", type=int, default=60)
    a = ap.parse_args(argv)
    cn = OD._db()
    cfg = OD.cau_hinh()
    if a.lenh == "chay":
        k = chay(cn, cfg, toan_tu=[x for x in a.toan_tu.split(",") if x] or None, tran=a.tran, phut=a.phut, song_song=a.song_song, dd=a.dd,
                 hat=a.hat, so_toi_uu=a.so_toi_uu, ngan_sach_toi_uu=a.ngan_sach_toi_uu, cha_id=[x for x in a.cha_id.split(",") if x] or None,
                 gan_dat=a.gan_dat, ghi=not a.khong_ghi)
        print(json.dumps({x: k[x] for x in ("so_cha", "toan_tu", "giay", "so_phep_do") if x in k}, ensure_ascii=False, default=str))
        print("bao cao: %s" % (RA / "XUONG.md"))
        return 0
    if a.lenh == "cha":
        may = XM.May(cfg, dd_muc_tieu=a.dd, tep_luu=TEP_LUU, dd_khuyen_nghi=a.dd)
        may.mo_song_song(a.song_song)
        try:
            cha = nap_cha(cn, may, _tk(TEP_LUU), gan_dat=a.gan_dat)
        finally:
            may.dong()
        for c_ in cha:
            print("%-34s %-7s %-3s lai@DD %7s  %s" % (c_.id[:34], c_.ma, c_.khung, round(c_.diem, 1), c_.nhan))
        return 0
    if a.lenh == "toi-uu":
        rows = [x for x in OD.cac_the(cn) if x[0]["id"] == a.id]
        if not rows:
            print("khong co the %s" % a.id)
            return 1
        t, _, _, kq = rows[0]
        thu = ((kq or {}).get("tot_nhat") or {}).get("thu")
        if not thu:
            print("the chua co phep thu tot nhat")
            return 1
        may = XM.May(cfg, dd_muc_tieu=a.dd, tep_luu=TEP_LUU, dd_khuyen_nghi=a.dd)
        k = TU.toi_uu(may, t, thu, ngan_sach=a.ngan_sach, cho_ma=OD.ma_co_du_lieu(cfg), cho_khung=cfg.get("khung"))
        print(json.dumps({x: k.get(x) for x in ("goc", "tot_nhat", "so_phep_do", "giay")}, ensure_ascii=False, indent=1, default=str)[:4000])
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
