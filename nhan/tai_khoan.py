# -*- coding: utf-8 -*-
"""tai_khoan.py - ENGINE CAP TAI KHOAN: nhieu NGUON LENH + quan li (TP, DCA, GO CHEO) chung MOT tai khoan.

Chu du an 17/10/2026: The Brain la de tim cac he thong / tin hieu vao lenh roi KET HOP chung voi nhau cung quan tri von;
danh gia tung manh dung mot minh qua cong hoc thuat la sai (xem CHI_THI_CHU_DU_AN.md, DE_XUAT_THAY_DOI_THE_BRAIN.md).

GIAO DIEN CHUNG: moi nguon lenh (EA, chi bao mui ten, luat DSL, lich su giao dich, su kien o moc ONH...) deu quy ve
mot DONG LENH VAO = danh sach `LenhVao(nguon, chi_so, gia, chieu)`. Khong can dich logic cua nguon: chi can biet no mo lenh
luc nao, chieu nao, gia nao. Ghep = chay nhieu dong cung luc tren mot tai khoan.

MO HINH (nen H1 tro len; thu tu trong nen la GIA DINH BAO THU, xem ghi chu):
  - moi lenh vao mo mot RO rieng, TP tinh tu gia trung binh cua ro (diem gia). KHONG co SL cung.
  - DCA: them tang khi gia di nguoc dca_buoc_pct so voi gia vao ban dau, toi da dca_toi_da tang, lot nhan he so moi tang.
  - GO CHEO: cuoi moi nen, ro dang LO lau nhat duoc dong cung (cac) ro dang LAI noi neu tong lai noi >= lo + nguong.
    Day la tong quat hoa `cat_hoa` cua mo_phong_v2 (ghep trong mot ro) len nhieu ro / nhieu nguon.
  - chi phi: spread tra mot lan luc mo moi tang; swap moi moc `rollover` theo gia hien tai (so mu nam), thu Sau x3 do ben goi dua vao.
  - don vi: lot = 1.0 nghia la 1 DIEM GIA = 1 don vi tien. Ket qua tinh bang DIEM GIA; quy ra tien theo lot cua chu du an.

GHI CHU THU TU TRONG NEN (khong biet duoc tu H1): trong mot nen, kiem TP truoc roi moi khop DCA va gỡ chéo (lay gia dong cua).
Lenh vua mo o nen t chi bat dau xet TP tu nen t+1. Mo phong -> co the lac quan/bi quan; hieu chuan voi MT5 la viec con lai.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class LenhVao:
    nguon: str
    chi_so: int          # vi tri nen khop lenh
    gia: float           # gia khop
    chieu: int = 1       # +1 mua, -1 ban


@dataclass
class QuanLi:
    tp_diem: float = 5.5
    dca_buoc_pct: float | None = None
    dca_toi_da: int = 0
    dca_he_so_lot: float = 1.0
    go_cheo: bool = False
    go_nguong_diem: float = 0.0
    spread_diem: float = 1.5
    swap_nam: float = 0.0577


@dataclass
class _Ro:
    nguon: str
    s: int
    sinh: int
    tang: list = field(default_factory=list)    # (gia, lot)
    muc: list = field(default_factory=list)     # cac muc DCA con lai (gia)
    lot_ke: float = 1.0
    dong: bool = False
    dong_boi: str = ""
    dong_luc: int = -1
    chi: float = 0.0                            # chi phi da tra (spread + swap), diem*lot
    lo_nhat: float = 0.0                        # lo treo lon nhat cua ro (diem*lot, duong)

    def lot(self): return sum(l for _, l in self.tang)
    def gia_tb(self): return sum(p * l for p, l in self.tang) / self.lot()
    def noi(self, gia): return sum(self.s * (gia - p) * l for p, l in self.tang)


def chay(bars: pd.DataFrame, luong: list[LenhVao], ql: QuanLi, rollover: np.ndarray | None = None) -> dict:
    """bars: cot open/high/low/close (index theo thu tu thoi gian). rollover[t] = he so swap phai tra cho lenh dang giu qua dau nen t
    (0 = khong co moc; 1 = mot dem; 3 = thu Sau). Tra dict: tong, duong von, nhat ky ro, chi so."""
    hi, lo, cl = bars["high"].to_numpy(float), bars["low"].to_numpy(float), bars["close"].to_numpy(float)
    n = len(bars)
    roll = np.zeros(n) if rollover is None else np.asarray(rollover, float)
    su_kien: dict[int, list[LenhVao]] = {}
    for e in luong:
        su_kien.setdefault(int(e.chi_so), []).append(e)

    ro_mo: list[_Ro] = []
    nhat_ky: list[dict] = []
    so_du = 0.0
    duong_von = np.zeros(n)
    so_du_t = np.zeros(n)
    treo_xau = np.zeros(n)
    so_ro_mo = np.zeros(n, int)
    lot_mo = np.zeros(n)

    def dong_ro(r: _Ro, gia: float, t: int, boi: str):
        nonlocal so_du
        kq = r.noi(gia) - r.chi
        so_du += r.noi(gia)
        r.dong, r.dong_boi, r.dong_luc = True, boi, t
        nhat_ky.append(dict(nguon=r.nguon, sinh=r.sinh, dong=t, boi=boi, lai_diem=kq / max(r.tang[0][1], 1e-12),
                            lo_treo=r.lo_nhat / max(r.tang[0][1], 1e-12), so_tang=len(r.tang)))

    for t in range(n):
        # swap cho ro dang giu qua dau nen t
        if roll[t] > 0 and t > 0:
            for r in ro_mo:
                if r.sinh < t:
                    c = r.lot() * cl[t - 1] * ql.swap_nam / 365 * roll[t]
                    r.chi += c
                    so_du -= c
        # TP (ro sinh truoc t)
        for r in list(ro_mo):
            if r.sinh >= t:
                continue
            tp_gia = r.gia_tb() + r.s * ql.tp_diem
            cham = hi[t] >= tp_gia if r.s > 0 else lo[t] <= tp_gia
            if cham:
                dong_ro(r, tp_gia, t, "tp")
                ro_mo.remove(r)
        # khop DCA (sau TP, bao thu)
        for r in ro_mo:
            if r.sinh >= t:
                continue
            while r.muc and ((lo[t] <= r.muc[0]) if r.s > 0 else (hi[t] >= r.muc[0])):
                gia = r.muc.pop(0)
                lot = r.lot_ke
                r.tang.append((gia, lot))
                r.lot_ke *= ql.dca_he_so_lot
                c = ql.spread_diem * lot
                r.chi += c
                so_du -= c
        # ro moi mo o nen t
        for e in su_kien.get(t, []):
            r = _Ro(nguon=e.nguon, s=int(e.chieu), sinh=t)
            r.tang.append((float(e.gia), 1.0))
            r.lot_ke = ql.dca_he_so_lot
            if ql.dca_buoc_pct and ql.dca_toi_da > 0:
                r.muc = [e.gia * (1 - r.s * ql.dca_buoc_pct * k) for k in range(1, ql.dca_toi_da + 1)]
            c = ql.spread_diem
            r.chi += c
            so_du -= c
            ro_mo.append(r)
        # lo treo xau nhat trong nen (gia bat loi nhat cho tung ro)
        if ro_mo:
            xau = 0.0
            for r in ro_mo:
                gx = lo[t] if r.s > 0 else hi[t]
                f = r.noi(gx)
                r.lo_nhat = max(r.lo_nhat, -f)
                xau += f
            treo_xau[t] = xau
        # GO CHEO cuoi nen
        if ql.go_cheo and len(ro_mo) >= 2:
            for b in sorted([r for r in ro_mo if r.noi(cl[t]) < 0], key=lambda r: r.sinh):
                if b.dong:
                    continue
                can = -b.noi(cl[t]) + ql.go_nguong_diem
                thang = sorted([w for w in ro_mo if w is not b and not w.dong and w.noi(cl[t]) > 0],
                               key=lambda w: -w.noi(cl[t]))
                tich, chon = 0.0, []
                for w in thang:
                    chon.append(w); tich += w.noi(cl[t])
                    if tich >= can:
                        break
                if tich >= can and chon:
                    for r in [b] + chon:
                        dong_ro(r, cl[t], t, "go_cheo")
                        ro_mo.remove(r)
        so_ro_mo[t] = len(ro_mo)
        lot_mo[t] = sum(r.lot() for r in ro_mo)
        duong_von[t] = so_du + sum(r.noi(cl[t]) for r in ro_mo)
        so_du_t[t] = so_du
    # ro con mo cuoi du lieu
    for r in list(ro_mo):
        nhat_ky.append(dict(nguon=r.nguon, sinh=r.sinh, dong=n - 1, boi="mo", lai_diem=(r.noi(cl[-1]) - r.chi) / max(r.tang[0][1], 1e-12),
                            lo_treo=r.lo_nhat / max(r.tang[0][1], 1e-12), so_tang=len(r.tang)))
    return dict(tong_diem=float(duong_von[-1]) if n else 0.0, duong_von=duong_von, von_xau=so_du_t + treo_xau, treo_xau=treo_xau, so_ro_mo=so_ro_mo,
                lot_mo=lot_mo, nhat_ky=pd.DataFrame(nhat_ky), so_du=so_du)


def rollover_tu_ny(t_ny: pd.DatetimeIndex) -> np.ndarray:
    """He so swap cho tung nen tu moc 17:00 gio New York (XM/Exness tinh swap luc doi ngay). Thu Sau x3; nen nam sau khoang trong
    cuoi tuan nhan dung moc thu Sau. t_ny: chi muc thoi gian da o mui gio America/New_York, moi phan tu la gio BAT DAU nen H1."""
    t_ny = pd.DatetimeIndex(t_ny)
    n = len(t_ny)
    ra = np.zeros(n)
    for i in range(1, n):
        prev_end = t_ny[i - 1] + pd.Timedelta(hours=1)
        cur = t_ny[i]
        d = prev_end.normalize()
        while d <= cur.normalize():
            b = d + pd.Timedelta(hours=17)
            if prev_end <= b <= cur and b.dayofweek < 5:
                ra[i] += 3.0 if b.dayofweek == 4 else 1.0
            d += pd.Timedelta(days=1)
    return ra
