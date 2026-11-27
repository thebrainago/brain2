# -*- coding: utf-8 -*-
"""Kéo nến 1m/1h và flowRecs/bigTrades GCZ6 từ Fxaurum local. KHÔNG gọi syncTicks/syncHistory."""
from __future__ import annotations
import argparse, asyncio, csv, json, os, time
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


async def rpc(ws, method, params, req_id, timeout=90):
    import json as _j
    await ws.send(_j.dumps({"method": method, "params": params, "id": req_id}))
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            raise TimeoutError(method)
        msg = _j.loads(await asyncio.wait_for(ws.recv(), timeout=remaining))
        if "stream" in msg:
            continue
        if msg.get("id") == req_id:
            return msg


def ghi_klines(path, rows, append=False):
    path = Path(path)
    moi = (not path.exists()) or not append
    with path.open("a" if append else "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if moi:
            w.writerow(["open_ms", "open_utc", "open_vn_utc7", "open", "high", "low", "close", "volume", "close_ms"])
        for r in rows:
            open_ms, o, h, l, c, v, close_ms = r
            utc = from_ms(open_ms)
            vn = (utc + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
            w.writerow([open_ms, utc.strftime("%Y-%m-%d %H:%M:%S"), vn, o, h, l, c, v, close_ms])


async def keo(out_dir: str, start: str, end: str):
    import websockets
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    t1 = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    meta = {"gateway": URL, "bat_dau_utc": t0.isoformat(), "ket_thuc_utc": t1.isoformat(),
            "keo_luc_utc": datetime.now(timezone.utc).isoformat(), "loi": [], "dem": {}}
    req = 1
    async with websockets.connect(URL, max_size=64 * 1024 * 1024, open_timeout=10, ping_interval=20) as ws:
        meta["ping"] = await rpc(ws, "ping", {}, req, 10); req += 1
        st = await rpc(ws, "syncStatus", {}, req, 10); req += 1
        meta["syncStatus"] = st
        if st.get("result", {}).get("running"):
            meta["loi"].append("syncStatus đang chạy — không gọi sync; chỉ đọc kho có sẵn")
        info = await rpc(ws, "tickInfo", {"exchange": "COMEX", "symbols": ["GCZ6"]}, req, 20); req += 1
        meta["tickInfo_GCZ6"] = info

        # 1h: cửa sổ 5 ngày, limit 200
        rows_h = []
        cur = t0
        while cur < t1:
            nxt = min(cur + timedelta(days=5), t1)
            try:
                msg = await rpc(ws, "klines", {
                    "exchange": "COMEX", "symbol": "GCZ6", "interval": "1h",
                    "startTime": ms(cur), "endTime": ms(nxt), "limit": 200,
                }, req, 60)
                req += 1
                rows = msg.get("result") or []
                rows_h.extend(rows)
                print(f"1h {cur}..{nxt} -> {len(rows)}", flush=True)
            except Exception as e:
                meta["loi"].append(f"klines 1h {cur}: {e}")
                print("loi 1h", cur, e, flush=True)
            cur = nxt
        ghi_klines(out / "gcz6_1h.csv", rows_h)
        meta["dem"]["gcz6_1h"] = len(rows_h)

        # 1m: cửa sổ 8 giờ (480 nến), limit 600
        path_m = out / "gcz6_1m.csv"
        if path_m.exists():
            path_m.unlink()
        dem_m = 0
        cur = t0
        first = True
        while cur < t1:
            nxt = min(cur + timedelta(hours=8), t1)
            try:
                msg = await rpc(ws, "klines", {
                    "exchange": "COMEX", "symbol": "GCZ6", "interval": "1m",
                    "startTime": ms(cur), "endTime": ms(nxt), "limit": 600,
                }, req, 60)
                req += 1
                rows = msg.get("result") or []
                if rows:
                    ghi_klines(path_m, rows, append=not first)
                    first = False
                    dem_m += len(rows)
                print(f"1m {cur}..{nxt} -> {len(rows)} tong={dem_m}", flush=True)
            except Exception as e:
                meta["loi"].append(f"klines 1m {cur}: {e}")
                print("loi 1m", cur, e, flush=True)
            cur = nxt
        meta["dem"]["gcz6_1m"] = dem_m

        # flowRecs + bigTrades theo ngày (tránh gói quá lớn)
        flow_all = {"sw": [], "cs": [], "ab": [], "ice": [], "lq": [], "cov": [], "abcov": [], "icecov": [], "lqcov": []}
        big_all = []
        cur = t0
        while cur < t1:
            nxt = min(cur + timedelta(days=1), t1)
            try:
                msg = await rpc(ws, "flowRecs", {
                    "exchange": "COMEX", "symbol": "GCZ6",
                    "startTime": ms(cur), "endTime": ms(nxt),
                }, req, 90)
                req += 1
                res = msg.get("result") or {}
                for k in flow_all:
                    flow_all[k].extend(res.get(k) or [])
                print(f"flow {cur.date()} sw={len(res.get('sw') or [])} ab={len(res.get('ab') or [])}", flush=True)
            except Exception as e:
                meta["loi"].append(f"flowRecs {cur.date()}: {e}")
                print("loi flow", cur.date(), e, flush=True)
            try:
                msg = await rpc(ws, "bigTrades", {
                    "exchange": "COMEX", "symbol": "GCZ6",
                    "startTime": ms(cur), "endTime": ms(nxt),
                    "min": 8, "merge": 0,
                }, req, 90)
                req += 1
                rows = msg.get("result") or []
                big_all.extend(rows)
                print(f"big {cur.date()} -> {len(rows)}", flush=True)
            except Exception as e:
                meta["loi"].append(f"bigTrades {cur.date()}: {e}")
                print("loi big", cur.date(), e, flush=True)
            cur = nxt

        (out / "gcz6_flow.json").write_text(json.dumps(flow_all, ensure_ascii=False), encoding="utf-8")
        with (out / "gcz6_bigtrades.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["time_ms", "time_utc", "time_vn_utc7", "side", "vol", "first_px", "last_px", "min_px", "max_px"])
            for r in big_all:
                # [timeMs, side, vol, firstPrice, lastPrice, minPrice, maxPrice, ...]
                tm, side, vol = r[0], r[1], r[2]
                fp = r[3] if len(r) > 3 else ""
                lp = r[4] if len(r) > 4 else ""
                mn = r[5] if len(r) > 5 else ""
                mx = r[6] if len(r) > 6 else ""
                utc = from_ms(tm)
                vn = (utc + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                w.writerow([tm, utc.strftime("%Y-%m-%d %H:%M:%S"), vn, side, vol, fp, lp, mn, mx])
        meta["dem"]["flow_sw"] = len(flow_all["sw"])
        meta["dem"]["flow_ab"] = len(flow_all["ab"])
        meta["dem"]["flow_ice"] = len(flow_all["ice"])
        meta["dem"]["flow_cs"] = len(flow_all["cs"])
        meta["dem"]["big"] = len(big_all)

    (out / "meta_keo.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("XONG", json.dumps(meta["dem"], ensure_ascii=False), "loi", len(meta["loi"]), flush=True)
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_MAC_DINH)
    ap.add_argument("--start", default="2026-08-20T00:00:00")
    ap.add_argument("--end", default="2026-11-27T16:00:00")
    args = ap.parse_args()
    asyncio.run(keo(args.out, args.start, args.end))


if __name__ == "__main__":
    main()
