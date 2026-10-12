# -*- coding: utf-8 -*-
"""_kiem_ke_nguon_the_brain.py - KIEM KE moi nguon Seeker cua the-brain -> config/nguon_seeker.json.

Doc THANG tu git cua the-brain (chi doc, khong sua): nhanh lam viec + commit ban giao.
Gom: tru/seeker.NGUON (14) + NGUON_TRINH_DUYET (23) + nhan/nguon_bai_viet FEEDS (27) + TRANG (7)
+ nguon_dien_dan.DIEN_DAN (6) + _do_dien_dan_quoc_gia.UNG_VIEN + config/dien_dan.json (23)
+ config/nguon_ung_vien.json (telegram) + config/nguon_tu_tim.json (blog tu sinh) + config/nguon_cho_ea.json
+ web_registry.json (cong API can dang nhap) + bang nen tang trong NGUON.md.
Moi nguon duoc gan nhan 4 chieu (phong_cach, tai_san, khung, quan_tri) bang luat tu khoa CHOT TRUOC
(`nhan/nguon_seeker.gan_nhan`). Chay:  python _kiem_ke_nguon_the_brain.py [--repo /workspace/the-brain]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
from nhan import nguon_seeker as NS  # noqa: E402

NHANH = "origin/claude/autonomous-trading-system-rzzt7h"
BAN_GIAO = "3c9827472992ae98b5a7a878f4c4dacd345ee02d"

# URL goc cho nguon API trong tru/seeker.NGUON (ham Python, khong co URL trong dict)
URL_API = {
    "arxiv": ("https://export.arxiv.org/api/query?search_query=all:trading+strategy&max_results=10", "api"),
    "github": ("https://api.github.com/search/repositories?q=expert+advisor+language:MQL5&per_page=30", "api"),
    "openalex": ("https://api.openalex.org/works?search=trading+strategy&per-page=25", "api"),
    "stackexchange": ("https://api.stackexchange.com/2.3/search/advanced?site=quant&q=strategy", "api"),
    "hackernews": ("https://hn.algolia.com/api/v1/search?query=trading+strategy", "api"),
    "semantic": ("https://api.semanticscholar.org/graph/v1/paper/search?query=trading+strategy", "api"),
    "lean_algo": ("https://api.github.com/repos/QuantConnect/Lean/contents/Algorithm.Python", "api"),
    "mql5_code": ("https://www.mql5.com/en/code/mt5/experts", "http"),
    "blog": ("(nhieu RSS - xem FEEDS)", "rss"),
    "quantconnect": ("https://www.quantconnect.com/forum/discussions", "http"),
    "crossref": ("https://api.crossref.org/works?query=trading+strategy&rows=20", "api"),
    "tradingview_pine": ("https://www.tradingview.com/pubscripts-suggest-json/?search=strategy", "api"),
    "fxblue": ("https://www.fxblue.com/users", "http"),
    "etoro": ("https://www.etoro.com/sapi/rankings/rankings/", "api"),
}


def _git(repo, rev, path):
    try:
        return subprocess.check_output(["git", "-C", repo, "show", f"{rev}:{path}"],
                                       stderr=subprocess.DEVNULL).decode("utf-8", "replace")
    except subprocess.CalledProcessError:
        return ""


def _gan_lit(src: str, ten: str):
    """literal_eval mot phep gan cap module; khoa co gia tri la ham -> bo gia tri do."""
    for n in ast.parse(src.lstrip("\ufeff")).body:
        tg = n.targets[0] if isinstance(n, ast.Assign) else (n.target if isinstance(n, ast.AnnAssign) else None)
        if isinstance(tg, ast.Name) and tg.id == ten:
            v = n.value
            if isinstance(v, ast.Dict):
                ra = {}
                for k, x in zip(v.keys, v.values):
                    try:
                        ra[ast.literal_eval(k)] = ast.literal_eval(x)
                    except Exception:
                        if isinstance(x, ast.Dict):
                            d = {}
                            for kk, xx in zip(x.keys, x.values):
                                try:
                                    d[ast.literal_eval(kk)] = ast.literal_eval(xx)
                                except Exception:
                                    pass
                            ra[ast.literal_eval(k)] = d
                return ra
            return ast.literal_eval(v)
    return None


def _them(ds, ma, **kw):
    ma = re.sub(r"[^a-z0-9_]+", "_", ma.lower()).strip("_")
    if ma in ds:                       # trung ma: gop noi khai bao
        ds[ma]["khai_bao_tai"] = sorted(set(ds[ma]["khai_bao_tai"]) | {kw["khai_bao_tai"]})
        for k, v in kw.items():
            if k != "khai_bao_tai" and not ds[ma].get(k) and v:
                ds[ma][k] = v
        return
    kw["khai_bao_tai"] = [kw["khai_bao_tai"]]
    ds[ma] = kw


def kiem_ke(repo: str) -> dict:
    ds: dict = {}
    sk = _git(repo, NHANH, "tru/seeker.py")
    for ma, c in (_gan_lit(sk, "NGUON") or {}).items():
        url, cach = URL_API.get(ma, ("", "api"))
        _them(ds, ma, ten=ma, url=url, loai=c.get("loai", ""), cach=cach, khai_bao_tai="tru/seeker.NGUON",
              chu_ky_giay=c.get("chu_ky"), uu_tien=c.get("uu_tien"))
    for ma, c in (_gan_lit(sk, "NGUON_TRINH_DUYET") or {}).items():
        seed = c.get("trang") or ([c["mau"]] if c.get("mau") else [])
        _them(ds, ma, ten=ma, url=seed[0] if seed else "", seed=seed, loai=c.get("loai", ""), cach="trinh_duyet",
              mau_tim=c.get("mau"), loc_lien_ket=c.get("loc_lien_ket"), mau_trang=c.get("mau_trang"),
              khai_bao_tai="tru/seeker.NGUON_TRINH_DUYET", chu_ky_giay=c.get("chu_ky"), uu_tien=c.get("uu_tien"),
              tu_khoa_rieng=c.get("tu_khoa_rieng"))
    nb = _git(repo, NHANH, "nhan/nguon_bai_viet.py")
    for ma, c in (_gan_lit(nb, "FEEDS") or {}).items():
        _them(ds, ma, ten=ma, url=c.get("url", ""), loai=c.get("loai", "blog"), cach="rss",
              khai_bao_tai="nhan/nguon_bai_viet.FEEDS", hang=c.get("hang"))
    for ma, c in (_gan_lit(nb, "TRANG") or {}).items():
        seed = c.get("seed") or []
        _them(ds, ma, ten=ma, url=seed[0] if seed else "", seed=seed, loai=c.get("loai", "trang"), cach="http",
              loc_lien_ket=c.get("loc") or c.get("loc_lien_ket"), khai_bao_tai="nhan/nguon_bai_viet.TRANG",
              ngon_ngu=c.get("ngon_ngu"))
    for t in (_gan_lit(_git(repo, NHANH, "nguon_dien_dan.py"), "DIEN_DAN") or []):
        _them(ds, t[0], ten=t[0], url=t[1], loai="dien_dan", cach="http", khai_bao_tai="nguon_dien_dan.DIEN_DAN")
    for t in (_gan_lit(_git(repo, NHANH, "_do_dien_dan_quoc_gia.py"), "UNG_VIEN") or []):
        _them(ds, t[1], ten=t[1], url=t[2], loai="dien_dan", cach="http", nuoc=t[0], loc_lien_ket=t[3] if len(t) > 3 else None,
              khai_bao_tai="_do_dien_dan_quoc_gia.UNG_VIEN")
    dd = json.loads((_git(repo, NHANH, "config/dien_dan.json") or "{}").lstrip("\ufeff"))
    for d in dd.get("dien_dan", []):
        _them(ds, d["ma"], ten=d.get("ten", d["ma"]), url=d["url"], loai=d.get("kieu", "dien_dan"),
              cach=d.get("cach_lay", "http"), nuoc=d.get("nuoc"), mau_trang=d.get("mau_trang"),
              loc_lien_ket=d.get("mau_bai"), bat_o_the_brain=d.get("bat"), kiem_tra_the_brain=d.get("kiem_tra"),
              khai_bao_tai="config/dien_dan.json")
    for k, c in json.loads((_git(repo, NHANH, "config/nguon_ung_vien.json") or "{}").lstrip("\ufeff")).items():
        _them(ds, k.replace(":", "_"), ten=c.get("ten", k), url=c.get("url", ""), loai=c.get("loai", ""),
              cach="telegram_web" if c.get("loai") == "telegram" else "http", nguoi_theo_doi=c.get("nguoi"),
              tu_khoa=c.get("tu_khoa"), khai_bao_tai="config/nguon_ung_vien.json")
    for k, c in json.loads((_git(repo, NHANH, "config/nguon_tu_tim.json") or "{}").lstrip("\ufeff")).items():
        if k.startswith("_"):
            continue
        _them(ds, "tutim_" + k, ten=c.get("ten", k), url=c.get("url", ""), loai=c.get("loai", "blog"), cach="rss",
              tu_dong_sinh=True, tu_thu_muc=c.get("tu_thu_muc"), khai_bao_tai="config/nguon_tu_tim.json")
    for k, c in json.loads((_git(repo, NHANH, "config/nguon_cho_ea.json") or "{}").lstrip("\ufeff")).items():
        if k.startswith("_"):
            continue
        _them(ds, k, ten=k, url=c.get("url", ""), loai=c.get("loai", ""),
              cach={"tu_dong": "http", "may_nha": "trinh_duyet", "tay": "tay"}.get(c.get("mo"), "http"),
              ghi_chu=c.get("vi_sao"), khai_bao_tai="config/nguon_cho_ea.json")
    for k, c in json.loads((_git(repo, NHANH, "web_registry.json") or "{}").lstrip("\ufeff")).items():
        _them(ds, "api_" + k, ten=c.get("ten", k) + " (API ca nhan)", url=(c.get("targets") or [""])[0],
              loai="api_ca_nhan", cach="dang_nhap", khai_bao_tai="web_registry.json")
    # Bang nen tang trong NGUON.md (ten, khong URL)
    for dong in _git(repo, NHANH, "NGUON.md").splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(public|api|login|tay|api/public|public/api)\s*\|", dong)
        if m and m.group(1) != "Nguồn":
            _them(ds, "nen_" + m.group(1)[:40], ten=m.group(1), url="", loai="nen_tang_nguon_md",
                  cach={"api": "api", "login": "dang_nhap", "tay": "tay"}.get(m.group(3), "http"),
                  ghi_chu=m.group(2), khai_bao_tai="NGUON.md")
    # Bo sung 12/10/2026 (chu du an qua tac tu cha): TradingView chien luoc cong khai
    _them(ds, "tradingview_strategies", ten="TradingView - Public strategies (Pine ma mo)",
          url="https://www.tradingview.com/scripts/?script_type=strategies", loai="ma_nguon", cach="http",
          ghi_chu="trang cong khai, khong dang nhap; strategy() Pine ma mo; hang cho: config/hang_cho_tradingview.json",
          khai_bao_tai="bo_sung_12_10_2026")
    for ma, s in ds.items():
        s.update(NS.gan_nhan(s))
        s["can_dang_nhap"] = NS.can_dang_nhap(s)
    return ds


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/workspace/the-brain")
    a = ap.parse_args(argv)
    ds = kiem_ke(a.repo)
    ra = {"_ghi_chu": ["Kiem ke tu the-brain " + NHANH + " (ban giao " + BAN_GIAO[:8] + "). Sinh boi _kiem_ke_nguon_the_brain.py.",
                       "Nhan 4 chieu theo luat tu khoa chot truoc trong nhan/nguon_seeker.gan_nhan; 'tong_hop' = nguon nhieu phong cach.",
                       "KHONG co khoa / mat khau / phien. Ket qua quet that o reports/SEEKER_QUET_NGUON.json."],
          "tong": len(ds), "nguon": dict(sorted(ds.items()))}
    p = LAB / "config" / "nguon_seeker.json"
    p.write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(len(ds), Counter(x for s in ds.values() for x in s["khai_bao_tai"]))


if __name__ == "__main__":
    main()
