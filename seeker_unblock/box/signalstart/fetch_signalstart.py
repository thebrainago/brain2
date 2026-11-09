#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SignalStart probe từ box.

ĐO 09–10/11/2026:
  - Homepage / search-signals: 200 HTML (không nhúng system id / CSV)
  - /login 200 — danh sách system cần đăng nhập
  - /systems,/api,/signals → 404
  - Không có CSV public kiểu FX Blue / C2

Script ghi probe; browser unlock = login + CDP bắt XHR.
Không lưu cookie/token.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

OUT_DEFAULT = Path("/workspace/nguon_khac/signalstart")


def session():
    from curl_cffi import requests as cr
    from curl_cffi import CurlOpt

    return cr.Session(impersonate="chrome", curl_options={CurlOpt.DOH_URL: "https://1.1.1.1/dns-query"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    s = session()
    rows = []
    for url in [
        "https://www.signalstart.com/",
        "https://www.signalstart.com/search-signals",
        "https://www.signalstart.com/login",
        "https://www.signalstart.com/simulator",
    ]:
        r = s.get(url, timeout=40)
        rows.append({"url": url, "status": r.status_code, "bytes": len(r.text), "final": str(r.url)})
        print(rows[-1])
    report = {
        "asof": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tz": "Asia/Bangkok",
        "verdict": "LOGIN_WALL — search-signals HTML không lộ CSV/id; cần login + XHR",
        "rows": rows,
        "browser_unlock": {
            "url": "https://www.signalstart.com/login",
            "steps": [
                "Login SignalStart trên máy nhà.",
                "Mở search-signals / system detail, CDP bắt XHR history/CSV.",
                "Chép endpoint (không cookie) vào module.",
            ],
        },
    }
    (args.out / "probe.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
