# -*- coding: utf-8 -*-
"""kham_pha_sau.py - TU KHAM PHA NGUON + DOC SAU (deep crawl) cho SEEKER (13/10/2026).

Tu moi nguon doc duoc, di theo: link ra ngoai, trang tac gia/ho so, thread/repo lien quan,
phan trang va binh luan -> ung vien nguon moi. Cham diem, khu trung, tu them vao
config/nguon_seeker.json (tu_sinh=true, trang_thai THU) + hang doi data/nguon_seeker/HANG_DOI_KHAM_PHA.json.
Gioi han: do sau (`sau`), ngan sach trang (`ngan_sach`), thoi gian (`giay`), >= NHIP_GIAY / ten mien.
Quet lai dinh ky cac nguon dang theo doi: config/nguon_theo_doi.json (`chu_ky_gio`, mac dinh 24).

LUAT CUNG: CHI DOC (+ follow lam tay/duoc phep). Khong dang bai, khong like, khong nhan tin,
khong tham gia nhom. Khong luu cookie/mat khau/phien. Khong sao chep ma nguon ben thu ba - chi URL.
Trang lay qua `lay(url) -> (html_or_text, links[(chu, href)])` tiem vao: CDP (Chrome may nha) hoac HTTP.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

LAB = Path(__file__).resolve().parent.parent
SO_DANG_KY = LAB / "config" / "nguon_seeker.json"
THEO_DOI = LAB / "config" / "nguon_theo_doi.json"
HANG_DOI = LAB / "data" / "nguon_seeker" / "HANG_DOI_KHAM_PHA.json"
NHIP_GIAY = 4.0

_THEO_DOI_QS = re.compile(r"^(utm_|fbclid|gclid|ref$|ref_src|s$|si$|mc_|igshid)", re.I)
_BO_MIEN = re.compile(r"(google\.|gstatic|doubleclick|facebook\.com/(sharer|dialog|tr)|"
                      r"twitter\.com/intent|x\.com/intent|apple\.com|microsoft\.com|cloudflare|"
                      r"cookie|privacy|onetrust|adservice|amazon-adsystem)", re.I)
#: Trang cua chinh tai khoan du an (khong phai nguon).
_TAI_KHOAN_RIENG = re.compile(r"thebrainago|thebrainalgo|vanhvanhvanh|/(user|account|settings|portfolio|dashboard|notifications)\b", re.I)
_BO_DUONG = re.compile(r"/(login|signin|signup|register|logout|cart|checkout|privacy|terms|"
                       r"cookies?|contact|about|help|advertis|careers|password)\b", re.I)

LOAI = [
    ("ma", re.compile(r"github\.com/[^/]+/[^/]+|gitlab\.com/|\.mq[45h]\b|\.ex[45]\b|pastebin\.com|"
                      r"tradingview\.com/script|mql5\.com/\w+/code/\d+", re.I)),
    ("phan_trang", re.compile(r"[?&](page|p|start|offset)=\d+|/page[-/]?\d+|/p\d+$|#comments?|/comments?\b", re.I)),
    ("tac_gia", re.compile(r"/(members?|users?|u|profile|author|traders?|leaders?|darwins?|people)/[^/?#]+|"
                           r"(x|twitter)\.com/[A-Za-z0-9_]{2,15}/?$|t\.me/[A-Za-z0-9_]{4,}|youtube\.com/@", re.I)),
    ("bai", re.compile(r"/(thread|threads|topic|t|post|posts|status|systems?|strategy|strategies|details|"
                       r"code|article|blog|research|papers?)/", re.I)),
]
TU_KHOA = re.compile(r"strateg|system|backtest|rule|entry|exit|stop.?loss|take.?profit|indicator|ea\b|"
                     r"expert advisor|robot|algo|quant|mean.?rev|trend|breakout|grid|scalp|carry|rsi|"
                     r"macd|bollinger|atr|ichimoku|drawdown|sharpe|profit factor|win.?rate|track.?record|"
                     r"signal|portfolio|chien luoc|he thong", re.I)
DIEM_LOAI = {"ma": 3.0, "tac_gia": 2.0, "bai": 1.5, "phan_trang": 1.0, "ngoai": 1.0}


def chuan_hoa(url: str) -> str:
    """Khoa khu trung: host thuong, bo www, bo fragment (tru #comments), bo tham so theo doi, bo '/' cuoi."""
    try:
        u = urlparse(url.strip())
    except Exception:
        return ""
    if u.scheme not in ("http", "https") or not u.netloc:
        return ""
    host = u.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    q = urlencode([(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not _THEO_DOI_QS.match(k)])
    path = re.sub(r"/+$", "", u.path) or "/"
    return urlunparse(("https", host, path, "", q, ""))


def mien(url: str) -> str:
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def phan_loai(url: str, goc: str) -> str | None:
    """Loai lien ket so voi trang goc; None = bo qua."""
    if (not chuan_hoa(url) or _BO_MIEN.search(url) or _BO_DUONG.search(urlparse(url).path)
            or _TAI_KHOAN_RIENG.search(url)):
        return None
    for ten, rx in LOAI:
        if rx.search(url):
            return ten
    return "ngoai" if mien(url) != mien(goc) else None


def cham_diem(url: str, chu: str, loai: str, sau: int = 0) -> float:
    """Diem = trong so loai + tu khoa trong chu/URL, giam theo do sau."""
    d = DIEM_LOAI.get(loai, 0.5)
    d += 0.7 * min(3, len(TU_KHOA.findall(f"{chu} {url}")))
    return round(d / (1 + 0.5 * sau), 3)


class KhamPha:
    """BFS co gioi han. `lay(url)` tra ve (text, [(chu, href), ...]) hoac raise."""

    def __init__(self, lay, sau: int = 2, ngan_sach: int = 60, giay: float = 900.0,
                 nhip: float = NHIP_GIAY, diem_toi_thieu: float = 1.5, ngu=time.sleep, dong_ho=time.time):
        self.lay, self.sau, self.ngan_sach, self.giay = lay, sau, ngan_sach, giay
        self.nhip, self.diem_toi_thieu, self.ngu, self.dong_ho = nhip, diem_toi_thieu, ngu, dong_ho
        self.da_xem: set[str] = set()
        self.ung_vien: dict[str, dict] = {}
        self.trang: list[dict] = []
        self._lan_cuoi: dict[str, float] = {}

    def _cho(self, url):
        m = mien(url); t = self._lan_cuoi.get(m)
        if t is not None:
            con = self.nhip - (self.dong_ho() - t)
            if con > 0:
                self.ngu(con)
        self._lan_cuoi[m] = self.dong_ho()

    def chay(self, hat: list[str]) -> dict:
        t0 = self.dong_ho()
        hang = [(chuan_hoa(u), u, 0, None) for u in hat if chuan_hoa(u)]
        while hang and len(self.trang) < self.ngan_sach and self.dong_ho() - t0 < self.giay:
            hang.sort(key=lambda x: -(self.ung_vien.get(x[0], {}).get("diem", 99)))
            khoa, url, d, cha = hang.pop(0)
            if khoa in self.da_xem:
                continue
            self.da_xem.add(khoa)
            self._cho(url)
            try:
                text, links = self.lay(url)
            except Exception as e:
                self.trang.append({"url": url, "sau": d, "loi": str(e)[:120]})
                continue
            self.trang.append({"url": url, "sau": d, "cha": cha, "do_dai": len(text or ""),
                               "so_tu_khoa": len(TU_KHOA.findall(text or ""))})
            for chu, href in links or []:
                loai = phan_loai(href, url)
                k = chuan_hoa(href)
                if not loai or not k or k in self.da_xem:
                    continue
                dm = cham_diem(href, chu or "", loai, d)
                cu = self.ung_vien.get(k)
                if cu:
                    cu["so_lan"] += 1
                    cu["diem"] = round(max(cu["diem"], dm) + 0.2, 3)
                    continue
                self.ung_vien[k] = {"url": href, "khoa": k, "loai": loai, "diem": dm, "chu": (chu or "")[:120],
                                    "tu": url, "sau": d + 1, "so_lan": 1, "mien": mien(href)}
                if d + 1 <= self.sau and dm >= self.diem_toi_thieu and loai != "ma":
                    hang.append((k, href, d + 1, url))
        return {"trang": self.trang, "ung_vien": sorted(self.ung_vien.values(), key=lambda x: -x["diem"])}


def _doc(p: Path, mac_dinh):
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return mac_dinh


def _ghi(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def khoa_nguon(url: str) -> str:
    """Khoa NGUON (khac khoa trang): bo query/fragment, bo /page-N, /post-N; thread forum gom ve thread goc."""
    k = chuan_hoa(url)
    if not k:
        return ""
    u = urlparse(k)
    p = re.sub(r"/(page|p)[-/]?\d+$", "", u.path)
    p = re.sub(r"(/thread/\d+)[^/]*.*$", r"\1", p)
    p = re.sub(r"/thread/post/\d+$", "/thread/post", p)
    return urlunparse(("https", u.netloc, p or "/", "", "", ""))


def _ma_nguon(uv: dict) -> str:
    kn = khoa_nguon(uv["url"]) or uv["url"]
    s = re.sub(r"[^a-z0-9]+", "_", (mien(kn) + urlparse(kn).path).lower()).strip("_")
    return ("tu_" + s)[:64]


def them_vao_so(ung_vien: list[dict], so: Path = SO_DANG_KY, hang_doi: Path = HANG_DOI,
                diem_toi_thieu: float = 2.5, toi_da: int = 50, bay_gio: str | None = None) -> dict:
    """Them ung vien dat diem (khong phai link ma) vao so dang ky + hang doi; khu trung theo khoa chuan hoa."""
    d = _doc(so, {"nguon": {}})
    d.setdefault("nguon", {})
    da_co = {khoa_nguon(v.get("url", "")) for v in d["nguon"].values()}
    hd = _doc(hang_doi, {"muc": []})
    hd_co = {m.get("khoa") for m in hd["muc"]}
    bay_gio = bay_gio or time.strftime("%Y-%m-%d %H:%M")
    them, xep = [], []
    for uv in ung_vien:
        if uv["khoa"] not in hd_co:
            hd["muc"].append({**uv, "luc": bay_gio}); hd_co.add(uv["khoa"]); xep.append(uv["khoa"])
        kn = khoa_nguon(uv["url"])
        if (len(them) >= toi_da or uv["loai"] in ("ma", "phan_trang") or uv["diem"] < diem_toi_thieu
                or kn in da_co or kn.endswith("/thread/post")):
            continue
        ma = _ma_nguon(uv)
        i = 2
        while ma in d["nguon"]:
            ma = f"{_ma_nguon(uv)[:60]}_{i}"; i += 1
        d["nguon"][ma] = {"ten": uv.get("chu") or ma, "url": kn, "loai": uv["loai"],
                          "cach": "trinh_duyet", "can_dang_nhap": False, "tu_sinh": True,
                          "trang_thai": "THU", "diem_kham_pha": uv["diem"], "tu_nguon": uv["tu"],
                          "them_luc": bay_gio, "chu_ky_gio": 168}
        da_co.add(kn); them.append(ma)
    if them:
        d["tong"] = len(d["nguon"])
        _ghi(so, d)
    _ghi(hang_doi, hd)
    return {"them_so": them, "them_hang_doi": len(xep)}


def den_han_quet_lai(theo_doi: Path = THEO_DOI, bay_gio: float | None = None) -> list[dict]:
    """Nguon dang theo doi da qua `chu_ky_gio` ke tu lan quet cuoi."""
    bay_gio = time.time() if bay_gio is None else bay_gio
    ds = _doc(theo_doi, {"nguon": []}).get("nguon", [])
    return [n for n in ds if bay_gio - float(n.get("quet_cuoi", 0)) >= 3600 * float(n.get("chu_ky_gio", 24))]


def danh_dau_da_quet(urls: list[str], theo_doi: Path = THEO_DOI, bay_gio: float | None = None) -> None:
    d = _doc(theo_doi, {"nguon": []})
    k = {chuan_hoa(u) for u in urls}
    for n in d.get("nguon", []):
        if chuan_hoa(n.get("url", "")) in k:
            n["quet_cuoi"] = time.time() if bay_gio is None else bay_gio
    _ghi(theo_doi, d)
