"""Sổ kết quả chung (ledger) cho mọi lần test/backtest của mọi phiên/bot.

Dùng:
    python -m nhan.so_ket_qua --thu-hoach      # gom lại toàn bộ kết quả có trong repo
    python -m nhan.so_ket_qua --tong-hop       # sinh TRI_NHO/so_ket_qua/TONG_HOP.md

API cho module khác (gọi sau mỗi lần chạy):
    from nhan.so_ket_qua import ghi_ket_qua
    ghi_ket_qua({"he": ..., "symbol": ..., "nguon": "mt5_real_tick", "net": ..., "cagr_pct": ..., "dd_pct": ..., ...})

Quy tắc: không bịa số. Ô không có dữ liệu để trống. Kết quả trước khi vá lỗi lot CSV
(2026-10-31 01:53 UTC+7) bị đánh dấu BI_THAY_THE. Tiêu chí ĐẠT duy nhất:
max DD < 80% VÀ CAGR > 10%/năm.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
THU_MUC = GOC / "TRI_NHO" / "so_ket_qua"
SO = THU_MUC / "ket_qua.csv"
MOC_VA_LOT = "2026-10-31T01:53:00"  # giờ UTC+7
DD_MAX = 80.0
CAGR_MIN = 10.0

COT = ["id", "he", "symbol", "timeframe", "tu", "den", "so_nam", "nguon", "real_tick_pct",
       "net", "von", "cagr_pct", "dd_pct", "so_lenh", "phi", "luc_chay", "phien_bot",
       "commit", "tep_goc", "trang_thai", "ghi_chu"]
TRANG_THAI = ("DAT", "KHONG_DAT", "BI_THAY_THE", "CHUA_DO", "UNG_VIEN")  # UNG_VIEN: dat so nhung kiem toan ha (03/11)


def _so(x):
    if x is None or x == "":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def tinh_cagr(net, von, so_nam):
    net, von, so_nam = _so(net), _so(von), _so(so_nam)
    if net is None or not von or not so_nam or so_nam <= 0:
        return None
    hs = 1 + net / von
    if hs <= 0:
        return -100.0
    return round((hs ** (1 / so_nam) - 1) * 100, 2)


def xet_trang_thai(d):
    """Trả về trạng thái theo đúng tiêu chí DD<80 & CAGR>10 và mốc vá lot."""
    luc = str(d.get("luc_chay") or "")
    if luc and luc[:19] < MOC_VA_LOT:
        return "BI_THAY_THE"
    cagr, dd = _so(d.get("cagr_pct")), _so(d.get("dd_pct"))
    if cagr is None or dd is None or not luc:
        return "CHUA_DO"
    if str(d.get("nguon", "")).startswith("python_mo_phong"):
        return "CHUA_DO"  # mô phỏng không bao giờ tự thành ĐẠT
    return "DAT" if (dd < DD_MAX and cagr > CAGR_MIN) else "KHONG_DAT"


def tao_id(d):
    khoa = "|".join(str(d.get(k) or "") for k in
                    ("he", "symbol", "timeframe", "tu", "den", "nguon", "net", "so_lenh", "luc_chay"))
    return hashlib.sha1(khoa.encode("utf-8")).hexdigest()[:16]


def chuan_hoa(d):
    r = {k: d.get(k) for k in COT}
    for k in ("net", "von", "cagr_pct", "dd_pct", "so_nam", "real_tick_pct", "so_lenh"):
        v = _so(r.get(k))
        r[k] = "" if v is None else (int(v) if k == "so_lenh" else round(v, 4))
    if r["cagr_pct"] == "" and r["net"] != "":
        c = tinh_cagr(r["net"], r["von"], r["so_nam"])
        r["cagr_pct"] = "" if c is None else c
    r = {k: ("" if v is None else v) for k, v in r.items()}
    if not r["id"]:
        r["id"] = tao_id(r)
    if r["trang_thai"] not in TRANG_THAI or r["trang_thai"] in ("DAT", "KHONG_DAT", ""):
        # luôn xét lại DAT/KHONG_DAT để không ai tự gán ĐẠT sai tiêu chí
        if r["trang_thai"] != "BI_THAY_THE" and r["trang_thai"] != "CHUA_DO":
            r["trang_thai"] = xet_trang_thai(r)
    return r


def doc_so(duong=SO):
    if not Path(duong).exists():
        return []
    with open(duong, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ghi_so(dong, duong=SO):
    Path(duong).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(duong) + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        for r in dong:
            w.writerow({k: r.get(k, "") for k in COT})
    os.replace(tmp, duong)


def gop(cu, moi):
    """Gộp + khử trùng theo id (giữ dòng đầu tiên)."""
    thay, ra = set(), []
    for r in list(cu) + list(moi):
        r = chuan_hoa(r)
        if r["id"] in thay:
            continue
        thay.add(r["id"])
        ra.append(r)
    return ra


def ghi_ket_qua(ket_qua, duong=SO):
    """API append: module khác gọi sau mỗi lần chạy. Trả về dòng đã chuẩn hoá.
    ket_qua có thể là dict hoặc list dict. Bắt buộc có 'he' và 'nguon'."""
    ds = ket_qua if isinstance(ket_qua, list) else [ket_qua]
    for d in ds:
        if not d.get("he") or not d.get("nguon"):
            raise ValueError("thiếu 'he' hoặc 'nguon'")
        d.setdefault("luc_chay", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        d.setdefault("commit", _commit_hien_tai())
        d["trang_thai"] = d.get("trang_thai") or ""
    cu = doc_so(duong)
    moi = gop(cu, ds)
    ghi_so(moi, duong)
    return moi[len(cu):]


# ---------------- thu hoạch từ repo ----------------

def _git(*a):
    try:
        return subprocess.run(["git", *a], cwd=GOC, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def _commit_hien_tai():
    return _git("rev-parse", "--short", "HEAD")


def _commit_tep(p):
    return _git("log", "-1", "--format=%h", "--", str(p))


def _ngay_tep(p):
    return _git("log", "-1", "--format=%ad", "--date=format:%Y-%m-%dT%H:%M:%S", "--", str(p))


def _rel(p):
    try:
        return str(Path(p).resolve().relative_to(GOC))
    except ValueError:
        return str(p)


def _bot_theo_ngay(luc):
    """Đoán phiên/bot theo ngày (theo lịch sử git); không chắc thì ghi rõ."""
    ngay = (luc or "")[:10]
    if "2026-10-16" <= ngay <= "2026-10-18":
        return "Claude/thebrainago (doan theo ngay)"
    if ngay:
        return "may_nha MT5 (thebrainago/Grok/Claude) - doan theo ngay"
    return "CHUA_RO"


def thu_so_cai_mt5(p):
    """Sổ cái MT5 dạng jsonl (reports/mt5_lien_tuc/so_cai.jsonl, 955 lần chạy máy nhà)."""
    ra, commit, rel = [], _commit_tep(p), _rel(p)
    for dong in open(p, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(dong)
        except ValueError:
            continue
        tu = den = ""
        m = re.search(r"\((\d{4}\.\d\d\.\d\d) - (\d{4}\.\d\d\.\d\d)\)", d.get("ky_bc") or "")
        so_nam = None
        if m:
            tu, den = m.group(1).replace(".", "-"), m.group(2).replace(".", "-")
            so_nam = round((datetime.fromisoformat(den) - datetime.fromisoformat(tu)).days / 365.25, 3)
        dd_pct = von = None
        mdd = re.search(r"\(([\d.]+)%\)", str(d.get("dd") or ""))  # 03/11: DD MT5 co dau cach nghin "2 076.85 (14.81%)"
        if mdd:
            dd_pct = float(mdd.group(1))
        von = d.get("von")
        tick = re.match(r"\s*(\d+)", str(d.get("chat_luong") or ""))
        ghi = []
        if d.get("loi"):
            ghi.append("loi=" + str(d["loi"]))
        if d.get("pha"):
            ghi.append("pha=" + str(d["pha"]))
        if not von:
            ghi.append("von khong ghi trong so cai -> CAGR CHUA DO DUOC")
        r = {"he": d.get("ten") or f"{d.get('ea')}:{d.get('file', '')}", "symbol": d.get("ma"),
             "timeframe": d.get("tf"), "tu": tu, "den": den, "so_nam": so_nam,
             "nguon": "mt5_real_tick" if tick and int(tick.group(1)) >= 90 else "mt5_tester",
             "real_tick_pct": tick.group(1) if tick else None, "net": d.get("net"), "von": von,
             "dd_pct": dd_pct, "so_lenh": d.get("lenh"), "phi": "XM that (EA BRAIN)" if d.get("san") == "XM" else "",
             "luc_chay": d.get("luc"), "phien_bot": _bot_theo_ngay(d.get("luc")), "commit": commit,
             "tep_goc": rel + "#" + str(d.get("file", "")), "ghi_chu": "; ".join(ghi)}
        if d.get("loi") or d.get("net") is None:
            r["trang_thai"] = "BI_THAY_THE" if (d.get("luc") or "") < MOC_VA_LOT else "CHUA_DO"
        ra.append(r)
    return ra


def thu_vong2(p):
    """reports/vong2/ket_qua_vong2.json: 78 hệ MT5 vòng 2 (đã tái dựng equity, CAGR)."""
    d = json.load(open(p, encoding="utf-8"))
    luc, commit, rel = d.get("luc") or _ngay_tep(p), _commit_tep(p), _rel(p)
    ra = []
    for ten, v in (d.get("mt5") or {}).items():
        if not isinstance(v, dict) or v.get("loi"):
            continue
        ra.append({"he": ten, "symbol": v.get("symbol") or v.get("ma") or "", "timeframe": v.get("tf") or "",
                   "tu": v.get("tu"), "den": v.get("den"), "so_nam": v.get("so_nam"), "nguon": "mt5_real_tick",
                   "net": v.get("lai_rong_tai_dung"), "von": 1000, "cagr_pct": v.get("lai_kep_pct_nam"),
                   "dd_pct": v.get("dd_equity_pct"), "so_lenh": v.get("so_lenh"),
                   "phi": "XM micro; stress x1.5+7USD (lai_kep_stress=%s)" % v.get("lai_kep_stress_pct_nam"),
                   "luc_chay": luc, "phien_bot": "box vong2 (thebrainago/Grok Bot)", "commit": commit,
                   "tep_goc": rel, "ghi_chu": "von 1000 theo CHIEN_LUOC_DA_LOC; = 78 he 'DAT' cu"})
    return ra


def thu_bench_qt(p):
    d = json.load(open(p, encoding="utf-8"))
    luc, commit, rel = _ngay_tep(p), _commit_tep(p), _rel(p)
    tu, den = "", ""
    m = re.match(r"(\d{4}\.\d\d\.\d\d)\.\.(\d{4}\.\d\d\.\d\d)", d.get("cua_so") or "")
    if m:
        tu, den = m.group(1).replace(".", "-"), m.group(2).replace(".", "-")
    ra = []
    for ho, v in list((d.get("tot_moi_ho") or {}).items()) + [("moc", d.get("moc") or {})]:
        if not isinstance(v, dict) or "lai" not in v:
            continue
        ra.append({"he": f"bench_qt:{p.stem}:{ho}", "symbol": d.get("symbol"), "timeframe": d.get("khung"),
                   "tu": tu, "den": den, "nguon": "mt5_tester (bench quan tri)", "net": v.get("lai"),
                   "dd_pct": v.get("dd_pct"), "so_lenh": v.get("lenh"), "luc_chay": luc,
                   "phien_bot": "SV STORE/Grok (doan theo ngay)", "commit": commit, "tep_goc": rel,
                   "ghi_chu": "von khong ghi -> CAGR CHUA DO DUOC"})
    return ra


# Kết quả chỉ tồn tại dạng bảng trong tài liệu (số chép NGUYÊN VĂN từ tài liệu, không tính thêm).
TAI_LIEU_TINH = [
    # tai_lieu/BAN_GIAO_CLAUDE_21_10.md mục 3 — Python MÔ PHỎNG, chưa đo MT5
    *[{"he": t, "symbol": s, "timeframe": tf, "nguon": "python_mo_phong", "cagr_pct": c, "dd_pct": dd,
       "luc_chay": "2026-10-21T22:15:00", "phien_bot": "Grok Bot (dich tay dot %s)" % dot,
       "tep_goc": "tai_lieu/BAN_GIAO_CLAUDE_21_10.md", "ghi_chu": "MÔ PHỎNG; " + ea}
      for dot, t, ea, s, tf, c, dd in [
        (3, "sk_ea_2f4540d68a", "GridScalperEA", "AUDUSD", "H1", 86.9, 45.1),
        (3, "sk_ea_3d5da5b65e", "Sniper Gold Hybrid Recovery", "XAUUSD", "H4", 33.6, 63.7),
        (3, "sk_ea_9345f47763", "MakeGrid193", "EURUSD", "H1", 24.8, 50.5),
        (3, "sk_ea_b18d784179", "Zerith XAU SwingGrid Recovery", "GBPUSD", "H1", 19.0, 20.0),
        (3, "sk_ea_31b7c0180f", "Zerith MACD Martingale Grid", "GBPUSD", "H4", 18.1, 55.7),
        (3, "sk_ea_8760277bca", "MintyGrid 7.2", "GBPJPY", "H4", 15.4, 43.5),
        (4, "sk_ea_b7faac890a", "Zerith Oneshot", "GBPUSD", "H1", 75.0, 62.2),
        (4, "sk_ea_a0d40c82ed", "Hon-Matrix (gan dung)", "EURUSD", "H1", 19.0, 16.5),
        (5, "sk_ea_37d18e3ece", "ZONE_RECOVERY_AREA_II", "EURCAD", "H1", 62.6, 55.9),
        (5, "sk_ea_c67d5d31e9", "Ichimoku EA v1.3", "GBPCAD", "H4", 33.0, 27.1),
        (5, "sk_ea_42415c4f24", "Trickerless_RHMP (gan dung)", "EURGBP", "H1", 24.5, 50.4),
        (5, "sk_ea_94672bd399", "GBPJPY_EA_scalper_n6", "GBPJPY", "H4", 24.1, 43.4),
        (5, "sk_ea_5056669865", "Zone_Recovery_Formula", "GBPCHF", "H1", 23.0, 36.8)]],
    # reports/kiem_toan_he_dat.md (kiểm toán 01/11) — số đo SAU vá lot theo tài liệu
    {"he": "skea61c (sk_ea_61c21a2049) lot x4", "symbol": "CADJPY", "timeframe": "H4", "tu": "2024-01-10",
     "den": "2026-10-01", "nguon": "mt5_real_tick", "real_tick_pct": 100, "net": 4039.2, "cagr_pct": 13.3,
     "dd_pct": 10.74, "so_lenh": 199, "luc_chay": "2026-10-31T13:56:57", "phien_bot": "Grok Bot (may nha)",
     "tep_goc": "reports/kiem_toan_he_dat.md (so cai goc so_cai_from_nha_1845.jsonl khong con tren box)",
     "trang_thai": "UNG_VIEN", "ghi_chu": "IS: cua so = span CSV; UNG_VIEN theo kiem_toan_he_dat.md (khong OOS sach)"},
    {"he": "brainxlmrz", "symbol": "GBPUSD", "timeframe": "H4", "tu": "2016-01", "den": "2026-10",
     "nguon": "mt5_tester (salvage)", "real_tick_pct": 25, "net": 28317.3, "von": 10000, "so_nam": 10.749,
     "cagr_pct": 13.31, "dd_pct": 78.81, "so_lenh": 1002, "luc_chay": "2026-10-31T15:23:00",
     "phien_bot": "Grok Bot (may nha)", "tep_goc": "reports/kiem_toan_he_dat.md",
     "trang_thai": "UNG_VIEN", "ghi_chu": "salvage orphan; simple 26.34%/nam; khong OOS; UNG_VIEN theo kiem_toan_he_dat.md (DD sat 80%, 25% tick)"},
    {"he": "sk_ea_3279057100", "symbol": "EURGBP", "timeframe": "H1", "nguon": "mt5_real_tick",
     "cagr_pct": 12.2, "dd_pct": 14.8, "luc_chay": "2026-10-31T16:37:51", "phien_bot": "Grok Bot (may nha)",
     "tep_goc": "reports/kiem_toan_he_dat.md",
     "ghi_chu": "IS b50; chua giai ma diem vao; luc chay xac minh 03/11 tu so_cai nhanh fix/r1 (od_v2r2p_b50_skea3279057100, net 3730.95, DD 14.81%)"},
    {"he": "mql5344 (dai han x1)", "symbol": "NZDUSD", "timeframe": "H1", "nguon": "mt5_tester",
     "real_tick_pct": 31, "cagr_pct": 3.5, "dd_pct": 5.3, "luc_chay": "", "phien_bot": "Grok Bot",
     "tep_goc": "reports/kiem_toan_he_dat.md", "trang_thai": "CHUA_DO", "ghi_chu": "luc chay CHUA RO"},
    {"he": "mql5344 lot x4 cua so ngan", "symbol": "NZDUSD", "timeframe": "H1", "nguon": "mt5_tester",
     "cagr_pct": 8.5, "dd_pct": 23.4, "luc_chay": "", "phien_bot": "Grok Bot",
     "tep_goc": "reports/kiem_toan_he_dat.md", "trang_thai": "CHUA_DO", "ghi_chu": "luc chay CHUA RO"},
    {"he": "ghep_0bf2 (verify lot01)", "symbol": "GBPCAD", "timeframe": "H4", "nguon": "mt5_tester",
     "cagr_pct": 10.3, "dd_pct": 14.9, "luc_chay": "2026-10-31T02:05:23", "phien_bot": "Grok Bot (may nha)",
     "tep_goc": "reports/kiem_toan_he_dat.md",
     "ghi_chu": "IS vs CSV; luc chay xac minh 03/11 tu so_cai nhanh fix/r1 (od_v2verify_lot01_full_ghep0bf2, net 3079.62, DD 14.89%)"},
]


def nguon_mac_dinh():
    ra = [GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl"]
    # bản sao khác trên box (nếu có) — khử trùng theo id nên an toàn
    for p in ("/workspace/so_cai_snap.jsonl", "/workspace/wt_vong2/reports/mt5_lien_tuc/so_cai.jsonl",
              "/workspace/brain2_box_wt/reports/mt5_lien_tuc/so_cai.jsonl"):
        if Path(p).exists():
            ra.append(Path(p))
    return ra


def thu_hoach(duong=SO):
    moi, bao = [], {}
    for p in nguon_mac_dinh():
        x = thu_so_cai_mt5(p); moi += x; bao[_rel(p)] = len(x)
    p = GOC / "reports" / "vong2" / "ket_qua_vong2.json"
    if p.exists():
        x = thu_vong2(p); moi += x; bao[_rel(p)] = len(x)
    for p in sorted((GOC / "reports").glob("BENCH_QT_*.json")):
        x = thu_bench_qt(p); moi += x; bao[_rel(p)] = len(x)
    moi += [dict(r) for r in TAI_LIEU_TINH]; bao["(bang trong tai lieu)"] = len(TAI_LIEU_TINH)
    for r in moi:
        r.setdefault("commit", "")
    tat = gop(doc_so(duong), moi)
    ghi_so(tat, duong)
    return tat, bao


def tong_hop(duong=SO, ra=THU_MUC / "TONG_HOP.md"):
    ds = doc_so(duong)
    dem = {t: sum(1 for r in ds if r["trang_thai"] == t) for t in TRANG_THAI}
    dat = [r for r in ds if r["trang_thai"] == "DAT"]
    sau = [r for r in ds if r["trang_thai"] in ("DAT", "KHONG_DAT")]
    L = ["# Tổng hợp sổ kết quả", "",
         f"Sinh tự động bởi `python -m nhan.so_ket_qua --tong-hop` lúc {datetime.now():%Y-%m-%d %H:%M} (UTC+7).",
         "Tiêu chí ĐẠT duy nhất: **max DD < 80% VÀ CAGR > 10%/năm**. Chỉ tính kết quả đo SAU khi vá lỗi lot (31/10/2026 01:53 UTC+7).", "",
         f"Tổng số dòng: **{len(ds)}**", "", "| Trạng thái | Số dòng |", "|---|---|"]
    L += [f"| {t} | {dem[t]} |" for t in TRANG_THAI]
    L += ["", "## Danh sách ĐẠT hiện tại", ""]
    if dat:
        L += ["| Hệ | Mã | TF | CAGR % | DD % | Nguồn |", "|---|---|---|---|---|---|"]
        L += [f"| {r['he']} | {r['symbol']} | {r['timeframe']} | {r['cagr_pct']} | {r['dd_pct']} | {r['tep_goc']} |" for r in dat]
    else:
        L.append("**Chưa có hệ nào ĐẠT** với kết quả hợp lệ sau vá lỗi lot.")
    L += ["", "## Kết quả hợp lệ sau vá (DAT/KHONG_DAT)", "", "| Hệ | Mã | TF | CAGR % | DD % | Trạng thái |", "|---|---|---|---|---|---|"]
    L += [f"| {r['he']} | {r['symbol']} | {r['timeframe']} | {r['cagr_pct']} | {r['dd_pct']} | {r['trang_thai']} |" for r in sau]
    L += ["", "Ghi chú: BI_THAY_THE = đo trước vá lot, phải chạy lại; CHUA_DO = thiếu số/không rõ lúc chạy, hoặc chỉ là MÔ PHỎNG Python."]
    ra.write_text("\n".join(L) + "\n", encoding="utf-8")
    return dem, dat


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if "--thu-hoach" in a:
        tat, bao = thu_hoach()
        print(json.dumps(bao, ensure_ascii=False, indent=1)); print("tong", len(tat))
    if "--tong-hop" in a or "--thu-hoach" in a:
        dem, dat = tong_hop(); print(dem, "DAT:", [r["he"] for r in dat])


if __name__ == "__main__":
    main()
