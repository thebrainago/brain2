# -*- coding: utf-8 -*-
"""tools/vong4.py — Vòng 4 scaffold: demo forward readiness (XM demo 345930355 only).

  python tools/vong4.py
  python tools/vong4.py --sinh-viec
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
RA = GOC / "reports" / "vong4"
HANG = RA / "hang_cho_vong4.jsonl"
DEMO = "345930355"
MA_OK = {
    "EURUSD#", "GBPUSD#", "AUDUSD#", "USDJPY#", "USDCAD#", "USDCHF#", "NZDUSD#",
    "EURGBP#", "EURCAD#", "EURJPY#", "GBPJPY#", "AUDCAD#", "AUDNZD#", "GBPCAD#",
    "EURAUD#", "NZDCAD#", "GOLD.i#", "GBPNZD#",
}


def checklist(he: dict) -> list[dict]:
    ma = str(he.get("ma") or "")
    checks = []
    checks.append({"muc": "demo_only", "ok": True, "chi_tiet": "XM demo %s only — không live/Exness" % DEMO})
    checks.append({"muc": "symbol_hash", "ok": ma in MA_OK or ma.endswith("#"),
                   "chi_tiet": "ma=%s" % ma})
    checks.append({"muc": "khong_toi_uu_forward", "ok": not bool(he.get("toi_uu")),
                   "chi_tiet": "toi_uu rỗng trên forward"})
    von = float(he.get("von") or 0)
    checks.append({"muc": "von_demo", "ok": 1000 <= von <= 100000,
                   "chi_tiet": "von=%s" % von})
    ts = he.get("ts") or {}
    checks.append({"muc": "co_session_cam", "ok": "InpGioCamTu" in ts,
                   "chi_tiet": "cam %s-%s" % (ts.get("InpGioCamTu"), ts.get("InpGioCamDen"))})
    if int(ts.get("InpVao") or 0) == 4:
        checks.append({"muc": "csv_tin_hieu", "ok": bool(ts.get("InpFileCsv") or he.get("csv_vao")),
                       "chi_tiet": str(ts.get("InpFileCsv") or he.get("csv_vao"))})
    return checks


def chay(sinh_viec: bool = False) -> dict:
    RA.mkdir(parents=True, exist_ok=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location("tv", GOC / "tools" / "vong2.py")
    TV = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(TV)
    # Prefer portfolio top from vong3 report if any; else top passers
    ps = TV.chon_passers()[:8]
    bases = TV.nap_viec_goc()
    bang = []
    viec = []
    for p in ps:
        g = TV.tim_viec_goc(p, bases) or {}
        he = {**g, **{k: p.get(k) for k in ("ten", "ma", "tf", "von")}}
        he["ma"] = TV._ma_hash(str(he.get("ma") or "EURUSD#"))
        ck = checklist(he)
        bang.append({"ten": p.get("ten"), "checks": ck,
                     "ok": all(c["ok"] for c in ck)})
        if sinh_viec and g:
            ten = TV._ten_v2(p.get("ten") or g["ten"], "d4", "demo").replace("v2r2", "v4r4")
            v = TV._clone(g, ten=ten, pha="V4_DEMO", diem=85,
                          them={"vong": 4, "demo": DEMO, "nguon": "vong4",
                                "vong2_goc": p.get("ten")})
            v["ma"] = he["ma"]
            # Short recent window for smoke forward-confirm
            v["tu"] = "2026.07.01"
            v["den"] = "2026.10.01"
            viec.append(v)
    if viec:
        HANG.write_text(
            "".join(json.dumps(x, ensure_ascii=False, sort_keys=True, default=str) + "\n" for x in viec),
            encoding="utf-8",
        )
    lines = [
        "# Vòng 4 — demo forward checklist (scaffold)",
        "",
        "Demo **%s** only. Lúc: %s (Asia/Bangkok, UTC+7)." % (DEMO, time.strftime("%Y-%m-%d %H:%M")),
        "",
        "Thiết kế: `reports/VONG_3_4.md`.",
        "",
    ]
    for b in bang:
        lines.append("## `%s` — %s" % (b["ten"], "OK" if b["ok"] else "THIẾU"))
        for c in b["checks"]:
            lines.append("- [%s] %s — %s" % ("x" if c["ok"] else " ", c["muc"], c["chi_tiet"]))
        lines.append("")
    path = RA / "CHECKLIST_DEMO.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"he": len(bang), "ok": sum(1 for b in bang if b["ok"]),
            "viec": len(viec), "bao_cao": str(path)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sinh-viec", action="store_true")
    a = ap.parse_args(argv)
    print(json.dumps(chay(a.sinh_viec), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
