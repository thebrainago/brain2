# -*- coding: utf-8 -*-
"""Strategy Tester p4: VANG_TayV2, tick that, mot test mot luc.
Khong dung p3/p5/p6. Khong giet claude.exe hay terminal XM chinh. Chi taskkill theo PID do script phong.
Khong dat lenh that.
"""
from __future__ import annotations
import json, sys, time, shutil
from pathlib import Path
import importlib.util

# uu tien ban trong repo neu chay tu may nha; fallback Temp
_cands = [
    Path(__file__).resolve().parent / "chay_tester_p4.py",
    Path(r"C:\Users\DUNG\AppData\Local\Temp\chay_tester_p4.py"),
    Path(r"E:\brain2_tmp\vang\chay_tester_p4.py"),
]
modpath = next((p for p in _cands if p.exists()), None)
if modpath is None:
    raise SystemExit("khong tim thay chay_tester_p4.py")
spec = importlib.util.spec_from_file_location("chay_tester_p4", modpath)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT = m.OUT
TU, DEN = "2025.09.01", "2026.11.27"
P = {
    "InpL0": 0.01, "InpK": 4, "InpMaxL": 8, "InpMaxH": 10,
    "InpTP": 4.00, "InpGap": 5.47, "InpHGap": 21.37, "InpHFrac": 1.0,
    "InpFlCap": 0.15, "InpLossClose": 0.30,
    "InpADXLen": 14, "InpADXTh": 30.0, "InpEMA200": 200, "InpSlopeBars": 10,
    "InpCooldown": 240, "InpMaxLc": 2, "InpShortCap": 0.04, "InpFlatOrphan": 1,
    "InpLcPeriod": 6900, "InpLcPause": 6900,
    "InpDayLoss": 0.15, "InpWeekLoss": 0.20, "InpEqLot": 1, "InpDcaMode": 2,
    "InpD1OneWay": 0.60, "InpBBLen": 20,
    "InpMagic": 2026112793, "InpSlippage": 50, "InpMaxSpreadPts": 500,
}

def cho_ram(toi_thieu=11.0, giay=300):
    t0 = time.time()
    while time.time() - t0 < giay:
        ram = m.ram_trong_gb()
        if ram >= toi_thieu:
            return ram
        m.log("cho RAM (%.2f < %.1f)" % (ram, toi_thieu))
        time.sleep(15)
    return m.ram_trong_gb()

def bien_dich_tay():
    dest = m.SLOT / "MQL5" / "Experts" / "VANG"
    dest.mkdir(parents=True, exist_ok=True)
    mq = dest / "VANG_TayV2.mq5"
    if not mq.exists():
        return "khong co " + str(mq)
    return m.bien_dich(mq)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ram = cho_ram()
    if ram < 11:
        m.log("DUNG: RAM trong %.2f" % ram)
        return 2
    m.log(m.dat_maxbars(m.SLOT, 1000000))
    loi = bien_dich_tay()
    if loi:
        m.log(loi)
        return 3
    m.log("bien dich ok VANG_TayV2.ex5")
    ten = "vang_tayv2_guard_th9_th11"
    r = m.chay_mot(ten, "VANG_TayV2.ex5", P, TU, DEN, 10000, khung="M1")
    if r.get("loi") == "bao_cao_rong":
        m.log("thu lai 1 lan sau 30s: %s" % ten)
        time.sleep(30)
        r = m.chay_mot(ten, "VANG_TayV2.ex5", P, TU, DEN, 10000, khung="M1")
    (OUT / "tong_hop_tayv2.json").write_text(
        json.dumps([r], ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    m.log("HOAN TAT TAYV2_GUARD %s" % r)
    return 0 if not r.get("loi") else 4

if __name__ == "__main__":
    sys.exit(main() or 0)
