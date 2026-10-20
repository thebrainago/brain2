# -*- coding: utf-8 -*-
"""quan_ly_slot.py - SLOT, O DIA, RAM va HAI TANG LOC cho chay_lien_tuc (20/10/2026). BACKTEST, khong phai tien that.

Moi thu chinh bang BIEN MOI TRUONG (may nha bo duoc ban sua tay cua chay_lien_tuc.py):
  BRAIN_SLOTS            danh sach slot theo THU TU UU TIEN, cach nhau ';' hoac ','. Mac dinh: SSD truoc
                         (D:\\mt5_tester\\p1; C:\\mt5_tester\\p7) roi HDD E (p3; p6; p4) lam du phong.
  BRAIN_O_SSD            o dia nhanh, mac dinh "C,D". O khac (E) coi la HDD.
  BRAIN_SAN_TRONG_GB     san cho trong o SSD (mac dinh 6). Duoi san -> don theo bac slot dang ranh; van thieu -> bo slot,
                         viec sang slot E.
  BRAIN_SAN_TRONG_HDD_GB san cho o HDD (mac dinh 3).
  BRAIN_RAM_MIN_GB       khong phong viec khi RAM con trong < muc nay (mac dinh 4; may nha 1 thanh 32 GB, moi
                         metatester real tick an 5-6,5 GB).
  BRAIN_RAM_TANG2_GB     viec real tick (tang 2) can them: RAM trong >= muc nay (mac dinh 6).
  BRAIN_HAI_TANG         "1" (mac dinh) bat loc hai tang cho viec ong dan; "0" tat (moi viec real tick nhu cu).
  BRAIN_TANG1_MODEL      Model tester tang 1: 1 = OHLC M1 (mac dinh), 2 = gia mo nen.
  BRAIN_TANG1_SLOT       so viec dong thoi toi da (ca hai tang) khi co viec tang 1 (mac dinh 5).
  BRAIN_TANG2_SLOT       so viec real tick dong thoi toi da (mac dinh 3).
  BRAIN_TANG1_DD_MAX     tang 1 truot neu sut giam > muc nay % (mac dinh 95) ...
  BRAIN_TANG1_NET_MIN    ... hoac lai rong < muc nay (mac dinh 0, tien te tai khoan).
  BRAIN_LANH_DIR         noi chuyen bao cao .htm DA DOC cua phien truoc (mac dinh E:\\lanh_tu_D\\rep).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import time
from pathlib import Path

SLOT_MAC_DINH = [r"D:\mt5_tester\p1", r"C:\mt5_tester\p7", r"E:\mt5_tester\p3", r"E:\mt5_tester\p6", r"E:\mt5_tester\p4"]


def _f(ten: str, md: float) -> float:
    try:
        return float(os.environ.get(ten, "") or md)
    except ValueError:
        return md


def ds_slot() -> list[str]:
    x = os.environ.get("BRAIN_SLOTS", "").strip()
    if not x:
        return list(SLOT_MAC_DINH)
    return [s.strip() for s in re.split(r"[;,]", x) if s.strip()]


def o_cua(slot: str) -> str:
    """'D:\\mt5_tester\\p1' -> 'D'. Duong dan POSIX (test) -> ''."""
    m = re.match(r"^([A-Za-z]):", str(slot))
    return m.group(1).upper() if m else ""


def la_ssd(slot: str) -> bool:
    o = os.environ.get("BRAIN_O_SSD", "C,D")
    return o_cua(slot) in {x.strip().upper() for x in re.split(r"[;,]", o) if x.strip()}


def san_trong(slot: str) -> float:
    return _f("BRAIN_SAN_TRONG_GB", 6.0) if la_ssd(slot) else _f("BRAIN_SAN_TRONG_HDD_GB", 3.0)


def goc_o(slot: str) -> str:
    o = o_cua(slot)
    return (o + ":\\") if o else str(Path(slot).anchor or "/")


def trong_gb(slot: str, disk_usage=shutil.disk_usage) -> float:
    try:
        return disk_usage(goc_o(slot)).free / 1024 ** 3
    except Exception:
        return float("inf")          # khong do duoc -> khong chan (ghi log o noi goi)


#: Bac don cache slot DANG RANH: (ten, cac mau glob tuong doi slot). Bac sau ton thoi gian tai lai hon bac truoc.
BAC_DON = [
    ("log_va_cache", ["logs/*", "Tester/logs/*", "MQL5/Logs/*", "Tester/Agent-*/logs/*", "Tester/cache/*",
                      "Tester/Agent-*/temp/*", "Tester/Agent-*/MQL5/Files/*"]),
    ("tick", ["bases/*/ticks", "Tester/Agent-*/bases/*/ticks"]),
    ("lich_su", ["bases/*/history", "Tester/Agent-*/bases/*/history"]),
]


def _xoa(p: Path) -> int:
    try:
        if p.is_dir():
            n = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            shutil.rmtree(p, ignore_errors=True)
            return n
        n = p.stat().st_size
        p.unlink()
        return n
    except Exception:
        return 0


def don_bac(slot: str, bac: int) -> int:
    """Xoa mot bac cache cua MOT slot (slot phai dang ranh). -> so byte da xoa."""
    n = 0
    for mau in BAC_DON[bac][1]:
        for p in Path(slot).glob(mau):
            n += _xoa(p)
    return n


def dam_bao_cho(slot: str, ranh: list[str], log=print, disk_usage=shutil.disk_usage) -> bool:
    """Truoc khi phong viec tren `slot`: o cua slot du san trong? Khong du -> don theo bac cac slot DANG RANH cung o
    (log/cache -> tick -> lich su), kiem lai sau moi bac. Van thieu -> False (bo slot nay, viec sang slot khac/E)."""
    san = san_trong(slot)
    if trong_gb(slot, disk_usage) >= san:
        return True
    cung_o = [s for s in ranh if o_cua(s) == o_cua(slot)] or [slot]
    for b in range(len(BAC_DON)):
        n = sum(don_bac(s, b) for s in cung_o)
        con = trong_gb(slot, disk_usage)
        log("DON O %s bac %s (%d slot ranh): xoa %.2f GB, con %.1f GB (san %.0f)" % (
            o_cua(slot) or "?", BAC_DON[b][0], len(cung_o), n / 1024 ** 3, con, san))
        if con >= san:
            return True
    return False


def don_sau_viec(slot: str, ten: str, common: Path | None = None, csv_vao: str | None = None) -> int:
    """Sau khi KET QUA DA CHEP ve reports/ong_dan/ket_qua_mt5: xoa file lam viec cua viec `ten` (ini, set, bao cao con sot,
    CSV vao/ra trong Common\\Files) + log/cache tester cua slot. KHONG dung tick / lich su (lan sau can)."""
    n = 0
    for p in [Path(slot, ten + ".ini"), Path(slot, "MQL5", "Profiles", "Tester", ten + ".set"),
              Path(slot, ten + ".htm"), Path(slot, ten + ".xml")] + list(Path(slot).glob(ten + "*.png")):
        if p.exists():
            n += _xoa(p)
    if common is not None and csv_vao:
        ten_csv = Path(str(csv_vao).replace("\\", "/")).name
        for duoi in ("", "_lenh_mt5.csv", "_gia.csv"):
            p = Path(common, ten_csv + duoi)
            if p.exists():
                n += _xoa(p)
    n += don_bac(slot, 0)
    return n


def ram_trong_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / 1024 ** 3
    except Exception:
        return float("inf")


def du_ram(tang: int, ram: float | None = None) -> tuple[bool, str]:
    ram = ram_trong_gb() if ram is None else ram
    can = _f("BRAIN_RAM_MIN_GB", 4.0)
    if tang != 1:
        can = max(can, _f("BRAIN_RAM_TANG2_GB", 6.0))
    return (ram >= can, "RAM trong %.1f GB %s %.1f GB (tang %d)" % (ram, ">=" if ram >= can else "<", can, tang))


def hai_tang() -> bool:
    return os.environ.get("BRAIN_HAI_TANG", "1").strip() not in ("0", "", "false", "False")


def model_tang1() -> int:
    return int(_f("BRAIN_TANG1_MODEL", 1))


MUC_MT5 = Path(__file__).resolve().parent.parent / "data" / "dieu_phoi" / "muc_mt5.json"


def muc_dieu_phoi(p: Path | None = None, tuoi_giay: float = 600) -> dict | None:
    """Muc slot do may_nha_toi_nay/dieu_phoi_may_nha.py ghi (RAM / game). Cu hon tuoi_giay hoac khong co -> None."""
    p = Path(os.environ.get("BRAIN_MUC_MT5") or p or MUC_MT5)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if time.time() - float(d.get("ts") or 0) <= tuoi_giay else None
    except (OSError, ValueError):
        return None


def slot_toi_da(co_tang1: bool, muc: dict | None = None) -> tuple[int, int]:
    """-> (tong viec dong thoi toi da, viec real tick toi da). Bo dieu phoi con song -> lay muc cua no (nho hon)."""
    t2 = int(_f("BRAIN_TANG2_SLOT", 3))
    tong = max(t2, int(_f("BRAIN_TANG1_SLOT", 5))) if co_tang1 else t2
    muc = muc_dieu_phoi() if muc is None else muc
    if muc:
        t2 = min(t2, int(muc.get("tang2", t2)))
        tong = min(tong, int(muc.get("tong", tong)))
        if not co_tang1:
            tong = min(tong, t2)          # khong co tang 1 thi moi viec la real tick
    return tong, t2


def _dd_pct(dd) -> float | None:
    m = re.search(r"\(([\d.]+)%\)", str(dd or ""))
    if m:
        return float(m.group(1))
    try:
        return float(dd)
    except (TypeError, ValueError):
        return None


def phan_xu_tang1(r: dict) -> tuple[bool, str]:
    """Ket qua tang 1 (OHLC M1 / gia mo) -> (qua, ly do). Truot: sut giam > DD_MAX hoac lai rong < NET_MIN.
    Thieu so -> KHONG loai (cho qua tang 2, ghi ro)."""
    dd = _dd_pct(r.get("dd"))
    net = r.get("net")
    dd_max, net_min = _f("BRAIN_TANG1_DD_MAX", 95.0), _f("BRAIN_TANG1_NET_MIN", 0.0)
    if net is None or dd is None:
        return True, "tang 1 thieu so (net=%s dd=%s) -> cho qua tang 2" % (net, r.get("dd"))
    if dd > dd_max:
        return False, "tang 1 TRUOT: sut giam %.2f%% > %.0f%%" % (dd, dd_max)
    if net < net_min:
        return False, "tang 1 TRUOT: lai rong %.2f < %.2f" % (net, net_min)
    return True, "tang 1 QUA: net %.2f, sut giam %.2f%%" % (net, dd)


def chuyen_bao_cao_cu(rep: Path, lanh: Path | None = None, truoc: float | None = None, log=print) -> int:
    """Bao cao .htm/.xml DA DOC trong `rep` cu hon dau phien (`truoc`) -> chuyen sang o HDD (BRAIN_LANH_DIR)."""
    lanh = Path(lanh or os.environ.get("BRAIN_LANH_DIR") or r"E:\lanh_tu_D\rep")
    truoc = time.time() if truoc is None else truoc
    if not Path(rep).exists():
        return 0
    n = 0
    for f in list(Path(rep).glob("*.htm")) + list(Path(rep).glob("*.xml")) + list(Path(rep).glob("*.png")):
        try:
            if f.stat().st_mtime >= truoc:
                continue
            lanh.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(lanh / f.name))
            n += 1
        except Exception as e:  # noqa: BLE001
            log("CHUYEN loi %s: %s" % (f.name, e))
    if n:
        log("CHUYEN %d bao cao cu %s -> %s" % (n, rep, lanh))
    return n
