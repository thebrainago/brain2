# -*- coding: utf-8 -*-
"""Ban Python DONG LOGIC voi hai EA demo (BRAIN_IBS_Demo.mq5, BRAIN_MuaVu_SPX.mq5) - de kiem tuong duong."""
from __future__ import annotations

import datetime as dt


def la_ngay_thuong(d: dt.date) -> bool:
    return d.weekday() < 5


def ngay_thuong_ke(d: dt.date) -> dt.date:
    x = d + dt.timedelta(days=1)
    while not la_ngay_thuong(x):
        x += dt.timedelta(days=1)
    return x


def vi_tri_trong_thang(d: dt.date) -> tuple[int, int]:
    x = d.replace(day=1); tt = cl = 0
    while x.month == d.month:
        if la_ngay_thuong(x):
            if x <= d: tt += 1
            else: cl += 1
        x += dt.timedelta(days=1)
    return tt, cl


def so_quy_tac_bat(d: dt.date, dct=True, santa=True, hw=True, n3=True) -> int:
    tt, cl = vi_tri_trong_thang(d); n = 0
    if n3 and d.year % 4 == 3: n += 1
    if hw and (d.month >= 11 or d.month <= 4): n += 1
    if dct and (cl == 0 or tt <= 3): n += 1
    if santa and ((d.month == 12 and cl <= 4) or (d.month == 1 and tt <= 2)): n += 1
    return n


def ibs_tin(h: float, l: float, c: float, nguong=0.2):
    if h - l <= 0:
        return None
    return (c - l) / (h - l) < nguong
