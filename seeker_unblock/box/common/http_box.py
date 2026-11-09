#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP helpers for box egress (no secrets). Pacing + Chrome UA."""
from __future__ import annotations

import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class HttpResult:
    url: str
    status: int
    body: bytes
    final_url: str
    error: Optional[str] = None


class PacedClient:
    """Sequential GET with minimum interval between calls (anti-ban)."""

    def __init__(self, min_interval_s: float = 0.4, ua: str = DEFAULT_UA, timeout: float = 45.0):
        self.min_interval_s = min_interval_s
        self.ua = ua
        self.timeout = timeout
        self._last = 0.0

    def _pace(self) -> None:
        dt = time.monotonic() - self._last
        if dt < self.min_interval_s:
            time.sleep(self.min_interval_s - dt)

    def get(self, url: str, headers: Optional[dict] = None) -> HttpResult:
        self._pace()
        hdrs = {"User-Agent": self.ua, "Accept": "*/*"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, headers=hdrs, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read()
                self._last = time.monotonic()
                return HttpResult(url=url, status=getattr(resp, "status", 200) or 200, body=body, final_url=resp.geturl())
        except urllib.error.HTTPError as e:
            self._last = time.monotonic()
            return HttpResult(url=url, status=int(e.code), body=e.read() if e.fp else b"", final_url=url, error=str(e))
        except Exception as e:  # noqa: BLE001
            self._last = time.monotonic()
            return HttpResult(url=url, status=0, body=b"", final_url=url, error=str(e))
