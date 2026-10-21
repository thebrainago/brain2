# -*- coding: utf-8 -*-
"""phan_viec.py - CHIA VIEC KHONG TRUNG giua may nha va box (20/10/2026 toi, Grok Bot).

So dang ky (chi METADATA, commit vao git): reports/phan_viec/NHAN_VIEC.jsonl, moi dong
  {"loai": "dich"|"thu_py", "khoa": <bam ma nguon (dich) | the_id (thu_py)>, "may": "box"|"nha", "luc": ..., "the": [...]}
Luat: khoa da co trong so (bat ky may nao) thi may khac KHONG lam lai. Dong dau tien thang (append-only, git rebase giu thu tu).
Box lay viec tu CUOI hang cho (dich_llm.danh_sach_cho), may nha lay tu DAU -> hai dau khong gap nhau cho toi khi gan het hang.

Hang MT5 cua box: reports/phan_viec/hang_cho_mt5_box.jsonl (cung dinh dang reports/ong_dan/hang_cho_mt5.jsonl).
May nha phien sau: `doc_hang_box()` (hoac gop vao sinh_viec.tu_ong_dan) - phien dang chay KHONG doc tep nay.
Khong chua ma nguon nguoi khac; ma EA chi o data/ (git bo qua).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
THU_MUC = GOC / "reports" / "phan_viec"
SO = THU_MUC / "NHAN_VIEC.jsonl"
HANG_BOX = THU_MUC / "hang_cho_mt5_box.jsonl"


def doc_so(loai: str | None = None, p: Path | None = None) -> dict:
    """-> {khoa: may} (dong dau tien thang)."""
    p = Path(p or SO)
    ra: dict = {}
    if not p.exists():
        return ra
    for x in p.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(x)
        except ValueError:
            continue
        if loai and d.get("loai") != loai:
            continue
        ra.setdefault(str(d.get("khoa")), d.get("may"))
    return ra


def nhan(loai: str, cac: list[tuple[str, list]], may: str, p: Path | None = None) -> list[str]:
    """Ghi nhan cac khoa chua ai nhan. cac = [(khoa, [the_id...])]. -> khoa da nhan duoc."""
    p = Path(p or SO)
    p.parent.mkdir(parents=True, exist_ok=True)
    da = doc_so(loai, p)
    moi = [(k, t) for k, t in cac if str(k) not in da]
    if moi:
        luc = time.strftime("%Y-%m-%dT%H:%M:%S")
        with open(p, "a", encoding="utf-8") as f:
            for k, t in moi:
                f.write(json.dumps({"loai": loai, "khoa": str(k), "may": may, "luc": luc, "the": list(t)[:20]},
                                   ensure_ascii=False, sort_keys=True) + "\n")
    return [k for k, _ in moi]


def cua_may_khac(loai: str, khoa: str, may: str, so: dict | None = None) -> bool:
    so = doc_so(loai) if so is None else so
    m = so.get(str(khoa))
    return m is not None and m != may


def doc_hang_box(p: Path | None = None, san: str | None = None) -> list[dict]:
    """Viec MT5 do box sinh (ea=XL), cung dinh dang tu_ong_dan; loc theo san neu co."""
    p = Path(p or HANG_BOX)
    if not p.exists():
        return []
    out = []
    for x in p.read_text(encoding="utf-8").splitlines():
        try:
            v = json.loads(x)
        except ValueError:
            continue
        if san and str(v.get("san", "")).lower() != san.lower():
            continue
        if v.get("ea") == "XL" and v.get("ma"):
            v.setdefault("nguon", "box")
            out.append(v)
    return out
