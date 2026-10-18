# -*- coding: utf-8 -*-
"""doc_seeker_da_nguon.py - BO DOC nguon Seeker da nguon (19/10/2026) cho ong dan (nhan/ong_dan.buoc_nhan).

Dau vao (do tac vu Seeker ghi, o day CHI DOC):
  - reports/SEEKER_DA_NGUON.json: `ung_vien` (id, ten, nguon, url, loai, nen_tang, tai_san, khung, phong_cach, co_ma,
    duong_dan_tai, bang_chung_lai, tra_phi, co_lich_su_tung_lenh, diem_uu_tien, ...);
  - data/seeker_da_nguon/tai_ve/...: ma da tai (git bo qua). Moi `duong_dan_tai` la mot file hoac mot thu muc repo;
  - reports/SEEKER_DA_NGUON.md: bang "Xep hang ung vien hoan thien" (28 he top) -> uu tien 0.
Ra: list THE (dang cua ong dan). Moi the:
  - EA (.mq4/.mq5 co OnTick): mot the / file, kem cac .set cung ten / cung thu muc;
  - .ex4/.ex5 khong co ma cung ten: the chi_bien_dich -> chay thang MT5;
  - statement / bao cao tester (.htm/.html/.csv co danh sach lenh): the STATEMENT + DO NGUOC (nhap_tay.do_nguoc);
  - Python / Pine: mot the / ung vien (file chinh) -> duong LLM;
  - khong co file: mot the / ung vien (MT5 can tai ma tren may nha, hoac chi so doi chieu).
`bang_chung_lai` cua Seeker giu nguyen trong `so_tac_gia` (SO TAC GIA, chua do), KHONG tron voi so mo phong.
Ham o day CHI DOC VAN BAN, khong chay ma tai ve.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from nhan import nhap_tay as NT

GOC = Path(__file__).resolve().parent.parent
NGUON = GOC / "reports" / "SEEKER_DA_NGUON.json"
BANG_MD = GOC / "reports" / "SEEKER_DA_NGUON.md"
TRAN_MA = 3 * 1024 * 1024
NEN = {"mt4": "MQL4", "mt5": "MQL5", "mt4_mt5": "MQL5", "pine": "TradingView", "tradingview": "TradingView",
       "freqtrade": "Python", "python": "Python", "ctrader": "cTrader", "ninjatrader": "NinjaTrader"}
LOAI_KK = {"ea_hoan_thien": "ea", "chi_bao": "chi_bao", "tien_ich": "thu_vien", "mo_ta_phuong_phap": "mo_ta",
           "lich_su_giao_dich": "mo_ta"}


def top28(md: Path = BANG_MD) -> list[str]:
    """URL cua bang 'Xep hang ung vien hoan thien dang test nhat' (thu tu giu nguyen)."""
    if not md.exists():
        return []
    vb = md.read_text(encoding="utf-8")
    i = vb.find("Xếp hạng ứng viên hoàn thiện")
    if i < 0:
        return []
    ra = []
    for dong in vb[i:].splitlines()[1:]:
        if dong.startswith("Danh sách tự động") or dong.startswith("## "):
            break
        m = re.match(r"\|\s*\d+\s*\|.*?\|\s*(https?://\S+?)\s*\|", dong)
        if m:
            ra.append(m.group(1))
    return ra


def _id(*x: str) -> str:
    return hashlib.sha1("|".join(x).encode("utf-8")).hexdigest()[:10]


def _cac_tep(u: dict) -> list[Path]:
    ra = []
    for d in u.get("duong_dan_tai") or []:
        p = GOC / d
        if p.is_file():
            ra.append(p)
        elif p.is_dir():
            ra += [q for q in sorted(p.rglob("*")) if q.is_file() and ".git" not in q.parts]
    return ra


def _vb(p: Path) -> str:
    try:
        return NT.doc_vb(p.read_bytes()[:TRAN_MA])
    except Exception:
        return ""


def _diem_ea(p: Path, u: dict, vb: str) -> float:
    """Xep EA trong mot repo nhieu file: co quan tri (DCA/grid/hedge/martingale) truoc, mq5 truoc, it long thu muc."""
    d = 0.0
    if re.search(r"(?i)grid|martin|dca|averag|recover|hedg|basket|lot\s*\*=|multiplier", vb):
        d += 5
    if p.suffix.lower() == ".mq5":
        d += 1
    if re.search(r"(?i)test|example|sample|old|backup|archive", str(p)):
        d -= 2
    d -= 0.1 * len(p.parts)
    return d


def _so_tac_gia(u: dict) -> dict:
    b = u.get("bang_chung_lai") or {}
    if not b.get("co"):
        return {}
    return {"nhan": "SỐ TÁC GIẢ (chưa đo)", "nguon": b.get("nguon"), "so": b.get("so") or {}, "trich": b.get("trich")}


_TIEN = ("EUR", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY")


def _ma_tu_ten(s: str) -> list[str]:
    """Ma xuat hien trong ten file / duong dan: cap FX (2 dong tien khac nhau), XAUUSD/GOLD, XAGUSD."""
    u = s.upper()
    ra = set()
    for m in re.finditer(r"(?=([A-Z]{6}))", u):
        x = m.group(1)
        if x[:3] in _TIEN and x[3:] in _TIEN and x[:3] != x[3:]:
            ra.add(x)
    if "XAUUSD" in u or "GOLD" in u:
        ra.add("XAUUSD")
    if "XAGUSD" in u or "SILVER" in u:
        ra.add("XAGUSD")
    return sorted(ra)


def doc(da_co: set[str] | None = None, tran_ea: int = 12, tran_ea_top: int = 40, tran_set: int = 60,
        nguon: Path = NGUON) -> list[dict]:
    """SEEKER_DA_NGUON.json -> list THE. `tran_ea`: so EA toi da / ung vien (`tran_ea_top` cho 28 he top)."""
    if not nguon.exists():
        return []
    d = json.loads(nguon.read_text(encoding="utf-8"))
    top = top28(nguon.with_suffix(".md"))
    hang_top = {url: i + 1 for i, url in enumerate(top)}
    da_co = da_co or set()
    the, da_them = [], set()
    for u in d.get("ung_vien") or []:
        if u.get("tra_phi"):
            continue                                                  # khong mua gi
        url = u.get("url") or ""
        h = hang_top.get(url)
        sk = {"id": u["id"], "nguon": u.get("nguon"), "loai": u.get("loai"), "nen_tang": u.get("nen_tang"),
              "tai_san": u.get("tai_san") or [], "khung": u.get("khung") or [], "phong_cach": u.get("phong_cach") or [],
              "diem_uu_tien": u.get("diem_uu_tien"), "top28": h, "co_lich_su_tung_lenh": bool(u.get("co_lich_su_tung_lenh"))}
        stg = _so_tac_gia(u)
        nt_u = NEN.get((u.get("nen_tang") or "").lower(), (u.get("nen_tang") or "").upper())
        tep = _cac_tep(u)
        goc = {"nhan": ["SEEKER"], "seeker": sk}
        if stg:
            goc["so_tac_gia"] = stg

        sinh = []                                                     # moi the sinh cho ung vien nay (ke ca da co)

        def _them(t: dict) -> None:
            sinh.append(t["id"])
            if t["id"] not in da_co and t["id"] not in da_them:
                da_them.add(t["id"])
                x = dict(goc)
                x.update(t)
                the.append(x)

        sets = [p for p in tep if p.suffix.lower() == ".set"]
        # 1) statement / bao cao co danh sach lenh
        for p in [q for q in tep if q.suffix.lower() in (".htm", ".html", ".csv")]:
            if p.stat().st_size > NT.TRAN_BYTE:
                continue
            vb = _vb(p)
            df = NT.doc_lenh_csv(vb) if p.suffix.lower() == ".csv" else NT.doc_lenh_html(vb)
            if df is None or len(df) < 3:
                continue
            sha = NT._sha(p.read_bytes())
            x = NT.the_statement(df, sha, NT.so_tac_gia_bao_cao(vb) if p.suffix.lower() != ".csv" else {})
            ea_cung = [q for q in tep if q.suffix.lower() in (".mq4", ".mq5", ".ex4", ".ex5") and
                       (q.parent == p.parent or q.parent == p.parent.parent)]
            x.update(id="sk_st_" + sha, ten="%s :: %s" % (u.get("ten"), p.name),
                     nguon={"kho": "seeker_da_nguon", "tep": str(p.relative_to(GOC)), "url": url},
                     ea_lien_quan=[str(q.relative_to(GOC)) for q in ea_cung[:5]])
            _them(x)
        # 2) EA co ma
        eas = []
        for p in tep:
            if p.suffix.lower() not in (".mq4", ".mq5") or p.stat().st_size > TRAN_MA:
                continue
            vb = _vb(p)
            if re.search(r"\bOnTick\s*\(|\bint\s+start\s*\(", vb):
                eas.append((_diem_ea(p, u, vb), p))
        eas.sort(key=lambda z: -z[0])
        ten_ma = {p.stem.lower() for _, p in eas}
        for _, p in eas[: (tran_ea_top if h else tran_ea)]:
            cung_ten = [q for q in sets if q.stem.lower().startswith(p.stem.lower())]
            cung_tm = [q for q in sets if q.parent == p.parent or p.parent in q.parents]
            if p.stem.lower() in ("main", "ea", "expert") or len(eas) == 1:
                cung_ten = cung_ten or cung_tm
            ds_set = list(dict.fromkeys(cung_ten + cung_tm))[:tran_set]
            x = {"id": "sk_ea_" + _id(u["id"], str(p)), "ten": "%s :: %s" % (u.get("ten"), p.relative_to(GOC).name),
                 "nen_tang": "MQL4" if p.suffix.lower() == ".mq4" else "MQL5",
                 "nguon": {"kho": "seeker_da_nguon", "tep": str(p.relative_to(GOC)), "url": url},
                 "loai_kiem_ke": "ea", "sets": [str(q.relative_to(GOC)) for q in ds_set],
                 "ma_goi_y": _ma_tu_ten(str(p.relative_to(GOC / "data"))) or [m for m in sk["tai_san"]],
                 "khung_ea": (sk["khung"] or [None])[0]}
            if cung_ten:
                x["set_goc"] = NT.doc_set(_vb(cung_ten[0]))
            _them(x)
        # 3) chi co ban bien dich
        for p in [q for q in tep if q.suffix.lower() in (".ex4", ".ex5") and q.stem.lower() not in ten_ma][:tran_ea]:
            _them({"id": "sk_ex_" + _id(u["id"], str(p)), "ten": "%s :: %s" % (u.get("ten"), p.name),
                   "nen_tang": "MQL4" if p.suffix.lower() == ".ex4" else "MQL5", "chi_bien_dich": True, "loai_kiem_ke": "ea",
                   "nguon": {"kho": "seeker_da_nguon", "tep": str(p.relative_to(GOC)), "url": url},
                   "sets": [str(q.relative_to(GOC)) for q in sets if q.parent == p.parent][:tran_set],
                   "ma_goi_y": _ma_tu_ten(p.name) or sk["tai_san"], "ghi_chu": "chỉ có file biên dịch: chạy thẳng MT5"})
        # 4) chi bao / thu vien MQL (khong OnTick) -> boc co che
        if not sinh and u.get("loai") in ("chi_bao", "tien_ich"):
            mq = [p for p in tep if p.suffix.lower() in (".mq4", ".mq5", ".mqh")][:3]
            for p in mq:
                _them({"id": "sk_cb_" + _id(u["id"], str(p)), "ten": "%s :: %s" % (u.get("ten"), p.name),
                       "nen_tang": "MQL4" if p.suffix.lower() == ".mq4" else "MQL5", "loai_kiem_ke": LOAI_KK[u["loai"]],
                       "nguon": {"kho": "seeker_da_nguon", "tep": str(p.relative_to(GOC)), "url": url}})
        # 5) Python / Pine
        if not sinh:
            dd = [".py"] if nt_u == "Python" else [".pine", ".txt"] if nt_u == "TradingView" else []
            ung = [p for p in tep if p.suffix.lower() in dd and p.stat().st_size < TRAN_MA]
            ung = [p for p in ung if re.search(r"IStrategy|populate_(entry|buy)_trend|strategy\.entry|def\s+on_(tick|bar|candle)|"
                                               r"create_order|place_order", _vb(p))] or ung[:0]
            if ung:
                p = max(ung, key=lambda q: q.stat().st_size)
                _them({"id": "sk_py_" + _id(u["id"], str(p)), "ten": "%s :: %s" % (u.get("ten"), p.name), "nen_tang": nt_u,
                       "loai_kiem_ke": LOAI_KK.get(u.get("loai"), "mo_ta"),
                       "nguon": {"kho": "seeker_da_nguon", "tep": str(p.relative_to(GOC)), "url": url}})
        # 6) khong co file dung duoc -> mot the cho ca ung vien
        if not sinh:
            _them({"id": "sk_uv_" + _id(u["id"]), "ten": u.get("ten") or u["id"], "nen_tang": nt_u,
                   "loai_kiem_ke": LOAI_KK.get(u.get("loai"), "mo_ta"),
                   "nguon": {"kho": "seeker_da_nguon", "tep": "", "url": url},
                   "ma_goi_y": sk["tai_san"], "khung_ea": (sk["khung"] or [None])[0],
                   "chi_doi_chieu": u.get("loai") == "lich_su_giao_dich"})
    return the
