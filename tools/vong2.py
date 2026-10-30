# -*- coding: utf-8 -*-
"""tools/vong2.py — Vòng 2 (kiểm sâu) generator for MT5 passers.

Pass criteria (labels only for FDR/placebo/Holm): profit after fees, max DD ≤ 80 %,
≥ 10 %/year. Emits MT5 job lines into reports/vong2/hang_cho_vong2.jsonl (same schema
as hang_cho_mt5.jsonl) with vong=2. Home runner picks them up only when
BRAIN_VONG2=1 (see mt5tools/sinh_viec.tu_vong2) — do NOT write the live queue.

Also: portfolio combinations from existing MT5 trade CSVs (nhan.vong2.danh_muc_v2)
and a scoring report reports/VONG2_KIEM_SAU.md.

  python tools/vong2.py                  # generate batch + report
  python tools/vong2.py --chi-bao-cao    # report/portfolio only
  python tools/vong2.py --top 20 --tran 400
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

RA = GOC / "reports" / "vong2"
HANG_CHO_V2 = RA / "hang_cho_vong2.jsonl"
BAO_CAO = RA / "VONG2_KIEM_SAU.md"
SO_CAI_PATHS = [
    Path("/workspace/may_nha_toi_nay/so_cai_from_nha_2132.jsonl"),
    Path("/workspace/may_nha_toi_nay/so_cai_from_nha.jsonl"),
    GOC / "reports" / "mt5_lien_tuc" / "so_cai_from_nha.jsonl",
    GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl",
]
HANG_CHO_NGUON = [
    GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl",
    GOC / "reports" / "phan_viec" / "hang_cho_mt5_hoan_may_nha.jsonl",
    GOC / "reports" / "phan_viec" / "hang_cho_mt5_box.jsonl",
    Path("/workspace/may_nha_toi_nay/hang_cho_mt5_hoan_may_nha.jsonl"),
    Path("/workspace/may_nha_toi_nay/hang_cho_mt5_XL_tu_hoan.jsonl"),
]

# Demo XM 345930355 uses # symbols (shared_bases / sinh_viec.MA).
MA_HASH = [
    "EURUSD#", "GBPUSD#", "AUDUSD#", "USDJPY#", "USDCAD#", "USDCHF#", "NZDUSD#",
    "EURGBP#", "EURCAD#", "EURJPY#", "GBPJPY#", "AUDCAD#", "AUDNZD#", "GBPCAD#",
    "EURAUD#", "NZDCAD#", "GOLD.i#",
]
TF_MT5 = {"M15": 15, "M30": 30, "H1": 16385, "H4": 16388, "D1": 16408}
TF_CSV_GIAY = {"M15": 900, "M30": 1800, "H1": 3600, "H4": 14400, "D1": 86400}

BAI_HOC_JSON = GOC / "data" / "bai_hoc.json"
BAI_HOC_JSON_REPO = GOC / "reports" / "bai_hoc.json"


def nap_priors() -> dict:
    """Weights from learning loop (data/ or reports/bai_hoc.json). Missing → empty."""
    for path in (BAI_HOC_JSON, BAI_HOC_JSON_REPO):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
    return {}


def diem_prior(passer: dict, priors: dict) -> float:
    """Boost passers whose family/tf/ma/entry match winning priors."""
    if not priors:
        return 0.0
    w = priors.get("trong_so") or {}
    s = 0.0
    ten = str(passer.get("ten") or "")
    fam = "khac"
    for k in ("skst", "skea", "mql5", "ghep", "brainxl", "tohop", "v2cn", "v2tf", "v2cap"):
        if k in ten.lower():
            fam = k
            break
    s += float((w.get("gia_dinh") or {}).get(fam, 0))
    s += float((w.get("tf") or {}).get(str(passer.get("tf") or "").upper(), 0))
    ma = str(passer.get("ma") or "").upper().replace("MICRO", "").rstrip("#")
    s += float((w.get("ma") or {}).get(ma, 0))
    return s


UU_TIEN_TEN = (
    "od_skst299b0817", "brainxlrsi", "brainxl", "mql5344ed0d", "mql5e52afb",
    "e52afb999eca4bd1", "od_brainxlmrz",
)


def _parse_dd_pct(dd) -> float | None:
    if dd is None:
        return None
    if isinstance(dd, (int, float)):
        return float(dd)
    m = re.search(r"\(([0-9.]+)\s*%\)", str(dd))
    if m:
        return float(m.group(1))
    m = re.search(r"([0-9.]+)\s*%", str(dd))
    return float(m.group(1)) if m else None


def _years(ky) -> float | None:
    m = re.search(
        r"(\d{4})\.(\d{2})\.(\d{2})\s*-\s*(\d{4})\.(\d{2})\.(\d{2})", str(ky or "")
    )
    if not m:
        return None
    a = datetime(*map(int, m.groups()[:3]))
    b = datetime(*map(int, m.groups()[3:]))
    return max((b - a).days / 365.25, 1 / 12)


def _apy(net, von, years) -> float | None:
    if not years or not von or von <= 0:
        return None
    return (float(net) / float(von)) / years * 100.0


def _doc_jsonl(paths) -> list[dict]:
    rows = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        with p.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def chon_passers(toi_thieu_apy: float = 10.0, dd_max: float = 80.0) -> list[dict]:
    """Pass = profit after fees, DD ≤ dd_max, APY ≥ toi_thieu_apy (when period known)."""
    best: dict[str, dict] = {}
    for r in _doc_jsonl(SO_CAI_PATHS):
        if r.get("loi") and str(r.get("loi")) not in ("None", "", "ok", "OK"):
            continue
        net = r.get("net")
        if not isinstance(net, (int, float)) or net <= 0:
            continue
        dd = _parse_dd_pct(r.get("dd"))
        if dd is None or dd > dd_max:
            continue
        if r.get("hop_le") is False:
            continue
        von = float(r.get("von") or 1000.0)
        y = _years(r.get("ky_bc"))
        apy = _apy(net, von, y)
        if apy is not None and apy < toi_thieu_apy:
            continue
        key = r.get("the_id") or r.get("ten")
        if not key:
            continue
        cur = {
            "ten": r.get("ten"),
            "the_id": r.get("the_id"),
            "ma": r.get("ma") or r.get("symbol_bc"),
            "tf": r.get("tf"),
            "net": float(net),
            "dd_pct": dd,
            "von": von,
            "lenh": r.get("lenh"),
            "chat_luong": r.get("chat_luong"),
            "ky_bc": r.get("ky_bc"),
            "apy": apy,
            "pha": r.get("pha"),
            "ea": r.get("ea"),
            "pf": r.get("pf"),
            "p": r.get("p"),
        }
        if key not in best or cur["net"] > best[key]["net"]:
            best[key] = cur

    priors = nap_priors()

    def diem(p):
        apy = p["apy"] if p["apy"] is not None else (p["net"] / max(p["von"], 1) * 40)
        uu = 0
        blob = str(p.get("ten") or "") + str(p.get("the_id") or "")
        for i, needle in enumerate(UU_TIEN_TEN):
            if needle in blob:
                uu = 1000 - i * 10
                break
        ticks = 0
        cl = str(p.get("chat_luong") or "")
        m = re.search(r"(\d+)\s*%", cl)
        if m:
            ticks = int(m.group(1))
        pr = diem_prior(p, priors)
        return (uu + pr, apy * math.sqrt(max(p["net"], 1)) / max(p["dd_pct"], 5), ticks, p["net"])

    return sorted(best.values(), key=diem, reverse=True)


def _tot_hon_viec(a: dict | None, b: dict | None) -> dict | None:
    if a is None:
        return b
    if b is None:
        return a

    def score(v):
        s = 0
        if v.get("san") == "XM":
            s += 10
        if v.get("pha") in ("KIEM_CSV", "KIEM", "V2_CAO_NGUYEN", "V2_DA_CAP", "V2_KHUNG"):
            s += 5
        ma = str(v.get("ma") or "")
        if ma.endswith("#") or "micro" in ma.lower():
            s += 2
        if v.get("ts"):
            s += 3
        return s

    return a if score(a) >= score(b) else b


def _hex_tokens(s: str) -> list[str]:
    return re.findall(r"[0-9a-f]{6,}", (s or "").lower())


def nap_viec_goc() -> dict[str, dict]:
    """Index base jobs by the_id, ten, and hex tokens (prefer XM, KIEM_CSV)."""
    idx: dict[str, dict] = {}
    for r in _doc_jsonl(HANG_CHO_NGUON):
        if not r.get("ts") or not r.get("ten"):
            continue
        keys = [r.get("the_id"), r.get("ten")]
        # Strip common suffixes so od_xxx_XM_CSV_IS → od_xxx_XM_CSV
        ten = r.get("ten") or ""
        for suf in ("_IS", "_RT", "_OOS"):
            if ten.endswith(suf):
                keys.append(ten[: -len(suf)])
        # v2cn / v2g variants: od_v2cn_mql5HASH... → also index by mql5HASH core
        m = re.search(r"(mql5|skst|skea|ghep|brainxl)[0-9a-f]{6,}", ten, re.I)
        if m:
            keys.append(m.group(0).lower())
        for h in _hex_tokens(ten) + _hex_tokens(r.get("the_id") or ""):
            keys.append(h)
        for k in filter(None, keys):
            idx[k] = _tot_hon_viec(idx.get(k), r)
    return idx


def tim_viec_goc(passer: dict, bases: dict[str, dict]) -> dict | None:
    """Resolve base job for a passer via direct key then fuzzy hex."""
    for k in (passer.get("the_id"), passer.get("ten")):
        if k and k in bases:
            return bases[k]
    ten = passer.get("ten") or ""
    for suf in ("_IS", "_RT", "_OOS"):
        if ten.endswith(suf) and ten[: -len(suf)] in bases:
            return bases[ten[: -len(suf)]]
    # od_v2cn_XXXXn125 → look for base without n-suffix / v2cn
    m = re.search(r"(?:od_v2cn_|od_v2g\w+_)?(mql5|skst|skea|ghep)([0-9a-f]{6,})", ten, re.I)
    if m:
        core = (m.group(1) + m.group(2)).lower()
        if core in bases:
            return bases[core]
        cand = "od_%s_XM_CSV" % core
        if cand in bases:
            return bases[cand]
    for h in _hex_tokens(ten) + _hex_tokens(passer.get("the_id") or ""):
        if h in bases:
            return bases[h]
    return None


def _ma_hash(ma: str) -> str:
    """Map micro / bare / # → demo hash symbol."""
    s = (ma or "").strip()
    u = s.upper()
    if u in ("XAUUSD", "XAUUSDMICRO", "GOLDMICRO", "GOLD", "XAUUSD#", "GOLD#", "GOLD.I#"):
        return "GOLD.i#"
    if u.endswith("MICRO"):
        return u[:-5] + "#"
    if u.endswith("#"):
        return s if s.endswith("#") else u
    if u.isalpha() and len(u) in (6, 7):
        return u + "#"
    return s


def _ten_v2(goc_ten: str, loai: str, salt: str) -> str:
    """Unique od_v2r2… name ≤ 60 chars (MT5 Common\\Files limit)."""
    base = goc_ten
    if base.startswith("od_"):
        base = base[3:]
    # strip trailing _XM_CSV / _Exness_CSV
    base = re.sub(r"_(XM|Exness)_CSV$", "", base)
    raw = "od_v2r2%s_%s_%s" % (loai, salt, base)
    if len(raw) > 54:
        raw = "od_v2r2%s_%s_%s" % (loai, salt, hashlib.sha1(base.encode()).hexdigest()[:10])
    return raw + "_XM_CSV"


def _clone(viec: dict, *, ten: str, pha: str, diem: float, them: dict | None = None) -> dict:
    v = copy.deepcopy(viec)
    cu = viec.get("ten") or ""
    v["ten"] = ten
    v["pha"] = pha
    v["nguon"] = "vong2"
    v["vong"] = 2
    v["diem"] = float(diem)
    v["san"] = "XM"
    v["tien"] = "USD"
    # Prefer demo hash symbol + deposit matching verified winners when possible
    if v.get("ma"):
        v["ma"] = _ma_hash(str(v["ma"]))
    v.pop("hoan_may_nha", None)
    v.pop("hoan_luc", None)
    v.pop("hoan_ly_do", None)
    # Keep csv_vao path; rewrite InpFileCsv if present to stay consistent with ten
    ts = dict(v.get("ts") or {})
    if "InpFileCsv" in ts and cu:
        ts["InpFileCsv"] = str(ts["InpFileCsv"]).replace(cu, ten)
    v["ts"] = ts
    if them:
        v.update(them)
    return v


def _set_tf(v: dict, tf: str) -> dict:
    v = copy.deepcopy(v)
    v["tf"] = tf
    ts = dict(v.get("ts") or {})
    ts["InpTF"] = TF_MT5[tf]
    if int(ts.get("InpVao") or 0) == 4:  # CSV signal
        ts["InpCsvTreGiay"] = TF_CSV_GIAY[tf]
    v["ts"] = ts
    return v


def _set_ql(v: dict, **kw) -> dict:
    """Patch python_ql + matching Inp* fields (pct and price modes)."""
    v = copy.deepcopy(v)
    ql = dict(v.get("python_ql") or {})
    ts = dict(v.get("ts") or {})
    map_inp = {
        "tp_pct": ("InpTPPct",),
        "dca_buoc_pct": ("InpBuocPct",),
        "dca_he_so_lot": ("InpHeSoLot",),
        "dca_toi_da": ("InpMaxTang",),
        "hedge_khi_lo_pct": ("InpHedgeKhiLoPct",),
        "lot_tren_1000": ("InpLot0",),
        "tp_gia": ("InpTPGia",),
        "buoc_gia": ("InpBuocGia",),
    }
    for k, val in kw.items():
        if val is None:
            continue
        ql[k] = val
        for inp in map_inp.get(k, ()):
            ts[inp] = val
    v["python_ql"] = ql
    v["ts"] = ts
    return v


def bien_the_tham_so(viec: dict, goc_ten: str) -> list[dict]:
    """±20/50 % neighborhood on key risk/TP/step/lot inputs."""
    ql = viec.get("python_ql") or {}
    ts = viec.get("ts") or {}
    tp = float(ql.get("tp_pct") or ts.get("InpTPPct") or 0) or None
    buoc = float(ql.get("dca_buoc_pct") or ts.get("InpBuocPct") or 0) or None
    tp_gia = float(ts.get("InpTPGia") or 0) or None
    buoc_gia = float(ts.get("InpBuocGia") or 0) or None
    he = float(ql.get("dca_he_so_lot") or ts.get("InpHeSoLot") or 0) or None
    mx = int(ql.get("dca_toi_da") or ts.get("InpMaxTang") or 0) or None
    lot = float(ql.get("lot_tren_1000") or ts.get("InpLot0") or 0) or None
    ra = []
    grid = []
    if tp:
        for f, tag in ((0.5, "tp50"), (0.8, "tp80"), (1.2, "tp120"), (1.5, "tp150")):
            grid.append((tag, {"tp_pct": round(tp * f, 6)}))
    elif tp_gia:
        for f, tag in ((0.5, "tpg50"), (0.8, "tpg80"), (1.2, "tpg120"), (1.5, "tpg150")):
            grid.append((tag, {"tp_gia": round(tp_gia * f, 8)}))
    if buoc:
        for f, tag in ((0.5, "b50"), (0.8, "b80"), (1.2, "b120"), (1.5, "b150")):
            grid.append((tag, {"dca_buoc_pct": round(buoc * f, 6)}))
    elif buoc_gia:
        for f, tag in ((0.5, "bg50"), (0.8, "bg80"), (1.2, "bg120"), (1.5, "bg150")):
            grid.append((tag, {"buoc_gia": round(buoc_gia * f, 8)}))
    if he:
        for f, tag in ((0.8, "hs80"), (1.2, "hs120")):
            grid.append((tag, {"dca_he_so_lot": round(he * f, 4)}))
    if mx:
        for d, tag in ((-2, "mxm2"), (-1, "mxm1"), (1, "mxp1"), (2, "mxp2")):
            nv = max(1, mx + d)
            if nv != mx:
                grid.append((tag, {"dca_toi_da": nv}))
    if lot and lot > 0:
        for f, tag in ((0.5, "lot50"), (0.8, "lot80"), (1.2, "lot120")):
            grid.append((tag, {"lot_tren_1000": round(lot * f, 4)}))
    # Session window shift (±2h on cam)
    g_tu = int(ts.get("InpGioCamTu") or 23)
    g_den = int(ts.get("InpGioCamDen") or 2)
    for d, tag in ((-2, "camm2"), (2, "camp2")):
        grid.append((tag, None))  # handled below

    seen = set()
    for tag, patch in grid:
        if patch is None:
            continue
        ten = _ten_v2(goc_ten, "p", tag)
        if ten in seen:
            continue
        seen.add(ten)
        vv = _set_ql(_clone(viec, ten=ten, pha="V2_ROBUST", diem=72,
                            them={"vong2_goc": goc_ten, "vong2_loai": "tham_so", "vong2_tag": tag}), **patch)
        ra.append(vv)
    for d, tag in ((-2, "camm2"), (2, "camp2")):
        ten = _ten_v2(goc_ten, "p", tag)
        vv = _clone(viec, ten=ten, pha="V2_ROBUST", diem=70,
                    them={"vong2_goc": goc_ten, "vong2_loai": "tham_so", "vong2_tag": tag})
        ts2 = dict(vv["ts"])
        ts2["InpGioCamTu"] = (g_tu + d) % 24
        ts2["InpGioCamDen"] = (g_den + d) % 24
        vv["ts"] = ts2
        ra.append(vv)
    return ra


def bien_the_khung(viec: dict, goc_ten: str) -> list[dict]:
    tf0 = (viec.get("tf") or "H1").upper()
    targets = [t for t in ("M30", "H1", "H4", "D1") if t != tf0]
    # Prefer nearby frames
    if tf0 == "H1":
        targets = ["M30", "H4"]
    elif tf0 == "H4":
        targets = ["H1", "D1"]
    elif tf0 == "D1":
        targets = ["H4"]
    ra = []
    for tf in targets:
        ten = _ten_v2(goc_ten, "tf", tf.lower())
        vv = _set_tf(_clone(viec, ten=ten, pha="V2_KHUNG", diem=68,
                            them={"vong2_goc": goc_ten, "vong2_loai": "khung", "vong2_tag": tf}), tf)
        ra.append(vv)
    return ra


def bien_the_cap(viec: dict, goc_ten: str, toi_da: int = 6) -> list[dict]:
    """Other # majors. Skip pure-CSV (InpVao=4) — signal is symbol-specific."""
    ts = viec.get("ts") or {}
    if int(ts.get("InpVao") or 0) == 4:
        return []
    ma0 = _ma_hash(str(viec.get("ma") or ""))
    others = [m for m in MA_HASH if m != ma0][:toi_da]
    ra = []
    for ma in others:
        tag = re.sub(r"[^A-Za-z0-9]", "", ma)[:8].lower()
        ten = _ten_v2(goc_ten, "cap", tag)
        vv = _clone(viec, ten=ten, pha="V2_DA_CAP", diem=66,
                    them={"vong2_goc": goc_ten, "vong2_loai": "cap", "vong2_tag": ma})
        vv["ma"] = ma
        vv["ma_box"] = ma.rstrip("#").replace(".i", "")
        ra.append(vv)
    return ra


def _parse_ymd(s: str) -> datetime | None:
    m = re.match(r"(\d{4})[.-](\d{2})[.-](\d{2})", str(s or "").strip())
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _csv_pham_vi(viec: dict) -> tuple[str, str] | None:
    """First/last signal date (YYYY.MM.DD) from csv_vao / InpFileCsv.

    CSV-driven EAs (InpVao=4) produce 0 trades when the OOS window has no overlap
    with this file. Home tick history is also thin before ~2024, so CSV coverage is
    the primary gate for V2_OOS windows.
    """
    candidates: list[Path] = []
    cv = viec.get("csv_vao") or ""
    if cv:
        candidates.append(Path(cv))
        if not Path(cv).is_absolute():
            candidates.append(GOC / cv)
    ts = viec.get("ts") or {}
    inp = str(ts.get("InpFileCsv") or "")
    if inp:
        candidates.append(Path(inp))
        if not Path(inp).is_absolute():
            candidates.append(GOC / inp)
            # common home layout: MQL5/Files/<name>
            candidates.append(GOC / "reports" / "phan_viec" / "viec_mt5" / inp)
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if not path.exists() or not path.is_file():
            continue
        first = last = None
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line[0] in "#;":
                        continue
                    # skip header
                    low = line[:24].lower()
                    if "time" in low or "ngay" in low or "date" in low:
                        if not line[0].isdigit():
                            continue
                    token = line.replace(";", ",").replace("\t", ",").split(",")[0].strip().strip('"')
                    d = _parse_ymd(token)
                    if d is None:
                        continue
                    stamp = d.strftime("%Y.%m.%d")
                    if first is None:
                        first = stamp
                    last = stamp
        except OSError:
            continue
        if first and last:
            return first, last
    return None


def _overlap_ok(tu: str, den: str, csv_tu: str, csv_den: str, min_days: int = 30) -> bool:
    a = _parse_ymd(tu)
    b = _parse_ymd(den)
    c0 = _parse_ymd(csv_tu)
    c1 = _parse_ymd(csv_den)
    if not all((a, b, c0, c1)):
        return False
    lo = max(a, c0)
    hi = min(b, c1)
    return (hi - lo).days >= min_days


def bien_the_oos(viec: dict, goc_ten: str) -> list[dict]:
    """Longer history + earlier OOS window (walk-forward style).

    Only emit windows that overlap CSV signal coverage (and therefore the
    tick/history range we actually have on home). Pre-2024 "truoc" windows
    against CSVs that start in 2024 produced 0% real ticks + 0 trades (~50s waste).
    """
    ra = []
    csv_pham = _csv_pham_vi(viec)
    den_mac = "2026.10.01"
    # Longer: from 2016 (or 2019) to 2026.10.01 — clamp tu up to CSV start when known
    for tu, tag, diem in (("2016.01.01", "dai16", 74), ("2019.01.01", "dai19", 73)):
        tu_eff, den_eff = tu, den_mac
        if csv_pham:
            csv_tu, csv_den = csv_pham
            # clamp window into CSV coverage (keep tag name for ledger continuity)
            if _parse_ymd(tu_eff) and _parse_ymd(csv_tu) and _parse_ymd(tu_eff) < _parse_ymd(csv_tu):
                tu_eff = csv_tu
            if not _overlap_ok(tu_eff, den_eff, csv_tu, csv_den):
                continue
        ten = _ten_v2(goc_ten, "oos", tag)
        vv = _clone(viec, ten=ten, pha="V2_OOS", diem=diem,
                    them={"vong2_goc": goc_ten, "vong2_loai": "oos", "vong2_tag": tag})
        vv["tu"] = tu_eff
        vv["den"] = den_eff
        if csv_pham:
            vv["csv_tu"] = csv_pham[0]
            vv["csv_den"] = csv_pham[1]
        ra.append(vv)
    # Earlier window ending before the original IS start (if known)
    tu0 = str(viec.get("tu") or "")
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})", tu0)
    if m:
        y = int(m.group(1))
        if y >= 2022:
            tu_t = "%d.01.01" % (y - 3)
            den_t = "%04d.%02d.01" % (y, int(m.group(2)))
            # Skip when CSV (typical home signals ~2024+) has no overlap with this window
            if csv_pham and not _overlap_ok(tu_t, den_t, csv_pham[0], csv_pham[1]):
                pass  # park: no emit
            else:
                # If no CSV info, still emit only when den reaches 2024+ (tick coverage floor)
                skip = False
                if csv_pham is None:
                    den_dt = _parse_ymd(den_t)
                    if den_dt is None or den_dt < datetime(2024, 1, 1):
                        skip = True  # already built dai*; skip truoc
                if not skip:
                    ten = _ten_v2(goc_ten, "oos", "truoc")
                    vv = _clone(viec, ten=ten, pha="V2_OOS", diem=75,
                                them={"vong2_goc": goc_ten, "vong2_loai": "oos", "vong2_tag": "truoc"})
                    vv["tu"] = tu_t
                    vv["den"] = den_t
                    if csv_pham:
                        vv["csv_tu"] = csv_pham[0]
                        vv["csv_den"] = csv_pham[1]
                    ra.append(vv)
    return ra


def bien_the_xac_nhan_tick(viec: dict, goc_ten: str) -> list[dict]:
    """Re-confirm on all-real-ticks (high priority) — same params, tagged."""
    ten = _ten_v2(goc_ten, "xt", "realtick")
    vv = _clone(viec, ten=ten, pha="V2_XAC_NHAN", diem=90,
                them={"vong2_goc": goc_ten, "vong2_loai": "xac_nhan_tick", "vong2_tag": "real",
                      "tang": 2, "model": 4})
    # Ensure hash symbol for demo
    vv["ma"] = _ma_hash(str(vv.get("ma") or ""))
    return [vv]


def sinh_cho_passer(passer: dict, goc: dict, gon: bool = False) -> list[dict]:
    goc_ten = passer.get("ten") or goc.get("ten")
    viec = copy.deepcopy(goc)
    # Demo hash account: prefer # symbols; deposit 10k when verified on 10k
    von_p = float(passer.get("von") or 0)
    if von_p >= 10000:
        viec["von"] = 10000.0
    elif passer.get("von") and von_p >= 1000:
        viec["von"] = von_p if von_p <= 100000 else 10000.0
    ma_nguon = passer.get("ma") or viec.get("ma")
    if ma_nguon:
        viec["ma"] = _ma_hash(str(ma_nguon))
        viec["ma_box"] = str(viec["ma"]).rstrip("#").replace(".i", "").replace(".I", "")
    ds = []
    ds += bien_the_xac_nhan_tick(viec, goc_ten)
    tham = bien_the_tham_so(viec, goc_ten)
    if gon:
        # Lean: keep ±20% + one extreme each + session; drop ±50% duplicates
        keep = {"tp80", "tp120", "tpg80", "tpg120", "b80", "b120", "bg80", "bg120",
                "hs80", "hs120", "mxm1", "mxp1", "lot80", "lot120", "camm2", "camp2",
                "tp50", "b50"}  # keep one extreme
        tham = [v for v in tham if v.get("vong2_tag") in keep][:10]
    ds += tham
    ds += bien_the_khung(viec, goc_ten)
    if not gon:
        ds += bien_the_cap(viec, goc_ten)
    else:
        # Lean cross-symbol: top-2 other majors for indicator EAs only
        ds += bien_the_cap(viec, goc_ten, toi_da=2)
    oos = bien_the_oos(viec, goc_ten)
    if gon:
        # Prefer coverage-clamped dai19; truoc only if generator kept it (CSV overlap)
        oos = [v for v in oos if v.get("vong2_tag") in ("dai19", "truoc", "dai16")][:2]
    ds += oos
    for v in ds:
        v["vong"] = 2
        v.setdefault("vong2_goc", goc_ten)
    return ds


def ghi_hang_cho(ds: list[dict], tep: Path = HANG_CHO_V2, thay_the: bool = False) -> int:
    tep.parent.mkdir(parents=True, exist_ok=True)
    cu: dict[str, dict] = {}
    if tep.exists() and not thay_the:
        for x in tep.read_text(encoding="utf-8").splitlines():
            try:
                v = json.loads(x)
                cu[v["ten"]] = v
            except (ValueError, KeyError):
                pass
    for v in ds:
        cu[v["ten"]] = v
    tep.write_text(
        "".join(json.dumps(cu[k], ensure_ascii=False, sort_keys=True, default=str) + "\n"
                for k in sorted(cu)),
        encoding="utf-8",
    )
    return len(cu)


def dem_theo_loai(ds: list[dict]) -> dict[str, int]:
    from collections import Counter
    return dict(Counter(v.get("vong2_loai") or v.get("pha") or "?" for v in ds))


def portfolio_tu_mt5(passers: list[dict], toi_da_he: int = 12) -> list[dict]:
    """Reuse nhan.vong2 equity rebuild + danh_muc_v2 when trade CSVs exist."""
    try:
        from nhan import vong2 as V
    except Exception as e:
        return [{"loi": "import nhan.vong2: %s" % e}]
    pt = {}
    for p in passers[:toi_da_he]:
        ten = p.get("ten")
        if not ten:
            continue
        # ket_qua files use ten_vao.csv_lenh_mt5.csv naming
        try:
            m = V.phan_tich_mt5(ten, net_bao_cao=p.get("net"))
        except Exception as e:
            m = {"loi": str(e)[:200]}
        m.update({"the_id": p.get("the_id"), "symbol": p.get("ma"), "tf": p.get("tf"),
                  "dd_bao_cao_pct": p.get("dd_pct"), "lai_rong_bao_cao": p.get("net")})
        pt[ten] = m
    try:
        return V.danh_muc_v2(pt, toi_da=4)
    except Exception as e:
        return [{"loi": "danh_muc_v2: %s" % e}]


def ghi_bao_cao(passers, viec_moi, dem, danh_muc, tep: Path = BAO_CAO) -> str:
    L = [
        "# Vòng 2 — kiểm sâu ứng viên PASS",
        "",
        "Lúc: %s (Asia/Bangkok, UTC+7)." % time.strftime("%Y-%m-%d %H:%M"),
        "",
        "**Pass (nhãn):** lãi sau phí > 0, DD ≤ 80 %, ≥ 10 %/năm. FDR/placebo/Holm = nhãn, không cổng.",
        "",
        "## 1. Ứng viên PASS từ sổ cái",
        "",
        "| # | ten | ma | tf | net | DD% | APY% | ticks | lệnh |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, p in enumerate(passers[:40], 1):
        L.append("| %d | `%s` | %s | %s | %.2f | %s | %s | %s | %s |" % (
            i, p.get("ten"), p.get("ma"), p.get("tf"), p["net"],
            p.get("dd_pct"), ("%.1f" % p["apy"]) if p.get("apy") is not None else "—",
            p.get("chat_luong") or "—", p.get("lenh") or "—"))
    L += ["", "## 2. Việc MT5 vòng 2 đã sinh", "",
          "Tổng việc mới lần này: **%d**. Phân loại:" % len(viec_moi), ""]
    for k, n in sorted(dem.items(), key=lambda z: -z[1]):
        L.append("- `%s`: %d" % (k, n))
    L += ["", "Tệp hàng chờ: `reports/vong2/hang_cho_vong2.jsonl`.",
          "Máy nhà **không** đọc trực tiếp vào `hang_cho_mt5.jsonl`.",
          "Bật trên cửa sổ `chay_lien_tuc.py`:",
          "```", "set BRAIN_VONG2=1", "set BRAIN_VONG2_UU_TIEN=1", "```",
          "Hoặc merge thủ công các dòng từ `reports/vong2/hang_cho_vong2.jsonl` "
          "(cùng schema) vào queue do owner quản lý.",
          "",
          "## 3. Danh mục kết hợp (từ lệnh MT5 thật đã có)",
          ""]
    if not danh_muc:
        L.append("_Chưa đo được — thiếu CSV lệnh MT5 trên box cho đủ hệ PASS mới._")
    else:
        L += ["| # | Hệ | Lãi kép %/năm | DD equity % | Corr ngày max | Kỳ |",
              "|---|---|---|---|---|---|"]
        for i, d in enumerate(danh_muc[:8], 1):
            if d.get("loi"):
                L.append("| %d | %s |||||" % (i, d["loi"]))
                continue
            L.append("| %d | %s | %s | %s | %s | %s → %s |" % (
                i, "<br>".join(d.get("he") or []), d.get("lai_kep_pct_nam"),
                d.get("dd_equity_pct"), d.get("tuong_quan_ngay_max"),
                d.get("tu"), d.get("den")))
    L += ["", "## 4. Cách chấm sau khi MT5 trả kết quả",
          "",
          "- **Robustness:** fraction of `V2_ROBUST` neighbors still PASS.",
          "- **Generalization:** `V2_DA_CAP` / `V2_KHUNG` still PASS.",
          "- **OOS:** `V2_OOS` APY ≥ 10 %, DD ≤ 80 %.",
          "- **Combination:** re-run `danh_muc_v2` on new equity curves.",
          ""]
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(L), encoding="utf-8")
    return str(tep)


def chay(top: int = 20, tran: int = 400, chi_bao_cao: bool = False, gon: bool = False) -> dict:
    passers = chon_passers()
    bases = nap_viec_goc()
    danh_muc = portfolio_tu_mt5(passers)
    viec_moi: list[dict] = []
    thieu = []
    if not chi_bao_cao:
        for p in passers[:top]:
            g = tim_viec_goc(p, bases)
            if not g:
                thieu.append(p.get("ten"))
                continue
            viec_moi += sinh_cho_passer(p, g, gon=gon)
            if len(viec_moi) >= tran:
                break
        viec_moi = viec_moi[:tran]
        # Fresh od_v2r2_* batch (do not keep legacy od_v2* naming)
        tong = ghi_hang_cho(viec_moi, thay_the=True)
    else:
        tong = len(HANG_CHO_V2.read_text().splitlines()) if HANG_CHO_V2.exists() else 0
    dem = dem_theo_loai(viec_moi)
    path = ghi_bao_cao(passers, viec_moi, dem, danh_muc)
    meta = {
        "luc": time.strftime("%Y-%m-%d %H:%M"),
        "so_passer": len(passers),
        "so_viec_moi": len(viec_moi),
        "so_viec_hang_cho": tong,
        "theo_loai": dem,
        "thieu_viec_goc": thieu[:20],
        "bao_cao": path,
        "hang_cho": str(HANG_CHO_V2),
        "danh_muc": danh_muc,
    }
    (RA / "vong2_kiem_sau_meta.json").write_text(
        json.dumps({k: v for k, v in meta.items() if k != "danh_muc"}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Vòng 2 kiểm sâu — sinh việc MT5 + báo cáo")
    ap.add_argument("--top", type=int, default=20, help="Số PASS ưu tiên để sinh việc")
    ap.add_argument("--tran", type=int, default=400, help="Trần số việc mới lần này")
    ap.add_argument("--chi-bao-cao", action="store_true")
    ap.add_argument("--gon", action="store_true",
                    help="Lean grid: ~15 jobs/system so --top 50 stays under ~900 jobs")
    a = ap.parse_args(argv)
    kq = chay(a.top, a.tran, a.chi_bao_cao, gon=a.gon)
    print(json.dumps({k: kq[k] for k in ("luc", "so_passer", "so_viec_moi", "so_viec_hang_cho", "theo_loai", "hang_cho", "bao_cao", "thieu_viec_goc")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
