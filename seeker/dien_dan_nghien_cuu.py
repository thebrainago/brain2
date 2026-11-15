# -*- coding: utf-8 -*-
"""Chẩn đoán 6 diễn đàn / bảng xếp hạng đã có trong sổ. Không thu thập, không xếp việc.

Mỗi nguồn tối đa 2 lần đọc (robots.txt rồi một trang). HTTP 200 mà không ra URL
bài/hồ sơ là parser chưa chạy được, không phải nguồn sống. Host đã chặn không gọi.

    python -m seeker.dien_dan_nghien_cuu
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from nhan.nguon_seeker import QuyTacRobots
from seeker.phan_loai_loi import phan_loai_http

GOC = Path(__file__).resolve().parents[1]
RA = GOC / "reports" / "seeker_nguon" / "DIEN_DAN_NC.json"
RA_DOT2 = GOC / "reports" / "seeker_nguon" / "DIEN_DAN_DOT2.json"
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
# Đợt 2: sáu nguồn trong sổ chưa đo ở đợt 1. Cùng một miền chỉ một URL.
# etoro trong sổ trỏ /sapi/ — không gọi API không có tài liệu.
NGUON_DOT2 = (
    {"id": "signalstart", "url": "https://www.signalstart.com/search-signals", "nhom": "lich_su_tai_khoan"},
    {"id": "fxblue", "url": "https://www.fxblue.com/users", "nhom": "lich_su_tai_khoan"},
    {"id": "gogojungle", "url": "https://www.gogojungle.co.jp/systemtrade/fx", "nhom": "xep_hang"},
    {"id": "duplitrade", "url": "https://www.duplitrade.com/", "nhom": "copy_trading"},
    {"id": "fxstat", "url": "https://www.fxstat.com/", "nhom": "lich_su_tai_khoan"},
    {"id": "fxon", "url": "https://fx-on.com/", "nhom": "xep_hang"},
)
KHONG_GOI = (
    {"id": "etoro", "url": "https://www.etoro.com/sapi/rankings/rankings/",
     "ly_do": "URL trong sổ là đường /sapi/, không phải trang xếp hạng có tài liệu. Không gọi."},
)
_HREF = re.compile(r'href=["\']([^"\'#]+)', re.I)


def host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def khoa_mien(nguon_id: str, url: str) -> str:
    """Một sàn = một khóa. Trang chủ, danh sách và bài không thành ba nguồn."""
    h = host(url).removeprefix("www.")
    i = nguon_id or ""
    if h in ("traderviet.com", "traderviet.tv") or i.startswith("traderviet"):
        return "traderviet"
    if i == "fxon" or h == "fx-on.com":
        return "gogojungle.co.jp"
    if "myfxbook" in i or h.endswith("myfxbook.com"):
        return "myfxbook.com"
    if "forexfactory" in i or h.endswith("forexfactory.com"):
        return "forexfactory.com"
    if i in ("mql5_forum_ru", "tqtj_ru"):
        return "mql5.com/forum"
    if i in ("fxblue", "fxblue_com", "fxblue_market") or h.endswith("fxblue.com"):
        return "fxblue.com"
    if "darwinex" in i or "darwinex" in h:
        return "darwinex.com"
    if "zulutrade" in i or h.endswith("zulutrade.com"):
        return "zulutrade.com"
    if i in ("ctrader_copy", "ctrader_algo") or h == "ctrader.com" or h.endswith(".ctrader.com"):
        return "ctrader.com"
    if h.endswith("quantconnect.com") or i.startswith("quantconnect"):
        return "quantconnect.com"
    if h.endswith("reddit.com") or i.startswith("reddit_"):
        return "reddit.com"
    if h.endswith("smart-lab.ru") or i.startswith("smartlab"):
        return "smart-lab.ru"
    if h in ("x.com", "twitter.com") or i == "x" or i.startswith("x_"):
        return "x.com"
    if "collective2" in i or "collective2" in h:
        return "collective2.com"
    if "elitetrader" in i or h.endswith("elitetrader.com"):
        return "elitetrader.com"
    if "babypips" in i or h.endswith("babypips.com"):
        return "babypips.com"
    if "exness" in i or "exness" in h:
        return "exness.com"
    return h or i


def bi_cam(url: str) -> bool:
    return host(url) in HOST_CAM


def _tuyet(base: str, href: str) -> str:
    return urljoin(base, href).split("#")[0]


def rut_lien_ket(html: str, base: str, nguon_id: str) -> list[dict]:
    """URL bài hoặc hồ sơ. Trang chỉ mục không tính."""
    thay, ra = set(), []
    for href in _HREF.findall(html or ""):
        u = html_lib.unescape(_tuyet(base, href))
        u = u.split("#")[0].split("?")[0]
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
        elif nguon_id == "signalstart" and re.search(r"signalstart\.com/analysis/[^/]+/\d+$", u):
            giu = True
        elif nguon_id == "fxblue" and re.search(r"fxblue\.com/users/[A-Za-z0-9_.-]{2,}$", u):
            giu = True
        elif nguon_id == "gogojungle" and re.search(
                r"gogojungle\.co\.jp/(?:[a-z]{2}/)?systemtrade/fx/\d+$", u):
            giu = True
        elif nguon_id == "fxon" and re.search(
                r"fx-on\.com/(?:[a-z]{2}/)?(?:post|systemtrade|review)/.+\d", u):
            giu = True
        elif nguon_id == "duplitrade" and re.search(
                r"duplitrade\.com/(?:en/)?(?:trader|strategy|strategies|signal)s?/[A-Za-z0-9_-]{2,}$", u, re.I):
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


def chi_la_cua_dang_nhap(html: str) -> bool:
    """Trang chỉ có form đăng nhập. Form ở đầu diễn đàn thật không tính."""
    t = html or ""
    if not re.search(r"type=[\"']password[\"']", t, re.I):
        return False
    mt = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    title = re.sub(r"<[^>]+>", " ", mt.group(1) if mt else "")
    if not re.search(r"\blog[\s-]?in\b|\bsign[\s-]?in\b|\bsign[\s-]?up\b", title, re.I):
        return False
    if re.search(r"href=[\"'][^\"']*(/analysis/|/systemtrade/fx/\d+|/(?:t|threads)/)", t, re.I):
        return False
    return True


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
    cuoi = trang.get("url_cuoi") or url
    if spec["id"] == "fxon" and host(cuoi).endswith("gogojungle.co.jp"):
        trung = rut_lien_ket(html, cuoi, "gogojungle")
        ly = "fx-on.com chuyển tới GogoJungle. Cùng một sàn, không tính nguồn mới."
        if "detailUrl" in html and not trung:
            ly += " Trang chủ không có thẻ a tới hồ sơ. Chuỗi detailUrl nằm trong JSON nhúng, không bóc."
        return {
            **_tom_tat(spec, "ok", "trung_nguon", trang.get("http"), ly,
                       0, len(html), "cao",
                       "nhận redirect, không tách thành nguồn thứ hai và không đọc JSON nhúng",
                       "dùng kết quả /systemtrade/fx của gogojungle. Không mở từng hệ.", cuoi),
            "trung_voi": "gogojungle",
            "so_ho_so_trung": len(trung),
            "khong_doc_payload": "detailUrl" in html and not trung,
        }
    lk = rut_lien_ket(html, cuoi, spec["id"])
    if not lk:
        js = bool(re.search(r"__NEXT_DATA__|data-next-head=|/_next/static/", html))
        return _tom_tat(spec, "ok", "js_can_trinh_duyet" if js else "khong_ra_url", trang.get("http"),
                        "HTTP 200 nhưng HTML tĩnh không có URL hồ sơ."
                        + (" Trang Next.js." if js else " Trang sống không có nghĩa parser chạy."),
                        0, len(html), "cao" if len(html) > 1000 else "trung",
                        "tách truy cập khỏi parser",
                        "không đọc payload JS và không gọi API riêng",
                        cuoi)
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
    ap.add_argument("--dot", type=int, default=1, choices=(1, 2))
    a = ap.parse_args(argv)
    nguon = NGUON if a.dot == 1 else NGUON_DOT2
    ra_file = RA if a.dot == 1 else RA_DOT2
    if a.khong_mang:
        print(json.dumps({"dot": a.dot, "nguon": [s["id"] for s in nguon], "khong_tao_viec": True,
                          "khong_goi": [s["id"] for s in KHONG_GOI]}, ensure_ascii=False))
        return 0
    from seeker.nhip_tai import NhipTai
    thu = "dien_dan_nc" if a.dot == 1 else "dien_dan_dot2"
    nip = NhipTai(GOC / "data" / "nguon_seeker" / thu, gian_cach=4.0)
    ra = chay(nip.lay, nguon)
    ra["dot"] = a.dot
    ra["khong_goi"] = list(KHONG_GOI)
    ra_file.parent.mkdir(parents=True, exist_ok=True)
    ra_file.write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({s["id"]: {"truy_cap": s["truy_cap"], "parser": s["parser"], "http": s["http"],
                                "so_lien_ket": s.get("so_lien_ket"), "ly_do": s.get("ly_do")}
                      for s in ra["nguon"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


