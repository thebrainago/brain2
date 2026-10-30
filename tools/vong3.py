# -*- coding: utf-8 -*-
"""tools/vong3.py — Vòng 3 scaffold: portfolio + WF/MC/stress on R2 survivors.

Full stress MT5 jobs are emitted only when --sinh-viec and survivors exist.
Portfolio / MC reuse nhan.vong2.

  python tools/vong3.py              # report from existing MT5 trade CSVs
  python tools/vong3.py --sinh-viec  # also write reports/vong3/hang_cho_vong3.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
RA = GOC / "reports" / "vong3"
HANG = RA / "hang_cho_vong3.jsonl"


def survivors_r2(toi_da: int = 30) -> list[dict]:
    import importlib.util
    spec = importlib.util.spec_from_file_location("tv", GOC / "tools" / "vong2.py")
    V = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(V)
    # Prefer rows whose ten/pha looks like vong2, else top passers
    ps = V.chon_passers()
    r2, other = [], []
    for p in ps:
        ten = str(p.get("ten") or "")
        pha = str(p.get("pha") or "")
        if "v2" in ten.lower() or pha.startswith("V2_") or p.get("vong") == 2:
            r2.append(p)
        else:
            other.append(p)
    return (r2 + other)[:toi_da]


def chay(sinh_viec: bool = False) -> dict:
    RA.mkdir(parents=True, exist_ok=True)
    surv = survivors_r2()
    try:
        from nhan import vong2 as V2
        pt = {}
        for p in surv[:12]:
            ten = p.get("ten")
            if not ten:
                continue
            try:
                m = V2.phan_tich_mt5(ten, net_bao_cao=p.get("net"), von=float(p.get("von") or 1000))
            except Exception as e:
                m = {"loi": str(e)[:200]}
            pt[ten] = m
        danh = V2.danh_muc_v2(pt, toi_da=4) if pt else []
    except Exception as e:
        danh, pt = [{"loi": str(e)}], {}

    # Scaffold stress job lines (same schema, vong=3) — thin set
    viec = []
    if sinh_viec:
        import importlib.util
        spec = importlib.util.spec_from_file_location("tv", GOC / "tools" / "vong2.py")
        TV = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(TV)
        bases = TV.nap_viec_goc()
        for p in surv[:10]:
            g = TV.tim_viec_goc(p, bases)
            if not g:
                continue
            for tag, note in (("spr15", "spread_x1.5"), ("fee7", "hoa_hong_7")):
                ten = TV._ten_v2(p.get("ten") or g["ten"], "s3", tag).replace("v2r2", "v3r3")
                v = TV._clone(g, ten=ten, pha="V3_STRESS", diem=80,
                              them={"vong": 3, "vong3_tag": tag, "vong3_note": note,
                                    "vong2_goc": p.get("ten"), "nguon": "vong3"})
                v["ma"] = TV._ma_hash(str(p.get("ma") or v.get("ma") or ""))
                viec.append(v)
        HANG.write_text(
            "".join(json.dumps(x, ensure_ascii=False, sort_keys=True, default=str) + "\n" for x in viec),
            encoding="utf-8",
        )

    md = [
        "# Vòng 3 — portfolio + stress (scaffold)",
        "",
        "Lúc: %s (Asia/Bangkok, UTC+7)." % time.strftime("%Y-%m-%d %H:%M"),
        "",
        "Survivor ứng viên: **%d**. Việc stress sinh: **%d**." % (len(surv), len(viec)),
        "",
        "Xem thiết kế đầy đủ: `reports/VONG_3_4.md`.",
        "",
        "## Danh mục",
        "",
    ]
    for i, d in enumerate(danh[:6], 1):
        if d.get("loi"):
            md.append("%d. %s" % (i, d["loi"]))
        else:
            md.append("%d. %s — APY %s DD %s corr %s" % (
                i, ", ".join(d.get("he") or []), d.get("lai_kep_pct_nam"),
                d.get("dd_equity_pct"), d.get("tuong_quan_ngay_max")))
    (RA / "VONG3_SCAFFOLD.md").write_text("\n".join(md), encoding="utf-8")
    return {"survivors": len(surv), "viec_stress": len(viec), "danh_muc": len(danh),
            "bao_cao": str(RA / "VONG3_SCAFFOLD.md"), "hang_cho": str(HANG) if viec else None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sinh-viec", action="store_true")
    a = ap.parse_args(argv)
    print(json.dumps(chay(a.sinh_viec), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
