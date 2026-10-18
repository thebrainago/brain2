# -*- coding: utf-8 -*-
"""an_toan_tester.py - ba cai bay cua MT5 tester ma launcher mt5tools tung dinh (ra soat 18/10/2026).

1. DON BAY: `Leverage=30` trong .ini bi tester LANG LE bo qua -> 58/58 bao cao that ghi "Leverage: 1:100".
   Phai viet `Leverage=1:30`. `dong_don_bay()` sinh dong dung; `kiem_don_bay()` doc lai tu bao cao.
2. BAO CAO CU: ten bao cao co dinh va file cu khong bi xoa -> mot lan chay hong doc lai ket qua LAN TRUOC.
   `xoa_bao_cao_cu()` truoc khi chay, `bao_cao_moi()` sau khi chay (ton tai VA moi hon luc bat dau).
3. .ex5 CU: MetaEditor thoat TRUOC khi bien dich xong, va kiem "co .ex5" thi lan bien dich hong van chay ban
   CU. `bien_dich()` doi .ex5 MOI HON ban truoc (cung cach `chay_tester_kho.bien_dich`).
Moi ket qua khong qua duoc mot trong ba thu tren la CHUA_DO_DUOC, khong phai AM.
"""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path


def dong_don_bay(don_bay: int) -> str:
    """Dong .ini dung dinh dang MT5 ("1:N"). So tran -> tester bo qua va dung 1:100."""
    return "Leverage=1:%d\n" % int(don_bay)


def kiem_don_bay(chuoi_bao_cao: str | None, don_bay: int) -> str:
    """'' neu bao cao ghi dung don bay da dat; khong thi chuoi canh bao (vd 'bao cao 1:100, dat 1:30')."""
    m = re.search(r"1\s*:\s*(\d+)", str(chuoi_bao_cao or ""))
    if m is None:
        return "khong doc duoc don bay trong bao cao"
    return "" if int(m.group(1)) == int(don_bay) else "bao cao 1:%s, dat 1:%d" % (m.group(1), int(don_bay))


def xoa_bao_cao_cu(slot: Path, ten: str) -> None:
    for duoi in (".htm", ".html", ".png", "-holding.png", "-hst.png", "-mfemae.png"):
        try:
            (Path(slot) / (ten + duoi)).unlink()
        except FileNotFoundError:
            pass


def bao_cao_moi(f: Path, t0: float) -> bool:
    """Bao cao ton tai VA viet SAU luc bat dau chay (dung sai 2 s cho dong ho file)."""
    f = Path(f)
    return f.exists() and f.stat().st_mtime >= t0 - 2.0


def bien_dich(me: Path, mq: Path, cho_giay: int = 180) -> str:
    """Bien dich `mq` bang MetaEditor `me`; tra '' khi .ex5 MOI HON ban truoc, khong thi chuoi loi.

    Khong tin exit code (MetaEditor tra 1 ca khi thanh cong) va khong tin "co .ex5" (ban cu van nam do)."""
    mq, ex5 = Path(mq), Path(mq).with_suffix(".ex5")
    cu = ex5.stat().st_mtime if ex5.exists() else 0.0
    log = mq.with_suffix(".log")
    subprocess.Popen([str(me), "/portable", "/compile:" + mq.name, "/log:" + log.name], cwd=str(mq.parent),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    het = time.time() + cho_giay
    while time.time() < het:
        if ex5.exists() and ex5.stat().st_mtime > cu:
            return ""
        time.sleep(1.0)
    try:
        duoi = log.read_bytes().decode("utf-16", errors="ignore")[-400:]
    except OSError:
        duoi = "khong co log"
    return "bien dich hong hoac qua %ds (.ex5 khong moi hon ban cu): %s" % (cho_giay, duoi.strip())


def phan_xu_ket_qua(r: dict, giay: float, giay_toi_thieu: float = 60.0) -> str:
    """'' = ket qua do duoc; khong thi ly do CHUA_DO_DUOC.

    Do 18/10: mot lan chay 20 s, chat luong 0 %, 0 lenh duoc ghi nhu ket qua that -> bien the bi coi la
    'da thu, khong lai' vinh vien. Bao cao doc khong ra so (nhan khac ngon ngu...) cung vay."""
    if r.get("net") is None or r.get("lenh") is None:
        return "khong_doc_duoc_bao_cao"
    if (r.get("lenh") or 0) == 0 and giay < giay_toi_thieu:
        return "chua_do_duoc_0_lenh_%ds" % int(giay)
    return ""
