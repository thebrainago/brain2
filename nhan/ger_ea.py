# -*- coding: utf-8 -*-
"""ger_ea.py - THU VIEN `GerEA` (geraked/metatrader5, EAUtils.mqh) DICH THANH CO CHE DUNG LAI (12/10/2026).

Vi sao: repo geraked/metatrader5 (655 sao, ~50 EA, moi EA kem `.set` cua tac gia) dat lenh qua lop
`GerEA` (`ea.BuyOpen(in, sl, tp, IgnoreSL, IgnoreTP)`), quan ly bang `OnTimer`: `CheckForTrail` (keo SL
theo % khoang cach vao), `CheckForGrid` (them tang luoi, nhan lot, TP CA RO), `CheckForEquity`. Bo doc
`doc_ma` khong thay lenh vao (no nam trong thu vien) va khong co dong co luoi kieu nay -> 6 goi co
`.set` deu "khong_dat_lenh". File nay dich DUNG MOT LAN phan quan ly cua thu vien (doc tu
`EAUtils.mqh`, dan dong o tung muc), dung cho MOI EA cua ho nay: EA chi con phai cap tin hieu
(bar, huong, muc SL goc, muc TP goc). Khong co tham so nao chinh theo ket qua.

LUAT (doc tu EAUtils.mqh; "GIA DINH" = cho mo phong khong tai hien duoc):
  1. Vao lenh: OnTick, tick DAU cua bar moi, chi khi khong co vi the/lenh cho cua magic
     (`(Grid || !MultipleOpenPos) && ea.OPTotal() > 0 -> return`). `BuySignal()` truoc, sai moi
     `SellSignal()`. Gia: mua ASK, ban BID cua tick do (= open bar; BID tu du lieu, ASK = BID + spread).
  2. `BuyOpen(in,sl,tp,isl,itp)` (ban 9 tham so): `if(grid) isl=true`; comment = d = |in - sl| (gia).
     `reverse` -> `order(SELL, Bid, sl=tp, tp=sl, isl=itp, itp=isl)` (dao SL/TP va co bo qua).
     `order()`: tu choi neu sl/tp sai phia gia (`sl>=Bid` voi mua...) TRUOC khi bo; khoi luong
     `calcVolume` = min(balance, margin_free)*risk / (|in-sl| * gia_tri_diem), lam tron 0.01,
     kep [0.01, lot_max] (ve sl=0 thi dung tp); roi `isl -> sl=0`, `itp -> tp=0`.
  3. `checkForTrail` (vi the co comment d != 0, ro 1 lenh): mua: Bid > pin ->
     sl = max(pin, hoa_von) + (Bid - pin) - L*d, chi dat khi sl >= pin va siet hon; neu Bid - sl < 30
     diem -> dong ngay neu lai > phi. Ban doi xung voi Ask. Ro nhieu lenh (k==1) -> nhanh "grid
     trailing", TAT khi GridTrailingStopLevel = 0 (ca 6 .set) - nhanh do CHUA DICH (bao loi neu bat).
  4. `checkForGrid`: n lenh (1 <= n < maxLvl), lenh dau co d: mua: lvl = pin - n*d (lech > 0.5d so voi
     gia lenh thap nhat - d -> lvl = gia_thap_nhat - d); |gia_thap_nhat - Ask| >= 30 diem; Bid <= lvl
     -> mo MUA lot = lot_lon_nhat * volMult (lam tron), TP CA RO = gia ma tong lai = loss1 (+ phi neu
     > 0), loss1 = lot_dau * gia_tri * d; TP toi thieu 30 diem; dat TP do cho moi lenh, SL giu
     psl. Lenh tu choi (thieu ky quy) -> thu lai lan sau.
  5. Timer 30-60 s: GIA DINH kiem LIEN TUC tren duong gia trong bar (O -> cuc gan -> cuc xa -> C,
     `luoi_duong.duong(..,"gan_open")`); su kien tren mot doan don dieu xu ly theo thu tu gap.
  6. Tai khoan (cung khai bao `vong_thu_nghiem.TAI_KHOAN_MAC_DINH`): ky quy = lot*hop_dong*gia/don_bay
     (USDxxx: lot*hop_dong/don_bay); STOP-OUT: von_rong <= stop_out*ky_quy -> dong lenh lo nhat tung
     lenh. Phi: spread theo gio (`chi_phi`), truot gia moi lan khop, qua dem tung lenh (`phi_giu_mang`).
  7. KHONG dich: tin tuc (`News=false` o ca 6 .set), `EquityDrawdownLimit` (=0), martingale theo lich su
     (`martingale=false`), `MarginLimit` (chi chan lenh MOI khi da co vi the - da bi luat 1 chan).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

DIEM_TOI_THIEU = 30          # `minPoints = 30` trong checkForTrail/checkForGrid


@dataclass
class ThamSoGer:
    risk: float = 0.01                 # ea.risk = Risk*0.01
    ignore_sl: bool = True
    ignore_tp: bool = True
    trail: bool = True
    trail_level: float = 0.5           # TrailingStopLevel*0.01
    grid: bool = False
    grid_vol_mult: float = 1.0
    grid_trail_level: float = 0.0
    grid_max_lvl: int = 20
    reverse: bool = False
    multiple_open_pos: bool = False


@dataclass
class TaiKhoan:
    von: float = 10000.0
    don_bay: float = 100.0
    stop_out: float = 0.5
    lot_max: float = 100.0
    lot_min: float = 0.01
    buoc_lot: float = 0.01


def hop_dong_cua(ma: str) -> float:
    m = ma.upper()
    return 100.0 if m.startswith(("XAU", "GOLD")) else 100000.0


def _quote_usd(ma: str) -> bool:
    return ma.upper()[3:6] == "USD" or ma.upper().startswith(("XAU", "GOLD"))


def _lam_tron(v: float, tk: TaiKhoan) -> float:
    v = math.floor(v / tk.buoc_lot + 0.5 + 1e-9) * tk.buoc_lot     # NormalizeDouble(vol, 2)
    return float(min(max(round(v, 2), tk.lot_min), tk.lot_max))


@dataclass
class KetQuaGer:
    von_cuoi: float
    duong_von: pd.Series                 # von rong cuoi moi bar
    von_thap: pd.Series                  # von rong THAP nhat trong bar (gom lo tha noi)
    ro: list = field(default_factory=list)
    so_lenh: int = 0
    so_stop_out: int = 0
    tang_max: int = 0
    lot_max: float = 0.0
    tu_choi: int = 0
    phi_qua_dem: float = 0.0
    chay: bool = False
    canh_bao: list = field(default_factory=list)


def chay(df: pd.DataFrame, tin_hieu: dict, ts: ThamSoGer, cp, ma: str, diem: float,
         tk: TaiKhoan | None = None, thu_tu: str = "gan_open") -> KetQuaGer:
    """`tin_hieu`: {"huong": int[n] (+1 BuySignal, -1 SellSignal, 0), "sl": float[n], "tp": float[n]}
    tinh tai tick dau bar j (chi dung bar <= j-1 va open j). Gia df = BID."""
    tk = tk or TaiKhoan()
    if ts.grid and ts.grid_trail_level:
        raise NotImplementedError("GridTrailingStopLevel > 0: nhanh grid trailing chua dich")
    n = len(df)
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    idx = df.index
    sp = cp.spread_mang(idx)
    truot = float(getattr(cp, "truot_gia_frac", 0.0) or 0.0)
    pm = cp.phi_giu_mang(idx, np.ones(n))
    pb = cp.phi_giu_mang(idx, -np.ones(n))
    hd = hop_dong_cua(ma)
    qusd = _quote_usd(ma)
    fx = (lambda p: 1.0) if qusd else (lambda p: 1.0 / p)
    from nhan.luoi_duong import duong

    B = tk.von
    legs: list[dict] = []          # {c, lot, gia, d, sl, tp, sw}
    kq = KetQuaGer(von_cuoi=B, duong_von=None, von_thap=None)
    ro_hien: dict | None = None
    eq_c = np.empty(n)
    eq_l = np.empty(n)
    kc = DIEM_TOI_THIEU * diem

    def loi(L, p_bid, s):           # lai/lo USD (dong: mua o BID, ban o ASK)
        px = p_bid if L["c"] > 0 else p_bid + s
        return L["lot"] * hd * L["c"] * (px - L["gia"]) * fx(p_bid)

    def ky_quy(p_bid):
        if not legs:
            return 0.0
        lm = sum(L["lot"] for L in legs if L["c"] > 0)
        lb = sum(L["lot"] for L in legs if L["c"] < 0)
        return max(lm, lb) * hd * (p_bid if qusd else 1.0) / tk.don_bay

    def von_rong(p_bid, s):
        return B + sum(loi(L, p_bid, s) - L["sw"] for L in legs)

    def dong(L, p_bid, s, ly_do):
        nonlocal B
        px = p_bid if L["c"] > 0 else p_bid + s
        px_t = px * (1 - truot) if L["c"] > 0 else px * (1 + truot)      # truot bat loi
        B += L["lot"] * hd * L["c"] * (px_t - L["gia"]) * fx(p_bid) - L["sw"]
        kq.phi_qua_dem += L["sw"]
        legs.remove(L)
        if ro_hien is not None:
            ro_hien["dong"].append(ly_do)

    def ket_ro(j):
        nonlocal ro_hien
        if ro_hien is not None and not legs:
            ro_hien["ket"] = j
            ro_hien["von_sau"] = B
            kq.ro.append(ro_hien)
            ro_hien = None

    def mo(chieu, lot, p_bid, s, d, sl, tp, j):
        px = p_bid + s if chieu > 0 else p_bid
        px *= (1 + truot) if chieu > 0 else (1 - truot)
        cu = ky_quy(p_bid)
        legs.append({"c": chieu, "lot": lot, "gia": px, "d": d, "sl": sl, "tp": tp, "sw": 0.0})
        if von_rong(p_bid, s) - ky_quy(p_bid) < 0 or ky_quy(p_bid) > 0 and \
                von_rong(p_bid, s) <= tk.stop_out * ky_quy(p_bid):
            legs.pop()
            kq.tu_choi += 1
            return False
        _ = cu
        kq.so_lenh += 1
        kq.lot_max = max(kq.lot_max, lot)
        kq.tang_max = max(kq.tang_max, len(legs))
        return True

    def thuc_hien_doan(p0, p1, s, j):
        """Doan don dieu BID p0 -> p1: xu ly su kien theo thu tu gap."""
        nonlocal B
        lap = 0
        p = p0
        while legs and lap < 200:
            lap += 1
            len_ = p1 > p
            ev = []                                 # (gia_bid_kich_hoat, loai, du_lieu)
            chieu = legs[0]["c"]
            # SL / TP tung lenh (muc tren gia dong: mua BID, ban ASK)
            for L in list(legs):
                for loai, muc in (("sl", L["sl"]), ("tp", L["tp"])):
                    if not muc:
                        continue
                    mb = muc if L["c"] > 0 else muc - s       # quy ve BID
                    cham = (L["c"] > 0 and ((loai == "sl" and not len_ and mb <= p and mb >= p1)
                                            or (loai == "tp" and len_ and p <= mb <= p1))) or \
                           (L["c"] < 0 and ((loai == "sl" and len_ and p <= mb <= p1)
                                            or (loai == "tp" and not len_ and p1 <= mb <= p)))
                    if cham:
                        ev.append((mb, loai, L))
            # luoi: gia lenh xa nhat
            dau = [L for L in legs if L["d"]]
            if ts.grid and dau and len(legs) < ts.grid_max_lvl:
                L0 = dau[0]
                d = L0["d"]
                k = len(legs)
                if chieu > 0 and not len_:
                    gx = min(L["gia"] for L in legs)
                    lvl = L0["gia"] - k * d
                    if abs(gx - d - lvl) > 0.5 * d:
                        lvl = gx - d
                    # |gx - Ask| >= 30 diem: Ask = bid + s <= gx - kc
                    trg = min(lvl, gx - kc - s)
                    if p1 <= trg <= p:
                        ev.append((trg, "luoi", None))
                elif chieu < 0 and len_:
                    gx = max(L["gia"] for L in legs)
                    lvl = L0["gia"] + k * d
                    if abs(gx + d - lvl) > 0.5 * d:
                        lvl = gx + d
                    trg = max(lvl - s, gx + kc)                # Ask >= lvl ; |gx - Bid| >= 30 diem
                    if p <= trg <= p1:
                        ev.append((trg, "luoi", None))
            # trailing (ro 1 lenh co d): kich hoat dong ngay khi khoang keo < 30 diem
            if ts.trail and ts.trail_level and len(legs) == 1 and legs[0]["d"]:
                L = legs[0]
                adj = max(0.0, L["sw"]) / (L["lot"] * hd * fx(p)) if L["lot"] else 0.0
                kc_keo = ts.trail_level * L["d"] - adj
                if kc_keo < kc:
                    if L["c"] > 0 and len_:
                        trg = L["gia"] + ts.trail_level * L["d"]
                        if p <= trg <= p1:
                            ev.append((trg, "keo_dong", L))
                    elif L["c"] < 0 and not len_:
                        trg = L["gia"] - ts.trail_level * L["d"] - s
                        if p1 <= trg <= p:
                            ev.append((trg, "keo_dong", L))
            # stop-out: von_rong(x) = so*ky_quy, tuyen tinh theo x tren doan (fx co dinh)
            kq_ = ky_quy(p)
            if kq_ > 0:
                f0 = von_rong(p, s) - tk.stop_out * kq_
                f1 = von_rong(p1, s) - tk.stop_out * ky_quy(p1)
                if f0 <= 0:
                    ev.append((p, "stop_out", None))
                elif f1 <= 0:
                    x = p + (p1 - p) * f0 / (f0 - f1)
                    ev.append((x, "stop_out", None))
            if not ev:
                break
            ev.sort(key=lambda e: abs(e[0] - p))
            x, loai, L = ev[0]
            p = x
            if loai in ("sl", "tp", "keo_dong"):
                if L in legs:
                    dong(L, x, s, loai)
            elif loai == "luoi":
                L0 = [L_ for L_ in legs if L_["d"]][0]
                lot = _lam_tron(max(L_["lot"] for L_ in legs) * ts.grid_vol_mult, tk)
                loss1 = L0["lot"] * hd * fx(x) * L0["d"]
                chi_phi = sum(L_["sw"] for L_ in legs)
                muc_tieu = loss1 + (chi_phi if chi_phi > 0 else 0.0)
                gia_moi = x + s if chieu > 0 else x
                sv = sum(L_["lot"] for L_ in legs) + lot
                svo = sum(L_["lot"] * L_["gia"] for L_ in legs) + lot * gia_moi
                tv = hd * fx(x)
                tp = (muc_tieu / tv + svo) / sv if chieu > 0 else (svo - muc_tieu / tv) / sv
                if chieu > 0 and tp - x < kc:
                    tp = x + kc
                if chieu < 0 and (x + s) - tp < kc:
                    tp = x + s - kc
                if mo(chieu, lot, x, s, 0.0, 0.0, tp, j):
                    for L_ in legs:
                        L_["tp"] = tp
                        L_["sl"] = L0["sl"]
                else:
                    break                                   # thu lai o doan/bar sau
            elif loai == "stop_out":
                kq.so_stop_out += 1
                while legs and von_rong(x, s) <= tk.stop_out * ky_quy(x):
                    xau = min(legs, key=lambda L_: loi(L_, x, s) - L_["sw"])
                    dong(xau, x, s, "stop_out")
            if not legs:
                ket_ro(j)
                break
        # keo SL cuoi doan di thuan (cuc tri moi)
        if ts.trail and ts.trail_level and len(legs) == 1 and legs[0]["d"]:
            L = legs[0]
            adj_g = max(0.0, L["sw"]) / (L["lot"] * hd * fx(p1))
            if L["c"] > 0 and p1 > L["gia"]:
                sl = max(L["gia"], L["gia"] + adj_g) + (p1 - L["gia"]) - ts.trail_level * L["d"]
                if sl >= L["gia"] and (not L["sl"] or sl > L["sl"]) and p1 - sl >= kc:
                    L["sl"] = sl
            elif L["c"] < 0 and p1 + s < L["gia"]:
                a = p1 + s
                sl = min(L["gia"], L["gia"] - adj_g) - (L["gia"] - a) + ts.trail_level * L["d"]
                if sl <= L["gia"] and (not L["sl"] or sl < L["sl"]) and sl - a >= kc:
                    L["sl"] = sl

    huong, slg, tpg = tin_hieu["huong"], tin_hieu["sl"], tin_hieu["tp"]
    for j in range(n):
        s = sp[j] * o[j]
        if B <= 0 and not legs:
            kq.chay = True
        # 1. tick dau: vao lenh
        if not legs and not kq.chay and huong[j] != 0:
            hb, sl0, tp0 = int(huong[j]), float(slg[j]), float(tpg[j])
            bid, ask = o[j], o[j] + s
            vao = ask if hb > 0 else bid
            d = abs(vao - sl0)
            isl = True if ts.grid else ts.ignore_sl
            itp = ts.ignore_tp
            ch, sl, tp = hb, sl0, tp0
            if ts.reverse:
                ch, sl, tp, isl, itp = -hb, tp0, sl0, itp, isl
            gia = ask if ch > 0 else bid
            hop = True
            if ch > 0:
                hop = not (sl and sl >= bid) and not (tp and tp <= bid)
            else:
                hop = not (sl and sl <= ask) and not (tp and tp >= ask)
            mau = abs(gia - (sl if sl else tp))
            if hop and mau > 0 and d > 0:
                bal = B                          # khong vi the: margin_free = von rong = so du
                lot = _lam_tron(bal * ts.risk / (mau * hd * fx(gia)), tk)
                if mo(ch, lot, bid, s, d, 0.0 if isl else sl, 0.0 if itp else tp, j):
                    ro_hien = {"vao": j, "chieu": ch, "d": d, "von_truoc": B, "dong": []}
        # 2. duong gia trong bar
        diem_duong = duong(o[j], h[j], l[j], c[j], thu_tu)
        thap = von_rong(o[j], s) if legs else B
        for a, b in zip(diem_duong[:-1], diem_duong[1:]):
            if legs and a != b:
                thuc_hien_doan(a, b, s, j)
            if legs:
                thap = min(thap, von_rong(b, s))
        # 3. qua dem cuoi bar
        for L in legs:
            L["sw"] += L["lot"] * hd * c[j] * fx(c[j]) * (pm[j] if L["c"] > 0 else pb[j])
        eq_c[j] = von_rong(c[j], s) if legs else B
        eq_l[j] = min(thap, eq_c[j])
    # con lenh cuoi du lieu: tinh theo gia dong cuoi
    kq.von_cuoi = float(eq_c[-1]) if n else B
    kq.duong_von = pd.Series(eq_c, index=idx)
    kq.von_thap = pd.Series(eq_l, index=idx)
    if legs:
        kq.canh_bao.append(f"{len(legs)} lenh con mo cuoi du lieu (tinh theo von rong)")
    return kq


def chi_so(kq: KetQuaGer, von: float) -> dict:
    e = kq.duong_von
    dd = 0.0
    if len(e):
        dinh = np.maximum.accumulate(np.maximum(e.to_numpy(), von))
        dd = float(np.max((dinh - np.minimum(kq.von_thap.to_numpy(), e.to_numpy())) / dinh))
    ngay = e.resample("1D").last().dropna()
    r = ngay.pct_change().dropna()
    sh = float(r.mean() / r.std() * math.sqrt(252)) if len(r) > 2 and r.std() > 0 else 0.0
    lai_ro = [x["von_sau"] - x["von_truoc"] for x in kq.ro]
    return {"lai_sau_phi_pct": round((kq.von_cuoi / von - 1) * 100, 2),
            "maxdd_pct": round(dd * 100, 2), "sharpe": round(sh, 2), "so_ro": len(kq.ro),
            "so_lenh": kq.so_lenh, "ro_thang_pct": round(100 * np.mean([x > 0 for x in lai_ro]), 1)
            if lai_ro else None, "tang_max": kq.tang_max, "lot_max": round(kq.lot_max, 2),
            "so_stop_out": kq.so_stop_out, "tu_choi_ky_quy": kq.tu_choi,
            "phi_qua_dem_usd": round(kq.phi_qua_dem, 2), "chay": kq.chay or kq.von_cuoi <= 0}


# ----------------------------------------------------------------- .set + input cua EA
_RX_INPUT = re.compile(r"^\s*(?:input|sinput)\s+([\w:]+)\s+(\w+)\s*=\s*([^;]+);", re.M)


def doc_input(vb: str) -> dict:
    """input cua EA -> {ten: gia tri mac dinh (chuoi da cat)}."""
    return {m.group(2): m.group(3).strip() for m in _RX_INPUT.finditer(vb)}


def doc_set(vb_set: str) -> dict:
    ra = {}
    for dong in vb_set.splitlines():
        dong = dong.strip()
        if not dong or dong.startswith(";") or "=" not in dong:
            continue
        k, v = dong.split("=", 1)
        ra[k.strip()] = v.split("||")[0].strip()
    return ra


def gop_tham_so(vb: str, vb_set: str | None) -> tuple[dict, list]:
    """Mac dinh cua EA, de bang `.set` - CHI ten khop CHINH XAC (MT5 phan biet hoa thuong);
    ten trong .set khong co trong EA -> ghi `bo_qua` (vd `SLLookBack` vs `SLLookback`)."""
    th = doc_input(vb)
    bo = []
    for k, v in (doc_set(vb_set) if vb_set else {}).items():
        if k in th:
            th[k] = v
        else:
            bo.append(k)
    return th, bo


def _so(v, mac=0.0):
    v = str(v).strip().strip('"')
    if v.lower() in ("true", "false"):
        return 1.0 if v.lower() == "true" else 0.0
    try:
        return float(v)
    except ValueError:
        return mac


def tham_so_ger(th: dict) -> ThamSoGer:
    """Anh xa input chung cua ho geraked -> GerEA (y het OnInit: risk*0.01, level*0.01)."""
    b = lambda k, m: bool(_so(th.get(k, m)))
    return ThamSoGer(risk=_so(th.get("Risk", 1)) * 0.01, ignore_sl=b("IgnoreSL", "true"),
                     ignore_tp=b("IgnoreTP", "true"), trail=b("Trail", "true"),
                     trail_level=_so(th.get("TrailingStopLevel", 50)) * 0.01,
                     grid=b("Grid", "false"), grid_vol_mult=_so(th.get("GridVolMult", 1)),
                     grid_trail_level=_so(th.get("GridTrailingStopLevel", 0)) * 0.01,
                     grid_max_lvl=int(_so(th.get("GridMaxLvl", 20))),
                     reverse=b("Reverse", "false"),
                     multiple_open_pos=b("MultipleOpenPos", "false"))


#: thanh vien GerEA -> (truong ThamSoGer, gia tri mac dinh cua constructor `GerEA()`)
_THANH_VIEN = {"risk": ("risk", 0.01), "reverse": ("reverse", False),
               "trailingStopLevel": ("trail_level", 0.5), "grid": ("grid", False),
               "gridVolMult": ("grid_vol_mult", 1.0), "gridTrailingStopLevel": ("grid_trail_level", 0.0),
               "gridMaxLvl": ("grid_max_lvl", 20)}


def tham_so_tu_ma(vb: str, th: dict) -> tuple[ThamSoGer, list]:
    """Doc `ea.X = Input [* 0.01];` trong OnInit (thanh vien KHONG gan -> mac dinh constructor,
    vd 3MAF khong gan `gridTrailingStopLevel` -> 0 du input = 40). IgnoreSL/IgnoreTP/Trail la input
    EA dung truc tiep (`BuyOpen(.., IgnoreSL, IgnoreTP)`, `if (Trail) ea.CheckForTrail()`)."""
    cb = []
    m = re.search(r"int\s+OnInit\s*\([^)]*\)\s*\{(.*?)\n\}", vb, re.S)
    than = m.group(1) if m else ""
    gt = {k: v for k, (_, v) in _THANH_VIEN.items()}
    for x in re.finditer(r"(?m)^\s*ea\.(\w+)\s*=\s*(\w+)\s*(\*\s*0\.01)?\s*;", than):
        k, ten, phan = x.group(1), x.group(2), x.group(3)
        if k not in _THANH_VIEN:
            continue
        if ten not in th:
            cb.append(f"ea.{k} = {ten}: khong phai input -> giu mac dinh")
            continue
        v = _so(th[ten])
        gt[k] = v * 0.01 if phan else v
    if re.search(r"RiskMode\s*==\s*RISK_FIXED_VOL", than) and \
            str(th.get("RiskMode", "0")).strip() not in ("0", "RISK_DEFAULT"):
        raise NotImplementedError("RiskMode khac RISK_DEFAULT chua dich")
    b = lambda k, mac: bool(_so(th.get(k, mac)))
    ts = ThamSoGer(risk=float(gt["risk"]), ignore_sl=b("IgnoreSL", "true"),
                   ignore_tp=b("IgnoreTP", "true"),
                   trail=b("Trail", "true") and "CheckForTrail" in vb,
                   trail_level=float(gt["trailingStopLevel"]), grid=bool(gt["grid"]),
                   grid_vol_mult=float(gt["gridVolMult"]),
                   grid_trail_level=float(gt["gridTrailingStopLevel"]),
                   grid_max_lvl=int(gt["gridMaxLvl"]), reverse=bool(gt["reverse"]),
                   multiple_open_pos=b("MultipleOpenPos", "false"))
    return ts, cb
