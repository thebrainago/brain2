# -*- coding: utf-8 -*-
"""nguon_seeker.py - SO DANG KY NGUON SEEKER theo 4 CHIEU PHONG CACH + QUET LICH SU (12/10/2026).

Port tu the-brain (nhanh claude/autonomous-trading-system-rzzt7h, ban giao 3c982747):
  * DANH SACH: 71 nguon dang ky + 19 dien dan quoc gia + 23 dien dan cau hinh + telegram + blog tu sinh
    + cho EA + nen tang NGUON.md -> `config/nguon_seeker.json` (sinh boi `_kiem_ke_nguon_the_brain.py`).
  * QUY TAC TU SINH NGUON (the-brain `nhan/kham_pha_nguon.py`, `config/nguon_tu_tim.json`): trang doc duoc ma
    khai `<link rel=alternate type=rss|atom>` -> ung vien RSS moi; link ra ngoai trong bai -> ung vien moi
    (`tu_sinh: true`, trang_thai THU). Ban o day CHI DOC: khong follow / join / dang ky.
  * MO RONG QUA MANG XA HOI (the-brain `tu_follow_join.py`, `seeker_theo_doi.py`): ban the-brain tu follow/join.
    O day CHI ghi ung vien (t.me/<kenh>, reddit r/<sub>, youtube @kenh, github <chu>) thay trong trang cong khai;
    KHONG theo doi, KHONG tham gia, KHONG dang nhap. Kenh Telegram cong khai doc qua trang xem truoc t.me/s/<kenh>.
  * CHU KY QUET (the-brain `config/tan_so_quet.json`, quet lai 168 gio): moi nguon co `chu_ky_gio`; trang thai
    `data/nguon_seeker/TRANG_THAI.json` (gitignore).
  * PHAN TRANG: danh sach nhieu trang di qua `nhan/doc_nhieu_trang.py` (rel_next -> mau_trang -> neo_so ->
    mau_suy_ra -> chu_tiep, con tro tung danh sach).
LUAT CUNG: ton trong robots.txt; >= 4 giay giua hai yeu cau cung ten mien; 403/429/503/captcha/Cloudflare ->
DUNG ten mien do, ghi "BI CHAN - can chay may nha" kem ly do; khong doi UA/IP, khong VPN, khong trinh duyet an,
khong gia nguoi. Phan WARP / gia nguoi cua the-brain nam o `nhan/may_nha_tuy_chon.py`, TAT mac dinh.
"""
from __future__ import annotations

import html as _h
import json
import os
import re
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse

LAB = Path(__file__).resolve().parent.parent
SO_DANG_KY = LAB / "config" / "nguon_seeker.json"
GOC = Path(os.environ.get("BRAIN_NGUON_SEEKER_DIR") or (LAB / "data" / "nguon_seeker"))
NHIP_GIAY = 4.0
UA = "brain2-seeker/1.0 (+https://github.com/thebrainago/brain2; doc cong khai, ton trong robots.txt)"
BI_CHAN = "BỊ CHẶN — cần chạy máy nhà"
CAN_DANG_NHAP = "CẦN ĐĂNG NHẬP"
ROBOTS_CAM = "ROBOTS.TXT CẤM — không đọc"
DOC_DUOC = "ĐỌC ĐƯỢC"
KHONG_URL = "CHƯA CÓ URL"
LOI_MANG = "LỖI MẠNG / HẾT HẠN"
THU_CONG = "THỦ CÔNG (chủ dự án)"

# ------------------------------------------------------------- 4 chieu ----
#: Luat CHOT TRUOC: (nhan, regex tren ten+url+ghi chu). Nguon khong khop chieu nao = 'tong_hop'.
PHONG_CACH = [
    ("xu_huong", r"trend|follow|turtle|seykota|donchian|momentum|ma.?cross|ema|supertrend|ichimoku|cta|managed.?futures|thetrend"),
    ("hoi_quy", r"mean.?rev|reversion|rsi|bollinger|z.?score|pairs|stat.?arb|meanreversion"),
    ("pha_vo", r"breakout|break.?out|range|straddle|session|london|asian"),
    ("luoi_dca", r"grid|martingale|dca|averag|hedg|basket|luoi|recovery"),
    ("luot_song", r"scalp|hft|tick|microstructure|order.?flow"),
    ("vi_mo_carry", r"macro|carry|fomc|cot\b|cftc|fred|interest|swap|vi.?mo|seasonal|mua.?vu"),
    ("hoc_may", r"machine.?learn|\bml\b|neural|deep|ai\b|paperswithcode|kaggle|numerai|forecast|huggingface"),
    ("danh_muc_factor", r"factor|portfolio|allocat|fama|asset.?alloc|smart.?beta|risk.?parity|buyandhold|passive"),
    ("tin_hieu_copy", r"signal|copy|darwin|myfxbook|fxblue|zulu|etoro|collective2|leaderboard|track.?record|ftmo|prop"),
]
TAI_SAN = [
    ("fx", r"forex|\bfx|mql|mt4|mt5|ea\b|expert|babypips|pips|myfxbook|fxblue|zulu|darwin|signalstart|traderviet|thaiforex|fx-on|note_fx|gogojungle|arabictrader|nawigator|forexfactory"),
    ("crypto", r"crypto|bitcoin|btc|binance|bybit|okx|sol|ether|defi|freqtrade"),
    ("co_phieu", r"stock|equit|s&p|sp500|smart-lab|boursorama|wallstreet|ariva|bankier|rankia|tradingqna|etoro|minervini|factor|fama"),
    ("futures_hang_hoa", r"futures|commodit|cta|gold|xau|oil|cme|cboe|managed"),
    ("chi_so", r"index|indices|us500|nasdaq|dax|vix"),
]
KHUNG = [
    ("ngan_M1_M15", r"scalp|m1\b|m5\b|m15|tick|hft|intraday|1.?min|5.?min"),
    ("trung_H1_H4", r"\bh1\b|\bh4\b|hour|swing"),
    ("dai_D1_W1", r"daily|\bd1\b|weekly|\bw1\b|position|monthly|long.?term|cta|trend.?follow|factor|alloc|seasonal|macro"),
]
QUAN_TRI = [
    ("luoi_martingale", r"grid|martingale|dca|averag|basket|recovery|luoi"),
    ("trailing_ATR", r"trail|atr|chandelier|stop"),
    ("rui_ro_co_dinh", r"risk.?%|percent.?risk|position.?siz|kelly|money.?manag|fixed.?fract"),
    ("danh_muc", r"portfolio|allocat|risk.?parity|rebalanc"),
    ("copy_theo_doi", r"signal|copy|leaderboard|track.?record"),
]

#: Truy van GitHub sinh theo phong cach (chot truoc). Moi phong cach 2-3 truy van MQL4/MQL5.
TRUY_VAN_THEO_PHONG_CACH = {
    "xu_huong": ("trend following EA language:MQL5", "moving average cross EA language:MQL4", "supertrend expert advisor mt5"),
    "hoi_quy": ("mean reversion EA language:MQL4", "rsi expert advisor language:MQL5", "bollinger bands EA mt4"),
    "pha_vo": ("breakout EA language:MQL4", "london breakout expert advisor", "donchian channel EA mql5"),
    "luoi_dca": ("grid EA language:MQL4", "martingale expert advisor mt5", "hedging EA language:MQL5"),
    "luot_song": ("scalping EA language:MQL4", "scalper expert advisor mt5"),
    "vi_mo_carry": ("carry trade EA", "news trading EA mql4"),
    "hoc_may": ("neural network expert advisor mql5", "machine learning EA language:MQL5"),
}


def _khop(bang, chu):
    return [ten for ten, rx in bang if re.search(rx, chu, re.I)]


def gan_nhan(s: dict) -> dict:
    """{'phong_cach': [...], 'tai_san': [...], 'khung': [...], 'quan_tri': [...]} theo luat tu khoa."""
    chu = " ".join(str(s.get(k) or "") for k in ("ten", "url", "ghi_chu", "loai", "tu_khoa", "mau_tim"))
    chu += " " + " ".join(s.get("seed") or [])
    return {"phong_cach": _khop(PHONG_CACH, chu) or ["tong_hop"],
            "tai_san": _khop(TAI_SAN, chu) or ["da_tai_san"],
            "khung": _khop(KHUNG, chu) or ["nhieu_khung"],
            "quan_tri": _khop(QUAN_TRI, chu) or ["khong_ro"]}


_DANG_NHAP = re.compile(r"facebook|tiktok|x\.com|darwinex\.com/(account|data)|zulutrade|collective2|myfxbook|"
                        r"etoro\.com/discover|ctrader|login|/account|api-management|/my/|dashboard|personal_token")


def can_dang_nhap(s: dict) -> bool:
    if s.get("cach") == "dang_nhap" or s.get("loai") == "api_ca_nhan":
        return True
    return bool(_DANG_NHAP.search(s.get("url") or ""))


def nap(p: Path = SO_DANG_KY) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))["nguon"]


# ------------------------------------------------------------- mang -------
class QuyTacRobots:
    """robots.txt theo RFC 9309 (kieu Google): khop TIEN TO tren duong dan + query, ho tro '*' va '$', luat DAI NHAT thang,
    bang dai thi Allow thang. Nhom theo User-agent: nhom ten trung UA (dai nhat) neu co, khong thi nhom '*'.

    20/10/2026: `urllib.robotparser` chuan hoa "Disallow: /?" thanh "Disallow: /" (urlparse bo dau '?' rong) -> coi CA
    trang web bi cam (earnforex.com bi ghi ROBOTS CAM sai). Lop nay giu nguyen y nghia: chi cam URL bat dau bang "/?"."""

    def __init__(self, van_ban: str, ua: str):
        nhom: list[tuple[list[str], list[tuple[bool, str]]]] = []
        ua_ds: list[str] = []
        luat: list[tuple[bool, str]] = []
        dang_luat = False
        for dong in (van_ban or "").splitlines():
            dong = dong.split("#", 1)[0].strip()
            if ":" not in dong:
                continue
            k, v = (x.strip() for x in dong.split(":", 1))
            k = k.lower()
            if k == "user-agent":
                if dang_luat:
                    nhom.append((ua_ds, luat)); ua_ds, luat, dang_luat = [], [], False
                ua_ds.append(v.lower())
            elif k in ("allow", "disallow"):
                dang_luat = True
                if v:                                      # "Disallow:" rong = khong cam gi
                    luat.append((k == "allow", v))
            elif k == "crawl-delay":
                dang_luat = True
                try:
                    luat.append((None, float(v)))           # (None, giay) = Crawl-delay cua nhom
                except ValueError:
                    pass
        if ua_ds:
            nhom.append((ua_ds, luat))
        ten = (ua or "").lower()
        tot, do_dai = None, -1
        for ds, l in nhom:
            for u in ds:
                if u != "*" and u and u.split("/")[0] in ten and len(u) > do_dai:
                    tot, do_dai = l, len(u)
        if tot is None:
            tot = [x for ds, l in nhom if "*" in ds for x in l]
        self.tre_giay = max([float(x[1]) for x in tot if x[0] is None] or [0.0])
        self.luat = [x for x in tot if x[0] is not None]

    @staticmethod
    def _khop(mau: str, duong: str) -> bool:
        cuoi = mau.endswith("$")
        if cuoi:
            mau = mau[:-1]
        rx = "".join(".*" if c == "*" else re.escape(c) for c in mau)
        return re.match(rx + ("$" if cuoi else ""), duong) is not None

    def can_fetch(self, ua: str, url: str) -> bool:
        p = urlparse(url)
        duong = (p.path or "/") + (("?" + p.query) if p.query else "")
        tot = None                                         # (do dai, cho_phep)
        for cho, mau in self.luat:
            if self._khop(mau, duong):
                k = (len(mau), cho)
                if tot is None or k > tot:
                    tot = k
        return True if tot is None else tot[1]


class Mang:
    """GET lich su: robots.txt, nhip theo ten mien, dung ten mien bi chan. `get` thay duoc (test)."""

    def __init__(self, get=None, ngu=time.sleep, dong_ho=time.time):
        self.get = get or self._get
        self.ngu, self.dong_ho = ngu, dong_ho
        self.lan_cuoi: dict[str, float] = {}
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.chan: dict[str, str] = {}
        self.so_yeu_cau = 0

    @staticmethod
    def _get(url, timeout=25):
        import requests
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en;q=0.9"}, timeout=timeout,
                             allow_redirects=True)
            return {"ma": r.status_code, "text": r.text or "", "url_cuoi": r.url, "loai": r.headers.get("content-type", "")}
        except Exception as e:                                    # noqa: BLE001
            return {"ma": None, "text": "", "url_cuoi": url, "loi": f"{type(e).__name__}: {str(e)[:120]}"}

    @staticmethod
    def mien(url):
        h = (urlparse(url).hostname or "").lower()
        return h[4:] if h.startswith("www.") else h

    def _cho(self, mien):
        tre = max([getattr(r, "tre_giay", 0.0) for g, r in self.robots.items() if r is not None and self.mien(g) == mien]
                  or [0.0])                         # 20/10/2026: ton trong Crawl-delay (earnforex: 10 s)
        cho = max(NHIP_GIAY, min(tre, 60.0)) - (self.dong_ho() - self.lan_cuoi.get(mien, -1e9))
        if cho > 0:
            self.ngu(cho)
        self.lan_cuoi[mien] = self.dong_ho()

    def robots_cho_phep(self, url) -> bool:
        p = urlparse(url)
        goc = f"{p.scheme}://{p.netloc}"
        if goc not in self.robots:
            self._cho(self.mien(url))
            kq = self.get(goc + "/robots.txt")
            self.so_yeu_cau += 1
            if kq.get("ma") == 200 and "<html" not in kq["text"][:500].lower():
                self.robots[goc] = QuyTacRobots(kq["text"], UA)
            else:
                self.robots[goc] = None          # khong co robots doc duoc -> cho phep
        rp = self.robots[goc]
        return True if rp is None else rp.can_fetch(UA, url)

    def lay(self, url) -> dict:
        m = self.mien(url)
        if m in self.chan:
            return {"ma": None, "text": "", "url_cuoi": url, "trang_thai": BI_CHAN, "ly_do": "ten mien da chan luot nay: " + self.chan[m]}
        if not self.robots_cho_phep(url):
            return {"ma": None, "text": "", "url_cuoi": url, "trang_thai": ROBOTS_CAM, "ly_do": "robots.txt Disallow cho UA nay"}
        self._cho(m)
        kq = self.get(url)
        self.so_yeu_cau += 1
        kq["trang_thai"], kq["ly_do"] = phan_loai(kq, url)
        if kq["trang_thai"] == BI_CHAN:
            self.chan[m] = kq["ly_do"]
        return kq


_DAU_CHAN = ("just a moment", "cf-chl", "cf_chl", "attention required", "captcha", "are you a robot",
             "access denied", "ddos-guard", "please enable js and disable any ad blocker", "anubis")
_DAU_LOGIN = ("log in to continue", "please log in", "sign in to continue", "login required", "you must be logged in",
              "to see trades in realtime, please log in")


def phan_loai(kq: dict, url: str) -> tuple[str, str]:
    if kq.get("ma") is None:
        return LOI_MANG, kq.get("loi") or "khong ket noi"
    t = (kq.get("text") or "")[:8000].lower()
    ma = kq["ma"]
    if ma in (401,):
        return CAN_DANG_NHAP, "HTTP 401"
    manh = [d for d in _DAU_CHAN if d not in ("captcha", "access denied")]
    if ma in (403, 429, 503) or (ma in (200, 202) and len(kq.get("text") or "") < 30000 and any(d in t for d in manh)) \
            or (ma in (202,) and "captcha" in t) or (ma == 200 and len(kq.get("text") or "") < 5000 and "captcha" in t):
        dau = next((d for d in _DAU_CHAN if d in t), "")
        return BI_CHAN, f"HTTP {ma}" + (f" + dau hieu '{dau}'" if dau else "")
    cuoi = kq.get("url_cuoi") or url
    if re.search(r"/(login|signin|sign-in|account/login|auth)\b", urlparse(cuoi).path, re.I) and cuoi != url:
        return CAN_DANG_NHAP, "chuyen huong sang trang dang nhap " + urlparse(cuoi).path
    if any(d in t for d in _DAU_LOGIN):
        return CAN_DANG_NHAP, "trang yeu cau dang nhap"
    if ma == 200:
        return DOC_DUOC, "HTTP 200"
    return LOI_MANG, f"HTTP {ma}"


# ------------------------------------------------------------- boc --------
_ITEM = re.compile(r"<(item|entry)\b.*?</\1>", re.S | re.I)
_TIT = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
_LNK = re.compile(r"<link[^>]*?(?:href=[\"']([^\"']+)[\"'][^>]*)?/?>(?:([^<]+)</link>)?", re.S | re.I)
_ALT = re.compile(r"<link[^>]+type=[\"']application/(?:rss|atom)\+xml[\"'][^>]*>", re.I)
_HREF = re.compile(r"href=[\"']([^\"']+)[\"']", re.I)
_A = re.compile(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.S | re.I)
MANG_XA_HOI = [("telegram", r"https?://t\.me/(?:s/)?([A-Za-z0-9_]{5,})"), ("reddit", r"reddit\.com/r/([A-Za-z0-9_]{3,})"),
               ("youtube", r"youtube\.com/(@[A-Za-z0-9_.-]{3,}|channel/[A-Za-z0-9_-]{10,})"),
               ("github", r"github\.com/([A-Za-z0-9-]{2,})/([A-Za-z0-9_.-]{2,})")]
_RAC_GH = {"features", "about", "pricing", "login", "join", "topics", "sponsors", "orgs", "settings", "marketplace", "site"}


def _sach(s):
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s or "", flags=re.S)
    return _h.unescape(re.sub(r"<[^>]+>", " ", s)).strip()


def boc_rss(xml: str) -> list[dict]:
    ra = []
    for m in _ITEM.finditer(xml or ""):
        k = m.group(0)
        t = _TIT.search(k)
        l = _LNK.search(k)
        url = (l.group(1) or l.group(2) or "").strip() if l else ""
        ra.append({"tieu_de": _sach(t.group(1))[:200] if t else "", "url": url})
    return ra


def boc_trang(html: str, url: str, loc: str | None = None) -> list[dict]:
    ra, thay = [], set()
    for href, chu in _A.findall(html or ""):
        u = urljoin(url, _h.unescape(href))
        if loc and not re.search(loc, u):
            continue
        if not loc and Mang.mien(u) != Mang.mien(url):
            continue
        t = _sach(chu)
        if u in thay or (not loc and len(t) < 25):
            continue
        thay.add(u)
        ra.append({"tieu_de": t[:200], "url": u})
    return ra


def kham_pha(html: str, url: str) -> dict:
    """Quy tac TU SINH NGUON (chi ghi ung vien): feed RSS khai trong trang + tai khoan mang xa hoi."""
    feed = []
    for the in _ALT.findall(html or ""):
        m = _HREF.search(the)
        if m:
            feed.append(urljoin(url, _h.unescape(m.group(1))))
    xh: dict[str, set] = {k: set() for k, _ in MANG_XA_HOI}
    for k, rx in MANG_XA_HOI:
        for m in re.finditer(rx, html or ""):
            if k == "github":
                if m.group(1).lower() in _RAC_GH:
                    continue
                xh[k].add(f"{m.group(1)}/{m.group(2)}".rstrip("."))
            elif k == "telegram" and m.group(1).lower() in ("share", "joinchat", "iv"):
                continue
            else:
                xh[k].add(m.group(1))
    return {"feed": sorted(set(feed)), "xa_hoi": {k: sorted(v)[:50] for k, v in xh.items()}}


_GH_RAW = re.compile(r"https?://(?:raw\.githubusercontent\.com|github\.com)/[^\s\"'<>]+?\.(?:mq4|mq5|mqh|set)\b", re.I)


def link_ma(html: str) -> list[str]:
    """Link truc tiep toi .mq4/.mq5/.mqh/.set cong khai tren GitHub thay trong trang."""
    return sorted(set(_GH_RAW.findall(html or "")))


# ------------------------------------------------------------- quet -------
CACH_TU_DONG = ("rss", "http", "api", "telegram_web")


def _url_quet(s: dict) -> str:
    u = s.get("url") or ""
    if s.get("cach") == "telegram_web":
        m = re.match(r"https?://t\.me/(?:s/)?([A-Za-z0-9_]+)", u)
        return f"https://t.me/s/{m.group(1)}" if m else u
    if s.get("mau_tim") and not s.get("seed"):
        return s["mau_tim"].replace("{k}", "trading+strategy")
    return u


def quet_mot(ma: str, s: dict, mang: Mang) -> dict:
    """Mot lan doc trang dau / feed cua nguon. Tra ban ghi ket qua (khong luu noi dung)."""
    ra = {"ma": ma, "ten": s.get("ten"), "cach": s.get("cach"), "can_dang_nhap": s.get("can_dang_nhap"),
          "phong_cach": s.get("phong_cach"), "tai_san": s.get("tai_san"), "khung": s.get("khung"),
          "quan_tri": s.get("quan_tri"), "luc": time.strftime("%Y-%m-%d %H:%M:%S")}
    url = _url_quet(s)
    ra["url"] = url
    if not url.startswith("http"):
        ra.update(trang_thai=KHONG_URL, ly_do="NGUON.md chi ghi ten nen tang, chua co URL")
        return ra
    if s.get("cach") == "tay":
        ra.update(trang_thai=THU_CONG, ly_do="the-brain danh dau 'tay' (cho EA thuong mai, chu du an tu xem)")
        return ra
    kq = mang.lay(url)
    ra.update(trang_thai=kq["trang_thai"], ly_do=kq["ly_do"], http=kq.get("ma"), ky_tu=len(kq.get("text") or ""))
    if kq["trang_thai"] == DOC_DUOC and s.get("can_dang_nhap"):
        ra["ghi_chu"] = "trang dau doc duoc nhung du lieu chinh (lich su lenh / API) can dang nhap"
    if kq["trang_thai"] != DOC_DUOC:
        if s.get("can_dang_nhap") and kq["trang_thai"] in (LOI_MANG,):
            ra["trang_thai"] = CAN_DANG_NHAP
        return ra
    t = kq.get("text") or ""
    if s.get("cach") == "rss" or "<rss" in t[:500] or "<feed" in t[:500]:
        muc = boc_rss(t)
    else:
        muc = boc_trang(t, kq.get("url_cuoi") or url, s.get("loc_lien_ket"))
    ra["muc"] = len(muc)
    ra["mau_muc"] = [m["url"] for m in muc[:3]]
    ra["kham_pha"] = kham_pha(t, kq.get("url_cuoi") or url)
    ra["link_ma"] = link_ma(t)
    if s.get("can_dang_nhap") and not muc:
        ra["trang_thai"] = CAN_DANG_NHAP
        ra["ly_do"] = "trang cong khai khong co muc nao (noi dung sau dang nhap / JS)"
    elif not muc and ra["ky_tu"] < 3000:
        ra["ghi_chu"] = "doc duoc nhung trang gan rong (JS)"
    return ra


def den_han(tt: dict, ma: str, s: dict, bay_gio: float) -> bool:
    c = tt.get(ma) or {}
    return bay_gio - float(c.get("luc_s") or 0) >= float(s.get("chu_ky_gio") or 168) * 3600


def chuyen_dien_dan(s: dict) -> dict | None:
    """Doi mot nguon co phan trang (mau_trang the-brain {base}/{n}) sang cau hinh `doc_nhieu_trang`."""
    if not s.get("mau_trang") or s.get("cach") not in ("http",) or not s.get("loc_lien_ket"):
        return None
    base = s["url"]
    mau = s["mau_trang"].replace("{base}", base).replace("{u}", base)
    mau = mau.replace("//page", "/page")
    return {"ten": s.get("ten"), "loai": s.get("loai", "dien_dan"), "hang": "B", "trang": [base], "mau_trang": mau,
            "loc_lien_ket": s["loc_lien_ket"], "trang_moi_luot": 3, "trang_toi_da": 40, "chu_ky_gio": 168, "mo": "tu_dong"}
