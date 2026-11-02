# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json
from pathlib import Path
from . import doc_lich_su as DL, phan_tich as PT, dac_trung as DT, the_chien_luoc as TC


def chay(lich_su, gia=None, nguon_url="file://local", tai_khoan="khong_ro"):
    df = DL.doc(lich_su)
    kq = {"tong_quat": PT.tong_quat(df)}
    if gia is not None:
        sym = df["symbol"].mode()[0]; p = PT.pip(sym)
        g = DT.doc_gia(gia); f = DT.chi_bao(g, p)
        dau = PT.ro(df).sort_values("mo_luc").groupby("ro").head(1)        # chỉ lệnh ĐẦU rổ = quyết định vào
        dau = dau[(dau.symbol == sym) & (dau.mo_luc >= g.index[60]) & (dau.mo_luc <= g.index[-1])]
        kq["phan_biet"] = DT.phan_biet(f.loc[g.index[60]:], dau["mo_luc"]) if len(dau) >= 10 else None
        kq["buoc_luoi_atr"] = DT.buoc_luoi_atr(df[df.symbol == sym], f, p)
    else:
        kq["phan_biet"] = None; kq["buoc_luoi_atr"] = None
    ls, the = TC.tao(df, kq, nguon_url, tai_khoan)
    return kq, ls, the


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--lich-su", required=True); ap.add_argument("--gia")
    ap.add_argument("--ra", default="data/dich_nguoc"); ap.add_argument("--url", default="file://local"); ap.add_argument("--ten", default="khong_ro")
    a = ap.parse_args()
    kq, ls, the = chay(a.lich_su, a.gia, a.url, a.ten)
    ra = Path(a.ra); ra.mkdir(parents=True, exist_ok=True)
    (ra / f"{a.ten}_lich_su.json").write_text(ls.to_json(), encoding="utf-8")
    (ra / f"{a.ten}_the.json").write_text(the.to_json(), encoding="utf-8")
    print(json.dumps(kq, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
