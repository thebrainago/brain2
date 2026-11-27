# -*- coding: utf-8 -*-
"""Xuat tick GCZ6 qua RPC aggTrades (doc kho local / replay). KHONG goi syncTicks/syncHistory."""
from __future__ import annotations
import argparse, asyncio, csv, json, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL = "ws://127.0.0.1:9001/"
OUT_MAC_DINH = r"E:\brain2_tmp\vang\fxaurum"


def ms(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def from_ms(x):
    return datetime.fromtimestamp(x / 1000, tz=timezone.utc)


async def rpc(ws, method, params, req_id, timeout=120):
    await ws.send(json.dumps({"method": method, "params": params, "id": req_id}))
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            raise TimeoutError(method)
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=remaining))
        if "stream" in msg:
            continue
        if msg.get("id") == req_id:
            return msg


async def keo(out_dir: str, start: str, end: str, buoc_gio=4):
    import websockets
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    t1 = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    path = out / "gcz6_ticks.csv"
    meta = {
        "gateway": URL, "method": "aggTrades",
        "bat_dau_utc": t0.isoformat(), "ket_thuc_utc": t1.isoformat(),
        "keo_luc_utc": datetime.now(timezone.utc).isoformat(),
        "loi": [], "dem": 0, "khong_goi": ["syncTicks", "syncHistory"],
    }
    req = 1
    # resume if file exists with last time
    dem = 0
    append = False
    cur = t0
    if path.exists() and path.stat().st_size > 100:
        # read last open_ms
        last = None
        with path.open("rb") as f:
            f.seek(0, 2)
            n = min(4096, f.tell())
            f.seek(-n, 2)
            tail = f.read().decode("utf-8", errors="ignore").splitlines()
            for line in reversed(tail):
                if line and not line.startswith("time_ms"):
                    try:
                        last = int(line.split(",")[0])
                        break
                    except Exception:
                        pass
        if last:
            cur = from_ms(last) + timedelta(milliseconds=1)
            append = True
            print("resume from", cur, flush=True)

    async with websockets.connect(URL, max_size=128 * 1024 * 1024, open_timeout=10, ping_interval=20) as ws:
        ping = await rpc(ws, "ping", {}, req, 10); req += 1
        st = await rpc(ws, "syncStatus", {}, req, 10); req += 1
        meta["ping"] = ping
        meta["syncStatus"] = st
        if st.get("result", {}).get("running"):
            meta["loi"].append("syncStatus dang chay — khong goi sync; chi doc kho co san")
        info = await rpc(ws, "tickInfo", {"exchange": "COMEX", "symbols": ["GCZ6"]}, req, 20); req += 1
        meta["tickInfo_GCZ6"] = info
        print("tickInfo", json.dumps(info.get("result"), ensure_ascii=False)[:500], flush=True)

        moi = not append
        f = path.open("a" if append else "w", newline="", encoding="utf-8")
        w = csv.writer(f)
        if moi:
            w.writerow(["time_ms", "time_utc", "time_vn_utc7", "price", "qty", "side", "ord_id", "tu"])
        t_bat = time.time()
        try:
            while cur < t1:
                nxt = min(cur + timedelta(hours=buoc_gio), t1)
                try:
                    msg = await rpc(ws, "aggTrades", {
                        "exchange": "COMEX", "symbol": "GCZ6",
                        "startTime": ms(cur), "endTime": ms(nxt), "limit": 0,
                    }, req, 180)
                    req += 1
                    rows = msg.get("result") or []
                    if msg.get("status") not in (None, 200):
                        meta["loi"].append("status %s %s..%s" % (msg.get("status"), cur, nxt))
                        print("status", msg.get("status"), cur, msg.get("error") or msg.get("msg"), flush=True)
                    for r in rows:
                        tm = r[0]; px = r[1]; qty = r[2]
                        side = r[3] if len(r) > 3 else ""
                        oid = r[4] if len(r) > 4 else ""
                        tu = r[5] if len(r) > 5 else ""
                        utc = from_ms(tm)
                        vn = (utc + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        w.writerow([tm, utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], vn, px, qty, side, oid, tu])
                    dem += len(rows)
                    f.flush()
                    print("ticks %s..%s -> %d tong=%d %.1fs" % (cur, nxt, len(rows), dem, time.time()-t_bat), flush=True)
                except Exception as e:
                    meta["loi"].append("aggTrades %s: %s" % (cur, e))
                    print("loi", cur, type(e).__name__, e, flush=True)
                    await asyncio.sleep(2)
                cur = nxt
        finally:
            f.close()
        meta["dem"] = dem
        meta["xong_luc_utc"] = datetime.now(timezone.utc).isoformat()
        (out / "meta_ticks.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print("XONG ticks", dem, "loi", len(meta["loi"]), "MB", path.stat().st_size/1024/1024, flush=True)
        return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_MAC_DINH)
    ap.add_argument("--start", default="2026-08-20T00:00:00")
    ap.add_argument("--end", default="2026-11-27T16:00:00")
    ap.add_argument("--buoc-gio", type=int, default=4)
    args = ap.parse_args()
    asyncio.run(keo(args.out, args.start, args.end, args.buoc_gio))


if __name__ == "__main__":
    main()
