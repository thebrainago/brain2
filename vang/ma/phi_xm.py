# -*- coding: utf-8 -*-
"""Chi phí XM GOLD CFD (tài khoản micro quy về GOLD.i#)."""
from __future__ import annotations
import json
from pathlib import Path

_CFG = Path(__file__).resolve().parents[1] / "cau_hinh" / "phi_xm_vang.json"


def tai_cau_hinh():
    with _CFG.open(encoding="utf-8") as f:
        return json.load(f)


CFG = tai_cau_hinh()
POINT = float(CFG["point"])
HOP_DONG = float(CFG["contract_size"])  # ounce / lot
LOT_MIN = float(CFG["vol_min"])
LOT_BUOC = float(CFG["vol_step"])
LOT_MAX = float(CFG["vol_max"])
SPREAD_H1_PTS = float(CFG["spread_h1_med_pts"])
SPREAD_M1_PTS = float(CFG["spread_m1_med_pts"])
TRUOT_NHAN = float(CFG["truot_gia_nhan_spread"])
HOA_HONG = float(CFG["hoa_hong"])
SWAP_LONG = float(CFG["swap_long_1_lot_1_dem"])
SWAP_SHORT = float(CFG["swap_short_1_lot_1_dem"])


def chuan_lot(lot: float) -> float:
    if lot <= 0:
        return 0.0
    n = round(lot / LOT_BUOC)
    v = n * LOT_BUOC
    if v < LOT_MIN:
        v = LOT_MIN
    if v > LOT_MAX:
        v = LOT_MAX
    return float(v)


def spread_gia(spread_pts, khung="H1") -> float:
    """Đổi điểm spread sang USD/ounce. Cột spread = 0 (trước 2018-10) thì dùng trung vị đã đo."""
    pts = float(spread_pts) if spread_pts and spread_pts > 0 else (
        SPREAD_M1_PTS if khung.upper() in {"M1", "M5"} else SPREAD_H1_PTS
    )
    return pts * POINT


def chi_phi_mot_chieu(spread_pts, khung="H1") -> float:
    """USD/ounce mỗi chiều: nửa spread + trượt (0,5 × spread)."""
    sg = spread_gia(spread_pts, khung)
    return 0.5 * sg + TRUOT_NHAN * sg


def pnl_usd(lot, huong, gia_vao, gia_ra) -> float:
    return float(lot) * HOP_DONG * huong * (gia_ra - gia_vao)


def swap_dem_usd(lot, huong, tinh_swap: bool) -> float:
    if not tinh_swap or lot <= 0:
        return 0.0
    muc = SWAP_LONG if huong > 0 else SWAP_SHORT
    return float(lot) * muc
