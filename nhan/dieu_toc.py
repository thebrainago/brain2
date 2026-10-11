# -*- coding: utf-8 -*-
"""DIEU TOC SEEKER (11/10/2026): backtest dang chay -> SEEKER/CAU KHO cham lai hoac dung.

VI SAO. Chu du an (t30u): "dieu toc khi he thong dang backtest". Do that 10-11/10 tren box:
vong G-a (1848 mo phong, 7 tien trinh) chiem gan het CPU hang gio; `dieu_phoi` chi co nguong
CPU chung (khong biet viec nao la backtest), con `vong_thu_nghiem.py` chay TAY ngoai
`dieu_phoi` thi khong de dau vet gi. Ket qua: quet + doc ma (doc_ma ton CPU) tranh CPU voi
mo phong, va mot luot tester MT5 (khoa `khoa_tester`) co the bi lam cham.

TIN HIEU (chi DOC, khong giet/khong doi gi cua tien trinh khac):
  1. khoa tester (`config/khoa_tester*.json`, chu giu con song)      -> DUNG
  2. dau backtest (`config/dang_backtest/<pid>.json`, ghi boi `dang_chay()`; pid con song)
     -> CHAM (vong_thu_nghiem, quet tester tay...)
  3. tien trinh co ten trong `TEN_BACKTEST` (doc /proc hoac psutil) -> CHAM;
     `terminal64.exe` / `metatester64.exe` -> DUNG
  4. CPU toan may >= `CPU_DUNG` (80%) -> DUNG; >= `CPU_CHAM` (60%) -> CHAM

MUC:
  - `binh_thuong`: chay du ngan sach.
  - `cham`: ngan sach tai x `HE_SO_CHAM` (0.33), nghi giua lan tai x3, doc_ma chi doc
    toi da `DOC_MOI_KHI_CHAM` file MOI (file cu lay tu bo nho dem - re).
  - `dung`: khong tai, khong doc; ghi `skip_reason` (dieu_phoi coi la luot bo qua, khong loi).
Tat bang `BRAIN_DIEU_TOC=tat` (vd khi do hieu nang co y).

Dung trong:
  - `tru/cau_kho.py` (CAU KHO + Telegram cong khai + truy van): tu cham/dung.
  - `dieu_phoi.py`: SEEKER/CAUKHO (nhom kham_pha, lane external/ma_nguon) KHONG khoi dong
    khi muc = `dung` (backpressure `dieu_toc_dung:<ly do>`).
  - `vong_thu_nghiem.py`: boc vong chinh trong `dang_chay("vong_thu_nghiem")`.
"""
from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
THU_MUC_DAU = LAB / "config" / "dang_backtest"

CPU_CHAM = 60.0
CPU_DUNG = 80.0
HE_SO_CHAM = 0.33
DOC_MOI_KHI_CHAM = 20
#: ten script backtest (khop trong dong lenh). QUANTLAB cua dieu_phoi KHONG nam day: no la
#: mot luot ngan, chu ky 120 s - tinh no thi SEEKER se khong bao gio duoc chay.
TEN_BACKTEST = ("vong_thu_nghiem.py", "chay_tester_kho.py", "chay_tester_z5.py",
                "quant_sweep.py", "_quet_quan_tri", "_san_4_gia_thuyet.py", "mt5_worker.py")
TEN_TESTER = ("terminal64.exe", "metatester64.exe")


def _con_song(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        try:
            import psutil
            return psutil.pid_exists(pid)
        except Exception:
            return True


def _dong_lenh_tat_ca() -> list[tuple[int, str]]:
    """(pid, dong lenh) moi tien trinh. /proc tren Linux; psutil neu co (Windows)."""
    ra = []
    proc = Path("/proc")
    if proc.is_dir():
        for p in proc.iterdir():
            if not p.name.isdigit():
                continue
            try:
                c = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "ignore")
            except OSError:
                continue
            if c.strip():
                ra.append((int(p.name), c))
        return ra
    try:
        import psutil
        for pr in psutil.process_iter(["pid", "name", "cmdline"]):
            c = " ".join(pr.info.get("cmdline") or []) or (pr.info.get("name") or "")
            ra.append((pr.info["pid"], c))
    except Exception:
        pass
    return ra


def _cpu() -> float | None:
    try:
        import psutil
        return float(psutil.cpu_percent(interval=0.3))
    except Exception:
        pass
    try:                                    # Linux khong co psutil: /proc/stat hai lan
        def doc():
            v = [int(x) for x in Path("/proc/stat").read_text().split("\n")[0].split()[1:]]
            return sum(v), v[3] + (v[4] if len(v) > 4 else 0)
        t1, r1 = doc()
        time.sleep(0.3)
        t2, r2 = doc()
        return round(100.0 * (1 - (r2 - r1) / max(1, t2 - t1)), 1)
    except Exception:
        return None


def _dau_song() -> list[dict]:
    ra = []
    if not THU_MUC_DAU.is_dir():
        return ra
    for p in THU_MUC_DAU.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            p.unlink(missing_ok=True)
            continue
        if _con_song(int(d.get("pid") or 0)):
            ra.append(d)
        else:
            p.unlink(missing_ok=True)       # dau mo coi (Ctrl-C, may sap): thu hoi
    return ra


def trang_thai(cpu: float | None = -1.0, tien_trinh=None, khoa=None) -> dict:
    """-> {muc, ly_do[], cpu}. Tham so thay duoc cho test (`cpu=None` = khong do)."""
    if os.environ.get("BRAIN_DIEU_TOC", "").lower() in ("tat", "off", "0"):
        return {"muc": "binh_thuong", "ly_do": ["BRAIN_DIEU_TOC=tat"], "cpu": None}
    dung, cham = [], []
    if khoa is None:
        try:
            from nhan import khoa_tester as KT
            khoa = []
            for p in sorted((LAB / "config").glob("khoa_tester*.json")):
                ten = None if p.stem == "khoa_tester" else p.stem[len("khoa_tester_"):]
                d = KT.dang_giu(ten)
                if d:
                    khoa.append(d)
        except Exception:
            khoa = []
    for d in khoa:
        dung.append("khoa_tester:%s" % str(d.get("viec") or d.get("pid"))[:40])
    for d in _dau_song():
        cham.append("backtest:%s" % str(d.get("viec"))[:40])
    if tien_trinh is None:
        tien_trinh = _dong_lenh_tat_ca()
    minh = os.getpid()
    for pid, c in tien_trinh:
        if pid == minh:
            continue
        thap = c.lower()
        if any(t in thap for t in TEN_TESTER):
            dung.append("tester_mt5:%d" % pid)
        elif any(t in thap for t in TEN_BACKTEST) and "pytest" not in thap:
            ten = next(t for t in TEN_BACKTEST if t in thap)
            cham.append("tien_trinh:%s:%d" % (ten, pid))
    if cpu == -1.0:
        cpu = _cpu()
    if cpu is not None:
        if cpu >= CPU_DUNG:
            dung.append("cpu_%.0f" % cpu)
        elif cpu >= CPU_CHAM:
            cham.append("cpu_%.0f" % cpu)
    muc = "dung" if dung else "cham" if cham else "binh_thuong"
    return {"muc": muc, "ly_do": list(dict.fromkeys(dung + cham))[:12], "cpu": cpu}


@contextmanager
def dang_chay(viec: str):
    """Dau 'backtest dang chay' cho tien trinh nay (SEEKER doc de cham lai). Tu xoa khi xong;
    mo coi (pid chet) duoc `_dau_song` thu hoi."""
    THU_MUC_DAU.mkdir(parents=True, exist_ok=True)
    p = THU_MUC_DAU / ("%d.json" % os.getpid())
    try:
        p.write_text(json.dumps({"pid": os.getpid(), "viec": viec, "luc": time.time(),
                                 "luc_doc": time.strftime("%Y-%m-%d %H:%M:%S")},
                                ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    try:
        yield p
    finally:
        p.unlink(missing_ok=True)


if __name__ == "__main__":
    print(json.dumps(trang_thai(), ensure_ascii=False))
