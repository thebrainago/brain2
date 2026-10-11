# -*- coding: utf-8 -*-
"""bang_diem_nguon.py - BANG DIEM NGUON theo HE DA KIEM, khong theo so ung vien (11/10/2026).

Y the-brain `pheu_gia_tri.xep_nguon` (goi ban giao A5):
    suat_tien = (so he DAT + 1) / (so he DA THU + 10)
"Da thu" = mot co che/he cua nguon do da CHAY DUOC qua `vong_thu_nghiem` tren GIA THAT (CSV);
"dat" = vong lap GIU LAI (cong brain2 hien tai, KHONG noi). Chay tren gia GIA LAP khong tinh
(chi la kiem ong). Day la MO PHONG, khong phai tien.

So cai: `data/bang_diem_nguon/so.jsonl` (git bo qua). Moi dong = mot lan chay mot he; bang diem
lay KET QUA MOI NHAT cua moi (nguon, file, ten). Nguon cua file EA doc tu `NGUON.json` trong
thu muc mau (do `cau_kho_ma.xuat` ghi), khong co thi `noi_bo:<ten thu muc>`.

    python -m nhan.bang_diem_nguon                       # in bang
    python -m nhan.bang_diem_nguon --nap kq.json --mau mau_thu --du-lieu eurusd.csv   # nap tay
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
SO_CAI = Path(os.environ.get("BRAIN_BANG_DIEM_NGUON") or
              (LAB / "data" / "bang_diem_nguon" / "so.jsonl"))


def suat_tien(dat: int, da_thu: int) -> float:
    return (dat + 1) / (da_thu + 10)


def _nguon_theo_file(mau: str | Path) -> dict:
    p = Path(mau) / "NGUON.json"
    ra = {}
    try:
        for x in json.loads(p.read_text(encoding="utf-8")):
            ra[x.get("file")] = x.get("nguon") or "khong_ro"
    except Exception:                                       # noqa: BLE001 - khong co NGUON.json
        pass
    return ra


def ghi_tu_vong(tong: list[dict], mau: str | Path, du_lieu: str | None,
                so_cai: Path | None = None, mo_hinh_phi: str | None = None) -> int:
    """Ghi ket qua mot lan `vong_thu_nghiem` vao so cai. Tra so dong ghi.
    Bo dong loi / trung / khong hop khung (khong phai 'da thu')."""
    so_cai = Path(so_cai or SO_CAI)
    ban_do = _nguon_theo_file(mau)
    mac_dinh = "noi_bo:" + Path(mau).name
    that = bool(du_lieu) and not str(du_lieu).startswith("gia_lap")
    n = 0
    so_cai.parent.mkdir(parents=True, exist_ok=True)
    with so_cai.open("a", encoding="utf-8") as f:
        for x in tong:
            if "loi" in x or x.get("trung") or x.get("khong_hop_khung"):
                continue
            f.write(json.dumps({
                "luc": time.strftime("%Y-%m-%d %H:%M:%S"),
                "nguon": ban_do.get(x.get("file"), mac_dinh), "file": x.get("file"),
                "ten": str(x.get("ten"))[:120], "giu_lai": bool(x.get("giu_lai")),
                "gia_that": that, "du_lieu": Path(str(du_lieu)).name if du_lieu else "gia_lap",
                "mo_hinh_phi": x.get("mo_hinh_phi") or mo_hinh_phi,
                "dat_25_09": (x.get("tieu_chi_25_09") or {}).get("dat")},
                ensure_ascii=False) + "\n")
            n += 1
    return n


def bang(so_cai: Path | None = None, them_nguon: dict | None = None) -> list[dict]:
    """[{nguon, da_thu, dat, dat_25_09, suat_tien, tai_lieu}] xep theo suat_tien giam dan.
    `them_nguon` = {ma: so tai lieu thu hoach} de nguon chua thu he nao van hien (suat san 0,1)."""
    so_cai = Path(so_cai or SO_CAI)
    moi_nhat: dict[tuple, dict] = {}
    if so_cai.exists():
        for dong in so_cai.read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(dong)
            except ValueError:
                continue
            if not x.get("gia_that"):
                continue
            moi_nhat[(x["nguon"], x.get("file"), x.get("ten"))] = x
    gop: dict[str, dict] = {}
    for (ng, _, _), x in moi_nhat.items():
        g = gop.setdefault(ng, {"nguon": ng, "da_thu": 0, "dat": 0, "dat_25_09": 0})
        g["da_thu"] += 1
        g["dat"] += int(bool(x.get("giu_lai")))
        g["dat_25_09"] += int(bool(x.get("dat_25_09")))
    for ma, tl in (them_nguon or {}).items():
        gop.setdefault(ma, {"nguon": ma, "da_thu": 0, "dat": 0, "dat_25_09": 0})["tai_lieu"] = tl
    ra = []
    for g in gop.values():
        g.setdefault("tai_lieu", None)
        g["suat_tien"] = round(suat_tien(g["dat"], g["da_thu"]), 4)
        ra.append(g)
    # Nguon DA THU he truoc (xep theo suat), roi nguon chua thu (xep theo tai lieu) - de bang
    # khong bi day so do that xuong duoi 50 nguon chua co so.
    ra.sort(key=lambda g: (g["da_thu"] == 0, -g["suat_tien"], -g["da_thu"],
                           -(g["tai_lieu"] or 0), g["nguon"]))
    return ra


def bang_md(ds: list[dict], toi_da: int = 25) -> list[str]:
    d = ["## 4. Bang diem nguon - theo HE DA KIEM, khong theo so ung vien", "",
         "suat tien = (he DAT + 1) / (he DA THU + 10). 'Da thu' = he cua nguon da chay qua "
         "`vong_thu_nghiem` tren GIA THAT co phi; 'dat' = cong brain2 GIU (khong noi). "
         "MO PHONG, khong phai tien. Nguon chua thu he nao = suat san 0,1 (CHUA DO DUOC).", "",
         "| nguon | he da thu | dat (GIU) | dat 25/09 (nhan) | suat tien | tai lieu thu hoach |",
         "|---|---|---|---|---|---|"]
    for g in ds[:toi_da]:
        d.append(f"| {g['nguon']} | {g['da_thu']} | {g['dat']} | {g['dat_25_09']} | "
                 f"{g['suat_tien']:.3f}{'' if g['da_thu'] else ' (CHUA DO DUOC)'} | "
                 f"{'' if g['tai_lieu'] is None else g['tai_lieu']} |")
    if len(ds) > toi_da:
        d.append(f"| ... {len(ds) - toi_da} nguon nua (chua thu he nao) | | | | | |")
    tong_thu = sum(g["da_thu"] for g in ds)
    tong_dat = sum(g["dat"] for g in ds)
    d += ["", f"- Tong: {tong_thu} he da thu tren gia that, {tong_dat} dat. "
          + ("Chua nguon nao cho ra he DAT -> bang chi giu san tham do, chua dung de cat nguon."
             if tong_dat == 0 else "")]
    return d


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nap", help="file JSON ket qua vong_thu_nghiem (--json)")
    ap.add_argument("--mau", help="thu muc mau da chay (de doc NGUON.json)")
    ap.add_argument("--du-lieu", help="CSV gia that da dung (bo trong = gia lap, khong tinh)")
    a = ap.parse_args(argv)
    if a.nap:
        n = ghi_tu_vong(json.loads(Path(a.nap).read_text(encoding="utf-8")), a.mau or ".", a.du_lieu)
        print(f"nap {n} dong vao {SO_CAI}")
    print("\n".join(bang_md(bang())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
