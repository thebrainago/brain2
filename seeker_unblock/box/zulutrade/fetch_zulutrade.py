#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZuluTrade probe từ box.

ĐO 09–10/11/2026:
  - SPA Vue: /js/app.*.js → VUE_APP_API_BASE_URL = https://www.zulutrade.com/zulutrade-gateway/
  - OAuth: POST {gateway}auth-server/oauth/token (cần credential user / SPA client — KHÔNG lưu secret)
  - GET {gateway}api/* → 401 unauthorized khi chưa có Bearer
  - Template công khai trong SPA (cần auth):
      api/providers/performance/topTraders/search?flavorId=&accessingFlavorId=
      v2/api/providers/{{TradeID}}/thi/init?...
  - api.zulutrade.com → 502; HTML /traders|/leaders = shell SPA

Script: probe status + ghi báo cáo. Không ghi client_secret/token/cookie.
Khi Anh login máy nhà: CDP bắt XHR ranking/trades → điền ZULU_JSON_ENDPOINTS.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.http_box import PacedClient  # noqa: E402

OUT_DEFAULT = Path("/workspace/nguon_khac/zulutrade")
GATEWAY = "https://www.zulutrade.com/zulutrade-gateway/"

PROBE_URLS = [
    "https://www.zulutrade.com/",
    "https://www.zulutrade.com/traders",
    "https://www.zulutrade.com/leaders",
    GATEWAY,
    GATEWAY + "api/providers",
    GATEWAY + "api/ranking",
    GATEWAY + "auth-server/oauth/token",
    "https://api.zulutrade.com/traders",
]

# Điền URL JSON SAU khi bắt XHR (không kèm cookie/token).
ZULU_JSON_ENDPOINTS: list[str] = []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--pace", type=float, default=0.5)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    client = PacedClient(min_interval_s=args.pace)
    rows = []
    for url in PROBE_URLS + ZULU_JSON_ENDPOINTS:
        r = client.get(url, headers={"Accept": "application/json,text/html,*/*"})
        snippet = r.body[:120].decode("utf-8", errors="ignore").replace("\n", " ")
        kind = "json" if r.body[:1] in (b"{", b"[") else ("html" if b"<html" in r.body[:200].lower() else "other")
        rows.append(
            {"url": url, "status": r.status, "bytes": len(r.body), "kind": kind, "snippet": snippet, "error": r.error}
        )
        print(rows[-1])
    report = {
        "asof": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tz": "Asia/Bangkok",
        "verdict": "GATEWAY_FOUND_BUT_401 — cần OAuth user (CDP máy nhà); không lưu secret",
        "gateway": GATEWAY,
        "oauth_path": "auth-server/oauth/token",
        "known_api_templates": [
            "api/providers/performance/topTraders/search?flavorId={{flavorId}}&accessingFlavorId={{accessingFlavorId}}",
            "v2/api/providers/{{TradeID}}/thi/init?accessingFlavorId={{flavorId}}&flavor={{region}}",
        ],
        "rows": rows,
        "browser_unlock": {
            "url": "https://www.zulutrade.com/traders",
            "steps": [
                "Login Zulu trên máy nhà (egress nhà).",
                "DevTools → Network → XHR, mở /traders hoặc /zuluranking.",
                "Chép URL JSON ranking + trade history (không cookie/token) vào ZULU_JSON_ENDPOINTS.",
                "Chạy lại script; không commit secret/token.",
            ],
        },
    }
    (args.out / "probe.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
