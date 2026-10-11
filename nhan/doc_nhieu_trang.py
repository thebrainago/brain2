# -*- coding: utf-8 -*-
"""doc_nhieu_trang.py - SEEKER doc DANH SACH NHIEU TRANG co con tro (11/10/2026).

Y lay tu the-brain DIEN_DAN_DOC (sua 08/10) - VIET LAI GON, khong port `doc_dien_dan.py`.
Loi the-brain gap: doc 1 trang danh sach roi bao XONG. O day:
  1. tim trang ke theo thu tu  rel_next -> mau_trang -> neo_so -> mau_suy_ra -> chu_tiep
     (nut Next/Trang sau/下一页/Следующая, chi mui ten don ›);
  2. CON TRO moi danh sach (`data/doc_nhieu_trang/CON_TRO.json`): luot sau di tiep tu trang
     dang do; het vong (het trang / cham `trang_toi_da`) thi quet lai sau 168 gio;
  3. trang 1 khong thay trang ke = KHONG_THAY_TRANG_TIEP (LOI CAU HINH, khong phai xong);
     nguon `phan_trang: false` (danh sach AJAX) = MOT_TRANG, khong tinh loi;
  4. tai hong -> con tro DUNG YEN; 403/429/captcha/Cloudflare -> DUNG ten mien do 24 gio;
  5. chi theo chuyen huong CUNG ten mien va https;
  6. trang ke tra lai dung tap link cua trang truoc (qua bien im lang) -> HET_TRANG.
Bi chan thoi gian (`han_giay`), nhip >= `NHIP_GIAY` giua hai lan tai cung ten mien.
CHI DOC trang cong khai. Khong dang nhap, khong dang bai, khong luu mat khau.
Nguon `mo: can_dang_nhap` khong quet: ghi CHUA DO DUOC kem ly do.
"""
from __future__ import annotations

import html as _h
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

LAB = Path(__file__).resolve().parent.parent
CAU_HINH = LAB / "config" / "dien_dan.json"
GOC = Path(os.environ.get("BRAIN_DOC_NHIEU_TRANG_DIR") or (LAB / "data" / "doc_nhieu_trang"))
QUET_LAI_GIAY = 168 * 3600
CHAN_GIAY = 24 * 3600
NHIP_GIAY = 4.0
DI_SAU_GIAY = 3600          # dang di sau: luot ke sau >= 1 gio
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DAU = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
       "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate"}
DAU_CHAN = ("just a moment...", "cf-chl-", "captcha", "attention required", "access denied")
CHU_TIEP = ("next", "next page", "next ›", "trang sau", "trang tiếp", "tiếp", "下一页", "下页",
            "следующая", "далее", "次へ", "›")
_A = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S | re.I)
_HREF = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)
_REL_NEXT = re.compile(r"""<(?:link|a)\b[^>]*rel\s*=\s*["']next["'][^>]*>""", re.I)
_SO_TRANG = [re.compile(r"([?&]page=)(\d+)"), re.compile(r"(/page-)(\d+)"),
             re.compile(r"(/page)(\d+)"), re.compile(r"(/p/)(\d+)")]


# ------------------------------------------------------------------ mang ---
def _lay_that(url: str, timeout: int = 25) -> dict:
    """{'ma', 'html', 'url_cuoi', 'loi'}. Khong nem loi."""
    try:
        import requests
        r = requests.get(url, headers=DAU, timeout=timeout, allow_redirects=True)
        return {"ma": r.status_code, "html": r.text or "", "url_cuoi": r.url, "loi": None}
    except Exception as e:                                  # noqa: BLE001
        return {"ma": None, "html": "", "url_cuoi": url, "loi": f"{type(e).__name__}: {str(e)[:100]}"}


def _mien(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def phan_loai(kq: dict, url: str) -> str:
    """ok | chan (403/429/503/captcha) | chuyen_huong_la | loi_tai."""
    if kq.get("loi") or kq.get("ma") is None:
        return "loi_tai"
    cuoi = kq.get("url_cuoi") or url
    if urlparse(cuoi).scheme != "https" or _mien(cuoi) != _mien(url):
        return "chuyen_huong_la"
    dau = (kq.get("html") or "")[:6000].lower()
    if kq["ma"] in (403, 429, 503) or any(d in dau for d in DAU_CHAN[:2]) or (
            kq["ma"] == 200 and len(kq.get("html") or "") < 20000
            and any(d in dau for d in DAU_CHAN[2:])):
        return "chan"
    return "ok" if kq["ma"] == 200 else "loi_tai"


# ------------------------------------------------------------- boc trang ---
def _chu(s: str) -> str:
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _chuan(url: str, mau: str) -> str:
    """Bo duoi /latest, #post, ?query (vd ?goto=lastpost) -> khu trung."""
    if "#acct." in url:                                      # FF Trade Explorer: giu ma tai khoan
        m = re.search(r"#acct\.\d+", url)
        return url.split("#")[0] + (m.group(0) if m else "")
    url = url.split("#")[0].split("?")[0]                     # ?goto=lastpost&userid=... -> cung bai
    url = re.sub(r"/(latest|unread|page-\d+)/?$", "/", url)
    return url


def boc_lien_ket(html: str, url_trang: str, loc: str) -> list[dict]:
    """[{url, tieu_de}] khop regex `loc`, khu trung, giu thu tu, chi cung ten mien."""
    rx = re.compile(loc)
    ra, thay = [], {}
    for thuoc_tinh, noi_dung in _A.findall(html or ""):
        m = _HREF.search(thuoc_tinh)
        if not m:
            continue
        u = urljoin(url_trang, _h.unescape(m.group(1)).strip())
        if _mien(u) != _mien(url_trang) or not rx.search(u if "#acct." in u else u.split("#")[0]):
            continue
        u = _chuan(u, loc)
        chu = _chu(noi_dung)
        if u in thay:
            if len(chu) > len(ra[thay[u]]["tieu_de"]):
                ra[thay[u]]["tieu_de"] = chu[:300]
            continue
        thay[u] = len(ra)
        ra.append({"url": u, "tieu_de": chu[:300]})
    for x in ra:                                             # link khong chu (anh) -> ten tu duong dan
        if len(x["tieu_de"]) < 4:
            x["tieu_de"] = re.sub(r"[-_./#]+", " ", urlparse(x["url"]).path + (
                urlparse(x["url"]).fragment or "")).strip()[:300]
    return ra


def _so_cua(url: str) -> tuple[re.Pattern, int] | None:
    for rx in _SO_TRANG:
        m = rx.search(url)
        if m:
            return rx, int(m.group(2))
    return None


def tim_trang_ke(html: str, url_hien: str, so_hien: int, cfg: dict) -> tuple[str | None, str]:
    """(url_ke, cach). Thu tu: rel_next -> mau_trang -> neo_so -> mau_suy_ra -> chu_tiep."""
    n = so_hien + 1
    for the in _REL_NEXT.findall(html or ""):
        m = _HREF.search(the)
        if m:
            u = urljoin(url_hien, _h.unescape(m.group(1)))
            if _mien(u) == _mien(url_hien) and u != url_hien:
                return u, "rel_next"
    if cfg.get("mau_trang"):
        return cfg["mau_trang"].format(n=n, u=url_hien), "mau_trang"
    neo = []
    for thuoc_tinh, noi_dung in _A.findall(html or ""):
        m = _HREF.search(thuoc_tinh)
        if m:
            neo.append((urljoin(url_hien, _h.unescape(m.group(1))), _chu(noi_dung).lower()))
    for u, chu in neo:
        if chu == str(n) and _mien(u) == _mien(url_hien) and (_so_cua(u) or (None, 0))[1] == n:
            return u, "neo_so"
    s = _so_cua(url_hien)
    if s and so_hien > 1:
        rx, k = s
        return rx.sub(lambda m: m.group(1) + str(k + 1), url_hien, count=1), "mau_suy_ra"
    for u, chu in neo:
        if chu in CHU_TIEP and _mien(u) == _mien(url_hien) and u.split("#")[0] != url_hien:
            return u, "chu_tiep"
    return None, "khong_thay"


# ------------------------------------------------------------- con tro ----
def doc_cau_hinh(p: Path = CAU_HINH) -> dict:
    """{ma: cfg} gop `dien_dan` + `lich_su_lenh` (bo khoa '_')."""
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    ra = {}
    for nhom in ("dien_dan", "lich_su_lenh"):
        for ma, c in (d.get(nhom) or {}).items():
            if not ma.startswith("_"):
                ra[ma] = dict(c, nhom=nhom)
    return ra


def _doc_ct(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except Exception:                                        # noqa: BLE001
        return {}


def _ghi_ct(p: Path, ct: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tam = p.with_suffix(".tam")
    tam.write_text(json.dumps(ct, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tam, p)


def den_han(c: dict, cfg: dict, bay_gio: float) -> tuple[bool, str]:
    if (c.get("chan_den") or 0) > bay_gio:
        return False, "bi_chan_tam"
    tt = c.get("trang_thai")
    if tt in ("HET_TRANG", "XONG_VONG", "MOT_TRANG", "KHONG_THAY_TRANG_TIEP"):
        cho = QUET_LAI_GIAY if tt != "MOT_TRANG" else float(cfg.get("chu_ky_gio", 24)) * 3600
        if bay_gio - (c.get("xong_luc") or 0) < cho:
            return False, "chua_den_han_quet_lai"
        return True, "quet_lai"
    if tt == "DANG_DI" and bay_gio - (c.get("luc") or 0) < DI_SAU_GIAY:
        return False, "chua_den_chu_ky"
    return True, "den_han"


def can_doc_dau(c: dict, cfg: dict, bay_gio: float) -> bool:
    """Dang di sau (trang > 1) ma trang 1 da cu hon chu ky -> doc lai trang 1 (bai MOI) truoc,
    KHONG doi con tro sau."""
    return int(c.get("so") or 1) > 1 and (
        bay_gio - (c.get("dau_luc") or 0) >= float(cfg.get("chu_ky_gio", 6)) * 3600)


def mot_luot(han_giay: float = 180, lay=None, luu=None, ngu=time.sleep, chi: list | None = None,
             cau_hinh: dict | None = None, goc: Path | None = None, bay_gio=time.time) -> dict:
    """Mot luot bi chan thoi gian. `lay(url)->dict`, `luu(ma, cfg, ds)->so_moi` thay duoc (test).

    Tra {'nguon': {ma#i: {...}}, 'tien': so danh sach tien duoc, 'moi', 'chua_do_duoc': {...}}.
    """
    lay = lay or _lay_that
    goc = Path(goc or GOC)
    p_ct = goc / "CON_TRO.json"
    ct = _doc_ct(p_ct)
    ch = cau_hinh if cau_hinh is not None else doc_cau_hinh()
    t0 = bay_gio()
    lan_cuoi_mien: dict[str, float] = {}
    mien_chan: set[str] = set()
    ra = {"nguon": {}, "tien": 0, "moi": 0, "tai": 0, "chua_do_duoc": {}, "loi_cau_hinh": []}
    for ma, cfg in ch.items():
        if chi and ma not in chi:
            continue
        if cfg.get("mo") != "tu_dong":
            ra["chua_do_duoc"][ma] = cfg.get("can_dang_nhap_cho") or "can dang nhap"
            continue
        if cfg.get("can_dang_nhap_cho"):
            ra["chua_do_duoc"][ma] = cfg["can_dang_nhap_cho"]
        for i, hat in enumerate(cfg.get("trang") or []):
            k = f"{ma}#{i}"
            c = ct.get(k) or {}
            ok, ly_do = den_han(c, cfg, bay_gio())
            bao = {"ly_do": ly_do, "trang": [], "moi": 0}
            ra["nguon"][k] = bao
            if not ok:
                bao["trang_thai"] = c.get("trang_thai")
                continue
            if ly_do == "quet_lai" or not c.get("url"):
                c = {"url": hat, "so": 1, "vong_luc": bay_gio(), "dau_luc": c.get("dau_luc")}
            if can_doc_dau(c, cfg, bay_gio()) and bay_gio() - t0 < han_giay \
                    and _mien(hat) not in mien_chan:
                cho = NHIP_GIAY - (bay_gio() - lan_cuoi_mien.get(_mien(hat), -1e9))
                if cho > 0:
                    ngu(cho)
                kq = lay(hat)
                lan_cuoi_mien[_mien(hat)] = bay_gio()
                ra["tai"] += 1
                if phan_loai(kq, hat) == "ok":
                    ds = boc_lien_ket(kq["html"], hat, cfg["loc_lien_ket"])
                    moi = luu(ma, cfg, ds) if luu else 0
                    bao["moi"] += moi
                    ra["moi"] += moi
                    c["dau_luc"] = bay_gio()
                    bao["trang"].append({"so": 1, "ket_qua": "ok_dau", "lien_ket": len(ds), "moi": moi})
            for _ in range(int(cfg.get("trang_moi_luot", 2))):
                if bay_gio() - t0 >= han_giay:
                    bao["het_gio"] = True
                    break
                url = c["url"]
                mien = _mien(url)
                if mien in mien_chan:
                    bao["bo_qua"] = "mien_bi_chan_luot_nay"
                    break
                cho = NHIP_GIAY - (bay_gio() - lan_cuoi_mien.get(mien, -1e9))
                if cho > 0:
                    ngu(cho)
                kq = lay(url)
                lan_cuoi_mien[mien] = bay_gio()
                ra["tai"] += 1
                pl = phan_loai(kq, url)
                if pl != "ok":
                    bao["trang"].append({"so": c["so"], "ket_qua": pl, "ma": kq.get("ma"),
                                         "loi": kq.get("loi")})
                    if pl == "loi_tai" and kq.get("ma") == 404 and c.get("cach") in (
                            "mau_trang", "mau_suy_ra"):
                        # trang ke do DOAN theo mau ma 404 = qua bien, khong phai mang hong
                        c.update(trang_thai="HET_TRANG", xong_luc=bay_gio(), url=hat, so=1)
                        break
                    if pl == "chan":
                        mien_chan.add(mien)
                        c["chan_den"] = bay_gio() + CHAN_GIAY
                        c["trang_thai"] = "BI_CHAN"
                    else:
                        c["trang_thai"] = "LOI_TAI"          # con tro DUNG YEN
                    c["loi"] = f"{pl} {kq.get('ma')} {kq.get('loi') or ''}".strip()
                    break
                ds = boc_lien_ket(kq["html"], url, cfg["loc_lien_ket"])
                vt = sorted(x["url"] for x in ds)[:50]
                lap_lai = bool(ds) and vt == c.get("van_tay_truoc")
                moi = 0 if lap_lai else (luu(ma, cfg, ds) if luu else 0)
                bao["moi"] += moi
                ra["moi"] += moi
                bao["trang"].append({"so": c["so"], "ket_qua": "ok", "lien_ket": len(ds),
                                     "moi": moi})
                c.pop("loi", None)
                c["luc"] = bay_gio()
                if c["so"] == 1:
                    c["dau_luc"] = c["luc"]
                if c["so"] == 1 and not ds:
                    c.update(trang_thai="KHONG_THAY_BAI", xong_luc=bay_gio())
                    ra["loi_cau_hinh"].append(f"{k}: trang 1 khong co link khop loc_lien_ket")
                    break
                if lap_lai:                                  # qua bien: trang tra lai trang truoc
                    c.update(trang_thai="HET_TRANG", xong_luc=bay_gio(), url=hat, so=1)
                    break
                ra["tien"] += 1
                c["van_tay_truoc"] = vt
                if cfg.get("phan_trang") is False:
                    c.update(trang_thai="MOT_TRANG", xong_luc=bay_gio())
                    break
                ke, cach = tim_trang_ke(kq["html"], url, c["so"], cfg)
                bao["trang"][-1]["trang_ke"] = cach
                if not ke:
                    if c["so"] == 1:
                        c.update(trang_thai="KHONG_THAY_TRANG_TIEP", xong_luc=bay_gio())
                        ra["loi_cau_hinh"].append(f"{k}: KHONG_THAY_TRANG_TIEP o trang 1")
                    else:
                        c.update(trang_thai="HET_TRANG", xong_luc=bay_gio(), url=hat, so=1)
                    break
                if c["so"] + 1 > int(cfg.get("trang_toi_da", 40)):
                    c.update(trang_thai="XONG_VONG", xong_luc=bay_gio(), url=hat, so=1)
                    break
                c.update(url=ke, so=c["so"] + 1, trang_thai="DANG_DI", cach=cach)
            bao["trang_thai"] = c.get("trang_thai")
            bao["den_trang"] = c.get("so")
            ct[k] = c
            _ghi_ct(p_ct, ct)
    ra["giay"] = round(bay_gio() - t0, 1)
    return ra


def luu_vao_so(ma: str, cfg: dict, ds: list[dict]) -> int:
    """Ghi muc luc SEEKER (`tai_lieu`) + cong thu hoach vao bang `nguon` (ma `dd_<ma>`/`ls_<ma>`)."""
    import tru.seeker as S
    from nhan import so as SO
    tien_to = "ls_" if cfg.get("nhom") == "lich_su_lenh" else "dd_"
    ten = tien_to + ma
    moi = S.luu_tai_lieu(ten, [{"tieu_de": f"[{cfg.get('ten', ma)}] {x['tieu_de']}", "url": x["url"],
                                "loai": cfg.get("loai", "dien_dan"), "hang": cfg.get("hang", "B"),
                                "tom_tat": ""} for x in ds])
    SO.chay("INSERT INTO nguon(ma,ten,loai,url,lay_gi,chu_ky_giay,uu_tien,lan_cuoi,so_lan,thu_hoach,"
            "trang_thai) VALUES(?,?,?,?,?,?,?,?,1,?,'BAT') ON CONFLICT(ma) DO UPDATE SET "
            "lan_cuoi=excluded.lan_cuoi, so_lan=so_lan+1, thu_hoach=thu_hoach+excluded.thu_hoach",
            ten, cfg.get("ten", ma), cfg.get("loai", ""), (cfg.get("trang") or [""])[0], "danh_sach",
            int(float(cfg.get("chu_ky_gio", 6)) * 3600), 2, time.time(), moi)
    return moi


def main(argv=None) -> int:
    import argparse
    import sys
    sys.path.insert(0, str(LAB))
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--giay", type=float, default=float(os.environ.get("BRAIN_DOC_NHIEU_TRANG_GIAY", 180)))
    ap.add_argument("--chi", help="ma nguon, phay")
    ap.add_argument("--khong-ghi-so", action="store_true", help="chi do, khong ghi nao.db")
    a = ap.parse_args(argv)
    luu = None
    if not a.khong_ghi_so:
        from nhan import so as SO
        SO.khoi_tao()
        luu = luu_vao_so
    ra = mot_luot(a.giay, luu=luu, chi=a.chi.split(",") if a.chi else None)
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    # Ma thoat != 0 khi KHONG danh sach nao tien duoc ma co nguon den han (D3: khong DAT gia).
    co_den_han = any(b.get("ly_do") in ("den_han", "quet_lai") for b in ra["nguon"].values())
    return 0 if (ra["tien"] > 0 or not co_den_han) else 2


if __name__ == "__main__":
    raise SystemExit(main())
