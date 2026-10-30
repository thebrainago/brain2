# -*- coding: utf-8 -*-
"""viet_viec_tin_hieu.py - Ghi việc MT5 tester từ spec tin hiệu công khai.

Ghi vào reports/vong2/hang_cho_tin_hieu.jsonl (HÀNG RIÊNG — không sửa hang_cho_vong2
hay ong_dan). Cùng schema việc vòng 2 để máy nhà/tester có thể merge khi owner muốn.

Chỉ demo 345930355; không live.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
HANG = GOC / "reports" / "vong2" / "hang_cho_tin_hieu.jsonl"


def mau_viec(*, the_id: str, ma: str, tf: str = "H1", san: str = "XM",
             track: str = "thuong", nguon_he: str = "",
             tu: str = "2023.01.01", den: str = "2026.10.01",
             von: float = 10000.0, don_bay: int = 500) -> dict:
    """Một dòng việc — khớp khóa hang_cho_vong2.jsonl."""
    ten = "th_%s_%s_%s_%s" % (track[:3], the_id[:24], ma.lower().replace("#", ""), san)
    return {
        "den": den,
        "tu": tu,
        "diem": 50.0,
        "don_bay": don_bay,
        "ea": "XL",
        "ea_file": "BRAIN_XuLiLenh",
        "ma": ma if ma.endswith("#") else (ma + "#" if san == "XM" else ma),
        "ma_box": ma.replace("#", ""),
        "nguon": "tin_hieu_cong_khai",
        "pha": "TH_DCA" if track == "dca" else "TH_THUONG",
        "python": {"lai_pct_nam": 0.0, "lot0": 0.01, "so_stop_out": 0, "sut_giam_pct": 0.0},
        "san": san,
        "ten": ten,
        "tf": tf,
        "the_id": the_id[:48],
        "tien": "USD",
        "toi_uu": False,
        "ts": {},
        "von": von,
        "vong": 2,
        "vong2_goc": nguon_he,
        "vong2_loai": "dca_go_lenh" if track == "dca" else "tin_hieu",
        "vong2_tag": "tin_hieu_%s" % track,
    }


def ghi_viec(viec: dict | list[dict], *, hang: Path | None = None) -> Path:
    hang = Path(hang) if hang else HANG
    hang.parent.mkdir(parents=True, exist_ok=True)
    ds = viec if isinstance(viec, list) else [viec]
    with hang.open("a", encoding="utf-8") as f:
        for v in ds:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    return hang


def ghi_tu_dich(ket_dich: list[dict], *, hang: Path | None = None,
                ma_mac: str = "EURUSD") -> dict:
    """Từ kết quả dich_nguoc (có id hang_cho) → việc tester placeholder.

    Spec thật vào QUANTLAB sau khi Grok trả xong/; đây chỉ xếp chỗ test
    theo symbol phổ biến của hệ.
    """
    ra = []
    for d in ket_dich:
        if d.get("trang_thai") not in ("CHO", "OK", "pending", None) and d.get("id") is None:
            # vẫn ghi nếu có id
            if not d.get("id"):
                continue
        he = d.get("he_id") or "unknown"
        track = d.get("track") or "thuong"
        the_id = "th_%s_%s" % (track, he)[:40]
        # symbol từ ho_so nếu có
        ma = ma_mac
        hp = d.get("ho_so_path")
        if hp and Path(hp).exists():
            try:
                ho = json.loads(Path(hp).read_text(encoding="utf-8"))
                syms = ho.get("symbols") or []
                if syms and isinstance(syms[0], (list, tuple)):
                    ma = str(syms[0][0]).split(".")[0].split("#")[0]
                elif isinstance(ho.get("module"), dict):
                    mau = ho.get("mau_basket") or []
                    if mau:
                        ma = str(mau[0].get("symbol") or ma).split(".")[0]
            except Exception:
                pass
        ra.append(mau_viec(the_id=the_id, ma=ma, track=track,
                           nguon_he="%s/%s" % (d.get("nguon") or "fxblue", he)))
    path = ghi_viec(ra, hang=hang) if ra else (hang or HANG)
    return {"so_viec": len(ra), "hang": str(path), "viet_luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
