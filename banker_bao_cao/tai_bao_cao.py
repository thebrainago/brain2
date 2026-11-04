# -*- coding: utf-8 -*-
"""Tải PDF báo cáo tổ chức, trích văn bản bằng pdftotext, ghi chỉ mục nguon.json.

Dùng: python banker_bao_cao/tai_bao_cao.py <url> --ky 2026-11_Q4 [--to-chuc SC] [--ngay 2026-10-30] [--giu-pdf]
"""
import argparse
import json
import os
import subprocess
import urllib.request
from datetime import date
from urllib.parse import urlparse

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bao_cao")
NGUONG_PDF = 2 * 1024 * 1024  # không giữ PDF > ~2MB trong git


def ten_tep(url):
    ten = os.path.basename(urlparse(url).path) or "bao_cao.pdf"
    return ten[:-4] if ten.lower().endswith(".pdf") else ten


def ghi_chi_muc(thu_muc, ban_ghi):
    """Thêm/cập nhật bản ghi theo url trong nguon.json."""
    duong = os.path.join(thu_muc, "nguon.json")
    ds = []
    if os.path.exists(duong):
        with open(duong, encoding="utf-8") as f:
            ds = json.load(f)
    ds = [b for b in ds if b.get("url") != ban_ghi["url"]] + [ban_ghi]
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=2)
    return ds


def tai(url, ky, to_chuc="", ngay="", giu_pdf=False, goc=GOC):
    thu_muc = os.path.join(goc, ky)
    os.makedirs(thu_muc, exist_ok=True)
    ten = ten_tep(url)
    pdf = os.path.join(thu_muc, ten + ".pdf")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(pdf, "wb") as f:
        f.write(r.read())
    with open(pdf, "rb") as f:
        if f.read(5) != b"%PDF-":
            os.remove(pdf)
            raise ValueError("Không phải PDF gốc: " + url)
    txt = os.path.join(thu_muc, ten + ".txt")
    subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)
    if not giu_pdf or os.path.getsize(pdf) > NGUONG_PDF:
        os.remove(pdf)
    return ghi_chi_muc(thu_muc, {
        "to_chuc": to_chuc, "ngay": ngay, "url": url,
        "tep_txt": os.path.basename(txt), "ngay_tai": date.today().isoformat(),
    })


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--ky", required=True)
    p.add_argument("--to-chuc", default="")
    p.add_argument("--ngay", default="")
    p.add_argument("--giu-pdf", action="store_true")
    a = p.parse_args()
    tai(a.url, a.ky, a.to_chuc, a.ngay, a.giu_pdf)
