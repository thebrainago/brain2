# -*- coding: utf-8 -*-
"""Đặc điểm tốt của MỌI hệ đã test — kể cả hệ trượt (Anh 03/11/2026). Mảnh dùng để ghép sau này.

Mỗi hệ (gộp theo mã nguồn gốc) -> TRI_NHO/dac_diem_he/<id>.md (+ .json máy đọc); mục lục TRI_NHO/DAC_DIEM_TOT.md.
Đặc điểm: kiểu vào/quản lý lệnh (từ spec/tên), mã + khung chạy tốt nhất, năm có lãi (từ bảng Deals MT5 nếu có),
PF, tỉ lệ thắng, DD, k lot an toàn, lý do trượt. Thiếu số -> 'CHƯA ĐO ĐƯỢC'. Kết quả BI_THAY_THE (lỗi lot CSV) chỉ đếm, không lấy số.
    python -m nhan.dac_diem_he            # điền lại từ sổ kết quả + báo cáo .htm
Thợ MT5 gọi `tu_ket_qua_tho(spec, ket_qua)` sau mỗi việc (tự động).
"""
from __future__ import annotations
import csv, html, json, re
from collections import defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
THU = GOC / "TRI_NHO/dac_diem_he"
MUC_LUC = GOC / "TRI_NHO/DAC_DIEM_TOT.md"
SO = GOC / "TRI_NHO/so_ket_qua/ket_qua.csv"
HTM = GOC / "reports/ong_dan/ket_qua_mt5"
DD_MAX, CAGR_MIN = 80.0, 10.0


# ---------------- hàm thuần ----------------
def ma_goc(he: str) -> str:
    """Tên lần chạy -> id hệ gốc. 'od_v2r2p_b80_skea3279057100_XM_CSV' -> 'skea3279057100'; 'MRZ:lt_MRZ_AUDUSD_D1_IS_1.htm' -> 'MRZ_AUDUSD_D1'."""
    h = re.sub(r":lot[^:]*$", "", str(he))
    h = re.sub(r"\s*\((verify|lot)[^)]*\)", "", h)
    h = re.sub(r"\.htm$", "", h.split(":", 1)[-1] if not h.startswith("DichNguoc") else h.split(":", 1)[-1])
    h = re.sub(r"sk_(ea|st)_([0-9a-f]{6,})", r"sk\1\2", h)
    h = re.sub(r"ghep_([0-9a-f]{4,})", r"ghep\1", h)
    h = re.sub(r"mql5_([0-9a-f]{6,})", r"mql5\1", h)
    h = re.sub(r"_+(swap_do|swap_bao_thu|swap_0_lac_quan)", "", h)
    h = re.sub(r"_+lot[_x0-9a-z]*$", "", h, flags=re.I)
    m = re.search(r"((?:skea|skst|mql5|ghep|brainxl|sk)[0-9a-z]*?[0-9a-f]{6,}|brainxl[a-z]+)", h)
    if m:
        return m.group(1)
    m = re.search(r"od_([A-Za-z0-9]+?)_(?:XM|Exness)", h)
    if m:
        return m.group(1)
    h = re.sub(r"^(lt|sc|hd|od)_", "", h)
    h = re.sub(r"_(IS|OOS|TOAN)?_?\d{5,}$", "", h)
    return re.sub(r"[^A-Za-z0-9_]", "_", h)[:60] or "khong_ten"


def so(x):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None


def deals_theo_nam(deals: list[list]) -> dict:
    """[[thoi_gian 'YYYY.MM.DD ...', rong]] -> {nam: lãi}, tỉ lệ thắng %, số lệnh."""
    nam: dict = defaultdict(float); thang = 0
    for tg, x in deals:
        nam[str(tg)[:4]] += x; thang += x > 0
    return {"lai_theo_nam": {k: round(v, 2) for k, v in sorted(nam.items())},
            "ti_le_thang_pct": round(100 * thang / len(deals), 1) if deals else None, "so_deal": len(deals)}


def ly_do_truot(chay: list[dict]) -> str | None:
    """None = có lần chạy đạt. Lần chạy có 'trang_thai_so' (từ sổ) chỉ tính đạt khi sổ ghi DAT (sổ đã loại IS/lạc quan
    theo kiểm toán); lần chạy của thợ (không có trường này) tính theo số."""
    hop = [c for c in chay if c.get("cagr_pct") is not None and c.get("dd_pct") is not None
           and "lac_quan" not in str(c.get("bien_the")) and c.get("trang_thai_so", "DAT") in ("DAT", "KHONG_DAT", "UNG_VIEN")]
    if not hop:
        return "CHƯA ĐO ĐƯỢC"
    if any(c["dd_pct"] < DD_MAX and c["cagr_pct"] > CAGR_MIN and c.get("trang_thai_so", "DAT") == "DAT" for c in hop):
        return None
    if any(c["dd_pct"] < DD_MAX and c["cagr_pct"] > CAGR_MIN for c in hop):
        return "số đạt nhưng sổ xếp UNG_VIEN/KHONG_DAT theo kiểm toán (IS / chưa giải mã điểm vào)"
    if all(c["cagr_pct"] <= 0 for c in hop):
        return "lỗ ở mọi mức lot (không có lợi thế sau phí)"
    if all(c["dd_pct"] >= DD_MAX for c in hop):
        return "DD >= 80 % ở mọi mức lot (rủi ro đuôi / cháy)"
    return "lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)"


def manh_tot(t: dict) -> list[str]:
    """Các điểm tốt có thể tái dùng dù hệ trượt."""
    out = []
    chay = [c for c in t["chay"] if c.get("cagr_pct") is not None]
    if any((c.get("pf") or 0) >= 1.3 for c in chay):
        out.append("PF >= 1,3 ở ít nhất một biến thể")
    if any((c.get("dd_pct") or 99) < 15 and (c.get("cagr_pct") or 0) > 0 for c in chay):
        out.append("DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot")
    nam = t.get("lai_theo_nam") or {}
    if len(nam) >= 3 and sum(v > 0 for v in nam.values()) / len(nam) >= 0.7:
        out.append("có lãi %d/%d năm" % (sum(v > 0 for v in nam.values()), len(nam)))
    tot = sorted({(c.get("ma"), c.get("tf")) for c in chay if (c.get("cagr_pct") or 0) > 0})
    if tot:
        out.append("chạy có lãi trên: " + ", ".join("%s %s" % x for x in tot[:6]))
    if (t.get("ti_le_thang_pct") or 0) >= 65:
        out.append("tỉ lệ thắng cao (%.0f %%) — điểm vào/TP nhỏ đáng giữ" % t["ti_le_thang_pct"])
    return out


def kieu_tu_spec(ts: dict) -> str:
    if not ts:
        return "CHƯA ĐO ĐƯỢC"
    p = []
    if ts.get("InpFileCsv"):
        p.append("vào theo CSV lệnh của nguồn")
    nhoi = {0: "không nhồi", 1: "DCA ngược (nhồi khi lỗ)", 2: "nhồi thuận"}.get(int(so(ts.get("InpNhoi")) or 0))
    if "InpNhoi" in ts:
        p.append(nhoi)
    if so(ts.get("InpMaxTang")):
        p.append("tối đa %d tầng, hệ số lot %s" % (int(so(ts["InpMaxTang"])), ts.get("InpHeSoLot", "?")))
    if so(ts.get("InpTPPct")) or so(ts.get("InpTPATR")):
        p.append("TP %s%s" % (ts.get("InpTPPct") or ts.get("InpTPATR"), " % giá" if so(ts.get("InpTPPct")) else " ATR"))
    if so(ts.get("InpHedgeKhiLoPct")):
        p.append("hedge khi lỗ %s %%" % ts["InpHedgeKhiLoPct"])
    if so(ts.get("InpCatLoPct")):
        p.append("cắt lỗ %s %%" % ts["InpCatLoPct"])
    for k in ("BuocPip", "TPPip"):
        if k in ts:
            p.append("%s=%s" % (k, ts[k]))
    return "; ".join(x for x in p if x) or "tham số: " + ", ".join(sorted(ts)[:8])


# ---------------- ghi ----------------
def chi_mo_phong(t: dict) -> bool:
    d = [c for c in t["chay"] if (c.get("cagr_pct") or 0) > CAGR_MIN and (c.get("dd_pct") or 100) < DD_MAX]
    return bool(d) and all("mo_phong" in str(c.get("nguon_do")) for c in d)


def trang_thai(t: dict) -> str:
    if t["ly_do_truot"] is not None:
        return "TRƯỢT — " + t["ly_do_truot"]
    return "ĐẠT MÔ PHỎNG (chưa MT5)" if chi_mo_phong(t) else "ĐẠT (theo sổ kết quả; xem reports/kiem_toan_he_dat.md)"


def ghi_the(t: dict) -> list[Path]:
    THU.mkdir(parents=True, exist_ok=True)
    t["manh_tot"] = manh_tot(t)
    t["ly_do_truot"] = ly_do_truot(t["chay"]) if t["chay"] else "CHƯA ĐO ĐƯỢC"
    j = THU / (t["id"] + ".json"); j.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
    f = lambda x, d="%.2f": "CHƯA ĐO ĐƯỢC" if x is None else (d % x).replace(".", ",")
    L = ["# Đặc điểm hệ `%s`" % t["id"], "", "- Nguồn: %s" % t.get("nguon", "CHƯA ĐO ĐƯỢC"), "- Kiểu vào / quản lý lệnh: %s" % t.get("kieu", "CHƯA ĐO ĐƯỢC"),
         "- Trạng thái: **%s**" % trang_thai(t),
         "- Số lần chạy hợp lệ: %d (bị thay thế do lỗi lot CSV: %d)" % (len(t["chay"]), t.get("bi_thay_the", 0)),
         "- Tỉ lệ thắng: %s %%" % f(t.get("ti_le_thang_pct"), "%.1f"),
         "- Năm có lãi: %s" % (", ".join("%s (%+.0f)" % kv for kv in (t.get("lai_theo_nam") or {}).items()) or "CHƯA ĐO ĐƯỢC"),
         "- Thời gian giữ lệnh TB: %s" % (t.get("giu_lenh") or "CHƯA ĐO ĐƯỢC"), "", "## Mảnh tốt dùng lại được", ""]
    L += ["- " + x for x in t["manh_tot"]] or ["- (chưa thấy)"]
    L += ["", "## Các lần chạy", "", "| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |", "|---|---|---|---|---|---|---|---|---|"]
    for c in sorted(t["chay"], key=lambda c: -(c.get("cagr_pct") or -1e9))[:40]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (str(c.get("bien_the", ""))[:50], c.get("ma"), c.get("tf"), c.get("nguon_do"),
                 c.get("k", 1), f(c.get("cagr_pct")), f(c.get("dd_pct")), f(c.get("pf")), c.get("lenh") or "CHƯA ĐO ĐƯỢC"))
    m = THU / (t["id"] + ".md"); m.write_text("\n".join(L) + "\n", encoding="utf-8")
    return [j, m]


def lap_muc_luc() -> Path:
    ds = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(THU.glob("*.json"))]
    co = [t for t in ds if t.get("manh_tot")]
    L = ["# Đặc điểm tốt — mục lục mảnh để ghép (tự sinh bởi `nhan/dac_diem_he.py`)", "",
         "Mỗi hệ đã test (kể cả trượt) có thẻ ở `TRI_NHO/dac_diem_he/<id>.md`. Bảng dưới: hệ có ít nhất một mảnh tốt.", "",
         "- Tổng thẻ: **%d**, có mảnh tốt: **%d**, đạt tiêu chí: **%d**" % (len(ds), len(co), sum(t.get("ly_do_truot") is None for t in ds)), "",
         "| Hệ | Trạng thái | Kiểu | Mảnh tốt |", "|---|---|---|---|"]
    for t in sorted(co, key=lambda t: (t.get("ly_do_truot") is not None, -len(t["manh_tot"]))):
        L.append("| [%s](dac_diem_he/%s.md) | %s | %s | %s |" % (t["id"], t["id"], trang_thai(t).split(" (")[0].split(" —")[0],
                 str(t.get("kieu", ""))[:70].replace("|", "/"), "; ".join(t["manh_tot"])[:220].replace("|", "/")))
    MUC_LUC.write_text("\n".join(L) + "\n", encoding="utf-8")
    return MUC_LUC


def _gop(cu: dict, moi: dict) -> dict:
    """Thẻ đã có -> thêm lần chạy mới (không trùng biến thể+k), giữ trường cũ nếu mới thiếu."""
    khoa = {(c.get("bien_the"), c.get("k"), c.get("ma"), c.get("tf")) for c in cu.get("chay", [])}
    cu["chay"] = cu.get("chay", []) + [c for c in moi["chay"] if (c.get("bien_the"), c.get("k"), c.get("ma"), c.get("tf")) not in khoa]
    for k, v in moi.items():
        if k != "chay" and v not in (None, "", {}, "CHƯA ĐO ĐƯỢC"):
            cu[k] = v
    return cu


def tu_ket_qua_tho(spec: dict, kq: dict) -> list[Path]:
    """Gọi từ thợ MT5 sau mỗi việc mt5_backtest. Trả đường dẫn đã ghi (để commit cùng kết quả)."""
    hid = ma_goc(spec.get("nguon") or spec["id"]) if spec.get("che_do") == "ong_dan_csv" else ma_goc(spec["id"])
    chay = [{"bien_the": spec["id"], "ma": spec.get("ma"), "tf": spec.get("tf"), "nguon_do": "mt5_tho_%s" % spec.get("may", ""),
             "k": c.get("k"), "cagr_pct": c.get("cagr_pct"), "dd_pct": c.get("dd_pct"), "pf": c.get("pf"), "lenh": c.get("lenh")}
            for c in kq.get("chay", []) if not c.get("loi")]
    nam: dict = {}; tl = None
    for c in kq.get("chay", []):
        if c.get("k") == 1.0 and c.get("lai_theo_nam"):
            nam, tl = c["lai_theo_nam"], c.get("ti_le_thang_pct")
    moi = {"id": hid, "nguon": spec.get("nguon") or spec.get("url_ma_nguon") or spec["id"], "kieu": kieu_tu_spec(spec.get("ts") or {}),
           "chay": chay, "lai_theo_nam": nam, "ti_le_thang_pct": tl, "giai_doan": "%s–%s" % (spec.get("tu"), spec.get("den"))}
    p = THU / (hid + ".json")
    t = _gop(json.loads(p.read_text(encoding="utf-8")), moi) if p.exists() else moi
    return ghi_the(t) + [lap_muc_luc()]


# ---------------- điền lại ----------------
def _spec_ong_dan() -> dict:
    out = {}
    for f in list((GOC / "reports").rglob("hang_cho*.jsonl")):
        for l in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            if '"ts"' in l:
                try:
                    v = json.loads(l)
                except ValueError:
                    continue
                out.setdefault(ma_goc(v.get("ten", "")), v.get("ts") or {})
    return out


def dien_lai() -> int:
    nhom: dict = defaultdict(lambda: {"chay": [], "bi_thay_the": 0, "nguon": set()})
    for r in csv.DictReader(SO.open(encoding="utf-8")):
        if r["nguon"] == "CONG_KHAI":
            continue
        g = nhom[ma_goc(r["he"])]
        if r["trang_thai"] == "BI_THAY_THE":
            g["bi_thay_the"] += 1; continue
        g["nguon"].add(r["nguon"])
        g["chay"].append({"bien_the": r["he"][:80], "ma": r["symbol"], "tf": r["timeframe"], "nguon_do": r["nguon"], "k": 1.0,
                          "cagr_pct": so(r["cagr_pct"]), "dd_pct": so(r["dd_pct"]), "pf": None, "lenh": r["so_lenh"] or None,
                          "trang_thai_so": r["trang_thai"],
                          "k_nang_lot": r.get("k_nang_lot")})
    ts = _spec_ong_dan()
    sys_path = str(GOC / "mt5tools")
    import sys
    sys.path.insert(0, sys_path)
    try:
        import chay_lai_tren_san as CLS
    except Exception:
        CLS = None
    htm = defaultdict(list)
    for f in HTM.glob("*.htm"):
        htm[ma_goc(f.stem)].append(f)
    n = 0
    for hid, g in nhom.items():
        t = {"id": hid, "nguon": ", ".join(sorted(g["nguon"])) or "CHƯA ĐO ĐƯỢC", "kieu": kieu_tu_spec(ts.get(hid, {})),
             "chay": g["chay"], "bi_thay_the": g["bi_thay_the"], "lai_theo_nam": {}, "ti_le_thang_pct": None}
        if CLS and htm.get(hid):
            f = max(htm[hid], key=lambda p: p.stat().st_size)
            try:
                tx = f.read_bytes().decode("utf-16", errors="ignore")
                t.update(deals_theo_nam(CLS.doc_deals(tx)))
                pf = re.search(r"Profit Factor:</td>\s*<td[^>]*><b>([\d.]+)", tx)
                if pf and t["chay"]:
                    t["pf_bao_cao"] = float(pf.group(1))
                    for c in t["chay"]:
                        c["pf"] = c["pf"] or (t["pf_bao_cao"] if "real_tick" in str(c["nguon_do"]) or "tester" in str(c["nguon_do"]) else None)
                t["bao_cao_htm"] = str(f.relative_to(GOC))
            except OSError:
                pass
        if not t["chay"] and not t["bi_thay_the"]:
            continue
        ghi_the(t); n += 1
    lap_muc_luc()
    return n


if __name__ == "__main__":
    print("the", dien_lai())
