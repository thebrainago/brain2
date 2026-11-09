#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tải CSV lịch sử lệnh công khai FX Blue từ box (không cần login nếu account public).

Endpoint sống (ĐO 09/11/2026):
  https://www.fxblue.com/users/{username}/csv
  https://api.fxblue.com/users/{username}/stats   (HTML thống kê)
  https://www.fxblue.com/users/{username}/rss     (open/recent only)

Một số account trả '(Only allowed when logged in)' trong CSV → cần session trình duyệt
(máy nhà / Anh login thebrainalgo). Không lưu cookie/password trong repo.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.http_box import PacedClient  # noqa: E402

OUT_DEFAULT = Path("/workspace/nguon_khac/fxblue")

# Username đã ĐO có CSV public (09/11/2026). Private/login wall không liệt kê đầy đủ.
KNOWN_USERS = [
    "liehtw", "night-hawk", "icmarkets-demo", "Public-stats", "happy-forex",
    "ibitebyt3s-10k-50r", "algobreed-xauusd-1", "algobreed-xauusd-2", "xmglobal",
    "eatradingacademy", "easyscalper", "trend-detector", "forex_trend_detector",
    "myforexpath1", "myforexpath2", "free-forex-signal", "Metaliq-Gold", "metaliq_gold",
    "Seagull_EA", "gpbootcamp", "forex_edge_pro", "bullbear", "algo-trading",
    "forexlive", "fx-ea", "swingfx", "robot-forex", "supplydemand", "fibonacci",
    "alphafx", "capitalgrowth", "gold-pips", "gold_scalping", "nsr_gold",
    "forex-gold-investor", "divisagold", "fx-ekspert-ma-demo",
]
# Cần login session: solid_gold_fund, 24hourfxsignals, steady_compounding


def fetch_csv(client: PacedClient, username: str, out_dir: Path) -> dict:
    url = f"https://www.fxblue.com/users/{username}/csv"
    r = client.get(url)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{username}.csv"
    path.write_bytes(r.body)
    text = r.body.decode("utf-8", errors="ignore")
    meta = {
        "username": username,
        "url": url,
        "status": r.status,
        "bytes": len(r.body),
        "path": str(path),
        "login_wall": "Only allowed when logged in" in text[:1000],
        "is_csv": "Type,Ticket" in text[:500],
    }
    if meta["login_wall"] or not meta["is_csv"]:
        meta["n_closed"] = 0
        return meta
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("sep=")]
    rows = list(csv.DictReader(lines))
    closed = [row for row in rows if (row.get("Type") or "").lower().startswith("closed")]
    dates = []
    for row in closed:
        for k in ("Close time", "Open time"):
            s = (row.get(k) or "").strip()
            if not s or s.startswith("1970"):
                continue
            for fmt in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
                try:
                    dates.append(datetime.strptime(s, fmt))
                    break
                except ValueError:
                    pass
    meta["n_closed"] = len(closed)
    if dates:
        meta["t0"] = min(dates).isoformat(sep=" ")
        meta["t1"] = max(dates).isoformat(sep=" ")
        meta["years"] = round((max(dates) - min(dates)).days / 365.25, 3)
    # optional stats history days
    sr = client.get(f"https://api.fxblue.com/users/{username}/stats")
    m = re.search(r"History.*?([\d,]+)\s*days", sr.body.decode("utf-8", errors="ignore"), re.I | re.S)
    if m:
        meta["history_days_stats"] = int(m.group(1).replace(",", ""))
    return meta


def main():
    ap = argparse.ArgumentParser(description="Fetch public FX Blue trade CSVs")
    ap.add_argument("usernames", nargs="+", help="FX Blue usernames")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--pace", type=float, default=0.5, help="seconds between requests")
    args = ap.parse_args()
    client = PacedClient(min_interval_s=args.pace)
    for u in args.usernames:
        meta = fetch_csv(client, u, args.out)
        print(meta)


if __name__ == "__main__":
    main()
