# -*- coding: utf-8 -*-
"""DO MOC: `doc_ma.py` boc duoc bao nhieu co che tu bo mau .mq5.

Bai nay chay duoc TREN CLOUD: khong dung `nao.db`, khong dung MT5, khong
dung du lieu gia. Chi can ma nguon trong repo.

    python mau_thu/do_moc.py

Moc do duoc ngay 18/09/2026, trong 10 file mau:

    tim THAY diem vao lenh : 22
    RA duoc co che         : 0        <- con so phai nang

Vi sao 0: dieu kien vao lenh nam trong BIEN TRUNG GIAN (`downbreakout`,
`Tradesinfo.initup && current[0].close >= Tradesinfo.hedgeprice`), con
`ngu_phap.py` chi dien dat duoc bieu thuc truc tiep tren gia/chi bao. Bo doc
thay cho vao lenh nhung khong truy nguoc duoc bien ve bieu thuc goc, nen bo
het vao muc `chua_dien_dat_duoc`.

Do la nut that THAT: kho co 12.078 tai lieu nhung chi boc ra 285 co che (2,4%).
"""
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB))

from nhan import doc_ma as DM                                    # noqa: E402

MAU = LAB / "mau_thu"


def do(files=None) -> dict:
    """`files`: danh sach Path .mq5 (mac dinh: mau_thu/*.mq5, KHONG de quy -
    so chinh lich su giu nguyen; bo mo rong do rieng o `do_moc_rong.py`)."""
    tong = co_che = vao_lenh = vao_co = 0
    loai = {"dich_duoc": 0, "ma_chet": 0, "quan_ly_vi_the": 0, "chua_dich": 0,
            "quan_ly_dich_duoc": 0}
    ly_do: dict[str, int] = {}
    dong: list[tuple] = []
    thoat: dict[str, int] = {}
    for p in (sorted(MAU.glob("*.mq5")) if files is None else files):
        vb = p.read_text(encoding="utf-8", errors="ignore")
        tong += 1
        ds = DM.doc_ma(vb, ngon_ngu="mql5", nguon=p.name)
        d = DM.doc_chien_luoc(vb, nguon=p.name)
        co_che += len(d.get("co_che", []))
        for sp in d.get("co_che", []):
            # LOI RA (them 11/10/2026): co che dong theo logic cua EA (SL/TP, ro lenh,
            # dong theo muc) hay chi giu co dinh `giu` bar (KHONG phai EA)
            # `dk_ra` (them 11/10/2026): dong theo DIEU KIEN cua EA (`ra`, vd 016
            # CloseTrades(TYPE) khi MA cat nguoc) - cung la loi ra cua EA
            k_ra = "ro" if sp.get("ro") else "sltp" if sp.get("sltp") else \
                "dk_ra" if sp.get("ra") else "dong_pip" if sp.get("dong_mo_pip") else \
                "giu_co_dinh"
            thoat[k_ra] = thoat.get(k_ra, 0) + 1
            if sp.get("dong_mo_bar"):
                thoat["dong_theo_muc"] = thoat.get("dong_theo_muc", 0) + 1
            if sp.get("gia_dinh_diem"):
                thoat["gia_dinh_point"] = thoat.get("gia_dinh_point", 0) + 1
        vao_lenh += d.get("so_vao_lenh", 0)
        vao_co += d.get("so_vao_lenh_co_co_che", 0)
        for k, v in (d.get("phan_loai_vao_lenh") or {}).items():
            loai[k] = loai.get(k, 0) + v
        for x in d.get("chua_dien_dat_duoc", []):
            k = str(x)[:70]
            ly_do[k] = ly_do.get(k, 0) + 1
        dong.append((p.name, len(d.get("co_che", [])), d.get("so_vao_lenh", 0)))
    return {"file": tong, "co_che": co_che, "vao_lenh": vao_lenh,
            "vao_co": vao_co, "loai": loai,
            "ly_do": ly_do, "dong": dong, "thoat": thoat}


def main() -> int:
    r = do()
    for ten, cc, vl in r["dong"]:
        print("  %-46s co_che=%d  vao_lenh=%d" % (ten[:46], cc, vl))
    print("\n  file mau               : %d" % r["file"])
    print("  tim THAY diem vao lenh : %d" % r["vao_lenh"])
    print("  RA duoc co che         : %d   (moc 18/09: 0)" % r["co_che"])
    ty = (100.0 * r["co_che"] / r["vao_lenh"]) if r["vao_lenh"] else 0.0
    print("  ty le dien dat duoc    : %.1f%%   (co che / diem vao)" % ty)
    # Mot lenh vao `if(up||down)` tach dung thanh 2 co che (mua + ban), nen ty
    # le tren co the vuot so diem vao THAT SU dich duoc. Day la so do chat hon:
    ty2 = (100.0 * r["vao_co"] / r["vao_lenh"]) if r["vao_lenh"] else 0.0
    print("  diem vao dich duoc     : %d/%d = %.1f%%   <- SO CHINH (moc 908075c0: 6/22 = 27.3%%;"
          " 21cc69dc: 8/22 = 36.4%%; 54c8597e: 11/22 = 50.0%%)"
          % (r["vao_co"], r["vao_lenh"], ty2))
    # PHAN LOAI (them 10/10/2026). Mau so tren tron ca "tao": lenh hedge/luoi/
    # nhoi lenh theo GIA VAO LENH / so lenh / loi lo (khong phai tin hieu thanh
    # nen - ngu phap DSL khong mo ta duoc va KHONG NEN mo ta) va ma chet (sau
    # `return;` vo dieu kien). Ty le tren TIN HIEU THANH NEN bo hai nhom do ra
    # khoi mau so. So chinh van la dong tren; dong duoi chi de biet con bao
    # nhieu tin hieu that chua dich duoc.
    L = r["loai"]
    # quan_ly_dich_duoc (them vong "ro hedge"): lenh hedge cua ro lenh duoc mo
    # phong DUNG trong khoi `ro` cua lenh dau (`nhan/ro_mql.py`) - tinh vao so
    # chinh. ma_chet gom ca khoi hedge KHONG BAO GIO toi duoc (`postotal==22`).
    print("  phan loai diem vao     : dich_duoc=%d (tin hieu) + quan_ly_dich_duoc=%d (hedge ro)"
          "  quan_ly_vi_the=%d  ma_chet=%d  chua_dich=%d"
          % (L["dich_duoc"], L["quan_ly_dich_duoc"], L["quan_ly_vi_the"], L["ma_chet"],
             L["chua_dich"]))
    ms = L["dich_duoc"] + L["chua_dich"]
    ty3 = (100.0 * L["dich_duoc"] / ms) if ms else 0.0
    print("  tin hieu thanh nen     : %d/%d = %.1f%%   (bo hedge/luoi + ma chet khoi mau so)"
          % (L["dich_duoc"], ms, ty3))
    print("\n  ly do 'chua dien dat duoc':")
    for k, n in sorted(r["ly_do"].items(), key=lambda x: -x[1])[:8]:
        print("   %2dx  %s" % (n, k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
