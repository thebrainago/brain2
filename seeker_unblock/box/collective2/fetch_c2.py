#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tải CSV lịch sử lệnh Collective2 công khai từ box.

Endpoint sống (ĐO 09/11/2026):
  https://collective2.com/strategy/csv/{strategyId}
  Trang chi tiết: https://collective2.com/details/{strategyId}
  Danh sách forex (HTML ít ID, phần lớn JS): https://collective2.com/forex-systems
  Leaderboard: https://collective2.com/leaderboard  (nhúng nhiều strategyId trong HTML)

API v4 GetStrategyHistoricalClosedTrades / api.collective2.com: 404 hoặc Offline maintenance từ box.
trade.collective2.com homepage hiện là mockup tĩnh — KHÔNG dùng làm nguồn.

Không cần API key cho /strategy/csv/{id}. Không lưu secret.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.http_box import PacedClient  # noqa: E402

OUT_DEFAULT = Path("/workspace/nguon_khac/collective2")

# ID forex đã ĐO có CSV (09/11/2026). Không phải danh sách đủ.
KNOWN_FOREX_IDS = [
    "134962085",  # FOREX VIX-3
    "122467834",  # Tendency Forex
    "94987184",   # Just Forex Trades
    "140118626",  # ECFXBB
    "125545530",  # Wait4Trade
    "128801236",  # MULTI FX PURE
    "128454494",  # Deep in the money
    "117104490",  # FX Hedge Fund
    "123920081",  # Multi Timeframe Forex
    "137931431",  # multiprofit
]


def discover_ids(client: PacedClient) -> list[str]:
    ids = set()
    for url in (
        "https://collective2.com/leaderboard",
        "https://collective2.com/forex-systems",
        "https://collective2.com/cgi-perl/newreports.mpl?instrument=forex",
        "https://collective2.com/grid",
    ):
        r = client.get(url)
        html = r.body.decode("utf-8", errors="ignore")
        ids.update(re.findall(r"/details/(\d{6,10})", html))
        ids.update(re.findall(r"(?:strategyId|systemid|SystemId)[\"\s:=]+(\d{6,10})", html, re.I))
        ids.update(re.findall(r"/strategy/csv/(\d{6,10})", html))
    return sorted(ids)


def fetch_csv(client: PacedClient, sid: str, out_dir: Path) -> dict:
    url = f"https://collective2.com/strategy/csv/{sid}"
    r = client.get(url)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{sid}.csv"
    path.write_bytes(r.body)
    meta = {"id": sid, "url": url, "status": r.status, "bytes": len(r.body), "path": str(path)}
    if r.status != 200 or b"Open Time ET" not in r.body[:200]:
        meta["ok"] = False
        return meta
    rows = list(csv.DictReader(path.open(encoding="utf-8", errors="ignore")))
    times = []
    fx = 0
    for row in rows:
        sym = (row.get("Symbol") or "")
        if "/" in sym:
            fx += 1
        for k in ("Closed Time ET", "Open Time ET"):
            s = (row.get(k) or "").strip().strip('"')
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    times.append(datetime.strptime(s, fmt))
                    break
                except ValueError:
                    pass
    meta.update({"ok": True, "n": len(rows), "fx_n": fx, "fx_pct": round(fx / len(rows), 3) if rows else 0})
    if times:
        meta["t0"] = min(times).isoformat(sep=" ")
        meta["t1"] = max(times).isoformat(sep=" ")
        meta["years"] = round((max(times) - min(times)).days / 365.25, 3)
    # optional name from details page
    d = client.get(f"https://collective2.com/details/{sid}")
    m = re.search(r"<title>([^—<]+)", d.body.decode("utf-8", errors="ignore"))
    if m:
        meta["name"] = m.group(1).strip()
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="strategy IDs; empty = discover then fetch")
    ap.add_argument("--discover-only", action="store_true")
    ap.add_argument("--fx-only", action="store_true", help="keep only fx_pct>=0.5")
    ap.add_argument("--min-years", type=float, default=0.0)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--pace", type=float, default=0.4)
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()
    client = PacedClient(min_interval_s=args.pace)
    ids = list(args.ids) if args.ids else discover_ids(client)
    if args.discover_only:
        print(json.dumps(ids, indent=2))
        return
    results = []
    for sid in ids[: args.limit]:
        meta = fetch_csv(client, sid, args.out)
        if args.fx_only and meta.get("fx_pct", 0) < 0.5:
            continue
        if meta.get("years", 0) < args.min_years:
            continue
        results.append(meta)
        print(meta)
    (args.out / "fetch_meta.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
