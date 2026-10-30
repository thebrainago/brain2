# -*- coding: utf-8 -*-
"""tools/hoc_tu_so_cai.py — LEARNING LOOP: mine so_cai (+ nao.db bai_hoc) → priors.

After each backtest session:
  1. Read ledgers (so_cai*.jsonl)
  2. Aggregate win/lose by family, TF, symbol, entry type (InpVao), key params
  3. Write data/bai_hoc.json (machine priors) + reports/BAI_HOC.md (human)
  4. Upsert short cards into nhan.bai_hoc so uu_tien / NGHI can query

Pass criteria: net>0 after fees, DD≤80%, APY≥10%/yr when period known.
FDR/placebo/Holm remain labels only.

  python tools/hoc_tu_so_cai.py
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

SO_CAI = [
    Path("/workspace/may_nha_toi_nay/so_cai_from_nha_2132.jsonl"),
    Path("/workspace/may_nha_toi_nay/so_cai_from_nha.jsonl"),
    GOC / "reports" / "mt5_lien_tuc" / "so_cai_from_nha.jsonl",
    GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl",
]
OUT_JSON = GOC / "data" / "bai_hoc.json"
OUT_MD = GOC / "reports" / "BAI_HOC.md"

VAO_TEN = {0: "khong", 1: "MRZ", 2: "RSI", 3: "khac_chi_bao", 4: "CSV_lenh"}


def _parse_dd(dd):
    if dd is None:
        return None
    if isinstance(dd, (int, float)):
        return float(dd)
    m = re.search(r"\(([0-9.]+)\s*%\)", str(dd))
    return float(m.group(1)) if m else None


def _years(ky):
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})\s*-\s*(\d{4})\.(\d{2})\.(\d{2})", str(ky or ""))
    if not m:
        return None
    a = datetime(*map(int, m.groups()[:3]))
    b = datetime(*map(int, m.groups()[3:]))
    return max((b - a).days / 365.25, 1 / 12)


def _fam(ten: str) -> str:
    t = (ten or "").lower()
    for k in ("skst", "skea", "mql5", "ghep", "brainxlmrz", "brainxlrsi", "brainxl",
              "tohop", "v2cn", "v2tf", "v2cap", "v2r2"):
        if k in t:
            return k
    return "khac"


def _ma_chuan(ma: str) -> str:
    s = (ma or "").upper().replace("MICRO", "").rstrip("#").replace(".I", "")
    if s in ("XAUUSD", "GOLD", "GOLD.I"):
        return "XAUUSD"
    return s


def _doc_rows():
    seen = set()
    rows = []
    for p in SO_CAI:
        if not p.exists():
            continue
        for line in p.open(encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (r.get("ten"), r.get("luc"), r.get("slot"), r.get("net"))
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
    return rows


def _nhan_pass(r) -> str:
    """pass | fail | loi | stub"""
    loi = r.get("loi")
    if loi and str(loi) not in ("None", "", "ok", "OK"):
        return "loi"
    net = r.get("net")
    if not isinstance(net, (int, float)):
        return "loi"
    dd = _parse_dd(r.get("dd"))
    von = float(r.get("von") or 1000)
    y = _years(r.get("ky_bc"))
    apy = (net / von) / y * 100 if y and von else None
    if net > 0 and (dd is None or dd <= 80) and (apy is None or apy >= 10):
        return "pass"
    if net <= 0 or (dd is not None and dd > 80) or (apy is not None and apy < 10):
        return "fail"
    return "fail"


def _bucket(rows):
    """Aggregate counts + mean net/dd/apy by dimension."""
    dims = {
        "gia_dinh": lambda r: _fam(r.get("ten") or ""),
        "tf": lambda r: str(r.get("tf") or "?").upper(),
        "ma": lambda r: _ma_chuan(str(r.get("ma") or r.get("symbol_bc") or "")),
        "vao": lambda r: VAO_TEN.get(int((r.get("ts") or {}).get("InpVao") or -1), "unknown"),
        "pha": lambda r: str(r.get("pha") or "?"),
        "san": lambda r: str(r.get("san") or "?"),
    }
    # param buckets
    def tp_bucket(r):
        ts = r.get("ts") or {}
        tp = float(ts.get("InpTPPct") or 0)
        if tp <= 0:
            tpg = float(ts.get("InpTPGia") or 0)
            if tpg <= 0:
                return "tp_none"
            return "tpg_<%.4f" % (0.002 if tpg < 0.002 else (0.005 if tpg < 0.005 else 0.01))
        if tp < 0.003:
            return "tp_pct_<0.3%"
        if tp < 0.006:
            return "tp_pct_0.3-0.6%"
        return "tp_pct_>=0.6%"

    def buoc_bucket(r):
        ts = r.get("ts") or {}
        b = float(ts.get("InpBuocPct") or 0)
        if b <= 0:
            return "buoc_gia_or_none"
        if b < 0.005:
            return "buoc_<0.5%"
        if b < 0.01:
            return "buoc_0.5-1%"
        return "buoc_>=1%"

    dims["tp"] = tp_bucket
    dims["buoc"] = buoc_bucket

    out = {}
    for name, fn in dims.items():
        agg = defaultdict(lambda: {"pass": 0, "fail": 0, "loi": 0, "net_pass": [], "dd_pass": [], "apy_pass": []})
        for r in rows:
            k = fn(r) or "?"
            if k in ("", "?"):
                continue
            nh = _nhan_pass(r)
            agg[k][nh if nh in ("pass", "fail", "loi") else "fail"] += 1
            if nh == "pass":
                agg[k]["net_pass"].append(float(r["net"]))
                dd = _parse_dd(r.get("dd"))
                if dd is not None:
                    agg[k]["dd_pass"].append(dd)
                y = _years(r.get("ky_bc"))
                von = float(r.get("von") or 1000)
                if y and von:
                    agg[k]["apy_pass"].append(float(r["net"]) / von / y * 100)
        out[name] = {}
        for k, v in agg.items():
            n = v["pass"] + v["fail"] + v["loi"]
            rate = v["pass"] / max(v["pass"] + v["fail"], 1)
            out[name][k] = {
                "n": n,
                "pass": v["pass"],
                "fail": v["fail"],
                "loi": v["loi"],
                "ti_le_pass": round(rate, 3),
                "net_tb": round(sum(v["net_pass"]) / len(v["net_pass"]), 2) if v["net_pass"] else None,
                "dd_tb": round(sum(v["dd_pass"]) / len(v["dd_pass"]), 2) if v["dd_pass"] else None,
                "apy_tb": round(sum(v["apy_pass"]) / len(v["apy_pass"]), 2) if v["apy_pass"] else None,
            }
    return out


def _trong_so(agg: dict) -> dict:
    """Convert pass-rate into prior boosts (−5..+15). Need n≥5 to score."""
    w = {}
    for dim, table in agg.items():
        w[dim] = {}
        for k, v in table.items():
            if v["pass"] + v["fail"] < 5:
                continue
            # baseline ~0.15–0.25 pass rate; score relative
            rate = v["ti_le_pass"]
            if rate >= 0.35:
                score = 12 + min(3, (rate - 0.35) * 20)
            elif rate >= 0.22:
                score = 5
            elif rate >= 0.12:
                score = 0
            elif rate >= 0.05:
                score = -3
            else:
                score = -5
            # APY bonus
            if v.get("apy_tb") and v["apy_tb"] >= 40 and score > 0:
                score += 2
            w[dim][k] = round(score, 1)
    return w


def _bai_hoc_cards(agg, trong_so, rows) -> list[dict]:
    cards = []
    ngay = time.strftime("%Y-%m-%d")
    # Top families
    fam = agg.get("gia_dinh") or {}
    top = sorted(fam.items(), key=lambda kv: (-kv[1]["pass"], -kv[1]["ti_le_pass"]))[:5]
    bot = sorted(
        [(k, v) for k, v in fam.items() if v["pass"] + v["fail"] >= 5],
        key=lambda kv: (kv[1]["ti_le_pass"], -kv[1]["fail"]),
    )[:3]
    if top:
        bc = "; ".join("%s pass=%d rate=%.0f%%" % (k, v["pass"], 100 * v["ti_le_pass"]) for k, v in top)
        cards.append({
            "ma": "mt5_fam_top_%s" % ngay.replace("-", ""),
            "loai": "huong_dang_mo",
            "tieu_de": "Gia dinh MT5 dang an (so_cai)",
            "noi_dung": "Cac family co nhieu PASS nhat sau phi, DD<=80, APY>=10: "
                        + ", ".join(k for k, _ in top)
                        + ". Vong 2/SEEKER uu tien nhan doi luoi quanh cac family nay.",
            "bang_chung": bc,
            "ngay": ngay,
            "nguon": "hoc_tu_so_cai",
        })
    if bot and bot[0][1]["ti_le_pass"] < 0.08:
        bc = "; ".join("%s pass=%d fail=%d rate=%.0f%%" % (
            k, v["pass"], v["fail"], 100 * v["ti_le_pass"]) for k, v in bot)
        cards.append({
            "ma": "mt5_fam_tranh_%s" % ngay.replace("-", ""),
            "loai": "huong_nen_tranh",
            "tieu_de": "Gia dinh MT5 yeu (so_cai)",
            "noi_dung": "Family co ti le PASS thap du da thu nhieu: "
                        + ", ".join(k for k, _ in bot)
                        + ". Giam uu tien sinh viec moi; van giu vong 2 neu da pass 1 lan.",
            "bang_chung": bc,
            "ngay": ngay,
            "nguon": "hoc_tu_so_cai",
        })
    # TF
    tf = agg.get("tf") or {}
    if tf:
        best_tf = max(tf.items(), key=lambda kv: (kv[1]["ti_le_pass"] if kv[1]["pass"]+kv[1]["fail"]>=5 else -1, kv[1]["pass"]))
        cards.append({
            "ma": "mt5_tf_%s" % ngay.replace("-", ""),
            "loai": "su_that_tai_san",
            "tieu_de": "Khung thoi gian manh nhat",
            "noi_dung": "Tren so_cai, khung %s co ti le PASS cao nhat trong cac khung du mau."
                        % best_tf[0],
            "bang_chung": "%s pass=%d fail=%d rate=%.0f%% apy_tb=%s" % (
                best_tf[0], best_tf[1]["pass"], best_tf[1]["fail"],
                100 * best_tf[1]["ti_le_pass"], best_tf[1].get("apy_tb")),
            "ngay": ngay,
            "nguon": "hoc_tu_so_cai",
        })
    # Entry
    vao = agg.get("vao") or {}
    if vao:
        ranked = sorted(
            [(k, v) for k, v in vao.items() if v["pass"] + v["fail"] >= 3],
            key=lambda kv: -kv[1]["ti_le_pass"],
        )
        if ranked:
            cards.append({
                "ma": "mt5_vao_%s" % ngay.replace("-", ""),
                "loai": "huong_dang_mo",
                "tieu_de": "Kieu vao (InpVao) dang an",
                "noi_dung": "Entry type manh: " + ", ".join(
                    "%s (rate %.0f%%, n=%d)" % (k, 100 * v["ti_le_pass"], v["n"])
                    for k, v in ranked[:3]),
                "bang_chung": "; ".join(
                    "%s p=%d f=%d" % (k, v["pass"], v["fail"]) for k, v in ranked[:4]),
                "ngay": ngay,
                "nguon": "hoc_tu_so_cai",
            })
    # Symbol
    ma = agg.get("ma") or {}
    top_ma = sorted(
        [(k, v) for k, v in ma.items() if v["pass"] >= 2],
        key=lambda kv: (-kv[1]["pass"], -kv[1]["ti_le_pass"]),
    )[:6]
    if top_ma:
        cards.append({
            "ma": "mt5_ma_%s" % ngay.replace("-", ""),
            "loai": "su_that_tai_san",
            "tieu_de": "Cap co nhieu PASS",
            "noi_dung": "Uu tien vong 2 cross-symbol / SEEKER tren: "
                        + ", ".join(k for k, _ in top_ma),
            "bang_chung": "; ".join(
                "%s pass=%d rate=%.0f%%" % (k, v["pass"], 100 * v["ti_le_pass"])
                for k, v in top_ma),
            "ngay": ngay,
            "nguon": "hoc_tu_so_cai",
        })
    # Throughput note
    n_pass = sum(1 for r in rows if _nhan_pass(r) == "pass")
    n_all = len(rows)
    cards.append({
        "ma": "mt5_throughput_%s" % ngay.replace("-", ""),
        "loai": "bay_do_luong",
        "tieu_de": "Suat PASS so_cai (muc tieu 1000/ngay → ≥5 ung vien)",
        "noi_dung": "Hien co %d dong so_cai unique, %d PASS theo rule (loi>0, DD<=80, APY>=10). "
                    "Muc tieu van hanh: ~1000 strategy/ngay de ky vong ≥5 ung vien moi; "
                    "vong 2 nham ~50 he goc." % (n_all, n_pass),
        "bang_chung": "n=%d pass=%d ti_le=%.3f" % (n_all, n_pass, n_pass / max(n_all, 1)),
        "ngay": ngay,
        "nguon": "hoc_tu_so_cai",
    })
    return cards


def ghi_md(agg, trong_so, cards, rows) -> str:
    n_pass = sum(1 for r in rows if _nhan_pass(r) == "pass")
    L = [
        "# Bài học từ sổ cái MT5 (learning loop)",
        "",
        "Lúc: %s (Asia/Bangkok, UTC+7)." % time.strftime("%Y-%m-%d %H:%M"),
        "",
        "Nguồn: `so_cai*.jsonl` (máy nhà + box). Pass = lãi sau phí, DD ≤ 80 %, ≥ 10 %/năm.",
        "",
        "## Tóm tắt",
        "",
        "- Dòng ledger unique: **%d**" % len(rows),
        "- PASS: **%d** (%.1f %%)" % (n_pass, 100 * n_pass / max(len(rows), 1)),
        "- Priors máy: `data/bai_hoc.json` (tools/vong2.py đọc `trong_so`).",
        "- Thẻ `nhan.bai_hoc`: %d thẻ ghi từ vòng học này." % len(cards),
        "",
        "## Key lessons",
        "",
    ]
    for c in cards:
        L.append("- **[%s]** %s — %s" % (c["loai"], c["tieu_de"], c["bang_chung"][:160]))
    for dim, title in (("gia_dinh", "Gia đình EA"), ("tf", "Khung"), ("ma", "Cặp"),
                       ("vao", "Kiểu vào"), ("tp", "TP bucket"), ("buoc", "Bước DCA")):
        L += ["", "## " + title, "",
              "| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |",
              "|---|---|---|---|---|---|---|---|---|"]
        table = agg.get(dim) or {}
        rows_s = sorted(table.items(), key=lambda kv: (-kv[1]["pass"], -kv[1]["ti_le_pass"]))[:15]
        for k, v in rows_s:
            L.append("| %s | %d | %d | %d | %.0f%% | %s | %s | %s | %s |" % (
                k, v["n"], v["pass"], v["fail"], 100 * v["ti_le_pass"],
                v.get("net_tb"), v.get("dd_tb"), v.get("apy_tb"),
                (trong_so.get(dim) or {}).get(k, "—")))
    L += ["", "## Cách feed-back",
          "",
          "1. `tools/vong2.py` — `nap_priors()` cộng điểm family/tf/ma khi xếp PASS.",
          "2. `nhan.bai_hoc.tra` — NGHI/uu_tien hỏi trước khi đào hướng mới.",
          "3. Chạy lại sau mỗi phiên MT5: `python tools/hoc_tu_so_cai.py`.",
          ""]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    return str(OUT_MD)


def ghi_nao(cards) -> int:
    try:
        from nhan import bai_hoc as BH
    except Exception as e:
        print("skip nao:", e)
        return 0
    n = 0
    for c in cards:
        kq = BH.them(
            ma=c["ma"], loai=c["loai"], tieu_de=c["tieu_de"], noi_dung=c["noi_dung"],
            bang_chung=c.get("bang_chung", ""), ngay=c.get("ngay", ""),
            nguon=c.get("nguon", "hoc_tu_so_cai"),
        )
        if kq.get("nhan"):
            n += 1
    return n


def chay() -> dict:
    rows = _doc_rows()
    agg = _bucket(rows)
    w = _trong_so(agg)
    cards = _bai_hoc_cards(agg, w, rows)
    payload = {
        "luc": time.strftime("%Y-%m-%d %H:%M"),
        "n_dong": len(rows),
        "n_pass": sum(1 for r in rows if _nhan_pass(r) == "pass"),
        "tong_hop": agg,
        "trong_so": w,
        "the": [{"ma": c["ma"], "loai": c["loai"], "tieu_de": c["tieu_de"]} for c in cards],
        "muc_tieu": {"strategy_per_day": 1000, "candidates_per_day": 5, "vong2_he_goc": 50},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ghi_md(agg, w, cards, rows)
    n_nao = ghi_nao(cards)
    return {"json": str(OUT_JSON), "md": md, "n_dong": payload["n_dong"],
            "n_pass": payload["n_pass"], "n_the_nao": n_nao, "trong_so": w}


def main():
    kq = chay()
    print(json.dumps({k: kq[k] for k in ("json", "md", "n_dong", "n_pass", "n_the_nao")},
                     ensure_ascii=False, indent=2))
    # print top weights
    w = kq["trong_so"]
    for dim in ("gia_dinh", "tf", "ma", "vao"):
        items = sorted((w.get(dim) or {}).items(), key=lambda kv: -kv[1])[:6]
        print(dim, items)


if __name__ == "__main__":
    raise SystemExit(main() or 0)
