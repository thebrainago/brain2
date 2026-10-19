# -*- coding: utf-8 -*-
"""dich_llm.py - BUOC DICH BANG LLM cua ong dan, chay RIENG tren MAY NHA (19/10/2026).

`python ong_dan.py dich_llm [--gioi_han N] [--luong K]`
  - Hang cho: the duong `llm` (Python / freqtrade / Pine) + EA MQL ma bo dich khong-LLM bo qua (`mt5_truc_tiep` vi "bo dich
    khong ra chan", ma co tren may) - uu tien 28 he top cua Seeker, roi the LLM, roi EA.
  - Moi ma nguon goi LLM MOT lan: cache theo sha256 ma nguon o data/ong_dan/dich_llm/<hash>.json (data/ khong vao git).
  - Ket qua (spec DSL hoac ham Python `tin_hieu(df)`) KIEM TU DONG tren gia mau: dung dinh dang, khong nhin truoc (tin hieu
    tren df[:k] trung tin hieu day du o moi nen < k), co ra lenh (>= SO_LENH_MIN). Ma Python chay trong hop cat
    (`nhan/hop_cat_llm.py`), khong exec trong tien trinh chinh.
  - Dat -> the ve buoc `quyet_dinh`, duong `spec_dsl` / `python_llm` -> `toi_uu` / `loc` chay tiep nhu the khac.
  - So lan goi + token ghi vao reports/ong_dan/DICH_LLM.md va data/ong_dan/dich_llm/nhat_ky.jsonl. Khong ghi khoa.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import cau_llm as LLM
from nhan import hop_cat_llm as HC
from nhan import nguon_lenh as NL
from nhan import nhap_tay as NT

GOC = Path(__file__).resolve().parent.parent
CACHE = GOC / "data" / "ong_dan" / "dich_llm"
BAO_CAO = GOC / "reports" / "ong_dan" / "DICH_LLM.md"
SO_LENH_MIN = 3
_KHOA = threading.Lock()
_TH: dict = {}


def bam(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:24]


def ngon_ngu(t: dict, vb: str) -> str:
    nt = (t.get("nen_tang") or "").upper()
    if "TRADINGVIEW" in nt or "PINE" in nt or "//@version" in vb:
        return "Pine Script (TradingView)"
    if "IStrategy" in vb:
        return "Python freqtrade (IStrategy)"
    if nt.startswith("MQL4") or "MT4" in nt:
        return "MQL4"
    if nt.startswith("MQL") or "MT5" in nt:
        return "MQL5"
    return "Python"


def _tep(t: dict) -> Path | None:
    p = (t.get("nguon") or {}).get("tep")
    if not p:
        return None
    f = GOC / p
    return f if f.exists() and f.is_file() else None


def can_dich(t: dict, tt: str) -> str | None:
    """-> "llm" | "ea_bo_qua" | None."""
    if t.get("loai") != "he_hoan_thien":
        return None
    if tt == "LLM" or t.get("duong_dich") == "llm":
        return "llm"
    if t.get("duong_dich") == "mt5_truc_tiep" and str(t.get("ly_do_duong", "")).startswith("bo dich khong ra chan"):
        return "ea_bo_qua"
    return None


def danh_sach_cho(cn) -> list[dict]:
    """The cho dich, da sap uu tien. Moi phan tu: {the, buoc, tt, kq, nhom, tep, top28}."""
    from nhan import ong_dan as OD
    ra = []
    for t, b, tt, kq in OD.cac_the(cn):
        nh = can_dich(t, tt)
        if not nh:
            continue
        if (t.get("dich_llm") or {}).get("trang_thai") in ("DAT", "HONG") and t["dich_llm"].get("bam"):
            continue                                    # da dich (cache) - lan sau chi lam lai khi ma doi
        ra.append({"the": t, "buoc": b, "tt": tt, "kq": kq, "nhom": nh, "tep": _tep(t),
                   "top28": bool((t.get("seeker") or {}).get("top28"))})
    ra.sort(key=lambda x: (int(x["the"].get("dich_llm_loi_lan") or 0) >= 2, not x["top28"], x["nhom"] != "llm",
                           x["tep"] is None, int(x["the"].get("uu_tien", 9)), x["the"]["id"]))
    return ra


def gia_mau(cfg: dict | None = None, n: int = 3000) -> tuple[pd.DataFrame, str]:
    """Gia de kiem: n nen H1 cuoi cua ma dau tien co du lieu; khong co -> buoc ngau nhien co dinh hat giong (ghi ro)."""
    from nhan import ong_dan as OD
    try:
        cfg = cfg or OD.cau_hinh()
        for m in OD.ma_co_du_lieu(cfg):
            df = OD.gia(m, "H1", cfg)
            if df is not None and len(df) >= 600:
                return df.iloc[-n:], "gia %s H1 (%d nen)" % (m, min(n, len(df)))
    except Exception:
        pass
    r = np.random.default_rng(20261019)
    x = 1.0 + np.cumsum(r.normal(0, 0.0012, n))
    i = pd.date_range("2024-01-01", periods=n, freq="h")
    h = x + np.abs(r.normal(0, 0.0006, n)); lo = x - np.abs(r.normal(0, 0.0006, n))
    o = np.r_[x[0], x[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum.reduce([o, x, h]), "low": np.minimum.reduce([o, x, lo]), "close": x},
                        index=i), "gia gia lap (khong co du lieu that, hat 20261019)"


def kiem_tra(d: dict, df: pd.DataFrame) -> dict:
    """Kiem ket qua LLM (spec hoac python) tren gia mau. -> {dat, kieu, ly_do[], so_lenh}."""
    n = len(df)
    # 19/10/2026: 3 diem cat chi kiem ~3 nen cuoi cua moi doan -> rolling(center=True) lot qua (18 lenh, DAT).
    # Nay 24 diem cat rai 30-99 % + mot diem lech (khong trung nhip 24 nen).
    cat = sorted({int(n * f) for f in np.linspace(0.30, 0.99, 24)} | {int(n * 0.8) + 7})
    if d.get("spec"):
        kieu = "spec"
        try:
            s = np.asarray(NL.tin_hieu_spec(d["spec"], df), int)
            doan = {k: np.asarray(NL.tin_hieu_spec(d["spec"], df.iloc[:k]), int) for k in cat}
        except Exception as e:  # noqa: BLE001
            return {"dat": False, "kieu": kieu, "ly_do": ["spec khong chay duoc: %s" % str(e)[:160]], "so_lenh": 0}
    elif (d.get("python") or "").strip():
        kieu = "python"
        r = HC.chay(d["python"], df, cat)
        if not r.get("ok"):
            return {"dat": False, "kieu": kieu, "ly_do": ["python: %s" % r.get("loi")], "so_lenh": 0}
        s = np.asarray(r["day_du"], int)
        doan = {int(k): np.asarray(v, int) for k, v in r["doan"].items()}
    else:
        return {"dat": False, "kieu": "", "ly_do": ["LLM khong ra spec hay python dung (%s)" %
                                                     "; ".join((d.get("chua_dich") or [])[:2])[:160]], "so_lenh": 0}
    ly = []
    if len(s) != n:
        ly.append("do dai tin hieu %d != %d" % (len(s), n))
    if not set(np.unique(s)).issubset({-1, 0, 1}):
        ly.append("tin hieu ngoai {-1,0,1}")
    for k, v in doan.items():
        if len(v) != k or not np.array_equal(v, s[:k]):
            lech = int(np.sum(v[:min(k, len(v))] != s[:min(k, len(v))])) if len(v) else k
            ly.append("NHIN TRUOC: cat o nen %d thi %d nen doi tin hieu" % (k, lech))
            break
    so = int(np.count_nonzero(s[1:] != s[:-1])) if len(s) else 0
    so_vao = int(np.count_nonzero((s != 0) & (np.r_[0, s[:-1]] != s)))
    if so_vao < SO_LENH_MIN:
        ly.append("chi ra %d lenh tren gia mau (< %d)" % (so_vao, SO_LENH_MIN))
    return {"dat": not ly, "kieu": kieu, "ly_do": ly, "so_lenh": so_vao, "so_doi": so}


def _doc_cache(h: str) -> dict | None:
    f = CACHE / (h + ".json")
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def _ghi_cache(h: str, d: dict) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / (h + ".json")).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def dich_mot(vb: str, nn: str, h: str, client=None, c: dict | None = None) -> tuple[dict, bool]:
    """-> (ket qua boc tach, tu_cache). Chi goi LLM khi chua co cache THANH CONG cho hash nay."""
    d = _doc_cache(h)
    if d and d.get("trang_thai") == "OK":
        return d, True
    d = LLM.boc_tach(vb, nn, client=client, c=c)
    if d.get("trang_thai") == "OK":
        _ghi_cache(h, dict(d, ngon_ngu=nn, luc=time.strftime("%Y-%m-%dT%H:%M:%S")))
    return d, False


def tin_hieu_python(ma: str, df: pd.DataFrame) -> np.ndarray:
    """Tin hieu cua the `python_llm` cho toi_uu: chay hop cat MOT lan moi (ma, gia), cache bo nho + dia."""
    k = bam(ma.encode("utf-8") + str((len(df), str(df.index[0]), str(df.index[-1]), float(df["close"].iloc[-1]))).encode())
    if k in _TH:
        return _TH[k]
    f = CACHE / "tin_hieu" / (k + ".npy")
    if f.exists():
        _TH[k] = np.load(f)
        return _TH[k]
    r = HC.chay(ma, df, [])
    if not r.get("ok"):
        raise RuntimeError("python_llm: %s" % r.get("loi"))
    s = np.asarray(r["day_du"], int)
    f.parent.mkdir(parents=True, exist_ok=True)
    np.save(f, s)
    _TH[k] = s
    return s


def buoc_dich_llm(cn, gioi_han: int | None = None, luong: int = 4, in_ra=print, client=None, c: dict | None = None,
                  cfg: dict | None = None) -> dict:
    from nhan import ong_dan as OD
    t0 = time.time()
    c = c or LLM.cau_hinh()
    co = LLM.co_khoa(c) or client is not None
    ds = danh_sach_cho(cn)
    tong_cho = len(ds)
    thieu_ma = [x for x in ds if x["tep"] is None]
    ds = [x for x in ds if x["tep"] is not None]
    if gioi_han is not None:
        ds = ds[:int(gioi_han)]
    tk0 = {k: v for k, v in LLM.THONG_KE.items() if k != "theo_model"}
    dem = {"cho": tong_cho, "thieu_ma": len(thieu_ma), "lam": 0, "goi_moi": 0, "tu_cache": 0, "dat": 0, "hong": 0,
           "loi_llm": 0, "chua_chay_duoc": 0}
    if not co:
        dem["chua_chay_duoc"] = len(ds)
        in_ra("dich_llm: CHUA CHAY DUOC - khong co khoa tren may nay (%d the cho). Chay tren may nha." % tong_cho)
        ghi_bao_cao(dem, LLM.THONG_KE, "", 0.0, ds_cho=danh_sach_cho(cn))
        return dem
    df, nguon_gia = gia_mau(cfg)
    # 1) doc ma + hash, gom theo hash (nhieu the cung mot ma -> mot lan goi)
    viec = {}
    for x in ds:
        b = x["tep"].read_bytes()[:800000]
        vb = NT.doc_vb(b)
        h = bam(b)
        x["bam"] = h
        viec.setdefault(h, {"vb": vb, "nn": ngon_ngu(x["the"], vb), "the": []})["the"].append(x)
    # 2) goi LLM song song (cho o mang), cache ghi ngay sau moi lan goi
    kq_h = {}

    def _lam(h):
        v = viec[h]
        try:
            d, tu_c = dich_mot(v["vb"], v["nn"], h, client=client, c=c)
        except Exception as e:  # noqa: BLE001 - mot the loi khong duoc lam sap ca luot (19/10/2026)
            d, tu_c = {"trang_thai": "LOI", "ghi_chu": "%s: %s" % (type(e).__name__, str(e)[:200])}, False
        with _KHOA:
            kq_h[h] = (d, tu_c)

    with ThreadPoolExecutor(max_workers=max(1, int(luong))) as ex:
        list(ex.map(_lam, list(viec)))
    # 3) kiem tu dong + ghi trang thai (tuan tu, mot ket noi sqlite)
    nk = []
    for h, v in viec.items():
        d, tu_c = kq_h[h]
        dem["tu_cache" if tu_c else "goi_moi"] += 1
        if d.get("trang_thai") != "OK":
            dem["loi_llm"] += len(v["the"])
            for x in v["the"]:
                nk.append({"the": x["the"]["id"], "bam": h, "ket_qua": "LOI_LLM", "ghi_chu": d.get("ghi_chu")})
                # 19/10/2026: dem so lan LOI_LLM; the loi mai xep CUOI hang (truoc day dung dau hang moi luot,
                # tra tien goi lai, 200 the loi = vong dich nen dung vi "3 luot khong lam duoc the nao")
                x["the"]["dich_llm_loi_lan"] = int(x["the"].get("dich_llm_loi_lan") or 0) + 1
                with cn:
                    OD._luu(cn, x["the"])
            continue                                     # khong ghi HONG: lan sau goi lai
        try:
            kt = kiem_tra(d, df)
        except Exception as e:  # noqa: BLE001 - ket qua cache OK nhung kiem loi -> HONG, khong sap ca luot
            kt = {"dat": False, "kieu": "", "ly_do": ["kiem_tra loi: %s: %s" % (type(e).__name__, str(e)[:160])],
                  "so_lenh": 0}
        for x in v["the"]:
            t = x["the"]
            dem["lam"] += 1
            t["dich_llm"] = {"trang_thai": "DAT" if kt["dat"] else "HONG", "bam": h, "kieu": kt["kieu"],
                             "so_lenh_mau": kt["so_lenh"], "ly_do": kt["ly_do"], "model": d.get("model"),
                             "gia_mau": nguon_gia, "luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "nhom": x["nhom"],
                             "co_che": d.get("co_che") or [], "quan_tri": d.get("quan_tri") or {},
                             "chua_dich": d.get("chua_dich") or []}
            if kt["dat"]:
                dem["dat"] += 1
                if kt["kieu"] == "spec":
                    t["duong_dich"] = "spec_dsl"
                    t["tin_hieu"] = {"kieu": "spec", "specs": d["spec"], "khoang": {}}
                else:
                    t["duong_dich"] = "python_llm"
                    t["tin_hieu"] = {"kieu": "python_llm", "ma": d["python"], "khoang": {}}
                t["ly_do_duong"] = "LLM dich (%s) -> %s, kiem tu dong DAT: %d lenh tren %s, khong nhin truoc" % (
                    d.get("model"), kt["kieu"], kt["so_lenh"], nguon_gia)
                with cn:
                    OD._luu(cn, t, "quyet_dinh", t["duong_dich"].upper())
                    OD._ghi_nk(cn, "dich_llm", t["id"], "DAT %s %s" % (kt["kieu"], h))
            else:
                dem["hong"] += 1
                with cn:
                    OD._luu(cn, t)
                    OD._ghi_nk(cn, "dich_llm", t["id"], "HONG %s" % "; ".join(kt["ly_do"])[:300])
            nk.append({"the": t["id"], "bam": h, "ket_qua": t["dich_llm"]["trang_thai"], "kieu": kt["kieu"],
                       "ly_do": kt["ly_do"][:3], "tu_cache": tu_c})
    tk1 = {k: LLM.THONG_KE[k] - tk0.get(k, 0) for k in tk0}
    dem.update({"so_lan_goi": tk1["so_lan_goi"], "token_vao": tk1["token_vao"], "token_ra": tk1["token_ra"],
                "doi_du_phong": tk1["doi_du_phong"], "so_lan_loi_http": tk1["so_lan_loi"]})
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(CACHE / "nhat_ky.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "dem": dem, "the": nk}, ensure_ascii=False) + "\n")
    ghi_bao_cao(dem, LLM.THONG_KE, nguon_gia, time.time() - t0, ds_cho=danh_sach_cho(cn))
    in_ra("dich_llm: %s" % json.dumps(dem, ensure_ascii=False))
    return dem


def ghi_bao_cao(dem: dict, tk: dict, nguon_gia: str, giay: float, ds_cho: list | None = None, tep: Path | None = None) -> str:
    tep = Path(tep or BAO_CAO)
    ds_cho = ds_cho or []
    from collections import Counter
    nh = Counter(x["nhom"] for x in ds_cho)
    d = ["# Bước dịch bằng LLM (máy nhà)", "",
         "Lần chạy %s, %.0f giây. Giá mẫu để kiểm: %s." % (time.strftime("%d/%m/%Y %H:%M"), giay, nguon_gia or "CHƯA CHẠY"), "",
         "| Chỉ số | Giá trị |", "|---|---|"]
    for k, ten in (("cho", "Thẻ chờ dịch lúc bắt đầu"), ("thieu_ma", "Thẻ thiếu mã trên máy (chưa dịch được)"),
                   ("lam", "Thẻ đã kiểm lần này"), ("dat", "Đạt kiểm tự động → chạy tiếp toi_uu/loc"),
                   ("hong", "Không đạt kiểm (lí do trong thẻ)"), ("loi_llm", "Lỗi LLM (sẽ thử lại)"),
                   ("goi_moi", "Mã nguồn gọi LLM mới"), ("tu_cache", "Mã nguồn lấy từ cache"),
                   ("so_lan_goi", "Số lần gọi API"), ("so_lan_loi_http", "Lần gọi lỗi"),
                   ("doi_du_phong", "Lần chuyển sang model dự phòng"), ("token_vao", "Token vào"), ("token_ra", "Token ra"),
                   ("chua_chay_duoc", "CHƯA CHẠY ĐƯỢC (không có khoá)")):
        if k in dem:
            d.append("| %s | %s |" % (ten, dem[k]))
    d += ["", "Còn chờ sau lần chạy: %d thẻ (LLM: %d, EA bộ dịch không-LLM bỏ qua: %d, top 28: %d)." % (
        len(ds_cho), nh.get("llm", 0), nh.get("ea_bo_qua", 0), sum(1 for x in ds_cho if x["top28"])), "",
        "Theo model (cộng dồn trong tiến trình): " + (", ".join("%s: %d lần, %d/%d token" % (
            m, v["so_lan_goi"], v["token_vao"], v["token_ra"]) for m, v in (tk.get("theo_model") or {}).items()) or "chưa gọi"),
        "", "Kết quả dịch là nhãn LLM, cần MT5 xác nhận; số Python là MÔ PHỎNG, PHÍ TẠM."]
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(d) + "\n", encoding="utf-8")
    return str(tep)
