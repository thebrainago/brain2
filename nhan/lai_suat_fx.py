# -*- coding: utf-8 -*-
"""lai_suat_fx.py - CHENH LAI SUAT QUA DEM theo THANG cho phi qua dem DUNG THOI KY (P3, 11/10/2026).

Van de (GHI_CHU muc "Vấn đề mở" 6): phi qua dem = bang swap HOM NAY cua san, ap cho ca
2003-2021. Swap FX that = chenh lai suat qua dem cua hai dong tien (thay doi theo thoi ky:
2003-05 EUR > USD -> MUA EURUSD duoc NHAN; 2009-15 ca hai ~0; 2017-19 USD > EUR ~2,5 %)
+ phi cong them (markup) cua san.

Mo hinh (`chi_phi.MoHinhChiPhi.chenh_lai_suat`):
    d(t)      = lai_suat(dong tien YET GIA, thang t) - lai_suat(dong tien CO SO, thang t)
    phi_mua(t)= d(t) + markup_mua      phi_ban(t) = -d(t) + markup_ban
    markup lay tu swap DO tren san hom nay: markup_mua = phi_mua_san - d(thang do),
    markup_ban = phi_ban_san + d(thang do). GIA DINH: markup cua san khong doi theo thoi gian
    (XM 09/2026 cho markup ~1,0 %/nam MOI chieu - doi xung, hop ly; truoc 2026 CHUA DO DUOC).
Bang: config/lai_suat_qua_dem_thang.csv (hieu_chuan/p3_lai_suat.py, FRED cong khai).
Cap co dong tien khong co trong bang -> None (khong doan; goi giu phi hom nay + canh bao).
"""
from __future__ import annotations

import csv
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
BANG = GOC / "config" / "lai_suat_qua_dem_thang.csv"
_CACHE: dict = {}


def doc_bang(p: Path = BANG) -> dict[str, dict[str, float]]:
    """{dong_tien: {"YYYY-MM": ti_le/nam}} (da chia 100)."""
    k = str(p)
    if k in _CACHE:
        return _CACHE[k]
    ra: dict[str, dict[str, float]] = {}
    if p.exists():
        with p.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            tien = [c for c in (r.fieldnames or []) if c.isupper() and len(c) == 3]
            for dong in r:
                for t in tien:
                    v = dong.get(t)
                    if v not in (None, ""):
                        ra.setdefault(t, {})[dong["thang"]] = float(v) / 100.0
    _CACHE[k] = ra
    return ra


def tach_cap(ma: str) -> tuple[str, str] | None:
    m = "".join(ch for ch in ma.upper() if ch.isalpha())
    if len(m) < 6:
        return None
    return m[:3], m[3:6]


def chenh_thang(ma: str, p: Path = BANG) -> dict[str, float] | None:
    """{"YYYY-MM": d} voi d = r(yet gia) - r(co so); None neu thieu mot dong tien."""
    cap = tach_cap(ma)
    if cap is None:
        return None
    b = doc_bang(p)
    co_so, yet = b.get(cap[0]), b.get(cap[1])
    if not co_so or not yet:
        return None
    return {t: yet[t] - co_so[t] for t in sorted(set(co_so) & set(yet))}


def tra_cuu(chenh: dict[str, float], thang: str) -> float:
    """Gia tri thang `thang`; ngoai bang -> thang gan nhat (dau/cuoi bang)."""
    if thang in chenh:
        return chenh[thang]
    ks = sorted(chenh)
    return chenh[ks[0]] if thang < ks[0] else chenh[ks[-1]]
