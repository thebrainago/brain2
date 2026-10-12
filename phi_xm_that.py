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
