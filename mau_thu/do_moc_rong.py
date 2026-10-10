# -*- coding: utf-8 -*-
"""DO MOC RONG: cung so do trung thuc nhu `do_moc.py` nhung tren bo EA NGOAI
`mau_thu/mo_rong/` (EA MT5 cong khai, giay phep MIT - nguon/commit/giay phep o
`mau_thu/mo_rong/NGUON.md` va LICENSE trong tung thu muc).

    python mau_thu/do_moc_rong.py          # chi bo mo rong
    python mau_thu/do_moc_rong.py --gop    # mau_thu + mo_rong

Bo nay KHONG dung de chinh doc_ma cho vua (khong co dap an viet tay): chi do
xem lop doc MQL5 tong quat hoa ra ngoai 10 file mau den dau. Dinh danh la
van KHONG duoc coi la `close`; diem vao khong dich duoc giu o `chua_dich`.
"""
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / "mau_thu"))

import do_moc as DMOC                                            # noqa: E402

RONG = LAB / "mau_thu" / "mo_rong"


def tep_rong() -> list:
    return sorted(RONG.rglob("*.mq5"))


def in_bang(tieu_de: str, r: dict) -> None:
    print("\n== %s ==" % tieu_de)
    for ten, cc, vl in r["dong"]:
        print("  %-46s co_che=%d  vao_lenh=%d" % (ten[:46], cc, vl))
    L = r["loai"]
    vl = r["vao_lenh"]
    print("\n  file                   : %d" % r["file"])
    print("  tim THAY diem vao lenh : %d" % vl)
    print("  RA duoc co che         : %d" % r["co_che"])
    print("  diem vao dich duoc     : %d/%d = %.1f%%   <- SO CHINH"
          % (r["vao_co"], vl, (100.0 * r["vao_co"] / vl) if vl else 0.0))
    print("  phan loai diem vao     : dich_duoc=%d  quan_ly_dich_duoc=%d  quan_ly_vi_the=%d"
          "  ma_chet=%d  chua_dich=%d"
          % (L["dich_duoc"], L["quan_ly_dich_duoc"], L["quan_ly_vi_the"], L["ma_chet"],
             L["chua_dich"]))
    ms = L["dich_duoc"] + L["chua_dich"]
    print("  tin hieu thanh nen     : %d/%d = %.1f%%"
          % (L["dich_duoc"], ms, (100.0 * L["dich_duoc"] / ms) if ms else 0.0))
    T = r.get("thoat") or {}
    co_ra = T.get("ro", 0) + T.get("sltp", 0)
    print("  loi ra theo EA         : %d/%d co che (sltp=%d, ro=%d; giu co dinh=%d; dong theo"
          " muc=%d; gia dinh _Point=%d)"
          % (co_ra, r["co_che"], T.get("sltp", 0), T.get("ro", 0), T.get("giu_co_dinh", 0),
             T.get("dong_theo_muc", 0), T.get("gia_dinh_point", 0)))
    print("  ly do 'chua dien dat duoc':")
    for k, n in sorted(r["ly_do"].items(), key=lambda x: -x[1])[:12]:
        print("   %2dx  %s" % (n, k))


def main() -> int:
    in_bang("mo_rong (%d EA ngoai)" % len(tep_rong()), DMOC.do(tep_rong()))
    if "--gop" in sys.argv:
        in_bang("gop mau_thu + mo_rong",
                DMOC.do(sorted(DMOC.MAU.glob("*.mq5")) + tep_rong()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
