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
cho `dieu_phoi.danh_gia_ket_qua`. Mang hong -> `tai.loi` / `tai.canh_bao` (suy giam, khong
chet; con tro trang sau DUNG YEN - `buoc_con_tro`):
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
from nhan import dieu_toc as DT                  # noqa: E402
from nhan import so as SO                        # noqa: E402
from nhan import tg_cong_khai as TGC             # noqa: E402
from nhan import truy_van_seeker as TV           # noqa: E402
from nhan import xep_hang_ung_vien as XH         # noqa: E402

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


def buoc_con_tro(sau: dict, trang_sau: int) -> dict:
    """Con tro trang sau (SUA 11/10/2026, the-brain 02 D2). Chi LUI them mot trang khi trang
    sau tai DUOC va co >= 1 bai. Tai hong (`loi_trang`) hoac het gio -> DUNG YEN (luot sau thu
    lai dung trang do). Tai duoc ma rong (`het_trang`) hoac cham TRANG_TOI_DA -> ve trang 2.
    Truoc day con tro doi ca khi tai hong -> mot trang sau bi bo qua vinh vien, im lang."""
    if sau.get("loi_trang"):
        return {"trang_moi": trang_sau, "ly_do": "loi_trang"}
    if sau.get("het_gio"):
        return {"trang_moi": trang_sau, "ly_do": "het_gio"}
    if sau.get("het_trang"):
        return {"trang_moi": 2, "ly_do": "het_trang"}
    if int(sau.get("thay", 0) or 0) < 1:
        return {"trang_moi": trang_sau, "ly_do": "khong_thay_bai"}
    return {"trang_moi": 2 if trang_sau >= TRANG_TOI_DA else trang_sau + 1, "ly_do": "tien"}


def _muc_toc(dieu_toc) -> dict:
    try:
        return dieu_toc() if dieu_toc else DT.trang_thai()
    except Exception as e:                          # noqa: BLE001 - do hong: khong chan
        return {"muc": "binh_thuong", "ly_do": ["dieu_toc_loi:%s" % type(e).__name__]}


def mot_luot(tai: bool = True, tai_mql5=None, gom_tu_so=None, tai_mt4=None, tg=None,
             dieu_toc=None, tai_github=None) -> dict:
    """Mot luot cau kho. `tai_mql5`/`gom_tu_so`/`tai_mt4`/`tg`/`dieu_toc` thay duoc cho test.

    11/10/2026 (uu tien chu du an: bot MT4/MT5 cong khai co chien luoc + .set):
      0. DIEU TOC (`nhan/dieu_toc.py`): `dung` (khoa tester / MT5 / CPU >= 80%) -> khong tai,
         khong doc, tra `skip_reason`; `cham` (vong_thu_nghiem / quet tay / CPU >= 60%) ->
         ngan sach tai x0.33, nghi x3, doc_ma toi da 20 file MOI.
      1. TRUY VAN (`truy_van_seeker.sinh`): hat giong + tu dao tu HANG_UU_TIEN cua luot truoc.
      2. TAI GOI MQL5 (`tai_mql5_goi`: .mq5 + .mqh + .set, xep bai theo tieu de) trang 1 + trang
         sau theo con tro; MT4 trang 1 (lan `mql4`, bo doc chua doc - chi xep hang).
      3. TELEGRAM cong khai (`tg_cong_khai`): kenh da biet, loc bai theo truy van.
      4. DO + XEP HANG (`xep_hang_ung_vien`) -> `ea_ra_co_che/` theo thu tu + HANG.json.
    Khi test chi tiem `tai_mql5` thi MT4/Telegram KHONG chay (khong mang trong test).
    """
    thu = tai_mql5 is not None
    tai_mql5 = tai_mql5 or CK.tai_mql5_goi
    gom_tu_so = gom_tu_so or CK.gom_tu_so
    t0 = time.time()
    kho = GOC / "mql5"                              # kho phang cu (file don) - van doc
    kho_goi = GOC / "goi_mql5"
    kho_mt4 = GOC / "goi_mql4"
    kho_gh = GOC / "goi_github"                     # 11/10/2026: nguon thu hai (GitHub EA + .set)
    for k in (kho, kho_goi, kho_mt4, kho_gh):
        k.mkdir(parents=True, exist_ok=True)
    ra: dict = {"tru": TRU, "kho": str(kho_goi)}
    toc = _muc_toc(dieu_toc) if (dieu_toc or not thu) else {"muc": "binh_thuong", "ly_do": []}
    ra["dieu_toc"] = toc
    if toc["muc"] == "dung":
        ra["skip_reason"] = ra["bo_qua"] = "dieu_toc_dung: " + ",".join(toc.get("ly_do", []))[:200]
        ra["giay"] = round(time.time() - t0, 1)
        return ra
    cham = toc["muc"] == "cham"
    hang_cu = _doc_json(GOC / "HANG_UU_TIEN.json", {}).get("hang", [])
    tv = TV.sinh(hang_cu, _doc_json(GOC / "LY_DO_CU.json", {}))
    TV.luu(tv, GOC / "TRUY_VAN.json")
    ra["truy_van"] = {"tong": len(tv), "dao": sum(1 for x in tv if x["nguon"] == "dao")}
    giay_tai = _so("BRAIN_CAU_KHO_GIAY_TAI", 180, 0, 900) * (DT.HE_SO_CHAM if cham else 1.0)
    nghi = 4.5 if cham else 1.5
    if tai and giay_tai > 0:
        con_tro_p = GOC / "TRANG_SAU.json"
        ct = _doc_json(con_tro_p, {"trang": 2})
        trang_sau = int(ct.get("trang", 2))
        bao: dict = {}
        kw = {} if thu else {"truy_van": tv, "nghi_giay": nghi}
        try:
            moi = tai_mql5(kho_goi, so_trang=1, in_ra=lambda *_: None,
                           han_giay=giay_tai * 0.4, **kw)
            con = max(1.0, giay_tai * 0.75 - (time.time() - t0))
            sau = tai_mql5(kho_goi, so_trang=1, trang_dau=trang_sau, in_ra=lambda *_: None,
                           han_giay=con, **kw)
            bao = {"trang_1": moi, f"trang_{trang_sau}": sau}
            bao["con_tro"] = buoc = buoc_con_tro(sau, trang_sau)
            if buoc["trang_moi"] != trang_sau:
                _ghi_json(con_tro_p, {"trang": buoc["trang_moi"],
                                      "luc": time.strftime("%Y-%m-%d %H:%M:%S")})
            if moi.get("loi_trang") or sau.get("loi_trang"):
                bao["canh_bao"] = ("trang danh sach MQL5 tai HONG (mang/403/429) - con tro "
                                   "DUNG YEN, luot sau thu lai; khong phai het trang")
        except Exception as e:                      # noqa: BLE001 - mang hong: van do kho cu
            bao["loi"] = f"{type(e).__name__}: {str(e)[:160]}"
        if tai_mt4 or not thu:
            try:
                con = max(1.0, giay_tai - (time.time() - t0))
                bao["mt4_trang_1"] = (tai_mt4 or CK.tai_mql5_goi)(
                    kho_mt4, so_trang=1, nen_tang="mt4", in_ra=lambda *_: None, han_giay=con,
                    truy_van=tv, nghi_giay=nghi)
            except Exception as e:                  # noqa: BLE001
                bao["mt4_loi"] = f"{type(e).__name__}: {str(e)[:160]}"
        if tai_github or not thu:
            try:
                from nhan import goi_github as GG
                bao["github"] = (tai_github or GG.tai_github_goi)(
                    kho_gh, han_giay=_so("BRAIN_CAU_KHO_GIAY_GH", 150, 0, 900)
                    * (DT.HE_SO_CHAM if cham else 1.0), truy_van=tv, in_ra=lambda *_: None)
            except Exception as e:                  # noqa: BLE001 - mang hong: van do kho cu
                bao["github_loi"] = f"{type(e).__name__}: {str(e)[:160]}"
        ra["tai"] = bao
    tg_ra = {}
    if (tg or not thu) and tai:
        try:
            tg_ra = (tg or TGC.mot_luot)(tv, han_giay=20 if cham else 60)
            _ghi_json(GOC / "TELEGRAM_CONG_KHAI.json", tg_ra)
            ra["telegram"] = TGC.tom_tat(tg_ra)
        except Exception as e:                      # noqa: BLE001
            ra["telegram"] = {"loi": f"{type(e).__name__}: {str(e)[:160]}"}
    elif not thu:                                   # khong tai: dung ket qua Telegram luot truoc
        tg_ra = _doc_json(GOC / "TELEGRAM_CONG_KHAI.json", {})
    bg = []
    for k in (kho_goi, kho_mt4, kho_gh, kho):
        g = CK.gom_tu_thu_muc(k)
        CK._url_tu_nguon_tai(g, k)
        for b in g:
            if not b["url"]:
                m = _doc_json(Path(b["nguon"][4:]).parent / "GOI.json", {})
                b["url"] = m.get("url", "")
                b["revision"] = m.get("revision") or (
                    ("mql5-code-%s" % m["id"]) if m.get("id") else "")
        bg += g
    try:
        tu_so = gom_tu_so()
    except Exception:                               # noqa: BLE001 - so cai trong/khong co
        tu_so = []
    ra["tu_so_cai"] = len(tu_so)
    bo_nho_p = GOC / "bo_nho_doc.json"
    bo_nho = _doc_json(bo_nho_p, {})
    pb = CK.phien_ban_bo_doc()
    bo_nho = {k: v for k, v in bo_nho.items() if k.endswith("@" + pb)}  # bo khoa bo doc cu
    if cham:                                        # dieu toc: chi doc toi da N file MOI
        da_doc = {k.split("@", 1)[0] for k in bo_nho}
        moi_doc, giu = 0, []
        for b in bg + tu_so:
            if CK.van_tay(b["src"] or "") not in da_doc:
                moi_doc += 1
                if moi_doc > DT.DOC_MOI_KHI_CHAM:
                    continue
            giu.append(b)
        ra["doc_hoan"] = max(0, moi_doc - DT.DOC_MOI_KHI_CHAM)
        bg, tu_so = giu, []
    r = CK.do_kho(bg + tu_so, bo_mau_thu=True, bo_nho=bo_nho)
    _ghi_json(bo_nho_p, bo_nho)
    _ghi_json(GOC / "LY_DO_CU.json", r.get("ly_do", {}))
    tl = CK.ty_le(r)
    hang = XH.xep(r, bg + tu_so, tg_ra.get("bai_khop", []))
    _ghi_json(GOC / "HANG_UU_TIEN.json", {"luc": time.strftime("%Y-%m-%d %H:%M:%S"),
                                         "tom_tat": XH.tom_tat(hang), "hang": hang})
    CK.xuat(r, GOC / "ea_ra_co_che", hang)
    (GOC / "BAO_CAO.md").write_text(
        CK.bao_cao_md(r, "tru CAUKHO (%s%s)" % (kho_goi, " + nao.db" if tu_so else ""))
        + "\n" + XH.bang_md(hang)
        + "\n## Dieu toc\n\n`%s`\n" % json.dumps(toc, ensure_ascii=False)
        + "\n## Telegram cong khai\n\n`%s`\n" % json.dumps(ra.get("telegram", {}),
                                                            ensure_ascii=False),
        encoding="utf-8")
    dong = {"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "bo_doc": pb,
            "pheu": r["pheu"], "so": r["so"], "dieu_toc": toc["muc"],
            "hang": XH.tom_tat(hang),
            "ty_le_dich": None if tl is None else round(tl, 4)}
    with (GOC / "lich_su.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(dong, ensure_ascii=False) + "\n")
    ra.update({"pheu": r["pheu"], "so": r["so"], "bo_doc": pb, "hang": XH.tom_tat(hang),
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
    if ra.get("skip_reason"):
        SO.nhip_tim(TRU, "nghi", {"bo_qua": ra["bo_qua"]})
        print(json.dumps(ra, ensure_ascii=False, indent=1))
        return 0
    if ra.get("ty_le_dich") is not None:
        SO.ghi_chi_so("cau_kho_ty_le_dich", ra["ty_le_dich"],
                      {"vao_lenh": ra["so"].get("vao_lenh", 0), "bo_doc": ra["bo_doc"]})
    SO.nhip_tim(TRU, "nghi", {k: ra.get(k) for k in ("ty_le_dich", "ea_ra_co_che", "giay")}
                | {"ea_dat_lenh": ra["pheu"].get("ea_dat_lenh", 0)}
                | ({"canh_bao": ra["tai"]["canh_bao"]}
                   if (ra.get("tai") or {}).get("canh_bao") else {}))
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
