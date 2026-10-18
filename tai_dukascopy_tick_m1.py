#!/usr/bin/env python3
"""Tải tick Dukascopy (bi5 giờ, Bid/Ask) -> gom NGAY thành M1 Bid/Ask OHLC + spread + số tick.

CHẠY TRÊN MÁY NHÀ: Dukascopy chặn IP của box (18/10/2026). Script nằm ở gốc repo như tai_dukascopy_h1.py và
tai_dukascopy_spread.py. Đặt biến DU_LIEU_CHUAN=<thư mục kho> (mặc định /workspace/du_lieu_chuan); bên đọc là `du_lieu_chuan.py` ở gốc repo.

    nohup python3 tai_dukascopy_tick_m1.py --luong 8 > /workspace/du_lieu_chuan/tai.log 2>&1 &
    python3 tai_dukascopy_tick_m1.py --ma EURUSD --tu 2024-01-01 --den 2024-01-31

- Không lưu bi5 xuống đĩa (giải nén trong RAM) -> không có file bi5 phải xoá.
- Ghi theo ngày: /workspace/du_lieu_chuan/_ngay/{MA}/{YYYY-MM-DD}.parquet, sau đó `gom_nam` gộp thành
  /workspace/du_lieu_chuan/m1/{MA}/{MA}_{YYYY}.parquet (zstd) và xoá file ngày.
- Trạng thái: /workspace/du_lieu_chuan/trang_thai.sqlite (ngày đã xong) -> chạy lại tự tiếp tục.
- Tốc độ tự điều chỉnh: 429/503 -> cả tiến trình nghỉ (backoff mũ, tối đa 15 phút) và giảm số luồng
  hoạt động; chuỗi thành công -> tăng dần tới --luong. Không vượt chống bot.
- Ô cuối tuần / giờ không có tick: server trả 200 rỗng hoặc 404 -> ghi là 0 tick (không bịa nến).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import lzma
import os
import random
import shutil
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

GOC = Path(os.environ.get("DU_LIEU_CHUAN", "/workspace/du_lieu_chuan"))
URL = "https://datafeed.dukascopy.com/datafeed/{ma}/{y}/{m0:02d}/{d:02d}/{h:02d}h_ticks.bi5"

# tên chuẩn -> (mã datafeed, hệ số giá, năm dò bắt đầu). Thứ tự = ưu tiên tải.
MA = {
    "USA500.IDX": ("USA500IDXUSD", 1000, 2010),
    "USATECH.IDX": ("USATECHIDXUSD", 1000, 2010),
    "XAUUSD": ("XAUUSD", 1000, 2003),
    "LIGHT.CMD": ("LIGHTCMDUSD", 1000, 2010),
    "EURUSD": ("EURUSD", 100000, 2003),
    "GBPUSD": ("GBPUSD", 100000, 2003),
    "AUDUSD": ("AUDUSD", 100000, 2003),
    "USDJPY": ("USDJPY", 1000, 2003),
    "XAGUSD": ("XAGUSD", 1000, 2003),
    "USDCAD": ("USDCAD", 100000, 2003),
    "USDCHF": ("USDCHF", 100000, 2003),
    "NZDUSD": ("NZDUSD", 100000, 2003),
    "EURJPY": ("EURJPY", 1000, 2003),
    "EURGBP": ("EURGBP", 100000, 2003),
    "GBPJPY": ("GBPJPY", 1000, 2003),
    "DEU.IDX": ("DEUIDXEUR", 1000, 2010),
    "GBR.IDX": ("GBRIDXGBP", 1000, 2010),
    "JPN.IDX": ("JPNIDXJPY", 1000, 2010),
    "BRENT.CMD": ("BRENTCMDUSD", 1000, 2010),
}
TICK_DT = np.dtype([("ms", ">u4"), ("ask", ">i4"), ("bid", ">i4"), ("av", ">f4"), ("bv", ">f4")])


def giai_ma_tick(raw: bytes, gio: pd.Timestamp, he_so: int) -> pd.DataFrame:
    """bi5 (LZMA, bản ghi 20 byte BE: ms,ask,bid,askvol,bidvol) -> DataFrame tick UTC."""
    if not raw:
        return pd.DataFrame(columns=["bid", "ask"])
    a = np.frombuffer(lzma.decompress(raw), dtype=TICK_DT)
    t = gio.value + a["ms"].astype(np.int64) * 1_000_000
    return pd.DataFrame({"bid": a["bid"] / he_so, "ask": a["ask"] / he_so},
                        index=pd.DatetimeIndex(t, tz="UTC"))


def gom_m1(tick: pd.DataFrame) -> pd.DataFrame:
    """tick -> M1 nhãn trái (phút 14:05 = 14:05:00..14:05:59.999). Phút không có tick -> không có dòng."""
    cot = ["bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c",
           "spread_tb", "spread_min", "spread_max", "so_tick"]
    if tick.empty:
        return pd.DataFrame(columns=cot)
    tick = tick.sort_index(kind="stable")
    sp = tick["ask"] - tick["bid"]
    g = tick.assign(sp=sp).groupby(tick.index.floor("1min"))
    df = pd.DataFrame({
        "bid_o": g["bid"].first(), "bid_h": g["bid"].max(), "bid_l": g["bid"].min(), "bid_c": g["bid"].last(),
        "ask_o": g["ask"].first(), "ask_h": g["ask"].max(), "ask_l": g["ask"].min(), "ask_c": g["ask"].last(),
        "spread_tb": g["sp"].mean(), "spread_min": g["sp"].min(), "spread_max": g["sp"].max(),
        "so_tick": g["sp"].size().astype("int32"),
    })
    df.index.name = "time"
    return df[cot]


class BoDieuToc:
    """Giới hạn luồng hoạt động + nghỉ toàn cục khi server báo quá tải."""

    def __init__(self, toi_da: int):
        self.toi_da, self.hien = toi_da, max(2, toi_da // 2)
        self.dang = 0
        self.cv = threading.Condition()
        self.nghi_den = 0.0
        self.lan_chan = 0
        self.ok_lien = 0
        self.dem = {"ok": 0, "rong": 0, "chan": 0, "loi": 0}

    def vao(self):
        with self.cv:
            while self.dang >= self.hien or time.time() < self.nghi_den:
                self.cv.wait(timeout=max(0.2, min(5, self.nghi_den - time.time())))
            self.dang += 1

    def ra(self):
        with self.cv:
            self.dang -= 1
            self.cv.notify_all()

    def bi_chan(self):
        with self.cv:
            self.dem["chan"] += 1
            if time.time() < self.nghi_den:
                return
            self.lan_chan += 1
            self.ok_lien = 0
            self.hien = max(1, self.hien // 2)
            nghi = min(900, 20 * 2 ** min(self.lan_chan - 1, 6)) * random.uniform(0.8, 1.2)
            self.nghi_den = time.time() + nghi
            print(f"{dt.datetime.now():%F %T} server chặn/quá tải -> nghỉ {nghi:.0f}s, luồng={self.hien}",
                  flush=True)

    def thanh_cong(self):
        with self.cv:
            self.ok_lien += 1
            if self.ok_lien >= 300:
                self.ok_lien = 0
                self.lan_chan = max(0, self.lan_chan - 1)
                if self.hien < self.toi_da:
                    self.hien += 1


_tl = threading.local()


def lay(url: str, dt_: BoDieuToc) -> bytes | None:
    """Trả bytes (b'' nếu không có tick); None nếu lỗi bền sau nhiều lần thử."""
    s = getattr(_tl, "s", None)
    if s is None:
        s = _tl.s = requests.Session()
        s.headers["User-Agent"] = "brain2-du-lieu-chuan/1.0 (nghien cuu)"
    lan = 0
    while lan < 12:
        dt_.vao()
        try:
            r = s.get(url, timeout=40)
            ma = r.status_code
            body = r.content
        except requests.RequestException:
            ma, body = -1, b""
        finally:
            dt_.ra()
        if ma == 200:
            dt_.thanh_cong()
            dt_.dem["ok" if body else "rong"] += 1
            return body
        if ma == 404:
            dt_.dem["rong"] += 1
            return b""
        if ma in (429, 503, 403):
            dt_.bi_chan()          # bị chặn: chờ, không tính vào số lần thử
        else:
            lan += 1
            dt_.dem["loi"] += 1
            time.sleep(min(60, 2 ** lan) * random.uniform(0.5, 1.5))
    return None


# ---------------- trạng thái ----------------
_db_khoa = threading.Lock()


def mo_db() -> sqlite3.Connection:
    GOC.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(GOC / "trang_thai.sqlite", check_same_thread=False, timeout=60)
    c.execute("CREATE TABLE IF NOT EXISTS ngay (ma TEXT, ngay TEXT, so_phut INT, so_tick INT, "
              "luc TEXT, PRIMARY KEY(ma, ngay))")
    c.execute("CREATE TABLE IF NOT EXISTS bat_dau (ma TEXT PRIMARY KEY, ngay TEXT)")
    c.commit()
    return c


def da_xong(c, ma) -> set:
    with _db_khoa:
        return {r[0] for r in c.execute("SELECT ngay FROM ngay WHERE ma=?", (ma,))}


def ghi_xong(c, ma, ngay, so_phut, so_tick):
    with _db_khoa:
        c.execute("INSERT OR REPLACE INTO ngay VALUES (?,?,?,?,?)",
                  (ma, ngay, so_phut, so_tick, dt.datetime.now().isoformat(timespec="seconds")))
        c.commit()


def do_bat_dau(c, ten: str, dt_: BoDieuToc) -> str | None:
    """Dò tháng đầu tiên có tick (thử các giờ 10/14 UTC của vài ngày thường trong tháng)."""
    with _db_khoa:
        r = c.execute("SELECT ngay FROM bat_dau WHERE ma=?", (ten,)).fetchone()
    if r:
        return r[0]
    ma, he_so, nam0 = MA[ten]

    def co_tick(thang: pd.Timestamp) -> str | None:
        for d in pd.date_range(thang, thang + pd.offsets.MonthEnd(0), freq="B")[:: 3]:
            for h in (10, 14):
                b = lay(URL.format(ma=ma, y=d.year, m0=d.month - 1, d=d.day, h=h), dt_)
                if b:
                    return d.strftime("%Y-%m-01")
        return None

    thang = list(pd.date_range(f"{nam0}-01-01", pd.Timestamp.today(), freq="MS"))
    # tìm nhị phân trên tháng (giả định có dữ liệu liên tục sau ngày đầu)
    lo, hi = 0, len(thang) - 1
    if not co_tick(thang[hi - 1]):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if co_tick(thang[mid]):
            hi = mid
        else:
            lo = mid + 1
    bd = thang[lo].strftime("%Y-%m-%d")
    with _db_khoa:
        c.execute("INSERT OR REPLACE INTO bat_dau VALUES (?,?)", (ten, bd))
        c.commit()
    print(f"{dt.datetime.now():%F %T} {ten}: tháng đầu có tick = {bd}", flush=True)
    return bd


def tai_ngay(ten: str, ngay: pd.Timestamp, dt_: BoDieuToc, c) -> bool:
    ma, he_so, _ = MA[ten]
    phan = []
    gio_list = range(24)
    for h in gio_list:
        g = ngay + pd.Timedelta(hours=h)
        b = lay(URL.format(ma=ma, y=g.year, m0=g.month - 1, d=g.day, h=h), dt_)
        if b is None:
            print(f"{dt.datetime.now():%F %T} {ten} {ngay:%F} {h}h lỗi bền -> để lần sau", flush=True)
            return False
        try:
            tk = giai_ma_tick(b, g, he_so)
        except lzma.LZMAError:
            print(f"{dt.datetime.now():%F %T} {ten} {ngay:%F} {h}h bi5 hỏng -> để lần sau", flush=True)
            return False
        if len(tk):
            phan.append(tk)
    m1 = gom_m1(pd.concat(phan)) if phan else gom_m1(pd.DataFrame(columns=["bid", "ask"]))
    so_tick = int(m1["so_tick"].sum()) if len(m1) else 0
    if len(m1):
        f = GOC / "_ngay" / ten / f"{ngay:%Y-%m-%d}.parquet"
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        m1.to_parquet(tmp, compression="zstd")
        tmp.replace(f)
    ghi_xong(c, ten, f"{ngay:%Y-%m-%d}", len(m1), so_tick)
    return True


def gom_nam(ten: str, chi_nam_xong: bool = True) -> None:
    """Gộp file ngày vào m1/{ten}/{ten}_{nam}.parquet (nối với file năm đã có)."""
    d = GOC / "_ngay" / ten
    if not d.exists():
        return
    theo_nam: dict[int, list[Path]] = {}
    for f in sorted(d.glob("*.parquet")):
        theo_nam.setdefault(int(f.name[:4]), []).append(f)
    for nam, fs in theo_nam.items():
        ra = GOC / "m1" / ten / f"{ten}_{nam}.parquet"
        ra.parent.mkdir(parents=True, exist_ok=True)
        phan = [pd.read_parquet(ra)] if ra.exists() else []
        phan += [pd.read_parquet(f) for f in fs]
        df = pd.concat(phan)
        df = df[~df.index.duplicated(keep="last")].sort_index()
        tmp = ra.with_suffix(".tmp")
        df.to_parquet(tmp, compression="zstd", compression_level=9)
        tmp.replace(ra)
        for f in fs:
            f.unlink()


def o_trong_gb() -> float:
    return shutil.disk_usage(GOC).free / 1e9


def chay(ds_ma, tu, den, luong):
    dt_ = BoDieuToc(luong)
    c = mo_db()
    den = pd.Timestamp(den or (pd.Timestamp.utcnow().tz_localize(None).normalize() - pd.Timedelta(days=1)))
    for ten in ds_ma:
        bd = tu or do_bat_dau(c, ten, dt_)
        if bd is None:
            print(f"{ten}: không dò được ngày bắt đầu (server chặn hoặc mã sai) -> bỏ qua lượt này", flush=True)
            continue
        xong = da_xong(c, ten)
        ngay = [d for d in pd.date_range(bd, den, freq="D")
                if d.weekday() != 5 and f"{d:%Y-%m-%d}" not in xong][::-1]   # mới -> cũ
        print(f"{dt.datetime.now():%F %T} {ten}: còn {len(ngay)} ngày ({bd} -> {den:%F})", flush=True)
        t0, n_ok = time.time(), 0
        with ThreadPoolExecutor(max_workers=luong) as ex:
            for i, ok in enumerate(ex.map(lambda d: tai_ngay(ten, d, dt_, c), ngay)):
                n_ok += ok
                if i % 50 == 49:
                    toc = (i + 1) / (time.time() - t0) * 86400
                    print(f"{dt.datetime.now():%F %T} {ten}: {i+1}/{len(ngay)} ngày, {toc:.0f} ngày/24h, "
                          f"đếm={dt_.dem}, luồng={dt_.hien}, ổ trống={o_trong_gb():.1f}GB", flush=True)
                    if o_trong_gb() < 15:
                        print("Ổ trống < 15 GB -> DỪNG", flush=True)
                        ex.shutdown(cancel_futures=True)
                        gom_nam(ten)
                        sys.exit(2)
        gom_nam(ten)
        print(f"{dt.datetime.now():%F %T} {ten}: XONG lượt ({n_ok}/{len(ngay)} ngày ok)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ma", nargs="*", default=list(MA))
    ap.add_argument("--tu")
    ap.add_argument("--den")
    ap.add_argument("--luong", type=int, default=8)
    ap.add_argument("--mot_luot", action="store_true")
    a = ap.parse_args()
    while True:
        chay(a.ma, a.tu, a.den, a.luong)
        if a.mot_luot:
            break
        print(f"{dt.datetime.now():%F %T} hết lượt; chạy lại sau 1 giờ để lấp ngày lỗi/ngày mới", flush=True)
        time.sleep(3600)
