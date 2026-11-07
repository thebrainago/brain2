# -*- coding: utf-8 -*-
"""Chẩn đoán 6 diễn đàn / bảng xếp hạng đã có trong sổ. Không thu thập, không xếp việc.

Mỗi nguồn tối đa 2 lần đọc (robots.txt rồi một trang). HTTP 200 mà không ra URL
bài/hồ sơ là parser chưa chạy được, không phải nguồn sống. Host đã chặn không gọi.

    python -m seeker.dien_dan_nghien_cuu
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from nhan.nguon_seeker import QuyTacRobots
from seeker.phan_loai_loi import phan_loai_http

GOC = Path(__file__).resolve().parents[1]
RA = GOC / "reports" / "seeker_nguon" / "DIEN_DAN_NC.json"
UA = "brain2-seeker/1.0 (+https://github.com/thebrainago/brain2; doc cong khai)"
HOST_CAM = {
    "myfxbook.com", "www.myfxbook.com",
    "forexfactory.com", "www.forexfactory.com",
    "forex-station.com", "www.forex-station.com",
    "social-trading.exness.com",
    "forums.babypips.com",
    # 2026-11-07: trang diễn đàn HTTP 403 Cloudflare sau robots 200. Không gọi lại.
    "www.elitetrader.com", "elitetrader.com",
}
# Đúng URL trong config/nguon_seeker.json hoặc config/dien_dan.json (TraderViet đã chuyển .tv).
NGUON = (
    {"id": "traderviet", "url": "https://traderviet.tv/forums/he-thong-giao-dich-trading-system.11/", "nhom": "dien_dan"},
    {"id": "mql5_forum_ru", "url": "https://www.mql5.com/ru/forum", "nhom": "dien_dan"},
    {"id": "babypips_forum", "url": "https://forums.babypips.com/", "nhom": "dien_dan"},
    {"id": "darwinex", "url": "https://www.darwinex.com/data/darwin-api", "nhom": "xep_hang"},
    {"id": "zulutrade", "url": "https://www.zulutrade.com/", "nhom": "xep_hang"},
    {"id": "ctrader_copy", "url": "https://ctrader.com/copy", "nhom": "xep_hang"},
)
_HREF = re.compile(r'href=["\']([^"\'#]+)', re.I)


def host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def bi_cam(url: str) -> bool:
    return host(url) in HOST_CAM


def _tuyet(base: str, href: str) -> str:
    return urljoin(base, href).split("#")[0]


def rut_lien_ket(html: str, base: str, nguon_id: str) -> list[dict]:
    """URL bài hoặc hồ sơ. Trang chỉ mục không tính."""
    thay, ra = set(), []
    for href in _HREF.findall(html or ""):
        u = _tuyet(base, href)
        u = re.sub(r"/(?:page-?\d+|latest)/?$", "", u).rstrip("/")
        h = host(u)
        path = urlparse(u).path or ""
        giu = False
        if nguon_id == "traderviet" and re.search(r"traderviet\.(?:tv|com)/(?:t|threads)/[^/]+\.\d+", u):
            giu = True
        elif nguon_id == "mql5_forum_ru" and re.search(r"mql5\.com/(?:ru|en)/forum/\d{3,}", u):
            giu = True
        elif nguon_id == "babypips_forum" and "forums.babypips.com" in h and re.search(r"/t/[^/]+/\d+", path):
            giu = True
        elif nguon_id == "darwinex" and re.search(r"darwinex\.com/invest/[A-Za-z0-9]{2,12}/?$", u):
            giu = True
        elif nguon_id == "zulutrade" and re.search(r"zulutrade\.com/.{0,40}trader", u, re.I):
            giu = True
        elif nguon_id == "ctrader_copy" and re.search(r"ctrader\.com/(?:[a-z]{2}/)?copy/strategies?/\d+", u):
            giu = True
        if not giu or u in thay:
            continue
        thay.add(u)
        ra.append({"url": u, "nguon_id": nguon_id})
    return ra


def _tom_tat(spec: dict, truy_cap: str, parser: str, http, ly_do: str, so: int, ky_tu: int,
             do_tin: str, da_sua: str, buoc: str, url_cuoi: str | None = None) -> dict:
    return {
        "id": spec["id"], "url": spec["url"], "ngay": "2026-11-07",
        "truy_cap": truy_cap, "parser": parser, "http": http, "ky_tu": ky_tu,
        "so_lien_ket": so, "do_tin": do_tin, "da_sua": da_sua, "buoc_tiep": buoc,
        "ly_do": ly_do[:400], "url_cuoi": url_cuoi, "khong_tao_viec": True,
    }


def phan_than_bai(html: str, kieu: str) -> dict:
    """Thân bài, không phải danh sách. 200 mà không có khối bài = parser không đọc được thân."""
    t = html or ""
    title = ""
    mt = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
    if mt:
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", mt.group(1))).strip()[:180]
    if re.search(r"just a moment|cf-chl|attention required", t[:4000], re.I):
        return {"parser": "trang_chan", "so_bai": 0, "ky_tu_than": 0, "co_ngay": False, "tieu_de": title}
    khoi = []
    if kieu == "xenforo":
        khoi = re.findall(r'class="bbWrapper">(.*?)</div>', t, re.S | re.I)
    elif kieu == "mql5":
        for m in re.finditer(r'id="comment_\d+"', t):
            chunk = t[m.start():m.start() + 4000]
            cm = re.search(r'class="content"[^>]*>(.*?)</div>', chunk, re.S | re.I)
            if cm:
                khoi.append(cm.group(1))
    chu = []
    for k in khoi:
        s = re.sub(r"<[^>]+>", " ", k)
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) > 40:
            chu.append(s)
    ngay = bool(re.search(r'data-date-create="\d+|datetime="\d{4}-', t))
    if kieu == "xenforo":
        ngay = ngay or bool(re.search(r'data-time="\d{8,}"', t))
    return {
        "parser": "co_than_bai" if chu else "khong_co_than",
        "so_bai": len(chu),
        "ky_tu_than": sum(len(x) for x in chu),
        "co_ngay": ngay,
        "tieu_de": title,
    }


def _robots_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}/robots.txt"


def _robots_that(text: str) -> bool:
    """File robots thật, kể cả khi có chữ captcha trong Disallow. Trang chặn thì không."""
    t = text or ""
    if re.search(r"just a moment|cf-chl|challenge-platform", t[:2500], re.I):
        return False
    return "user-agent" in t.lower()


def doc_mot(spec: dict, lay) -> dict:
    """Một nguồn. lay(url) giống NhipTai.lay. Không đi vào bài, không tạo việc."""
    url = spec["url"]
    if bi_cam(url):
        return _tom_tat(spec, "challenge", "khong_chay", None, "host đã chặn từ trước, không gọi", 0, 0, "cao",
                        "không gọi lại", "để chủ mở trình duyệt nếu cần; box không vượt")
    rb = lay(_robots_url(url))
    rb_text = rb.get("text") or ""
    if rb.get("loai") == "challenge" and not _robots_that(rb_text):
        return _tom_tat(spec, "challenge", "khong_chay", rb.get("http"),
                        "robots hoặc host bị chặn: " + str(rb.get("ly_do") or ""), 0, 0, "cao",
                        "dừng tại robots", "không đọc trang; không đổi UA")
    if _robots_that(rb_text):
        rp = QuyTacRobots(rb_text, UA)
        if not rp.can_fetch(UA, url):
            return _tom_tat(spec, "robots", "khong_chay", 200, "robots.txt cấm URL này", 0, 0, "cao",
                            "tôn trọng Disallow", "không đọc trang")
    trang = lay(url)
    if trang.get("loai") != "ok":
        return _tom_tat(spec, trang.get("loai") or "network", "khong_chay", trang.get("http"),
                        str(trang.get("ly_do") or ""), 0, len(trang.get("text") or ""), "cao",
                        "ghi đúng loại lỗi", "không thử lại trong phiên này", trang.get("url_cuoi"))
    html = trang.get("text") or ""
    pl = phan_loai_http(200, html, url, trang.get("url_cuoi"))
    if pl["loai"] != "ok":
        return _tom_tat(spec, pl["loai"], "khong_chay", 200, pl["ly_do"], 0, len(html), "cao",
                        "200 kèm dấu chặn không tính là đọc được", "dừng", trang.get("url_cuoi"))
    lk = rut_lien_ket(html, trang.get("url_cuoi") or url, spec["id"])
    if not lk:
        return _tom_tat(spec, "ok", "khong_ra_url", trang.get("http"),
                        "HTTP 200 nhưng parser không thấy URL bài hoặc hồ sơ. Trang sống không có nghĩa parser chạy.",
                        0, len(html), "cao" if len(html) > 1000 else "trung",
                        "tách truy cập khỏi parser",
                        "bước sau mới xét HTML đã lưu; chưa xếp hạng và chưa tạo việc",
                        trang.get("url_cuoi"))
    return {
        **_tom_tat(spec, "ok", "ra_url_danh_sach", trang.get("http"),
                   "trang danh sách có URL bài/hồ sơ. Chưa mở từng bài, chưa có số lãi.",
                   len(lk), len(html), "cao", "parser danh sách",
                   "chưa đào bài. Việc nghiên cứu để đợt sau.", trang.get("url_cuoi")),
        "mau_url": [x["url"] for x in lk[:5]],
    }


def chay(lay, nguon=NGUON) -> dict:
    return {"ngay": "2026-11-07", "khong_tao_viec": True, "nguon": [doc_mot(s, lay) for s in nguon]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--khong-mang", action="store_true")
    a = ap.parse_args(argv)
    if a.khong_mang:
        print(json.dumps({"nguon": [s["id"] for s in NGUON], "khong_tao_viec": True}, ensure_ascii=False))
        return 0
    from seeker.nhip_tai import NhipTai
    nip = NhipTai(GOC / "data" / "nguon_seeker" / "dien_dan_nc", gian_cach=4.0)
    ra = chay(nip.lay)
    RA.parent.mkdir(parents=True, exist_ok=True)
    RA.write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({s["id"]: {"truy_cap": s["truy_cap"], "parser": s["parser"], "http": s["http"]}
                      for s in ra["nguon"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


