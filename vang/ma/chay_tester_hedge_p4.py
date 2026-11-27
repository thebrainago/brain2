# -*- coding: utf-8 -*-
"""Tester p4: hedge H1/M15, luoi+go, bien thien luoi. Mot test mot luc.
Cua so 2025.09.01-2026.10.12 va 2025.10.01-2026.10.12. Khong dung 2025.08.01.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import importlib.util

p = Path(r"C:\Users\DUNG\AppData\Local\Temp\chay_tester_p4.py")
spec = importlib.util.spec_from_file_location("chay_tester_p4", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT = m.OUT
TU9, TU10, DEN = "2025.09.01", "2025.10.01", "2026.10.12"

P_HEDGE_H1 = {
    "InpEMA": 55, "InpATR": 14, "InpHedgeATR": 2.0, "InpTP_ATR": 1.2,
    "InpSL_ATR": 4.0, "InpHeSoHedge": 1.5, "InpLotGoc": 0.08,
    "InpMagic": 2026112703, "InpSlippage": 50,
}
P_HEDGE_M15 = dict(P_HEDGE_H1, InpLotGoc=0.16, InpMagic=2026112704)
P_PHUC = {
    "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
    "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.02,
    "InpHeSoLot": 1.0, "InpHeSoPhuc": 1.3, "InpMaxBac": 2,
    "InpMagic": 2026112705, "InpSlippage": 50,
}
P_LUOI_X15 = {
    "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
    "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.03,
    "InpHeSoLot": 1.5, "InpHeSoPhuc": 1.0, "InpMaxBac": 0,
    "InpMagic": 2026112706, "InpSlippage": 50,
}

def hang_doi():
    h = []
    # --- cua so chinh 2025.09.01 ---
    h.append(dict(ten="vang_hedge_h1_th9", ea="VANG_HedgeEMA.ex5", p=P_HEDGE_H1, tu=TU9, den=DEN, khung="H1"))
    h.append(dict(ten="vang_hedge_m15_th9", ea="VANG_HedgeEMA.ex5", p=P_HEDGE_M15, tu=TU9, den=DEN, khung="M15"))
    h.append(dict(ten="vang_phuc_h1_th9", ea="VANG_LuoiPhuc.ex5", p=P_PHUC, tu=TU9, den=DEN, khung="H1"))
    h.append(dict(ten="vang_luoi_x15_h1_th9", ea="VANG_LuoiPhuc.ex5", p=P_LUOI_X15, tu=TU9, den=DEN, khung="H1"))
    # bien thien luoi goc (EA da xac nhan), cung cua so th9
    base = {"InpEMA": 55, "InpATR": 14, "InpTP_ATR": 1.2, "InpSL_ATR": 5.0,
            "InpMagic": 2026112702, "InpSlippage": 50}
    for ten, extra in (
        ("vang_luoi_b10_c4_l008_th9", {"InpBuocATR": 1.0, "InpMaxChan": 4, "InpLotChan": 0.08}),
        ("vang_luoi_b20_c4_l008_th9", {"InpBuocATR": 2.0, "InpMaxChan": 4, "InpLotChan": 0.08}),
        ("vang_luoi_b15_c6_l008_th9", {"InpBuocATR": 1.5, "InpMaxChan": 6, "InpLotChan": 0.08}),
        ("vang_luoi_b15_c4_l004_th9", {"InpBuocATR": 1.5, "InpMaxChan": 4, "InpLotChan": 0.04}),
        ("vang_luoi_b15_c4_l012_th9", {"InpBuocATR": 1.5, "InpMaxChan": 4, "InpLotChan": 0.12}),
    ):
        pp = dict(base, **extra)
        h.append(dict(ten=ten, ea="VANG_LuoiEMA.ex5", p=pp, tu=TU9, den=DEN, khung="H1"))
    # --- cua so ben 2025.10.01 ---
    h.append(dict(ten="vang_hedge_h1_th10", ea="VANG_HedgeEMA.ex5", p=P_HEDGE_H1, tu=TU10, den=DEN, khung="H1"))
    h.append(dict(ten="vang_hedge_m15_th10", ea="VANG_HedgeEMA.ex5", p=P_HEDGE_M15, tu=TU10, den=DEN, khung="M15"))
    h.append(dict(ten="vang_phuc_h1_th10", ea="VANG_LuoiPhuc.ex5", p=P_PHUC, tu=TU10, den=DEN, khung="H1"))
    h.append(dict(ten="vang_luoi_x15_h1_th10", ea="VANG_LuoiPhuc.ex5", p=P_LUOI_X15, tu=TU10, den=DEN, khung="H1"))
    return h

def cho_ram(toi_thieu=11.0, giay=300):
    t0 = time.time()
    while time.time() - t0 < giay:
        ram = m.ram_trong_gb()
        if ram >= toi_thieu:
            return ram
        m.log("cho RAM (%.2f < %.1f)" % (ram, toi_thieu))
        time.sleep(15)
    return m.ram_trong_gb()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ram = cho_ram()
    if ram < 11:
        m.log("DUNG: RAM trong %.2f" % ram); return 2
    m.log(m.dat_maxbars(m.SLOT, 100000))
    hang = hang_doi()
    kq = []
    for item in hang:
        ram = cho_ram()
        if ram < 11:
            kq.append({"ten": item["ten"], "loi": "RAM %.2f" % ram})
            (OUT / "tong_hop_hedge.json").write_text(json.dumps(kq, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            break
        r = m.chay_mot(item["ten"], item["ea"], item["p"], item["tu"], item["den"], 10000, khung=item["khung"])
        if r.get("loi") == "bao_cao_rong":
            m.log("thu lai 1 lan sau 30s: %s" % item["ten"])
            time.sleep(30)
            r = m.chay_mot(item["ten"], item["ea"], item["p"], item["tu"], item["den"], 10000, khung=item["khung"])
        kq.append(r)
        (OUT / "tong_hop_hedge.json").write_text(json.dumps(kq, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        time.sleep(20)
        m.log("RAM sau test %.2f GB" % m.ram_trong_gb())
    m.log("HOAN TAT HEDGE %d test" % len(kq))
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
