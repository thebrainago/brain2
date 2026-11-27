# Keo du lieu ESZ6 (E-mini S&P) tu Fxaurum gateway tren MAY NHA: ws://127.0.0.1:9001/
# CHI goi RPC doc (klines 1m, bigTrades, flowRecs). KHONG goi syncTicks/syncHistory.
# Chay tren may nha:  python keo_esz6.py <thu_muc_ra>
import asyncio, json, os, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import websockets
URL = "ws://127.0.0.1:9001/"; NY = ZoneInfo("America/New_York")
OUT = sys.argv[1] if len(sys.argv) > 1 else "esz6"
os.makedirs(OUT, exist_ok=True)
async def rpc(ws, method, params, rid, timeout=120):
    await ws.send(json.dumps({"method": method, "params": params, "id": rid}))
    end = asyncio.get_event_loop().time() + timeout
    while True:
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(1, end - asyncio.get_event_loop().time())))
        if msg.get("id") == rid: return msg
async def main():
    async with websockets.connect(URL, max_size=2**28) as ws:
        d = datetime(2026, 8, 20); rid = 100
        while d <= datetime(2026, 11, 27):
            if d.weekday() < 5:
                t0 = int(datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).timestamp()*1000)
                t1 = int(datetime(d.year, d.month, d.day, 16, 0, tzinfo=NY).timestamp()*1000)
                ten = d.strftime("%Y%m%d"); kq = {}
                for ten_rpc, p in [("klines", {"interval": "1m", "limit": 1000}), ("bigTrades", {"min": 50, "merge": 0}), ("flowRecs", {})]:
                    rid += 1
                    try:
                        m = await rpc(ws, ten_rpc, {"exchange": "CME", "symbol": "ESZ6", "startTime": t0, "endTime": t1, **p}, rid)
                        kq[ten_rpc] = m.get("result"); kq[ten_rpc + "_status"] = m.get("status")
                    except Exception as e:
                        kq[ten_rpc + "_loi"] = repr(e)
                json.dump(kq, open(os.path.join(OUT, f"{ten}.json"), "w"))
                print(ten, {k: (len(v) if isinstance(v, list) else (list(v.keys()) if isinstance(v, dict) else v)) for k, v in kq.items()}, flush=True)
            d += timedelta(days=1)
asyncio.run(main())
