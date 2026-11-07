# -*- coding: utf-8 -*-
"""Nhịp tải dùng chung: giãn cách, cache, lùi khi 429, chạy tiếp, dừng khi challenge.

Giới hạn (cố ý, không phải chỗ để nới khi bị chặn):
- Tối thiểu 4 giây giữa hai lần chạm cùng một host (có thể cao hơn, không thấp hơn 0 khi test tiêm đồng hồ).
- HTTP 429: chờ 2^n lần nhịp, tối đa `lan_429` lần thử thêm, cùng User-Agent. Hết lượt thì dừng host.
- HTTP 403 / captcha / Cloudflare: dừng host ngay trong phiên. Không đổi UA, không đổi IP, không tắt TLS.
- Cache còn hạn trả lại bản đã lưu và ghi `nguon=cache`.
- Mạng lỗi mà còn bản hết hạn: trả `stale`, không trả rỗng như một phép đo mới.
- `resume.json` nhớ khóa đã xong để lần sau bỏ qua, không quét lại cả kho.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlparse

from seeker.phan_loai_loi import phan_loai_http


def _host(url: str) -> str:
    return (urlparse(url).netloc or "").lower()


class NhipTai:
    def __init__(self, cache: Path, get=None, ngu=time.sleep, dong_ho=time.time,
                 gian_cach: float = 4.0, het_han: float = 6 * 3600, lan_429: int = 2):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.get = get or self._get_requests
        self.ngu = ngu
        self.dong_ho = dong_ho
        self.gian_cach = gian_cach
        self.het_han = het_han
        self.lan_429 = lan_429
        self.lan_cuoi: dict[str, float] = {}
        self.dung: dict[str, str] = {}
        self.so_mang = 0
        self.resume_path = self.cache / "resume.json"
        self._resume = set()
        if self.resume_path.exists():
            try:
                self._resume = set(json.loads(self.resume_path.read_text(encoding="utf-8")))
            except (ValueError, OSError):
                self._resume = set()

    @staticmethod
    def _get_requests(url: str) -> dict:
        import requests
        try:
            r = requests.get(url, timeout=25, allow_redirects=True, headers={
                "User-Agent": "brain2-seeker/1.0 (+https://github.com/thebrainago/brain2; doc cong khai)",
                "Accept-Language": "en;q=0.9",
            })
            return {"ma": r.status_code, "text": r.text or "", "url_cuoi": str(r.url),
                    "content_type": r.headers.get("content-type", "")}
        except Exception as e:  # noqa: BLE001 — phân loại, không nuốt
            return {"ma": None, "text": "", "url_cuoi": url, "loi": f"{type(e).__name__}: {str(e)[:800]}"}

    def _cho(self, host: str) -> None:
        cho = self.gian_cach - (self.dong_ho() - self.lan_cuoi.get(host, -1e9))
        if cho > 0:
            self.ngu(cho)
        self.lan_cuoi[host] = self.dong_ho()

    def _tep(self, url: str) -> Path:
        return self.cache / (hashlib.sha1(url.encode()).hexdigest() + ".json")

    def _doc(self, url: str) -> dict | None:
        f = self._tep(url)
        if not f.exists():
            return None
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None
        obj["tuoi"] = self.dong_ho() - float(obj.get("luc") or 0)
        obj["con_han"] = obj["tuoi"] < self.het_han
        return obj

    def _ghi(self, url: str, ban: dict) -> None:
        self._tep(url).write_text(json.dumps({
            "url": url, "luc": self.dong_ho(), "loai": ban.get("loai"), "http": ban.get("http"),
            "ly_do": ban.get("ly_do"), "text": ban.get("text") or "", "url_cuoi": ban.get("url_cuoi") or url,
        }, ensure_ascii=False), encoding="utf-8")

    def da_xong(self, khoa: str) -> bool:
        return khoa in self._resume

    def danh_dau(self, khoa: str) -> None:
        self._resume.add(khoa)
        self.resume_path.write_text(json.dumps(sorted(self._resume), ensure_ascii=False, indent=1), encoding="utf-8")

    def lay(self, url: str) -> dict:
        host = _host(url)
        if host in self.dung:
            return {"loai": "challenge", "ly_do": "host đã dừng trong phiên: " + self.dung[host],
                    "http": None, "text": "", "url": url, "url_cuoi": url, "dung_mien": True,
                    "stale": False, "nguon": "dung", "khong_goi": True}
        cu = self._doc(url)
        if cu and cu.get("con_han") and cu.get("loai") in ("ok", "no_data", "auth", "challenge", "robots", "parse"):
            return {**cu, "stale": False, "nguon": "cache", "dung_mien": cu.get("loai") == "challenge", "khong_goi": True}
        self._cho(host)
        lan = 0
        ban = None
        while True:
            self.so_mang += 1
            try:
                raw = self.get(url)
            except Exception as e:  # noqa: BLE001
                raw = {"ma": None, "text": "", "url_cuoi": url, "loi": f"{type(e).__name__}: {str(e)[:800]}"}
            ban = phan_loai_http(raw.get("ma"), raw.get("text") or "", url, raw.get("url_cuoi"),
                                 raw.get("loi"), raw.get("content_type") or "")
            ban.update(text=raw.get("text") or "", url=url, url_cuoi=raw.get("url_cuoi") or url, nguon="mang")
            if ban["loai"] == "challenge" and ban.get("http") == 429 and lan < self.lan_429:
                lan += 1
                self.ngu(min(60.0, max(self.gian_cach, 1.0) * (2 ** lan)))
                self.lan_cuoi[host] = self.dong_ho()
                continue
            break
        assert ban is not None
        if ban["loai"] == "challenge":
            self.dung[host] = ban["ly_do"]
            self._ghi(url, {**ban, "text": ""})
            return ban
        if ban["loai"] == "network" and cu:
            return {"loai": "stale", "loai_ban_chup": cu.get("loai"), "text": cu.get("text") or "",
                    "http": cu.get("http"), "url": url, "url_cuoi": cu.get("url_cuoi") or url,
                    "ly_do": f"mạng lỗi ({ban['ly_do']}); dùng bản chụp hết hạn, không phải phép đo mới",
                    "stale": True, "dung_mien": False, "nguon": "stale", "khong_goi": False}
        if ban["loai"] in ("ok", "no_data", "auth", "parse", "robots"):
            self._ghi(url, ban)
        return ban
