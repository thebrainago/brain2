# -*- coding: utf-8 -*-
"""cau_kho.py - TRU CAU KHO MA: SEEKER -> doc_ma, chay dinh ky trong `dieu_phoi`.

Them 11/10/2026. `nhan/cau_kho_ma.py` noi kho ma SEEKER voi bo doc MQL5 cau truc,
nhung truoc day chi chay TAY (`b cau-kho`). Tru nay chay no theo lich, KHONG can
`nao.db` co du lieu (cloud/Linux/VPS moi): nguon chinh la `--tai-mql5` (bo tai
cua SEEKER, chi file `.mq5` don, khong giai nen, khong chay ma). Neu so cai co
artifact `code`/`noi_dung` ma nguon (may Windows chay SEEKER lau) thi gom them.

Moi luot (gioi han: tai <= `BRAIN_CAU_KHO_GIAY_TAI` giay, mac dinh 180; doc tren
bo nho dem theo van tay noi dung + phien ban bo doc -> chi file MOI hoac bo doc
MOI moi doc lai):
  1. tai bai MOI trang 1 (Code Base xep moi nhat truoc) + MOT trang sau theo con
     tro (`TRANG_SAU.json`) de kho lon dan nguoc thoi gian (toi `TRANG_TOI_DA`);
  2. do pheu + ty le dich (CUNG dinh nghia `mau_thu/do_moc.py`) - day la PHEP DO
     tong quat hoa cua `doc_ma`, KHONG phai dap an de chinh bo doc;
  3. xuat EA ra co che sang `data/cau_kho/ea_ra_co_che/` (+ NGUON.json) cho
     `python vong_thu_nghiem.py --mau data/cau_kho/ea_ra_co_che` - cong giu cua
     vong lap KHONG doi;
  4. ghi `data/cau_kho/BAO_CAO.md`, `lich_su.jsonl`, chi so `cau_kho_ty_le_dich`.

Chi ghi trong `data/cau_kho/` (git bo qua) + so cai (nhip, chi so). In JSON cuoi
cho `dieu_phoi.danh_gia_ket_qua`. Mang hong -> `tai.loi` (suy giam, khong chet):
van do lai kho dang co.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB))
from nhan import cau_kho_ma as CK                # noqa: E402
from nhan import so as SO                        # noqa: E402

TRU = "CAUKHO"
GOC = Path(os.environ.get("BRAIN_CAU_KHO_DIR") or (LAB / "data" / "cau_kho"))
TRANG_TOI_DA = 60


def _so(ten: str, mac_dinh: float, thap: float, cao: float) -> float:
    try:
        return max(thap, min(cao, float(os.environ.get(ten, mac_dinh))))
    except ValueError:
        return mac_dinh


def _doc_json(p: Path, mac_dinh):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else mac_dinh
    except Exception:                               # noqa: BLE001 - file hong: lam lai
        return mac_dinh


def _ghi_json(p: Path, x) -> None:
    tam = p.with_suffix(p.suffix + ".tam")
    tam.write_text(json.dumps(x, ensure_ascii=False), encoding="utf-8")
    os.replace(tam, p)                              # nguyen tu: khong de file nua voi


def mot_luot(tai: bool = True, tai_mql5=None, gom_tu_so=None) -> dict:
    """Mot luot cau kho. `tai_mql5`/`gom_tu_so` thay duoc cho test (khong mang)."""
    tai_mql5 = tai_mql5 or CK.tai_mql5
    gom_tu_so = gom_tu_so or CK.gom_tu_so
    t0 = time.time()
    kho = GOC / "mql5"
    kho.mkdir(parents=True, exist_ok=True)
    ra: dict = {"tru": TRU, "kho": str(kho)}
    giay_tai = _so("BRAIN_CAU_KHO_GIAY_TAI", 180, 0, 900)
    if tai and giay_tai > 0:
        con_tro_p = GOC / "TRANG_SAU.json"
        ct = _doc_json(con_tro_p, {"trang": 2})
        trang_sau = int(ct.get("trang", 2))
        bao: dict = {}
        try:
            moi = tai_mql5(kho, so_trang=1, in_ra=lambda *_: None, han_giay=giay_tai * 0.5)
            con = max(1.0, giay_tai - (time.time() - t0))
            sau = tai_mql5(kho, so_trang=1, trang_dau=trang_sau, in_ra=lambda *_: None,
                           han_giay=con)
            bao = {"trang_1": moi, f"trang_{trang_sau}": sau}
            if not sau.get("het_gio"):              # trang sau xong -> lui them mot trang
                _ghi_json(con_tro_p, {"trang": 2 if trang_sau >= TRANG_TOI_DA
                                      else trang_sau + 1,
                                      "luc": time.strftime("%Y-%m-%d %H:%M:%S")})
        except Exception as e:                      # noqa: BLE001 - mang hong: van do kho cu
            bao["loi"] = f"{type(e).__name__}: {str(e)[:160]}"
        ra["tai"] = bao
    bg = CK.gom_tu_thu_muc(kho)
    CK._url_tu_nguon_tai(bg, kho)
    try:
        tu_so = gom_tu_so()
    except Exception:                               # noqa: BLE001 - so cai trong/khong co
        tu_so = []
    ra["tu_so_cai"] = len(tu_so)
    bo_nho_p = GOC / "bo_nho_doc.json"
    bo_nho = _doc_json(bo_nho_p, {})
    pb = CK.phien_ban_bo_doc()
    bo_nho = {k: v for k, v in bo_nho.items() if k.endswith("@" + pb)}  # bo khoa bo doc cu
    r = CK.do_kho(bg + tu_so, bo_nho=bo_nho)
    _ghi_json(bo_nho_p, bo_nho)
    tl = CK.ty_le(r)
    CK.xuat(r, GOC / "ea_ra_co_che")
    (GOC / "BAO_CAO.md").write_text(
        CK.bao_cao_md(r, "tru CAUKHO (%s%s)" % (kho, " + nao.db" if tu_so else "")),
        encoding="utf-8")
    dong = {"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "bo_doc": pb,
            "pheu": r["pheu"], "so": r["so"],
            "ty_le_dich": None if tl is None else round(tl, 4)}
    with (GOC / "lich_su.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(dong, ensure_ascii=False) + "\n")
    ra.update({"pheu": r["pheu"], "so": r["so"], "bo_doc": pb,
               "ty_le_dich": dong["ty_le_dich"], "ea_ra_co_che": len(r["xuat"]),
               "giay": round(time.time() - t0, 1)})
    return ra


def main() -> int:
    SO.khoi_tao()
    SO.nhip_tim(TRU, "chay")
    try:
        ra = mot_luot(tai="--khong-tai" not in sys.argv)
    except Exception as e:                          # noqa: BLE001 - bao cho dieu_phoi
        SO.nhip_tim(TRU, "loi", {"loi": f"{type(e).__name__}: {str(e)[:200]}"})
        print(json.dumps({"tru": TRU, "loi": f"{type(e).__name__}: {str(e)[:200]}"}))
        return 1
    if ra.get("ty_le_dich") is not None:
        SO.ghi_chi_so("cau_kho_ty_le_dich", ra["ty_le_dich"],
                      {"vao_lenh": ra["so"].get("vao_lenh", 0), "bo_doc": ra["bo_doc"]})
    SO.nhip_tim(TRU, "nghi", {k: ra.get(k) for k in ("ty_le_dich", "ea_ra_co_che", "giay")}
                | {"ea_dat_lenh": ra["pheu"].get("ea_dat_lenh", 0)})
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
