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
import os
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


#: model dich hien tai (config/llm_dich.json); the HONG voi model khac (vd flash) va ly do thuoc nhom thu lai -> dich lai
MODEL_HIEN = ""


def _model_hien() -> str:
    try:
        return str(LLM.cau_hinh().get("model") or "")
    except Exception:
        return ""


def danh_sach_cho(cn) -> list[dict]:
    """The cho dich, da sap uu tien. Moi phan tu: {the, buoc, tt, kq, nhom, tep, top28}."""
    from nhan import ong_dan as OD
    global MODEL_HIEN
    MODEL_HIEN = _model_hien()
    ra = []
    for t, b, tt, kq in OD.cac_the(cn):
        nh = can_dich(t, tt)
        if not nh:
            continue
        dl = t.get("dich_llm") or {}
        if dl.get("trang_thai") in ("DAT", "BO_QUA"):
            continue
        if int(t.get("dich_llm_loi_lan") or 0) >= SO_LAN_TOI_DA:
            continue                                    # 20/10/2026: LOI_LLM lap lai -> da/se ghi BO_QUA
        if dl.get("trang_thai") == "HONG" and dl.get("bam"):
            # 20/10/2026: HONG chi duoc lam lai khi phien prompt/bo kiem moi hon VA ly do thuoc nhom do loi phia ta
            moi = int(dl.get("phien") or 1) < LLM.PHIEN_PROMPT or (MODEL_HIEN and dl.get("model") and dl["model"] != MODEL_HIEN)
            if not moi or (dl.get("nhom_ly_do") or nhom_ly_do(dl.get("ly_do"))) not in NHOM_THU_LAI:
                continue                                # 20/10/2026: doi sang model manh moi -> HONG do loi phia ta duoc dich lai
        ra.append({"the": t, "buoc": b, "tt": tt, "kq": kq, "nhom": nh, "tep": _tep(t),
                   "top28": bool((t.get("seeker") or {}).get("top28"))})
    ra.sort(key=lambda x: (int(x["the"].get("dich_llm_loi_lan") or 0) >= 2, not x["top28"], x["nhom"] != "llm",
                           x["tep"] is None, int(x["the"].get("uu_tien", 9)), x["the"]["id"]))
    return ra


def gia_mau(cfg: dict | None = None, n: int = 3000) -> tuple[pd.DataFrame, str]:
    """20/10/2026: da thu 12000 nen - dau ra A/B cua 5 model cho KET QUA Y HET 3000 nen (IT_LENH la do tin hieu 0 lenh
    that, khong do it du lieu) -> giu 3000. Gia de kiem: n nen H1 cuoi cua ma dau tien co du lieu; khong co -> buoc ngau nhien co dinh hat giong (ghi ro)."""
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
    sp_ds = d.get("spec")
    sp_ds = sp_ds if isinstance(sp_ds, list) else ([sp_ds] if isinstance(sp_ds, dict) else [])
    # 20/10/2026: chuan hoa ca spec trong cache cu (cat_len -> cheo_len, thieu "cua", chieu "buy") truoc khi chay
    sp_ds = [LLM.chuan_hoa_spec(x) for x in sp_ds if isinstance(x, dict)]
    sp_ds = [x for x in sp_ds if not LLM.kiem_spec(x)]
    if sp_ds:
        kieu = "spec"
        d = dict(d, spec=sp_ds)
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
    r = {"dat": not ly, "kieu": kieu, "ly_do": ly, "so_lenh": so_vao, "so_doi": so}
    if not ly and kieu == "spec":
        r["spec"] = d["spec"]          # ban da chuan hoa -> ghi vao the (toi_uu chay dung spec nay)
    return r


#: Nhom ly do HONG (20/10/2026) - bao cao DICH_LLM.md dem theo nhom de biet hong o dau (LLM, prompt, bo kiem, EA).
NHOM_LY_DO = [
    ("NHIN_TRUOC", ("NHIN TRUOC",)),                     # truoc "python: " - "python: shift am (nhin truoc)"
    ("LOI_LLM", ("LOI_LLM",)),
    ("PY_CAM_CU_PHAP", ("python: cam ", "python: loi cu phap", "python: khong co ham", "python: top-level")),
    ("PY_LOI_CHAY", ("python: ",)),
    ("SPEC_KHONG_CHAY", ("spec khong chay duoc",)),
    ("KHONG_RA_SPEC_PY", ("LLM khong ra spec hay python",)),
    ("IT_LENH", ("chi ra ",)),
    ("SAI_DINH_DANG", ("do dai tin hieu", "tin hieu ngoai")),
    ("KIEM_LOI", ("kiem_tra loi",)),
]
#: Nhom co the do LOI PHIA TA (prompt / chuan hoa / hop cat) -> duoc kiem lai khi PHIEN_PROMPT tang.
NHOM_THU_LAI = {"PY_CAM_CU_PHAP", "SPEC_KHONG_CHAY", "KHONG_RA_SPEC_PY", "KIEM_LOI", "PY_LOI_CHAY", "LOI_LLM"}
#: So lan that bai (LOI_LLM + HONG o cac phien prompt) toi da; qua -> BO_QUA kem ly do, khong goi LLM nua.
SO_LAN_TOI_DA = 3


def nhom_ly_do(ly_do: list | str | None) -> str:
    t = "; ".join(ly_do) if isinstance(ly_do, list) else str(ly_do or "")
    tl = t.lower()
    for ten, mau in NHOM_LY_DO:
        if any(m.lower() in tl for m in mau):
            return ten
    return "KHAC" if t else "KHONG_RO"


def thong_ke_hong(cn) -> dict:
    """Dem the da dich theo trang thai + nhom ly do (tu CSDL, khong goi LLM). Chay duoc tren box lan may nha."""
    from collections import Counter
    from nhan import ong_dan as OD
    tt, nh, vd = Counter(), Counter(), {}
    for t, b, _tt, kq in OD.cac_the(cn):
        dl = t.get("dich_llm") or {}
        if not dl:
            continue
        tt[dl.get("trang_thai", "?")] += 1
        if dl.get("trang_thai") in ("HONG", "BO_QUA"):
            g = dl.get("nhom_ly_do") or nhom_ly_do(dl.get("ly_do"))
            nh[g] += 1
            vd.setdefault(g, "; ".join(dl.get("ly_do") or [])[:160])
    return {"trang_thai": dict(tt), "nhom_ly_do": dict(nh), "vi_du": vd}


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


def kiem_tinh(d: dict, df: pd.DataFrame | None = None) -> list[str]:
    """20/10/2026: bo kiem TINH (khong chay ma) cho ban dich python - bat cac kieu 0 lenh do tren dau ra A/B
    (data/ong_dan/ab_model): tin hieu gia toan 0, khong bao gio gan 1/-1, cung gia tuyet doi lech thang gia mau."""
    import re
    py = (d.get("python") or "").strip()
    if not py:
        return []
    ly = []
    gan_khac_0 = re.search(r"(=\s*-?1\b|append\(\s*-?1\s*\)|np\.where|np\.select|np\.sign|[-+*]\s*1\b|astype|\?\s*-?1)", py)
    if re.search(r"return\s*(\[\s*0\s*\]\s*\*|np\.zeros|\[0 for)", py) and not gan_khac_0:
        ly.append("tin hieu gia: ham tra mang toan 0, khong co nhanh nao gan 1/-1")
    elif not gan_khac_0:
        ly.append("khong thay cho nao gan tin hieu 1 hoac -1")
    if df is not None and len(df):
        lo, hi = float(df["low"].min()), float(df["high"].max())
        for m in re.finditer(r"(?<![\w.])(\d+\.\d+|\d{3,})(?![\w.])", py):
            v = float(m.group(1))
            dong = py[max(0, py.rfind("\n", 0, m.start())):m.start()].lower()
            if v > 0 and (v > 20 * hi or v < lo / 20) and re.search(r"(gia|price|central|level|muc|trung_tam)", dong) \
                    and not re.search(r"(point|diem|pips?|period|n_|so_|max_|count|candles|nen)", dong):
                ly.append("cung gia tuyet doi %s (gia mau %.5g-%.5g): quy ve tuong doi (pct / ATR / cao-thap N nen)"
                          % (m.group(1), lo, hi))
                break
    return ly


def can_sua(kt: dict, d: dict) -> bool:
    """Ket qua kiem_tra co dang SUA DUOC bang mot lan hoi lai khong (co ma ma 0-it lenh / nhin truoc / loi chay)."""
    if kt.get("dat") or not (d.get("spec") or (d.get("python") or "").strip()):
        return False                       # khong co ma = LLM tu noi khong dich duoc -> hoi lai la phi tien
    return any(("lenh tren gia mau" in x) or ("NHIN TRUOC" in x) or x.startswith("python:") or
               x.startswith("spec khong chay") for x in kt.get("ly_do") or [])


def dich_mot(vb: str, nn: str, h: str, client=None, c: dict | None = None,
             df: pd.DataFrame | None = None, nguon_gia: str = "") -> tuple[dict, bool]:
    """-> (ket qua boc tach, tu_cache). Chi goi LLM khi chua co cache THANH CONG cho hash nay."""
    d = _doc_cache(h)
    if d and d.get("trang_thai") == "OK":
        # 20/10/2026: cache cua phien prompt cu KHONG co spec/python (thuong do ma bi cat cut mat OnTick) -> goi lai
        # voi ban rut gon moi; cache co spec/python -> chi kiem lai (chuan hoa moi), khong ton luot goi.
        cm = str((c or LLM.cau_hinh()).get("model") or "")
        cung_model = not d.get("model") or not cm or d.get("model") == cm or not (client is not None or LLM.co_khoa(c))
        co_ma = d.get("spec") or (d.get("python") or "").strip()
        if cung_model and (int(d.get("phien") or 1) >= LLM.PHIEN_PROMPT or co_ma):
            return d, True                              # khac model + co khoa -> goi lai bang model manh hien tai
        # 20/10/2026 (kiem chi phi): 36 ma DA DAT hom 19/10 bi dich lai vi (1) trang_thai.sqlite tren may nha bi ban
        # chup tu box ghi de (goi_may_nha) -> mat trang thai DAT, (2) cache khac model -> luon goi lai. Nay: cache khac
        # model ma VAN DAT bo kiem hien tai -> dung lai, khong goi.
        if co_ma and df is not None:
            try:
                kt0 = kiem_tra(d, df)
            except Exception:  # noqa: BLE001
                kt0 = {"dat": False}
            if kt0.get("dat"):
                return d, True
        # 20/10/2026: "khong ra spec/python" voi >= 2 model khac nhau -> khong goi lai (tru khi ghi de bang tay)
        if len(model_khong_ra(d)) >= SO_MODEL_KHONG_RA and not cho_dich_lai(h):
            return dict(d, ghi_chu="KHONG_RA_SPEC_PY o %d model - khong dich lai (ghi de: %s)" % (
                len(model_khong_ra(d)), DICH_LAI.name)), True
    if client is None and not LLM.co_khoa(c):
        return {"trang_thai": "CHUA_CHAY_DUOC", "ghi_chu": "khong co khoa, khong co cache dung duoc"}, False
    # 20/10/2026 (kiem chi phi): hai tien trinh (buoc 5 thu + dieu_phoi) cung lay dau hang -> 20 ma bi tra tien 2 lan.
    # Giu cho theo hash: tien trinh khac dang dich hash nay -> bo qua luot nay (lan sau lay tu cache).
    giu = _giu_cho(h, c)
    if giu is None:
        return {"trang_thai": "DANG_DICH", "ghi_chu": "tien trinh khac dang dich ma nay"}, False
    try:
        d0 = _doc_cache(h)
        cm = str((c or {}).get("model") or "")
        if d0 and d0.get("trang_thai") == "OK" and (not d or d0.get("luc") != d.get("luc")) \
                and (not cm or d0.get("model") == cm) and int(d0.get("phien") or 1) >= LLM.PHIEN_PROMPT:
            return d0, True                             # tien trinh khac vua dich xong trong luc cho
        return _dich_that(vb, nn, h, client, c, df, nguon_gia), False
    finally:
        _tha_cho(giu)


SO_MODEL_KHONG_RA = 2
#: Ghi de bang tay: moi dong mot hash (24 ky tu) hoac "*" = dich lai het; hoac bien moi truong BRAIN_DICH_LAI=1
DICH_LAI = CACHE / "dich_lai.txt"


def model_khong_ra(d: dict | None) -> set:
    """Cac model da tra 'khong ra spec/python' cho ma nay: lich su hong_theo_model + chinh ban cache neu rong."""
    if not d:
        return set()
    ra = {m for m, n in (d.get("hong_theo_model") or {}).items() if n == "KHONG_RA_SPEC_PY"}
    if d.get("trang_thai") == "OK" and d.get("model") and not d.get("spec") and not (d.get("python") or "").strip():
        ra.add(d["model"])
    return ra


def cho_dich_lai(h: str) -> bool:
    if os.environ.get("BRAIN_DICH_LAI") == "1":
        return True
    f = CACHE / DICH_LAI.name
    try:
        ds = {x.strip() for x in f.read_text(encoding="utf-8").splitlines()}
    except OSError:
        return False
    return "*" in ds or h in ds


def ghi_hong_theo_model(h: str, model: str, nhom: str) -> None:
    """Luu lich su HONG theo model vao cache (song sot khi trang_thai.sqlite bi ghi de)."""
    d = _doc_cache(h)
    if not d or not model or not nhom:
        return
    hm = dict(d.get("hong_theo_model") or {})
    if hm.get(model) != nhom:
        hm[model] = nhom
        _ghi_cache(h, dict(d, hong_theo_model=hm))


#: Truoc 20/10/2026 10:20 (commit 3b62c6e2) model dich la qwen3.7-flash (config/qwen.json) va nhat_ky khong ghi model
MOC_FLASH = ("2026-10-20T10:20:00", "qwen3.7-flash")


def bo_sung_lich_su_cu() -> int:
    """Mot lan: nhat_ky.jsonl truoc MOC_FLASH -> hong_theo_model[qwen3.7-flash] cho ma KHONG_RA_SPEC_PY (cache hom do da
    bi ghi de khi dich lai bang model moi). Tep danh dau .lich_su_cu -> khong lam lai."""
    dau = CACHE / ".lich_su_cu"
    if dau.exists():
        return 0
    n = 0
    try:
        with open(CACHE / "nhat_ky.jsonl", encoding="utf-8") as f:
            for dong in f:
                try:
                    x = json.loads(dong)
                except ValueError:
                    continue
                if str(x.get("luc") or "") >= MOC_FLASH[0]:
                    continue
                for c in x.get("the") or []:
                    if c.get("ket_qua") in ("HONG", "BO_QUA") and c.get("bam") and \
                            nhom_ly_do(c.get("ly_do")) == "KHONG_RA_SPEC_PY":
                        d = _doc_cache(c["bam"])
                        if d and MOC_FLASH[1] not in (d.get("hong_theo_model") or {}):
                            ghi_hong_theo_model(c["bam"], MOC_FLASH[1], "KHONG_RA_SPEC_PY")
                            n += 1
    except OSError:
        pass
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        dau.write_text(str(n), encoding="utf-8")
    except OSError:
        pass
    return n


def _giu_cho(h: str, c: dict | None = None):
    """Tep <hash>.dang (O_EXCL). Tep cu hon han goi (timeout * so lan thu + 120 s) coi nhu treo -> chiem lai."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (h + ".dang")
    han = float((c or {}).get("timeout_giay") or 900) * 2 + 120
    for _ in range(2):
        try:
            fd = os.open(str(f), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode()); os.close(fd)
            return f
        except FileExistsError:
            try:
                if time.time() - f.stat().st_mtime < han:
                    return None
                f.unlink()
            except FileNotFoundError:
                pass
        except OSError:
            return CACHE                                # khong tao duoc tep giu cho -> van dich (hanh vi cu)
    return None


def _tha_cho(f) -> None:
    if f is not None and f != CACHE:
        try:
            f.unlink()
        except OSError:
            pass


def _dich_that(vb, nn, h, client, c, df, nguon_gia) -> dict:
    d = LLM.boc_tach(vb, nn, client=client, c=c)
    tong = {k: int(d.get(k) or 0) for k in ("token_vao", "token_ra", "token_suy_luan")}
    if d.get("trang_thai") == "OK" and df is not None:
        # 20/10/2026: VONG SUA MOT LAN - ban dich 0 lenh / nhin truoc / loi chay -> hoi lai kem chan doan
        try:
            kt = kiem_tra(d, df)
        except Exception as e:  # noqa: BLE001
            kt = {"dat": False, "ly_do": ["python: kiem loi %s" % str(e)[:120]]}
        if can_sua(kt, d):
            cd = list(kt.get("ly_do") or []) + kiem_tinh(d, df)
            d2 = LLM.sua_lai(vb, nn, d, cd, (nguon_gia or "gia mau", len(df), float(df["low"].min()),
                                            float(df["high"].max())), client=client, c=c)
            for k in tong:
                tong[k] += int(d2.get(k) or 0)
            if d2.get("trang_thai") == "OK":
                try:
                    kt2 = kiem_tra(d2, df)
                except Exception:  # noqa: BLE001
                    kt2 = {"dat": False}
                if kt2.get("dat") or not (d2.get("spec") or (d2.get("python") or "").strip()):
                    d = dict(d2, da_sua=1, chan_doan_truoc=cd[:6])
                else:
                    d = dict(d, da_sua=1, chan_doan_truoc=cd[:6])
    if d.get("trang_thai") == "OK":
        # token_*_tong: cong ca lan hoi lai (truoc day cache chi giu token cua lan cuoi -> khong do duoc chi phi sua)
        cu = _doc_cache(h) or {}
        hm = dict(cu.get("hong_theo_model") or {})
        for m in model_khong_ra(cu):
            hm.setdefault(m, "KHONG_RA_SPEC_PY")
        if hm:
            d = dict(d, hong_theo_model=hm)
        _ghi_cache(h, dict(d, ngon_ngu=nn, phien=LLM.PHIEN_PROMPT, luc=time.strftime("%Y-%m-%dT%H:%M:%S"),
                           **{k + "_tong": v for k, v in tong.items()}))
    return d


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
    LLM.HET_QUOTA.clear()
    dem = {"cho": tong_cho, "thieu_ma": len(thieu_ma), "lam": 0, "goi_moi": 0, "tu_cache": 0, "dat": 0, "hong": 0,
           "loi_llm": 0, "bo_qua": 0, "chua_chay_duoc": 0, "cham_tran_token": 0, "ly_do_hong": {}}
    if not co:
        # 20/10/2026: khong co khoa van KIEM LAI duoc the co cache (data/ong_dan/dich_llm/<hash>.json) - khong goi mang
        ds = [x for x in ds if _doc_cache(bam(x["tep"].read_bytes()[:800000])) is not None]
        dem["chua_chay_duoc"] = tong_cho - len(thieu_ma) - len(ds)
        if not ds:
            in_ra("dich_llm: CHUA CHAY DUOC - khong co khoa tren may nay (%d the cho). Chay tren may nha." % tong_cho)
            ghi_bao_cao(dem, LLM.THONG_KE, "", 0.0, ds_cho=danh_sach_cho(cn), tk_hong=thong_ke_hong(cn))
            return dem
        in_ra("dich_llm: khong co khoa - chi kiem lai %d the tu cache" % len(ds))
    try:
        bo_sung_lich_su_cu()
    except Exception:  # noqa: BLE001 - chi la lich su, khong duoc chan buoc dich
        pass
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
        if LLM.HET_QUOTA:                       # 20/10/2026: het quota giua luot -> khong goi tiep, the giu nguyen
            with _KHOA:
                kq_h[h] = ({"trang_thai": "CHUA_CHAY_DUOC", "ghi_chu": "HET_QUOTA - bo qua luot"}, False)
            return
        try:
            d, tu_c = dich_mot(v["vb"], v["nn"], h, client=client, c=c, df=df, nguon_gia=nguon_gia)
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
        if "CHAM_TRAN_TOKEN" in str(d.get("ghi_chu") or ""):
            dem["cham_tran_token"] += 1
        if d.get("trang_thai") == "DANG_DICH":
            dem["dang_dich_noi_khac"] = dem.get("dang_dich_noi_khac", 0) + len(v["the"])
            continue                                     # khong ghi gi: luot sau lay tu cache
        if d.get("trang_thai") == "CHUA_CHAY_DUOC":
            dem["chua_chay_duoc"] += len(v["the"])
            continue
        if d.get("trang_thai") != "OK":
            dem["loi_llm"] += len(v["the"])
            dem["ly_do_hong"]["LOI_LLM"] = dem["ly_do_hong"].get("LOI_LLM", 0) + len(v["the"])
            for x in v["the"]:
                nk.append({"the": x["the"]["id"], "bam": h, "ket_qua": "LOI_LLM", "ghi_chu": d.get("ghi_chu")})
                # 19/10/2026: dem so lan LOI_LLM; the loi mai xep CUOI hang (truoc day dung dau hang moi luot,
                # tra tien goi lai, 200 the loi = vong dich nen dung vi "3 luot khong lam duoc the nao")
                x["the"]["dich_llm_loi_lan"] = int(x["the"].get("dich_llm_loi_lan") or 0) + 1
                if x["the"]["dich_llm_loi_lan"] >= SO_LAN_TOI_DA:     # 20/10/2026: thoi goi lai mai
                    x["the"]["dich_llm"] = {"trang_thai": "BO_QUA", "bam": h, "nhom_ly_do": "LOI_LLM",
                                            "ly_do": ["LOI_LLM %d lan: %s" % (x["the"]["dich_llm_loi_lan"],
                                                                             str(d.get("ghi_chu"))[:200])],
                                            "phien": LLM.PHIEN_PROMPT, "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
                    dem["bo_qua"] += 1
                with cn:
                    OD._luu(cn, x["the"])
            continue                                     # khong ghi HONG: lan sau goi lai
        try:
            kt = kiem_tra(d, df)
        except Exception as e:  # noqa: BLE001 - ket qua cache OK nhung kiem loi -> HONG, khong sap ca luot
            kt = {"dat": False, "kieu": "", "ly_do": ["kiem_tra loi: %s: %s" % (type(e).__name__, str(e)[:160])],
                  "so_lenh": 0}
        nhom = "" if kt["dat"] else nhom_ly_do(kt["ly_do"])
        for x in v["the"]:
            t = x["the"]
            dem["lam"] += 1
            lan = int((t.get("dich_llm") or {}).get("lan") or 0) + (0 if kt["dat"] else 1)
            tt_moi = "DAT" if kt["dat"] else ("BO_QUA" if lan >= SO_LAN_TOI_DA else "HONG")  # HONG ngoai NHOM_THU_LAI: khong vao lai hang (danh_sach_cho)
            t["dich_llm"] = {"trang_thai": tt_moi, "bam": h, "kieu": kt["kieu"], "nhom_ly_do": nhom, "lan": lan,
                             "phien": LLM.PHIEN_PROMPT,
                             "so_lenh_mau": kt["so_lenh"], "ly_do": kt["ly_do"], "model": d.get("model"),
                             "gia_mau": nguon_gia, "luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "nhom": x["nhom"],
                             "co_che": d.get("co_che") or [], "quan_tri": d.get("quan_tri") or {},
                             "chua_dich": d.get("chua_dich") or []}
            if kt["dat"]:
                dem["dat"] += 1
                if kt["kieu"] == "spec":
                    t["duong_dich"] = "spec_dsl"
                    t["tin_hieu"] = {"kieu": "spec", "specs": kt.get("spec") or d["spec"], "khoang": {}}
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
                dem["ly_do_hong"][nhom] = dem["ly_do_hong"].get(nhom, 0) + 1
                if t is v["the"][0]["the"]:
                    ghi_hong_theo_model(h, str(d.get("model") or ""), nhom)
                if tt_moi == "BO_QUA":
                    dem["bo_qua"] += 1
                with cn:
                    OD._luu(cn, t)
                    OD._ghi_nk(cn, "dich_llm", t["id"], "HONG %s" % "; ".join(kt["ly_do"])[:300])
            nk.append({"the": t["id"], "bam": h, "ket_qua": t["dich_llm"]["trang_thai"], "kieu": kt["kieu"],
                       "ly_do": kt["ly_do"][:3], "tu_cache": tu_c})
    tk1 = {k: v - tk0.get(k, 0) for k, v in LLM.THONG_KE.items() if k != "theo_model"}
    dem.update({"so_lan_goi": tk1["so_lan_goi"], "token_vao": tk1["token_vao"], "token_ra": tk1["token_ra"],
                "doi_du_phong": tk1["doi_du_phong"], "so_lan_loi_http": tk1["so_lan_loi"],
                "token_suy_luan": tk1.get("token_suy_luan", 0), "token_vao_cache": tk1.get("token_vao_cache", 0),
                "so_lan_429": tk1.get("so_lan_429", 0)})
    if LLM.HET_QUOTA:
        dem["het_quota"] = str(LLM.HET_QUOTA.get("ghi_chu") or "het quota")[:300]
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(CACHE / "nhat_ky.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "dem": dem, "the": nk}, ensure_ascii=False) + "\n")
    ghi_bao_cao(dem, LLM.THONG_KE, nguon_gia, time.time() - t0, ds_cho=danh_sach_cho(cn), tk_hong=thong_ke_hong(cn))
    in_ra("dich_llm: %s" % json.dumps(dem, ensure_ascii=False))
    return dem


GIAI_THICH_NHOM = {
    "LOI_LLM": "LLM lỗi / không trả JSON (thử lại tối đa %d lần rồi BO_QUA)" % SO_LAN_TOI_DA,
    "PY_CAM_CU_PHAP": "Mã Python bị hộp cát chặn (import, cú pháp cấm, chuỗi cấm)",
    "PY_LOI_CHAY": "Mã Python chạy lỗi trong hộp cát",
    "SPEC_KHONG_CHAY": "Spec không chạy được trên bộ máy DSL (phép/chỉ báo không biết)",
    "KHONG_RA_SPEC_PY": "LLM không ra spec hay python dùng được",
    "NHIN_TRUOC": "Tín hiệu nhìn trước tương lai (bộ kiểm chặn đúng)",
    "IT_LENH": "Ra < %d lệnh trên giá mẫu" % SO_LENH_MIN,
    "SAI_DINH_DANG": "Tín hiệu sai độ dài / ngoài {-1,0,1}",
    "KIEM_LOI": "Bộ kiểm lỗi", "KHAC": "Khác", "KHONG_RO": "Không rõ (thẻ cũ không ghi lí do)"}


def ghi_bao_cao(dem: dict, tk: dict, nguon_gia: str, giay: float, ds_cho: list | None = None, tep: Path | None = None,
                tk_hong: dict | None = None) -> str:
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
                   ("token_suy_luan", "Token suy luận (trong token ra)"), ("so_lan_429", "Lần bị 429"),
                   ("dang_dich_noi_khac", "Thẻ bỏ qua vì tiến trình khác đang dịch cùng mã"),
                   ("bo_qua", "Đánh dấu BO_QUA lần này (hỏng lặp lại / lỗi không do ta)"),
                   ("cham_tran_token", "Câu trả lời chạm trần max_tokens"),
                   ("chua_chay_duoc", "CHƯA CHẠY ĐƯỢC (không có khoá)")):
        if k in dem:
            d.append("| %s | %s |" % (ten, dem[k]))
    if dem.get("ly_do_hong"):
        d += ["", "## Lí do hỏng lần này (theo nhóm)", "", "| Nhóm | Số thẻ | Nghĩa |", "|---|---|---|"]
        for g, n in sorted(dem["ly_do_hong"].items(), key=lambda z: -z[1]):
            d.append("| %s | %d | %s |" % (g, n, GIAI_THICH_NHOM.get(g, "")))
    if tk_hong:
        d += ["", "## Cộng dồn trong CSDL (mọi lần dịch)", "",
              "Trạng thái: " + (", ".join("%s %d" % kv for kv in sorted((tk_hong.get("trang_thai") or {}).items())) or "chưa có"), ""]
        if tk_hong.get("nhom_ly_do"):
            d += ["| Nhóm | Số thẻ HONG/BO_QUA | Ví dụ |", "|---|---|---|"]
            for g, n in sorted(tk_hong["nhom_ly_do"].items(), key=lambda z: -z[1]):
                d.append("| %s | %d | %s |" % (g, n, str((tk_hong.get("vi_du") or {}).get(g, "")).replace("|", "/")))
    d += ["", "Còn chờ sau lần chạy: %d thẻ (LLM: %d, EA bộ dịch không-LLM bỏ qua: %d, top 28: %d)." % (
        len(ds_cho), nh.get("llm", 0), nh.get("ea_bo_qua", 0), sum(1 for x in ds_cho if x["top28"])), "",
        "Theo model (cộng dồn trong tiến trình): " + (", ".join("%s: %d lần, %d/%d token" % (
            m, v["so_lan_goi"], v["token_vao"], v["token_ra"]) for m, v in (tk.get("theo_model") or {}).items()) or "chưa gọi"),
        "", "Vì sao hàng chờ lớn lên: hàng gồm thẻ LLM (Python/Pine) **và mọi EA MQL mà bộ dịch không-LLM bỏ qua** "
        "(`ea_bo_qua`). Mỗi lần `nhan` nhận thẻ Seeker mới, các EA này vào hàng; mỗi lượt chỉ làm tối đa `--gioi_han` thẻ. "
        "Thẻ HONG không vào lại hàng trừ khi phiên prompt mới hơn và lí do thuộc nhóm lỗi phía ta; hỏng %d lần → BO_QUA." % SO_LAN_TOI_DA,
        "", "Kết quả dịch là nhãn LLM, cần MT5 xác nhận; số Python là MÔ PHỎNG, PHÍ TẠM."]
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(d) + "\n", encoding="utf-8")
    return str(tep)
