#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP với curl_cffi Chrome impersonate — dùng khi Cloudflare chặn urllib thường.

Không lưu cookie. DoH Cloudflare 1.1.1.1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CfResult:
    url: str
    status: int
    text: str
    headers: dict
    error: Optional[str] = None

    @property
    def cloudflare_challenge(self) -> bool:
        return "Just a moment" in self.text or "cf-browser-verification" in self.text.lower()


def get(url: str, timeout: float = 40.0, params: Optional[dict] = None, headers: Optional[dict] = None) -> CfResult:
    from curl_cffi import requests as cr
    from curl_cffi import CurlOpt

    s = cr.Session(impersonate="chrome", curl_options={CurlOpt.DOH_URL: "https://1.1.1.1/dns-query"})
    try:
        r = s.get(url, timeout=timeout, params=params or {}, headers=headers or {})
        return CfResult(url=url, status=r.status_code, text=r.text, headers=dict(r.headers))
    except Exception as e:  # noqa: BLE001
        return CfResult(url=url, status=0, text="", headers={}, error=str(e))
