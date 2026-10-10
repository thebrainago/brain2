# -*- coding: utf-8 -*-
"""luoi_duong.py - mo phong luoi `ThamSo` theo DUONG GIA trong nen (P1, 10/10/2026).

Vi sao co file nay (khong sua `luoi.chay`): P1 cua goi ban giao the-brain do `luoi.chay`
(ban "cuc tri": them tang o LOW -> chot cap tia o HIGH -> TP, moi nen) voi 15 o MT5 tester
sach (H1 AUDCAD/NZDCAD 2019-03..08). Ket qua + cach doc: `hieu_chuan/P1_KET_QUA.md`.
File nay la ban doi chung theo dung luat EA `ea_LuoiDayDu.mq5` (the-brain, chi doc y):
  - moi logic theo BID; spread tra MOT lan moi lenh luc mo (luoi.chay tru them spread khi tia);
  - them tang khi BID di nguoc >= buoc(k) tu gia mo tang SAU CUNG, khop tai MOC (nhay gia:
    khop tai gia nhay, toi da mot tang moi "tick");
  - tia lenh: cap (som nhat, muon nhat) dong khi gia >= trung binh-lot cua cap + bien_cap,
    khop tai GIA NGUONG (khong phai cuc tri nen); ro tia het -> mo lai tang 1 ngay;
  - TP = trung binh BID co trong so lot +- tp, khop tai nguong (nhay gia: tai gia nhay);
  - lot lam tron toi buoc 0,01 gan nhat, toi thieu 0,01 (`ChuanLot` cua EA) - `lam_tron_lot`;
  - het cua so: dong het o gia dong cuoi (tester "end of test").
Thu tu gia trong nen (`thu_tu`): "gan_open" (= `mo_phong._duong_bar`), "thap_truoc",
"cao_truoc", "mau_nen" (xanh O-L-H-C, do O-H-L-C). Nen H1 an het dao dong nho ben trong
-> moi thu tu deu chi la GIA DINH; bao KHOANG giua cac thu tu, khong chon ban dep.
Swap (G06, 11/10/2026): TUY CHON `swap_nam` (mac dinh None = khong swap, giong het P1): ti le THU
nhap/nam theo notional cho (mua, ban), so hoac mang (n, 2) theo nen; tinh cho lot CON MO qua moi
rollover nua dem gio server (`chi_phi.dem_qua_dem`: thu Tu x3, T7/CN 0), cong vao tai khoan (va equity)
ngay luc rollover. Chua co: stop-out tung lenh (chi gan co `cham_stopout`),
cho_lui / chot_tien / dung_lo_tong (15 o P1 deu tat) -> gap tham so do thi bao loi.
Don vi: tien BAO GIA (CAD voi xxxCAD); `quy_doi` (mang, so don vi bao gia / 1 don vi tai
khoan, vd USDCAD tung nen) de doi lai/lo sang tien tai khoan TAI LUC phat sinh.
Quan tri ro (G08 / G-a, 11/10/2026) - TUY CHON, mac dinh tat (= giong het truoc tung so):
  - `chot_usd`: dong CA RO khi lai noi cua ro (tien tai khoan, chua tru spread da tra) >= X USD (thay TP pip);
  - `duoi`=(kich_pip, lui_pip): bo TP pip; khi gia vuot trung binh + kich_pip thi theo dinh, dong ca ro khi
    gia lui `lui_pip` tu dinh (khop tai nguong; nhay gia: tai gia nhay);
  - `dung_gio`: ro (tinh tu luc mo tang 1) song >= N gio -> dong ca ro tai gia mo nen, mo lai tang 1.
KET QUA LA MO PHONG, KHONG PHAI TIEN THAT.
"""
from __future__ import annotations

import numpy as np

from nhan.luoi import HOP_DONG, PIP, ThamSo

THU_TU = ("gan_open", "thap_truoc", "cao_truoc", "mau_nen")


def duong(o, h, l, c, thu_tu: str) -> tuple:
    if thu_tu == "thap_truoc":
        return (o, l, h, c)
    if thu_tu == "cao_truoc":
        return (o, h, l, c)
    if thu_tu == "mau_nen":
        return (o, l, h, c) if c >= o else (o, h, l, c)
    if abs(h - o) < abs(o - l):                     # gan_open = mo_phong._duong_bar
        return (o, h, l, c)
    if abs(h - o) > abs(o - l):
        return (o, l, h, c)
    return (o, l, h, c) if c >= o else (o, h, l, c)


class _Ro:
    """Mot ro (mot chieu). Gia theo BID; tien theo don vi bao gia."""

    def __init__(self, chieu: int, ts: ThamSo, lam_tron_lot: bool, spread: float,
                 chot_usd: float | None = None, duoi: tuple | None = None):
        self.c, self.ts, self.lt, self.sp = chieu, ts, lam_tron_lot, spread
        self.chot_usd, self.duoi = chot_usd, duoi
        self.dinh: float | None = None              # dinh gia (theo chieu ro) khi duoi da kich hoat
        self.dv_hien = 1.0                          # quy doi nen hien tai (cho chot_usd)
        self.t_hien = None                          # thoi diem nen hien tai (cho dung_gio)
        self.t0 = None                              # thoi diem mo tang 1 cua ro hien tai
        self.so_duoi = self.so_dung = 0
        self.vao: list[tuple[float, float]] = []    # (gia BID mo, lot), theo thu tu mo
        self.k = 0                                  # so tang DA mo cua ro (khong tut khi tia)
        self.chot = 0.0                             # lai/lo da chot (sau spread) tu dau
        self.so_dong = self.so_mo = self.so_ro = self.so_cap = 0
        self.tang_max = 0
        self.tia_nen = 0

    def lot(self, k: int) -> float:
        ts = self.ts
        if ts.kieu_lot == "nhan":
            x = ts.lot * ts.he_so_lot ** k
        elif ts.kieu_lot == "cong":
            x = ts.lot * (1.0 + ts.he_so_lot * k)
        else:
            x = ts.lot
        if self.lt:
            x = max(0.01, np.floor(x / 0.01 + 0.5 + 1e-9) * 0.01)
        return x

    def buoc(self, k: int) -> float:
        ts = self.ts
        if ts.he_so_buoc == 1.0:
            return ts.buoc
        return min(ts.buoc * ts.he_so_buoc ** k, ts.buoc_tran)

    def mo(self, gia: float, dv: float, lai_tk: list):
        l = self.lot(self.k)
        if self.k == 0:
            self.t0 = self.t_hien
            self.dinh = None
        self.vao.append((gia, l))
        self.k += 1
        self.so_mo += 1
        phi = self.sp * l * HOP_DONG
        self.chot -= phi
        lai_tk[0] -= phi / dv
        self.tang_max = max(self.tang_max, len(self.vao))

    def _dong(self, idx: list[int], gia: float, dv: float, lai_tk: list):
        for i in sorted(idx, reverse=True):
            g, l = self.vao.pop(i)
            x = self.c * (gia - g) * l * HOP_DONG
            self.chot += x
            lai_tk[0] += x / dv
            self.so_dong += 1

    def noi(self, gia: float) -> float:
        return sum(self.c * (gia - g) * l for g, l in self.vao) * HOP_DONG

    def moc_tang(self) -> float | None:
        if not self.vao or len(self.vao) >= self.ts.tran_tang:
            return None
        return self.vao[-1][0] - self.c * self.buoc(self.k - 1) * PIP

    def moc_tia(self) -> float | None:
        if not self.ts.tia_lenh or len(self.vao) < 2 or self.tia_nen >= self.ts.cap_moi_bar:
            return None
        (gd, ld), (gc, lc) = self.vao[0], self.vao[-1]
        return (gd * ld + gc * lc) / (ld + lc) + self.c * self.ts.bien_cap * PIP

    def tb(self) -> float:
        tl = sum(l for _g, l in self.vao)
        return sum(g * l for g, l in self.vao) / tl

    def moc_tp(self) -> float | None:
        if not self.vao or self.duoi is not None:
            return None
        if self.chot_usd is not None:
            tl = sum(l for _g, l in self.vao)
            return self.tb() + self.c * self.chot_usd * self.dv_hien / (tl * HOP_DONG)
        return self.tb() + self.c * self.ts.tp * PIP

    def moc_duoi(self) -> float | None:
        """Nguong dong theo duoi (chi khi da kich hoat)."""
        if self.duoi is None or not self.vao or self.dinh is None:
            return None
        return self.dinh - self.c * self.duoi[1] * PIP

    def cap_nhat_dinh(self, gia: float):
        if self.duoi is None or not self.vao:
            return
        if self.dinh is None:
            if self.c * (gia - (self.tb() + self.c * self.duoi[0] * PIP)) >= 0:
                self.dinh = gia
        elif self.c * (gia - self.dinh) > 0:
            self.dinh = gia

    def dong_ro(self, gia: float, dv: float, lai_tk: list):
        self._dong(list(range(len(self.vao))), gia, dv, lai_tk)
        self.k = 0
        self.mo(gia, dv, lai_tk)

    def toi(self, gia_tu: float, gia_den: float, dv: float, lai_tk: list, nhay: bool):
        """Di gia don dieu tu `gia_tu` toi `gia_den` (nhay=True: chi co gia den, khong co gia giua)."""
        c = self.c
        if not self.vao:                            # (chi xay ra o tick dau)
            self.mo(gia_den, dv, lai_tk)
            return
        if c * (gia_den - gia_tu) < 0 or (nhay and c * (gia_den - gia_tu) <= 0):
            # doan NGUOC chieu ro: (duoi) dong ro neu lui toi nguong - nguong duoi luon tren trung binh
            # nen gap TRUOC moc them tang; sau do them tang
            md = self.moc_duoi()
            if md is not None and c * (gia_den - md) <= 0:
                gia = gia_den if (nhay or c * (md - gia_tu) > 0) else md
                self.dong_ro(gia, dv, lai_tk)
                self.so_duoi += 1
                self.so_ro += 1
                if nhay:
                    return
                gia_tu = gia
            if nhay:
                m = self.moc_tang()
                if m is not None and c * (gia_den - m) <= 0:
                    self.mo(gia_den, dv, lai_tk)
                # sau nhay: van co the cham tia/TP? khong - gia di nguoc
                return
            for _ in range(10_000):
                m = self.moc_tang()
                if m is None or c * (gia_den - m) > 0:
                    break
                self.mo(m, dv, lai_tk)
            return
        # doan THUAN chieu: tia / TP tai nguong, theo thu tu gap tren duong
        for _ in range(100_000):
            ev = []
            mt = self.moc_tia()
            if mt is not None:
                ev.append((mt, 0))
            mp = self.moc_tp()
            if mp is not None:
                ev.append((mp, 1))
            ev = [(m, t) for m, t in ev if c * (gia_den - m) >= 0]
            if not ev:
                break
            m, t = min(ev, key=lambda e: (c * e[0], e[1]))
            if nhay:
                gia = gia_den                       # nhay gia: khop tai gia nhay
            elif c * (m - gia_tu) < 0:
                gia = gia_tu                        # nguong da bi vuot (sau mot lan dong): khop ngay tai gia hien tai
            else:
                gia = m                             # khop tai nguong
            if t == 0:
                self._dong([0, len(self.vao) - 1], gia, dv, lai_tk)
                self.so_cap += 1
                self.tia_nen += 1
                if not self.vao:
                    self.k = 0
                    self.mo(gia, dv, lai_tk)
            else:
                self._dong(list(range(len(self.vao))), gia, dv, lai_tk)
                self.so_ro += 1
                self.k = 0
                self.mo(gia, dv, lai_tk)
            gia_tu = gia
        self.cap_nhat_dinh(gia_den)


def chay_duong(df, ts: ThamSo, von_tk: float, thu_tu: str = "gan_open",
               spread_pip: float = 2.0, quy_doi=None, lam_tron_lot: bool = True,
               swap_nam=None, chot_usd: float | None = None, duoi: tuple | None = None,
               dung_gio: float | None = None) -> dict:
    """Mo phong ThamSo tren nen OHLC theo `thu_tu`. `von_tk` bang tien TAI KHOAN; `quy_doi`
    (mang cung do dai df hoac so) = don vi bao gia tren 1 don vi tai khoan (USDCAD).
    Tra lai/nam %, maxDD % (dinh-xuong cua equity tai cac diem duong), so lenh dong."""
    if ts.cho_lui or ts.chot_tien or ts.dung_lo_tong:
        raise ValueError("luoi_duong: cho_lui / chot_tien / dung_lo_tong chua cai dat")
    if thu_tu not in THU_TU:
        raise ValueError(thu_tu)
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    n = len(c)
    dv = np.broadcast_to(np.asarray(1.0 if quy_doi is None else quy_doi, float), (n,))
    chieus = {"mua": (1,), "ban": (-1,), "hai_chieu": (1, -1)}[ts.che_do]
    ros = [_Ro(x, ts, lam_tron_lot, spread_pip * PIP, chot_usd, duoi) for x in chieus]
    tg = df.index
    han = None if dung_gio is None else np.timedelta64(int(round(dung_gio * 3600)), "s")
    lai_tk = [0.0]
    dinh = von_tk
    dd = 0.0
    cham_so = False
    gia_truoc = None
    swap_tk = 0.0
    lot_dem = [0.0, 0.0]                            # lot x dem (co trong so) mua / ban - do phoi bay
    if swap_nam is not None:
        from nhan.chi_phi import dem_qua_dem
        dem = dem_qua_dem(df.index)
        sw = np.broadcast_to(np.asarray(swap_nam, float), (n, 2))
    for i in range(n):
        if swap_nam is not None and i > 0 and dem[i - 1] > 0:
            for r in ros:
                tl = sum(x for _g, x in r.vao)
                if tl <= 0:
                    continue
                k = 0 if r.c == 1 else 1
                lot_dem[k] += tl * dem[i - 1]
                x = sw[i - 1, k] * tl * HOP_DONG * c[i - 1] * dem[i - 1] / 365.0 / dv[i - 1]
                lai_tk[0] += x
                swap_tk += x
        pts = duong(o[i], h[i], l[i], c[i], thu_tu)
        for r in ros:
            r.tia_nen = 0
            r.dv_hien = dv[i]
            r.t_hien = tg[i]
        for j, p in enumerate(pts):
            for r in ros:
                if j == 0:
                    if gia_truoc is None:
                        r.mo(p, dv[i], lai_tk)
                    else:
                        r.toi(gia_truoc, p, dv[i], lai_tk, nhay=True)
                    if han is not None and r.vao and r.t0 is not None and (tg[i] - r.t0) >= han:
                        r.dong_ro(p, dv[i], lai_tk)
                        r.so_dung += 1
                else:
                    r.toi(pts[j - 1], p, dv[i], lai_tk, nhay=False)
            eq = von_tk + lai_tk[0] + sum(r.noi(p) for r in ros) / dv[i]
            dinh = max(dinh, eq)
            dd = max(dd, (dinh - eq) / dinh)
            lot_m = max(sum(x for _g, x in r.vao) for r in ros)
            ky_quy = lot_m * HOP_DONG * p / ts.don_bay / dv[i]
            if eq <= ts.muc_stopout * ky_quy:
                cham_so = True
        gia_truoc = c[i]
    # het cua so: dong het o gia dong cuoi
    for r in ros:
        r._dong(list(range(len(r.vao))), c[-1], dv[-1], lai_tk)
    ngay = (df.index[-1] - df.index[0]).total_seconds() / 86400.0
    return {
        "lai_tk": lai_tk[0], "ngay": ngay,
        "maxdd_pct": dd * 100.0,
        "so_lenh": sum(r.so_dong for r in ros),
        "so_cap": sum(r.so_cap for r in ros), "so_ro": sum(r.so_ro for r in ros),
        "tang_max": max(r.tang_max for r in ros), "cham_stopout": cham_so,
        "so_duoi": sum(r.so_duoi for r in ros), "so_dung_gio": sum(r.so_dung for r in ros),
        "swap_tk": swap_tk, "lot_dem_mua": lot_dem[0], "lot_dem_ban": lot_dem[1],
    }
