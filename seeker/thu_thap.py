# -*- coding: utf-8 -*-
"""Bộ tải lịch sự: tôn trọng robots.txt, giãn cách theo tên miền, cache đĩa, phát hiện bị chặn.
KHÔNG vượt captcha / chống bot: gặp chặn thì ghi log và bỏ qua."""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.robotparser
from pathlib import Path
import requests

UA = "BrainSeeker/2.0 (+https://github.com/thebrainago/brain2; nghien cuu, chi doc)"
DAU_HIEU_CHAN = ("cf-chl", "challenge-platform", "captcha", "Just a moment...", "Attention Required",
                 "checkpoint", "are you a robot", "Access denied")


class BiChan(Exception):
    pass


class ThuThap:
    def __init__(self, thu_muc_cache: Path, gian_cach_s: float = 3.0, het_han_cache_s: float = 6 * 3600,
                 phien=None, nhat_ky=None):
        self.cache = Path(thu_muc_cache); self.cache.mkdir(parents=True, exist_ok=True)
        self.gian_cach = gian_cach_s; self.het_han = het_han_cache_s
        self.s = phien or requests.Session(); self.s.headers["User-Agent"] = UA
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.lan_cuoi: dict[str, float] = {}
        self.nhat_ky = nhat_ky if nhat_ky is not None else []
        self.dem = {"tai": 0, "cache": 0, "robots_cam": 0, "bi_chan": 0, "loi": 0}

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

    def tai(self, url: str, kieu: str = "text") -> str | None:
        k = hashlib.sha1(url.encode()).hexdigest()
        f = self.cache / (k + ".json")
        if f.exists() and time.time() - f.stat().st_mtime < self.het_han:
            self.dem["cache"] += 1
            return json.loads(f.read_text(encoding="utf-8"))["noi_dung"]
        if not self._robots_cho_phep(url):
            self.dem["robots_cam"] += 1; self.nhat_ky.append({"url": url, "tt": "robots_cam"}); return None
        self._cho(url)
        try:
            r = self.s.get(url, timeout=25)
        except requests.RequestException as e:
            self.dem["loi"] += 1; self.nhat_ky.append({"url": url, "tt": "loi", "chi_tiet": str(e)[:200]}); return None
        txt = r.text
        if r.status_code in (403, 429, 503) or any(d in txt[:5000] for d in DAU_HIEU_CHAN):
            self.dem["bi_chan"] += 1; self.nhat_ky.append({"url": url, "tt": "bi_chan", "http": r.status_code}); return None
        if r.status_code >= 400:
            self.dem["loi"] += 1; self.nhat_ky.append({"url": url, "tt": "http", "http": r.status_code}); return None
        self.dem["tai"] += 1
        f.write_text(json.dumps({"url": url, "luc": time.time(), "noi_dung": txt}, ensure_ascii=False), encoding="utf-8")
        return txt

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
