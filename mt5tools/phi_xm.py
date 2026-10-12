"""Xuat phi/spread that tu XM MT5 (doc symbol_info + spread lich su tu bar M1/H1). Khong dung mat khau: gan vao terminal dang dang nhap."""
import sys, csv, json, re
import numpy as np, pandas as pd, MetaTrader5 as mt5
from datetime import datetime, timedelta
term = sys.argv[1]; out = sys.argv[2]
assert mt5.initialize(path=term), mt5.last_error()
ai = mt5.account_info()
print("ACCOUNT server=%s currency=%s leverage=%s trade_mode=%s company=%s" % (ai.server, ai.currency, ai.leverage, ai.trade_mode, ai.company))
want = ["EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","USDCAD","NZDUSD","GOLD","XAUUSD","OIL","US500","US100","US30","UK100","GER40","SILVER"]
allsym = mt5.symbols_get()
print("TOTAL", len(allsym))
rows = []
SM = {0:"DISABLED",1:"POINTS",2:"BASE_CCY",3:"MARGIN_CCY",4:"DEPOSIT_CCY",5:"INTEREST_CURRENT",6:"INTEREST_OPEN",7:"REOPEN_CURRENT",8:"REOPEN_BID"}
DAY = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
for s in allsym:
    u = s.name.upper()
    if not any(u.startswith(w) for w in want) or len(u) > len([w for w in want if u.startswith(w)][0]) + 6: continue
    mt5.symbol_select(s.name, True); i = mt5.symbol_info(s.name)
    if i is None: continue
    r = dict(symbol=i.name, path=i.path, trade_mode=i.trade_mode, digits=i.digits, point=i.point, bid=i.bid, ask=i.ask,
             spread_pts_now=i.spread, spread_float=i.spread_float, contract_size=i.trade_contract_size,
             tick_size=i.trade_tick_size, tick_value=i.trade_tick_value, vol_min=i.volume_min, vol_step=i.volume_step, vol_max=i.volume_max,
             swap_long=i.swap_long, swap_short=i.swap_short, swap_mode=SM.get(i.swap_mode, i.swap_mode), swap3=(DAY[i.swap_rollover3days] if 0 <= i.swap_rollover3days < 7 else i.swap_rollover3days),
             margin_initial=i.margin_initial, currency_profit=i.currency_profit, currency_margin=i.currency_margin)
    try: r["margin_1lot_buy"] = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, i.name, 1.0, i.ask)
    except Exception: r["margin_1lot_buy"] = None
    mid = (i.bid + i.ask) / 2 if i.bid else None
    r["spread_bps_now"] = round((i.ask - i.bid) / mid * 1e4, 3) if mid else None
    for tf, nm, n in ((mt5.TIMEFRAME_M1, "M1", 20000), (mt5.TIMEFRAME_H1, "H1", 30000), (mt5.TIMEFRAME_D1, "D1", 9000)):
        b = mt5.copy_rates_from_pos(i.name, tf, 0, n)
        if b is None or len(b) == 0: continue
        d = pd.DataFrame(b); d["t"] = pd.to_datetime(d["time"], unit="s")
        r["%s_from" % nm] = str(d.t.iloc[0].date()); r["%s_n" % nm] = len(d)
        if nm in ("M1", "H1"):
            sb = d["spread"] * i.point / d["close"] * 1e4; sb = sb[d["spread"] > 0]
            if len(sb):
                r["%s_spread_bps_med" % nm] = round(float(sb.median()), 3); r["%s_spread_bps_p90" % nm] = round(float(sb.quantile(.9)), 3)
                r["%s_spread_pts_med" % nm] = float(d["spread"][d["spread"] > 0].median())
            if nm == "H1":
                g = d[d["spread"] > 0].groupby(d.t.dt.hour)["spread"]
                r["H1_spread_pts_med_by_hour"] = json.dumps({int(h): float(v) for h, v in g.median().items()})
                r["H1_spread_pts_p90_by_hour"] = json.dumps({int(h): float(v) for h, v in g.quantile(.9).items()})
                # gio mo nen D1 (server 00:00) -> spread luc vao lenh EA
                h0 = d[(d.t.dt.hour == 0) & (d["spread"] > 0)]
                if len(h0): r["H1_h00_spread_bps_med"] = round(float((h0["spread"] * i.point / h0["close"] * 1e4).median()), 3)
    t = mt5.copy_ticks_from(i.name, datetime.now() - timedelta(days=3), 200000, mt5.COPY_TICKS_INFO)
    if t is not None and len(t):
        tt = pd.DataFrame(t); tt = tt[(tt.ask > 0) & (tt.bid > 0)]
        sb = (tt.ask - tt.bid) / ((tt.ask + tt.bid) / 2) * 1e4
        r["tick_n_3d"] = len(tt); r["tick_spread_bps_med"] = round(float(sb.median()), 3); r["tick_spread_bps_p90"] = round(float(sb.quantile(.9)), 3)
    rows.append(r); print("ok", i.name, flush=True)
keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 999)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
for r in rows: print(r["symbol"], r["trade_mode"], r["spread_bps_now"], r.get("H1_spread_bps_med"), r["contract_size"], r["swap_long"], r["swap_short"], r["swap_mode"], r.get("M1_from"), r.get("D1_from"))
mt5.shutdown()
