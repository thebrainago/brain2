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
    gia: float           # gia khop (gia BID nhu bieu do MT5; lenh mua chiu them spread trong `chay_tk`)
    chieu: int = 1       # +1 mua, -1 ban
    ma: str = ""         # 18/10/2026: ma giao dich (nhieu ma tren mot tai khoan, `chay_tk`); "" = ma duy nhat
    lot: float | None = None   # lot tang dau rieng cua lenh nay; None = QuanLi.lot0


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
    # ---- 18/10/2026: cac truong duoi day CHI dung trong `chay_tk` (cap tai khoan that). `chay` cu bo qua.
    lot0: float = 0.01                 # lot tang dau (lot THAT cua san, vd 0,01 micro / cent)
    tp_pct: float | None = None        # TP ro tinh tu GIA VON binh quan, phan cua gia (0.003 = 0,3 %); None -> tp_gia
    tp_gia: float | None = None        # TP ro theo DON VI GIA; None ca hai -> tp_diem * point
    mot_ro_moi_chieu: bool = True      # nhu EA: dang co ro (nguon, ma, chieu) thi bo lenh vao moi cung chieu
    trail_kich_pct: float = 0.0        # trailing ro: bat khi gia vuot gia von + X (phan cua gia); 0 = tat
    trail_khoang_pct: float = 0.0      # tra lai X tu dinh thi dong ro
    hedge_khi_lo_pct: float = 0.0      # ro lo tha noi >= X % so du -> mo lenh KHOA nguoc chieu (0 = tat)
    hedge_ti_le: float = 1.0           # lot khoa = tong lot ro x ti le
    mo_khoa_pct: float = 0.0           # mo khoa (dong lenh khoa) khi gia hoi X tu cuc tri sau khi khoa; 0 = khong tu mo
    hedge_max_lan: int = 3
    go_tien: float | None = None       # GO: ro + lenh khoa + lai da chot cua khoa >= X (tien) -> dong ca ro. None = tat
    cat_lo_pct: float = 0.0            # cat ca ro khi lo >= X % so du (0 = KHONG SL, mac dinh phong cach chu du an)


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


# =====================================================================================================================
# 18/10/2026 - CAP TAI KHOAN THAT (`chay_tk`). Mo rong engine nay, KHONG phai engine moi:
#   - cung mo hinh RO (TP tu gia von, DCA, go cheo) nhu `chay` o tren;
#   - them phan KY QUY / STOP-OUT lay dung logic cua `mo_phong.chay_he(tai_khoan=)` (ky quy = hop_dong*gia/don_bay*
#     max(lot mua, lot ban) moi ma; stop-out: von rong <= stop_out*ky quy -> san dong lenh LO NHAT truoc, tung lenh mot,
#     den khi muc ky quy > stop_out; lenh moi bi TU CHOI khi thieu ky quy tu do; lot_max);
#   - phi THEO SAN + THEO MA (`HoSoPhi`, lay tu `nhan/chi_phi` hoac reports/phi_san/ khi may nha da do): spread theo GIO
#     server, swap MUA va BAN rieng (diem/lot/dem, ngay x3 theo san), hoa hong / lot, point dung;
#   - nhieu ma, lenh ban, hedge chu dong (khoa - mo khoa - go), trailing ro, cat lo tuy chon (mac dinh KHONG SL).
# Don vi tien = tien tai khoan quy ve USD (cent: 1 USD = 100 USC, nhap `von` theo USD tuong duong).
# Gia trong DataFrame la BID (nhu bieu do MT5): mua vao o ASK = BID + spread, dong o BID; ban vao BID, dong o ASK.
# Thu tu trong nen (khong biet tu H1): swap -> TP/trailing -> khop DCA -> hedge/go/go cheo (gia dong) -> stop-out o gia
# BAT LOI NHAT cua nen cho MOI lenh cung luc (bao thu). Day la MO PHONG; phan xu cuoi la MT5.
# =====================================================================================================================
import json as _json
import math as _math
from pathlib import Path as _Path

_GOC = _Path(__file__).resolve().parent.parent
NHAN_PHI_TAM = "PHÍ TẠM"


@dataclass
class HoSoPhi:
    """Phi va thong so MOT ma tren MOT san. Moi so tien tinh cho 1 lot."""
    ma: str
    symbol: str = ""
    san: str = "XM"
    point: float = 1e-5
    hop_dong: float = 1000.0              # don vi co so / lot (XM micro va Exness cent deu ~1.000 USD-tuong-duong)
    quy_doi_usd: float | None = None      # 1 don vi tien YET GIA = ? USD. None -> tu suy (xxxUSD = 1, USDxxx = 1/gia)
    spread_gio: list = field(default_factory=lambda: [0.0] * 24)   # DON VI GIA, theo gio SERVER 0..23
    swap_mua_diem: float = 0.0            # diem / lot / dem (swap_mode DIEM cua MT5); am = tra
    swap_ban_diem: float = 0.0
    ngay_x3: int = 2                      # thu (0 = thu Hai) cua phien bi tinh x3; FX = thu Tu, chi so thuong thu Sau
    hoa_hong_lot: float = 0.0             # USD / lot / MOT chieu
    spread_nam: dict = field(default_factory=dict)   # {nam: he so} nhan spread_gio (config/phi_xm_micro.json); rong = 1
    lot_min: float = 0.01
    buoc_lot: float = 0.01
    lot_max: float = 100.0
    nhan: str = NHAN_PHI_TAM
    nguon: str = ""

    def qd(self, gia: float) -> float:
        if self.quy_doi_usd is not None:
            return float(self.quy_doi_usd)
        m = self.ma.upper()
        if m.endswith("USD") or m.startswith(("XAU", "US500", "US30", "US100")):
            return 1.0
        if m.startswith("USD"):
            return 1.0 / max(gia, 1e-12)
        return 1.0

    def lam_tron(self, lot: float) -> float:
        b = self.buoc_lot or 0.01
        return max(self.lot_min, round(_math.floor(lot / b + 1e-9) * b, 8))


@dataclass
class TaiKhoan:
    von: float = 1000.0          # USD tuong duong (cent: 10 USD = 1.000 USC)
    don_bay: float = 500.0
    stop_out: float = 0.2        # muc ky quy (0.2 = 20 %)
    ten: str = "XM_MICRO_TAM"
    nhan: str = NHAN_PHI_TAM


#: Ho so tai khoan TAM (CHUA DO tren tai khoan that cua chu du an; may nha do bang mt5tools/do_phi_san.py).
TAI_KHOAN_TAM = {
    "XM_MICRO_TAM": TaiKhoan(von=1000.0, don_bay=500.0, stop_out=0.2, ten="XM_MICRO_TAM"),
    "EXNESS_CENT_TAM": TaiKhoan(von=1000.0, don_bay=500.0, stop_out=0.0, ten="EXNESS_CENT_TAM"),
}

#: He so gian spread gio doi ngay (23h, 0h server) khi bang da luu KHONG do gio do (loi A4). Rollover rong 5-9 lan.
GIAN_DOI_NGAY_TAM = 5.0
#: Quy doi tien yet gia -> USD TAM cho cap cheo (khi khong co chuoi quy doi). Ghi nhan "QUY DOI TAM".
QUY_DOI_TAM = {"CAD": 0.73, "GBP": 1.27, "CHF": 1.12, "JPY": 0.0067, "AUD": 0.66, "NZD": 0.60, "EUR": 1.08}


def _phi_san_moi_nhat(san: str) -> _Path | None:
    """reports/phi_san/<server>/ (may nha do) cua san `san` (XM / Exness). Chon thu muc moi nhat."""
    goc = _GOC / "reports" / "phi_san"
    if not goc.exists():
        return None
    ds = [d for d in goc.iterdir() if d.is_dir() and san.lower() in d.name.lower() and (d / "ma.csv").exists()]
    return max(ds, key=lambda d: (d / "ma.csv").stat().st_mtime) if ds else None


def ho_so_phi(ma: str, san: str = "XM", phi_san_dir: _Path | None = None) -> HoSoPhi:
    """Ho so phi (xem _ho_so_phi_goc) + he so spread theo NAM cho XM (backtest du lieu dai)."""
    return _gan_spread_nam(_ho_so_phi_goc(ma, san, phi_san_dir))


def _ho_so_phi_goc(ma: str, san: str = "XM", phi_san_dir: _Path | None = None) -> HoSoPhi:
    """Ho so phi cho ma `ma` (ten goc, vd AUDCAD) tren san `san`.

    Uu tien: (1) reports/phi_san/<server>/ma.csv + spread_gio.csv (DO tren tai khoan that, may nha) -> nhan "ĐO";
    (2) PHÍ TẠM: swap diem tu config/chi_phi_do.json (`chi_phi.phi_cua`, san XM truoc), spread theo gio tu bang da luu
    (`chi_phi._spread_da_luu`, gio 23/0 thieu -> x GIAN_DOI_NGAY_TAM). Khi co (1) thi tu thay, khong can sua code.
    """
    import csv
    goc = ma.upper()
    d = phi_san_dir or _phi_san_moi_nhat(san)
    if d is not None:
        rows = list(csv.DictReader(open(d / "ma.csv", encoding="utf-8")))
        r = next((x for x in rows if (x.get("goc") or "").upper() == goc), None)
        if r is not None:
            def f(k, md=0.0):
                try:
                    return float(r.get(k) or md)
                except ValueError:
                    return md
            pt = f("point", 1e-5)
            sg = [None] * 24
            sp_f = d / "spread_gio.csv"
            if sp_f.exists():
                for x in csv.DictReader(open(sp_f, encoding="utf-8")):
                    if (x.get("goc") or "").upper() == goc:
                        sg[int(x["gio_server"]) % 24] = float(x.get("p50_gia") or 0.0)
            co = [v for v in sg if v]
            md = float(np.median(co)) if co else f("spread_gia_luc_do", 10 * pt)
            sg = [v if v else md for v in sg]
            thu = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "T2": 0, "T3": 1, "T4": 2, "T5": 3, "T6": 4}
            x3 = thu.get(str(r.get("ngay_x3") or "WED").upper()[:3], 2)
            sw_mode = str(r.get("swap_mode") or "DIEM").upper()
            hs = HoSoPhi(ma=goc, symbol=r.get("symbol", goc), san=san, point=pt, hop_dong=f("hop_dong", 1000.0),
                         spread_gio=sg, swap_mua_diem=f("swap_mua"), swap_ban_diem=f("swap_ban"), ngay_x3=x3,
                         hoa_hong_lot=f("hoa_hong_lot"), lot_min=f("lot_min", 0.01), buoc_lot=f("buoc_lot", 0.01),
                         lot_max=f("lot_max", 100.0), nhan="ĐO (%s)" % d.name, nguon=str(d))
            # 20/10/2026: cap CHEO (lai tinh bang tien yet gia khac USD, vd GBPNZD -> NZD) truoc day KHONG quy doi o
            # nhanh "ĐO" -> qd() = 1, lai Python = lai NZD coi la USD: GBPNZD lot 30 TP 0,5 %% Python +303 USD/lenh,
            # MT5 +190 USD (NZDUSD ~0,6) -> mot phan lon cua "lech ~2 lan" Python/MT5. Nay lay he so DO luc do phi:
            # tien_moi_1_gia_lot_min / (lot_min x hop_dong) = USD cho 1 don vi gia x 1 don vi co so.
            tl = str(r.get("tien_te_loi") or "").upper()
            if tl and tl != "USD" and not goc.startswith("USD"):
                t1 = f("tien_moi_1_gia_lot_min")
                if t1 > 0 and hs.lot_min > 0 and hs.hop_dong > 0:
                    hs.quy_doi_usd = t1 / (hs.lot_min * hs.hop_dong)
                    hs.nhan += " | QUY ĐỔI %s->USD %.4f (đo lúc đo phí)" % (tl, hs.quy_doi_usd)
                elif tl in QUY_DOI_TAM:
                    hs.quy_doi_usd = QUY_DOI_TAM[tl]
                    hs.nhan += " | QUY ĐỔI TẠM %s->USD %.4f" % (tl, hs.quy_doi_usd)
            if sw_mode not in ("DIEM", "1", "POINTS"):
                hs.nhan += " | swap_mode %s chua quy doi -> swap = 0, CHUA ĐO ĐƯỢC" % sw_mode
                hs.swap_mua_diem = hs.swap_ban_diem = 0.0
            return hs
    # (2) PHI TAM
    from nhan import chi_phi as CP
    luu = CP.phi_cua(goc, [san, "XM", "Exness", "FXCE", "MetaQuotes"]) or {}
    pt = float(luu.get("point") or (1e-3 if goc.endswith("JPY") else 1e-5))
    gia = float(luu.get("gia_luc_do") or 1.0)
    sp = CP._spread_da_luu(goc) or {}
    chung = float(sp.get("chung") or 1.5e-4)
    tg = {int(k): float(v) for k, v in (sp.get("theo_gio") or {}).items()}
    sg = [tg.get(h, chung) * gia for h in range(24)]
    for h in (23, 0):
        if h not in tg:
            sg[h] = chung * gia * GIAN_DOI_NGAY_TAM
    sw_ok = int(luu.get("swap_mode") or 0) == 1
    # hop dong / lot: lay contract_size da do (config/chi_phi_do.json; vd GOLDmicro 1, SILVERmicro 50), khong co thi 1.000
    hd = float(luu.get("contract_size") or 1000.0)
    hs = HoSoPhi(ma=goc, symbol=str(luu.get("symbol_lay") or goc), san=san, point=pt, hop_dong=hd, spread_gio=sg,
                 swap_mua_diem=float(luu.get("swap_long") or 0.0) if sw_ok else 0.0,
                 swap_ban_diem=float(luu.get("swap_short") or 0.0) if sw_ok else 0.0,
                 ngay_x3=2 if CP._loai_tai_san(goc) == "fx" else 4,
                 nhan="%s (swap %s:%s %s; spread bang luu %s, gio 23/0 x%.0f)" % (
                     NHAN_PHI_TAM, luu.get("san_lay", "?"), luu.get("symbol_lay", "?"), luu.get("do_luc", "?")[:10],
                     sp.get("symbol", "khai bao 1,5 bps"), GIAN_DOI_NGAY_TAM),
                 nguon="config/chi_phi_do.json")
    ten_yet = goc[3:6]
    if not (goc.endswith("USD") or goc.startswith("USD")) and ten_yet in QUY_DOI_TAM:
        hs.quy_doi_usd = QUY_DOI_TAM[ten_yet]
        hs.nhan += " | QUY ĐỔI TẠM %s->USD %.4f" % (ten_yet, hs.quy_doi_usd)
    if not sw_ok:
        hs.nhan += " | swap CHƯA ĐO ĐƯỢC (=0)"
    return hs


def _he_so_nam(idx, hs) -> np.ndarray:
    if not getattr(hs, "spread_nam", None):
        return np.ones(len(idx))
    from nhan.phi_dai import mang_he_so
    return mang_he_so(pd.DatetimeIndex(idx), hs.spread_nam)


def _gan_spread_nam(hs: "HoSoPhi") -> "HoSoPhi":
    """21/10/2026: XM -> he so spread theo nam tu config/phi_xm_micro.json (nhan.phi_dai). Khong co tep -> giu nguyen."""
    if hs.san != "XM" or hs.spread_nam:
        return hs
    from nhan.phi_dai import doc
    r = doc().get(hs.ma) or {}
    if r.get("spread_nam"):
        hs.spread_nam = {int(k): float(v) for k, v in r["spread_nam"].items()}
        hs.nhan += " | spread x hệ số năm (phi_xm_micro.json)"
    return hs


def ho_so_tai_khoan(ten: str = "XM_MICRO_TAM", von: float | None = None) -> TaiKhoan:
    """Tai khoan TAM; neu may nha da do (reports/phi_san/<server>/san.json: don_bay, stop_out) thi tu thay."""
    tk = TAI_KHOAN_TAM.get(ten, TAI_KHOAN_TAM["XM_MICRO_TAM"])
    tk = TaiKhoan(von=tk.von if von is None else float(von), don_bay=tk.don_bay, stop_out=tk.stop_out, ten=tk.ten, nhan=tk.nhan)
    d = _phi_san_moi_nhat("Exness" if "EXNESS" in ten.upper() else "XM")
    for tep in ((d / "san.json"), (d / "tai_khoan.json")) if d else ():
        if tep.exists():
            try:
                x = _json.loads(tep.read_text(encoding="utf-8"))
                tk.don_bay = float(x.get("don_bay") or tk.don_bay)
                if x.get("stop_out") is not None and str(x.get("so_mode", "PERCENT")).upper() == "PERCENT":
                    tk.stop_out = float(x["stop_out"]) / 100.0
                tk.nhan = "ĐO (%s)" % d.name
                break
            except Exception:
                pass
    return tk


def nen_server(df: pd.DataFrame) -> pd.DataFrame:
    """Chuan hoa bang gia: chi muc thoi gian (gio SERVER) + open/high/low/close float."""
    x = df[["open", "high", "low", "close"]].astype(float)
    x.index = pd.DatetimeIndex(x.index)
    return x[~x.index.duplicated()].sort_index()


def _dem_qua_dem(idx: pd.DatetimeIndex, ngay_x3: int) -> np.ndarray:
    """So dem swap phai tra cho lenh giu qua dau nen t: moi moc 00:00 server nam giua nen t-1 va t, NGAY TRUOC moc la
    thu Hai..thu Sau -> 1 dem (x3 neu ngay do == ngay_x3). Cuoi tuan khong tinh them (x3 da bu)."""
    n = len(idx)
    ra = np.zeros(n)
    if n < 2:
        return ra
    d = idx.normalize()
    for t in np.nonzero(d[1:] > d[:-1])[0] + 1:
        k = d[t - 1] + pd.Timedelta(days=1)
        while k <= d[t]:
            truoc = (k - pd.Timedelta(days=1)).dayofweek
            if truoc < 5:
                ra[t] += 3.0 if truoc == ngay_x3 else 1.0
            k += pd.Timedelta(days=1)
    return ra


@dataclass(eq=False)
class _Chan:
    ch: int
    gia: float
    lot: float
    sinh: int
    swap: float = 0.0     # USD da tich (am = tra) - nam trong vi the den khi dong, nhu MT5
    khoa: bool = False    # lenh khoa (hedge)


@dataclass(eq=False)
class _RoTK:
    id: int
    nguon: str
    ma: str
    s: int
    sinh: int
    chan: list = field(default_factory=list)
    muc: list = field(default_factory=list)      # (gia, lot) cac tang DCA con lai
    lot_ke: float = 0.0
    dinh: float | None = None                    # trailing: gia tot nhat tu khi kich
    tich: float = 0.0                            # lai/lo da CHOT cua lenh khoa (USD)
    so_khoa: int = 0
    cuc: float | None = None                     # cuc tri bat loi tu khi khoa (mo khoa)
    lo_max: float = 0.0
    ql: object = None


def chay_tk(du_lieu: dict | pd.DataFrame, luong: list[LenhVao], ql: QuanLi | dict, tk: TaiKhoan | None = None,
            phi: dict | HoSoPhi | None = None, ghi_von: bool = True, ghi_lenh: bool = False) -> dict:
    """ENGINE CAP TAI KHOAN (lot that, ky quy, stop-out, phi theo san). Xem khoi chu thich phia tren.

    du_lieu: {ma: DataFrame open/high/low/close, chi muc gio SERVER} hoac mot DataFrame (ma = "").
    luong: LenhVao (chi_so = vi tri nen tren TRUC THOI GIAN CHUNG; gia = gia BID luc khop, thuong la open nen do).
    ql: QuanLi chung, hoac {nguon: QuanLi}.  phi: {ma: HoSoPhi} hoac mot HoSoPhi (None -> ho_so_phi(ma)).
    -> dict: von_cuoi, lai_tien, lai_pct_nam, sut_giam_pct (von rong o gia bat loi nhat / dinh von rong), so_stop_out,
       so_lenh_stop_out, chay, muc_ky_quy_min, tu_choi_ky_quy, tu_choi_lot_max, phi (spread/swap/hoa_hong USD),
       nhat_ky (DataFrame moi ro), duong_von, nhan_phi.
       ghi_lenh=True: them "lenh" = DataFrame TUNG LENH (moi chan; lenh tach vi lot_max la nhieu dong) voi
       ro, ma, chieu, khoa, lot, mo (chi so nen), gia_mo, dong (None = con mo), gia_dong, lai_tien - de doi chieu MT5.
    """
    tk = tk or ho_so_tai_khoan()
    if isinstance(du_lieu, pd.DataFrame):
        du_lieu = {"": du_lieu}
    ds_ma = list(du_lieu)
    bang = {m: nen_server(du_lieu[m]) for m in ds_ma}
    idx = bang[ds_ma[0]].index
    for m in ds_ma[1:]:
        idx = idx.union(bang[m].index)
    n = len(idx)
    if isinstance(phi, HoSoPhi):
        phi = {ds_ma[0]: phi}
    phi = dict(phi or {})
    for m in ds_ma:
        if m not in phi:
            phi[m] = ho_so_phi(m or "EURUSD")
    A = {}
    for m in ds_ma:
        b = bang[m].reindex(idx)
        co = b["close"].notna().to_numpy()
        b = b.ffill().bfill()
        hs = phi[m]
        gio = idx.hour.to_numpy()
        A[m] = dict(o=b["open"].to_numpy(), h=b["high"].to_numpy(), l=b["low"].to_numpy(), c=b["close"].to_numpy(), co=co,
                    sp=np.asarray(hs.spread_gio, float)[gio] * _he_so_nam(idx, hs), dem=_dem_qua_dem(idx, hs.ngay_x3), hs=hs)
    lay_ql = (lambda nguon: ql.get(nguon) or ql.get("*")) if isinstance(ql, dict) else (lambda nguon: ql)
    su_kien: dict[int, list] = {}
    for e in luong:
        su_kien.setdefault(int(e.chi_so), []).append(e)

    von = float(tk.von)
    ro_mo: list[_RoTK] = []
    nk: list[dict] = []
    phi_tong = {"spread": 0.0, "swap": 0.0, "hoa_hong": 0.0}
    dem = {"so_stop_out": 0, "so_lenh_stop_out": 0, "tu_choi_ky_quy": 0, "tu_choi_lot_max": 0, "so_ro": 0,
           "so_lenh": 0, "so_khoa": 0, "so_go": 0, "so_go_cheo": 0, "so_tp": 0, "so_trail": 0, "so_cat_lo": 0}
    eq_c = np.zeros(n) if ghi_von else None
    eq_x = np.zeros(n) if ghi_von else None
    dinh_eq, dd_max, kq_min, chay_tk_ = float(tk.von), 0.0, float("inf"), False
    lot_mo_max, ro_mo_max, dem_id = 0.0, 0, [0]
    EPS = 1e-9
    so_lenh: dict = {}                      # _Chan -> ban ghi (ghi_lenh)
    ds_lenh: list[dict] = []

    def tien(m, ch, vao, ra, lot):
        hs = phi[m]
        return ch * (ra - vao) * lot * hs.hop_dong * hs.qd(ra)

    def gia_dong(m, ch, bid, t):           # gia dong lenh: mua dong o BID, ban dong o ASK
        return bid if ch > 0 else bid + A[m]["sp"][t]

    def loi_chan(r, L, bid, t):
        return tien(r.ma, L.ch, L.gia, gia_dong(r.ma, L.ch, bid, t), L.lot) + L.swap

    def ky_quy(t, gia_theo_ma=None):
        tong = 0.0
        for m in ds_ma:
            mua = sum(L.lot for r in ro_mo if r.ma == m for L in r.chan if L.ch > 0)
            ban = sum(L.lot for r in ro_mo if r.ma == m for L in r.chan if L.ch < 0)
            if mua or ban:
                g = A[m]["c"][t] if gia_theo_ma is None else gia_theo_ma[m]
                hs = phi[m]
                tong += hs.hop_dong * g * hs.qd(g) / tk.don_bay * max(mua, ban)
        return tong

    def noi_tong(t, theo):                 # theo: "c" (dong cua) | "x" (bat loi nhat moi lenh)
        s = 0.0
        for r in ro_mo:
            a = A[r.ma]
            for L in r.chan:
                bid = a["c"][t] if theo == "c" else (a["l"][t] if L.ch > 0 else a["h"][t])
                s += loi_chan(r, L, bid, t)
        return s

    def mo_chan(r, ch, lot, gia_bid, t, khoa=False) -> bool:
        nonlocal von
        m = r.ma
        hs = phi[m]
        lot = hs.lam_tron(lot)
        if lot > hs.lot_max + EPS:
            # lot_max la tran MOI LENH: san cho mo nhieu lenh -> tach (nhu EA tach lenh); qua 50 lenh thi tu choi
            n = int(_math.ceil(lot / hs.lot_max - 1e-9))
            if n > 50:
                dem["tu_choi_lot_max"] += 1
                return False
            con = lot
            for _ in range(n):
                p = min(con, hs.lot_max)
                con = round(con - p, 8)
                if p < hs.lot_min - EPS:
                    break
                if not mo_chan(r, ch, p, gia_bid, t, khoa):
                    return False
            return True
        sp = A[m]["sp"][t]
        gia = gia_bid + sp if ch > 0 else gia_bid
        # ky quy tu do (nhu chay_he._du_ky_quy): von rong sau khi them >= ky quy moi
        L = _Chan(ch=ch, gia=gia, lot=lot, sinh=t, khoa=khoa)
        r.chan.append(L)
        them = r not in ro_mo
        if them:
            ro_mo.append(r)
        g = {mm: A[mm]["c"][t] for mm in ds_ma}
        g[m] = gia_bid
        eq = von + sum(loi_chan(rr, LL, g[rr.ma], t) for rr in ro_mo for LL in rr.chan) - lot * hs.hoa_hong_lot
        if eq <= ky_quy(t, g) + EPS:
            r.chan.pop()
            if them:
                ro_mo.remove(r)
            dem["tu_choi_ky_quy"] += 1
            return False
        hh = lot * hs.hoa_hong_lot
        von -= hh
        phi_tong["hoa_hong"] += hh
        phi_tong["spread"] += sp * lot * hs.hop_dong * hs.qd(gia_bid)
        dem["so_lenh"] += 1
        if ghi_lenh:
            bg = dict(ro=r.id, nguon=r.nguon, ma=m, chieu=ch, khoa=bool(khoa), lot=lot, mo=t, gia_mo=gia,
                      dong=None, gia_dong=None, lai_tien=None)
            so_lenh[L] = bg
            ds_lenh.append(bg)
        return True

    def dong_chan(r, L, bid, t):
        nonlocal von
        hs = phi[r.ma]
        x = loi_chan(r, L, bid, t) - L.lot * hs.hoa_hong_lot
        von += x
        phi_tong["hoa_hong"] += L.lot * hs.hoa_hong_lot
        if ro_mo and r in ro_mo:
            r.chan.remove(L)
        if ghi_lenh and L in so_lenh:
            bg = so_lenh.pop(L)
            bg.update(dong=t, gia_dong=gia_dong(r.ma, L.ch, bid, t), lai_tien=round(x, 4))
        return x

    def dong_ro(r, bid, t, boi):
        lai = r.tich
        so_tang = sum(1 for L in r.chan if not L.khoa)
        for L in list(r.chan):
            lai += dong_chan(r, L, bid, t)
        if r in ro_mo:
            ro_mo.remove(r)
        nk.append(dict(id=r.id, nguon=r.nguon, ma=r.ma, chieu=r.s, sinh=r.sinh, dong=t, boi=boi, lai_tien=round(lai, 4),
                       lo_treo_max=round(r.lo_max, 4), so_khoa=r.so_khoa, ket_nen=t - r.sinh,
                       so_tang=so_tang))

    def gia_von(r):
        ch = [L for L in r.chan if not L.khoa]
        lot = sum(L.lot for L in ch)
        return (sum(L.gia * L.lot for L in ch) / lot, lot) if lot else (None, 0.0)

    for t in range(n):
        vua_dong: set = set()               # (nguon, ma, chieu) co ro dong TRONG nen t (TP/trailing o buoc 2)
        # 1) swap cho lenh giu qua moc 00:00 server
        for r in ro_mo:
            a = A[r.ma]
            if a["dem"][t] > 0:
                hs = phi[r.ma]
                for L in r.chan:
                    if L.sinh < t:
                        sw = (hs.swap_mua_diem if L.ch > 0 else hs.swap_ban_diem) * hs.point * L.lot * hs.hop_dong \
                            * hs.qd(a["c"][t - 1]) * a["dem"][t]
                        L.swap += sw
                        phi_tong["swap"] -= sw
        # 2) TP / trailing / cat lo / DCA cho ro sinh truoc t
        for r in list(ro_mo):
            a = A[r.ma]
            if r.sinh >= t or not a["co"][t]:
                continue
            q = r.ql
            gv, lot_ro = gia_von(r)
            if gv is None:
                continue
            sp = a["sp"][t]
            tp = q.tp_gia if q.tp_gia is not None else (q.tp_pct * gv if q.tp_pct else q.tp_diem * phi[r.ma].point)
            if r.so_khoa == 0 or not any(L.khoa for L in r.chan):
                tp_gia = gv + r.s * tp
                cham = (a["h"][t] >= tp_gia) if r.s > 0 else (a["l"][t] + sp <= tp_gia)
                if tp > 0 and cham:
                    dong_ro(r, tp_gia if r.s > 0 else tp_gia - sp, t, "tp")
                    dem["so_tp"] += 1
                    vua_dong.add((r.nguon, r.ma, r.s))
                    continue
                if q.trail_kich_pct > 0:
                    if r.dinh is not None:
                        stop = r.dinh * (1 - r.s * q.trail_khoang_pct)
                        if (a["l"][t] <= stop) if r.s > 0 else (a["h"][t] + sp >= stop):
                            dong_ro(r, stop if r.s > 0 else stop - sp, t, "trailing")
                            dem["so_trail"] += 1
                            vua_dong.add((r.nguon, r.ma, r.s))
                            continue
                    tot = a["h"][t] if r.s > 0 else a["l"][t] + sp
                    if r.s * (tot - gv) >= q.trail_kich_pct * gv:
                        r.dinh = tot if r.dinh is None else (max(r.dinh, tot) if r.s > 0 else min(r.dinh, tot))
            # DCA (sau TP, bao thu); khong nhoi khi dang khoa
            # 20/10/2026 (od_skea3279057100): EA xet KHOA truoc NHOI moi tick -> ngay sau khi mo khoa ma lo van >= nguong
            # thi EA khoa lai ngay, KHONG nhoi. Python truoc day nhoi 3 tang trong nen ke tiep (o gia muc cu) roi khoa 50 lot
            # (MT5 khoa 20). Nay: neu dau nen (gia dong nen t-1) ro dang du nguong khoa -> bo nhoi nen nay (buoc 4 se khoa).
            c0 = a["c"][t - 1] if t > 0 else a["c"][t]
            du_khoa = (q.hedge_khi_lo_pct > 0 and r.so_khoa < q.hedge_max_lan and not any(L.khoa for L in r.chan)
                       and sum(loi_chan(r, L, c0, t) for L in r.chan) <= -q.hedge_khi_lo_pct / 100.0 * von)
            if not any(L.khoa for L in r.chan) and not du_khoa:
                while r.muc:
                    g, lt = r.muc[0]
                    hit = (a["l"][t] + sp <= g) if r.s > 0 else (a["h"][t] >= g)
                    if not hit:
                        break
                    # gia da vuot muc tu dau nen (sau khoa / gap): EA mo o gia thi truong, khong o gia muc cu
                    gm = min(g, c0 + sp) if r.s > 0 else max(g, c0)
                    if not mo_chan(r, r.s, lt, gm - sp if r.s > 0 else gm, t):
                        break                      # tu choi (ky quy / lot_max): thu lai nen sau
                    r.muc.pop(0)
        # 3) lenh vao moi o nen t
        for e in su_kien.get(t, []):
            m = e.ma if e.ma in A else ds_ma[0]
            if not A[m]["co"][t]:
                continue
            q = lay_ql(e.nguon)
            if q is None:
                continue
            ch = 1 if int(e.chieu) >= 0 else -1
            if q.mot_ro_moi_chieu and any(r.nguon == e.nguon and r.ma == m and r.s == ch for r in ro_mo):
                continue
            # 20/10/2026: lenh vao o OPEN nen t xay ra TRUOC luc ro cung chieu cham TP/trailing trong nen t -> luc do
            # ro van mo, EA (mot ro moi chieu) BO lenh nay. Truoc day Python dong ro truoc roi mo lenh moi o gia open
            # (nhin truoc trong nen): od_skea0ca971ac32 Python 35 lenh / MT5 27, cac lenh "them" deu mo dung nen TP.
            if q.mot_ro_moi_chieu and (e.nguon, m, ch) in vua_dong:
                continue
            dem_id[0] += 1
            r = _RoTK(id=dem_id[0], nguon=e.nguon, ma=m, s=ch, sinh=t, ql=q)
            lot0 = float(e.lot if e.lot is not None else q.lot0)
            if not mo_chan(r, ch, lot0, float(e.gia), t):
                continue
            dem["so_ro"] += 1
            if q.dca_buoc_pct and q.dca_toi_da > 0:
                lt, gv0 = lot0, r.chan[0].gia
                for k in range(1, q.dca_toi_da + 1):
                    lt = lt * q.dca_he_so_lot
                    r.muc.append((gv0 * (1 - ch * q.dca_buoc_pct * k), lt))
        # 4) cuoi nen: hedge / mo khoa / go / cat lo (gia dong cua)
        for r in list(ro_mo):
            a = A[r.ma]
            if not a["co"][t] or r not in ro_mo:
                continue
            q = r.ql
            c = a["c"][t]
            noi = sum(loi_chan(r, L, c, t) for L in r.chan)
            khoa = [L for L in r.chan if L.khoa]
            if q.cat_lo_pct > 0 and noi + r.tich <= -q.cat_lo_pct / 100.0 * von:
                dong_ro(r, c, t, "cat_lo"); dem["so_cat_lo"] += 1
                continue
            if q.go_tien is not None and (khoa or r.tich) and noi + r.tich >= q.go_tien:
                dong_ro(r, c, t, "go"); dem["so_go"] += 1
                continue
            if khoa:
                r.cuc = c if r.cuc is None else (min(r.cuc, c) if r.s > 0 else max(r.cuc, c))
                if q.mo_khoa_pct > 0 and r.s * (c - r.cuc) >= q.mo_khoa_pct * r.cuc:
                    for L in khoa:
                        r.tich += dong_chan(r, L, c, t)
                    r.cuc = None
            elif q.hedge_khi_lo_pct > 0 and r.so_khoa < q.hedge_max_lan and noi <= -q.hedge_khi_lo_pct / 100.0 * von:
                lot_ro = sum(L.lot for L in r.chan)
                if mo_chan(r, -r.s, lot_ro * q.hedge_ti_le, c, t, khoa=True):
                    r.so_khoa += 1; dem["so_khoa"] += 1; r.cuc = c
        # 5) go cheo giua cac ro (nguon khac / ma khac) - nhu `chay`, theo TIEN
        nhom = {}
        for r in ro_mo:
            if r.ql is not None and r.ql.go_cheo:
                nhom.setdefault(id(r.ql), []).append(r)
        for ds in nhom.values():
            if len(ds) < 2:
                continue
            q = ds[0].ql
            val = {r.id: sum(loi_chan(r, L, A[r.ma]["c"][t], t) for L in r.chan) + r.tich for r in ds}
            for b in sorted([r for r in ds if val[r.id] < 0], key=lambda r: r.sinh):
                if b not in ro_mo:
                    continue
                can = -val[b.id] + q.go_nguong_diem
                thang = sorted([w for w in ds if w is not b and w in ro_mo and val[w.id] > 0], key=lambda w: -val[w.id])
                tich, chon = 0.0, []
                for w in thang:
                    chon.append(w); tich += val[w.id]
                    if tich >= can:
                        break
                if chon and tich >= can:
                    for r in [b] + chon:
                        dong_ro(r, A[r.ma]["c"][t], t, "go_cheo")
                    dem["so_go_cheo"] += 1
        # 6) stop-out o gia BAT LOI NHAT cua nen (moi lenh cung luc - bao thu), dong lenh lo nhat truoc
        if ro_mo:
            gx = {}
            for m in ds_ma:
                gx[m] = A[m]["c"][t]
            eq = von + noi_tong(t, "x")
            kq = ky_quy(t)
            if kq > 0:
                kq_min = min(kq_min, eq / kq)
                if eq <= tk.stop_out * kq + 1e-6:
                    dem["so_stop_out"] += 1
                    while ro_mo:
                        cac = [(loi_chan(r, L, (A[r.ma]["l"][t] if L.ch > 0 else A[r.ma]["h"][t]), t), r, L)
                               for r in ro_mo for L in r.chan]
                        if not cac:
                            break
                        x, r, L = min(cac, key=lambda z: (z[0], z[2].sinh))
                        bid = A[r.ma]["l"][t] if L.ch > 0 else A[r.ma]["h"][t]
                        dong_chan(r, L, bid, t)
                        dem["so_lenh_stop_out"] += 1
                        if not [LL for LL in r.chan if not LL.khoa]:
                            for LL in list(r.chan):
                                dong_chan(r, LL, A[r.ma]["c"][t], t)
                            if r in ro_mo:
                                ro_mo.remove(r)
                            nk.append(dict(id=r.id, nguon=r.nguon, ma=r.ma, chieu=r.s, sinh=r.sinh, dong=t, boi="stop_out",
                                           lai_tien=None, lo_treo_max=round(r.lo_max, 4), so_khoa=r.so_khoa,
                                           ket_nen=t - r.sinh, so_tang=0))
                        eq = von + noi_tong(t, "x")
                        kq = ky_quy(t)
                        if kq <= 0 or eq > tk.stop_out * kq + 1e-6:
                            break
        # 7) so do
        for r in ro_mo:
            a = A[r.ma]
            lx = sum(loi_chan(r, L, (a["l"][t] if L.ch > 0 else a["h"][t]), t) for L in r.chan) + r.tich
            r.lo_max = max(r.lo_max, -lx)
        e_c = von + noi_tong(t, "c") if ro_mo else von
        e_x = von + noi_tong(t, "x") if ro_mo else von
        if ghi_von:
            eq_c[t], eq_x[t] = e_c, e_x
        dinh_eq = max(dinh_eq, e_c)
        if dinh_eq > 0:
            dd_max = max(dd_max, (dinh_eq - e_x) / dinh_eq)
        lot_mo_max = max(lot_mo_max, sum(L.lot for r in ro_mo for L in r.chan))
        ro_mo_max = max(ro_mo_max, len(ro_mo))
        if e_x <= 0.0 or von <= 0.0:
            chay_tk_ = True
            for r in list(ro_mo):
                dong_ro(r, A[r.ma]["c"][t], t, "chay")
            if ghi_von:
                eq_c[t:], eq_x[t:] = min(e_c, 0.0), min(e_x, 0.0)
            break
    # ro con mo cuoi du lieu: tinh theo gia dong cuoi (khong dong)
    t_cuoi = n - 1
    noi_cuoi = noi_tong(t_cuoi, "c") if ro_mo else 0.0
    for r in ro_mo:
        nk.append(dict(id=r.id, nguon=r.nguon, ma=r.ma, chieu=r.s, sinh=r.sinh, dong=t_cuoi, boi="mo",
                       lai_tien=round(sum(loi_chan(r, L, A[r.ma]["c"][t_cuoi], t_cuoi) for L in r.chan) + r.tich, 4),
                       lo_treo_max=round(r.lo_max, 4), so_khoa=r.so_khoa, ket_nen=t_cuoi - r.sinh, so_tang=len(r.chan)))
    von_cuoi = von + noi_cuoi
    nam = max((idx[-1] - idx[0]).days / 365.25, 1e-9) if n > 1 else 1e-9
    if chay_tk_ or von_cuoi <= 0:
        lai_pct_nam = -100.0
    else:
        lai_pct_nam = ((von_cuoi / tk.von) ** (1.0 / nam) - 1.0) * 100.0
    nk_df = pd.DataFrame(nk)
    ket = nk_df["ket_nen"].max() if len(nk_df) else 0
    return dict(von_dau=tk.von, von_cuoi=round(von_cuoi, 4), lai_tien=round(von_cuoi - tk.von, 4),
                lai_pct_nam=round(lai_pct_nam, 3), sut_giam_pct=round(dd_max * 100.0, 3), so_nam=round(nam, 2),
                chay=bool(chay_tk_), muc_ky_quy_min_pct=(round(kq_min * 100, 1) if kq_min < float("inf") else None),
                lot_mo_max=round(lot_mo_max, 4), ro_mo_max=ro_mo_max, ket_nen_max=int(ket or 0),
                phi={k: round(v, 4) for k, v in phi_tong.items()}, nhat_ky=nk_df, duong_von=eq_c, von_xau=eq_x,
                chi_muc=idx, tai_khoan=dict(ten=tk.ten, von=tk.von, don_bay=tk.don_bay, stop_out=tk.stop_out, nhan=tk.nhan),
                nhan_phi={m: phi[m].nhan for m in ds_ma}, nhan="MÔ PHỎNG",
                **({"lenh": pd.DataFrame(ds_lenh)} if ghi_lenh else {}), **dem)
