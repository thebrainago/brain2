# -*- coding: utf-8 -*-
"""ghep_cheo.py - GHEP CHEO co che giua cac he dat / gan dat (20/10/2026 toi, Grok Bot).

Chu du an: ghep cheo PHONG CACH la bat buoc. Ba kieu:
  1. vao_x_quan_li : lenh vao cua A + bo quan li (TP/DCA/hedge/go) TOT NHAT cua B; A va B PHAI khac phong cach
                     (phong cach vao cua A != cua B, hoac bo quan li cua B co ky thuat A khong dung).
  2. hai_nguon     : A + B cung ma, cung tai khoan, go cheo (to_hop.nguon_b, engine chay_tk san co); khac phong cach.
  3. danh_muc      : 2-3 he DAT MT5 khac ma/phong cach, tuong quan lai/lo NGAY (tu lenh MT5 that trong
                     reports/ong_dan/ket_qua_mt5/*_lenh_mt5.csv) <= nguong -> cong chuoi lai/lo, tinh %/nam + DD
                     tren von chung, phan xu loc 65/15 ngay (so MT5 that cong lai, nhan "GHÉP TỪ LỆNH MT5").
Kieu 1-2 sinh THE MOI vao data/ong_dan/trang_thai.sqlite o buoc quyet_dinh / duong_dich noi_bo -> buoc_toi_uu (loc
Python 65/15) tu nhat; qua loc thi sinh_mt5 dua vao hang MT5 hai tang nhu moi the khac. Ma nguon A/B KHONG bao gio ra
khoi data/ (the ghep chi tham chieu tin_hieu trong cache).
Chong trung: khoa = sha(kieu, A, B, ma, khung) + so voi the da co. Tran: `tran_moi_luot`, `tran_ton` (the ghep chua toi uu).
Cau hinh: config/dieu_phoi.json muc "ghep_cheo".

Chay: python -m nhan.ghep_cheo [--tran 20] [--kho]      (--kho: chi in, khong ghi)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import so_co_che as SO

GOC = Path(__file__).resolve().parent.parent
KQ_MT5 = GOC / "reports" / "ong_dan" / "ket_qua_mt5"
DANH_MUC = GOC / "reports" / "kho_co_che" / "danh_muc_ghep.jsonl"
TRANG_GHEP = "GHEP_CHEO"
MAC_DINH = {"bat": True, "tran_moi_luot": 20, "tran_ton": 60, "tuong_quan_toi_da": 0.3, "danh_muc_toi_da": 10,
            "von_moi_he": 1000.0, "ti_le_gan_dat": 0.6,
            "toi_da_moi_he": 3, "nam_toi_thieu": 1.5}


def cau_hinh() -> dict:
    try:
        c = json.loads((GOC / "config" / "dieu_phoi.json").read_text(encoding="utf-8")).get("ghep_cheo") or {}
    except (OSError, ValueError):
        c = {}
    return {**MAC_DINH, **c}


def khoa(kieu: str, a: str, b: str, ma: str, kh: str) -> str:
    return hashlib.sha1(json.dumps([kieu, a, b, ma, kh]).encode()).hexdigest()[:16]


def khac_phong_cach(a: dict, b: dict, kieu: str) -> bool:
    """Ghep cheo phong cach BAT BUOC. Thieu nhan ca hai ben -> khong biet -> khong ghep."""
    va, vb = set(a.get("phong_cach") or []), set(b.get("phong_cach") or [])
    if kieu == "vao_x_quan_li":
        qa, qb = set(a.get("phong_cach_quan_li") or []), set(b.get("phong_cach_quan_li") or [])
        return bool((va and vb and va != vb) or (qb - qa))
    return bool(va and vb and va != vb) or bool(set(a.get("tai_san") or []) ^ set(b.get("tai_san") or []))


def ung_vien(ds: list[dict]) -> list[dict]:
    return [r for r in ds if r.get("trang_thai") in ("DAT_MT5", "DAT_PY", "GAN_DAT")]


def _ql_tot(cn, the_id: str) -> tuple[dict | None, str | None, str | None]:
    r = cn.execute("SELECT kq FROM the WHERE id=?", (the_id,)).fetchone()
    tot = (json.loads(r[0] or "{}").get("tot_nhat") or {}) if r else {}
    thu = tot.get("thu") or {}
    return (thu.get("ql") or None), thu.get("ma"), thu.get("khung")


def _tin_hieu(cn, the_id: str) -> dict | None:
    r = cn.execute("SELECT json FROM the WHERE id=?", (the_id,)).fetchone()
    return (json.loads(r[0]).get("tin_hieu") or None) if r else None


def sinh(cn, ds: list[dict], cfg: dict | None = None, kho: bool = False, in_ra=print) -> dict:
    """Sinh the ghep (kieu 1, 2) vao cache ong dan. -> {"moi": n, "bo_trung": n, "ton": n, "ly_do": ...}."""
    cfg = {**MAC_DINH, **(cfg or {})}
    ton = cn.execute("SELECT COUNT(*) FROM the WHERE buoc='quyet_dinh' AND trang_thai=?", (TRANG_GHEP,)).fetchone()[0]
    kq = {"moi": 0, "bo_trung": 0, "ton": ton, "khac_phong_cach_bo": 0}
    if ton >= int(cfg["tran_ton"]):
        kq["ly_do"] = "đã có %d thẻ ghép chờ Python >= trần %s" % (ton, cfg["tran_ton"])
        return kq
    tran = min(int(cfg["tran_moi_luot"]), int(cfg["tran_ton"]) - ton)
    co = {r[0] for r in cn.execute("SELECT id FROM the")}
    uv = ung_vien(ds)
    nguon = [r for r in uv if r.get("chay_python") and _tin_hieu(cn, r["id"])]
    ql = []
    for r in uv:
        q, ma, kh = _ql_tot(cn, r["id"])
        if q:
            ql.append((r, q, ma, kh))
    # uu tien cap manh nhat: diem A + diem B
    cap = []
    for a in nguon:
        for b, q, ma_b, kh_b in ql:
            if a["id"] != b["id"]:
                cap.append(("vao_x_quan_li", a, b, q, ma_b, kh_b))
        for b in nguon:
            if a["id"] < b["id"]:
                cap.append(("hai_nguon", a, b, None, None, None))
    cap.sort(key=lambda x: -((SO.diem_lai(x[1]) or 0) + (SO.diem_lai(x[2]) or 0)))
    moi = []
    dung: dict[str, int] = {}
    for kieu, a, b, q, ma_b, kh_b in cap:
        if len(moi) >= tran:
            break
        if dung.get(a["id"], 0) >= int(cfg["toi_da_moi_he"]) or dung.get(b["id"], 0) >= int(cfg["toi_da_moi_he"]):
            continue                                     # da dang: mot he toi da N lan / luot
        if not khac_phong_cach(a, b, kieu):
            kq["khac_phong_cach_bo"] += 1
            continue
        qa, ma_a, kh_a = _ql_tot(cn, a["id"])
        ma = ma_a or (a.get("ma") or [None])[0]
        kh = kh_a or (a.get("khung") or ["H1"])[0]
        if not ma:
            continue
        k = khoa(kieu, a["id"], b["id"], ma, kh)
        tid = "ghep_" + k
        if tid in co:
            kq["bo_trung"] += 1
            continue
        co.add(tid)
        th_a = _tin_hieu(cn, a["id"])
        th = {"kieu": "to_hop", "nguon": th_a, "bo_loc": [],
              "nguon_b": _tin_hieu(cn, b["id"]) if kieu == "hai_nguon" else None}
        ql_dung = dict(q) if kieu == "vao_x_quan_li" else dict(qa or {"tp_pct": 0.002})
        if kieu == "hai_nguon":
            ql_dung["go_cheo"] = True
        the = {"id": tid, "ten": "Ghép %s: %s × %s" % (kieu, a.get("ten", a["id"])[:40], b.get("ten", b["id"])[:40]),
               "loai": "he_hoan_thien", "uu_tien": 2, "nen_tang": "GHEP_CHEO", "duong_dich": "noi_bo", "tin_hieu": th,
               "nguon": {"kho": "ghep_cheo", "tep": ""}, "thanh_phan": [a["id"], b["id"]], "ma_goi_y": [ma],
               "thu_goi_y": [{"ma": ma, "khung": kh, "tham": {}, "ql": ql_dung}],
               "ghep_cheo": {"kieu": kieu, "a": a["id"], "b": b["id"], "phong_cach_a": a.get("phong_cach"),
                             "phong_cach_b": b.get("phong_cach"), "quan_li_b": b.get("phong_cach_quan_li"),
                             "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}}
        moi.append(the)
        dung[a["id"]] = dung.get(a["id"], 0) + 1
        dung[b["id"]] = dung.get(b["id"], 0) + 1
    if not kho and moi:
        with cn:
            for t in moi:
                cn.execute("INSERT OR IGNORE INTO the (id, json, loai, uu_tien, duong, buoc, trang_thai, kq, cap_nhat) "
                           "VALUES (?,?,?,?,?,?,?,?,?)", (t["id"], json.dumps(t, ensure_ascii=False), t["loai"], t["uu_tien"],
                                                          t["duong_dich"], "quyet_dinh", TRANG_GHEP, "{}",
                                                          time.strftime("%Y-%m-%dT%H:%M:%S")))
                cn.execute("INSERT INTO nhat_ky VALUES (?,?,?,?)", (time.strftime("%Y-%m-%dT%H:%M:%S"), "ghep_cheo", t["id"],
                                                                     t["ghep_cheo"]["kieu"]))
    kq["moi"] = len(moi)
    kq["vi_du"] = [t["ten"][:120] for t in moi[:5]]
    in_ra("ghep_cheo: %s" % json.dumps({k: v for k, v in kq.items() if k != "vi_du"}, ensure_ascii=False))
    return kq


# ------------------------------------------------------------------ kieu 3: danh muc tu lenh MT5 that
def lai_ngay_mt5(tep: Path) -> pd.Series:
    """CSV lenh MT5 (thoi_gian;...;loi;swap;hoa_hong) -> lai/lo theo NGAY (USD)."""
    b = pd.read_csv(tep, sep=";")
    b = b[b["vao_ra"].astype(str).str.lower().isin(["out", "inout", "out_by"])]
    if b.empty:
        return pd.Series(dtype=float)
    t = pd.to_datetime(b["thoi_gian"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    v = b["loi"].astype(float) + b["swap"].astype(float) + b["hoa_hong"].astype(float)
    return v.groupby(t.dt.normalize()).sum().sort_index()


def do_danh_muc(chuoi: dict[str, pd.Series], von_moi_he: float = 1000.0) -> dict:
    """Cong lai/lo ngay cua cac he (von moi he `von_moi_he`) -> %/nam kep, DD dong (tren duong von dong lenh)."""
    bang = pd.DataFrame(chuoi).fillna(0.0)
    if bang.empty:
        return {"loi": "CHƯA ĐO ĐƯỢC: không có lệnh"}
    tu = max(s.index.min() for s in chuoi.values())
    den = min(s.index.max() for s in chuoi.values())
    bang = bang.loc[tu:den]
    if len(bang) < 30:
        return {"loi": "CHƯA ĐO ĐƯỢC: khoảng chung < 30 ngày"}
    von0 = von_moi_he * len(chuoi)
    eq = von0 + bang.sum(axis=1).cumsum()
    nam = max((bang.index[-1] - bang.index[0]).days / 365.25, 1e-6)
    dinh = np.maximum.accumulate(np.maximum(eq.values, 1e-9))
    dd = float(np.max((dinh - eq.values) / dinh)) * 100
    lai = ((max(eq.iloc[-1], 1e-9) / von0) ** (1 / nam) - 1) * 100
    tq = bang.corr().values
    tq_max = float(np.nanmax(tq[np.triu_indices_from(tq, 1)])) if len(chuoi) > 1 else 0.0
    return {"lai_pct_nam": round(float(lai), 2), "sut_giam_pct": round(dd, 2), "so_nam": round(nam, 2), "von": von0,
            "tuong_quan_max": round(tq_max, 3), "tu": str(bang.index[0].date()), "den": str(bang.index[-1].date()),
            "nhan": "GHÉP TỪ LỆNH MT5 (DD trên vốn đóng lệnh, chưa tính equity nổi)"}


def tep_lenh(r: dict, thu_muc: Path = KQ_MT5) -> Path | None:
    for x in r.get("mt5") or []:
        if x.get("ket_luan") == "ĐẠT":
            p = thu_muc / ("%s_vao.csv_lenh_mt5.csv" % x["ten"])
            if p.exists():
                return p
    return None


def danh_muc(ds: list[dict], cfg: dict | None = None, thu_muc: Path = KQ_MT5, in_ra=print) -> list[dict]:
    from nhan import nguong as NG
    cfg = {**MAC_DINH, **(cfg or {})}
    he = [(r, tep_lenh(r, thu_muc)) for r in ds if r.get("trang_thai") == "DAT_MT5"]
    he = [(r, lai_ngay_mt5(p)) for r, p in he if p is not None]
    he = [(r, s) for r, s in he if len(s) >= 10]
    he.sort(key=lambda x: -(SO.diem_lai(x[0]) or 0))
    he = he[:16]                                         # tran to hop: C(16,3) = 560
    ra = []
    for n in (2, 3):
        for nhom in itertools.combinations(he, n):
            if len({tuple(r.get("ma") or []) for r, _ in nhom}) < n:
                continue                                 # khac ma bat buoc
            if all(set(nhom[0][0].get("phong_cach") or []) == set(r.get("phong_cach") or []) for r, _ in nhom):
                continue                                 # ghep cheo phong cach
            m = do_danh_muc({r["id"]: s for r, s in nhom}, float(cfg["von_moi_he"]))
            if m.get("loi") or m["tuong_quan_max"] > float(cfg["tuong_quan_toi_da"]) or m["so_nam"] < float(cfg["nam_toi_thieu"]):
                continue
            m["nhan_dat_loc_python_dd_dong_lenh"] = NG.dat(m["lai_pct_nam"], m["sut_giam_pct"], "loc_python")["dat"]
            m["nhan_dat_cuoi_dd_dong_lenh"] = NG.dat(m["lai_pct_nam"], m["sut_giam_pct"], "cuoi")["dat"]
            m["he"] = [r["id"] for r, _ in nhom]
            m["id"] = "dm_" + hashlib.sha1(json.dumps(sorted(m["he"])).encode()).hexdigest()[:12]
            ra.append(m)
    # uu tien DD thap tren cung muc lai: diem = lai / max(dd, 5)
    ra.sort(key=lambda m: -(m["lai_pct_nam"] / max(m["sut_giam_pct"], 5.0)))
    ra = ra[:int(cfg["danh_muc_toi_da"])]
    in_ra("danh_muc: %d hệ ĐẠT MT5 có lệnh, giữ %d danh mục (tương quan ngày <= %s)" % (len(he), len(ra), cfg["tuong_quan_toi_da"]))
    return ra


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tran", type=int)
    ap.add_argument("--kho", action="store_true")
    ap.add_argument("--db")
    a = ap.parse_args(argv)
    cfg = cau_hinh()
    if not cfg.get("bat"):
        print("ghep_cheo: tat trong config/dieu_phoi.json")
        return 0
    if a.tran:
        cfg["tran_moi_luot"] = a.tran
    db = Path(a.db) if a.db else SO.DB
    ds = SO.xay(db)
    SO.luu(ds)
    SO.ghi_md(ds)
    cn = sqlite3.connect(str(db), timeout=60)
    try:
        sinh(cn, ds, cfg, kho=a.kho)
    finally:
        cn.close()
    dm = danh_muc(ds, cfg)
    if not a.kho:
        DANH_MUC.parent.mkdir(parents=True, exist_ok=True)
        DANH_MUC.write_text("".join(json.dumps(m, ensure_ascii=False, sort_keys=True) + "\n" for m in dm), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
