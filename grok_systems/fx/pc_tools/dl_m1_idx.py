# Export XM Ultra Low Cash index M1 BID+spread from tester p6 to C: staging as npz.
# Run ONLY when p6 tester is idle (no terminal64 under E:\mt5_tester\p6).
# Never initialize the main XM terminal. Never print secrets.
import datetime as dt, json, os, sys, time
import numpy as np

P6 = r"E:\mt5_tester\p6\terminal64.exe"
OUTC = r"C:\Users\DUNG\v3work\out\m1_idx"
LOG = r"C:\Users\DUNG\v3work\out\mt5\dl_m1_idx.log"
START = dt.datetime(2025, 6, 2)
END = dt.datetime(2026, 11, 27, 23, 59)

SYMS = [
    "UK100Cash#", "AUS200Cash#", "EU50Cash#", "FRA40Cash#", "HK50Cash#",
    "SpainCash#", "CHN50Cash#", "IT40Cash#", "NETH25Cash#", "SWI20Cash#",
    "CA60Cash#", "US2000Cash#", "TaiwanCash#", "GerMid50Cash#", "ChinaHCash#",
    "US400Cash#", "USFANGCash#",
]

def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + msg
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)

def main():
    import MetaTrader5 as mt5
    os.makedirs(OUTC, exist_ok=True)
    log("init p6 portable")
    if not mt5.initialize(P6, portable=True):
        log("FAIL initialize %s" % (mt5.last_error(),))
        return 2
    try:
        acc = mt5.account_info()
        log("account login=%s server=%s" % (getattr(acc, "login", None), getattr(acc, "server", None)))
        info = {}
        for sym in SYMS:
            si = mt5.symbol_info(sym)
            if si is None:
                # try select
                mt5.symbol_select(sym, True)
                time.sleep(0.2)
                si = mt5.symbol_info(sym)
            if si is None:
                log("KHONG CO symbol %s" % sym)
                info[sym] = {"ok": False, "reason": "KHONG CO symbol"}
                continue
            rates = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M1, START, END)
            if rates is None or len(rates) == 0:
                log("KHONG CO rates %s err=%s" % (sym, mt5.last_error()))
                info[sym] = {"ok": False, "reason": "KHONG CO rates", "err": str(mt5.last_error())}
                continue
            point = float(si.point)
            digits = int(si.digits)
            # integer prices like existing npz
            t = rates["time"].astype(np.uint32)
            def to_i(x):
                return np.rint(x / point).astype(np.int32)
            o, h, l, c = to_i(rates["open"]), to_i(rates["high"]), to_i(rates["low"]), to_i(rates["close"])
            sp = rates["spread"].astype(np.int32)
            tv = rates["tick_volume"].astype(np.int32)
            fn = sym.replace("#","").replace(".","_") + "_h.npz"
            # keep Gold-style: SILVER_i_h, GER40Cash_h
            path = os.path.join(OUTC, fn)
            np.savez_compressed(path, t=t, o=o, h=h, l=l, c=c, sp=sp, tv=tv,
                                point=np.array([point], dtype=np.float64),
                                digits=np.array([digits], dtype=np.int64))
            rec = {
                "ok": True, "n": int(len(t)), "file": path, "point": point, "digits": digits,
                "first": str(dt.datetime.utcfromtimestamp(int(t[0]))),
                "last": str(dt.datetime.utcfromtimestamp(int(t[-1]))),
                "last_px": float(c[-1])*point,
                "vmin": float(si.volume_min), "tick_value": float(si.trade_tick_value),
                "tick_size": float(si.trade_tick_size), "profit": si.currency_profit,
                "contract": float(si.trade_contract_size),
            }
            info[sym] = rec
            log("OK %s n=%d %s..%s last=%.2f vmin=%s tv=%s %s" % (
                sym, rec["n"], rec["first"], rec["last"], rec["last_px"], rec["vmin"], rec["tick_value"], rec["profit"]))
        with open(os.path.join(OUTC, "dl_m1_idx.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
        log("done")
        return 0
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    sys.exit(main())
