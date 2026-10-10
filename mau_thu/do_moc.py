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


def do() -> dict:
    tong = co_che = vao_lenh = vao_co = 0
    ly_do: dict[str, int] = {}
    dong: list[tuple] = []
    for p in sorted(MAU.glob("*.mq5")):
        vb = p.read_text(encoding="utf-8", errors="ignore")
        tong += 1
        ds = DM.doc_ma(vb, ngon_ngu="mql5", nguon=p.name)
        d = DM.doc_chien_luoc(vb, nguon=p.name)
        co_che += len(d.get("co_che", []))
        vao_lenh += d.get("so_vao_lenh", 0)
        vao_co += d.get("so_vao_lenh_co_co_che", 0)
        for x in d.get("chua_dien_dat_duoc", []):
            k = str(x)[:70]
            ly_do[k] = ly_do.get(k, 0) + 1
        dong.append((p.name, len(d.get("co_che", [])), d.get("so_vao_lenh", 0)))
    return {"file": tong, "co_che": co_che, "vao_lenh": vao_lenh,
            "vao_co": vao_co,
            "ly_do": ly_do, "dong": dong}


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
    print("  diem vao dich duoc     : %d/%d = %.1f%%" % (r["vao_co"], r["vao_lenh"], ty2))
    print("\n  ly do 'chua dien dat duoc':")
    for k, n in sorted(r["ly_do"].items(), key=lambda x: -x[1])[:8]:
        print("   %2dx  %s" % (n, k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
