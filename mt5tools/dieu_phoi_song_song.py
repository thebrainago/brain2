# -*- coding: utf-8 -*-
"""dieu_phoi_song_song.py - DIEU PHOI MAY NHA + BOX chay song song (vong 27, 13/10/2026). Xem tai_lieu/DIEU_PHOI.md.

4 muc: MAX (~90% CPU, 4 MT5, cao + phan tich), CAO, VUA, THAP (chu du an choi game / dung may: toi thieu).
Muc tu chon theo: tien trinh game dang chay + cua so truoc toan man hinh + CPU nen (khong tinh viec cua ta).
Chi DOC trang thai may (psutil); khong doi cai dat Windows. Tren box (Linux) luon tra 'MAX' cho lan Python.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, asdict

GAME = {"valorant-win64-shipping.exe", "valorant.exe", "league of legends.exe", "leagueclientux.exe",
        "cs2.exe", "dota2.exe", "gta5.exe", "fortniteclient-win64-shipping.exe", "r5apex.exe",
        "overwatch.exe", "pubg-win64-shipping.exe", "eldenring.exe", "genshinimpact.exe"}
# RiotClientServices / launcher dang mo KHONG tinh la dang choi (chi game that).
CUA_TA = ("mt5_tester", "metatester64", "seeker_doc", "dieu_phoi")


@dataclass(frozen=True)
class Muc:
    ten: str
    tran_cpu: int      # % CPU ca may muc tieu
    mt5: int           # so terminal MT5 song song
    cao: int           # so tab trinh duyet cao song song
    python: int        # so tien trinh phan tich Python
    uu_tien: str       # lop uu tien Windows cho tien trinh cua ta


MUC = {
    "MAX": Muc("MAX", 90, 4, 3, 8, "BelowNormal"),
    "CAO": Muc("CAO", 75, 3, 2, 6, "BelowNormal"),
    "VUA": Muc("VUA", 50, 2, 1, 3, "Idle"),
    "THAP": Muc("THAP", 15, 0, 0, 1, "Idle"),
}


def chon_muc(game: bool, toan_man_hinh: bool, cpu_nguoi_dung: float, ep: str | None = None) -> str:
    """cpu_nguoi_dung = % CPU ca may TRU tien trinh cua ta."""
    if ep in MUC:
        return ep
    if game or toan_man_hinh:
        return "THAP"
    if cpu_nguoi_dung >= 40:
        return "VUA"
    if cpu_nguoi_dung >= 15:
        return "CAO"
    return "MAX"


def phan_viec(muc: str) -> dict:
    """Chia viec giua may nha va box theo muc."""
    m = MUC[muc]
    return {"may_nha": {"mt5": m.mt5, "cao_nguon_bi_chan_hoac_dang_nhap": m.cao, "python": m.python},
            "box": {"python": 8, "cao_nguon_cong_khai": 2, "phan_tich_bao_cao_mt5": True}}


def _toan_man_hinh() -> bool:
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        h = u.GetForegroundWindow()
        if not h or h in (u.GetDesktopWindow(), u.GetShellWindow()):
            return False
        r = wintypes.RECT(); u.GetWindowRect(h, ctypes.byref(r))
        return (r.right - r.left) >= u.GetSystemMetrics(0) and (r.bottom - r.top) >= u.GetSystemMetrics(1)
    except Exception:
        return False


def do_may(giay: float = 2.0) -> dict:
    import psutil
    procs = list(psutil.process_iter(["name", "cmdline"]))
    for p in procs:
        try: p.cpu_percent(None)
        except Exception: pass
    time.sleep(giay)
    tong = cua_ta = 0.0; game = False
    for p in procs:
        try:
            c = p.cpu_percent(None); ten = (p.info["name"] or "").lower(); cmd = " ".join(p.info["cmdline"] or []).lower()
        except Exception:
            continue
        tong += c
        if ten in GAME: game = True
        if any(k in cmd or k in ten for k in CUA_TA): cua_ta += c
    n = psutil.cpu_count() or 1
    return {"game": game, "toan_man_hinh": _toan_man_hinh() if sys.platform == "win32" else False,
            "cpu_nguoi_dung": round(max(0.0, tong - cua_ta) / n, 1), "cpu_cua_ta": round(cua_ta / n, 1)}


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    ep = a[0].upper() if a else None
    d = do_may() if sys.platform == "win32" else {"game": False, "toan_man_hinh": False, "cpu_nguoi_dung": 0.0, "cpu_cua_ta": 0.0}
    m = chon_muc(d["game"], d["toan_man_hinh"], d["cpu_nguoi_dung"], ep)
    print(json.dumps({"muc": m, "do": d, "cau_hinh": asdict(MUC[m]), "phan_viec": phan_viec(m)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ---- noi voi sinh_viec (13/10 toi): hang doi khong bao gio can --------------------------------
def so_slot_mt5(muc: str, toi_da: int = 4) -> int:
    """So terminal MT5 duoc chay theo muc (MAX=4 ... THAP=0)."""
    return min(toi_da, MUC[muc].mt5)


def viec_tiep(n: int, dang_chay: set | None = None) -> list:
    """Hang doi rong -> sinh viec moi tu sinh_viec.py (near-miss, luoi, ma moi, khung moi)."""
    import sinh_viec as SV
    return SV.lay_viec(n, dang_chay=dang_chay)
