# -*- coding: utf-8 -*-
"""quet_tin_hieu_dem.py - Vòng quét đêm: FXBlue mass → dual-track dich → việc tester.

Chạy trên máy nhà (E:\\brain2_grok_tin_hieu) hoặc box.
Lịch sự >=4s; CPU vừa phải; không đụng mt5_slots / ong_dan / mt5_lien_tuc.

Ví dụ Task Scheduler (máy nhà), 02:00 hàng đêm:
  powershell -NoProfile -ExecutionPolicy Bypass -File E:\\brain2_grok_tin_hieu\\chay_quet_dem.ps1
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))


def main(argv=None):
    import argparse
    from nhan import thu_thap_tin_hieu_cong_khai as TT
    from nhan import dich_nguoc_tin_hieu as DN
    from nhan import viet_viec_tin_hieu as VV

    ap = argparse.ArgumentParser()
    ap.add_argument("--nghi", type=float, default=4.0)
    ap.add_argument("--kho-gia", default=os.environ.get("BRAIN_DATA") or "")
    ap.add_argument("--toi-da-he", type=int, default=40)
    ap.add_argument("--bo-kham-pha", action="store_true")
    ap.add_argument("--mql5-list", action="store_true")
    ap.add_argument("--hang-viec", default="",
                    help="Mac dinh reports/vong2/hang_cho_tin_hieu.jsonl")
    ap.add_argument("--loop-giay", type=int, default=0,
                    help="Neu >0: lap vo han moi N giay (vd 86400)")
    a = ap.parse_args(argv)
    kho = Path(a.kho_gia) if a.kho_gia else None
    hang = Path(a.hang_viec) if a.hang_viec else None

    def mot_vong():
        t0 = time.time()
        if a.mql5_list:
            TT.liet_ke_mql5_signals(nghi=a.nghi)
        if a.bo_kham_pha:
            users = list(TT.FXBLUE_SEED)
        else:
            users = TT.kham_pha_user_fxblue(nghi=a.nghi)[: a.toi_da_he]
        kq = DN.chay_ong(users, nghi=a.nghi, kho_gia=kho, ca_hai_track=True)
        viec = VV.ghi_tu_dich(kq.get("dich") or [], hang=hang)
        # mirror hang_cho sang workspace neu co
        mirror = Path(os.environ.get("BRAIN_HANG_CHO_MIRROR") or "")
        if mirror:
            mirror.mkdir(parents=True, exist_ok=True)
            from nhan import hang_cho_llm as HCL
            for p in HCL.CHO.glob("*.json"):
                dest = mirror / p.name
                if not dest.exists():
                    dest.write_bytes(p.read_bytes())
        tong = {
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "giay": round(time.time() - t0, 1),
            "users": len(users),
            "dich": len(kq.get("dich") or []),
            "bo_qua": len(kq.get("bo_qua") or []),
            "viec": viec,
        }
        print(json.dumps(tong, ensure_ascii=False, indent=2))
        log = GOC / "reports" / "vong2" / "quet_tin_hieu_log.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(tong, ensure_ascii=False) + "\n")
        return tong

    while True:
        mot_vong()
        if a.loop_giay <= 0:
            break
        time.sleep(a.loop_giay)


if __name__ == "__main__":
    main()
