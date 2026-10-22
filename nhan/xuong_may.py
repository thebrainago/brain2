# -*- coding: utf-8 -*-
"""xuong_may.py - MAY DO cua XUONG (22/10/2026, Claude): do mot cau hinh (the + thu) o LOT THAT, THEO RUI RO NGANG NHAU.

Vi sao khong chi goi `ong_dan.danh_gia`: no do o MOT lot co dinh (lot_tren_1000 la mot chieu cua luoi tim kiem), nen hai cau hinh
khong so sanh duoc cong bang - cau hinh nao chon lot cao thi "lai" cao va sut giam cao. Chu du an chi hoi ba thu: lai sau phi,
sut giam <= 80 %, lai >= 10 %/nam, va LOT CO GIAN. Nen o day moi cau hinh duoc KEO LOT toi cung mot muc sut giam muc tieu
(`dd_muc_tieu`, mac dinh 60 % - chua 20 diem de dong OOS / MT5 co the xau hon) bang chia doi tren engine THAT (ky quy,
stop-out, phi san), roi so `lai %/nam o do`. Voi DCA / khong SL, sut giam khong tuyen tinh theo lot nen khong the quy theo cong thuc.
`ong_dan` ghi ro: "lai o DD 80 tuyen tinh - THAM KHAO, sai voi DCA".

Ba thu quan trong:
  * Chon tren IS (mac dinh 70 % dau), OOS (30 % cuoi) CHI de ghi nhan - khong bao gio de chon. Tin hieu tinh tren ca chuoi roi cat
    (chi bao nhan qua nen khong nhin truoc), engine chay tren lat cat.
  * Moi phep do luu trong bo nho (va tuy chon SQLite) theo khoa; chay lai la tiep, khong do lai.
  * Moi so la MÔ PHỎNG (`tai_khoan.chay_tk`); phi la phi san da do neu co `reports/phi_san/`, khong thi PHÍ TẠM (nhan trong ket qua).
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import nguon_lenh as NL
from nhan import ong_dan as OD
from nhan import tai_khoan as TK

GOC = Path(__file__).resolve().parent.parent
TEP_LUU = GOC / "data" / "xuong" / "xuong.sqlite"
KIEU_KHONG_HO_TRO = ("lenh_ngoai",)          # statement: gia bi cat theo khoang lenh, khong hop voi lat cat IS/OOS
KIEU_TU_TINH = ("luoi",)                      # luoi: lenh vao sinh tu bo cho_phep trong chuan_bi, khong tu chuoi tin hieu


def _kh(*phan) -> str:
    return hashlib.sha1(json.dumps(phan, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:20]


class Luu:
    """Bo nho SQLite mot bang (khoa -> json) cho phep do. Chi tien trinh CHA ghi (cong nhan tra ket qua ve)."""

    def __init__(self, tep: Path | None):
        self.tep = Path(tep) if tep else None
        self.cn = None
        if self.tep:
            self.tep.parent.mkdir(parents=True, exist_ok=True)
            self.cn = sqlite3.connect(str(self.tep), timeout=60)
            self.cn.execute("CREATE TABLE IF NOT EXISTS phep (khoa TEXT PRIMARY KEY, json TEXT)")
            self.cn.commit()

    def lay(self, khoa: str):
        if not self.cn:
            return None
        r = self.cn.execute("SELECT json FROM phep WHERE khoa=?", (khoa,)).fetchone()
        return json.loads(r[0]) if r else None

    def ghi(self, khoa: str, v: dict) -> None:
        if self.cn:
            with self.cn:
                self.cn.execute("INSERT OR REPLACE INTO phep VALUES (?,?)", (khoa, json.dumps(v, default=str)))


#: Tham so quan li ma EA MT5 (BRAIN_XuLiLenh, che do VAO_CSV) THUC SU chay duoc - xuong chi tim trong vung nay de moi ket qua
#: Python deu xac nhan duoc bang MT5. (go_cheo = go cheo giua hai NGUON khong co trong EA -> xuong khong dung.)
TRUONG_QL_MT5 = ("tp_pct", "dca_buoc_pct", "dca_toi_da", "dca_he_so_lot", "dca_lot_tuyen_tinh", "hedge_khi_lo_pct", "hedge_ti_le",
                 "mo_khoa_pct", "hedge_max_lan", "go_tien", "trail_kich_pct", "trail_khoang_pct", "lot_tren_1000")


def chuan_hoa_ql(ql: dict) -> dict:
    """Bo tham so KHONG co tac dung (buoc DCA khi khong DCA, chi tiet hedge khi khong hedge, khoang trailing khi khong trailing)
    de hai cau hinh tuong duong khong bi do hai lan; bo go_cheo (EA khong co). Khong sua dau vao."""
    q = {k: v for k, v in (ql or {}).items() if k != "go_cheo"}
    for k in ("dca_toi_da", "hedge_max_lan"):                    # so nguyen / so thuc nhat quan -> cung khoa bo nho
        if q.get(k) is not None:
            q[k] = int(q[k])
    for k in ("tp_pct", "dca_buoc_pct", "dca_he_so_lot", "hedge_khi_lo_pct", "hedge_ti_le", "mo_khoa_pct", "trail_kich_pct",
              "trail_khoang_pct", "go_tien", "lot_tren_1000"):
        if isinstance(q.get(k), (int, float)) and not isinstance(q.get(k), bool):
            q[k] = float(q[k])
    if not q.get("dca_toi_da"):
        for k in ("dca_buoc_pct", "dca_he_so_lot", "dca_lot_tuyen_tinh"):
            q.pop(k, None)
        q["dca_toi_da"] = 0
    if not q.get("hedge_khi_lo_pct"):
        for k in ("hedge_ti_le", "mo_khoa_pct", "hedge_max_lan", "go_tien"):
            q.pop(k, None)
        q["hedge_khi_lo_pct"] = 0.0
    if not q.get("trail_kich_pct"):
        q.pop("trail_khoang_pct", None)
        q["trail_kich_pct"] = 0.0
    return q


def diem_tho(r: dict | None) -> float:
    """Diem SANG LOC o lot tham chieu: lai/sut giam (tuong ung tieu chi chu du an 10/80 = 0,125). Chay / stop-out / loi -> rat thap.
    Khong du lenh KHONG phai ly do loai (chi la it bang chung): 0 diem."""
    if not r or r.get("loi"):
        return -1e9
    if r.get("chay") or r.get("so_stop_out"):
        return -100.0
    if (r.get("so_ro") or 0) < 1:
        return 0.0
    return float(r["lai_pct_nam"]) / max(float(r["sut_giam_pct"]), 3.0)


class May:
    def __init__(self, cfg: dict | None = None, dd_muc_tieu: float = 60.0, ty_le_oos: float | None = None,
                 lot_tham_chieu: float = 1.0, lot_min: float = 0.1, lot_max: float = 100.0, tep_luu: Path | None = None,
                 giu_duong_von: bool = False, dd_khuyen_nghi: float = 65.0):
        self.cfg = cfg or OD.cau_hinh()
        self.dd = float(dd_muc_tieu)
        self.dd_khuyen_nghi = float(dd_khuyen_nghi)
        self.oos = float(self.cfg.get("ty_le_oos", 0.3) if ty_le_oos is None else ty_le_oos)
        self.lot_ref, self.lot_min, self.lot_max = float(lot_tham_chieu), float(lot_min), float(lot_max)
        self.giu_duong_von = giu_duong_von
        self.luu = Luu(tep_luu)
        self._bo_nho: dict = {}
        self._tin_hieu: dict = {}
        self.so_chay = 0              # so lan goi engine THAT (khong tinh trung bo nho)
        self.giay = 0.0

    # ------------------------------------------------------------------ du lieu
    @property
    def cuoi_is(self) -> float:
        return 1.0 - self.oos

    def gia(self, ma: str, khung: str) -> pd.DataFrame | None:
        return OD.gia(ma, khung, self.cfg)

    def tin_hieu(self, t: dict, thu: dict, df: pd.DataFrame) -> np.ndarray | None:
        kieu = (t.get("tin_hieu") or {}).get("kieu")
        if kieu in KIEU_TU_TINH:
            return None
        k = (_kh(t["id"], t.get("tin_hieu")), thu["ma"], thu["khung"], _kh(thu.get("tham") or {}), len(df))
        if k not in self._tin_hieu:
            if len(self._tin_hieu) > 400:
                self._tin_hieu.clear()
            self._tin_hieu[k] = np.asarray(OD.tin_hieu(t, df, thu.get("tham") or {}, thu["ma"]), int)
        return self._tin_hieu[k]

    # ------------------------------------------------------------------ mot phep do
    def khoa(self, t: dict, thu: dict, doan: tuple, lot: float | None) -> str:
        ql = chuan_hoa_ql(thu.get("ql"))
        ql["lot_tren_1000"] = lot if lot is not None else ql.get("lot_tren_1000")
        return _kh("v2", t["id"], t.get("tin_hieu"), thu["ma"], thu["khung"], thu.get("tham") or {}, thu.get("he_so_n", 1.0), ql,
                   [round(x, 4) for x in doan], self.cfg.get("von"), self.cfg.get("san_phi"), self.cfg.get("tai_khoan"))

    @staticmethod
    def the_cua(t: dict, thu: dict) -> dict:
        """The sau khi ap he so chu ky (`he_so_n`, chi voi spec DSL): nhan moi chu ky chi bao `n` voi he so do."""
        he = float(thu.get("he_so_n", 1.0) or 1.0)
        if he == 1.0 or (t.get("tin_hieu") or {}).get("kieu") != "spec":
            return t
        from nhan import vong2 as V
        return V.nhan_chu_ky(t, he)

    def chay(self, t: dict, thu: dict, doan: tuple = (0.0, 1.0), lot: float | None = None) -> dict:
        """Do tren lat cat [doan[0], doan[1]) cua chuoi gia. `lot` (lot_tren_1000) ghi de ql; None -> theo thu["ql"]."""
        kh = self.khoa(t, thu, doan, lot)
        if kh in self._bo_nho:
            return self._bo_nho[kh]
        r = self.luu.lay(kh)
        if r is None:
            r = self._chay_that(t, thu, doan, lot)
            self.luu.ghi(kh, {k: v for k, v in r.items() if k not in ("duong_von", "von_xau", "chi_muc")})
        self._bo_nho[kh] = r
        return r

    def _chay_that(self, t: dict, thu: dict, doan: tuple, lot: float | None) -> dict:
        t0 = time.time()
        kieu = (t.get("tin_hieu") or {}).get("kieu")
        if kieu in KIEU_KHONG_HO_TRO:
            return {"loi": "CHUA_DO_DUOC: kieu %s chua ho tro trong xuong" % kieu}
        try:
            df = self.gia(thu["ma"], thu["khung"])
            if df is None or len(df) < 300:
                return {"loi": "CHUA_DO_DUOC: thieu du lieu %s %s" % (thu["ma"], thu["khung"])}
            t = self.the_cua(t, thu)
            s = self.tin_hieu(t, thu, df)
            a, b = int(len(df) * doan[0]), int(len(df) * doan[1])
            if b - a < 200:
                return {"loi": "CHUA_DO_DUOC: lat cat qua ngan (%d nen)" % (b - a)}
            thu2 = dict(thu, ql=chuan_hoa_ql(thu.get("ql")))
            if lot is not None:
                thu2["ql"]["lot_tren_1000"] = float(lot)
            cb = OD.chuan_bi(t, thu2, self.cfg, df=df.iloc[a:b], s=None if s is None else s[a:b])
            if "loi" in cb:
                return {"loi": cb["loi"]}
            kq = TK.chay_tk({thu["ma"]: cb["df"]}, cb["ev"], cb["ql"], cb["tk"], {thu["ma"]: cb["hs"]})
        except Exception as e:  # noqa: BLE001
            return {"loi": "CHUA_DO_DUOC: %s: %s" % (type(e).__name__, str(e)[:160])}
        r = {k: (float(kq[k]) if isinstance(kq.get(k), (np.floating, np.integer)) else kq.get(k))
             for k in ("lai_pct_nam", "sut_giam_pct", "von_cuoi", "lai_tien", "chay", "so_stop_out", "so_lenh_stop_out", "so_ro",
                       "so_lenh", "so_tp", "so_khoa", "so_go", "tu_choi_ky_quy", "ket_nen_max", "so_nam", "lot_mo_max")
             if k in kq}
        r["chay"] = bool(r.get("chay"))
        r["lot0"] = float(cb["ql"].lot0)
        r["nhan_phi"] = cb["hs"].nhan
        r["giay"] = round(time.time() - t0, 2)
        self.so_chay += 1
        self.giay += r["giay"]
        if self.giu_duong_von:
            r["duong_von"] = np.asarray(kq["duong_von"], float)
            r["von_xau"] = np.asarray(kq["von_xau"], float)
            r["chi_muc"] = cb["df"].index
        return r

    # ------------------------------------------------------------------ chay nhieu phep do song song
    def mo_song_song(self, so_nhan: int) -> None:
        """Mo bo cong nhan (tien trinh). Moi cong nhan giu bo nho gia / tin hieu rieng; chi tien trinh cha ghi SQLite."""
        if so_nhan and so_nhan > 1 and getattr(self, "_pool", None) is None:
            from concurrent.futures import ProcessPoolExecutor
            self._pool = ProcessPoolExecutor(max_workers=int(so_nhan), initializer=_khoi_tao_cn,
                                             initargs=(self.cfg, self.dd, self.oos, self.lot_ref, self.lot_min, self.lot_max))

    def dong(self) -> None:
        p = getattr(self, "_pool", None)
        if p is not None:
            p.shutdown(wait=True)
            self._pool = None

    def chay_lo(self, viec: list[tuple]) -> list[dict]:
        """viec = [(t, thu, doan, lot)] -> ket qua cung thu tu. Phep da co trong bo nho / SQLite khong do lai."""
        kq: list = [None] * len(viec)
        cho: dict[str, tuple] = {}
        vt: dict[str, list[int]] = {}
        for i, (t, thu, doan, lot) in enumerate(viec):
            kh = self.khoa(t, thu, doan, lot)
            r = self._bo_nho.get(kh) or self.luu.lay(kh)
            if r is not None:
                self._bo_nho[kh] = r
                kq[i] = r
            else:
                cho[kh] = (t, thu, doan, lot)
                vt.setdefault(kh, []).append(i)
        if cho:
            pool = getattr(self, "_pool", None)
            ks = list(cho)
            if pool is not None and len(ks) > 1:
                res = list(pool.map(_lam_viec, [cho[k] for k in ks], chunksize=max(1, len(ks) // (4 * pool._max_workers))))
            else:
                res = [self._chay_that(*cho[k]) for k in ks]
            for k, r in zip(ks, res):
                self.luu.ghi(k, {a: b for a, b in r.items() if a not in ("duong_von", "von_xau", "chi_muc")})
                self._bo_nho[k] = r
                for i in vt[k]:
                    kq[i] = r
        return kq

    # ------------------------------------------------------------------ cac lat cat tien loi
    def is_(self, t, thu, lot=None):
        return self.chay(t, thu, (0.0, self.cuoi_is), lot)

    def oos_(self, t, thu, lot=None):
        return self.chay(t, thu, (self.cuoi_is, 1.0), lot)

    def toan(self, t, thu, lot=None):
        return self.chay(t, thu, (0.0, 1.0), lot)

    # ------------------------------------------------------------------ keo lot toi sut giam muc tieu
    def dat(self, r: dict, dd: float | None = None) -> bool:
        return (not r.get("loi")) and not r.get("chay") and not r.get("so_stop_out") and \
            float(r["sut_giam_pct"]) <= (self.dd if dd is None else dd)

    def chuan_lot(self, t: dict, thu: dict, doan: tuple | None = None, toi_da_buoc: int = 7, dd: float | None = None) -> dict:
        """Lot_tren_1000 LON NHAT con giu sut giam <= dd_muc_tieu va khong stop-out tren lat cat `doan` (mac dinh IS).
        -> {"lot", "r" (do o lot do), "lai_o_dd", "tinh_trang": vua | qua_rui_ro | tran_lot | khong_lenh | loi, "so_buoc"}.
        Chia doi co khoi tao bang noi suy tuyen tinh (sut giam xap xi ti le voi lot) - thuong 3-5 phep do."""
        doan = doan or (0.0, self.cuoi_is)
        dd = self.dd if dd is None else float(dd)
        r0 = self.chay(t, thu, doan, self.lot_ref)
        if r0.get("loi"):
            return {"lot": None, "r": r0, "lai_o_dd": None, "tinh_trang": "loi", "so_buoc": 1}
        if (r0.get("so_ro") or 0) < 1:
            return {"lot": self.lot_ref, "r": r0, "lai_o_dd": 0.0, "tinh_trang": "khong_lenh", "so_buoc": 1}
        ok = {self.lot_ref: r0} if self.dat(r0, dd) else {}
        xau = {} if self.dat(r0, dd) else {self.lot_ref: r0}
        so = 1
        lam = lambda x: round(min(max(float(x), self.lot_min), self.lot_max), 2)           # noqa: E731
        probe = lam(self.lot_ref * dd / max(float(r0["sut_giam_pct"]), 0.5) * 0.9) if not r0.get("chay") else lam(self.lot_ref / 2)
        for _ in range(toi_da_buoc):
            if probe in ok or probe in xau:
                break
            r = self.chay(t, thu, doan, probe)
            so += 1
            (ok if self.dat(r, dd) else xau)[probe] = r
            hi_xau = min([x for x in xau if not ok or x > max(ok)], default=None)
            lo_ok = max(ok, default=None)
            if lo_ok is None:                                         # chua co lot nao dat: ha manh
                nxt = lam(min(xau) / 3)
                if nxt >= min(xau):
                    break
            elif hi_xau is None:                                      # chua co lot nao xau: tang manh
                nxt = lam(lo_ok * 2)
                if nxt <= lo_ok:
                    break
            else:
                if hi_xau / lo_ok < 1.08:
                    break
                d1, d2 = float(ok[lo_ok]["sut_giam_pct"]), float(xau[hi_xau]["sut_giam_pct"]) if not xau[hi_xau].get("chay") else 200.0
                f = (dd - d1) / (d2 - d1) if d2 > d1 else 0.5
                nxt = lam(lo_ok + min(max(f, 0.15), 0.85) * (hi_xau - lo_ok))
            probe = nxt
        if not ok:
            lo = self.chay(t, thu, doan, self.lot_min) if self.lot_min not in xau else xau[self.lot_min]
            return {"lot": self.lot_min, "r": lo, "lai_o_dd": float(lo.get("lai_pct_nam") or 0.0), "tinh_trang": "qua_rui_ro", "so_buoc": so}
        lot = max(ok)
        tt = "tran_lot" if lot >= self.lot_max - 1e-9 else "vua"
        return {"lot": lot, "r": ok[lot], "lai_o_dd": float(ok[lot]["lai_pct_nam"]), "tinh_trang": tt, "so_buoc": so}

    def diem(self, cl: dict) -> float:
        """Diem cuoi (so sanh cong bang): lai %/nam o sut giam muc tieu. qua_rui_ro / loi -> am; khong lenh -> 0."""
        if cl["tinh_trang"] == "loi":
            return -1e9
        if cl["tinh_trang"] == "qua_rui_ro":
            return -100.0 - float(cl["r"].get("sut_giam_pct") or 0.0)
        return float(cl["lai_o_dd"] or 0.0)

    # ------------------------------------------------------------------ do ben
    def ben_theo_doan(self, t: dict, thu: dict, lot: float, so_doan: int = 4) -> dict:
        """Chay o lot da keo tren `so_doan` doan lien tiep cua IS: ti le doan co lai > 0 va khong stop-out, lai tung doan."""
        c = self.cuoi_is
        rs = [self.chay(t, thu, (c * i / so_doan, c * (i + 1) / so_doan), lot) for i in range(so_doan)]
        tot = [r for r in rs if not r.get("loi")]
        lai = [round(float(r["lai_pct_nam"]), 1) for r in tot]
        duong = sum(1 for r in tot if r["lai_pct_nam"] > 0 and not r.get("so_stop_out") and not r.get("chay"))
        return {"ti_le_doan_duong": round(duong / len(rs), 2), "lai_doan": lai, "so_doan_do_duoc": len(tot),
                "doan_te_nhat": min(lai) if lai else None}

    def khoang_lot(self) -> tuple[float, float]:
        return self.lot_min, self.lot_max


# ---------------------------------------------------------------------------------------------- cong nhan (tien trinh con)
_MAY_CN: "May | None" = None


def _khoi_tao_cn(cfg, dd, oos, lot_ref, lot_min, lot_max):
    global _MAY_CN
    _MAY_CN = May(cfg, dd_muc_tieu=dd, ty_le_oos=oos, lot_tham_chieu=lot_ref, lot_min=lot_min, lot_max=lot_max)


def _lam_viec(args):
    return _MAY_CN._chay_that(*args)
