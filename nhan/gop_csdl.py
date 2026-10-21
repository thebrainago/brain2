# -*- coding: utf-8 -*-
"""gop_csdl.py - GOP (khong ghi de) CSDL trang thai ong dan + cache dich LLM giua box va may nha (20/10/2026).

Truoc day goi_may_nha.py dat ban chup trang_thai.sqlite cua box vao data/ong_dan/trang_thai.sqlite trong zip, may nha
giai nen la GHI DE -> mat trang thai DAT cua cac lan dich tren may nha (36 ma da DAT bi tra tien dich lai 20/10).
Cache dich (data/ong_dan/dich_llm/<hash>.json) cung bi ghi de bang ban cu hon cua box.

Nay goi dat ban chup vao data/ong_dan/goi_vao/ (trang_thai_box.sqlite, tho_box.sqlite, dich_llm/*.json) va may nha chay
`python -m nhan.gop_csdl --nhap-goi` sau khi giai nen. Luat gop moi the:
  1. KHONG BAO GIO ha cap the da DAT dich_llm (ben nao co dich_llm.trang_thai == DAT thang ben khong co).
  2. Sau do: buoc tien xa hon (ong_dan.BUOC) thang; cung buoc -> cap_nhat moi hon thang; hoa -> giu ben dich.
nhat_ky: hop hai ben (bo trung). thu / to_hop: hop, trung khoa -> giu ben dich.
Cache dich: giu ban dich tru khi ban nguon OK con ban dich khong OK, hoac ban nguon moi hon (luc) va khong lam mat ma
(spec/python); hong_theo_model hop hai ben. Truoc khi gop: sao luu CSDL dich (*.truoc_gop_<luc>.sqlite).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TT = GOC / "data" / "ong_dan" / "trang_thai.sqlite"
GOI_VAO = GOC / "data" / "ong_dan" / "goi_vao"
CACHE = GOC / "data" / "ong_dan" / "dich_llm"


def _buoc_idx(b: str) -> int:
    from nhan import ong_dan as OD
    try:
        return OD.BUOC.index(b)
    except ValueError:
        return -1


def _dat(js: str | None) -> bool:
    try:
        return ((json.loads(js or "{}").get("dich_llm") or {}).get("trang_thai")) == "DAT"
    except ValueError:
        return False


def _hang(r: tuple) -> tuple:
    """r = (id, json, loai, uu_tien, duong, buoc, trang_thai, kq, cap_nhat) -> khoa so sanh (lon hon = thang)."""
    return (_dat(r[1]), _buoc_idx(r[5] or ""), str(r[8] or ""))


def gop_db(dich: Path, nguon: Path, sao_luu: bool = True) -> dict:
    """Gop CSDL `nguon` vao `dich` (tao bang neu thieu). -> dem."""
    from nhan import ong_dan as OD
    dich, nguon = Path(dich), Path(nguon)
    dem = {"nguon": str(nguon), "the_moi": 0, "the_thay": 0, "the_giu": 0, "giu_vi_dat": 0, "nhat_ky_them": 0,
           "thu_them": 0, "to_hop_them": 0}
    if not nguon.exists():
        dem["loi"] = "khong co nguon"
        return dem
    if sao_luu and dich.exists():
        bk = dich.with_name(dich.stem + ".truoc_gop_%s.sqlite" % time.strftime("%Y%m%d_%H%M%S"))
        s = sqlite3.connect(str(dich)); b = sqlite3.connect(str(bk))
        with b:
            s.backup(b)
        s.close(); b.close()
        dem["sao_luu"] = str(bk)
    cn = OD._db(dich)                                   # tao bang neu chua co
    src = sqlite3.connect("file:%s?mode=ro" % nguon.as_posix(), uri=True)
    cot = "id, json, loai, uu_tien, duong, buoc, trang_thai, kq, cap_nhat"
    with cn:
        for r in src.execute("SELECT %s FROM the" % cot):
            cu = cn.execute("SELECT %s FROM the WHERE id=?" % cot, (r[0],)).fetchone()
            if cu is None:
                cn.execute("INSERT INTO the (%s) VALUES (?,?,?,?,?,?,?,?,?)" % cot, r)
                dem["the_moi"] += 1
            elif _hang(r) > _hang(cu):
                cn.execute("UPDATE the SET json=?, loai=?, uu_tien=?, duong=?, buoc=?, trang_thai=?, kq=?, cap_nhat=? "
                           "WHERE id=?", r[1:] + (r[0],))
                dem["the_thay"] += 1
            else:
                dem["the_giu"] += 1
                if _dat(cu[1]) and not _dat(r[1]):
                    dem["giu_vi_dat"] += 1
        co = {tuple(x) for x in cn.execute("SELECT luc, buoc, the_id, ghi FROM nhat_ky")}
        for x in src.execute("SELECT luc, buoc, the_id, ghi FROM nhat_ky"):
            if tuple(x) not in co:
                cn.execute("INSERT INTO nhat_ky VALUES (?,?,?,?)", x)
                co.add(tuple(x))
                dem["nhat_ky_them"] += 1
        bang = {x[0] for x in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "thu" in bang:
            for x in src.execute("SELECT the_id, khoa, json FROM thu"):
                dem["thu_them"] += cn.execute("INSERT OR IGNORE INTO thu VALUES (?,?,?)", x).rowcount
        if "to_hop" in bang:
            for x in src.execute("SELECT khoa, json FROM to_hop"):
                dem["to_hop_them"] += cn.execute("INSERT OR IGNORE INTO to_hop VALUES (?,?)", x).rowcount
    src.close(); cn.close()
    return dem


def _co_ma(d: dict) -> bool:
    return bool(d.get("spec") or (d.get("python") or "").strip())


def gop_cache(dich: Path, nguon: Path) -> dict:
    """Gop thu muc cache dich LLM `nguon` vao `dich` theo luat o dau tep."""
    dich, nguon = Path(dich), Path(nguon)
    dem = {"cache_moi": 0, "cache_thay": 0, "cache_giu": 0}
    if not nguon.is_dir():
        return dem
    dich.mkdir(parents=True, exist_ok=True)
    for f in sorted(nguon.glob("*.json")):
        try:
            dn = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        g = dich / f.name
        if not g.exists():
            shutil.copy2(f, g); dem["cache_moi"] += 1
            continue
        try:
            dd = json.loads(g.read_text(encoding="utf-8"))
        except ValueError:
            shutil.copy2(f, g); dem["cache_thay"] += 1
            continue
        ok_n, ok_d = dn.get("trang_thai") == "OK", dd.get("trang_thai") == "OK"
        thay = (ok_n and not ok_d) or (ok_n == ok_d and str(dn.get("luc") or "") > str(dd.get("luc") or "")
                                       and (_co_ma(dn) or not _co_ma(dd)))
        hm = dict(dn.get("hong_theo_model") or {}); hm.update(dd.get("hong_theo_model") or {})
        if thay:
            hm.update(dn.get("hong_theo_model") or {})
        moi = dict(dn if thay else dd)
        if hm:
            moi["hong_theo_model"] = hm
        if thay or moi != dd:
            g.write_text(json.dumps(moi, ensure_ascii=False), encoding="utf-8")
        dem["cache_thay" if thay else "cache_giu"] += 1
    return dem


def nhap_goi(goi_vao: Path = GOI_VAO, tt: Path = TT, cache: Path = CACHE) -> dict:
    """May nha, sau khi giai nen zip: gop moi *.sqlite trong goi_vao/ (box + tho_box) va goi_vao/dich_llm/ vao ban that."""
    goi_vao = Path(goi_vao)
    ra = {"db": [], "cache": gop_cache(cache, goi_vao / "dich_llm")}
    for f in sorted(goi_vao.glob("*.sqlite")):
        ra["db"].append(gop_db(tt, f))
    return ra


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nhap-goi", action="store_true", help="gop data/ong_dan/goi_vao/ vao CSDL + cache that")
    ap.add_argument("--vao", default=str(TT)); ap.add_argument("--tu", nargs="*", default=[])
    a = ap.parse_args(argv)
    if a.nhap_goi:
        r = nhap_goi(tt=Path(a.vao))
    else:
        r = [gop_db(Path(a.vao), Path(x)) for x in a.tu]
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
