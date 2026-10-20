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


def ung_vien(hang: dict | None = None, thu_muc: Path = KQ) -> list[dict]:
    """Moi bao cao real tick od_*.htm (goc ket_qua_mt5, KHONG gom tang1/) -> mot dong do that + phan xu chuan cuoi."""
    from nhan import ong_dan as OD
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
        von = float(r.get("von_dau") or v.get("von") or cfg.get("von", 1000.0))
        dung_sym = OD.ky_hieu_dung(r.get("symbol"), v.get("ma"))
        if not dung_sym:
            ph = {"dat": False, "ly_do": ["SAI SYMBOL %s (việc %s) - %s" % (r.get("symbol"), v.get("ma"), CDD)]}
        else:
            ph = OD._cot_loi_mt5(r.get("net"), r.get("dd"), von, OD._nam_bc(r, v, cfg))
        m = re.search(r"\(([\d.]+)%\)", str(r.get("dd") or ""))
        ra.append({"ten": f.stem, "the_id": v.get("the_id", ""), "nguon": (v.get("the_id") or f.stem).split("_")[0],
                   "ma": r.get("symbol") or v.get("ma"), "tf": v.get("tf", ""), "net": r.get("net"),
                   "lai_pct_nam": ph.get("lai_pct_nam"), "lai_kep_pct_nam": ph.get("lai_kep_pct_nam"),
                   "dd_pct": float(m.group(1)) if m else None, "pf": r.get("pf"), "lenh": r.get("lenh"),
                   "chat_luong": r.get("chat_luong") or CDD, "ky": "%s–%s" % (r.get("tu_bc", "?"), r.get("den_bc", "?")),
                   "phien": luc.get(f.stem) or dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                   "ket_luan": "ĐẠT" if ph.get("dat") else ("CHƯA ĐO ĐƯỢC" if "CHUA_DO_DUOC" in " ".join(ph.get("ly_do", []))
                                                           or not dung_sym else "TRƯỢT"),
                   "ly_do": "; ".join(ph.get("ly_do", []) + (
                       ["chất lượng tick thấp (%s)" % r.get("chat_luong")] if _cl(r.get("chat_luong")) < 90 else []))})
    return ra


def _cl(x) -> float:
    m = re.search(r"(\d+)%", str(x or ""))
    return float(m.group(1)) if m else 100.0


def _o(x, d=2):
    return CDD if x is None else (("%." + str(d) + "f") % x if isinstance(x, float) else str(x))


def ghi_ung_vien(ds: list[dict], tep: Path = UNG_VIEN) -> str:
    d = ["# Ứng viên MT5 (cộng dồn, tự sinh bởi `mt5tools/bao_cao_phien.py`)", "",
         "Mỗi hệ một dòng, số **đo thật** từ báo cáo MT5 real tick (`reports/ong_dan/ket_qua_mt5/od_*.htm`), tài khoản XM micro "
         "1:500, vốn trong báo cáo. Chuẩn cuối của chủ dự án: sụt giảm ≤ 80 %, lãi ≥ 10 %/năm sau phí (lãi/năm = lãi ròng / vốn / "
         "số năm của **kỳ trong báo cáo**). Lãi kép ghi kèm để so với Python. Chạy sai symbol → CHƯA ĐO ĐƯỢC, phải chạy lại.",
         "", "Cập nhật: %s (giờ máy chạy)." % dt.datetime.now().strftime("%d/%m/%Y %H:%M"), "",
         "| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm | %/năm kép | Sụt giảm % | PF | Lệnh | Kỳ | Phiên đo | Chất lượng tick | Ghi chú |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    thu_tu = {"ĐẠT": 0, "TRƯỢT": 1, "CHƯA ĐO ĐƯỢC": 2}
    for r in sorted(ds, key=lambda r: (thu_tu.get(r["ket_luan"], 3), -(r["lai_pct_nam"] or -1e9))):
        d.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["ket_luan"], r["ten"], r["the_id"] or r["nguon"], r["ma"], r["tf"], _o(r["net"]), _o(r["lai_pct_nam"]),
            _o(r["lai_kep_pct_nam"]), _o(r["dd_pct"]), _o(r["pf"]), _o(r["lenh"], 0), r["ky"], r["phien"], r["chat_luong"],
            r["ly_do"].replace("|", "/")[:120]))
    if not ds:
        d.append("| %s | – | – | – | – | – | – | – | – | – | – | – | – | – | chưa có báo cáo MT5 real tick |" % CDD)
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(d) + "\n", encoding="utf-8")
    return str(tep)


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
    hom = [r for r in ds_uv if r["phien"] == ngay]
    d = ["# Phiên máy nhà %s/%s/%s" % (ngay8[6:], ngay8[4:6], ngay8[:4]), "",
         "Tự sinh bởi `mt5tools/bao_cao_phien.py` lúc %s (giờ máy chạy). Số MT5 là đo thật (real tick); số Python là MÔ PHỎNG; "
         "thiếu số ghi %s." % (dt.datetime.now().strftime("%H:%M"), CDD), "",
         "## Hệ đo trong phiên này (MT5 real tick)", ""]
    for nhan in ("ĐẠT", "TRƯỢT", "CHƯA ĐO ĐƯỢC"):
        nhom = [r for r in hom if r["ket_luan"] == nhan]
        d.append("- **%s**: %d%s" % (nhan, len(nhom), (" — " + ", ".join("%s (%s %s, %s %%/năm, DD %s %%)" % (
            r["ten"], r["ma"], r["tf"], _o(r["lai_pct_nam"]), _o(r["dd_pct"])) for r in nhom[:15])) if nhom else ""))
    d += ["", "Cộng dồn mọi phiên: xem `reports/UNG_VIEN.md` (%d hệ, ĐẠT %d)." % (
        len(ds_uv), sum(1 for r in ds_uv if r["ket_luan"] == "ĐẠT")), "",
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
    ds = ung_vien()
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
