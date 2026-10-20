# -*- coding: utf-8 -*-
"""so_co_che.py - SO CO CHE co cau truc, doc lap du lieu (20/10/2026 toi, Grok Bot).

Khac `nhan/kho_co_che.py` (manh co che theo VAI TRO, sqlite trong data/ - git bo qua): so nay la MOT BAN GHI / HE
(chien luoc) va CHI chua METADATA de commit duoc: tom tat lenh vao, thoat/TP, DCA/hedge/go, khung, ma, nhan phong cach,
ket qua Python (MO PHONG) va MT5 (DO THAT). KHONG BAO GIO chua ma nguon ben thu ba (ma EA / ma Python LLM / spec day du
nam trong data/ong_dan/trang_thai.sqlite, git bo qua) - ban ghi chi tro toi id the.

Tep:  reports/kho_co_che/so_co_che.jsonl  (moi dong mot he, sap theo id -> diff git gon)
      reports/kho_co_che/SO_CO_CHE.md     (tom tat cho nguoi doc)
Nguon dien lai: data/ong_dan/trang_thai.sqlite (the + ket qua toi uu) + reports/UNG_VIEN.md (bang "Tất cả", so MT5 that).

Chay:
  python -m nhan.so_co_che xay                 # dien lai tu cache + UNG_VIEN, ghi jsonl + md
  python -m nhan.so_co_che tim --tag dca --trang DAT_MT5 --ma GBPCAD --khung H1
  python -m nhan.so_co_che thong_ke
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TEP = GOC / "reports" / "kho_co_che" / "so_co_che.jsonl"
TOM_TAT = GOC / "reports" / "kho_co_che" / "SO_CO_CHE.md"
UNG_VIEN = GOC / "reports" / "UNG_VIEN.md"
DB = GOC / "data" / "ong_dan" / "trang_thai.sqlite"
PHIEN_BAN = 1

#: tu dien nhan phong cach chuan (moi tu khac -> giu nguyen, chu thuong)
BI_DANH = {"quay_ve_trung_binh": "mean_reversion", "mr": "mean_reversion", "xu_huong": "trend", "theo_xu_huong": "trend",
           "trend_following": "trend", "pha_vo": "breakout", "dot_pha": "breakout", "luoi": "grid", "dao_dong": "oscillator",
           "dong_luong": "momentum", "luot_song": "scalping", "scalp": "scalping", "go_lenh": "recovery", "khoa": "hedge",
           "hoa_von": "breakeven", "chot_ro": "basket_tp", "lenh_cho": "pending"}
QUAN_LI_TAG = {"dca", "martingale", "grid", "hedge", "recovery", "trailing", "breakeven", "basket_tp", "go_cheo",
               "dong_mot_phan", "sua_sl_tp"}
TRANG = ("DAT_MT5", "TRUOT_MT5", "CHUA_DO_MT5", "DAT_PY", "GAN_DAT", "TRUOT_PY", "CHUA_DO")
CHAY_PY = ("brain", "spec", "to_hop", "python_llm")


def tag(x: str) -> str:
    x = str(x).strip().lower().replace(" ", "_").replace("-", "_")
    return BI_DANH.get(x, x)


def ma_goc(sym: str | None) -> str:
    """'GBPCADmicro' / 'EURUSD#' / 'XAUUSD' -> ma chuan box ('GBPCAD', 'EURUSD', 'GOLD')."""
    s = re.sub(r"(micro|mini|cent|\.m|#|_i|\.raw|m)$", "", str(sym or ""), flags=re.I).upper()
    return "GOLD" if s in ("XAUUSD", "XAU") else s


def lop_tai_san(ma: str) -> str:
    m = ma_goc(ma)
    if m in ("GOLD", "SILVER", "XAGUSD"):
        return "kim_loai"
    if re.fullmatch(r"[A-Z]{6}", m):
        tien = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"}
        if m[:3] in tien and m[3:] in tien:
            return "fx_chinh" if "USD" in (m[:3], m[3:]) else "fx_cheo"
        if m[:3] in ("BTC", "ETH", "LTC", "XRP"):
            return "crypto"
    if any(k in m for k in ("US30", "US500", "NAS", "SP500", "GER", "DE40", "JP225", "UK100", "SPX")):
        return "chi_so"
    return "khac"


# ------------------------------------------------------------------ the (cache ong dan) -> ban ghi
def _tom_tat_vao(th: dict) -> str:
    k = th.get("kieu")
    if k == "brain":
        return "BRAIN %s %s" % (th.get("tham", {}).get("kieu"), json.dumps({a: b for a, b in (th.get("tham") or {}).items()
                                                                              if a != "kieu"}, ensure_ascii=False)[:160])
    if k == "spec":
        ds = th.get("specs") or []
        return " | ".join(("%s: %s" % (s.get("ten", "spec"), (s.get("co_che") or "")[:160])) for s in ds[:2])[:300]
    if k == "to_hop":
        return "TỔ HỢP: [%s]%s%s" % (_tom_tat_vao(th.get("nguon") or {})[:140],
                                    (" + lọc " + ",".join(str((x.get("tham") or {}).get("kieu")) for x in th["bo_loc"])) if th.get("bo_loc") else "",
                                    (" + nguồn B [%s]" % _tom_tat_vao(th["nguon_b"])[:100]) if th.get("nguon_b") else "")
    if k == "python_llm":
        return "Python dịch bằng LLM (mã trong data/, không commit)"
    if k == "lenh_ngoai":
        return "lệnh statement ngoài"
    return str(k or "chưa dịch")


def _quan_li(ql: dict | None) -> dict:
    ql = ql or {}
    dca = int(ql.get("dca_toi_da") or 0)
    return {"tp_pct": ql.get("tp_pct"), "dca": dca > 0, "dca_toi_da": dca, "dca_buoc_pct": ql.get("dca_buoc_pct") if dca else None,
            "martingale": dca > 0 and float(ql.get("dca_he_so_lot") or 1) > 1.0, "he_so_lot": ql.get("dca_he_so_lot"),
            "hedge": float(ql.get("hedge_khi_lo_pct") or 0) > 0, "hedge_khi_lo_pct": ql.get("hedge_khi_lo_pct") or 0.0,
            "go_cheo": bool(ql.get("go_cheo")), "trailing": float(ql.get("trail_kich_pct") or 0) > 0,
            "lot_tren_1000": ql.get("lot_tren_1000")}


def _tag_ql(q: dict) -> list[str]:
    r = [k for k in ("dca", "martingale", "hedge", "go_cheo", "trailing") if q.get(k)]
    if q.get("hedge"):
        r.append("recovery")
    return r


def tu_the(t: dict, buoc: str, tt: str, kq: dict) -> dict:
    th = t.get("tin_hieu") or {}
    tot = (kq or {}).get("tot_nhat") or {}
    thu, so = tot.get("thu") or {}, tot.get("kq") or {}
    q = _quan_li(thu.get("ql"))
    sk = t.get("seeker") or {}
    pc = [tag(x) for x in (sk.get("phong_cach") or []) + (t.get("ho") or []) + (t.get("quan_tri_goc") or [])]
    pc += [tag(s.get("ho")) for s in th.get("specs") or [] if s.get("ho") and s.get("ho") != "khac"]
    if th.get("kieu") == "brain":
        pc.append(tag((th.get("tham") or {}).get("kieu", "brain")))
    pc_ql = _tag_ql(q)
    ma = [ma_goc(m) for m in ([thu.get("ma")] + list(t.get("ma_goi_y") or []) + list(sk.get("tai_san") or [])) if m]
    khung = [k for k in [thu.get("khung"), t.get("khung_ea")] + list(sk.get("khung") or []) if k]
    py = {}
    if so and not so.get("loi"):
        py = {k: so.get(k) for k in ("lai_pct_nam", "sut_giam_pct", "so_stop_out", "so_lenh", "so_nam") if so.get(k) is not None}
        py.update(ma=thu.get("ma"), khung=thu.get("khung"), nhan="MÔ PHỎNG")
    elif so.get("loi"):
        py = {"loi": str(so["loi"])[:160]}
    ng = t.get("nguon") or {}
    r = {"id": t["id"], "ten": str(t.get("ten", ""))[:120], "nen_tang": t.get("nen_tang"),
         "nguon": {"kho": ng.get("kho"), "url": ng.get("url") or sk.get("url")},
         "duong_dich": t.get("duong_dich"), "kieu_tin_hieu": th.get("kieu"), "chay_python": th.get("kieu") in CHAY_PY,
         "vao": _tom_tat_vao(th), "thoat": ("TP %.3g%%" % (100 * q["tp_pct"])) if q.get("tp_pct") else "theo EA / chưa đo",
         "quan_li": q, "khung": sorted(set(khung)), "ma": sorted(set(ma)),
         "tai_san": sorted({lop_tai_san(m) for m in ma}),
         "phong_cach": sorted(set(x for x in pc if x and x not in QUAN_LI_TAG)),
         "phong_cach_quan_li": sorted(set([x for x in pc if x in QUAN_LI_TAG] + pc_ql)),
         "python": py, "loc_python": ((kq or {}).get("loc") or {}).get("dat"), "mt5": [],
         "buoc": buoc, "trang_thai_ong": tt, "thanh_phan": list(t.get("thanh_phan") or []),
         "ghep": t.get("ghep_cheo") or None}
    return r


# ------------------------------------------------------------------ UNG_VIEN.md (so MT5 that)
def doc_ung_vien(p: Path = UNG_VIEN) -> list[dict]:
    """Bang "Tất cả" cua UNG_VIEN.md -> [{ket_luan, ten, the_id, symbol, tf, lai_rong, lai_kep, lai_don, dd, pf, lenh, stop_out, ky, ly_do}]."""
    if not p.exists():
        return []
    ra, trong = [], False
    for d in p.read_text(encoding="utf-8").splitlines():
        if d.startswith("## "):
            trong = d.strip() == "## Tất cả"
            continue
        if not trong or not d.startswith("|") or d.startswith("|---") or "Kết luận" in d:
            continue
        c = [x.strip() for x in d.strip().strip("|").split("|")]
        if len(c) < 15:
            continue

        def f(x):
            try:
                return float(x)
            except ValueError:
                return None
        ra.append({"ket_luan": c[0], "ten": c[1], "the_id": c[2], "symbol": c[3], "tf": c[4], "lai_rong": f(c[5]),
                   "lai_kep_pct_nam": f(c[6]), "lai_don_pct_nam": f(c[7]), "dd_von_pct": f(c[8]), "pf": f(c[9]),
                   "lenh": f(c[10]), "stop_out": f(c[11]), "ky": c[13], "ly_do": c[15] if len(c) > 15 else "",
                   "nhan": "ĐO THẬT MT5 real tick"})
    return ra


def trang_thai(r: dict) -> str:
    from nhan import nguong as NG
    mt = r.get("mt5") or []
    if any(x["ket_luan"] == "ĐẠT" for x in mt):
        return "DAT_MT5"
    if any(x["ket_luan"] == "TRƯỢT" for x in mt):
        return "TRUOT_MT5"
    if mt:
        return "CHUA_DO_MT5"
    py = r.get("python") or {}
    if py.get("lai_pct_nam") is None:
        return "CHUA_DO"
    if NG.dat(py["lai_pct_nam"], py.get("sut_giam_pct"), "loc_python", py.get("so_stop_out") or 0)["dat"]:
        return "DAT_PY"
    if gan_dat(py):
        return "GAN_DAT"
    return "TRUOT_PY"


def gan_dat(py: dict, ti_le: float = 0.6) -> bool:
    """GẦN ĐẠT: chưa qua 65/15 nhưng lãi >= 60% ngưỡng và DD <= 80%, không stop-out -> đáng đem ghép."""
    from nhan import nguong as NG
    t = NG.tang("loc_python")
    try:
        return (float(py["lai_pct_nam"]) >= ti_le * t["lai_nam_toi_thieu_pct"] and float(py["sut_giam_pct"]) <= 80.0
                and not py.get("so_stop_out"))
    except (KeyError, TypeError, ValueError):
        return False


def xay(db: Path | None = DB, ung_vien: Path = UNG_VIEN) -> list[dict]:
    ds: dict[str, dict] = {}
    p = Path(db) if db else None
    if p and p.exists():
        cn = sqlite3.connect(str(p), timeout=30)
        try:
            for js, buoc, tt, kq in cn.execute("SELECT json, buoc, trang_thai, kq FROM the WHERE buoc IN "
                                               "('toi_uu','loc','sinh_mt5','goi','doc_mt5') OR json LIKE '%\"ghep_cheo\"%'"):
                t = json.loads(js)
                ds[t["id"]] = tu_the(t, buoc, tt, json.loads(kq or "{}"))
        finally:
            cn.close()
    for u in doc_ung_vien(ung_vien):
        r = ds.get(u["the_id"])
        if r is None:                    # the khong co trong cache box (vd may nha) -> ban ghi toi thieu
            r = ds[u["the_id"]] = {"id": u["the_id"], "ten": u["ten"], "vao": "chưa có trong cache box", "chay_python": False,
                                   "quan_li": {}, "khung": [], "ma": [], "tai_san": [], "phong_cach": [],
                                   "phong_cach_quan_li": [], "python": {}, "mt5": [], "thanh_phan": []}
        r.setdefault("mt5", []).append({k: u[k] for k in u if k not in ("the_id",)})
        r["ma"] = sorted(set(r.get("ma") or []) | {ma_goc(u["symbol"])})
        r["khung"] = sorted(set(r.get("khung") or []) | {u["tf"]})
        r["tai_san"] = sorted({lop_tai_san(m) for m in r["ma"]})
    for r in ds.values():
        r["trang_thai"] = trang_thai(r)
        r["phien_ban"] = PHIEN_BAN
    return sorted(ds.values(), key=lambda r: r["id"])


def luu(ds: list[dict], tep: Path = TEP) -> Path:
    tep = Path(tep)
    tep.parent.mkdir(parents=True, exist_ok=True)
    tmp = tep.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in ds), encoding="utf-8")
    tmp.replace(tep)
    return tep


def doc(tep: Path = TEP) -> list[dict]:
    tep = Path(tep)
    if not tep.exists():
        return []
    return [json.loads(x) for x in tep.read_text(encoding="utf-8").splitlines() if x.strip()]


def tim(ds: list[dict], tag_: str | None = None, trang: str | None = None, ma: str | None = None, khung: str | None = None,
        lai_min: float | None = None, chay_python: bool | None = None) -> list[dict]:
    ra = []
    for r in ds:
        if tag_ and tag(tag_) not in set(r.get("phong_cach", [])) | set(r.get("phong_cach_quan_li", [])) | set(r.get("tai_san", [])):
            continue
        if trang and r.get("trang_thai") not in set(trang.split(",")):
            continue
        if ma and ma_goc(ma) not in r.get("ma", []):
            continue
        if khung and khung.upper() not in r.get("khung", []):
            continue
        if chay_python is not None and bool(r.get("chay_python")) != chay_python:
            continue
        if lai_min is not None and (diem_lai(r) or -1e9) < lai_min:
            continue
        ra.append(r)
    return sorted(ra, key=lambda r: -(diem_lai(r) or -1e9))


def diem_lai(r: dict) -> float | None:
    """%/nam tot nhat: MT5 (kep) neu co, khong thi Python."""
    v = [x.get("lai_kep_pct_nam") for x in r.get("mt5") or [] if x.get("ket_luan") == "ĐẠT" and x.get("lai_kep_pct_nam") is not None]
    if v:
        return max(v)
    return (r.get("python") or {}).get("lai_pct_nam")


def thong_ke(ds: list[dict]) -> dict:
    from collections import Counter
    return {"tong": len(ds), "trang_thai": dict(Counter(r.get("trang_thai") for r in ds)),
            "phong_cach": dict(Counter(x for r in ds for x in r.get("phong_cach", [])).most_common(15)),
            "quan_li": dict(Counter(x for r in ds for x in r.get("phong_cach_quan_li", [])).most_common(10)),
            "tai_san": dict(Counter(x for r in ds for x in r.get("tai_san", []))),
            "chay_python": sum(1 for r in ds if r.get("chay_python")),
            "ghep_cheo": sum(1 for r in ds if r.get("ghep"))}


def ghi_md(ds: list[dict], ra: Path = TOM_TAT) -> str:
    tk = thong_ke(ds)
    d = ["# Sổ cơ chế (tự sinh bởi `python -m nhan.so_co_che xay`, đừng sửa tay)", "",
         "Một dòng mỗi hệ, chỉ metadata (không có mã nguồn bên thứ ba). Số Python là MÔ PHỎNG; số MT5 là ĐO THẬT real tick "
         "lấy từ `reports/UNG_VIEN.md`. Bản đầy đủ: `reports/kho_co_che/so_co_che.jsonl`.", "",
         "Cập nhật: %s (giờ máy chạy). Tổng %d hệ; trạng thái: %s." % (
             time.strftime("%d/%m/%Y %H:%M"), tk["tong"], ", ".join("%s %d" % (k, v) for k, v in sorted(tk["trang_thai"].items()))), "",
         "Phong cách vào lệnh nhiều nhất: %s." % (", ".join("%s %d" % kv for kv in tk["phong_cach"].items()) or "—"), "",
         "Quản lí: %s." % (", ".join("%s %d" % kv for kv in tk["quan_li"].items()) or "—"), "",
         "## Hệ đạt / gần đạt (tối đa 80)", "",
         "| id | Trạng thái | Mã | TF | Phong cách | Quản lí | %/năm (MT5 kép hoặc Python) | DD % | Vào lệnh |", "|---|---|---|---|---|---|---|---|---|"]
    for r in tim(ds, trang="DAT_MT5,DAT_PY,GAN_DAT")[:80]:
        mt = [x for x in r.get("mt5") or [] if x.get("ket_luan") == "ĐẠT"]
        dd = mt[0].get("dd_von_pct") if mt else (r.get("python") or {}).get("sut_giam_pct")
        d.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"][:40], r["trang_thai"], ",".join(r.get("ma", []))[:30], ",".join(r.get("khung", [])),
            ",".join(r.get("phong_cach", []))[:40], ",".join(r.get("phong_cach_quan_li", []))[:30],
            "%.1f" % diem_lai(r) if diem_lai(r) is not None else "—", "%.1f" % dd if isinstance(dd, (int, float)) else "—",
            r.get("vao", "").replace("|", "/")[:90]))
    s = "\n".join(d) + "\n"
    Path(ra).parent.mkdir(parents=True, exist_ok=True)
    Path(ra).write_text(s, encoding="utf-8")
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="So co che co cau truc (metadata, commit duoc)")
    ap.add_argument("lenh", choices=["xay", "tim", "thong_ke"])
    ap.add_argument("--tag"); ap.add_argument("--trang"); ap.add_argument("--ma"); ap.add_argument("--khung")
    ap.add_argument("--lai_min", type=float); ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--db"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.lenh == "xay":
        ds = xay(Path(a.db) if a.db else DB)
        luu(ds)
        ghi_md(ds)
        print(json.dumps(thong_ke(ds), ensure_ascii=False))
        return 0
    ds = doc()
    if a.lenh == "thong_ke":
        print(json.dumps(thong_ke(ds), ensure_ascii=False, indent=1))
        return 0
    kq = tim(ds, a.tag, a.trang, a.ma, a.khung, a.lai_min)[:a.n]
    for r in kq:
        print(json.dumps(r, ensure_ascii=False) if a.json else "%-34s %-11s %-14s %-6s %6s  %s | %s" % (
            r["id"][:34], r.get("trang_thai"), ",".join(r.get("ma", []))[:14], ",".join(r.get("khung", []))[:6],
            ("%.1f" % diem_lai(r)) if diem_lai(r) is not None else "—", ",".join(r.get("phong_cach", []))[:30],
            ",".join(r.get("phong_cach_quan_li", []))[:30]))
    print("(%d / %d)" % (len(kq), len(ds)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
