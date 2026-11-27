# -*- coding: utf-8 -*-
"""Chay lai cac test tick con thieu tren p4, mot test mot luc."""
import os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(r"C:\Users\DUNG\AppData\Local\Temp")))
# load functions from chay_tester_p4 in Temp
import importlib.util
p = Path(r"C:\Users\DUNG\AppData\Local\Temp\chay_tester_p4.py")
spec = importlib.util.spec_from_file_location("chay_tester_p4", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

hang = []
hang.append(("vang_luoi_khoi_dong", "VANG_LuoiEMA.ex5", {
    "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
    "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.08,
    "InpMagic": 2026112702, "InpSlippage": 50,
}, "2025.10.01", "2026.10.12"))

hang.append(("vang_dc_tick_202508_202610", "VANG_DonchianEMA.ex5", {
    "InpDonchian": 20, "InpEMA": 55, "InpATR": 14, "InpSL_ATR": 2.0, "InpTP_ATR": 4.0,
    "InpRuiRo": 0.02, "InpVonTham": 0, "InpMagic": 2026112701, "InpSlippage": 50,
}, "2025.08.01", "2026.10.12"))

hang.append(("vang_luoi_tick_202508_202610", "VANG_LuoiEMA.ex5", {
    "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
    "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.08,
    "InpMagic": 2026112702, "InpSlippage": 50,
}, "2025.08.01", "2026.10.12"))

if m.ram_trong_gb() < 11:
    m.log("DUNG: RAM thap"); sys.exit(2)

kq = []
for item in hang:
    r = m.chay_mot(*item)
    if r.get("loi") == "bao_cao_rong":
        m.log("thu lai 1 lan sau 30s: %s" % item[0])
        time.sleep(30)
        r = m.chay_mot(*item)
    kq.append(r)
    import json
    (m.OUT / "tong_hop_lai.json").write_text(json.dumps(kq, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    time.sleep(20)
    m.log("RAM sau test %.2f GB" % m.ram_trong_gb())
m.log("HOAN TAT LAI %d test" % len(kq))
sys.exit(0)
