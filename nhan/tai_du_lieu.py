# -*- coding: utf-8 -*-
"""tai_du_lieu.py - tai du lieu gia DAI (2000..2026) LICH SU, mot luong, lich su, co resume + cache (21/10/2026, Grok Bot).

Nguon (cong khai, khong dang nhap, khong vuot chong bot):
  * histdata.com  : M1 ASCII bid, gio EST CO DINH (UTC-5, khong DST). Form tai binh thuong cua trang (POST get.php voi tk an
                    trong trang), nguoi dung da cho phep 21/10/2026. Nam cu = 1 zip/nam, nam hien tai = 1 zip/thang.
  * Dukascopy     : datafeed cong khai, nen phut BID + ASK theo ngay (.bi5 = LZMA) -> SPREAD lich su theo gio/nam.
                    Ton trong 429/503: lui theo cap so nhan (Retry-After neu co), 1 luong, nghi dai. Lay MAU (vai ngay/thang).
Moi tep tho luu o data/du_lieu_dai/ (git bo qua). Trang thai: data/du_lieu_dai/trang_thai_<nguon>.json (tep da co = bo qua).
Chay nen:  nohup python3 -m nhan.tai_du_lieu --tat-ca > data/du_lieu_dai/tai.log 2>&1 &
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import lzma
import random
import re
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
THU = GOC / "data" / "du_lieu_dai"
UA = "Mozilla/5.0 (X11; Linux x86_64) brain2-research (1 request at a time)"

#: 19 ma cua 78 he DAT (UNG_VIEN.md) ; GOLD = XAUUSD
MA = ["EURUSD", "GBPCAD", "GBPNZD", "EURCHF", "XAUUSD", "EURGBP", "USDCAD", "USDJPY", "CADJPY", "AUDUSD", "AUDJPY",
      "EURCAD", "GBPUSD", "CHFJPY", "NZDJPY", "EURAUD", "AUDNZD", "EURNZD", "GBPAUD"]
NAM_DAU = 2000
NGHI_HD = (6.0, 12.0)          # giay giua 2 lan tai histdata
NGHI_DK = (2.0, 4.0)           # giay giua 2 lan tai Dukascopy
LUI_MAX = 3600.0               # lui toi da 1 gio


def _tep_tt(nguon: str) -> Path:
    return THU / ("trang_thai_%s.json" % nguon)


def _tt(nguon: str) -> dict:
    try:
        return json.loads(_tep_tt(nguon).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _ghi_tt(nguon: str, d: dict) -> None:
    THU.mkdir(parents=True, exist_ok=True)
    f = _tep_tt(nguon); tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=0, sort_keys=True), encoding="utf-8"); tmp.replace(f)


def lui(lan: int, retry_after: str | None = None, goc: float = 60.0) -> float:
    """Thoi gian cho sau lan loi thu `lan` (0-based): Retry-After neu co, khong thi goc*2^lan (+-20%), tran LUI_MAX."""
    if retry_after:
        try:
            return min(max(float(retry_after), 1.0), LUI_MAX)
        except ValueError:
            pass
    return min(goc * (2 ** lan), LUI_MAX) * random.uniform(0.8, 1.2)


def _get(url: str, data: bytes | None = None, hdr: dict | None = None, cj: dict | None = None, timeout: int = 180):
    h = {"User-Agent": UA, **(hdr or {})}
    if cj:
        h["Cookie"] = "; ".join("%s=%s" % kv for kv in cj.items())
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout)
    for c in r.headers.get_all("Set-Cookie") or []:
        k, _, v = c.split(";")[0].partition("=")
        if cj is not None:
            cj[k.strip()] = v.strip()
    return r.status, r.read(), r.headers


def _lay_lui(fn, ten: str, log, toi_da: int = 8):
    """Goi fn(); 429/503/5xx/mang -> lui cap so nhan; 404 -> None. Het luot -> raise."""
    for lan in range(toi_da):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 503) or e.code >= 500:
                w = lui(lan, e.headers.get("Retry-After") if e.headers else None)
                log("  %s: HTTP %d -> chờ %.0f giây (lần %d)" % (ten, e.code, w, lan + 1)); time.sleep(w); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            w = lui(lan, None, 30.0); log("  %s: mạng %s -> chờ %.0f giây" % (ten, str(e)[:60], w)); time.sleep(w)
    raise RuntimeError("hết lượt thử: " + ten)


# ------------------------------------------------------------------------------------------------ histdata
def ky_histdata(nam_nay: int | None = None, thang_nay: int | None = None) -> list[str]:
    """'2010' (ca nam) ... nam truoc; nam hien tai: '202601'..thang truoc (thang chua xong khong tai)."""
    h = dt.date.today()
    nn, tn = nam_nay or h.year, thang_nay or h.month
    return [str(y) for y in range(NAM_DAU, nn)] + ["%d%02d" % (nn, m) for m in range(1, tn)]


def tep_histdata(ma: str, ky: str) -> Path:
    return THU / "histdata" / ("%s_M1_%s.zip" % (ma, ky))


def tai_histdata(ma: str, ky: str, log=print) -> str:
    f = tep_histdata(ma, ky)
    if f.exists():
        return "CO_SAN"
    nam, thang = ky[:4], ky[4:]
    trang = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/%s/%s%s" % (
        ma.lower(), nam, ("/" + str(int(thang))) if thang else "")
    cj: dict = {}

    def buoc():
        _, html, _ = _get(trang, cj=cj)
        html = html.decode("utf-8", "ignore")
        tk = re.search(r'name="tk" id="tk" value="([0-9a-f]+)"', html)
        if not tk or ("fxpair" not in html):
            return b""
        form = {"tk": tk.group(1), "date": nam, "datemonth": ky, "platform": "ASCII", "timeframe": "M1", "fxpair": ma.upper()}
        _, z, _ = _get("https://www.histdata.com/get.php", data=urllib.parse.urlencode(form).encode(),
                       hdr={"Referer": trang, "Content-Type": "application/x-www-form-urlencoded"}, cj=cj, timeout=600)
        return z

    z = _lay_lui(buoc, "histdata %s %s" % (ma, ky), log)
    if not z or z[:2] != b"PK":
        return "KHONG_CO"
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".part"); tmp.write_bytes(z)
    try:
        with zipfile.ZipFile(tmp) as zz:
            if not any(n.endswith(".csv") for n in zz.namelist()):
                tmp.unlink(); return "KHONG_CO"
    except zipfile.BadZipFile:
        tmp.unlink(); return "HONG"
    tmp.replace(f)
    return "OK"


# ------------------------------------------------------------------------------------------------ Dukascopy
DK_HE_SO = {"JPY": 1e3, "XAUUSD": 1e3}


def he_so_dk(ma: str) -> float:
    return DK_HE_SO.get(ma, DK_HE_SO["JPY"] if ma.endswith("JPY") else 1e5)


def ngay_mau_dk(nam_dau: int = 2004, den: dt.date | None = None) -> list[dt.date]:
    """2 ngay giua tuan moi thang (thu Ba + thu Tu sau ngay 8) -> mau spread theo gio x nam."""
    den = den or dt.date.today() - dt.timedelta(days=3)
    ra = []
    for y in range(nam_dau, den.year + 1):
        for m in range(1, 13):
            d = dt.date(y, m, 8)
            while d.weekday() != 1:
                d += dt.timedelta(days=1)
            for x in (d, d + dt.timedelta(days=1)):
                if x <= den:
                    ra.append(x)
    return ra


def tep_dk(ma: str, ngay: dt.date, ben: str) -> Path:
    return THU / "duka" / ma / ("%s_%s_m1.bi5" % (ngay.isoformat(), ben))


def tai_dk(ma: str, ngay: dt.date, ben: str, log=print) -> str:
    f = tep_dk(ma, ngay, ben)
    if f.exists() or f.with_suffix(".rong").exists():
        return "CO_SAN"
    url = "https://datafeed.dukascopy.com/datafeed/%s/%04d/%02d/%02d/%s_candles_min_1.bi5" % (
        ma, ngay.year, ngay.month - 1, ngay.day, ben)
    b = _lay_lui(lambda: _get(url)[1], "duka %s %s %s" % (ma, ngay, ben), log, toi_da=10)
    f.parent.mkdir(parents=True, exist_ok=True)
    if not b:
        f.with_suffix(".rong").write_text(""); return "KHONG_CO"
    f.write_bytes(b)
    return "OK"


def doc_bi5_nen(b: bytes, ngay: dt.date, he_so: float) -> list[tuple]:
    """bi5 nen phut: moi ban ghi 24 byte >iiiiif (giay tu 00:00 UTC, open, close, low, high, volume)."""
    if not b:
        return []
    raw = lzma.decompress(b)
    t0 = dt.datetime(ngay.year, ngay.month, ngay.day)
    ra = []
    for i in range(0, len(raw) - 23, 24):
        s, o, c, lo, hi, v = struct.unpack(">iiiiif", raw[i:i + 24])
        ra.append((t0 + dt.timedelta(seconds=s), o / he_so, hi / he_so, lo / he_so, c / he_so, v))
    return ra


# ------------------------------------------------------------------------------------------------ dieu phoi
def chay(ma: list[str], histdata: bool = True, duka: bool = True, log=print) -> dict:
    tt = {"histdata": _tt("histdata"), "duka": _tt("duka")}
    if histdata:
        for k in ky_histdata():
            for m in ma:
                key = "%s_%s" % (m, k)
                if tt["histdata"].get(key) in ("OK", "KHONG_CO") or tep_histdata(m, k).exists():
                    continue
                try:
                    r = tai_histdata(m, k, log)
                except Exception as e:                       # ghi lai, di tiep (lan sau thu lai)
                    r = "LOI: " + str(e)[:80]
                tt["histdata"][key] = r; _ghi_tt("histdata", tt["histdata"])
                log("histdata %s %s -> %s" % (m, k, r))
                if r != "CO_SAN":
                    time.sleep(random.uniform(*NGHI_HD))
    if duka:
        for d in ngay_mau_dk():
            for m in ma:
                for ben in ("BID", "ASK"):
                    key = "%s_%s_%s" % (m, d, ben)
                    if tt["duka"].get(key) in ("OK", "KHONG_CO"):
                        continue
                    try:
                        r = tai_dk(m, d, ben, log)
                    except Exception as e:
                        r = "LOI: " + str(e)[:80]
                    tt["duka"][key] = r if r != "CO_SAN" else "OK"; _ghi_tt("duka", tt["duka"])
                    if r != "CO_SAN":
                        log("duka %s %s %s -> %s" % (m, d, ben, r)); time.sleep(random.uniform(*NGHI_DK))
    return tt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ma", nargs="*", default=MA)
    ap.add_argument("--tat-ca", action="store_true")
    ap.add_argument("--chi-histdata", action="store_true")
    ap.add_argument("--chi-duka", action="store_true")
    a = ap.parse_args(argv)
    chay(a.ma, histdata=not a.chi_duka, duka=not a.chi_histdata, log=lambda s: print(time.strftime("%H:%M:%S"), s, flush=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
