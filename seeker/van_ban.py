# -*- coding: utf-8 -*-
"""Tách văn bản/liên kết từ HTML, RSS, JSON; tách token đa ngôn ngữ (CJK theo n-gram ký tự)."""
from __future__ import annotations
import json, re, urllib.parse, warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]+")
TU = re.compile(r"[^\W\d_][\w'\-]{1,30}", re.UNICODE)
DUNG = set("""the a an and or of to in on for is are was were be been it this that with as at by from you your we our i
they he she not but if so do does did have has had can could will would should just get got more most very about
than then there here what which who how when why all any some one two out up down over into also like only my me
http https www com amp quot reddit submitted comments link
và của là có không cho những các một được người này đã thì với để khi trong""".split())


def tach_trang(html: str, url_goc: str) -> dict:
    """Trả {'tieu_de','van_ban','lien_ket':[(url, chu)]} từ HTML hoặc RSS/Atom."""
    dau = html.lstrip()[:200].lower()
    if dau.startswith("<?xml") or "<rss" in dau or "<feed" in dau:
        sp = BeautifulSoup(html, "html.parser")
        muc = []
        for e in sp.find_all(["entry", "item"]):
            tt = (e.find("title").get_text(" ", strip=True) if e.find("title") else "")
            lk = e.find("link"); href = (lk.get("href") or lk.get_text(strip=True)) if lk else ""
            nd = e.find(["content", "description", "summary"])
            nd = BeautifulSoup(nd.get_text(), "html.parser").get_text(" ", strip=True) if nd else ""
            ng = e.find(["updated", "pubdate", "published"])
            muc.append({"tieu_de": tt, "url": href, "van_ban": nd, "ngay": ng.get_text(strip=True) if ng else None})
        return {"tieu_de": "", "van_ban": "\n".join(m["tieu_de"] + " " + m["van_ban"] for m in muc),
                "lien_ket": [(m["url"], m["tieu_de"]) for m in muc if m["url"]], "muc": muc}
    sp = BeautifulSoup(html, "html.parser")
    for t in sp(["script", "style", "noscript", "nav", "footer"]):
        t.decompose()
    lk = []
    for a in sp.find_all("a", href=True):
        h = urllib.parse.urljoin(url_goc, a["href"]).split("#")[0]
        if h.startswith("http"):
            lk.append((h, a.get_text(" ", strip=True)[:120]))
    return {"tieu_de": sp.title.get_text(strip=True) if sp.title else "",
            "van_ban": re.sub(r"\s+", " ", sp.get_text(" ", strip=True)), "lien_ket": lk, "muc": []}


def tach_json(txt: str) -> dict:
    """Cho API JSON (GitHub, HN, note.com): gom mọi chuỗi + url."""
    try:
        d = json.loads(txt)
    except ValueError:
        return {"tieu_de": "", "van_ban": "", "lien_ket": [], "muc": []}
    chuoi, url = [], []
    def di(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, str) and v.startswith("http") and k in ("html_url", "url", "story_url", "noteUrl"):
                    url.append((v, ""))
                elif isinstance(v, str) and k in ("name", "description", "title", "story_text", "comment_text", "body", "full_name"):
                    chuoi.append(v)
                else:
                    di(v)
        elif isinstance(x, list):
            for v in x: di(v)
    di(d)
    return {"tieu_de": "", "van_ban": "\n".join(chuoi), "lien_ket": url, "muc": []}


def token(van_ban: str) -> list[str]:
    t = van_ban.lower()
    ra = [w for w in TU.findall(CJK.sub(" ", t)) if w not in DUNG and len(w) > 2]
    for khoi in CJK.findall(t):                 # tiếng Trung/Nhật: bigram ký tự
        ra += [khoi[i:i + 2] for i in range(len(khoi) - 1)]
    return ra


def cum_tu(tok: list[str], n: int = 2) -> list[str]:
    return [" ".join(tok[i:i + n]) for i in range(len(tok) - n + 1)]
