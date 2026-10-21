# -*- coding: utf-8 -*-
"""ong_dan.py - CLI cua ong dan mot lenh (nhan/ong_dan.py). Xem tai_lieu/ONG_DAN.md.

  python3 ong_dan.py chay                 # chay het cac buoc a..i (chay tiep duoc neu dung giua chung)
  python3 ong_dan.py <buoc>               # nhan | phan_loai | quyet_dinh | dich_llm (may nha) | toi_uu | loc | sinh_mt5 | goi | boc | to_hop | doc_mt5
  python3 ong_dan.py trang_thai | bao_cao | do_nguoc
Tuy chon: --lam-lai (toi_uu theo dot), --toi-da N (so the toi uu moi lan), --ngan-sach N (phep thu / the), --ngan-sach-to-hop N, --db <sqlite>, --id <the_id>, --gioi_han N + --luong K (dich_llm)
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
    ap.add_argument("--lam-lai", action="store_true", help="toi_uu: mo lai the da toi uu con thieu phep thu (chia dot)")
    ap.add_argument("--gioi_han", "--gioi-han", dest="gioi_han", type=int, help="dich_llm: so the toi da lan nay")
    ap.add_argument("--luong", type=int, default=4, help="dich_llm: so loi goi LLM song song")
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
        OD.buoc_toi_uu(cn, a.toi_da, a.ngan_sach, chi_id=a.id, lam_lai=a.lam_lai)
    elif b == "dich_llm":
        r = OD.buoc_dich_llm(cn, gioi_han=a.gioi_han, luong=a.luong)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        if r.get("het_quota"):                  # 20/10/2026: het quota LLM -> rc 3: dieu_phoi nghi roi lam Python thay
            OD.ghi_bao_cao(cn)
            return 3
    elif b == "to_hop":
        OD.buoc_to_hop(cn, a.ngan_sach_to_hop)
    else:
        getattr(OD, "buoc_" + b)(cn)
    OD.ghi_bao_cao(cn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
