#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Forex Factory từ box — bypass Cloudflare bằng curl_cffi (Chrome impersonate + DoH).

ĐO 09/11/2026:
  - urllib/curl thường: 403 Cloudflare
  - curl_cffi impersonate=chrome: homepage/calendar/tradeexplorer **200**
  - URL đúng: /tradeexplorer (không phải /trade-explorer)
  - API: GET /tradeexplorer/public-by-username?username=X → JSON {user_id, explorers:[]}
  - /explorerapi.php?content=graphdata&id=... (cần id explorer công khai)
  - Leaderboard list explorers: chưa bắt được endpoint list (có thể cần login)

Không lưu cookie/token.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

OUT_DEFAULT = Path("/workspace/nguon_khac/forexfactory")


def session():
    from curl_cffi import requests as cr
    from curl_cffi import CurlOpt

    return cr.Session(impersonate="chrome", curl_options={CurlOpt.DOH_URL: "https://1.1.1.1/dns-query"})


def probe(out: Path) -> dict:
    s = session()
    rows = []
    for url in [
        "https://www.forexfactory.com/",
        "https://www.forexfactory.com/tradeexplorer",
        "https://www.forexfactory.com/trades",
        "https://www.forexfactory.com/traders",
        "https://www.forexfactory.com/calendar",
    ]:
        r = s.get(url, timeout=40)
        t = r.text
        rows.append(
            {
                "url": url,
                "status": r.status_code,
                "bytes": len(t),
                "cloudflare": "Just a moment" in t,
                "title": (t[t.find("<title>") + 7 : t.find("</title>")][:80] if "<title>" in t else ""),
            }
        )
        print(rows[-1])
    # warm + sample username API
    s.get("https://www.forexfactory.com/tradeexplorer", timeout=40)
    sample = s.get(
        "https://www.forexfactory.com/tradeexplorer/public-by-username",
        params={"username": "example"},
        timeout=20,
    )
    report = {
        "asof": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tz": "Asia/Bangkok",
        "method": "curl_cffi impersonate=chrome + DoH 1.1.1.1",
        "rows": rows,
        "public_by_username_example": sample.json() if sample.headers.get("content-type", "").startswith("application/json") else sample.text[:200],
        "verdict": "CF_BYPASS_OK — pages readable; trade CSV cần explorer id công khai (list leaderboard chưa có)",
        "browser_unlock": {
            "url": "https://www.forexfactory.com/tradeexplorer",
            "steps": [
                "Login FF trên máy nhà nếu leaderboard private.",
                "DevTools → XHR khi mở leaderboard / một explorer công khai.",
                "Chép endpoint list + trades (không cookie) vào module.",
                "Hoặc gửi username FF có explorer public → gọi public-by-username.",
            ],
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe_curl_cffi.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def try_explorerapi(explorer_id: int, content: str = "graphdata", **extra) -> dict:
    """Gọi explorerapi.php — cần id explorer công khai. content: graphdata|tradegraphdata|chartedtrade|positions."""
    s = session()
    s.get("https://www.forexfactory.com/tradeexplorer", timeout=40)
    params = {"content": content, "id": explorer_id, **extra}
    r = s.get("https://www.forexfactory.com/explorerapi.php", params=params, timeout=25)
    body = r.json() if "json" in r.headers.get("content-type", "") else r.text
    return {"status": r.status_code, "params": params, "body": body}


def lookup_username(username: str) -> dict:
    s = session()
    s.get("https://www.forexfactory.com/tradeexplorer", timeout=40)
    r = s.get(
        "https://www.forexfactory.com/tradeexplorer/public-by-username",
        params={"username": username},
        timeout=20,
    )
    return {"status": r.status_code, "body": r.json() if "json" in r.headers.get("content-type", "") else r.text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--username", help="lookup public explorers by FF username")
    ap.add_argument("--explorer-id", type=int, help="probe explorerapi.php with this id")
    ap.add_argument("--content", default="graphdata")
    args = ap.parse_args()
    if args.explorer_id is not None:
        print(try_explorerapi(args.explorer_id, content=args.content, period="all", overview=1))
    elif args.username:
        print(lookup_username(args.username))
    else:
        probe(args.out)


if __name__ == "__main__":
    main()
