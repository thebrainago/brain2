# Xuat spread theo gio (tick XM that) + gia D1/H1 XM. Chi DOC du lieu, khong dat lenh. Terminal portable D:\mt5_tester\p1.
import MetaTrader5 as mt5, pandas as pd, numpy as np, os, datetime as dt, sys
OUT = r"C:\Users\DUNG\brain2\reports\mt5_v27"; os.makedirs(OUT + r"\spread_gio", exist_ok=True); os.makedirs(OUT + r"\gia_xm", exist_ok=True)
assert mt5.initialize(path=r"D:\mt5_tester\p1\terminal64.exe", portable=True), mt5.last_error()
ai = mt5.account_info(); print("demo" if ai and ai.trade_mode == 0 else "KHONG PHAI DEMO", flush=True)
FX = ["EURUSD#","GBPUSD#","USDJPY#","USDCHF#","AUDUSD#","NZDUSD#","USDCAD#","EURGBP#","EURJPY#","GBPJPY#","AUDCAD#","EURCAD#","GOLD.i#","US500Cash#","GER40Cash#"]
tom = []
for s in FX:
    if not mt5.symbol_select(s, True): print(s, "khong co"); continue
    pt = mt5.symbol_info(s).point; parts = []
    for m in range(6):   # 6 thang gan nhat, tung thang (do RAM)
        a = dt.datetime(2026, 4 + m, 1); b = dt.datetime(2026 + (4 + m) // 12, (4 + m) % 12 + 1, 1)
        t = mt5.copy_ticks_range(s, a, b, mt5.COPY_TICKS_INFO)
        if t is None or len(t) == 0: continue
        d = pd.DataFrame(t); d = d[(d.bid > 0) & (d.ask > 0)]
        d["gio"] = pd.to_datetime(d.time, unit="s").dt.hour; d["sp"] = (d.ask - d.bid) / pt
        parts.append(d.groupby("gio").sp.describe(percentiles=[.5, .9])[["count", "50%", "90%"]])
    if not parts: print(s, "0 tick"); continue
    g = pd.concat(parts).groupby(level=0).agg({"count": "sum", "50%": "median", "90%": "median"})
    g.columns = ["so_tick", "trung_vi_point", "p90_point"]; g.to_csv(OUT + rf"\spread_gio\{s.replace('#','').replace('.','_')}.csv")
    tom.append((s, int(g.so_tick.sum()), float(g.trung_vi_point.loc[0]) if 0 in g.index else None, float(g.trung_vi_point.median())))
    print(s, tom[-1], flush=True)
pd.DataFrame(tom, columns=["ma", "so_tick", "tv_00h_point", "tv_ca_ngay_point"]).to_csv(OUT + r"\spread_gio\_tom_tat.csv", index=False)
for s in ["US500Cash#", "GER40Cash#", "GOLD.i#"]:
    for tf, ten in ((mt5.TIMEFRAME_D1, "D1"), (mt5.TIMEFRAME_H1, "H1")):
        r = mt5.copy_rates_range(s, tf, dt.datetime(2010, 1, 1), dt.datetime(2026, 10, 13))
        if r is None: print(s, ten, "None", mt5.last_error()); continue
        d = pd.DataFrame(r); d["time"] = pd.to_datetime(d.time, unit="s"); d.to_csv(OUT + rf"\gia_xm\{s.replace('#','').replace('.','_')}_{ten}.csv", index=False)
        print(s, ten, len(d), d.time.iloc[0], d.time.iloc[-1], flush=True)
mt5.shutdown(); print("XONG")
