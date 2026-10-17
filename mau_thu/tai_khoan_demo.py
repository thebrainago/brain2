# -*- coding: utf-8 -*-
"""Demo GHEP NHIEU NGUON LENH tren MOT tai khoan (nhan/tai_khoan.py) bang du lieu H1 US500Cash XM co san trong repo.
Ba nguon (deu la LONG, de hieu cach ghep - khong phai de chon tham so):
  ONH : mua khi gia quay ve cham ONH sau khi nen H1 dong tren ONH (he cua chu du an, xap xi)
  ONL : mua khi gia cham ONL (dinh/day phien dem) trong phien My (he ONL DCA cu cua chu du an, xap xi)
  IBS : mua luc mo phien My sau ngay IBS<0,2 (he song sot cua brain2 vong 29)
MO PHONG H1 xap xi, 1 don vi / ro, tinh bang DIEM GIA. python mau_thu/tai_khoan_demo.py"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "mau_thu")]
import numpy as np, pandas as pd
import onh_h1 as O
from nhan import tai_khoan as TK


def nguon_onh(d):
    return [TK.LenhVao("ONH", j, e) for j, e, _H, _day in O.tim_setup(d)[0]]


def phien_dem(d):
    sess = d.ny_date + pd.to_timedelta((d.ny_h >= 18).astype(int), unit="D")
    dem = (d.ny_h >= 18) | (d.ny_h < 9)
    return d[dem].groupby(sess[dem]).high.max(), d[dem].groupby(sess[dem]).low.min()


def nguon_onl(d):
    _, onl = phien_dem(d)
    out = []
    cash = d[(d.ny_h >= 9) & (d.ny_h <= 15) & (d.ny_dow < 5)]
    for day, g in cash.groupby("ny_date"):
        if day not in onl.index:
            continue
        L = onl[day]
        for j in g.index:
            if d.low[j] <= L:
                out.append(TK.LenhVao("ONL", int(j), float(min(d.open[j], L))))
                break
    return out


def nguon_ibs(d, nguong=0.2):
    cash = d[(d.ny_h >= 9) & (d.ny_h <= 15) & (d.ny_dow < 5)]
    ngay = []
    for day, g in cash.groupby("ny_date"):
        H, L = g.high.max(), g.low.min()
        ngay.append((day, (g.close.iloc[-1] - L) / (H - L) if H > L else 0.5, g.index[0], g.iloc[0].ny_h))
    out = []
    for k in range(len(ngay) - 1):
        if ngay[k][1] < nguong and ngay[k + 1][3] == 9:
            j = int(ngay[k + 1][2])
            out.append(TK.LenhVao("IBS", j, float(d.open[j])))
    return out


def chi_so(kq, d, ten):
    nk = kq["nhat_ky"]
    t = d.t_ny
    ngay_giu = [(t[int(b.dong)] - t[int(b.sinh)]).total_seconds() / 86400 for b in nk.itertuples()]
    nam = (t.iloc[-1] - t.iloc[0]).days / 365.25
    von_xau = kq["von_xau"]; dv = kq["duong_von"]
    return dict(ten=ten, ro=len(nk), tong=kq["tong_diem"], moi_nam=kq["tong_diem"] / nam,
                tb_ro=nk.lai_diem.mean(), treo_max=-kq["treo_xau"].min(),
                sut_von=float(np.max(np.maximum.accumulate(dv) - von_xau)),
                ro_mo_max=int(kq["so_ro_mo"].max()), giu_max=max(ngay_giu), qua_5ngay=int(sum(g > 5 for g in ngay_giu)),
                go_cheo=int((nk.boi == "go_cheo").sum()), con_mo=int((nk.boi == "mo").sum()))


def in_bang(rows, tieu_de):
    print(f"\n=== {tieu_de} ===")
    print(f"{'kich ban':44s}{'so ro':>6s}{'tong(diem)':>12s}{'/nam':>8s}{'TB/ro':>7s}{'treo max':>9s}{'sut von':>9s}{'ro mo max':>10s}{'giu max(ngay)':>14s}{'ro>5ngay':>9s}{'go cheo':>8s}")
    for r in rows:
        print(f"{r['ten']:44s}{r['ro']:6d}{r['tong']:12.0f}{r['moi_nam']:8.0f}{r['tb_ro']:7.2f}{r['treo_max']:9.0f}{r['sut_von']:9.0f}{r['ro_mo_max']:10d}{r['giu_max']:14.0f}{r['qua_5ngay']:9d}{r['go_cheo']:8d}")


def chay_bo(d, nguon, tu_ngay, tieu_de, spread):
    off = int(d.index[d.t_ny >= tu_ngay][0]) if tu_ngay else 0
    b = d.iloc[off:].reset_index(drop=True)
    roll = TK.rollover_tu_ny(pd.DatetimeIndex(b.t_ny))
    def rb(ten_nguon):
        return [TK.LenhVao(e.nguon, e.chi_so - off, e.gia, e.chieu) for k in ten_nguon for e in nguon[k] if e.chi_so >= off]
    base = dict(tp_diem=5.5, spread_diem=spread)
    kb = []
    for ten, ks, ql in [
        ("ONH rieng", ["ONH"], TK.QuanLi(**base)),
        ("ONL rieng", ["ONL"], TK.QuanLi(**base)),
        ("IBS rieng", ["IBS"], TK.QuanLi(**base)),
        ("GHEP 3 nguon, khong go cheo", ["ONH", "ONL", "IBS"], TK.QuanLi(**base)),
        ("GHEP 3 nguon + GO CHEO", ["ONH", "ONL", "IBS"], TK.QuanLi(**base, go_cheo=True)),
        ("GHEP 3 + DCA 0,5%x2, khong go cheo", ["ONH", "ONL", "IBS"], TK.QuanLi(**base, dca_buoc_pct=0.005, dca_toi_da=2)),
        ("GHEP 3 + DCA 0,5%x2 + GO CHEO", ["ONH", "ONL", "IBS"], TK.QuanLi(**base, dca_buoc_pct=0.005, dca_toi_da=2, go_cheo=True)),
    ]:
        kq = TK.chay(b, rb(ks), ql, roll)
        kb.append(chi_so(kq, b, ten))
    in_bang(kb, f"{tieu_de} (TP 5,5 diem, spread {spread}, swap 5,77%/nam, 1 don vi/ro)")


if __name__ == "__main__":
    d = O.nap()
    nguon = {"ONH": nguon_onh(d), "ONL": nguon_onl(d), "IBS": nguon_ibs(d)}
    print({k: len(v) for k, v in nguon.items()}, "lenh vao 2016-2026")
    sp = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
    chay_bo(d, nguon, pd.Timestamp("2023-01-01", tz="America/New_York"), "2023-2026", sp)
    chay_bo(d, nguon, None, "2016-2026", sp)
