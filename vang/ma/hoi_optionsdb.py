# -*- coding: utf-8 -*-
"""Doc OptionsDb qua RPC (optionRecordStatus, optionHistory). Khong bat recorder moi, khong sync."""
from __future__ import annotations
import asyncio, json
from datetime import datetime, timezone
from pathlib import Path

URL = "ws://127.0.0.1:9001/"
OUT = Path(r"E:\brain2_tmp\vang\fxaurum")


async def rpc(ws, method, params, req_id, timeout=60):
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


async def main():
    import websockets
    OUT.mkdir(parents=True, exist_ok=True)
    bao = {"luc_utc": datetime.now(timezone.utc).isoformat(), "loi": []}
    req = 1
    async with websockets.connect(URL, max_size=64*1024*1024, open_timeout=10, ping_interval=20) as ws:
        bao["ping"] = await rpc(ws, "ping", {}, req, 10); req += 1
        try:
            bao["optionRecordStatus"] = await rpc(ws, "optionRecordStatus", {}, req, 20); req += 1
        except Exception as e:
            bao["loi"].append("optionRecordStatus: %s" % e)
        # thu cac cap exchange/underlying pho bien cho vang
        pairs = [
            ("COMEX", "GCZ6"), ("COMEX", "GC"), ("NYMEX", "GCZ6"),
            ("CME", "GCZ6"), ("CME", "GC"),
        ]
        for ex, und in pairs:
            try:
                msg = await rpc(ws, "optionChain", {"exchange": ex, "underlying": und}, req, 30)
                req += 1
                res = msg.get("result")
                n = 0
                if isinstance(res, list):
                    n = len(res)
                elif isinstance(res, dict):
                    n = len(res.get("legs") or res.get("options") or res.keys())
                print("optionChain", ex, und, "status", msg.get("status"), "n", n, flush=True)
                bao.setdefault("optionChain", {})["%s|%s"%(ex,und)] = {
                    "status": msg.get("status"), "keys": list(res)[:8] if isinstance(res, dict) else n,
                    "sample": (res[:2] if isinstance(res, list) else None),
                }
            except Exception as e:
                bao["loi"].append("optionChain %s %s: %s" % (ex, und, e))
                print("loi chain", ex, und, e, flush=True)
        # optionHistory neu status cho thay chuoi
        st = bao.get("optionRecordStatus") or {}
        print("optionRecordStatus", json.dumps(st, ensure_ascii=False)[:800], flush=True)
        # thu doc lich su GC / GCZ6 thang 8-11 2026
        for ex, und in (("COMEX","GCZ6"),("COMEX","GC"),("CME","GCZ6")):
            try:
                msg = await rpc(ws, "optionHistory", {
                    "exchange": ex, "underlying": und,
                    "fromTime": int(datetime(2026,8,20,tzinfo=timezone.utc).timestamp()*1000),
                    "endTime": int(datetime(2026,11,27,16,tzinfo=timezone.utc).timestamp()*1000),
                    "limit": 200000,
                }, req, 90)
                req += 1
                res = msg.get("result") or {}
                ev = res.get("events") or []
                md = res.get("metadata") or []
                print("optionHistory", ex, und, "status", msg.get("status"), "meta", len(md) if isinstance(md,list) else type(md), "events", len(ev) if isinstance(ev,list) else type(ev), flush=True)
                bao.setdefault("optionHistory", {})["%s|%s"%(ex,und)] = {
                    "status": msg.get("status"),
                    "n_meta": len(md) if isinstance(md, list) else None,
                    "n_events": len(ev) if isinstance(ev, list) else None,
                    "truncated": res.get("truncated"),
                    "sample_meta": (md[:1] if isinstance(md, list) else None),
                }
                if ev:
                    # ghi gon
                    p = OUT / ("option_hist_%s_%s.json" % (ex, und))
                    p.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
                    print("ghi", p, p.stat().st_size, flush=True)
            except Exception as e:
                bao["loi"].append("optionHistory %s %s: %s" % (ex, und, e))
                print("loi hist", ex, und, e, flush=True)

    (OUT / "meta_optionsdb.json").write_text(json.dumps(bao, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("XONG options probe loi", len(bao["loi"]), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
