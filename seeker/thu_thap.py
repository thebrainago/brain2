# -*- coding: utf-8 -*-
"""Bộ tải lịch sự: tôn trọng robots.txt, giãn cách theo tên miền, cache đĩa, dừng khi bị chặn.

KHÔNG vượt captcha / chống bot. 403/Cloudflare dừng cả host trong phiên (không đổi UA, không đổi IP).
429 chỉ được chờ rồi thử lại vài lần cùng UA; hết lượt thì dừng host.
`tai()` vẫn trả str hoặc None để tương thích. `tai_ro()` trả loại lỗi.
Bản cache hết hạn khi mạng lỗi là `stale`, và `tai()` không trả nó như dữ liệu mới.
"""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.robotparser
from pathlib import Path
import requests

from seeker.phan_loai_loi import phan_loai_http

UA = "BrainSeeker/2.0 (+https://github.com/thebrainago/brain2; nghien cuu, chi doc)"
DAU_HIEU_CHAN = ("cf-chl", "challenge-platform", "captcha", "Just a moment...", "Attention Required",
                 "checkpoint", "are you a robot", "Access denied")


class BiChan(Exception):
    pass


class ThuThap:
    def __init__(self, thu_muc_cache: Path, gian_cach_s: float = 3.0, het_han_cache_s: float = 6 * 3600,
                 phien=None, nhat_ky=None, ngu=time.sleep, lan_429: int = 2):
        self.cache = Path(thu_muc_cache); self.cache.mkdir(parents=True, exist_ok=True)
        self.gian_cach = gian_cach_s; self.het_han = het_han_cache_s
        self.s = phien or requests.Session(); self.s.headers["User-Agent"] = UA
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.lan_cuoi: dict[str, float] = {}
        self.nhat_ky = nhat_ky if nhat_ky is not None else []
        self.dem = {"tai": 0, "cache": 0, "robots_cam": 0, "bi_chan": 0, "loi": 0}
        self.ngu = ngu
        self.lan_429 = lan_429
        self.dung_mien: dict[str, str] = {}

    def _robots_cho_phep(self, url: str) -> bool:
        p = urllib.parse.urlsplit(url); goc = f"{p.scheme}://{p.netloc}"
        if goc not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(goc + "/robots.txt", timeout=15)
                if r.status_code >= 400:
                    rp = None          # không có robots.txt -> cho phép
                else:
                    rp.parse(r.text.splitlines())
            except requests.RequestException:
                rp = None
            self.robots[goc] = rp
        rp = self.robots[goc]
        return True if rp is None else rp.can_fetch(UA, url)

    def _cho(self, url: str):
        mien = urllib.parse.urlsplit(url).netloc
        con = self.lan_cuoi.get(mien, 0) + self.gian_cach - time.time()
        if con > 0:
            time.sleep(con)
        self.lan_cuoi[mien] = time.time()

    def _doc_cache(self, url: str) -> dict | None:
        f = self.cache / (hashlib.sha1(url.encode()).hexdigest() + ".json")
        if not f.exists():
            return None
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None
        obj["_tuoi"] = time.time() - float(obj.get("luc") or 0)
        obj["_con_han"] = obj["_tuoi"] < self.het_han
        obj["_f"] = f
        return obj

    def tai_ro(self, url: str) -> dict:
        """Kết quả có loai. Bản hết hạn khi mạng lỗi mang loai=stale, không được hiểu là đo mới."""
        host = urllib.parse.urlsplit(url).netloc
        if host in self.dung_mien:
            return {"loai": "challenge", "ly_do": "host đã dừng: " + self.dung_mien[host], "http": None,
                    "text": "", "url": url, "url_cuoi": url, "stale": False, "dung_mien": True}
        cu = self._doc_cache(url)
        if cu and cu.get("_con_han") and cu.get("loai", "ok") == "ok" and "noi_dung" in cu:
            self.dem["cache"] += 1
            return {"loai": "ok", "ly_do": "cache còn hạn", "http": cu.get("http") or 200,
                    "text": cu.get("noi_dung") or "", "url": url, "url_cuoi": cu.get("url_cuoi") or url,
                    "stale": False, "dung_mien": False, "nguon": "cache"}
        if not self._robots_cho_phep(url):
            self.dem["robots_cam"] += 1
            self.nhat_ky.append({"url": url, "tt": "robots_cam", "loai": "robots"})
            return {"loai": "robots", "ly_do": "robots.txt cấm UA này", "http": None, "text": "",
                    "url": url, "url_cuoi": url, "stale": False, "dung_mien": False}
        lan = 0
        ban = None
        while True:
            self._cho(url)
            try:
                r = self.s.get(url, timeout=25)
            except requests.RequestException as e:
                ly = f"{type(e).__name__}: {str(e)[:800]}"
                self.dem["loi"] += 1
                self.nhat_ky.append({"url": url, "tt": "loi", "loai": "network", "chi_tiet": ly[:200]})
                if cu and cu.get("noi_dung"):
                    return {"loai": "stale", "ly_do": f"mạng lỗi ({ly}); bản cache hết hạn không phải phép đo mới",
                            "http": cu.get("http"), "text": cu.get("noi_dung") or "", "url": url,
                            "url_cuoi": url, "stale": True, "dung_mien": False, "loai_ban_chup": cu.get("loai", "ok")}
                return {"loai": "network", "ly_do": ly, "http": None, "text": "", "url": url, "url_cuoi": url,
                        "stale": False, "dung_mien": False}
            txt = getattr(r, "text", "") or ""
            pl = phan_loai_http(r.status_code, txt, url, getattr(r, "url", url), content_type=getattr(getattr(r, "headers", {}), "get", lambda *_: "")("content-type") if hasattr(r, "headers") else "")
            if pl["loai"] == "challenge" and r.status_code == 429 and lan < self.lan_429:
                lan += 1
                self.ngu(min(60.0, max(self.gian_cach, 1.0) * (2 ** lan)))
                continue
            ban = pl
            ban.update(text=txt, url=url, url_cuoi=getattr(r, "url", url))
            break
        assert ban is not None
        if ban["loai"] == "challenge":
            self.dung_mien[host] = ban["ly_do"]
            self.dem["bi_chan"] += 1
            self.nhat_ky.append({"url": url, "tt": "bi_chan", "loai": "challenge", "http": ban.get("http")})
            return ban
        if ban["loai"] != "ok":
            self.dem["loi"] += 1
            self.nhat_ky.append({"url": url, "tt": ban["loai"], "loai": ban["loai"], "http": ban.get("http")})
            return ban
        self.dem["tai"] += 1
        f = self.cache / (hashlib.sha1(url.encode()).hexdigest() + ".json")
        f.write_text(json.dumps({"url": url, "luc": time.time(), "noi_dung": ban["text"], "loai": "ok",
                                 "http": ban.get("http"), "url_cuoi": ban.get("url_cuoi")}, ensure_ascii=False), encoding="utf-8")
        return ban

    def tai(self, url: str, kieu: str = "text") -> str | None:
        r = self.tai_ro(url)
        if r.get("stale") or r.get("loai") != "ok":
            return None
        return r.get("text")

    def tai_tep(self, url: str, dich: Path, toi_da_mb: float = 20) -> bool:
        """Tải tệp nhị phân (ex4/ex5/...) vào dich — chỉ dùng thư mục data/ (gitignored)."""
        if dich.exists():
            return True
        if not self._robots_cho_phep(url):
            self.dem["robots_cam"] += 1; return False
        self._cho(url)
        try:
            with self.s.get(url, timeout=60, stream=True) as r:
                if r.status_code != 200:
                    return False
                dich.parent.mkdir(parents=True, exist_ok=True)
                n = 0
                with open(dich, "wb") as o:
                    for c in r.iter_content(65536):
                        n += len(c)
                        if n > toi_da_mb * 1e6:
                            o.close(); dich.unlink(); return False
                        o.write(c)
            return True
        except requests.RequestException:
            return False
