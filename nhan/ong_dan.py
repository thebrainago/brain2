# -*- coding: utf-8 -*-
"""ong_dan.py - ONG DAN MOT LENH: kho Seeker -> phan loai -> dich / gui MT5 -> optimizer Python -> loc 65/15 (lot that)
-> sinh viec MT5 (.set + .ini, ca Optimization=1) -> boc co che ung vien truot vao KHO -> thu to hop -> doc ket qua MT5.

18/10/2026, chu du an: "noi cac module lai de chuoi CHAY THONG"; uu tien he da hoan thien (EA, chien luoc, chi bao co ma),
co che / tien ich / mo ta xep sau. CLI: `python ong_dan.py <buoc>` (xem tai_lieu/ONG_DAN.md).

Moi buoc chay RIENG duoc, chay TIEP duoc sau khi dung giua chung (moi the / moi phep thu ghi xong la luu vao SQLite
`data/ong_dan/trang_thai.sqlite`), va ghi trang thai + nhat ky. Khong chay MT5 tren box: buoc sinh_mt5 chi ghi file viec
vao `reports/ong_dan/` (di qua git ve may nha) va hang cho cua `mt5tools/sinh_viec.py` / `chay_lien_tuc.py`.
Moi so o day la MÔ PHỎNG Python (`nhan/tai_khoan.chay_tk`, lot that + ky quy + stop-out), phi la PHÍ TẠM cho toi khi
may nha do xong `reports/phi_san/` (khi do tu thay, khong sua code). Holm / OOS / placebo chi la NHAN.
"""
from __future__ import annotations

import json
import os
import random
import re
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import kho_co_che as KHO
from nhan import nguon_lenh as NL
from nhan import nguong as NG
from nhan import tai_khoan as TK
from nhan import gio_san as GS
from nhan import nhap_tay as NT
from nhan import doc_seeker_da_nguon as SK

GOC = Path(__file__).resolve().parent.parent
CAU_HINH = GOC / "config" / "ong_dan.json"
TT = GOC / "data" / "ong_dan" / "trang_thai.sqlite"
RA = GOC / "reports" / "ong_dan"
HANG_CHO = RA / "hang_cho_mt5.jsonl"
VIEC = RA / "viec_mt5"
KET_QUA_MT5 = RA / "ket_qua_mt5"
BUOC = ["nhan", "phan_loai", "quyet_dinh", "toi_uu", "loc", "sinh_mt5", "goi", "boc", "to_hop", "doc_mt5"]
TF_MT5 = {"M15": 15, "M30": 30, "H1": 16385, "H4": 16388, "D1": 16408}

#: Khong gian QUAN LI theo phong cach chu du an: khong SL cung, TP nho (chot non), DCA am/duong, hedge, go lenh.
#: lot0 tinh theo "lot tren 1.000 USD von" (micro XM / cent Exness: 1 lot = 1.000 don vi co so).
KHONG_GIAN_QL = {"tp_pct": [0.001, 0.002, 0.003, 0.005], "dca_buoc_pct": [0.003, 0.005, 0.008, 0.012],
                 "dca_toi_da": [0, 3, 5, 8], "dca_he_so_lot": [1.0, 1.0, 1.3, 1.6], "hedge_khi_lo_pct": [0.0, 0.0, 10.0, 20.0],
                 "lot_tren_1000": [0.3, 1.0, 3.0, 10.0, 30.0]}

THE_BRAIN = [
    {"id": "brain_xl_mrz", "ten": "BRAIN_XuLiLenh · MRZ (hồi quy z-score)", "nen_tang": "BRAIN",
     "nguon": {"kho": "brain2", "tep": "ea_demo/BRAIN_XuLiLenh.mq5"},
     "tin_hieu": {"kieu": "brain", "tham": {"kieu": "MRZ", "n": 50, "nguong_z": 2.0},
                  "khoang": {"n": [20, 50, 100], "nguong_z": [1.5, 2.0, 2.5]}}, "ea_mt5": {"file": "BRAIN_XuLiLenh"}},
    {"id": "brain_xl_rsi", "ten": "BRAIN_XuLiLenh · RSI quá mua / quá bán", "nen_tang": "BRAIN",
     "nguon": {"kho": "brain2", "tep": "ea_demo/BRAIN_XuLiLenh.mq5"},
     "tin_hieu": {"kieu": "brain", "tham": {"kieu": "RSI", "rsi_thap": 30, "rsi_cao": 70},
                  "khoang": {"rsi_thap": [20, 25, 30], "rsi_cao": [70, 75, 80]}}, "ea_mt5": {"file": "BRAIN_XuLiLenh"}},
    {"id": "brain_xl_donchian", "ten": "BRAIN_XuLiLenh · Donchian phá đỉnh/đáy", "nen_tang": "BRAIN",
     "nguon": {"kho": "brain2", "tep": "ea_demo/BRAIN_XuLiLenh.mq5"},
     "tin_hieu": {"kieu": "brain", "tham": {"kieu": "DONCHIAN", "n": 50}, "khoang": {"n": [20, 50, 100]}},
     "ea_mt5": {"file": "BRAIN_XuLiLenh"}},
]
VAO_EA = {"MRZ": 1, "RSI": 2, "DONCHIAN": 3, "KHONG": 0}


# ---------------------------------------------------------------------------------------------------- tien ich chung
def cau_hinh() -> dict:
    c = json.loads(CAU_HINH.read_text(encoding="utf-8"))
    p = os.environ.get("BRAIN_ONG_DAN_DU_LIEU")
    if p and Path(p).exists():
        c["du_lieu"] = json.loads(Path(p).read_text(encoding="utf-8"))
    return c


def _db(tep: Path | None = None) -> sqlite3.Connection:
    p = Path(tep or TT)
    p.parent.mkdir(parents=True, exist_ok=True)
    cn = sqlite3.connect(str(p), timeout=60)
    cn.executescript("""
    CREATE TABLE IF NOT EXISTS the (id TEXT PRIMARY KEY, json TEXT, loai TEXT, uu_tien INTEGER, duong TEXT,
        buoc TEXT, trang_thai TEXT, kq TEXT, cap_nhat TEXT);
    CREATE TABLE IF NOT EXISTS thu (the_id TEXT, khoa TEXT, json TEXT, PRIMARY KEY (the_id, khoa));
    CREATE TABLE IF NOT EXISTS to_hop (khoa TEXT PRIMARY KEY, json TEXT);
    CREATE TABLE IF NOT EXISTS nhat_ky (luc TEXT, buoc TEXT, the_id TEXT, ghi TEXT);
    """)
    return cn


def _ghi_nk(cn, buoc: str, the_id: str, ghi: str) -> None:
    cn.execute("INSERT INTO nhat_ky VALUES (?,?,?,?)", (time.strftime("%Y-%m-%dT%H:%M:%S"), buoc, the_id, ghi[:2000]))


def _luu(cn, the: dict, buoc: str | None = None, trang_thai: str | None = None, kq: dict | None = None) -> None:
    cu = cn.execute("SELECT buoc, trang_thai, kq FROM the WHERE id=?", (the["id"],)).fetchone()
    b = buoc or (cu[0] if cu else "nhan")
    tt = trang_thai if trang_thai is not None else (cu[1] if cu else "")
    k = kq if kq is not None else (json.loads(cu[2]) if cu and cu[2] else {})
    cn.execute("INSERT OR REPLACE INTO the VALUES (?,?,?,?,?,?,?,?,?)",
               (the["id"], json.dumps(the, ensure_ascii=False, default=str), the.get("loai", ""), int(the.get("uu_tien", 9)),
                the.get("duong_dich", ""), b, tt, json.dumps(k, ensure_ascii=False, default=str),
                time.strftime("%Y-%m-%dT%H:%M:%S")))


def cac_the(cn, buoc: str | None = None, trang_thai: str | None = None) -> list[tuple[dict, str, str, dict]]:
    q, a = "SELECT json, buoc, trang_thai, kq FROM the", []
    dk = []
    if buoc:
        dk.append("buoc=?"); a.append(buoc)
    if trang_thai:
        dk.append("trang_thai=?"); a.append(trang_thai)
    if dk:
        q += " WHERE " + " AND ".join(dk)
    q += " ORDER BY uu_tien, id"
    return [(json.loads(r[0]), r[1], r[2], json.loads(r[3] or "{}")) for r in cn.execute(q, a)]


_GIA: dict = {}


def gia(ma: str, khung: str = "H1", cfg: dict | None = None) -> pd.DataFrame | None:
    cfg = cfg or cau_hinh()
    k = (ma, khung, cfg.get("tu_ngay"))
    if k in _GIA:
        return _GIA[k]
    p = (cfg.get("du_lieu") or {}).get(ma)
    ds = [p] if isinstance(p, str) else list(p or [])
    if not ds or not all(Path(x).exists() for x in ds):
        return None
    df = _doc_h1(ds)
    if cfg.get("tu_ngay"):
        df = df[df.index >= pd.Timestamp(cfg["tu_ngay"])]
    df = NL.doi_khung(df, khung)
    _GIA[k] = df
    return df


def _doc_h1(ds: list[str]) -> pd.DataFrame:
    """Doc 1..n CSV gia (H1 hoac M5, gio SERVER) -> H1, noi theo thoi gian (file sau thang file truoc o moc trung).
    Ban H1 gop tu M5 cache o data/ong_dan/gia_h1/ (git bo qua), tu lam lai khi file nguon doi."""
    import hashlib
    k = hashlib.sha1("|".join("%s:%d:%d" % (x, Path(x).stat().st_size, int(Path(x).stat().st_mtime)) for x in ds).encode()).hexdigest()[:16]
    c = GOC / "data" / "ong_dan" / "gia_h1" / (k + ".pkl")
    if c.exists():
        return pd.read_pickle(c)
    phan = []
    for x in ds:
        df = pd.read_csv(x)
        cot = "time" if "time" in df.columns else df.columns[0]
        df.index = pd.to_datetime(df[cot])
        df = df[["open", "high", "low", "close"]].astype(float)
        if len(df) > 10 and df.index.to_series().diff().median() < pd.Timedelta(minutes=60):
            g = df.resample("1h", label="left", closed="left")
            df = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                               "close": g["close"].last()}).dropna()
        phan.append(df)
    df = pd.concat(phan)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = TK.nen_server(df)
    c.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(c)
    return df


def _td(p: Path) -> str:
    try:
        return str(Path(p).relative_to(GOC))
    except ValueError:
        return str(p)


def ma_co_du_lieu(cfg: dict | None = None) -> list[str]:
    cfg = cfg or cau_hinh()
    return [m for m, p in (cfg.get("du_lieu") or {}).items()
            if all(Path(x).exists() for x in ([p] if isinstance(p, str) else p))]


# ---------------------------------------------------------------------------------------------------- (a) NHAN
def buoc_nhan(cn, in_ra=print) -> int:
    """Nhan dau vao tu kho Seeker da kiem ke: EA BRAIN + data/cau_kho/ea_ra_co_che + reports/KHO_*.json."""
    da = {r[0] for r in cn.execute("SELECT id FROM the")}
    moi = []
    for t in THE_BRAIN:
        moi.append(dict(t))
    goc_ea = GOC / "data" / "cau_kho" / "ea_ra_co_che"
    nguon_f = goc_ea / "NGUON.json"
    if nguon_f.exists():
        for x in json.loads(nguon_f.read_text(encoding="utf-8")):
            tep = goc_ea / x["file"]
            if not tep.exists():
                continue
            nt = "MQL4" if ".mq4" in x["file"].lower() else "MQL5"
            moi.append({"id": "mql5_" + x["van_tay"], "ten": x["ten"], "nen_tang": nt,
                        "nguon": {"kho": "mql5_code_base", "tep": str(tep.relative_to(GOC)), "url": x.get("url", "")},
                        "khung_ea": x.get("khung_ea"), "quan_tri_goc": [], "ho": x.get("ho", [])})
    for f in sorted((GOC / "reports").glob("KHO_*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "tep" not in d or "kho" not in d:
            continue
        kho = d["kho"]
        thu_muc = GOC / "data" / "cau_kho" / kho.replace("/", "__")
        for t in d["tep"]:
            loai_kk = t.get("loai")
            if loai_kk == "thu_vien" and not t.get("quan_tri"):
                continue
            tep = thu_muc / t["tep"]
            moi.append({"id": KHO.ma_id(kho, t["tep"]), "ten": "%s :: %s" % (kho, t["tep"]), "nen_tang": t.get("nen_tang", ""),
                        "nguon": {"kho": kho, "tep": str(tep.relative_to(GOC)) if tep.exists() else "",
                                  "url": "https://github.com/%s/blob/HEAD/%s" % (kho, t["tep"]) if "/" in kho else ""},
                        "loai_kiem_ke": loai_kk, "van_hanh": t.get("van_hanh"), "quan_tri_goc": t.get("quan_tri", []),
                        "co_ma_tren_box": tep.exists()})
    # thu muc NHAP TAY: chu du an tu mo trang bi chan bang Chrome cua minh roi luu file vao day (nhan/nhap_tay.py)
    moi += NT.quet(NT.thu_muc(cau_hinh()), da)
    # nguon Seeker da nguon (reports/SEEKER_DA_NGUON.json + data/seeker_da_nguon/tai_ve/), nhan/doc_seeker_da_nguon.py
    c = cau_hinh().get("seeker_da_nguon") or {}
    if c.get("bat", True):
        moi += SK.doc(da, tran_ea=int(c.get("tran_ea", 12)), tran_ea_top=int(c.get("tran_ea_top", 40)))
    n = 0
    with cn:
        for t in moi:
            if t["id"] in da:
                continue
            t.setdefault("nhan", [])
            _luu(cn, t, "nhan", "MOI")
            n += 1
        _ghi_nk(cn, "nhan", "*", "them %d the" % n)
    in_ra("nhan: %d the moi (tong %d)" % (n, len(da) + n))
    return n


# ---------------------------------------------------------------------------------------------------- (b) PHAN LOAI
_KY_HIEU_EA = re.compile(r"OnTick|OrderSend|trade\.(Buy|Sell)|CTrade|strategy\.entry|IStrategy|populate_(entry|buy)_trend")


def phan_loai_mot(t: dict) -> tuple[str, int, str]:
    """-> (loai, uu_tien, ly do). He hoan thien truoc (0-3), co che 4, tien ich 6, mo ta 8."""
    nt = t.get("nen_tang", "")
    lk = t.get("loai_kiem_ke")
    if nt == "BRAIN":
        return "he_hoan_thien", 0, "EA BRAIN da hoan thien, khop MT5 1-1"
    if nt == "STATEMENT":
        return "he_hoan_thien", 1, "statement / bao cao nhap tay: co danh sach lenh that (%d lenh vao)" % \
            (t.get("dau_hieu") or {}).get("so_lenh_vao", 0)
    if t.get("chi_bien_dich"):
        return "he_hoan_thien", 1, "EA chi co ban bien dich (.ex4/.ex5) nhap tay"
    if nt == "SET":
        return "co_che", 4, "bo thong so .set nhap tay (khong co EA cung ten)"
    tep = GOC / (t.get("nguon") or {}).get("tep", "") if (t.get("nguon") or {}).get("tep") else None
    if t.get("chi_doi_chieu"):
        return "mo_ta", 7, "chỉ lịch sử / số tác giả để đối chiếu (không có mã, không có từng lệnh)"
    if lk in ("mo_ta",):
        return "mo_ta", 8, "trang / van ban mo ta (nhap tay), khong co ma"
    vb = ""
    if tep and tep.exists() and tep.is_file():
        try:
            vb = NT.doc_vb(tep.read_bytes()[:800000])
        except Exception:
            vb = ""
    if lk == "chi_bao":
        return "co_che", 4, "chi bao -> moc/vung hoac nguon lenh"
    if lk == "thu_vien":
        return "tien_ich", 6, "thu vien co ky thuat xu li lenh: %s" % ",".join(t.get("quan_tri_goc") or [])
    if vb and _KY_HIEU_EA.search(vb):
        if nt.startswith("MQL") or "MT4" in nt or "MT5" in nt:
            return "he_hoan_thien", 1, "ma MQL co OnTick + lenh vao"
        if "IStrategy" in vb:
            return "he_hoan_thien", 2, "chien luoc freqtrade (IStrategy)"
        return "he_hoan_thien", 3, "bot Python co lenh vao"
    if lk in ("ea", "chien_luoc"):
        return "he_hoan_thien", 3 if not vb else 2, "kiem ke ghi %s%s" % (lk, "" if vb else " (ma CHUA co tren box)")
    return "mo_ta", 8, "khong thay ky hieu lenh vao"


def buoc_phan_loai(cn, in_ra=print) -> int:
    n = 0
    with cn:
        for t, _, _, _ in cac_the(cn, "nhan"):
            t["loai"], t["uu_tien"], t["ly_do_loai"] = phan_loai_mot(t)
            if t.get("nhap_tay") and t["loai"] == "he_hoan_thien":
                t["uu_tien"] = 0          # chu du an tu chon va mo tay -> uu tien ngang EA BRAIN
            sk = t.get("seeker") or {}
            if t["loai"] == "he_hoan_thien" and (sk.get("top28") or t.get("nen_tang") == "STATEMENT"):
                t["uu_tien"] = 0          # 28 he top cua SEEKER_DA_NGUON.md + statement co tung lenh
                t["ly_do_loai"] += "; Seeker top %s" % sk["top28"] if sk.get("top28") else "; statement co tung lenh"
            _luu(cn, t, "phan_loai", "DA_PHAN_LOAI")
            n += 1
    in_ra("phan_loai: %d the" % n)
    return n


# ---------------------------------------------------------------------------------------------------- (c) QUYET DINH
def quyet_dinh_mot(t: dict) -> dict:
    """Chon duong: noi_bo (BRAIN) | spec_dsl (bo dich MQL khong LLM) | llm | mt5_truc_tiep | bo_qua."""
    from nhan import cau_llm as LLM
    if t.get("nen_tang") == "BRAIN":
        t["duong_dich"], t["ly_do_duong"] = "noi_bo", "tin hieu BRAIN viet lai trong nhan/nguon_lenh.py"
        return t
    if t.get("nen_tang") == "STATEMENT":
        ok = bool((t.get("dau_hieu") or {}).get("so_lenh_vao"))
        t["duong_dich"] = "noi_bo" if ok else "bo_qua"
        t["ly_do_duong"] = "lenh that tu statement -> gan quan li phong cach chu du an trong Python" if ok else \
            "statement khong doc duoc lenh nao (CHUA_DO_DUOC)"
        return t
    if t.get("chi_bien_dich"):
        t["duong_dich"], t["ly_do_duong"] = "mt5_truc_tiep", "chi co .ex4/.ex5 -> chay thang MT5 tren may nha"
        return t
    if t.get("loai") != "he_hoan_thien":
        t["duong_dich"], t["ly_do_duong"] = "bo_qua", "khong phai he hoan thien -> boc co che, khong toi uu"
        return t
    tep = GOC / t["nguon"]["tep"] if (t.get("nguon") or {}).get("tep") else None
    if not tep or not tep.exists():
        t["duong_dich"] = "mt5_truc_tiep" if (t.get("nen_tang") or "").startswith(("MQL", "MT")) else "bo_qua"
        t["ly_do_duong"] = "ma chua co tren box -> may nha tai theo url roi chay thang MT5" if t["duong_dich"] != "bo_qua" \
            else "ma chua co tren box, khong phai MQL"
        return t
    vb = NT.doc_vb(tep.read_bytes())
    nt = t.get("nen_tang", "")
    if nt.startswith("MQL") or "MT" in nt:
        from nhan import doc_ma as DM
        try:
            cl = DM.doc_chien_luoc(vb)
        except Exception as e:  # noqa: BLE001
            cl = {"co_che": [], "chua_dien_dat_duoc": ["loi bo dich: %s" % str(e)[:80]]}
        cc = cl.get("co_che") or []
        if cc:
            t["duong_dich"] = "spec_dsl"
            t["tin_hieu"] = {"kieu": "spec", "specs": cc, "khoang": {}}
            t["ly_do_duong"] = "bo dich MQL khong LLM (doc_ma.doc_chien_luoc): %d chan" % len(cc)
            t["chua_dich"] = cl.get("chua_dien_dat_duoc") or []
            t["inputs"] = DM.rut_input(vb)
        else:
            t["duong_dich"] = "mt5_truc_tiep"
            t["ly_do_duong"] = "bo dich khong ra chan (%s) -> chay thang EA goc tren MT5 re hon dich" % \
                "; ".join((cl.get("chua_dien_dat_duoc") or ["?"])[:2])[:160]
        return t
    # Python / Pine: chua co bo dich khong LLM -> LLM (neu co khoa)
    r = LLM.boc_tach(vb, nt or "Python") if LLM.co_khoa() else {"trang_thai": "CHUA_CHAY_DUOC"}
    if r.get("trang_thai") == "OK" and r.get("spec"):
        t["duong_dich"] = "spec_dsl"
        t["tin_hieu"] = {"kieu": "spec", "specs": r["spec"], "khoang": {}}
        t["ly_do_duong"] = "LLM boc tach (%s)" % r.get("nhan", "")
        t["co_che_llm"] = r.get("co_che") or []
    else:
        t["duong_dich"] = "llm"
        t["ly_do_duong"] = "can LLM de dich %s; CHƯA CHẠY ĐƯỢC (%s)" % (nt or "Python", r.get("ghi_chu") or r.get("trang_thai"))
    return t


def buoc_quyet_dinh(cn, in_ra=print) -> int:
    n = 0
    for t, _, _, _ in cac_the(cn, "phan_loai"):
        t = quyet_dinh_mot(t)
        with cn:
            _luu(cn, t, "quyet_dinh", t["duong_dich"].upper())
        n += 1
    in_ra("quyet_dinh: %d the" % n)
    return n


# ---------------------------------------------------------------------------------------------------- (d) OPTIMIZER
def tin_hieu(t: dict, df: pd.DataFrame, tham: dict, ma: str = "") -> np.ndarray:
    th = t["tin_hieu"]
    if th["kieu"] == "brain":
        x = dict(th["tham"]); x.update(tham or {})
        k = x.pop("kieu")
        return NL.tin_hieu_brain(df, k, **x)
    if th["kieu"] == "spec":
        return NL.tin_hieu_spec(th["specs"], df)
    if th["kieu"] == "to_hop":
        return tin_hieu_to_hop(th, df, ma)
    if th["kieu"] == "lenh_ngoai":
        return NT.tin_hieu_lenh_ngoai(th, df, ma)
    raise ValueError(th["kieu"])


def tin_hieu_to_hop(th: dict, df: pd.DataFrame, ma: str = "") -> np.ndarray:
    """Nguon lenh A + bo loc (neu co)."""
    s = tin_hieu({"tin_hieu": th["nguon"]}, df, {}, ma)
    for lc in th.get("bo_loc") or []:
        k = lc["tham"].get("kieu")
        if k == "xu_huong":
            cm, cb = NL.bo_loc_xu_huong(df, int(lc["tham"].get("n", 200)))
            s = NL.ap_loc(s, cho_mua=cm, cho_ban=cb)
        elif k == "gio":
            s = NL.ap_loc(s, cho_ca=NL.bo_loc_gio(df, int(lc["tham"]["tu"]), int(lc["tham"]["den"])))
        elif k == "bien_dong":
            s = NL.ap_loc(s, cho_ca=NL.bo_loc_bien_dong(df, int(lc["tham"].get("n", 14)), float(lc["tham"].get("tran_pct", 1.0))))
    return s


def quan_li_tu(x: dict, von: float) -> TK.QuanLi:
    lot = round(float(x.get("lot_tren_1000", 1.0)) * von / 1000.0, 2)
    return TK.QuanLi(lot0=max(lot, 0.01), tp_pct=x.get("tp_pct"), dca_buoc_pct=x.get("dca_buoc_pct") if x.get("dca_toi_da") else None,
                     dca_toi_da=int(x.get("dca_toi_da", 0)), dca_he_so_lot=float(x.get("dca_he_so_lot", 1.0)),
                     hedge_khi_lo_pct=float(x.get("hedge_khi_lo_pct", 0.0)), mo_khoa_pct=float(x.get("mo_khoa_pct", 0.005)),
                     go_tien=x.get("go_tien", 0.0 if x.get("hedge_khi_lo_pct") else None), go_cheo=bool(x.get("go_cheo", False)),
                     trail_kich_pct=float(x.get("trail_kich_pct", 0.0)), trail_khoang_pct=float(x.get("trail_khoang_pct", 0.0)))


def mau_thu(t: dict, rng: random.Random, cfg: dict) -> dict | None:
    co = ma_co_du_lieu(cfg)
    rieng = (t.get("tin_hieu") or {}).get("ma")          # the gan voi ma cu the (vd statement) -> chi ma do
    if rieng:
        co = [m for m in co if m in set(rieng)]
        if not co:
            return None
    goi_y = [m for m in co if m in set(t.get("ma_goi_y") or [])]
    if goi_y and rng.random() < 0.7:                    # EA ghi ro ma (ten file / tai_san Seeker) -> uu tien ma do
        co = goi_y
    ma = rng.choice(co)
    kh = rng.choice(cfg.get("khung") or ["H1"])
    if (t.get("tin_hieu") or {}).get("kieu") == "lenh_ngoai":
        kh = "H1"                                       # lenh ngoai: khung chi dung de dat lenh, giu H1
    kg = (t.get("tin_hieu") or {}).get("khoang") or {}
    tham = {k: rng.choice(v) for k, v in kg.items()}
    ql = {k: rng.choice(v) for k, v in KHONG_GIAN_QL.items()}
    return {"ma": ma, "khung": kh, "tham": tham, "ql": ql}


def danh_gia(t: dict, thu: dict, cfg: dict) -> dict:
    """MOT phep thu o LOT THAT: tin hieu -> LenhVao -> chay_tk (ky quy, stop-out, phi theo san). OOS chi la NHAN."""
    t0 = time.time()
    df = gia(thu["ma"], thu["khung"], cfg)
    if df is None or len(df) < 300:
        return {"loi": "CHUA_DO_DUOC: thieu du lieu %s %s" % (thu["ma"], thu["khung"])}
    if (t.get("tin_hieu") or {}).get("kieu") == "lenh_ngoai":
        df = _cua_so_lenh(t, df)                        # chi chay trong khoang thoi gian cua statement
        if df is None or len(df) < 48:
            return {"loi": "CHUA_DO_DUOC: statement khong trung khoang du lieu gia %s tren box" % thu["ma"]}
    s = tin_hieu(t, df, thu.get("tham") or {}, thu["ma"])
    tu, den = GS.cam_doi_ngay(cfg.get("san_phi", "XM"))
    s = NL.ap_loc(s, cho_ca=NL.bo_loc_gio(df, den, tu))       # nhu EA: khong mo ro moi trong gio doi ngay
    ev = NL.lenh_vao(df, s, t["id"], thu["ma"])
    von = float(cfg.get("von", 1000.0))
    tk = TK.ho_so_tai_khoan(cfg.get("tai_khoan", "XM_MICRO_TAM"), von)
    hs = TK.ho_so_phi(thu["ma"], cfg.get("san_phi", "XM"))
    ql = quan_li_tu(thu["ql"], von)
    if t.get("tin_hieu", {}).get("kieu") == "to_hop" and t["tin_hieu"].get("nguon_b"):
        sb = tin_hieu({"tin_hieu": t["tin_hieu"]["nguon_b"]}, df, {}, thu["ma"])
        ev += NL.lenh_vao(df, NL.ap_loc(sb, cho_ca=NL.bo_loc_gio(df, den, tu)), t["id"] + "_b", thu["ma"])
        ql.go_cheo = True
    kq = TK.chay_tk({thu["ma"]: df}, ev, ql, tk, {thu["ma"]: hs})
    eq, ex = kq["duong_von"], kq["von_xau"]
    n = len(eq)
    k = int(n * (1 - float(cfg.get("ty_le_oos", 0.3))))
    oos = {}
    if 0 < k < n - 10 and eq[k] > 0 and not kq["chay"]:
        nam_o = max((df.index[-1] - df.index[k]).days / 365.25, 1e-6)
        dinh = np.maximum.accumulate(np.maximum(eq[k:], 1e-9))
        oos = {"lai_pct_nam": round(((max(eq[-1], 1e-9) / eq[k]) ** (1 / nam_o) - 1) * 100, 2),
               "sut_giam_pct": round(float(np.max((dinh - ex[k:]) / dinh)) * 100, 2), "nhan": "NHÃN, không phải cổng"}
    r = {k_: kq[k_] for k_ in ("lai_pct_nam", "sut_giam_pct", "von_cuoi", "lai_tien", "chay", "so_stop_out", "so_lenh_stop_out",
                                "so_ro", "so_lenh", "so_tp", "so_khoa", "so_go", "so_go_cheo", "tu_choi_ky_quy", "lot_mo_max",
                                "muc_ky_quy_min_pct", "ket_nen_max", "phi", "so_nam")}
    r["ket_ngay_max"] = round(kq["ket_nen_max"] * NL.KHUNG_PHUT.get(thu["khung"], 60) / 1440.0, 1)
    r["oos"] = oos
    r["lot0"] = ql.lot0
    r["nhan_phi"] = hs.nhan
    r["tai_khoan"] = kq["tai_khoan"]
    r["nhan_lot_tuyen_tinh"] = {"lai_pct_nam_o_dd80": (round(NG.lai_o_dd(r["lai_pct_nam"], r["sut_giam_pct"]), 1)
                                                       if r["sut_giam_pct"] and r["lai_pct_nam"] > -100 else None),
                                "ghi_chu": "THAM KHẢO, sai với DCA / không SL"}
    r["giay"] = round(time.time() - t0, 2)
    r["nhan"] = "MÔ PHỎNG"
    return r


def _cua_so_lenh(t: dict, df: pd.DataFrame) -> pd.DataFrame | None:
    try:
        l = pd.read_csv(t["tin_hieu"]["tep"], parse_dates=["luc"])
    except Exception:
        return None
    if not len(l):
        return None
    a = l["luc"].min() - pd.Timedelta(days=2)
    b = pd.to_datetime(l["het"], errors="coerce").max() if "het" in l.columns else pd.NaT
    b = (b if pd.notna(b) else l["luc"].max()) + pd.Timedelta(days=5)
    return df[(df.index >= a) & (df.index <= b)]


def diem(r: dict) -> float:
    if r.get("loi"):
        return -1e9
    pen = 0.0
    if r["chay"] or r["so_stop_out"]:
        pen += 500.0
    dd_tran = NG.sut_giam_toi_da("loc_python")
    if r["sut_giam_pct"] >= dd_tran:
        pen += 100.0 + r["sut_giam_pct"]
    return float(r["lai_pct_nam"]) - pen


def buoc_toi_uu(cn, toi_da: int | None = None, ngan_sach: int | None = None, in_ra=print, chi_id: str | None = None) -> int:
    cfg = cau_hinh()
    toi_da = int(toi_da or cfg.get("toi_da_the_moi_lan", 6))
    ngan_sach = int(ngan_sach or cfg.get("ngan_sach_moi_the", 16))
    ds = [x for x in cac_the(cn, "quyet_dinh") if x[0].get("duong_dich") in ("noi_bo", "spec_dsl")
          and x[0].get("loai") == "he_hoan_thien" and (not chi_id or x[0]["id"] == chi_id)]
    if not ma_co_du_lieu(cfg):
        in_ra("toi_uu: KHONG co du lieu gia nao trong config/ong_dan.json -> CHUA_DO_DUOC")
        return 0
    n = 0
    for t, _, _, _ in ds[:toi_da]:
        rng = random.Random(t["id"])
        cu = {r[0]: json.loads(r[1]) for r in cn.execute("SELECT khoa, json FROM thu WHERE the_id=?", (t["id"],))}
        lam = 0
        thay = set()
        hat = []
        if t.get("ql_goi_y"):                           # phep thu dau: quan li DO NGUOC tu statement
            for ma in [m for m in ((t.get("tin_hieu") or {}).get("ma") or []) if m in ma_co_du_lieu(cfg)][:2]:
                q = {k: v[0] for k, v in KHONG_GIAN_QL.items()}
                q.update(dca_toi_da=0, hedge_khi_lo_pct=0.0, lot_tren_1000=1.0)
                q.update(t["ql_goi_y"])
                hat.append({"ma": ma, "khung": "H1", "tham": {}, "ql": q})
        for _ in range(ngan_sach * 4):
            if len(cu) >= ngan_sach:
                break
            thu = hat.pop(0) if hat else mau_thu(t, rng, cfg)
            if thu is None:
                break
            khoa = json.dumps(thu, sort_keys=True)
            if khoa in cu or khoa in thay:
                continue
            thay.add(khoa)
            try:
                r = danh_gia(t, thu, cfg)
            except Exception as e:  # noqa: BLE001
                r = {"loi": "CHUA_DO_DUOC: %s" % str(e)[:160]}
            with cn:
                cn.execute("INSERT OR REPLACE INTO thu VALUES (?,?,?)", (t["id"], khoa, json.dumps({"thu": thu, "kq": r}, default=str)))
            cu[khoa] = {"thu": thu, "kq": r}
            lam += 1
        tot = max(cu.values(), key=lambda z: diem(z["kq"])) if cu else None
        if tot is None and (t.get("tin_hieu") or {}).get("ma"):
            tot = {"thu": {"ma": None, "khung": None, "tham": {}, "ql": {}},
                   "kq": {"loi": "CHUA_DO_DUOC: box khong co du lieu gia cho %s" % ",".join(t["tin_hieu"]["ma"])}}
        with cn:
            _luu(cn, t, "toi_uu", "DA_TOI_UU", {"tot_nhat": tot, "so_thu": len(cu)})
            _ghi_nk(cn, "toi_uu", t["id"], "thu moi %d, tong %d" % (lam, len(cu)))
        kq = (tot or {}).get("kq", {})
        in_ra("toi_uu %-40s thu=%d tot: lai %s%%/nam dd %s%% stop_out %s (%s %s)" % (
            t["id"][:40], len(cu), kq.get("lai_pct_nam"), kq.get("sut_giam_pct"), kq.get("so_stop_out"),
            (tot or {}).get("thu", {}).get("ma"), (tot or {}).get("thu", {}).get("khung")))
        n += 1
    return n


# ---------------------------------------------------------------------------------------------------- (e) LOC 65/15
def buoc_loc(cn, in_ra=print) -> dict:
    dem = {"DAT_LOC": 0, "TRUOT_LOC": 0, "CHUA_DO_DUOC": 0}
    with cn:
        for t, _, _, kq in cac_the(cn, "toi_uu"):
            tot = (kq or {}).get("tot_nhat") or {}
            r = tot.get("kq") or {}
            if not r or r.get("loi"):
                tt, ph = "CHUA_DO_DUOC", {"dat": False, "ly_do": [r.get("loi", "khong co phep thu")]}
            elif float(r.get("so_nam") or 0) < float(cau_hinh().get("nam_du_lieu_toi_thieu", 1.0)):
                tt, ph = "CHUA_DO_DUOC", {"dat": False, "ly_do": ["CHUA_DO_DUOC: chi %.2f nam du lieu (< %.1f)" % (
                    float(r.get("so_nam") or 0), float(cau_hinh().get("nam_du_lieu_toi_thieu", 1.0)))]}
            else:
                ph = NG.dat(r["lai_pct_nam"], r["sut_giam_pct"], "loc_python", r["so_stop_out"], r["chay"])
                tt = "DAT_LOC" if ph["dat"] else "TRUOT_LOC"
                ph["nhan_cuoi_python"] = NG.dat(r["lai_pct_nam"], r["sut_giam_pct"], "cuoi", r["so_stop_out"], r["chay"])["dat"]
            kq["loc"] = ph
            _luu(cn, t, "loc", tt, kq)
            dem[tt] += 1
    in_ra("loc 65/15 (lot that): %s" % dem)
    return dem


# ---------------------------------------------------------------------------------------------------- (f) SINH VIEC MT5
def _dong_set(ten: str, gt, khoang: tuple | None = None) -> str:
    def f(x):
        return ("%.6g" % x) if isinstance(x, float) else str(x)
    if not khoang:
        return "%s=%s" % (ten, f(gt))
    a, b, c = khoang
    return "%s=%s||%s||%s||%s||Y" % (ten, f(gt), f(a), f(b), f(c))


def set_xu_li_lenh(tham_tin: dict, ql: dict, gia_tc: float, von: float, san: str, khung: str = "H1") -> tuple[dict, dict]:
    """(gia tri, khoang toi uu) cho BRAIN_XuLiLenh tu mot phep thu Python. Buoc/TP doi sang DON VI GIA theo gia tham chieu."""
    q = quan_li_tu(ql, von)
    v = {"InpVao": VAO_EA[tham_tin["kieu"]], "InpTF": TF_MT5[khung], "InpN": int(tham_tin.get("n", 50)), "InpNguongZ": float(tham_tin.get("nguong_z", 2.0)),
         "InpRsiThap": float(tham_tin.get("rsi_thap", 30)), "InpRsiCao": float(tham_tin.get("rsi_cao", 70)),
         "InpChieuKhongTin": 0, "InpChoNen": 0, "InpLot0": q.lot0,
         "InpNhoi": 1 if q.dca_toi_da > 0 else 0, "InpBuocGia": round((q.dca_buoc_pct or 0.0) * gia_tc, 6), "InpBuocATR": 0.0,
         "InpGianBuoc": 1.0, "InpKieuLot": 0 if q.dca_he_so_lot == 1.0 else 2, "InpHeSoLot": q.dca_he_so_lot,
         "InpMaxTang": q.dca_toi_da + 1, "InpTPGia": round((q.tp_pct or 0.0) * gia_tc, 6), "InpTPATR": 0.0,
         "InpTrailKichGia": 0.0, "InpTrailKichATR": 0.0, "InpTrailKhoangGia": 0.0, "InpTrailKhoangATR": 0.0, "InpGiuToiDaNen": 0,
         "InpHedgeKhiLoPct": q.hedge_khi_lo_pct, "InpHedgeTiLe": q.hedge_ti_le, "InpMoKhoaGia": round(q.mo_khoa_pct * gia_tc, 6),
         "InpMoKhoaATR": 0.0, "InpGoTien": float(q.go_tien or 0.0), "InpHedgeMaxLan": q.hedge_max_lan, "InpMarginMin": 0.0,
         "InpCatLoPct": 0.0, "InpSpreadMaxGia": 0.0, "InpLogChung": "false"}
    tu, den = GS.cam_doi_ngay(san)                      # D8: gio cam doi ngay THEO SAN (Exness GMT+0)
    v["InpGioCamTu"], v["InpGioCamDen"] = tu, den
    k = {}
    if v["InpTPGia"] > 0:
        k["InpTPGia"] = (round(v["InpTPGia"] * 0.5, 6), round(v["InpTPGia"] * 0.25, 6), round(v["InpTPGia"] * 2.0, 6))
    if v["InpNhoi"]:
        k["InpBuocGia"] = (round(v["InpBuocGia"] * 0.5, 6), round(v["InpBuocGia"] * 0.25, 6), round(v["InpBuocGia"] * 2.0, 6))
        k["InpMaxTang"] = (max(2, v["InpMaxTang"] - 2), 1, v["InpMaxTang"] + 3)
    if v["InpVao"] == 1:
        k["InpNguongZ"] = (max(1.0, v["InpNguongZ"] - 0.5), 0.25, v["InpNguongZ"] + 0.5)
    if v["InpVao"] in (1, 3):
        k["InpN"] = (max(10, v["InpN"] // 2), max(5, v["InpN"] // 4), v["InpN"] * 2)
    return v, k


def _so_to_hop(k: dict) -> int:
    n = 1
    for a, b, c in k.values():
        n *= int(round((c - a) / b)) + 1 if b else 1
    return n


def file_viec_xl(ten: str, ma_san: str, khung: str, v: dict, k: dict, san_cfg: dict, cfg: dict, toi_uu: bool) -> tuple[str, str]:
    set_txt = "\n".join(_dong_set(x, v[x], k.get(x) if toi_uu else None) for x in sorted(v)) + "\n"
    von = float(cfg.get("von", 1000.0)) * (100 if san_cfg.get("tien") == "USC" else 1)
    opt = 0
    if toi_uu:
        opt = 1 if _so_to_hop(k) <= 2000 else 2          # vet can khi it to hop, nguoc lai di truyen
    ini = ("[Tester]\nExpert=BRAIN\\BRAIN_XuLiLenh.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
           "Optimization=%d\nOptimizationCriterion=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=%d\nCurrency=%s\n"
           "Leverage=1:%d\nReport=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n") % (
        ten, ma_san, khung, opt, cfg.get("mt5_tu", "2016.01.01"), cfg.get("mt5_den", "2026.10.01"), int(von),
        san_cfg.get("tien", "USD"), int(san_cfg.get("don_bay", 500)), ten)
    return set_txt, ini


def _ky_hieu(ma: str, san: str, san_cfg: dict) -> str:
    """Ten symbol tren san: uu tien reports/phi_san/<server>/ma_san.json (may nha do), khong co thi theo mau config."""
    d = TK._phi_san_moi_nhat(san)
    if d is not None and (d / "ma_san.json").exists():
        try:
            m = json.loads((d / "ma_san.json").read_text(encoding="utf-8")).get("ma", {}).get(ma)
            if m:
                return m["symbol"]
        except Exception:
            pass
    return san_cfg.get("ky_hieu", "{ma}").format(ma=ma)


def buoc_sinh_mt5(cn, in_ra=print, toi_da_ngoai: int | None = None) -> int:
    cfg = cau_hinh()
    toi_da_ngoai = int(toi_da_ngoai if toi_da_ngoai is not None else cfg.get("toi_da_viec_ea_ngoai", 10))
    VIEC.mkdir(parents=True, exist_ok=True)
    da = set()
    if HANG_CHO.exists():
        da = {json.loads(x).get("ten") for x in HANG_CHO.read_text(encoding="utf-8").splitlines() if x.strip()}
    moi, n_ngoai = [], 0
    for t, buoc, tt, kq in cac_the(cn):
        if buoc != "loc" or tt != "DAT_LOC":
            continue
        tot = kq["tot_nhat"]
        thu, r = tot["thu"], tot["kq"]
        th = t["tin_hieu"]
        nguon_th = th["nguon"] if th["kieu"] == "to_hop" else th
        bieu_dat = (nguon_th["kieu"] == "brain" and not (th.get("bo_loc") or th.get("nguon_b")))
        d = VIEC / t["id"]
        d.mkdir(parents=True, exist_ok=True)
        if bieu_dat:
            tham_tin = dict(nguon_th["tham"]); tham_tin.update(thu.get("tham") or {})
            df = gia(thu["ma"], thu["khung"], cfg)
            gia_tc = float(df["close"].iloc[-min(len(df), 2000):].median())
            for san, sc in (cfg.get("san_mt5") or {}).items():
                ma_san = _ky_hieu(thu["ma"], san, sc)
                v, k = set_xu_li_lenh(tham_tin, thu["ql"], gia_tc, float(cfg.get("von", 1000.0)), san, thu["khung"])
                for pha, toi_uu in (("KIEM", False), ("TOI_UU", True)):
                    ten = "od_%s_%s_%s" % (re.sub(r"[^A-Za-z0-9]", "", t["id"])[:24], san, pha)
                    s_txt, ini = file_viec_xl(ten, ma_san, thu["khung"], v, k, sc, cfg, toi_uu)
                    (d / (ten + ".set")).write_text(s_txt, encoding="ascii")
                    (d / (ten + ".ini")).write_text(ini, encoding="ascii")
                    if ten in da:
                        continue
                    moi.append({"ten": ten, "ea": "XL", "ea_file": "BRAIN_XuLiLenh", "ma": ma_san, "tf": thu["khung"],
                                "ts": {x: v[x] for x in sorted(v)}, "toi_uu": {x: list(k[x]) for x in sorted(k)} if toi_uu else {},
                                "pha": pha, "nguon": "ong_dan", "the_id": t["id"], "san": san,
                                "tu": cfg.get("mt5_tu"), "den": cfg.get("mt5_den"),
                                "von": float(cfg.get("von", 1000.0)) * (100 if sc.get("tien") == "USC" else 1),
                                "tien": sc.get("tien", "USD"), "don_bay": int(sc.get("don_bay", 500)),
                                "python": {k_: r.get(k_) for k_ in ("lai_pct_nam", "sut_giam_pct", "so_stop_out", "lot0")},
                                "diem": 60 + min(r.get("lai_pct_nam", 0), 40) / 10.0})
        else:
            (d / "CAN_EA_GHEP.md").write_text(
                "# %s\n\nHệ này đạt lọc Python 65/15 (MÔ PHỎNG, %s) nhưng chưa có EA MT5 biểu đạt được đúng nó "
                "(nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom "
                "(bước 7a của bản rà soát, việc của Claude).\n\nThông số Python tốt nhất:\n\n```json\n%s\n```\n" % (
                    t.get("ten", t["id"]), r.get("nhan_phi", ""), json.dumps(thu, ensure_ascii=False, indent=1)),
                encoding="utf-8")
        with cn:
            _luu(cn, t, "sinh_mt5", "CHO_MT5" if bieu_dat else "CHO_EA_GHEP")
    # EA ngoai chay thang MT5: (a) moi .set co san -> mot viec (co ||Y -> optimizer), (b) khong co .set -> chay 1 lan xuat lenh
    for t, buoc, tt, kq in cac_the(cn, "quyet_dinh"):
        if n_ngoai >= toi_da_ngoai:
            break
        if t.get("duong_dich") != "mt5_truc_tiep" and not (t.get("duong_dich") == "spec_dsl" and not _co_gia_box(t, cfg)):
            continue
        viec = viec_ngoai(t, cfg, 100 if (t.get("seeker") or {}).get("top28") else 40)
        for v in viec:
            if v["ten"] not in da:
                moi.append(v)
                da.add(v["ten"])
        n_ngoai += 1
        with cn:
            _luu(cn, t, "sinh_mt5", "CHO_MT5_NGOAI", {"viec": [v["ten"] for v in viec]})
    if moi:
        HANG_CHO.parent.mkdir(parents=True, exist_ok=True)
        with open(HANG_CHO, "a", encoding="utf-8") as f:
            for v in moi:
                f.write(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
    ghi_viec_md(cn)
    in_ra("sinh_mt5: %d viec moi -> %s" % (len(moi), _td(HANG_CHO)))
    return len(moi)


def _co_gia_box(t: dict, cfg: dict) -> bool:
    g = t.get("ma_goi_y") or []
    co = set(ma_co_du_lieu(cfg))
    return not g or bool(co & set(g))


_TF_SET = {v: k for k, v in TF_MT5.items()}
_TF_SET.update({1: "M1", 5: "M5", 15: "M15", 30: "M30", 60: "H1", 240: "H4", 1440: "D1", 16386: "H2", 16408: "D1"})


def viec_ngoai(t: dict, cfg: dict, tran_set: int = 40) -> list[dict]:
    """Viec MT5 cho EA NGOAI (ma trong data/ tren box, khong vao git -> goi zip /workspace/goi_may_nha/)."""
    tep = (t.get("nguon") or {}).get("tep", "")
    sk = t.get("seeker") or {}
    goc_ma = (t.get("ma_goi_y") or ["EURUSD"])[0]
    tf0 = t.get("khung_ea") or "H1"
    co_ban = {"ea": "NGOAI", "ea_file": Path(tep or t["ten"]).stem, "url": (t.get("nguon") or {}).get("url", ""),
              "tep_box": tep, "nguon": "ong_dan", "the_id": t["id"], "can_tai_ma": not bool(tep),
              "chi_bien_dich": bool(t.get("chi_bien_dich")), "nen_tang": t.get("nen_tang"),
              "seeker": {k: sk.get(k) for k in ("id", "top28", "diem_uu_tien")} if sk else None,
              "so_tac_gia": t.get("so_tac_gia"), "tu": cfg.get("mt5_tu"), "den": cfg.get("mt5_den"),
              "diem": (30 if sk.get("top28") else 5) + float(sk.get("diem_uu_tien") or 0) / 10.0}
    goc_id = re.sub(r"[^A-Za-z0-9]", "", t["id"])[:24]
    ra = []
    for f in (t.get("sets") or [])[:tran_set]:
        p = GOC / f
        vb = NT.doc_vb(p.read_bytes()) if p.exists() else ""
        st = NT.doc_set(vb)
        ma = (SK._ma_tu_ten(p.stem) or t.get("ma_goi_y") or [goc_ma])[0]
        tf = tf0
        for k in ("Timeframe", "TimeFrame", "InpTimeframe", "TF"):
            if str(st.get(k, "")).isdigit():
                tf = _TF_SET.get(int(st[k]), tf)
        toi_uu = bool(re.search(r"\|\|Y\s*$", vb, re.M))
        v = dict(co_ban)
        v.update(ten="od_%s_%s" % (goc_id, re.sub(r"[^A-Za-z0-9]", "", p.stem)[:28]), ma=ma, tf=tf, set_box=f,
                 pha="TOI_UU_SET" if toi_uu else "CHAY_SET", ts={},
                 ghi_chu="Máy nhà: lấy mã + .set từ gói zip (/workspace/goi_may_nha/), biên dịch, nạp .set này, chạy tester "
                         "%s; xuất báo cáo .htm (có danh sách lệnh) vào reports/ong_dan/ket_qua_mt5/." % (
                             "Optimization=1 theo cờ ||Y trong .set" if toi_uu else "1 lần"))
        ra.append(v)
    if not ra:
        v = dict(co_ban)
        v.update(ten="od_%s_XUAT_LENH" % goc_id, ma=goc_ma, tf=tf0, ts={}, pha="XUAT_LENH",
                 ghi_chu="Máy nhà: lấy mã từ gói zip (hoặc tải theo url nếu can_tai_ma), biên dịch, chạy tester 1 lần thông số "
                         "mặc định, xuất báo cáo .htm vào reports/ong_dan/ket_qua_mt5/ -> nhan/nhap_tay đọc lệnh, dò ngược.")
        ra.append(v)
    return ra


def ghi_viec_md(cn) -> None:
    rows = [json.loads(x) for x in HANG_CHO.read_text(encoding="utf-8").splitlines() if x.strip()] if HANG_CHO.exists() else []
    d = ["# Việc MT5 do ống dẫn sinh (`python ong_dan.py sinh_mt5`)", "",
         "Máy nhà: `python mt5tools/chay_lien_tuc.py` tự lấy việc `ea=XL` (BRAIN_XuLiLenh) từ `hang_cho_mt5.jsonl`; "
         "hoặc chạy tay từng ini trong `viec_mt5/<the_id>/`. Việc `NGOAI` cần tải mã theo URL trước. Số Python là MÔ PHỎNG, PHÍ TẠM.", "",
         "| Việc | EA | Mã | Khung | Pha | Python: lãi %/năm · sụt % · stop-out |", "|---|---|---|---|---|---|"]
    for v in rows:
        p = v.get("python") or {}
        d.append("| %s | %s | %s | %s | %s | %s |" % (v["ten"], v.get("ea_file"), v.get("ma"), v.get("tf"), v.get("pha"),
                 ("%s · %s · %s" % (p.get("lai_pct_nam"), p.get("sut_giam_pct"), p.get("so_stop_out"))) if p else "-"))
    (RA / "VIEC_MT5.md").write_text("\n".join(d) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------------- (g) BOC CO CHE
_MOC = ("bollinger", "muc_song", "donchian", "pivot", "kenh", "high", "low", "dinh", "day", "fib", "envelope", "keltner")


def boc_mot(t: dict, kq: dict) -> list[dict]:
    """The he -> cac co che co nhan vai tro. Dung ca the DAT lan TRUOT; the truot thi day la cach giu lai phan dang dung."""
    ra = []
    tot = (kq or {}).get("tot_nhat") or {}
    so = (tot.get("kq") or {})
    do = {k: so[k] for k in ("lai_pct_nam", "sut_giam_pct", "so_stop_out") if k in so}
    if do:
        do.update(ma=tot["thu"]["ma"], khung=tot["thu"]["khung"])
    nhan = ["MÔ PHỎNG", "PHÍ TẠM"] if do else ["CHƯA ĐO ĐƯỢC"]
    th = t.get("tin_hieu") or {}
    kho = (t.get("nguon") or {}).get("kho", "")
    if t.get("set_goc"):
        ra.append(KHO.co_che("quan_li", "bo .set %s" % Path((t.get("nhap_tay") or {}).get("tep", t["id"])).name,
                             "thong so goc (nhap tay) cua %s" % t.get("ten", ""), {"kieu": "set", "set": t["set_goc"]}, {},
                             t["id"], kho, {}, ["NHẬP TAY", "MÔ TẢ, chưa chạy được riêng"]))
    if th.get("kieu") == "lenh_ngoai":
        ra.append(KHO.co_che("nguon_lenh", "lenh statement %s" % Path(th["tep"]).stem, t.get("ten", ""),
                             {"kieu": "lenh_ngoai", "tep": th["tep"], "ma": th.get("ma") or []}, {}, t["id"], kho, do,
                             (nhan or []) + ["NHẬP TAY"]))
    if th.get("kieu") == "brain":
        tham = dict(th["tham"]); tham.update((tot.get("thu") or {}).get("tham") or {})
        ra.append(KHO.co_che("nguon_lenh", "%s %s" % (t["id"], tham.get("kieu")), t.get("ten", ""),
                             {"kieu": "brain", "tham": tham}, th.get("khoang"), t["id"], kho, do, nhan))
    elif th.get("kieu") == "spec":
        for sp in th.get("specs") or []:
            ra.append(KHO.co_che("nguon_lenh", sp.get("ten", "spec")[:60], (sp.get("co_che") or "")[:300],
                                 {"kieu": "spec", "specs": [sp]}, {}, t["id"], kho, do, nhan))
            vao = sp.get("vao") or []
            for d in vao if len(vao) > 1 else []:
                txt = json.dumps(d, ensure_ascii=False)
                vai = "moc_vung" if any(m in txt.lower() for m in _MOC) else "bo_loc"
                ra.append(KHO.co_che(vai, ("%s :: %s" % (sp.get("ten", ""), txt))[:90], "dieu kien tach tu %s" % t["id"],
                                     {"kieu": "dieu_kien", "dieu_kien": d}, {}, t["id"], kho, {}, ["CHƯA ĐO ĐƯỢC riêng"]))
    if tot.get("thu"):
        ql = tot["thu"]["ql"]
        ra.append(KHO.co_che("go_lenh" if ql.get("hedge_khi_lo_pct") else "quan_li",
                             "ql tp%.3g dca%sx%s hs%s hedge%s" % (ql.get("tp_pct") or 0, ql.get("dca_buoc_pct"), ql.get("dca_toi_da"),
                                                                ql.get("dca_he_so_lot"), ql.get("hedge_khi_lo_pct")),
                             "bo quan li tot nhat cua %s trong optimizer Python" % t["id"], {"kieu": "ql", "ql": ql}, {},
                             t["id"], kho, do, nhan))
    for tag in t.get("quan_tri_goc") or []:
        vai = KHO.VAI_TU_NHAN.get(tag)
        if vai:
            # mot co che / (ky thuat, kho): nhieu file cung kho cung nhan thi gop, khong nhan ban
            ra.append(KHO.co_che(vai, "%s (%s)" % (tag, kho), "ky thuat '%s' thay trong kho %s (kiem ke Seeker, chua co tham so); "
                                 "vi du %s" % (tag, kho, (t.get("nguon") or {}).get("tep", "")), {"kieu": "nhan", "ky_thuat": tag},
                                 {}, "kho:" + kho, kho, {}, ["MÔ TẢ, chưa có tham số"]))
    for c in t.get("co_che_llm") or []:
        if c.get("vai_tro") in KHO.VAI_TRO:
            ra.append(KHO.co_che(c["vai_tro"], c.get("ten", "llm")[:60], c.get("mo_ta", ""), {"kieu": "llm", **(c.get("tham") or {})},
                                 {}, t["id"], kho, {}, ["LLM"]))
    return ra


HAT_GIONG = [
    ("bo_loc", "loc xu huong SMA200", {"kieu": "xu_huong", "n": 200}),
    ("bo_loc", "loc gio 07-20 server", {"kieu": "gio", "tu": 7, "den": 20}),
    ("bo_loc", "loc bien dong ATR14 <= 1%", {"kieu": "bien_dong", "n": 14, "tran_pct": 1.0}),
    ("quan_li", "DCA deu 0,5% x5, TP 0,2%", {"kieu": "ql", "ql": {"tp_pct": 0.002, "dca_buoc_pct": 0.005, "dca_toi_da": 5,
                                                                    "dca_he_so_lot": 1.0, "hedge_khi_lo_pct": 0.0, "lot_tren_1000": 1.0}}),
    ("quan_li", "DCA nhan 1,3 0,8% x5, TP 0,3%", {"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.008, "dca_toi_da": 5,
                                                                         "dca_he_so_lot": 1.3, "hedge_khi_lo_pct": 0.0, "lot_tren_1000": 1.0}}),
    ("go_lenh", "khoa khi lo 10% so du, mo khoa 0,5%, go hoa von", {"kieu": "ql", "ql": {
        "tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 3, "dca_he_so_lot": 1.0, "hedge_khi_lo_pct": 10.0, "lot_tren_1000": 1.0}}),
    ("go_lenh", "go cheo giua hai nguon", {"kieu": "go_cheo"}),
]


def buoc_boc(cn, in_ra=print) -> int:
    ds = []
    for t, buoc, tt, kq in cac_the(cn):
        if t.get("da_boc"):
            continue
        if (buoc == "loc" and tt in ("TRUOT_LOC", "CHUA_DO_DUOC")) or buoc in ("quyet_dinh",) and \
                t.get("duong_dich") in ("bo_qua", "llm", "mt5_truc_tiep") or (buoc == "sinh_mt5" and tt in ("CHO_MT5_NGOAI",)):
            c = boc_mot(t, kq)
            ds += c
            t["da_boc"] = len(c)
            with cn:
                _luu(cn, t, None, None)
    ds += [KHO.co_che(v, ten, "hat giong cua ong dan (phong cach chu du an)", th, {}, "brain_hat_giong", "brain2") for v, ten, th in HAT_GIONG]
    moi = KHO.them(ds)
    KHO.ghi_tom_tat()
    in_ra("boc: %d co che (moi %d) -> %s" % (len(ds), moi, _td(KHO.TOM_TAT)))
    return moi


# ---------------------------------------------------------------------------------------------------- (h) TO HOP
def chay_duoc(c: dict) -> bool:
    k = (c.get("tham") or {}).get("kieu")
    return k in ("brain", "spec", "lenh_ngoai") if c["vai_tro"] == "nguon_lenh" else \
        k in ("xu_huong", "gio", "bien_dong") if c["vai_tro"] == "bo_loc" else k in ("ql", "go_cheo")


def buoc_to_hop(cn, ngan_sach: int | None = None, in_ra=print) -> dict:
    """Thu cac to hop co che (co ngan sach): nguon lenh A [+ bo loc] + quan li/go lenh [+ nguon B de go cheo]."""
    cfg = cau_hinh()
    ngan_sach = int(ngan_sach or cfg.get("ngan_sach_to_hop", 24))
    nguon = [c for c in KHO.lay("nguon_lenh") if chay_duoc(c)]
    loc = [c for c in KHO.lay("bo_loc") if chay_duoc(c)]
    ql = [c for c in KHO.lay("quan_li") + KHO.lay("go_lenh") if chay_duoc(c)]
    if not nguon or not ql or not ma_co_du_lieu(cfg):
        in_ra("to_hop: thieu nguon lenh / quan li chay duoc / du lieu -> bo qua")
        return {"thu": 0, "dat": 0}
    da = {r[0] for r in cn.execute("SELECT khoa FROM to_hop")}
    rng = random.Random(len(da) + 18102026)
    thu_n, dat_n = 0, 0
    for _ in range(ngan_sach * 5):
        if thu_n >= ngan_sach:
            break
        a = rng.choice(nguon)
        q = rng.choice(ql)
        lc = [rng.choice(loc)] if loc and rng.random() < 0.6 else []
        b = rng.choice([x for x in nguon if x["id"] != a["id"]] or [a]) if q["tham"]["kieu"] == "go_cheo" else None
        if q["tham"]["kieu"] == "go_cheo":
            qx = dict(rng.choice([x for x in ql if x["tham"]["kieu"] == "ql"] or [{"tham": {"ql": {"tp_pct": 0.002}}}])["tham"]["ql"])
            qx["go_cheo"] = True
        else:
            qx = dict(q["tham"]["ql"])
        qx["lot_tren_1000"] = rng.choice(KHONG_GIAN_QL["lot_tren_1000"])
        rieng = [m for m in ((a.get("tham") or {}).get("ma") or []) if m in ma_co_du_lieu(cfg)]
        if (a.get("tham") or {}).get("kieu") == "lenh_ngoai" and not rieng:
            continue                               # lenh statement tren ma box khong co gia
        ma = (a.get("do_duoc") or {}).get("ma") or (rng.choice(rieng) if rieng else rng.choice(ma_co_du_lieu(cfg)))
        kh = (a.get("do_duoc") or {}).get("khung") or rng.choice(cfg.get("khung") or ["H1"])
        th = {"kieu": "to_hop", "nguon": a["tham"], "bo_loc": lc, "nguon_b": b["tham"] if b else None}
        khoa = json.dumps({"a": a["id"], "b": b["id"] if b else None, "loc": [x["id"] for x in lc], "ql": qx, "ma": ma, "kh": kh},
                          sort_keys=True)
        if khoa in da:
            continue
        da.add(khoa)
        the = {"id": "to_hop_" + KHO.ma_id(khoa), "ten": "Tổ hợp: %s%s + %s%s" % (
            a["ten"][:40], (" + " + lc[0]["ten"]) if lc else "", q["ten"][:40], (" + " + b["ten"][:30]) if b else ""),
            "loai": "he_hoan_thien", "uu_tien": 5, "nen_tang": "TO_HOP", "duong_dich": "noi_bo", "tin_hieu": th,
            "nguon": {"kho": "kho_co_che", "tep": ""}, "thanh_phan": [a["id"]] + [x["id"] for x in lc] + [q["id"]] + ([b["id"]] if b else [])}
        thu = {"ma": ma, "khung": kh, "tham": {}, "ql": qx}
        try:
            r = danh_gia(the, thu, cfg)
        except Exception as e:  # noqa: BLE001
            r = {"loi": "CHUA_DO_DUOC: %s" % str(e)[:160]}
        thu_n += 1
        ph = NG.dat(r.get("lai_pct_nam"), r.get("sut_giam_pct"), "loc_python", r.get("so_stop_out", 0), r.get("chay", False)) \
            if not r.get("loi") else {"dat": False, "ly_do": [r["loi"]]}
        with cn:
            cn.execute("INSERT OR REPLACE INTO to_hop VALUES (?,?)", (khoa, json.dumps({"the": the["id"], "kq": r, "loc": ph}, default=str)))
            if ph["dat"]:
                _luu(cn, the, "loc", "DAT_LOC", {"tot_nhat": {"thu": thu, "kq": r}, "loc": ph, "so_thu": 1})
                dat_n += 1
            _ghi_nk(cn, "to_hop", the["id"], "lai %s dd %s dat %s" % (r.get("lai_pct_nam"), r.get("sut_giam_pct"), ph["dat"]))
    in_ra("to_hop: thu %d, dat 65/15 %d" % (thu_n, dat_n))
    return {"thu": thu_n, "dat": dat_n}


# ---------------------------------------------------------------------------------------------------- (i) DOC MT5
def doc_htm(p: Path) -> dict:
    """Bao cao tester .htm (utf-16) -> net, pf, lenh, dd (chuoi 'x (y%)'), von_dau."""
    import html as H
    t = p.read_bytes().decode("utf-16", errors="ignore")
    if "<td" not in t:
        t = p.read_bytes().decode("utf-8", errors="ignore")
    o = [H.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S)]

    def g(k):
        try:
            return o[o.index(k) + 1]
        except ValueError:
            return None

    def so(x):
        try:
            return float(str(x).replace(" ", "").replace("\xa0", "").split("(")[0])
        except Exception:
            return None
    return {"net": so(g("Total Net Profit:")), "pf": so(g("Profit Factor:")), "lenh": so(g("Total Trades:")),
            "dd": g("Equity Drawdown Maximal:"), "von_dau": so(g("Initial Deposit:"))}


def doc_xml_toi_uu(p: Path) -> list[dict]:
    """Bao cao OPTIMIZER (.xml SpreadsheetML) -> list pass {cot: gia tri}."""
    t = p.read_bytes()
    t = t.decode("utf-16", errors="ignore") if t[:2] in (b"\xff\xfe", b"\xfe\xff") else t.decode("utf-8", errors="ignore")
    hang = []
    for row in re.findall(r"<Row[^>]*>(.*?)</Row>", t, re.S):
        hang.append([re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<Data[^>]*>(.*?)</Data>", row, re.S)])
    if not hang:
        return []
    dau = hang[0]
    ra = []
    for h in hang[1:]:
        d = {}
        for k, v in zip(dau, h):
            try:
                d[k] = float(v)
            except ValueError:
                d[k] = v
        ra.append(d)
    return ra


def _cot_loi_mt5(net: float | None, dd_chuoi: str | None, von: float, nam: float) -> dict:
    m = re.search(r"\(([\d.]+)%\)", str(dd_chuoi or ""))
    if net is None or m is None or not von:
        return {"dat": False, "ly_do": ["CHUA_DO_DUOC"]}
    lai = net / von / max(nam, 1e-6) * 100.0
    ph = NG.dat(lai, float(m.group(1)), "cuoi")
    ph.update(lai_pct_nam=round(lai, 2), sut_giam_pct=float(m.group(1)), nhan="MT5 lot that")
    return ph


def buoc_doc_mt5(cn, in_ra=print) -> dict:
    """Doc ket qua MT5 tra ve: so cai chay_lien_tuc (dong nguon=ong_dan) + reports/ong_dan/ket_qua_mt5/*.htm|*.xml."""
    cfg = cau_hinh()
    nam = (int(cfg.get("mt5_den", "2026.10.01")[:4]) - int(cfg.get("mt5_tu", "2016.01.01")[:4]))
    hang = {json.loads(x)["ten"]: json.loads(x) for x in HANG_CHO.read_text(encoding="utf-8").splitlines() if x.strip()} \
        if HANG_CHO.exists() else {}
    ket: dict[str, list] = {}
    so_cai = GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl"
    if so_cai.exists():
        for x in so_cai.read_text(encoding="utf-8").splitlines():
            if '"ong_dan"' not in x:
                continue
            r = json.loads(x)
            if r.get("nguon") == "ong_dan" and r.get("pha") != "TOI_UU":   # toi uu: doc file .xml ben duoi
                ket.setdefault(r.get("the_id", ""), []).append(r)
    KET_QUA_MT5.mkdir(parents=True, exist_ok=True)
    for f in sorted(KET_QUA_MT5.glob("od_*")):
        v = hang.get(f.stem) or {}
        tid = v.get("the_id")
        if not tid:
            continue
        if f.suffix.lower() in (".htm", ".html"):
            r = doc_htm(f); r.update(ten=f.stem, pha=v.get("pha"), von=v.get("von"))
            ket.setdefault(tid, []).append(r)
        elif f.suffix.lower() == ".xml":
            ps = doc_xml_toi_uu(f)
            von = float(v.get("von") or cfg.get("von", 1000.0))
            tot = None
            for p in ps:
                dd = p.get("Equity DD %")
                if isinstance(dd, float) and isinstance(p.get("Profit"), float):
                    ph = _cot_loi_mt5(p["Profit"], "(%s%%)" % dd, von, nam)
                    if ph["dat"] and (tot is None or p["Profit"] > tot["Profit"]):
                        tot = dict(p, _ph=ph)
            ket.setdefault(tid, []).append({"ten": f.stem, "pha": "TOI_UU", "so_pass": len(ps), "pass_dat_tot_nhat": tot})
    dem = {"DAT_CUOI": 0, "TRUOT_CUOI": 0, "CHUA_DO_DUOC": 0}
    with cn:
        for t, buoc, tt, kq in cac_the(cn):
            if t["id"] not in ket:
                continue
            ds = ket[t["id"]]
            ph_ds = []
            for r in ds:
                if r.get("pha") == "TOI_UU":
                    tot = r.get("pass_dat_tot_nhat")
                    ph_ds.append(tot["_ph"] if tot else {"dat": False, "ly_do": ["khong pass nao dat 80/10"]})
                elif r.get("loi"):
                    ph_ds.append({"dat": False, "ly_do": ["CHUA_DO_DUOC: %s" % r["loi"]]})
                else:
                    ph_ds.append(_cot_loi_mt5(r.get("net"), r.get("dd"), float(r.get("von") or cfg.get("von", 1000.0)), nam))
            if any(p["dat"] for p in ph_ds):
                moi = "DAT_CUOI"
            elif all("CHUA_DO_DUOC" in " ".join(p.get("ly_do", [])) for p in ph_ds):
                moi = "CHUA_DO_DUOC"
            else:
                moi = "TRUOT_CUOI"
            kq["mt5"] = {"ket_qua": ds, "phan_xu": ph_ds}
            _luu(cn, t, "doc_mt5", moi, kq)
            dem[moi] += 1
    in_ra("doc_mt5: %s (the co ket qua MT5: %d)" % (dem, len(ket)))
    return dem


# ---------------------------------------------------------------------------------------------------- TRANG THAI / BAO CAO
def trang_thai(cn) -> dict:
    d = {}
    for b, tt, n in cn.execute("SELECT buoc, trang_thai, COUNT(*) FROM the GROUP BY buoc, trang_thai"):
        d.setdefault(b, {})[tt] = n
    d["_so_phep_thu"] = cn.execute("SELECT COUNT(*) FROM thu").fetchone()[0]
    d["_so_to_hop"] = cn.execute("SELECT COUNT(*) FROM to_hop").fetchone()[0]
    d["_kho_co_che"] = {v: len(KHO.lay(v)) for v in KHO.VAI_TRO}
    return d


def ghi_bao_cao(cn) -> str:
    tt = trang_thai(cn)
    dong = ["# Ống dẫn: trạng thái (tự sinh bởi `python ong_dan.py bao_cao`)", "",
            "Mọi số là **MÔ PHỎNG** Python ở **lot thật** (ký quỹ, stop-out, `nhan/tai_khoan.chay_tk`). Phí: **PHÍ TẠM** "
            "(hồ sơ XM đã đo trong `config/chi_phi_do.json`) cho tới khi máy nhà đo `reports/phi_san/`. "
            "Ngưỡng lọc Python: sụt giảm < 65 %% và lãi > 15 %%/năm; chuẩn cuối 80/10 (đo ở MT5). OOS chỉ là nhãn.", "",
            "## Đếm theo bước", "", "```json", json.dumps(tt, ensure_ascii=False, indent=1), "```", "",
            "## Ứng viên đã tối ưu (tốt nhất mỗi thẻ)", "",
            "| Thẻ | Mã · khung | Lot | Lãi %/năm | Sụt % | Stop-out | Kẹt lâu nhất (ngày) | OOS (nhãn) | Lọc 65/15 |",
            "|---|---|---|---|---|---|---|---|---|"]
    for t, buoc, st, kq in cac_the(cn):
        tot = (kq or {}).get("tot_nhat")
        if not tot or not tot.get("kq") or tot["kq"].get("loi"):
            continue
        r, th = tot["kq"], tot["thu"]
        o = r.get("oos") or {}
        dong.append("| %s | %s %s | %s | %s | %s | %s | %s | %s | %s |" % (
            t.get("ten", t["id"])[:60], th["ma"], th["khung"], r.get("lot0"), r["lai_pct_nam"], r["sut_giam_pct"], r["so_stop_out"],
            r.get("ket_ngay_max"), ("%s / %s" % (o.get("lai_pct_nam"), o.get("sut_giam_pct"))) if o else "-",
            "ĐẠT" if (kq.get("loc") or {}).get("dat") else st))
    s = "\n".join(dong) + "\n"
    RA.mkdir(parents=True, exist_ok=True)
    (RA / "TRANG_THAI.md").write_text(s, encoding="utf-8")
    return s


def buoc_goi(cn, in_ra=print) -> dict:
    """Goi zip ma EA ngoai cho may nha (/workspace/goi_may_nha/, ngoai git) - nhan/goi_may_nha.py."""
    from nhan import goi_may_nha as GM
    try:
        r = GM.dong_goi()
    except Exception as e:  # noqa: BLE001
        r = {"loi": str(e)[:200]}
    with cn:
        _ghi_nk(cn, "goi", "*", json.dumps(r, ensure_ascii=False))
    in_ra("goi_may_nha: %s" % r)
    return r


def ghi_do_nguoc(cn, tep: Path | None = None) -> str:
    """reports/ong_dan/DO_NGUOC_STATEMENT.md: moi statement co tung lenh -> cach xu li lenh do nguoc (SUY TU STATEMENT),
    so tac gia (rieng, chua do) va so Python (MÔ PHỎNG, PHÍ TẠM) neu box co gia cua ma do."""
    tep = tep or (RA / "DO_NGUOC_STATEMENT.md")
    hang = []
    for t, buoc, tt, kq in cac_the(cn):
        if t.get("nen_tang") != "STATEMENT" or not t.get("do_nguoc"):
            continue
        dn, tg = t["do_nguoc"], t.get("so_tac_gia") or {}
        r = ((kq or {}).get("tot_nhat") or {}).get("kq") or {}
        py = ("CHƯA ĐO ĐƯỢC" if not r or r.get("loi") else "%s%%/năm · DD %s%% · %s năm" % (
            r.get("lai_pct_nam"), r.get("sut_giam_pct"), r.get("so_nam")))
        if r and r.get("loi"):
            py += " (%s)" % r["loi"][:60]
        hang.append((dn.get("so_lenh", 0), t, dn, tg, py))
    hang.sort(key=lambda z: -z[0])
    def f(x, d=4):
        return "—" if x is None else (("%." + str(d) + "g") % x if isinstance(x, float) else str(x))
    d = ["# Dò ngược statement có từng lệnh (`python ong_dan.py nhan` → `nhan/nhap_tay.do_nguoc`)", "",
         "Số trong bảng là **SUY TỪ STATEMENT** (trung vị trên các rổ lệnh), không phải số đo. Rổ = chuỗi lệnh cùng mã cùng "
         "chiều chồng lên nhau. Bước DCA tính giữa hai lệnh liền nhau trong rổ; «ngược» = tỉ lệ bước đi ngược giá (nhồi khi lỗ). "
         "TP rổ = (giá đóng bình quân − giá vốn bình quân) theo chiều, chỉ với rổ đóng gần như cùng lúc và có lãi. "
         "Giờ = giờ server của tác giả. Cột «Tác giả» là SỐ TÁC GIẢ (chưa đo). Cột «Python» là MÔ PHỎNG, PHÍ TẠM "
         "(lệnh vào của statement + quản lí dò ngược, chạy trong đúng khoảng thời gian statement).", "",
         "| Statement | Mã | Kỳ | Lệnh | Rổ ≥2 tầng | Tầng max | Bước DCA pip (%) · ngược | Hệ số lot | TP rổ pip (%) | "
         "Giờ mở chính | Tác giả (chưa đo) | Python |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, t, dn, tg, py in hang:
        ma = ",".join(list((dn.get("ma") or {}).keys())[:3])
        gio = dn.get("gio_hoat_dong") or []
        gio_s = ("%d–%d h" % (min(gio), max(gio))) if gio and len(gio) < 20 else ("cả ngày" if gio else "—")
        tgs = "; ".join("%s %s" % (k, tg[k]) for k in ("von_dau", "lai_rong", "sut_giam", "khung") if tg.get(k)) or "—"
        d.append("| %s | %s | %s → %s | %s | %s/%s | %s | %s (%s %%) · %s | %s (max %s) | %s (%s %%) | %s | %s | %s |" % (
            t["ten"][:70].replace("|", "/"), ma, (dn.get("tu") or "")[:10], (dn.get("den") or "")[:10], dn.get("so_lenh"),
            dn.get("so_ro_nhieu_tang"), dn.get("so_ro"), dn.get("tang_max"), f(dn.get("buoc_dca_pip")), f(dn.get("buoc_dca_pct")),
            f(dn.get("ty_le_buoc_nguoc"), 2), f(dn.get("he_so_lot")), f(dn.get("he_so_lot_max")), f(dn.get("tp_ro_pip")),
            f(dn.get("tp_ro_pct")), gio_s, tgs.replace("|", "/"), py))
    d += ["", "Tệp gốc: cột `nguon.tep` của thẻ trong `data/ong_dan/trang_thai.sqlite` (nằm trong `data/seeker_da_nguon/`, "
          "không vào git; có trong gói máy nhà nếu kèm EA)."]
    vb = "\n".join(d) + "\n"
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text(vb, encoding="utf-8")
    return str(tep)


def chay_het(cn, in_ra=print, **kw) -> dict:
    buoc_nhan(cn, in_ra)
    buoc_phan_loai(cn, in_ra)
    buoc_quyet_dinh(cn, in_ra)
    buoc_toi_uu(cn, kw.get("toi_da"), kw.get("ngan_sach"), in_ra)
    buoc_loc(cn, in_ra)
    buoc_boc(cn, in_ra)
    buoc_to_hop(cn, kw.get("ngan_sach_to_hop"), in_ra)
    buoc_sinh_mt5(cn, in_ra)
    if kw.get("goi", True):
        buoc_goi(cn, in_ra)
    buoc_doc_mt5(cn, in_ra)
    ghi_bao_cao(cn)
    ghi_do_nguoc(cn)
    try:                                   # danh sach URL bi chan cho chu du an mo tay (khong vuot chan)
        import sys as _sys
        _sys.path.insert(0, str(GOC))
        from tru import seeker as _SK
        in_ra("url_bi_chan: %s" % _SK.url_bi_chan(GOC / "reports" / "URL_BI_CHAN_THEM.md"))
    except Exception as e:  # noqa: BLE001
        in_ra("url_bi_chan: CHUA_CHAY_DUOC (%s)" % str(e)[:120])
    return trang_thai(cn)
