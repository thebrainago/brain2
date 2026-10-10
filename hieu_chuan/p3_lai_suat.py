# -*- coding: utf-8 -*-
"""P3 (11/10/2026): dung bang LAI SUAT QUA DEM theo THANG cho phi qua dem dung thoi ky.

Nguon (FRED, cong khai, 0 dong - tai CSV `fredgraph.csv?id=<SERI>`):
  USD: DFF            Fed Funds hieu luc, hang ngay -> trung binh thang.
  EUR: IRSTCI01EZM156N lai suat qua dem (call money, ~EONIA/EURSTR), hang thang (OECD).
       Sau thang cuoi cua seri nay: ECBDFR (lai suat tien gui ECB, hang ngay -> TB thang)
       + chenh lech TB (call money - ECBDFR) cua 12 thang chong nhau cuoi cung (ghi o cot nguon).
Ghi: config/lai_suat_qua_dem_thang.csv (thang, USD, EUR, nguon_EUR) - % / nam.

    python hieu_chuan/p3_lai_suat.py [thu_muc_csv_fred]   # thieu file -> tai tu FRED
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import pandas as pd

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "config" / "lai_suat_qua_dem_thang.csv"
SERI = ("DFF", "IRSTCI01EZM156N", "ECBDFR")


def _doc(thu_muc: Path, s: str) -> pd.Series:
    p = thu_muc / f"{s}.csv"
    if not p.exists():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
        p.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    d = pd.read_csv(p)
    d.columns = ["t", "v"]
    d["t"] = pd.to_datetime(d["t"])
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    return d.set_index("t")["v"].dropna()


def dung(thu_muc: Path) -> pd.DataFrame:
    usd = _doc(thu_muc, "DFF").resample("MS").mean()
    cm = _doc(thu_muc, "IRSTCI01EZM156N").resample("MS").mean()
    dfr = _doc(thu_muc, "ECBDFR").resample("MS").mean()
    chung = pd.concat([cm, dfr], axis=1, keys=["cm", "dfr"]).dropna().tail(12)
    lech = float((chung["cm"] - chung["dfr"]).mean())
    eur = cm.copy()
    nguon = pd.Series("IRSTCI01EZM156N", index=cm.index)
    sau = dfr[dfr.index > cm.index.max()]
    eur = pd.concat([eur, sau + lech])
    nguon = pd.concat([nguon, pd.Series(f"ECBDFR{lech:+.3f}", index=sau.index)])
    bang = pd.DataFrame({"USD": usd, "EUR": eur, "nguon_EUR": nguon}).dropna()
    bang = bang[bang.index >= "1999-01-01"]
    bang.index = bang.index.strftime("%Y-%m")
    bang.index.name = "thang"
    return bang.round(4)


if __name__ == "__main__":
    tm = Path(sys.argv[1]) if len(sys.argv) > 1 else GOC / "data" / "fred_tam"
    tm.mkdir(parents=True, exist_ok=True)
    b = dung(tm)
    tam = RA.with_suffix(".tmp")
    b.to_csv(tam)
    tam.replace(RA)
    print(f"Da ghi {RA} ({len(b)} thang, {b.index[0]}..{b.index[-1]})")
