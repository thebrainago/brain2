# -*- coding: utf-8 -*-
"""Lich su kien vi mo tu nguon cong khai: FOMC (federalreserve.gov), NFP (quy tac thu 6 dau thang - xap xi)."""
import datetime as dt
import re
from pathlib import Path

TH = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                         "September", "October", "November", "December"])}


def fomc(thu_muc="/tmp"):
    out = set()
    for f in sorted(Path(thu_muc).glob("fomc[12]*.htm")):
        for m, d, y in re.findall(r"<h5[^>]*>\s*(\w+)\s+(?:\d+-)?(\d+)\s+Meeting - (\d{4})", f.read_text(errors="ignore")):
            if m in TH: out.add(dt.date(int(y), TH[m], int(d)))
        for m, m2, d, y in re.findall(r"<h5[^>]*>\s*(\w+)/(\w+)\s+\d+-(\d+)\s+Meeting - (\d{4})", f.read_text(errors="ignore")):
            if m2 in TH: out.add(dt.date(int(y), TH[m2], int(d)))
    s = Path(thu_muc, "fomccal.htm").read_text(errors="ignore")
    for blk in re.split(r"(\d{4}) FOMC Meetings", s)[1:]:
        pass
    parts = re.split(r">(\d{4}) FOMC Meetings<", s)
    for y, blk in zip(parts[1::2], parts[2::2]):
        for mo, d in re.findall(r'fomc-meeting__month[^>]*>(?:<strong>)?([A-Za-z/]+)(?:</strong>)?<.*?fomc-meeting__date[^>]*>([\d\-]+)', blk, re.S):
            mo = mo.split("/")[-1]
            if mo in TH and dt.date(int(y), TH[mo], int(d.split("-")[-1])) < dt.date.today():
                out.add(dt.date(int(y), TH[mo], int(d.split("-")[-1])))
    return sorted(out)


def nfp(tu=1994, den=2026):
    o = []
    for y in range(tu, den + 1):
        for m in range(1, 13):
            d = dt.date(y, m, 1)
            while d.weekday() != 4: d += dt.timedelta(days=1)
            o.append(d)
    return o


if __name__ == "__main__":
    f = fomc(); print(len(f), f[:3], f[-3:])
