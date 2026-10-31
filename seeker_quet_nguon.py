# -*- coding: utf-8 -*-
"""seeker_quet_nguon.py - QUET moi nguon trong config/nguon_seeker.json (HTTP / RSS / API / t.me/s cong khai).

  python seeker_quet_nguon.py [--chi ma1,ma2] [--ep] [--trang-sau GIAY]
Moi ten mien mot luong, tuan tu ben trong (>= 4 s / yeu cau, robots.txt). Nguon `trinh_duyet`/`dang_nhap`
khong quet: ghi CAN DANG NHAP / can may nha. Ket qua: reports/SEEKER_QUET_NGUON.{json,md} (khong URL bai),
ung vien tu sinh + link ma: data/nguon_seeker/ (gitignore). `--trang-sau`: chay phan trang
(nhan/doc_nhieu_trang) cho cac dien dan co mau_trang, voi ham lay ton trong robots.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from nhan import nguon_seeker as NS

LAB = Path(__file__).resolve().parent


def _quet_mien(muc, mang_cho_mien):
    return [NS.quet_mot(ma, s, mang_cho_mien) for ma, s in muc]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chi")
    ap.add_argument("--ep", action="store_true", help="bo qua chu ky quet lai")
    ap.add_argument("--trang-sau", type=float, default=0)
    a = ap.parse_args(argv)
    ds = NS.nap()
    NS.GOC.mkdir(parents=True, exist_ok=True)
    p_tt = NS.GOC / "TRANG_THAI.json"
    tt = {}
    if p_tt.exists():
        try:
            raw = p_tt.read_text(encoding="utf-8-sig").strip()
            if raw:
                tt = json.loads(raw)
            else:
                print("QUET_NGUON skip empty TRANG_THAI.json -> {}", flush=True)
        except Exception as e:
            print("QUET_NGUON skip corrupt TRANG_THAI.json (%s: %s) -> {}" % (type(e).__name__, e), flush=True)
            tt = {}
    bay = time.time()
    nhom = defaultdict(list)
    ket = []
    for ma, s in ds.items():
        if a.chi and ma not in a.chi.split(","):
            continue
        if s["cach"] == "dang_nhap" or (s["cach"] == "trinh_duyet" and s.get("can_dang_nhap")):
            ket.append({"ma": ma, "ten": s.get("ten"), "cach": s["cach"], "url": s.get("url"),
                        "phong_cach": s["phong_cach"], "tai_san": s["tai_san"], "khung": s["khung"], "quan_tri": s["quan_tri"],
                        "trang_thai": NS.CAN_DANG_NHAP if s.get("can_dang_nhap") else NS.BI_CHAN,
                        "ly_do": ("can phien dang nhap cua chu du an" if s.get("can_dang_nhap") else
                                  "the-brain chi doc qua Chrome CDP (JS / chan requests); khong chay trinh duyet tu dong o box")})
            continue
        if not a.ep and not NS.den_han(tt, ma, s, bay):
            continue
        nhom[NS.Mang.mien(NS._url_quet(s)) or ma].append((ma, s))
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(lambda kv: _quet_mien(kv[1], NS.Mang()), nhom.items()):
            ket.extend(r)
    for r in ket:
        tt[r["ma"]] = {"luc_s": bay, "trang_thai": r["trang_thai"]}
    _tmp = p_tt.with_suffix('.json.tmp')
    _tmp.write_text(json.dumps(tt, ensure_ascii=False, indent=1), encoding='utf-8')
    _tmp.replace(p_tt)
    # ung vien tu sinh (quy tac kham pha) + link ma
    ung = {"feed": set(), "telegram": set(), "reddit": set(), "youtube": set(), "github": set()}
    lm = set()
    for r in ket:
        kp = r.pop("kham_pha", None) or {}
        ung["feed"].update(kp.get("feed", []))
        for k, v in (kp.get("xa_hoi") or {}).items():
            ung[k].update(v)
        lm.update(r.pop("link_ma", []) or [])
        r.pop("mau_muc", None)
    da_co = {(s.get("url") or "").rstrip("/") for s in ds.values()}
    ung["feed"] = {u for u in ung["feed"] if u.rstrip("/") not in da_co}
    (NS.GOC / "UNG_VIEN_TU_SINH.json").write_text(json.dumps({k: sorted(v) for k, v in ung.items()}, ensure_ascii=False, indent=1))
    (NS.GOC / "LINK_MA.json").write_text(json.dumps(sorted(lm), indent=1))
    trang = {}
    if a.trang_sau > 0:
        from nhan import doc_nhieu_trang as DNT
        cfg = {}
        for ma, s in ds.items():
            c = NS.chuyen_dien_dan(s)
            if c:
                cfg[ma] = c
        cfg.update(DNT.doc_cau_hinh())
        mg = NS.Mang()

        def lay(u):
            k = mg.lay(u)
            return {"ma": k.get("ma") if k["trang_thai"] != NS.ROBOTS_CAM else 403, "html": k.get("text", ""),
                    "url_cuoi": k.get("url_cuoi", u), "loi": k.get("loi")}
        mg_ngu = lambda x: None   # nhip da nam trong Mang
        tr = DNT.mot_luot(a.trang_sau, lay=lay, ngu=mg_ngu, cau_hinh=cfg)
        trang = {"tien_trang": tr["tien"], "tai": tr["tai"], "chua_do_duoc": len(tr["chua_do_duoc"]),
                 "loi_cau_hinh": tr["loi_cau_hinh"],
                 "theo_nguon": {k: {"trang_thai": b.get("trang_thai"), "den_trang": b.get("den_trang"),
                                    "trang": [(t["so"], t["ket_qua"], t.get("lien_ket")) for t in b["trang"]]}
                                for k, b in tr["nguon"].items()}}
    dem = Counter(r["trang_thai"] for r in ket)
    tong = {"luc": time.strftime("%Y-%m-%d %H:%M"), "so_nguon": len(ds), "da_xet": len(ket), "theo_trang_thai": dict(dem),
            "ung_vien_tu_sinh": {k: len(v) for k, v in ung.items()}, "link_ma_github": len(lm), "phan_trang": trang,
            "theo_phong_cach": {pc: dict(Counter(r["trang_thai"] for r in ket if pc in (r.get("phong_cach") or [])))
                                for pc in sorted({x for r in ket for x in r.get("phong_cach") or []})},
            "nguon": sorted(ket, key=lambda r: (r["trang_thai"], r["ma"]))}
    (LAB / "reports" / "SEEKER_QUET_NGUON.json").write_text(json.dumps(tong, ensure_ascii=False, indent=1))
    d = [f"# SEEKER — quét nguồn {tong['luc']}", "", f"Tổng {len(ds)} nguồn, xét {len(ket)}.", ""]
    d += [f"- {k}: {v}" for k, v in dem.most_common()]
    d += ["", "| mã | cách | phong cách | tài sản | trạng thái | lý do | mục |", "|---|---|---|---|---|---|---|"]
    for r in tong["nguon"]:
        d.append(f"| {r['ma']} | {r.get('cach')} | {','.join(r.get('phong_cach') or [])} | {','.join(r.get('tai_san') or [])} | "
                 f"{r['trang_thai']} | {str(r.get('ly_do',''))[:70]} | {r.get('muc','')} |")
    (LAB / "reports" / "SEEKER_QUET_NGUON.md").write_text("\n".join(d) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in tong.items() if k != "nguon"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
