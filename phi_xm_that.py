# -*- coding: utf-8 -*-
"""Mo hinh phi theo tai khoan XM THAT dang dang nhap (XMGlobal-MT5 10, nhom 'Standard/Cash Ultra Low', hau to '#').
Nguon: reports/phi_xm_micro_that.csv (doc symbol_info + spread bar H1 ~5 nam, 13/10/2026).
Khong thay doi ket qua vong 24 cu (v24.bps_of giu nguyen de tai lap); dung bps_of_xm cho cac vong sau / so sanh.
Spread = trung vi H1 (bps); spread_h00 = trung vi luc mo nen D1 (00h server) - EA D1 vao lenh dung luc nay nen dat hon.
Swap: nhom '#' tren tk nay co swap_mode=DISABLED (khong tinh swap) -> QD_XM = 0; Python cu tru 2,5%/nam (QD)."""
BANG = {  # ten Python: (ma XM, spread_med_bps, spread_h00_bps)
    "EURUSD_X": ("EURUSD#", 0.72, 1.46), "GBPUSD_X": ("GBPUSD#", 0.60, 2.20), "JPY_X": ("USDJPY#", 0.52, 1.50),
    "USDCHF_X": ("USDCHF#", 1.33, 4.56), "AUDUSD_X": ("AUDUSD#", 1.83, 3.38), "NZDUSD_X": ("NZDUSD#", 3.10, 5.34),
    "USDCAD_X": ("USDCAD#", 1.16, 2.33), "GC_F": ("GOLD.i#", 0.65, 0.63), "SI_F": ("SILVER.i#", 8.19, 8.72),
    "CL_F": ("OILCash#", 3.99, 3.71), "iGSPC": ("US500Cash#", 1.00, 1.02), "iNDX": ("US100Cash#", 0.97, 1.39),
    "iDJI": ("US30Cash#", 0.97, 1.14), "iGDAXI": ("GER40Cash#", 0.95, 3.69), "iFTSE": ("UK100Cash#", 2.10, 7.41),
}
QD_XM = 0.0


def bps_of_xm(ten, luc_mo_nen=True):
    if ten in BANG: return BANG[ten][2 if luc_mo_nen else 1] * 1e-4
    import v24
    return v24.bps_of(ten)


# --- Bo sung 14/10/2026: kich ban swap day du + spread theo gio + truot gia (so_sanh_san.py) ---
TRUOT_X_SPREAD = 0.5  # truot gia = 0,5 x spread moi chieu (gia dinh than trong, CHUA DO tren demo)
CSV_XM = "reports/phi_xm_micro_that.csv"
_SPEC = None


def spec_xm():
    """Doc symbol_info that tu CSV: {ma: dict(point, contract, swap_long, swap_short, swap_mode, swap3, gio_med, gio_p90, gia)}."""
    global _SPEC
    if _SPEC is None:
        import csv, json, os
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_XM); _SPEC = {}
        for r in csv.DictReader(open(p, encoding="utf-8")):
            _SPEC[r["symbol"]] = {"point": float(r["point"]), "contract": float(r["contract_size"]), "swap_long": float(r["swap_long"]),
                                  "swap_short": float(r["swap_short"]), "swap_mode": r["swap_mode"], "swap3": r["swap3"],
                                  "gia": (float(r["bid"]) + float(r["ask"])) / 2,
                                  "gio_med": {int(k): v for k, v in json.loads(r["H1_spread_pts_med_by_hour"]).items()},
                                  "gio_p90": {int(k): v for k, v in json.loads(r["H1_spread_pts_p90_by_hour"]).items()}}
    return _SPEC


def spread_gio_bps_xm(ma, gio_server, p90=False):
    """Spread (bps) theo gio server tu bang H1 by-hour (gia quy doi bang gia luc do 13/10/2026)."""
    s = spec_xm().get(ma)
    if s is None: return None
    return s["gio_p90" if p90 else "gio_med"][gio_server] * s["point"] / s["gia"] * 1e4


def swap_dem_ty_le(ma, huong, gia, kich_ban):
    """Swap mot dem (ty le tren danh nghia, am = mat tien). kich_ban 'nhu_tester': theo swap_mode (DISABLED -> 0);
    'day_du': FX/vang dung muc swap_long/short trong CSV du DISABLED."""
    s = spec_xm()[ma]; v = s["swap_long"] if huong > 0 else s["swap_short"]
    if s["swap_mode"] == "DISABLED" and kich_ban == "nhu_tester": return 0.0
    if s["swap_mode"] == "MARGIN_CCY": return v / (s["contract"] * s["gia"])  # tien/lot/dem theo gia hien tai -> ty le
    return v * s["point"] / gia  # POINTS (va DISABLED o kich ban day du)


# --- Bo sung 14/10/2026 (2): XM STANDARD (ma khong hau to, tai khoan co bonus) = MAC DINH tu nay ---
TAI_KHOAN_MAC_DINH = "Standard"   # "Standard" (khong hau to) | "UltraLow" (hau to #)
HOA_HONG_STANDARD = 0.0
_FX_DO = ("EURUSD", "GBPUSD", "USDCAD", "USDCHF", "USDJPY", "AUDUSD", "NZDUSD")


def ti_le_std_ul(gio):
    """Trung vi (qua 7 cap FX da do ca 2 nhom) cua spread Standard/UltraLow tai gio server - dung de UOC ma thieu."""
    import statistics
    s = spec_xm(); return statistics.median(s[m]["gio_med"][gio] / s[m + "#"]["gio_med"][gio] for m in _FX_DO)


def ho_so_xm(ma_ul, tk=None):
    """Tra ve (ma_dung, la_uoc). ma_ul la ma Ultra Low co '#'. Standard: bo '#'; neu CSV khong co -> uoc tu ma '#'."""
    tk = tk or TAI_KHOAN_MAC_DINH
    if tk == "UltraLow": return ma_ul, False
    m = ma_ul.rstrip("#"); return (m, False) if m in spec_xm() else (ma_ul, True)


def spread_gio_bps_tk(ma_ul, gio, tk=None, p90=False):
    m, uoc = ho_so_xm(ma_ul, tk); v = spread_gio_bps_xm(m, gio, p90)
    return (v * ti_le_std_ul(gio) if uoc else v), uoc


def swap_dem_tk(ma_ul, huong, gia, kich_ban, tk=None):
    """Standard: FX swap_mode POINTS (tinh that) nen ca 2 kich ban deu tru swap; ma uoc dung muc swap cua ma '#' (kich ban day du)."""
    m, uoc = ho_so_xm(ma_ul, tk)
    if (tk or TAI_KHOAN_MAC_DINH) == "Standard": return swap_dem_ty_le(m, huong, gia, "day_du")
    return swap_dem_ty_le(m, huong, gia, kich_ban)
