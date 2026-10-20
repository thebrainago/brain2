# -*- coding: utf-8 -*-
"""Bo dieu phoi tai nguyen may nha (20/10/2026, Grok Bot).

Xoay vong 3 loai viec de may nha luon ban nhung khong nghen:
  * MT5 tester (mt5tools/chay_lien_tuc.py) - uu tien so 1 ve RAM / IO dia. Bo dieu phoi KHONG chay MT5; no ghi
    data/dieu_phoi/muc_mt5.json (so slot tang 1 / tang 2 cho phep) - quan_ly_slot.slot_toi_da() doc tep nay neu con moi.
  * dich_llm (ong_dan.py dich_llm) - cho mang/LLM, nhe CPU/RAM -> chay lien tuc song song MT5 khi con the cho dich.
  * Seeker (seeker_quet_nguon.py roi ong_dan nhan/phan_loai/quyet_dinh) - mang + ghi dia -> chi chay khi hang dau vao
    sap can (hang MT5 < N hoac the chua dich < M) VA o dia cua thu muc tai ve con > san; co tran GB moi luot + tong;
    xong luot thi xoa tep tho (nen/zip/bi5, nhi phan lon, trung noi dung) khong the nao tro toi.
20/10/2026 09:50 (chu du an): KHONG giam tai theo game - may chay The Brain het suc (CPU toi ~95%, uu tien Normal)
hoac tat han (BAT_THE_BRAIN.bat / TAT_THE_BRAIN.bat). Gioi han duy nhat: RAM trong >= ram_toi_thieu_gb (chong swap /
sap), CPU < cpu_cao_pct, san o dia.
Moi quyet dinh -> data/dieu_phoi/nhat_ky.jsonl (kem ly do); mau su dung -> data/dieu_phoi/su_dung.jsonl.
Cau hinh: config/dieu_phoi.json (tai_lieu/ONG_DAN.md muc "Bo dieu phoi"). Khong doc / in khoa.

Chay:  python may_nha_toi_nay/dieu_phoi_may_nha.py --den 07:00 [--mot_lan] [--kho]   (--kho: chi tinh + ghi, khong phong gi)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "mt5tools"))
CAU_HINH = GOC / "config" / "dieu_phoi.json"
THU_MUC = GOC / "data" / "dieu_phoi"
MUC_MT5 = THU_MUC / "muc_mt5.json"
NHAT_KY = THU_MUC / "nhat_ky.jsonl"
SU_DUNG = THU_MUC / "su_dung.jsonl"
TRANG_THAI = THU_MUC / "trang_thai.json"
LOG_DIR = Path(os.environ.get("BRAIN_LOG_DIR") or (GOC / "may_nha_toi_nay" / "log"))
CO_TAT = GOC / "may_nha_toi_nay" / "TAT_THE_BRAIN.co"   # TAT_THE_BRAIN.bat tao, BAT_THE_BRAIN.bat xoa (git bo qua)
KHOA_OD = LOG_DIR / "ong_dan_chay.lock"          # chung voi chay_toi_nay.ps1 buoc 6 / dich_llm_nen.ps1 (noi dung = PID)


def cau_hinh(p: Path | None = None) -> dict:
    p = Path(os.environ.get("BRAIN_DIEU_PHOI_JSON") or p or CAU_HINH)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"bat": False}


def _bay_gio() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _ghi_dong(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ do dac
def _psutil():
    try:
        import psutil
        return psutil
    except Exception:
        return None


def tien_trinh() -> list[tuple[str, str]]:
    """[(ten tien trinh thuong, duong dan exe thuong)]; khong co psutil -> tasklist (Windows) / rong."""
    ps = _psutil()
    ra = []
    if ps:
        for p in ps.process_iter(["name", "exe"]):
            try:
                ra.append(((p.info.get("name") or "").lower(), (p.info.get("exe") or "").lower()))
            except Exception:
                pass
        return ra
    if os.name == "nt":
        try:
            o = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, timeout=30).stdout
            ra = [(x.split('","')[0].strip('"').lower(), "") for x in o.splitlines() if x]
        except Exception:
            pass
    return ra


def thu_muc_that(p) -> Path:
    p = Path(p)
    p = p if p.is_absolute() else GOC / p
    try:
        return Path(os.path.realpath(p))
    except OSError:
        return p


def trong_gb(p, disk_usage=shutil.disk_usage) -> float:
    q = thu_muc_that(p)
    while not q.exists() and q != q.parent:
        q = q.parent
    try:
        return disk_usage(str(q)).free / 1024 ** 3
    except OSError:
        return float("nan")


def kich_thuoc_gb(p) -> float:
    q = thu_muc_that(p)
    s = 0
    for r, _, fs in os.walk(q):
        for f in fs:
            try:
                s += os.lstat(os.path.join(r, f)).st_size
            except OSError:
                pass
    return s / 1024 ** 3


def slot_ban(ds_tt: list, slots: list[str]) -> int:
    n = 0
    for s in slots:
        s2 = s.lower().rstrip("\\/")
        n += sum(1 for t, e in ds_tt if t == "terminal64.exe" and e.startswith(s2))
    return n


def hang_mt5() -> int | None:
    try:
        import sinh_viec as SV
        import quan_ly_slot as QS
        return len(SV.lay_viec(200, hai_tang=QS.hai_tang()))
    except Exception:
        return None


def the_chua_dich() -> int | None:
    try:
        from nhan import dich_llm as DL
        from nhan import ong_dan as OD
        cn = OD._db()
        try:
            return sum(1 for x in DL.danh_sach_cho(cn) if x["tep"] is not None)
        finally:
            cn.close()
    except Exception:
        return None


def cho_python() -> tuple[int | None, int | None]:
    """(the cho toi_uu Python, trong do the ghep cheo) - tu cache ong dan. Loi -> (None, None) (CHUA DO DUOC)."""
    try:
        from nhan import ong_dan as OD
        cn = OD._db()
        try:
            n = cn.execute("SELECT COUNT(*) FROM the WHERE buoc='quyet_dinh' AND loai='he_hoan_thien' AND "
                           "duong IN ('noi_bo','spec_dsl','python_llm')").fetchone()[0]
            g = cn.execute("SELECT COUNT(*) FROM the WHERE buoc='quyet_dinh' AND trang_thai='GHEP_CHEO'").fetchone()[0]
            return int(n), int(g)
        finally:
            cn.close()
    except Exception:
        return None, None


def do_dac(cfg: dict) -> dict:
    """Mot mau tai nguyen. Thieu psutil -> ghi None (CHUA DO DUOC), khong doan."""
    import quan_ly_slot as QS
    ps = _psutil()
    ds = tien_trinh()
    slots = QS.ds_slot()
    sk = cfg.get("seeker") or {}
    d = {"luc": _bay_gio(), "cpu_pct": None, "ram_trong_gb": None, "ram_tong_gb": None,
         "slot_tong": len(slots), "slot_ban": slot_ban(ds, slots),
         "o_trong_gb": {}, "tai_ve_trong_gb": round(trong_gb(sk.get("thu_muc_tai_ve") or "data/seeker_da_nguon/tai_ve"), 1)}
    if ps:
        d["cpu_pct"] = ps.cpu_percent(interval=1.0)
        vm = ps.virtual_memory()
        d["ram_trong_gb"], d["ram_tong_gb"] = round(vm.available / 1024 ** 3, 2), round(vm.total / 1024 ** 3, 1)
    for s in slots:
        o = QS.o_cua(s)
        if o and o not in d["o_trong_gb"]:
            d["o_trong_gb"][o] = round(trong_gb(QS.goc_o(s)), 1)
    for o in (cfg.get("suc_khoe") or {}).get("o_kiem") or []:      # 20/10 toi: san C/D ~6 GB du khong co slot
        if os.path.exists(o) and o[:2].upper() not in {k[:2].upper() for k in d["o_trong_gb"]}:
            d["o_trong_gb"][o[:2].upper()] = round(trong_gb(o), 1)
    return d


# ------------------------------------------------------------------ quyet dinh (ham thuan - co test)
def muc_mt5(d: dict, cfg: dict) -> dict:
    """So slot tang 1 / tang 2 cho phep theo RAM / CPU."""
    t1max, t2max = int(cfg.get("tang1_slot_toi_da", 5)), int(cfg.get("tang2_slot_toi_da", 3))
    ram, rmin = d.get("ram_trong_gb"), float(cfg.get("ram_toi_thieu_gb", 4.0))
    if ram is None:
        return {"tong": t1max, "tang2": t2max, "nang_moi": True, "ly_do": "RAM CHUA DO DUOC (thieu psutil) -> giu muc cau hinh"}
    if ram < rmin:
        return {"tong": 0, "tang2": 0, "nang_moi": False,
                "ly_do": "RAM trong %.1f GB < %.1f GB -> khong phong viec nang moi (viec dang chay giu nguyen)" % (ram, rmin)}
    # RAM con lai sau san -> bao nhieu slot MOI phong them duoc; viec dang chay da nam trong RAM da dung
    ban = int(d.get("slot_ban") or 0)
    du = ram - rmin
    t2 = min(t2max, ban + int(du // float(cfg.get("ram_moi_slot_tang2_gb", 2.5))))
    t2 = max(min(int(cfg.get("tang2_slot_toi_thieu", 1)), t2max), t2) if ram >= float(cfg.get("ram_moi_slot_tang2_gb", 2.5)) + rmin else t2
    tong = min(t1max, ban + int(du // float(cfg.get("ram_moi_slot_tang1_gb", 1.2))))
    tong = max(tong, t2)
    cpu = d.get("cpu_pct")
    ly = "RAM trong %.1f GB (san %.1f): tong %d viec (tang 1 nhe), tang 2 toi da %d" % (ram, rmin, tong, t2)
    if cpu is not None and cpu >= float(cfg.get("cpu_cao_pct", 92)):
        tong = max(ban, 1) if ban else min(tong, 1)
        ly += "; CPU %.0f%% >= %s%% -> khong them viec" % (cpu, cfg.get("cpu_cao_pct", 92))
    return {"tong": int(tong), "tang2": int(min(t2, tong)), "nang_moi": True, "ly_do": ly}


def nen_chay_dich(d: dict, cfg: dict, cho: int | None, dang_chay: bool, nghi_toi: float, bay_gio: float) -> tuple[bool, str]:
    c = cfg.get("dich_llm") or {}
    if not c.get("bat", True):
        return False, "dich_llm tat trong cau hinh"
    if dang_chay:
        return False, "dich_llm dang chay"
    if bay_gio < nghi_toi:
        return False, "dich_llm vua het viec / loi - nghi toi %s" % dt.datetime.fromtimestamp(nghi_toi).strftime("%H:%M")
    if cho is not None and cho <= 0:
        return False, "khong con the cho dich"
    if d.get("ram_trong_gb") is not None and d["ram_trong_gb"] < 1.0:
        return False, "RAM trong %.1f GB < 1 GB" % d["ram_trong_gb"]
    return True, "con %s the cho dich; dich_llm nhe (cho mang) -> chay song song MT5" % ("?" if cho is None else cho)


def nen_chay_seeker(d: dict, cfg: dict, hang: int | None, cho: int | None, tt: dict, dang_chay: bool, bay_gio: float) -> tuple[bool, str]:
    c = cfg.get("seeker") or {}
    if not c.get("bat", True):
        return False, "Seeker tat trong cau hinh"
    if dang_chay:
        return False, "Seeker dang chay"
    if d.get("ram_trong_gb") is not None and d["ram_trong_gb"] < float(cfg.get("ram_toi_thieu_gb", 4.0)):
        return False, "RAM trong %.1f GB < san -> nhuong MT5" % d["ram_trong_gb"]
    nghi = float(c.get("nghi_giua_hai_luot_phut", 60)) * 60
    if bay_gio - float(tt.get("seeker_luc_xong") or 0) < nghi:
        return False, "Seeker vua chay xong < %d phut" % (nghi // 60)
    thieu = o_duoi_san(d, cfg)
    if thieu:
        return False, "ổ %s dưới sàn %.0f GB -> không tải thêm" % (",".join(thieu), float((cfg.get("suc_khoe") or {}).get("san_o_gb", 6)))
    tg = d.get("tai_ve_trong_gb")
    san = float(c.get("o_toi_thieu_gb", 20))
    if tg is None or tg != tg or tg < san:
        return False, "o thu muc tai ve con %s GB < %.0f GB -> khong tai them" % (tg, san)
    tong = float(tt.get("seeker_gb_tong") or 0)
    if tong >= float(c.get("gb_tong_toi_da", 60)):
        return False, "da tai %.1f GB >= tran tong %.0f GB" % (tong, float(c.get("gb_tong_toi_da", 60)))
    can_hang = hang is not None and hang < int(c.get("hang_mt5_duoi", 20))
    can_dich = cho is not None and cho < int(c.get("the_chua_dich_duoi", 40))
    if not (can_hang or can_dich):
        return False, "hang dau vao con du (MT5 %s viec, chua dich %s the)" % (hang, cho)
    return True, "hang sap can (MT5 %s < %s hoac chua dich %s < %s), o tai ve con %.1f GB" % (
        hang, c.get("hang_mt5_duoi", 20), cho, c.get("the_chua_dich_duoi", 40), tg)


def o_duoi_san(d: dict, cfg: dict) -> list[str]:
    """O he thong / SSD (C, D) duoi san (mac dinh 6 GB) -> danh sach; E (lanh) khong tinh."""
    san = float((cfg.get("suc_khoe") or {}).get("san_o_gb", 6.0))
    lanh = {x[:1].upper() for x in (cfg.get("suc_khoe") or {}).get("o_lanh") or ["E"]}
    return sorted(k for k, v in (d.get("o_trong_gb") or {}).items()
                  if isinstance(v, (int, float)) and v == v and v < san and k[:1].upper() not in lanh)


def chon_viec_od(hang: int | None, cho_dich: int | None, cho_py: int | None, ton_ghep: int | None, cfg: dict,
                 tt: dict, bay_gio: float) -> tuple[str | None, str]:
    """Mot o "ong dan" (chung khoa ong_dan_chay.lock: dich_llm / python / ghep khong chay cung luc).
    Day chuyen san xuat -> tieu thu, khong de o trong:
      MT5 doi (hang < hang_mt5_duoi): the cho Python -> python (nhanh nhat ra viec MT5);
                                       het the Python -> ghep_cheo (lap cho trong MT5) neu het nghi, khong thi dich_llm.
      MT5 du viec: con the chua dich -> dich_llm; con the Python -> python; con lai -> ghep_cheo.
    -> (viec | None, ly do)."""
    c = cfg.get("vong_lap") or {}
    if not c.get("bat", True):
        return ("dich" if (cho_dich or 0) > 0 else None), "vong_lap tat -> chi dich_llm nhu cu"
    duoi = int((cfg.get("seeker") or {}).get("hang_mt5_duoi", 20))
    doi = hang is not None and hang < duoi
    gc = cfg.get("ghep_cheo") or {}
    ghep_ok = gc.get("bat", True) and bay_gio - float(tt.get("ghep_luc_xong") or 0) >= float(gc.get("nghi_phut", 30)) * 60 \
        and (ton_ghep or 0) < int(gc.get("tran_ton", 60))
    py_ok = (cho_py or 0) > 0 and bay_gio - float(tt.get("python_luc_xong") or 0) >= float(c.get("python_nghi_giay", 60))
    if doi:
        if py_ok:
            return "python", "MT5 đói (%s < %d) và còn %s thẻ chờ Python" % (hang, duoi, cho_py)
        if ghep_ok:
            return "ghep", "MT5 đói (%s < %d), hết thẻ Python -> sinh thẻ ghép chéo" % (hang, duoi)
        if (cho_dich or 0) > 0:
            return "dich", "MT5 đói, ghép đang nghỉ/đủ trần -> đẩy dịch (%s thẻ chờ)" % cho_dich
    if (cho_dich or 0) > 0:
        return "dich", "MT5 đủ việc (%s), còn %s thẻ chờ dịch" % (hang, cho_dich)
    if py_ok:
        return "python", "hết thẻ dịch, còn %s thẻ chờ Python" % cho_py
    if ghep_ok:
        return "ghep", "mọi hàng trống -> ghép chéo"
    return None, "không có việc ống dẫn (MT5 %s, dịch %s, Python %s, ghép tồn %s)" % (hang, cho_dich, cho_py, ton_ghep)


def terminal_bo_roi(ds: list[dict], bay_gio: float, cfg: dict, la_tester=None) -> list[dict]:
    """Terminal TESTER bo roi (giet DUNG PID, chi khi la_terminal_tester): (a) mo khong co /config: (do mt5.initialize mo,
    loi truoc d4100d3d) qua `terminal_tran_phut` phut; (b) chay qua `terminal_qua_gio_phut` (lon hon han viec 6 gio).
    ds: [{pid, exe, cmd, tao}]. Terminal giao dich (BRAIN_TERMINAL_GIAO_DICH) / mo tay -> la_tester False -> khong dung."""
    if la_tester is None:
        from nhan.khoa_tester import la_terminal_tester as la_tester
    c = cfg.get("suc_khoe") or {}
    tran, qua = float(c.get("terminal_tran_phut", 20)) * 60, float(c.get("terminal_qua_gio_phut", 420)) * 60
    ra = []
    for t in ds:
        exe, cmd = t.get("exe") or "", t.get("cmd") or ""
        if not la_tester(exe, cmd):
            continue
        tuoi = bay_gio - float(t.get("tao") or bay_gio)
        if "/config:" not in cmd.lower() and tuoi > tran:
            ra.append(dict(t, ly_do="terminal tester không /config: (initialize mở) %.0f phút" % (tuoi / 60)))
        elif tuoi > qua:
            ra.append(dict(t, ly_do="terminal tester chạy %.0f phút > %.0f" % (tuoi / 60, qua / 60)))
    return ra


def _ds_terminal() -> list[dict]:
    ps = _psutil()
    if not ps:
        return []
    ra = []
    for p in ps.process_iter(["pid", "name", "exe", "cmdline", "create_time"]):
        try:
            if (p.info.get("name") or "").lower() == "terminal64.exe":
                ra.append({"pid": p.info["pid"], "exe": p.info.get("exe") or "", "cmd": " ".join(p.info.get("cmdline") or []),
                           "tao": p.info.get("create_time")})
        except Exception:
            pass
    return ra


def mt5_dang_chay() -> bool | None:
    """Co tien trinh python chay mt5tools/chay_lien_tuc.py? Khong co psutil -> None."""
    ps = _psutil()
    if not ps:
        return None
    for p in ps.process_iter(["name", "cmdline"]):
        try:
            if "python" in (p.info.get("name") or "").lower() and any("chay_lien_tuc" in x for x in p.info.get("cmdline") or []):
                return True
        except Exception:
            pass
    return False


# ------------------------------------------------------------------ don tep tho sau khi nhan
def tep_duoc_tham_chieu() -> set[str]:
    """Moi duong dan (tuyet doi, realpath, thuong) ma the trong trang_thai.sqlite tro toi."""
    from nhan import ong_dan as OD
    ra = set()
    cn = OD._db()
    try:
        for t, *_ in OD.cac_the(cn):
            ng = t.get("nguon") or {}
            ds = [ng.get("tep")] + list(t.get("sets") or []) + list(t.get("ea_lien_quan") or [])
            for p in ds:
                if p:
                    ra.add(str(thu_muc_that(p)).lower())
    finally:
        cn.close()
    return ra


def don_tho(goc, cfg: dict, tham_chieu: set[str], bay_gio: float | None = None, log=print) -> dict:
    """Xoa tep tho trong thu muc tai ve: nen/zip/bi5, nhi phan lon khong phai ma, tep trung sha1 - tru tep the tro toi."""
    c = cfg.get("don_tho") or {}
    kq = {"xoa": 0, "gb": 0.0, "trung": 0}
    if not c.get("bat", True):
        return kq
    bay_gio = bay_gio or time.time()
    duoi_xoa = {x.lower() for x in c.get("duoi_xoa") or []}
    giu = {x.lower() for x in c.get("giu_duoi") or []}
    lon = float(c.get("tep_lon_mb", 5)) * 1024 ** 2
    cu = float(c.get("chi_xoa_cu_hon_phut", 30)) * 60
    goc = thu_muc_that(goc)
    thay = {}
    # luot 1: tep duoc tham chieu truoc (ban goc giu lai), luot 2: con lai
    tat_ca = []
    for r, ds_d, fs in os.walk(goc):
        ds_d[:] = [x for x in ds_d if x != ".git"]
        tat_ca += [(r, f) for f in fs]
    tat_ca.sort(key=lambda rf: (str(thu_muc_that(Path(*rf))).lower() not in tham_chieu, rf))
    for r, ds_d, fs in [(r, [], [f]) for r, f in tat_ca]:
        ds_d[:] = [x for x in ds_d if x != ".git"]
        for f in sorted(fs):
            p = Path(r, f)
            try:
                st = p.stat()
            except OSError:
                continue
            k = str(thu_muc_that(p)).lower()
            if k in tham_chieu:                    # the dang tro toi: giu, nhung ghi sha1 de ban sao khac bi xoa
                if 4096 < st.st_size <= lon:
                    thay.setdefault(hashlib.sha1(p.read_bytes()).hexdigest(), p)
                continue
            if bay_gio - st.st_mtime < cu:
                continue
            ext = p.suffix.lower()
            ly = None
            if ext in duoi_xoa:
                ly = "tep nen/tho %s" % ext
            elif st.st_size > lon and ext not in giu:
                ly = "nhi phan lon %.1f MB" % (st.st_size / 1024 ** 2)
            else:
                if st.st_size > 4096:
                    h = hashlib.sha1(p.read_bytes()).hexdigest()
                    if h in thay:
                        ly = "trung noi dung voi %s" % thay[h].name
                        kq["trung"] += 1
                    else:
                        thay[h] = p
            if ly:
                try:
                    p.unlink()
                    kq["xoa"] += 1
                    kq["gb"] += st.st_size / 1024 ** 3
                except OSError as e:
                    log("khong xoa duoc %s: %s" % (p, e))
    kq["gb"] = round(kq["gb"], 3)
    return kq


# ------------------------------------------------------------------ vong chinh
def ghi_muc_mt5(m: dict, p: Path = MUC_MT5) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(dict(m, luc=_bay_gio(), ts=time.time()), ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def _khoa_ranh() -> bool:
    if not KHOA_OD.exists():
        return True
    try:
        pid = int(KHOA_OD.read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return True
    ps = _psutil()
    cu = time.time() - KHOA_OD.stat().st_mtime > 3 * 3600          # khong co psutil: khoa > 3 gio coi nhu bo roi
    if (ps and not ps.pid_exists(pid)) or (not ps and cu):
        KHOA_OD.unlink(missing_ok=True)
        return True
    return False


PID_DIR = LOG_DIR / "pid"


def ghi_pid(ten: str, pid: int) -> None:
    """PID tien trinh ong dan cua ta -> log/pid/<ten>.pid (TAT_THE_BRAIN chi dung cac PID nay)."""
    try:
        PID_DIR.mkdir(parents=True, exist_ok=True)
        (PID_DIR / ("%s.pid" % ten)).write_text(str(pid))
    except OSError:
        pass


def co_lenh_tat() -> bool:
    """TAT_THE_BRAIN.bat tao may_nha_toi_nay/TAT_THE_BRAIN.co -> khong phong viec moi, ket thuc em."""
    return CO_TAT.exists()


def _phong(lenh: list[str], ten: str) -> subprocess.Popen:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    out = open(LOG_DIR / ("dp_%s.out.txt" % ten), "a", encoding="utf-8")
    kw = {}                                      # 20/10/2026 09:50: uu tien Normal (khong BelowNormal) - chay het suc
    if os.name == "nt":
        kw["creationflags"] = 0x00000200          # CREATE_NEW_PROCESS_GROUP: TAT_THE_BRAIN dung dung cay nay
    p = subprocess.Popen([sys.executable] + lenh, cwd=str(GOC), stdout=out, stderr=subprocess.STDOUT, **kw)
    ghi_pid(ten, p.pid)
    return p


def giet_cay(p) -> None:
    """Giet tien trinh Popen p cua ta va cac con cua no theo PID (psutil); khong psutil -> chi p."""
    ps = _psutil()
    try:
        if ps:
            for c in ps.Process(p.pid).children(recursive=True):
                try:
                    c.kill()
                except Exception:
                    pass
        p.kill()
    except Exception:
        pass


def lenh_od(viec: str, cfg: dict) -> list[str]:
    """Lenh cho o ong dan. python = toi_uu -> loc -> boc -> sinh_mt5 (moi buoc mot tien trinh con, noi tiep)."""
    if viec == "dich":
        c = cfg.get("dich_llm") or {}
        return ["ong_dan.py", "dich_llm", "--gioi_han", str(c.get("gioi_han_moi_luot", 200)), "--luong", str(c.get("luong", 4))]
    if viec == "python":
        c = cfg.get("vong_lap") or {}
        buoc = [["toi_uu", "--toi-da", str(c.get("python_the_moi_luot", 12))], ["loc"], ["boc"], ["sinh_mt5"]]
        return ["-c", "import subprocess,sys\nfor b in %r:\n    r=subprocess.run([sys.executable,'ong_dan.py']+b).returncode\n"
                      "    print(b[0],'rc',r,flush=True)\n    if r: sys.exit(r)" % (buoc,)]
    if viec == "ghep":
        return ["-m", "nhan.ghep_cheo", "--tran", str((cfg.get("ghep_cheo") or {}).get("tran_moi_luot", 20))]
    raise ValueError(viec)


class DieuPhoi:
    def __init__(self, cfg: dict, kho: bool = False):
        self.cfg, self.kho = cfg, kho
        self.dich = None
        self.seeker = None            # (Popen, pha, t0, gb_dau)
        self.nghi_dich = 0.0
        self.cu = {}
        try:
            self.tt = json.loads(TRANG_THAI.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.tt = {}
        self.t_hang = (0.0, None, None)
        self.od_ten = None            # viec dang giu o ong dan: dich / python / ghep
        self.t_py = (0.0, None, None)
        self.mt5_tat_luc = 0.0

    def ghi(self, viec: str, quyet: str, ly_do: str, ep: bool = False) -> None:
        if not ep and self.cu.get(viec) == (quyet, ly_do):
            return
        self.cu[viec] = (quyet, ly_do)
        _ghi_dong(NHAT_KY, {"luc": _bay_gio(), "viec": viec, "quyet": quyet, "ly_do": ly_do})
        print("%s [%s] %s: %s" % (_bay_gio(), viec, quyet, ly_do), flush=True)

    def _luu_tt(self):
        THU_MUC.mkdir(parents=True, exist_ok=True)
        TRANG_THAI.write_text(json.dumps(self.tt, ensure_ascii=False), encoding="utf-8")

    def vong(self) -> dict:
        cfg = self.cfg
        d = do_dac(cfg)
        now = time.time()
        if now - self.t_hang[0] > 300:
            self.t_hang = (now, hang_mt5(), the_chua_dich())
        _, hang, cho = self.t_hang
        d.update(hang_mt5=hang, the_chua_dich=cho)
        # MT5
        m = muc_mt5(d, cfg)
        if not self.kho:
            ghi_muc_mt5(m)
        self.ghi("mt5", "tong=%d tang2=%d" % (m["tong"], m["tang2"]), m["ly_do"])
        # o ong dan (dich_llm / python / ghep_cheo - chung khoa ong_dan_chay.lock)
        if now - self.t_py[0] > 120:
            self.t_py = (now, *cho_python())
        _, cho_py, ton_ghep = self.t_py
        d.update(cho_python=cho_py, ghep_ton=ton_ghep)
        if self.dich is not None and self.dich.poll() is not None:
            rc, ten = self.dich.returncode, self.od_ten
            self.dich, self.od_ten = None, None
            KHOA_OD.unlink(missing_ok=True)
            if ten == "dich":
                self.nghi_dich = now + float((cfg.get("dich_llm") or {}).get("nghi_khi_het_giay", 900)) if rc != 0 or (cho or 0) == 0 else now
            else:
                self.tt["%s_luc_xong" % ten] = now
                self._luu_tt()
            self.ghi(ten or "dich_llm", "xong", "rc=%s" % rc, ep=True)
            self.t_hang = (0.0, None, None)
            self.t_py = (0.0, None, None)
        elif self.dich is not None:
            han = {"dich": float((cfg.get("dich_llm") or {}).get("qua_gio_phut", 120)),
                   "python": float((cfg.get("vong_lap") or {}).get("python_qua_gio_phut", 90)),
                   "ghep": float((cfg.get("ghep_cheo") or {}).get("qua_gio_phut", 30))}.get(self.od_ten, 120.0)
            if now - self.dich_t0 > han * 60:
                giet_cay(self.dich)                  # DUNG PID con cua minh + cay con cua no, khong taskkill theo ten
                self.ghi(self.od_ten or "dich_llm", "giet", "qua gio %.0f phut" % han, ep=True)
        if self.dich is None:
            viec, ly = chon_viec_od(hang, cho, cho_py, ton_ghep, cfg, self.tt, now)
            if viec == "dich":
                ok, ly2 = nen_chay_dich(d, cfg, cho, False, self.nghi_dich, now)
                if not ok and (cho_py or 0) > 0:
                    viec, ly = "python", ly2 + " -> làm Python thay"
                elif not ok:
                    viec, ly = None, ly2
            if viec and self.seeker is not None and self.seeker[1] == "ong_dan":
                viec, ly = None, "ong_dan nhan/phan_loai dang ghi CSDL"
            if viec and not _khoa_ranh():
                viec, ly = None, "ong_dan_chay.lock dang bi tien trinh khac giu"
            self.ghi("ong_dan", ("CHAY " + viec) if viec else "cho", ly)
            if viec and not self.kho:
                self.dich = _phong(lenh_od(viec, cfg), {"dich": "dich_llm"}.get(viec, viec))
                self.od_ten, self.dich_t0 = viec, now
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                KHOA_OD.write_text(str(self.dich.pid))
        # suc khoe / tu hoi phuc
        self._suc_khoe(d, m, hang, now)
        # Seeker
        self._seeker(d, hang, cho, now)
        d["dang_chay"] = {"dich_llm": self.od_ten == "dich", "python": self.od_ten == "python", "ghep": self.od_ten == "ghep",
                          "seeker": None if self.seeker is None else self.seeker[1],
                          "mt5_cho_phep": m["tong"]}
        _ghi_dong(SU_DUNG, d)
        return d

    def _suc_khoe(self, d, m, hang, now):
        c = self.cfg.get("suc_khoe") or {}
        if not c.get("bat", True):
            return
        thieu = o_duoi_san(d, self.cfg)
        if thieu:
            if not self.kho:
                ghi_muc_mt5(dict(m, tong=0, tang2=0, nang_moi=False, ly_do="ổ %s dưới sàn -> dừng phóng việc MT5 mới" % ",".join(thieu)))
            self.ghi("suc_khoe", "O_DAY", "ổ %s < %.0f GB: không phóng MT5/Seeker mới; dời dữ liệu lạnh sang E" % (
                ",".join(thieu), float(c.get("san_o_gb", 6))))
        for t in terminal_bo_roi(_ds_terminal(), now, self.cfg):
            self.ghi("suc_khoe", "DONG_TERMINAL", "PID %s %s: %s" % (t["pid"], t["exe"], t["ly_do"]), ep=True)
            if not self.kho:
                try:
                    _psutil().Process(int(t["pid"])).terminate()      # dung PID, khong bao gio theo ten
                except Exception as e:  # noqa: BLE001
                    self.ghi("suc_khoe", "loi", "PID %s: %s" % (t["pid"], e), ep=True)
        if c.get("khoi_dong_lai_mt5", True) and hang and not co_lenh_tat() and not thieu:
            chay = mt5_dang_chay()
            if chay is False and now - self.mt5_tat_luc > float(c.get("mt5_cho_khoi_dong_giay", 600)):
                self.mt5_tat_luc = now
                den = self.den.strftime("%H:%M") if getattr(self, "den", None) else "07:00"
                self.ghi("suc_khoe", "KHOI_DONG_LAI_MT5", "hàng MT5 %s việc nhưng không thấy chay_lien_tuc.py -> phóng lại tới %s" % (hang, den), ep=True)
                if not self.kho:
                    _phong(["mt5tools/chay_lien_tuc.py", "--den", den], "mt5_hoi_phuc")
            elif chay:
                self.mt5_tat_luc = now

    def _seeker(self, d, hang, cho, now):
        cfg = self.cfg
        c = cfg.get("seeker") or {}
        tv = c.get("thu_muc_tai_ve") or "data/seeker_da_nguon/tai_ve"
        if self.seeker is not None:
            p, pha, t0, gb0 = self.seeker
            moi = kich_thuoc_gb(tv) - gb0 if pha == "quet" else 0.0
            if pha == "quet" and (moi > float(c.get("gb_moi_luot", 3))
                                  or (d.get("tai_ve_trong_gb") or 99) < float(c.get("o_toi_thieu_gb", 20))):
                p.kill()
                self.ghi("seeker", "DUNG", "luot tai %.2f GB / o con %s GB" % (moi, d.get("tai_ve_trong_gb")), ep=True)
            if p.poll() is None:
                if now - t0 > float(c.get("qua_gio_phut", 90)) * 60:
                    p.kill()
                    self.ghi("seeker", "giet", "qua gio %s phut (pha %s)" % (c.get("qua_gio_phut", 90), pha), ep=True)
                return
            if pha == "quet":
                self.tt["seeker_gb_tong"] = round(float(self.tt.get("seeker_gb_tong") or 0) + max(0.0, moi), 3)
                self.ghi("seeker", "quet xong", "rc=%s, tai them %.2f GB" % (p.returncode, moi), ep=True)
                if self.dich is not None or not _khoa_ranh():
                    self.tt["seeker_can_nhan"] = True           # nhan sau, khi dich_llm / khoa ranh
                else:
                    self._nhan(now)
                    return
            elif pha == "ong_dan":
                KHOA_OD.unlink(missing_ok=True)
                kq = don_tho(tv, cfg, tep_duoc_tham_chieu(), log=lambda s: self.ghi("don_tho", "loi", s, ep=True)) \
                    if (cfg.get("don_tho") or {}).get("bat", True) and not self.kho else {"xoa": 0, "gb": 0.0, "trung": 0}
                self.ghi("don_tho", "xong", "xoa %d tep tho (%.2f GB, %d trung noi dung)" % (kq["xoa"], kq["gb"], kq["trung"]), ep=True)
                self.tt["seeker_can_nhan"] = False
            self.seeker = None
            self.tt["seeker_luc_xong"] = now
            self._luu_tt()
            return
        if self.tt.get("seeker_can_nhan") and self.dich is None and _khoa_ranh() and not self.kho:
            self._nhan(now)
            return
        ok, ly = nen_chay_seeker(d, cfg, hang, cho, self.tt, False, now)
        self.ghi("seeker", "CHAY" if ok else "cho", ly)
        if ok and not self.kho:
            self.seeker = (_phong(list(c.get("lenh") or ["seeker_quet_nguon.py"]), "seeker"), "quet", now, kich_thuoc_gb(tv))

    def _nhan(self, now):
        # nhan + phan_loai + quyet_dinh mot tien trinh noi tiep (giu khoa ong_dan_chay.lock)
        lenh = ["-c", "import subprocess,sys\nfor b in ('nhan','phan_loai','quyet_dinh'):\n"
                      "    r=subprocess.run([sys.executable,'ong_dan.py',b]).returncode\n    print(b,'rc',r,flush=True)"]
        p = _phong(lenh, "seeker_ong_dan")
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        KHOA_OD.write_text(str(p.pid))
        self.seeker = (p, "ong_dan", now, 0.0)
        self.ghi("seeker", "ong_dan nhan/phan_loai/quyet_dinh", "sau luot quet", ep=True)

    def dung(self):
        for p in (self.dich, None if self.seeker is None else self.seeker[0]):
            if p is not None and p.poll() is None:
                p.terminate()
        KHOA_OD.unlink(missing_ok=True)
        self._luu_tt()


def tom_tat_su_dung(tu: float, p: Path = SU_DUNG) -> dict | None:
    """Trung binh mau tu thoi diem `tu` (epoch) - cho bao_cao_phien. Khong co mau -> None (CHUA DO DUOC)."""
    if not p.exists():
        return None
    ds = []
    for x in p.read_text(encoding="utf-8").splitlines()[-5000:]:
        try:
            d = json.loads(x)
            if dt.datetime.fromisoformat(d["luc"]).timestamp() >= tu:
                ds.append(d)
        except (ValueError, KeyError):
            continue
    if not ds:
        return None

    def tb(k):
        v = [x[k] for x in ds if isinstance(x.get(k), (int, float))]
        return round(sum(v) / len(v), 1) if v else None
    ban = [100.0 * x["slot_ban"] / x["slot_tong"] for x in ds if x.get("slot_tong")]
    o = {}
    for x in ds:
        for k, v in (x.get("o_trong_gb") or {}).items():
            o[k] = v
    return {"so_mau": len(ds), "cpu_pct": tb("cpu_pct"), "ram_trong_gb": tb("ram_trong_gb"), "ram_tong_gb": tb("ram_tong_gb"),
            "slot_ban_pct": round(sum(ban) / len(ban), 1) if ban else None, "o_trong_gb_cuoi": o,
            "tai_ve_trong_gb_cuoi": ds[-1].get("tai_ve_trong_gb"),
            "dich_llm_pct": round(100.0 * sum(1 for x in ds if (x.get("dang_chay") or {}).get("dich_llm")) / len(ds), 1),
            "seeker_pct": round(100.0 * sum(1 for x in ds if (x.get("dang_chay") or {}).get("seeker")) / len(ds), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--den", default="07:00")
    ap.add_argument("--mot_lan", action="store_true")
    ap.add_argument("--kho", action="store_true", help="chi do + ghi quyet dinh, khong phong tien trinh, khong ghi muc_mt5")
    a = ap.parse_args()
    cfg = cau_hinh()
    if not cfg.get("bat"):
        print("dieu_phoi: tat trong config/dieu_phoi.json")
        return 0
    h = dt.datetime.combine(dt.date.today(), dt.datetime.strptime(a.den, "%H:%M").time())
    if h <= dt.datetime.now():
        h += dt.timedelta(days=1)
    dp = DieuPhoi(cfg, kho=a.kho)
    dp.den = h
    ghi_pid("dieu_phoi", os.getpid())
    dp.ghi("dieu_phoi", "BAT DAU", "toi %s, chu ky %ss" % (h, cfg.get("chu_ky_giay", 60)), ep=True)
    try:
        while True:
            try:
                dp.vong()
            except Exception as e:  # noqa: BLE001 - mot vong loi khong dung bo dieu phoi
                dp.ghi("dieu_phoi", "loi", "%s: %s" % (type(e).__name__, str(e)[:200]), ep=True)
            if a.mot_lan or dt.datetime.now() >= h or co_lenh_tat():
                break
            time.sleep(float(cfg.get("chu_ky_giay", 60)))
    finally:
        dp.dung()
        dp.ghi("dieu_phoi", "HET", "toi gio / mot lan", ep=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
