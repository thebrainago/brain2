# -*- coding: utf-8 -*-
"""seeker_tai_ma_theo_phong_cach.py - tai EA (.mq4/.mq5/.mqh/.set) cong khai tren GitHub THEO PHONG CACH.

Truy van chot truoc: nhan/nguon_seeker.TRUY_VAN_THEO_PHONG_CACH. Tai vao data/cau_kho/goi_github (gitignore -
ma cua nguoi khac KHONG vao git). Token GitHub chi doc tu bien moi truong (nhan/bi_mat). Ghi dem moi phong
cach vao reports/SEEKER_TAI_MA_PHONG_CACH.json.   python seeker_tai_ma_theo_phong_cach.py [--giay 300]
"""
import argparse
import json
from pathlib import Path

from nhan import goi_github as GG
from nhan import nguon_seeker as NS

LAB = Path(__file__).resolve().parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--giay", type=float, default=300)
    ap.add_argument("--so-trang", type=int, default=2)
    a = ap.parse_args(argv)
    kho = LAB / "data" / "cau_kho" / "goi_github"
    ra = {}
    for pc, q in NS.TRUY_VAN_THEO_PHONG_CACH.items():
        b = GG.tai_github_goi(kho, han_giay=a.giay, so_repo=120, ds_truy_van=q, so_trang=a.so_trang, nghi_giay=1.5)
        b["loi"] = [str(x)[:120] for x in (b.get("loi") or [])][:5]
        ra[pc] = b
        print(pc, {k: b.get(k) for k in ("truy_van", "repo_thay", "repo_xem", "ea_moi", "ea_co_set", "tep")}, flush=True)
    (LAB / "reports" / "SEEKER_TAI_MA_PHONG_CACH.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
