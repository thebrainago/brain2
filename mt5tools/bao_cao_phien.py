# -*- coding: utf-8 -*-
"""bao_cao_phien.py - BAO CAO PHIEN MAY NHA (20/10/2026). BACKTEST, khong phai tien that.

    python mt5tools/bao_cao_phien.py [--day] [--ket_thuc] [--ngay YYYYMMDD]

Moi ~60 phut trong phien (chay_toi_nay.ps1 goi): ghi
  - reports/phien/PHIEN_<YYYYMMDD>.md: he dat chuan cuoi MT5, truot, chua do; viec xong / con cho; thoi gian TB moi slot;
    the Seeker moi; dich_llm (dem + nhom ly do hong); o dia / RAM; loi.
  - reports/UNG_VIEN.md: cong don, MOI HE MOT DONG tu bao cao MT5 real tick that (reports/ong_dan/ket_qua_mt5/od_*.htm).
--day: git add DUNG hai loai tep tren (khong bao gio add khoa / data), commit, pull --rebase, push; loi mang -> bo qua,
       lan sau day lai (khong lam hong phien).
--ket_thuc: cuoi phien: `ong_dan.py doc_mt5` -> bao cao -> don cache tester slot ranh (quan_ly_slot bac 0) -> day.
Chi so DO THAT; khong co thi ghi CHƯA ĐO ĐƯỢC. So Python la MÔ PHỎNG.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import time
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(Path(__file__).resolve().parent))

KQ = GOC / "reports" / "ong_dan" / "ket_qua_mt5"
HANG = GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl"
SO_CAI = GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl"
PHIEN = GOC / "reports" / "phien"
UNG_VIEN = GOC / "reports" / "UNG_VIEN.md"
CDD = "CHƯA ĐO ĐƯỢC"


def _hang() -> dict:
    if not HANG.exists():
        return {}
    ra = {}
    for x in HANG.read_text(encoding="utf-8").splitlines():
        try:
            v = json.loads(x)
            ra[v["ten"]] = v
        except (ValueError, KeyError):
            continue
    return ra


def _so_cai() -> list[dict]:
    if not SO_CAI.exists():
        return []
    ra = []
    for x in SO_CAI.read_text(encoding="utf-8").splitlines():
        try:
            ra.append(json.loads(x))
        except ValueError:
            continue
    return ra


def kiem_toan_htm(f: Path) -> dict:
    """20/10/2026 kiem toan: doc them tu .htm - DD von (equity) % LON NHAT trong 'Maximal' va 'Relative', stop-out
    (comment 'so ...'), lenh dong cuong buc cuoi ky ('end of test'), tong hoa hong / swap trong bang deal, margin level thap nhat."""
    import html as H
    t = f.read_bytes().decode("utf-16", errors="ignore")
    if "<td" not in t:
        t = f.read_bytes().decode("utf-8", errors="ignore")
    o = [H.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S)]

    def g(k):
        try:
            return o[o.index(k) + 1]
        except ValueError:
            return None

    def so(x):
        try:
            return float(str(x).replace(" ", "").replace("\xa0", "").replace("%", "").split("(")[0])
        except Exception:
            return None
    pct = []
    m = re.search(r"\(([\d.]+)%\)", str(g("Equity Drawdown Maximal:") or ""))
    if m:
        pct.append(float(m.group(1)))
    x = so(g("Equity Drawdown Relative:"))
    if x is not None:
        pct.append(x)
    hh = sw = 0.0
    so_out = cuoi = 0
    hang = re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
    R = [[H.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)] for r in hang]
    i0 = next((k for k, r in enumerate(R) if r[:3] == ["Time", "Deal", "Symbol"]), None)
    if i0 is not None:
        for r in R[i0 + 1:]:
            if len(r) < 13:
                continue
            hh += so(r[8]) or 0.0
            sw += so(r[9]) or 0.0
            c = r[12].lower()
            so_out += bool(re.match(r"^so\b", c) or "stop out" in c)
            cuoi += c == "end of test" and r[4] == "out"
    return {"dd_von_pct": max(pct) if pct else None, "stop_out": so_out, "dong_cuoi_ky": cuoi, "hoa_hong": round(hh, 2),
            "swap": round(sw, 2), "margin_min_pct": so(g("Margin Level:")), "lo_gop": so(g("Gross Loss:"))}


LENH_TOI_THIEU = 30


def ung_vien(hang: dict | None = None, thu_muc: Path = KQ, ti_so: dict | None = None) -> list[dict]:
    """Moi bao cao real tick od_*.htm (goc ket_qua_mt5, KHONG gom tang1/) -> mot dong do that + phan xu chuan cuoi.
    20/10/2026 (kiem toan): chuan cuoi dung lai KEP %/nam (chat hon lai don) tren KY bao cao, DD von = max(Maximal %,
    Relative %), stop-out -> TRUOT, symbol phai dung *micro cua viec, tick < 90 % -> CHUA DO DUOC; trung (the, symbol, TF)
    hoac trung ket qua -> dem MOT lan (dong kem 'TRÙNG'). ti_so: ten -> Python/MT5 (doi chieu), de gan nhan."""
    from nhan import ong_dan as OD
    from nhan import nguong as NG
    hang = _hang() if hang is None else hang
    cfg = OD.cau_hinh()
    luc = {}                                  # ten -> ngay do (so cai, lan xong cuoi); khong co -> mtime tep
    for r in _so_cai():
        if r.get("ten") and not r.get("loi") and r.get("tang") != 1:
            luc[r["ten"]] = max(luc.get(r["ten"], ""), str(r.get("luc", ""))[:10])
    ra = []
    for f in sorted(Path(thu_muc).glob("od_*.htm")):
        v = hang.get(f.stem) or {}
        r = OD.doc_htm(f)
        kt = kiem_toan_htm(f)
        von = float(r.get("von_dau") or v.get("von") or cfg.get("von", 1000.0))
        sym = r.get("symbol") or ""
        dung_sym = OD.ky_hieu_dung(sym, v.get("ma")) and (not v.get("ma") or str(sym).lower().endswith("micro"))
        nam = OD._nam_bc(r, v, cfg)
        ph = OD._cot_loi_mt5(r.get("net"), r.get("dd"), von, nam)
        dd = kt["dd_von_pct"] if kt["dd_von_pct"] is not None else ph.get("sut_giam_pct")
        kep = ph.get("lai_kep_pct_nam")
        ly, nhan = [], []
        if not dung_sym:
            kl = "CHƯA ĐO ĐƯỢC"
            ly.append("SAI SYMBOL %s (việc %s)" % (sym, v.get("ma")))
        elif r.get("net") is None or dd is None or kep is None:
            kl = "CHƯA ĐO ĐƯỢC"
            ly.append("thiếu số trong .htm")
        elif _cl(r.get("chat_luong")) < 90 and not kt["stop_out"]:
            kl = "CHƯA ĐO ĐƯỢC"
            ly.append("chất lượng tick %s < 90%%" % r.get("chat_luong"))
        else:
            ok = NG.dat(kep, dd, "cuoi")
            kl = "ĐẠT" if ok.get("dat") and not kt["stop_out"] else "TRƯỢT"   # stop-out: TRUOT ca khi tick thap
            if kt["stop_out"]:
                ly.append("STOP-OUT %d lần" % kt["stop_out"])
            ly += ok.get("ly_do") or []
        if (r.get("lenh") or 0) < LENH_TOI_THIEU:
            nhan.append("ít lệnh (%d < %d)" % (r.get("lenh") or 0, LENH_TOI_THIEU))
        if nam < 2.0:
            nhan.append("lịch sử ngắn (%.1f năm)" % nam)
        if kt["dong_cuoi_ky"] >= 3:
            nhan.append("%d lệnh còn mở bị đóng cuối kỳ" % kt["dong_cuoi_ky"])
        if kt["lo_gop"] == 0 and (r.get("lenh") or 0) > 0:
            nhan.append("không đóng lệnh lỗ nào (PF vô hạn; DD vốn %.0f%%)" % (dd or 0))
        ts = (ti_so or {}).get(f.stem)
        if ts is not None and not (0.8 <= ts <= 1.25):
            nhan.append("Python/MT5 %.2f ngoài 0,8–1,25" % ts)
        ra.append({"ten": f.stem, "the_id": v.get("the_id", ""), "nguon": (v.get("the_id") or f.stem).split("_")[0],
                   "ma": sym or v.get("ma"), "tf": v.get("tf", ""), "net": r.get("net"),
                   "lai_pct_nam": ph.get("lai_pct_nam"), "lai_kep_pct_nam": kep, "so_nam": round(nam, 2),
                   "dd_pct": dd, "pf": r.get("pf"), "lenh": r.get("lenh"), "stop_out": kt["stop_out"],
                   "hoa_hong": kt["hoa_hong"], "swap": kt["swap"], "ti_so_py_mt5": ts,
                   "chat_luong": r.get("chat_luong") or CDD, "ky": "%s–%s" % (r.get("tu_bc", "?"), r.get("den_bc", "?")),
                   "phien": luc.get(f.stem) or dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                   "ket_luan": kl, "ly_do": "; ".join(ly), "nhan": nhan, "trung": None})
    # trung: cung (the, symbol, TF) hoac cung (symbol, net, so lenh) -> giu dong %/nam kep cao nhat
    nhom = {}
    for x in sorted(ra, key=lambda x: -(x["lai_kep_pct_nam"] if x["lai_kep_pct_nam"] is not None else -1e9)):
        for k in ((x["the_id"] or x["ten"], x["ma"], x["tf"]), ("kq", x["ma"], x["net"], x["lenh"])):
            if k in nhom and x["trung"] is None:
                x["trung"] = nhom[k]
            nhom.setdefault(k, x["ten"])
    return ra


def _cl(x) -> float:
    m = re.search(r"(\d+)%", str(x or ""))
    return float(m.group(1)) if m else 100.0


def _o(x, d=2):
    return CDD if x is None else (("%." + str(d) + "f") % x if isinstance(x, float) else str(x))


def ghi_ung_vien(ds: list[dict], tep: Path = UNG_VIEN) -> str:
    dem = [r for r in ds if not r["trung"]]
    d = ["# Ứng viên MT5 (cộng dồn, tự sinh bởi `mt5tools/bao_cao_phien.py`)", "",
         "Mỗi hệ một dòng, số **đo thật** từ báo cáo MT5 real tick (`reports/ong_dan/ket_qua_mt5/od_*.htm`), tài khoản XM micro "
         "1:500, vốn trong báo cáo (1.000 USD). **Chuẩn cuối (kiểm toán 20/10/2026):**",
         "",
         "- **%/năm:** lãi **kép** (chặt hơn lãi đơn) trên **kỳ trong báo cáo**, tính bằng (1 + lãi ròng/vốn)^(1/số năm) − 1. Đạt khi ≥ 10 %.",
         "- **Sụt giảm:** lấy theo **vốn (equity)**, là số lớn hơn giữa *Equity Drawdown Maximal %* và *Relative %*. Đạt khi ≤ 80 %.",
         "- **Loại:** có stop-out thì TRƯỢT. Sai symbol (không phải `*micro` của việc) hoặc tick < 90 % thì CHƯA ĐO ĐƯỢC.",
         "- **Phí:** spread và swap đã nằm trong báo cáo real tick. Hoa hồng trong báo cáo XM micro bằng 0, hoa hồng thật **CHƯA ĐO ĐƯỢC**.",
         "- **Trùng:** cùng thẻ + symbol + TF, hoặc cùng kết quả, chỉ đếm một lần.",
         "",
         "Cập nhật: %s (giờ máy chạy). Đếm (không trùng): ĐẠT %d, TRƯỢT %d, CHƯA ĐO ĐƯỢC %d; trùng bỏ %d." % (
             dt.datetime.now().strftime("%d/%m/%Y %H:%M"), sum(r["ket_luan"] == "ĐẠT" for r in dem),
             sum(r["ket_luan"] == "TRƯỢT" for r in dem), sum(r["ket_luan"] == "CHƯA ĐO ĐƯỢC" for r in dem), len(ds) - len(dem)),
         "", "## Bảng xếp hạng (ĐẠT, không trùng, theo %/năm kép)", "",
         "| # | id | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | Lệnh | Số năm | Py/MT5 | Điểm yếu |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    top = sorted([r for r in dem if r["ket_luan"] == "ĐẠT"], key=lambda r: -r["lai_kep_pct_nam"])
    for i, r in enumerate(top, 1):
        d.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, r["ten"], r["ma"], r["tf"], _o(r["net"]), _o(r["lai_kep_pct_nam"]), _o(r["lai_pct_nam"]), _o(r["dd_pct"]),
            _o(r["lenh"], 0), _o(r["so_nam"]), _o(r["ti_so_py_mt5"]) if r["ti_so_py_mt5"] is not None else CDD,
            "; ".join(r["nhan"]) or "—"))
    if not top:
        d.append("| – | chưa có hệ ĐẠT | | | | | | | | | | |")
    d += ["", "## Tất cả", "",
          "| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | PF | Lệnh | Stop-out | Swap | Kỳ | Chất lượng tick | Lí do / nhãn |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    thu_tu = {"ĐẠT": 0, "TRƯỢT": 1, "CHƯA ĐO ĐƯỢC": 2}
    for r in sorted(ds, key=lambda r: (bool(r["trung"]), thu_tu.get(r["ket_luan"], 3), -(r["lai_kep_pct_nam"] or -1e9))):
        gc = "; ".join(([r["ly_do"]] if r["ly_do"] else []) + r["nhan"] + (["TRÙNG với %s" % r["trung"]] if r["trung"] else []))
        d.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["ket_luan"] + (" (trùng)" if r["trung"] else ""), r["ten"], r["the_id"] or r["nguon"], r["ma"], r["tf"],
            _o(r["net"]), _o(r["lai_kep_pct_nam"]), _o(r["lai_pct_nam"]), _o(r["dd_pct"]), _o(r["pf"]), _o(r["lenh"], 0),
            r["stop_out"], _o(r["swap"]), r["ky"], r["chat_luong"], gc.replace("|", "/")[:160]))
    if not ds:
        d.append("| %s | – | – | – | – | – | – | – | – | – | – | – | – | – | – | chưa có báo cáo MT5 real tick |" % CDD)
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(d) + "\n", encoding="utf-8")
    return str(tep)


def ti_so_doi_chieu(hang: dict | None = None) -> dict:
    """ten -> lai Python / lai MT5 (MO PHONG / do that) cho viec KIEM_CSV co lenh MT5; loi -> bo qua."""
    from nhan import ong_dan as OD
    hang = _hang() if hang is None else hang
    ra = {}
    for ten, v in hang.items():
        if v.get("pha") != "KIEM_CSV" or not v.get("csv_vao"):
            continue
        try:
            r = OD.doi_chieu_viec(v, KQ)
            if r.get("lai_mt5") and r.get("lai_python") is not None and r["lai_mt5"] > 0:
                ra[ten] = round(r["lai_python"] / r["lai_mt5"], 2)
        except Exception:  # noqa: BLE001
            continue
    return ra


def thong_ke_viec(so_cai: list[dict], ngay: str, hang: dict) -> dict:
    """Viec trong phien `ngay` (YYYY-MM-DD theo `luc`): xong / loi / tang 1 qua-truot / TB giay moi slot; con cho."""
    import sinh_viec as SV
    hom = [r for r in so_cai if str(r.get("luc", "")).startswith(ngay)]
    xong = [r for r in hom if not r.get("loi")]
    loi = Counter(str(r["loi"]).split(":")[0] for r in hom if r.get("loi"))
    t1 = [r for r in xong if r.get("tang") == 1]
    theo_slot = defaultdict(list)
    for r in hom:
        if r.get("giay"):
            theo_slot[r.get("slot") or "không ghi slot (bản cũ)"].append(int(r["giay"]))
    da = {SV.khoa(r) for r in so_cai if not r.get("loi")}
    cho = sum(1 for v in hang.values() if v.get("ea") == "XL" and v.get("tf") in SV.TF and SV.khoa(v) not in da)
    return {"tong": len(hom), "xong": len(xong), "loi": dict(loi), "tang1": len(t1),
            "tang1_qua": sum(1 for r in t1 if r.get("tang1_qua")), "tang1_truot": sum(1 for r in t1 if r.get("tang1_qua") is False),
            "tang2": len([r for r in xong if r.get("tang") != 1 and r.get("nguon") == "ong_dan"]),
            "slot": {k: (len(v), round(sum(v) / len(v))) for k, v in theo_slot.items()}, "con_cho_xl": cho}


def thong_ke_db(ngay: str) -> dict:
    """The Seeker moi trong ngay + dich_llm (tu CSDL ong dan, chi co tren may nha)."""
    from nhan import ong_dan as OD
    if not OD.TT.exists():
        return {"co_db": False}
    cn = OD._db()
    try:
        moi = cn.execute("SELECT COUNT(*) FROM nhat_ky WHERE buoc='nhan' AND luc LIKE ?", (ngay + "%",)).fetchone()[0]
        dl = Counter(r[0] for r in cn.execute("SELECT ghi FROM nhat_ky WHERE buoc='dich_llm' AND luc LIKE ?", (ngay + "%",)))
        dl_dem = Counter(x.split(" ")[0] for x in dl.elements())
        from nhan import dich_llm as DL
        tk = DL.thong_ke_hong(cn)
        return {"co_db": True, "seeker_moi": moi, "dich_hom_nay": dict(dl_dem), "dich_cong_don": tk}
    finally:
        cn.close()


def may() -> dict:
    o = {}
    for d in ("C:\\", "D:\\", "E:\\") if os.name == "nt" else ("/",):
        try:
            u = shutil.disk_usage(d)
            o[d] = round(u.free / 1024 ** 3, 1)
        except Exception:
            pass
    try:
        import psutil
        vm = psutil.virtual_memory()
        ram = (round(vm.available / 1024 ** 3, 1), round(vm.total / 1024 ** 3, 1))
    except Exception:
        ram = None
    return {"o_trong_gb": o, "ram": ram}


def loi_log(n: int = 15) -> list[str]:
    p = Path(os.environ.get("BRAIN_LOG_LIEN_TUC") or r"D:\mt5_lien_tuc\chay.log")
    if not p.exists():
        return []
    try:
        dong = p.read_text(encoding="utf-8", errors="ignore").splitlines()[-3000:]
    except Exception:
        return []
    return [x for x in dong if re.search(r"loi|HONG|KHONG PHONG|QUA GIO|BO SLOT|CHO RAM|BO QUA SLOT", x)][-n:]


def model_llm_md() -> list[str]:
    """Model dich_llm dang khoa + bang A/B gan nhat (reports/ong_dan/CHON_MODEL_LLM.json, do tren may nha)."""
    d = ["", "## Model LLM dịch", ""]
    try:
        cfg = json.loads((GOC / "config" / "llm_dich.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {}
    d.append("- Model cố định: %s (dự phòng chỉ khi 5xx: %s; chọn lúc %s)" % (
        cfg.get("model") or "CHƯA CHỌN (đang dùng config/qwen.json)", cfg.get("model_du_phong") or "không", cfg.get("chon_luc") or CDD))
    try:
        r = json.loads((GOC / "reports" / "ong_dan" / "CHON_MODEL_LLM.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return d + ["- A/B: %s" % CDD]
    if not r.get("ab"):
        return d + ["- A/B: %s (%s)" % (CDD, r.get("ly_do", ""))]
    d += ["", "| Model | ĐẠT | JSON hợp lệ | Giây/mẫu | Chạm trần token |", "|---|---|---|---|---|"]
    d += ["| %s | %d/%d | %d | %s | %d |" % (x["model"], x["dat"], x["so_mau"], x["ok_json"], x["giay_tb"], x["cham_tran"]) for x in r["ab"]]
    return d


def su_dung_md(phut: int = 60) -> list[str]:
    """Mức sử dụng giờ qua từ data/dieu_phoi/su_dung.jsonl (bộ điều phối ghi mỗi chu kỳ) + quyết định gần nhất."""
    try:
        import importlib.util
        sp = importlib.util.spec_from_file_location("dieu_phoi_may_nha", GOC / "may_nha_toi_nay" / "dieu_phoi_may_nha.py")
        DP = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(DP)        # goc repo co dieu_phoi.py khac (qwen) -> nap theo duong dan
    except Exception as e:  # noqa: BLE001
        return ["", "## Sử dụng tài nguyên %d phút qua" % phut, "", "- %s (không nạp được dieu_phoi: %s)" % (CDD, e)]
    t = DP.tom_tat_su_dung(time.time() - phut * 60)
    d = ["", "## Sử dụng tài nguyên %d phút qua (bộ điều phối, đo thật)" % phut, ""]
    if not t:
        return d + ["- %s (chưa có mẫu trong data/dieu_phoi/su_dung.jsonl — dieu_phoi_may_nha.py chưa chạy)" % CDD]
    v = lambda x, dv="": CDD if x is None else "%s%s" % (x, dv)  # noqa: E731
    d += ["| Chỉ số | Giá trị |", "|---|---|",
          "| Số mẫu | %d |" % t["so_mau"], "| CPU trung bình | %s |" % v(t["cpu_pct"], " %"),
          "| RAM trống trung bình | %s / %s GB |" % (v(t["ram_trong_gb"]), v(t["ram_tong_gb"])),
          "| Slot MT5 bận | %s |" % v(t["slot_ban_pct"], " %"),
          "| dich_llm chạy | %s |" % v(t["dich_llm_pct"], " % thời gian"),
          "| Seeker chạy | %s |" % v(t["seeker_pct"], " % thời gian"),
          "| Ổ trống cuối (GB) | %s |" % (", ".join("%s %s" % kv for kv in t["o_trong_gb_cuoi"].items()) or CDD),
          "| Thư mục tải về Seeker: ổ trống cuối | %s |" % v(t["tai_ve_trong_gb_cuoi"], " GB")]
    try:
        ds = DP.NHAT_KY.read_text(encoding="utf-8").splitlines()[-8:]
        d += ["", "Quyết định gần nhất:", ""] + ["- %s [%s] %s — %s" % ((lambda x: (x["luc"][11:16], x["viec"], x["quyet"], x["ly_do"]))(json.loads(z))) for z in ds]
    except (OSError, ValueError, KeyError):
        pass
    return d


def ghi_phien(ngay8: str, ds_uv: list[dict]) -> Path:
    ngay = "%s-%s-%s" % (ngay8[:4], ngay8[4:6], ngay8[6:])
    hang = _hang()
    sc = _so_cai()
    tv = thong_ke_viec(sc, ngay, hang)
    try:
        db = thong_ke_db(ngay)
    except Exception as e:  # noqa: BLE001
        db = {"co_db": False, "loi": str(e)[:200]}
    m = may()
    hom = [r for r in ds_uv if r["phien"] == ngay and not r.get("trung")]
    d = ["# Phiên máy nhà %s/%s/%s" % (ngay8[6:], ngay8[4:6], ngay8[:4]), "",
         "Tự sinh bởi `mt5tools/bao_cao_phien.py` lúc %s (giờ máy chạy). Số MT5 là đo thật (real tick); số Python là MÔ PHỎNG; "
         "thiếu số ghi %s." % (dt.datetime.now().strftime("%H:%M"), CDD), "",
         "## Hệ đo trong phiên này (MT5 real tick)", ""]
    for nhan in ("ĐẠT", "TRƯỢT", "CHƯA ĐO ĐƯỢC"):
        nhom = [r for r in hom if r["ket_luan"] == nhan]
        d.append("- **%s**: %d%s" % (nhan, len(nhom), (" — " + ", ".join("%s (%s %s, %s %%/năm kép, DD vốn %s %%)" % (
            r["ten"], r["ma"], r["tf"], _o(r["lai_kep_pct_nam"]), _o(r["dd_pct"])) for r in nhom[:15])) if nhom else ""))
    d += ["", "Cộng dồn mọi phiên: xem `reports/UNG_VIEN.md` (%d hệ, ĐẠT %d)." % (
        len(ds_uv), sum(1 for r in ds_uv if r["ket_luan"] == "ĐẠT" and not r.get("trung"))), "",
        "## Hàng MT5", "",
        "| Chỉ số | Giá trị |", "|---|---|",
        "| Lượt chạy trong phiên (sổ cái) | %d |" % tv["tong"], "| Xong có báo cáo | %d |" % tv["xong"],
        "| Tầng 1 (OHLC M1): qua / trượt | %d / %d |" % (tv["tang1_qua"], tv["tang1_truot"]),
        "| Tầng 2 real tick (ống dẫn) | %d |" % tv["tang2"],
        "| Lỗi (CHƯA ĐO ĐƯỢC, sẽ thử lại) | %s |" % (", ".join("%s %d" % kv for kv in tv["loi"].items()) or "0"),
        "| Việc VAO_CSV/XL còn chờ (ước) | %d |" % tv["con_cho_xl"], "",
        "| Slot | Lượt | Thời gian TB (giây) |", "|---|---|---|"]
    for k, (n, tb) in sorted(tv["slot"].items()):
        d.append("| %s | %d | %d |" % (k, n, tb))
    if not tv["slot"]:
        d.append("| – | 0 | %s |" % CDD)
    d += ["", "## Seeker và dịch LLM", ""]
    if db.get("co_db"):
        d.append("- Thẻ Seeker mới nhận hôm nay: %d" % db["seeker_moi"])
        d.append("- Dịch LLM hôm nay (theo nhật ký): %s" % (", ".join("%s %d" % kv for kv in db["dich_hom_nay"].items()) or "chưa chạy"))
        tk = db["dich_cong_don"]
        d.append("- Cộng dồn trạng thái dịch: %s" % (", ".join("%s %d" % kv for kv in sorted(tk["trang_thai"].items())) or "chưa có"))
        if tk.get("nhom_ly_do"):
            d.append("- Lí do hỏng (cộng dồn): " + ", ".join("%s %d" % kv for kv in sorted(tk["nhom_ly_do"].items(), key=lambda z: -z[1])))
    else:
        d.append("- %s (không có CSDL ống dẫn trên máy này%s)" % (CDD, (": " + db["loi"]) if db.get("loi") else ""))
    d += model_llm_md()
    d += ["", "## Máy", "",
          "- Ổ trống (GB): %s" % (", ".join("%s %s" % kv for kv in m["o_trong_gb"].items()) or CDD),
          "- RAM trống / tổng (GB): %s" % ("%s / %s" % m["ram"] if m["ram"] else CDD)]
    d += su_dung_md()
    d += ["", "## Lỗi gần nhất (chay.log)", ""]
    ll = loi_log()
    d += ["    " + x for x in ll] if ll else ["- không có / không đọc được log"]
    PHIEN.mkdir(parents=True, exist_ok=True)
    tep = PHIEN / ("PHIEN_%s.md" % ngay8)
    tep.write_text("\n".join(d) + "\n", encoding="utf-8")
    return tep


def day_git(tep: list[Path], thong_diep: str, chay=subprocess.run) -> str:
    """Chi add DUNG cac tep bao cao (khong -A, khong data/). Loi mang / xung dot -> tra thong bao, khong nem loi."""
    g = lambda *x: chay(["git", "-C", str(GOC)] + list(x), capture_output=True, text=True, timeout=180)  # noqa: E731
    try:
        rel = [str(Path(t).resolve().relative_to(GOC)) for t in tep if Path(t).exists()]
        rel = [x for x in rel if x.replace("\\", "/").startswith(("reports/phien/", "reports/UNG_VIEN.md"))]
        if not rel:
            return "khong co tep"
        g("add", "--", *rel)
        r = g("diff", "--cached", "--quiet", "--", *rel)
        if r.returncode == 0:
            return "khong doi"
        r = g("commit", "-m", thong_diep, "--", *rel)
        if r.returncode != 0:
            return "commit loi: %s" % (r.stderr or r.stdout)[-200:]
        r = g("pull", "--rebase", "--autostash")
        if r.returncode != 0:
            g("rebase", "--abort")
            return "pull loi (se day lan sau): %s" % (r.stderr or "")[-200:]
        r = g("push")
        return "push rc=%s %s" % (r.returncode, (r.stderr or "")[-200:])
    except Exception as e:  # noqa: BLE001
        return "git loi (se day lan sau): %s" % str(e)[:200]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", action="store_true")
    ap.add_argument("--ket_thuc", action="store_true")
    ap.add_argument("--ngay", default=dt.datetime.now().strftime("%Y%m%d"))
    a = ap.parse_args(argv)
    if a.ket_thuc:
        r = subprocess.run([sys.executable, str(GOC / "ong_dan.py"), "doc_mt5"], cwd=str(GOC), capture_output=True,
                           text=True, timeout=1800)
        print("doc_mt5 rc=%s %s" % (r.returncode, (r.stdout or r.stderr)[-300:]))
    try:
        ts = ti_so_doi_chieu()
    except Exception:  # noqa: BLE001
        ts = {}
    ds = ung_vien(ti_so=ts)
    ghi_ung_vien(ds)
    tep = ghi_phien(a.ngay, ds)
    print("ghi %s, %s" % (tep, UNG_VIEN))
    if a.ket_thuc:
        try:
            import quan_ly_slot as QS
            n = 0
            dang = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower() if os.name == "nt" else ""
            if "terminal64.exe" not in dang and "metatester64.exe" not in dang:
                for s in QS.ds_slot():
                    if Path(s).exists():
                        n += QS.don_bac(s, 0)
                print("don cache tester cuoi phien: %.1f MB" % (n / 1024 ** 2))
            else:
                print("MT5 con chay - khong don cache cuoi phien")
        except Exception as e:  # noqa: BLE001
            print("don loi %s" % e)
    if a.day or a.ket_thuc:
        print(day_git([tep, UNG_VIEN], "Phiên máy nhà %s: báo cáo phiên + UNG_VIEN%s" % (a.ngay, " (cuối phiên)" if a.ket_thuc else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
