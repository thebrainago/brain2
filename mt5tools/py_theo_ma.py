"""Python (ea_logic_v24, du lieu Yahoo) theo tung ma & giai doan de so voi MT5. MO PHONG."""
import sys, json; sys.path[:0] = [".", "ea_demo"]
import numpy as np, pandas as pd, v24, phi_xm_that as PX, ea_logic_v24 as E
MAP = {"EURUSD#": "EURUSD_X", "GBPUSD#": "GBPUSD_X", "USDJPY#": "JPY_X", "USDCHF#": "USDCHF_X", "AUDUSD#": "AUDUSD_X",
       "GOLD.i#": "GC_F", "US500Cash#": "iGSPC", "UK100Cash#": "iFTSE", "GER40Cash#": "iGDAXI", "OILCash#": "CL_F"}
o = {}
for xm, ten in MAP.items():
    d = pd.read_csv(f"/workspace/du_lieu_ngay/v24/{ten}.csv", index_col=0, parse_dates=True)
    d = d[(d["high"] >= d["low"]) & (d["close"] > 0)]; d = d[(d["high"] > d["low"]) | (d["open"] != d["close"])]
    O, H, L, C = (d[k].tolist() for k in ("open", "high", "low", "close"))
    for mo, b in (("cu", v24.bps_of(ten)), ("xm", PX.bps_of_xm(ten))):
        sp = [c * b for c in C]
        for ea in ("RSI", "MRZ"):
            T = E.ea(O, H, L, C, ea, sp)
            for tag, a, z in (("2004", "2004-01-01", "2015-12-31"), ("2016", "2016-01-01", "2026-10-01")):
                r = [s * (x - e) / e * 1e4 for j, s, e, k, x in T if a <= str(d.index[j].date()) <= z]
                o[f"{ea}|{xm}|{tag}|{mo}"] = dict(n=len(r), tb_bps=round(float(np.mean(r)), 2) if r else None, du_lieu_tu=str(d.index[0].date()))
json.dump(o, open("reports/mt5_v24/python_theo_ma.json", "w"), indent=1)
print(len(o))
