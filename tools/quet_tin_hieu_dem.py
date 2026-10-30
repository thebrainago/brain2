# -*- coding: utf-8 -*-
"""quet_tin_hieu_dem.py - Vòng quét đêm: FXBlue + Myfxbook HTML History + MQL5 PW
→ dual-track dich → việc tester.

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

# VNPT DNS NXDOMAIN → patch getaddrinfo (same process as network calls)
try:
    sys.path.insert(0, str(GOC / "tools"))
    import dns_override as _dns
    _dns.ensure("api.fxblue.com", "www.fxblue.com", "www.mql5.com",
                "www.myfxbook.com", "myfxbook.com")
except Exception as _e:
    print("[dns_override]", _e)


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
    ap.add_argument("--mql5-pw", action="store_true",
                    help="Playwright: tu dong Export CSV History MQL5 (may nha)")
    ap.add_argument("--mql5-toi-da", type=int, default=100)
    ap.add_argument("--myfxbook-pw", nargs="*", default=None,
                    help="Playwright Myfxbook HTML History paths; empty = MYFXBOOK_SEED")
    ap.add_argument("--kiem-tra-mql5-profiles", action="store_true",
                    help="Probe all Chrome profiles for live mql5.com login")
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
        mql5_pw_kq = None
        myfx_kq = None
        if a.mql5_pw:
            try:
                from tools import tai_lich_su_trinh_duyet as PW
                mql5_pw_kq = PW.chay_mql5(
                    toi_da=a.mql5_toi_da,
                    nghi=max(float(a.nghi), 5.0),
                    tuoi_min_ngay=365,
                    headed=True,
                )
                print("[mql5_pw]", json.dumps({
                    k: mql5_pw_kq.get(k) for k in
                    ("ok", "tong_ok", "tong_loi", "tong_bo_qua", "can_dang_nhap", "ly_do")
                }, ensure_ascii=False))
                csv_dir = Path(os.environ.get("BRAIN_MQL5_CSV") or
                               r"E:\brain2_grok_tin_hieu\data\mql5_csv")
                if csv_dir.is_dir():
                    nap = TT.nap_mql5_csv_thu_muc(csv_dir)
                    dich_m = []
                    for h in (nap.get("he") or []):
                        hid = h["he_id"]
                        trades = TT.doc_he_da_luu("mql5_csv", hid)
                        if not trades:
                            continue
                        loc = DN.loc_he(trades, tu_choi_nguy_hiem=False)
                        tracks = ["dca"] if (loc.get("martingale") or loc.get("grid")) else ["thuong"]
                        url = "https://www.mql5.com/en/signals/%s" % hid
                        for tr in tracks:
                            kq1 = DN.xep_dich_boc(
                                "mql5_csv", hid, trades, kho_gia=kho, url=url, track=tr)
                            dich_m.append({
                                "he_id": hid, "track": tr, "nguon": "mql5_csv",
                                **{k: kq1.get(k) for k in
                                   ("trang_thai", "id", "ghi_chu", "so_lenh",
                                    "so_mau", "so_multi", "ho_so_path")},
                            })
                            print("[dich_nguoc/%s] mql5_csv %s -> %s" % (
                                tr, hid, kq1.get("trang_thai")))
                    if dich_m:
                        VV.ghi_tu_dich(dich_m, hang=hang)
            except Exception as e:
                print("[mql5_pw loi]", e)
                mql5_pw_kq = {"ok": False, "ly_do": str(e)}
        if a.myfxbook_pw is not None:
            try:
                from tools import tai_lich_su_trinh_duyet as PW
                paths = list(a.myfxbook_pw) if a.myfxbook_pw else list(
                    getattr(TT, "MYFXBOOK_SEED", ()) or ())
                if paths:
                    myfx_kq = PW.chay_myfxbook(
                        paths, nghi=max(float(a.nghi), 5.0), headed=True,
                        html=True, csv_export=False)
                    print("[myfxbook_html]", json.dumps({
                        k: myfx_kq.get(k) for k in
                        ("ok", "tong_ok", "tong_loi", "tong_bo_qua")
                    }, ensure_ascii=False))
                    myfx_dir = Path(os.environ.get("BRAIN_MYFX_CSV") or
                                    r"E:\brain2_grok_tin_hieu\data\myfxbook_csv")
                    if myfx_dir.is_dir():
                        nap_m = TT.nap_myfxbook_csv_thu_muc(myfx_dir)
                        dich_fx = []
                        for h in (nap_m.get("he") or []):
                            hid = h["he_id"]
                            trades = TT.doc_he_da_luu("myfxbook", hid)
                            if not trades:
                                continue
                            loc = DN.loc_he(trades, tu_choi_nguy_hiem=False)
                            tracks = (["dca"] if (loc.get("martingale") or loc.get("grid"))
                                      else ["thuong"])
                            url = "https://www.myfxbook.com/members/"
                            for tr in tracks:
                                kq1 = DN.xep_dich_boc(
                                    "myfxbook", hid, trades, kho_gia=kho,
                                    url=url + hid, track=tr)
                                dich_fx.append({
                                    "he_id": hid, "track": tr, "nguon": "myfxbook",
                                    **{k: kq1.get(k) for k in
                                       ("trang_thai", "id", "ghi_chu", "so_lenh",
                                        "so_mau", "so_multi", "ho_so_path")},
                                })
                                print("[dich_nguoc/%s] myfxbook %s -> %s" % (
                                    tr, hid, kq1.get("trang_thai")))
                        if dich_fx:
                            VV.ghi_tu_dich(dich_fx, hang=hang)
            except Exception as e:
                print("[myfxbook_html loi]", e)
                myfx_kq = {"ok": False, "ly_do": str(e)}
        if a.kiem_tra_mql5_profiles:
            try:
                from tools import tai_lich_su_trinh_duyet as PW
                pr = PW.kiem_tra_login_mql5_moi_profile(headed=True)
                print("[mql5_profiles]", json.dumps({
                    "co_profile_login": pr.get("co_profile_login"),
                    "logged": pr.get("logged"),
                    "profiles": [
                        {k: x.get(k) for k in
                         ("name", "prefs_mql5", "login", "goto", "header", "loi", "bo_qua")}
                        for x in (pr.get("profiles") or [])
                    ],
                }, ensure_ascii=False, indent=2))
            except Exception as e:
                print("[mql5_profiles loi]", e)
        if a.bo_kham_pha:
            users = list(TT.FXBLUE_SEED)
        else:
            users = TT.kham_pha_user_fxblue(nghi=a.nghi)[: a.toi_da_he]
        kq = DN.chay_ong(users, nghi=a.nghi, kho_gia=kho, ca_hai_track=True)
        viec = VV.ghi_tu_dich(kq.get("dich") or [], hang=hang)
        # mirror hang_cho sang workspace neu co — skip neu id da co trong xong/
        mirror = Path(os.environ.get("BRAIN_HANG_CHO_MIRROR") or "")
        if mirror:
            mirror.mkdir(parents=True, exist_ok=True)
            from nhan import hang_cho_llm as HCL
            xong_mirror = mirror.parent / "xong"
            for p in HCL.CHO.glob("*.json"):
                # skip-if-in-xong (local, sibling, hoac canh mirror)
                if HCL.tim_xong(p.stem) is not None:
                    continue
                if (xong_mirror / p.name).is_file():
                    continue
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
            "mql5_pw": ({k: mql5_pw_kq.get(k) for k in
                        ("ok", "tong_ok", "tong_loi", "tong_bo_qua", "can_dang_nhap", "ly_do")}
                       if mql5_pw_kq else None),
            "myfxbook_html": ({k: myfx_kq.get(k) for k in
                               ("ok", "tong_ok", "tong_loi", "tong_bo_qua", "ly_do")}
                              if myfx_kq else None),
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
