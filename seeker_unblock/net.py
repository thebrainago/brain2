"""net.py - lop mang dung chung, chi cho trang CONG KHAI.
- requests thuong, User-Agent trung thuc (khong gia van tay trinh duyet, khong proxy, khong DoH lach chan).
- Nhip lich su theo host (min_gap, mac dinh 4 s) + backoff khi loi ket noi tam thoi.
- Gap 403/429/503 hoac trang chan cua Cloudflare (1015, "Access denied", "Just a moment") -> DUNG NGAY (SiteBan),
  khong thu lai, khong doi duong. Chan do trang dat ra phai duoc ton trong."""
import time, random
from urllib.parse import urlparse
import requests

UA = "brain2-seeker/1.0 (nghien cuu ca nhan; requests)"
BAN_MARKERS = ("error code: 1015", "Error 1015", "used Cloudflare to restrict access", "Just a moment", "Access denied")

class SiteBan(RuntimeError):
    """Trang chu dong chan/gioi han -> dung toan bo lan chay."""

class Net:
    def __init__(self, min_gap=4.0, tries=3, timeout=40):
        self.min_gap, self.tries, self.timeout = min_gap, tries, timeout
        self.s = requests.Session(); self.s.headers["User-Agent"] = UA
        self._last = {}
        self.stats = {"ok": 0, "loi_ket_noi": 0, "bi_chan": 0}

    def _pace(self, host):
        gap = time.time() - self._last.get(host, 0)
        if gap < self.min_gap: time.sleep(self.min_gap - gap + random.uniform(0, 1))
        self._last[host] = time.time()

    def get(self, url, **kw):
        host = urlparse(url).hostname; delay = 5; last = None
        for _ in range(self.tries):
            self._pace(host)
            try:
                r = self.s.get(url, timeout=self.timeout, **kw)
            except requests.RequestException as e:
                last = e; self.stats["loi_ket_noi"] += 1; time.sleep(delay); delay *= 2; continue
            head = r.text[:5000] if "text" in r.headers.get("content-type", "") else ""
            if r.status_code in (403, 429, 503) or any(m in head for m in BAN_MARKERS):
                self.stats["bi_chan"] += 1
                raise SiteBan(f"{host} tra {r.status_code} / trang chan -> dung, khong thu lai")
            self.stats["ok"] += 1
            return r
        raise RuntimeError(f"loi ket noi lien tiep {url}: {last}")
