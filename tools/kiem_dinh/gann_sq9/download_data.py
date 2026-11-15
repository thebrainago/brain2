#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tải lại các file data_*.pkl từ Yahoo Finance để chạy bộ kiểm định.

Chạy từ thư mục này (tools/kiem_dinh/gann_sq9):

    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python download_data.py

Các test đọc file .pkl cạnh script, đúng tên dưới đây. Không commit file .pkl.

Giới hạn Yahoo (tại thời điểm viết, 11/2026):
  - 1d: lịch sử dài (period=max)
  - 1h: khoảng 2 năm
  - 15m / 5m: khoảng 60 ngày

Lưu ý: GC=F trước 2008 có nhiều nến High=Low (dữ liệu hỏng);
các script vòng 2+ đã lọc từ 2008-01-01 và loại nến H=L.
ES=F là chuỗi hợp đồng gần nhất, không điều chỉnh roll.
^GSPC Open trước ~2014 trên Yahoo thường trùng Close hôm trước.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yfinance as yf

HERE = Path(__file__).resolve().parent

# (yahoo ticker, file stem, interval)
JOBS = [
    ("GC=F", "GCF", "1d"),
    ("GC=F", "GCF", "1h"),
    ("GC=F", "GCF", "15m"),
    ("GC=F", "GCF", "5m"),
    ("ES=F", "ESF", "1d"),
    ("ES=F", "ESF", "1h"),
    ("ES=F", "ESF", "15m"),
    ("ES=F", "ESF", "5m"),
    ("^GSPC", "GSPC", "1d"),
    ("^GSPC", "GSPC", "1h"),
    ("^GSPC", "GSPC", "15m"),
    ("^GSPC", "GSPC", "5m"),
    ("SPY", "SPY", "1d"),
    ("^VIX", "VIX", "1d"),
    ("GLD", "GLD", "1d"),
]


def download_one(ticker: str, stem: str, interval: str, out_dir: Path) -> Path:
    print(f"Tải {ticker} {interval} ...", flush=True)
    df = yf.download(ticker, period="max", interval=interval, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise RuntimeError(f"Yahoo trả về rỗng cho {ticker} {interval}")
    path = out_dir / f"data_{stem}_{interval}.pkl"
    df.to_pickle(path)
    print(f"  -> {path.name}: {len(df)} hàng, {df.index.min()} → {df.index.max()}")
    return path


def main() -> None:
    p = argparse.ArgumentParser(description="Tải data_*.pkl từ Yahoo Finance")
    p.add_argument("--out", type=Path, default=HERE, help="Thư mục ghi file (mặc định: cạnh script)")
    p.add_argument("--only", nargs="*", help="Chỉ tải các stem_interval, ví dụ: GCF_1d ESF_1d VIX_1d")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = JOBS
    if args.only:
        want = set(args.only)
        jobs = [(t, s, i) for t, s, i in JOBS if f"{s}_{i}" in want]
        missing = want - {f"{s}_{i}" for _, s, i in jobs}
        if missing:
            raise SystemExit(f"Không nhận ra: {sorted(missing)}")
    for ticker, stem, interval in jobs:
        download_one(ticker, stem, interval, args.out)


if __name__ == "__main__":
    main()
