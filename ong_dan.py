# -*- coding: utf-8 -*-
"""ong_dan.py - CLI cua ong dan mot lenh (nhan/ong_dan.py). Xem tai_lieu/ONG_DAN.md.

  python3 ong_dan.py chay                 # chay het cac buoc a..i (chay tiep duoc neu dung giua chung)
  python3 ong_dan.py <buoc>               # nhan | phan_loai | quyet_dinh | toi_uu | loc | sinh_mt5 | goi | boc | to_hop | doc_mt5
  python3 ong_dan.py trang_thai | bao_cao | do_nguoc
Tuy chon: --toi-da N (so the toi uu moi lan), --ngan-sach N (phep thu / the), --ngan-sach-to-hop N, --db <sqlite>, --id <the_id>
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nhan import ong_dan as OD  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ong dan BRAIN: kho -> Python -> loc 65/15 -> MT5 -> kho co che")
    ap.add_argument("buoc", choices=OD.BUOC + ["chay", "trang_thai", "bao_cao", "do_nguoc"])
    ap.add_argument("--toi-da", type=int)
    ap.add_argument("--ngan-sach", type=int)
    ap.add_argument("--ngan-sach-to-hop", type=int)
    ap.add_argument("--db")
    ap.add_argument("--id")
    a = ap.parse_args(argv)
    cn = OD._db(Path(a.db) if a.db else None)
    b = a.buoc
    if b == "chay":
        r = OD.chay_het(cn, toi_da=a.toi_da, ngan_sach=a.ngan_sach, ngan_sach_to_hop=a.ngan_sach_to_hop)
        print(json.dumps(r, ensure_ascii=False, indent=1))
    elif b == "trang_thai":
        print(json.dumps(OD.trang_thai(cn), ensure_ascii=False, indent=1))
    elif b == "bao_cao":
        print(OD.ghi_bao_cao(cn))
    elif b == "do_nguoc":
        print(OD.ghi_do_nguoc(cn))
    elif b == "toi_uu":
        OD.buoc_toi_uu(cn, a.toi_da, a.ngan_sach, chi_id=a.id)
    elif b == "to_hop":
        OD.buoc_to_hop(cn, a.ngan_sach_to_hop)
    else:
        getattr(OD, "buoc_" + b)(cn)
    OD.ghi_bao_cao(cn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
