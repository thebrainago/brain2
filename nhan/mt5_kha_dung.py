# -*- coding: utf-8 -*-
"""mt5_kha_dung.py - MT5 tester co dung duoc tren MAY NAY khong?

Tren box (Linux+Wine) XM thuong bi chan TLS: terminal64.exe van song nhung
VAO_CSV khong bao gio xong -> dieu_toc coi `tester_mt5:<pid>` la DUNG va
SEEKER/CAUKHO/NGHI bi treo mai (tru_dung_im). Module nay do suc khoe MT5
de dieu_toc BO QUA tin hieu tester ma khong tien, Evo bao `mt5_khong_kha_dung`,
va viec MT5 duoc danh dau HOAN cho may nha (giu hang, khong xoa).

Tin hieu (theo thu tu uu tien):
  1. `BRAIN_MT5_KHA_DUNG=0|tat|off|false` -> khong kha dung (ep)
  2. `BRAIN_MT5_KHA_DUNG=1|bat|on|true`  -> kha dung (ep)
  3. Auto: co ket qua MT5 moi trong N gio (mac dinh 6) -> kha dung;
     co tien trinh terminal/metatester nhung ket qua cu/khong co -> khong.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
KQ_ONG_DAN = LAB / "reports" / "ong_dan" / "ket_qua_mt5"
HANG_ONG_DAN = LAB / "reports" / "ong_dan" / "hang_cho_mt5.jsonl"
HANG_HOAN = LAB / "reports" / "phan_viec" / "hang_cho_mt5_hoan_may_nha.jsonl"
TRANG_THAI = LAB / "reports" / "phan_viec" / "MT5_KHA_DUNG.json"

#: Het N gio khong co file ket qua moi -> coi MT5 khong kha dung tren may nay.
GIO_KHONG_KET_QUA = float(os.environ.get("BRAIN_MT5_GIO_KHONG_KQ", "6"))
TEN_TESTER = ("terminal64.exe", "metatester64.exe")


def _env_ep() -> bool | None:
    v = (os.environ.get("BRAIN_MT5_KHA_DUNG") or "").strip().lower()
    if v in ("0", "tat", "off", "false", "no", "khong"):
        return False
    if v in ("1", "bat", "on", "true", "yes", "co"):
        return True
    return None


def _mtime_moi_nhat(thu: Path) -> float | None:
    if not thu.is_dir():
        return None
    moi = None
    try:
        for p in thu.iterdir():
            if p.name.startswith("."):
                continue
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if moi is None or m > moi:
                moi = m
    except OSError:
        return None
    return moi


def _co_tien_trinh_tester(tien_trinh=None) -> list[int]:
    """pid cac terminal/metatester dang song (doc /proc)."""
    if tien_trinh is None:
        try:
            from nhan.dieu_toc import _dong_lenh_tat_ca
            tien_trinh = _dong_lenh_tat_ca()
        except Exception:
            tien_trinh = []
    ra = []
    for pid, c in tien_trinh:
        thap = (c or "").lower()
        if any(t in thap for t in TEN_TESTER):
            ra.append(int(pid))
    return ra


def trang_thai(tien_trinh=None, bay_gio: float | None = None) -> dict:
    """-> {ok, ly_do, gio_tu_kq_moi, pid_tester[], ep_boi_env}.

    `ok=True` = MT5 tren may nay dang lam duoc viec (co ket qua moi / ep bat).
    `ok=False` = khong tin dung tester o day (TLS/XM die, ep tat, hang treo).
    """
    bay_gio = time.time() if bay_gio is None else bay_gio
    ep = _env_ep()
    pids = _co_tien_trinh_tester(tien_trinh)
    mtime = _mtime_moi_nhat(KQ_ONG_DAN)
    gio_tu = None if mtime is None else (bay_gio - mtime) / 3600.0

    if ep is False:
        return {"ok": False, "ly_do": "BRAIN_MT5_KHA_DUNG=0",
                "gio_tu_kq_moi": gio_tu, "pid_tester": pids, "ep_boi_env": True}
    if ep is True:
        return {"ok": True, "ly_do": "BRAIN_MT5_KHA_DUNG=1",
                "gio_tu_kq_moi": gio_tu, "pid_tester": pids, "ep_boi_env": True}

    # Auto
    if gio_tu is not None and gio_tu <= GIO_KHONG_KET_QUA:
        return {"ok": True,
                "ly_do": "ket_qua_mt5 moi (%.1fh < %.1fh)" % (gio_tu, GIO_KHONG_KET_QUA),
                "gio_tu_kq_moi": gio_tu, "pid_tester": pids, "ep_boi_env": False}

    if pids and (mtime is None or (gio_tu is not None and gio_tu > GIO_KHONG_KET_QUA)):
        return {"ok": False,
                "ly_do": ("tester song nhung khong co ket_qua moi "
                          "(%.1fh > %.1fh; pid=%s) — thuong TLS/XM bi chan tren box"
                          % (gio_tu if gio_tu is not None else -1,
                             GIO_KHONG_KET_QUA, ",".join(map(str, pids[:6])))),
                "gio_tu_kq_moi": gio_tu, "pid_tester": pids, "ep_boi_env": False}

    if mtime is None and not pids:
        # Chua bao gio chay MT5 o day — coi la khong kha dung (box thuong khong co XM).
        return {"ok": False, "ly_do": "chua co ket_qua_mt5 va khong co terminal",
                "gio_tu_kq_moi": None, "pid_tester": [], "ep_boi_env": False}

    # Co ket qua cu, khong con tester — van khong kha dung cho viec MOI
    return {"ok": False,
            "ly_do": "ket_qua_mt5 cu (%.1fh > %.1fh), khong co tester dang chay"
                     % (gio_tu if gio_tu is not None else -1, GIO_KHONG_KET_QUA),
            "gio_tu_kq_moi": gio_tu, "pid_tester": pids, "ep_boi_env": False}


def bo_qua_tin_hieu_tester(ly_do: list[str], tt: dict | None = None) -> list[str]:
    """Khi MT5 khong kha dung: loc bo `tester_mt5:*` khoi ly_do dieu_toc."""
    tt = tt or trang_thai()
    if tt.get("ok"):
        return list(ly_do)
    return [x for x in ly_do if not str(x).startswith("tester_mt5:")]


def danh_dau_hoan_may_nha(hang_nguon: Path | None = None,
                          hang_dich: Path | None = None,
                          gioi_han: int = 500) -> dict:
    """Chep viec dang cho trong hang MT5 sang file HOAN cho may nha.

    KHONG xoa hang nguon. Ghi de theo `ten` (viec da co giu nguyen). Tra so
    da them / tong trong file dich. Chi chay khi MT5 khong kha dung.
    """
    tt = trang_thai()
    if tt.get("ok"):
        return {"ok": True, "bo_qua": "mt5_kha_dung", "them": 0, "tong_dich": 0}

    nguon = Path(hang_nguon or HANG_ONG_DAN)
    dich = Path(hang_dich or HANG_HOAN)
    dich.parent.mkdir(parents=True, exist_ok=True)

    da: dict[str, dict] = {}
    if dich.exists():
        for line in dich.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ten = str(d.get("ten") or "")
            if ten:
                da[ten] = d

    them = 0
    if nguon.exists():
        for i, line in enumerate(nguon.read_text(encoding="utf-8").splitlines()):
            if i >= gioi_han * 20:  # doc toi da ~10k dong
                break
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ten = str(d.get("ten") or "")
            if not ten or ten in da:
                continue
            d = dict(d)
            d["hoan_may_nha"] = True
            d["hoan_luc"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            d["hoan_ly_do"] = tt.get("ly_do")
            da[ten] = d
            them += 1
            if them >= gioi_han:
                break

    # Ghi lai toan bo (giu thu tu on dinh theo ten)
    with open(dich, "w", encoding="utf-8") as f:
        for ten in sorted(da.keys()):
            f.write(json.dumps(da[ten], ensure_ascii=False, sort_keys=True) + "\n")

    TRANG_THAI.parent.mkdir(parents=True, exist_ok=True)
    TRANG_THAI.write_text(json.dumps({
        **tt, "luc": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hang_hoan": str(dich), "so_viec_hoan": len(da), "them_luot_nay": them,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": False, "them": them, "tong_dich": len(da),
            "hang_hoan": str(dich), "ly_do": tt.get("ly_do")}


if __name__ == "__main__":
    print(json.dumps(trang_thai(), ensure_ascii=False, indent=2))
