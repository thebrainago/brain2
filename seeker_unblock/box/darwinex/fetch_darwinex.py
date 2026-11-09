#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Darwinex từ box: series-level thôi (lệnh từng trade KHÔNG công khai).

ĐO 09/11/2026:
  - https://www.darwinex.com/invest/{TICKER} → 200 HTML (return total / annualized)
  - https://www.darwinex.com/api/filters/products/all → 401 (trước 14/08/2026 từng 200)
  - api.darwinex.com/* quotes/info → cần OAuth token (không tạo tài khoản trả phí / không nhét secret)

Snapshot 1000 DARWIN còn trong reports/darwinex_darwins.json (2026-08-14) dùng làm universe.
Script này: (1) lọc ≥2y DD/return từ snapshot, (2) refresh HTML metrics, (3) ghi series CSV.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.http_box import PacedClient  # noqa: E402

SNAP = Path("/workspace/brain2/reports/darwinex_darwins.json")
OUT_DEFAULT = Path("/workspace/nguon_khac/darwinex")


def load_candidates(min_years: float = 2.0, max_dd: float = 60.0, min_ret: float = 10.0, limit: int = 30):
    data = json.loads(SNAP.read_text(encoding="utf-8"))
    now_ms = datetime(2026, 11, 9, tzinfo=timezone.utc).timestamp() * 1000
    rows = []
    for r in data.get("darwins", []):
        fq = r.get("firstQuoteDate") or 0
        years = (now_ms - fq) / 1000 / 86400 / 365.25
        dd = abs(r.get("drawDownByPeriod") or 99)
        ret = r.get("returnByPeriod") or 0
        if years >= min_years and dd <= max_dd and ret >= min_ret:
            cagr = ((1 + ret / 100) ** (1 / 2) - 1) * 100
            rows.append({**r, "years": years, "cagr_2y_approx": cagr})
    rows.sort(key=lambda x: -(x["returnByPeriod"] / max(abs(x.get("drawDownByPeriod") or 1), 1)))
    return rows[:limit]


def scrape_invest(client: PacedClient, ticker: str, out_dir: Path) -> dict:
    url = f"https://www.darwinex.com/invest/{ticker}"
    r = client.get(url)
    html_path = out_dir / f"{ticker}.html"
    html_path.write_bytes(r.body)
    html = r.body.decode("utf-8", errors="ignore")

    def grab(pat):
        m = re.search(pat, html, re.I | re.S)
        return m.group(1).replace(",", "") if m else None

    return {
        "ticker": ticker,
        "status": r.status,
        "ret_total_html": grab(r"return-total[^>]*>\s*([-\d.,]+)\s*<"),
        "ret_ann_html": grab(r"return-annualized[^>]*>\s*([-\d.,]+)\s*<"),
        "html": str(html_path),
    }


def write_series_csv(out_dir: Path, row: dict, html_meta: dict) -> None:
    path = out_dir / f"{row['darwin']}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["level", "ticker", "metric", "value", "unit", "source", "asof"])
        w.writerow(["series", row["darwin"], "return_2y", row.get("returnByPeriod"), "pct", "darwinex_darwins.json", "2026-08-14"])
        w.writerow(["series", row["darwin"], "drawdown_2y", row.get("drawDownByPeriod"), "pct", "darwinex_darwins.json", "2026-08-14"])
        w.writerow(["series", row["darwin"], "cagr_2y_approx", round(row.get("cagr_2y_approx") or 0, 2), "pct/yr", "computed", "2026-11-09"])
        w.writerow(["series", row["darwin"], "ret_total_html", html_meta.get("ret_total_html"), "pct", f"invest/{row['darwin']}", "2026-11-09"])
        w.writerow(["series", row["darwin"], "ret_ann_html", html_meta.get("ret_ann_html"), "pct/yr", f"invest/{row['darwin']}", "2026-11-09"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--pace", type=float, default=0.5)
    ap.add_argument("--min-years", type=float, default=2.0)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    client = PacedClient(min_interval_s=args.pace)
    cands = load_candidates(min_years=args.min_years, limit=args.limit)
    gate = []
    for row in cands:
        html_meta = scrape_invest(client, row["darwin"], args.out)
        write_series_csv(args.out, row, html_meta)
        verdict = "SERIES_PASS" if (row["cagr_2y_approx"] > 10 and abs(row.get("drawDownByPeriod") or 0) < 80) else "SERIES_FAIL"
        gate.append(
            {
                "ticker": row["darwin"],
                "years_api": round(row["years"], 2),
                "ret_2y_api": row.get("returnByPeriod"),
                "dd_2y_api": row.get("drawDownByPeriod"),
                "cagr_2y_approx": round(row["cagr_2y_approx"], 2),
                "verdict": verdict,
                "gate": "series-level (no trades public)",
                **{k: html_meta.get(k) for k in ("ret_total_html", "ret_ann_html", "status")},
            }
        )
        print(gate[-1])
    (args.out / "series_gate.json").write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
