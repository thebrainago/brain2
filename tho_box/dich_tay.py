# -*- coding: utf-8 -*-
"""dich_tay.py - DICH TAY (Grok Bot doc ma MQL va viet spec/python) khi het quota ai-box (20/10/2026 toi).

Ban dich: data/tho_box/dich_tay/<bam>.json (data/ git bo qua) dang JSON nhu cau_llm.MAU_BOC (spec/python/quan_tri/tham_so/...).
  python3 tho_box/dich_tay.py thu <bam>...   - chi kiem (kiem_tinh + kiem_tra hop cat + so lenh toi thieu), khong ghi gi
  python3 tho_box/dich_tay.py ghi <bam>...   - nhan viec trong NHAN_VIEC.jsonl (may box), ghi cache dich_llm voi
                                               model "grokbot-tay", roi chay dich_llm.buoc_dich_llm (KHONG khoa, KHONG goi mang:
                                               chi kiem lai tu cache) -> the DAT ve quyet_dinh cho `tho_box.py thu`.
Khong goi ai-box hay API LLM nao: co_khoa/goi/boc_tach/sua_lai bi thay bang ham bao loi trong tien trinh nay.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))

from nhan import cau_llm as LLM  # noqa: E402
from nhan import dich_llm as DL  # noqa: E402
from nhan import phan_viec as PV  # noqa: E402

MODEL = "grokbot-tay"
THU = GOC / "data" / "tho_box" / "dich_tay"


def _cam(*_a, **_k):
    raise RuntimeError("dich_tay: cam goi LLM")


LLM.co_khoa = lambda *_a, **_k: False
LLM.goi = LLM.boc_tach = LLM.sua_lai = _cam


def doc(h: str) -> dict:
    d = json.loads((THU / (h + ".json")).read_text(encoding="utf-8"))
    sp = d.get("spec")
    sp = sp if isinstance(sp, list) else ([sp] if isinstance(sp, dict) else [])
    d["spec"] = [LLM.chuan_hoa_spec(x) for x in sp]
    d["python"] = d.get("python") or ""
    return d


def thu(hs, df=None):
    if df is None:
        df, ng = DL.gia_mau()
    else:
        ng = "?"
    ra = {}
    for h in hs:
        d = doc(h)
        loi_sp = [e for x in d["spec"] for e in LLM.kiem_spec(x)]
        kt = DL.kiem_tra(d, df)
        ra[h] = {"kiem_tinh": DL.kiem_tinh(d, df), "kiem_spec": loi_sp, "dat": kt["dat"], "kieu": kt["kieu"],
                 "so_lenh": kt["so_lenh"], "ly_do": kt["ly_do"]}
        print(h, json.dumps(ra[h], ensure_ascii=False), flush=True)
    return ra, df, ng


def ghi(hs):
    import sqlite3
    ra, df, ng = thu(hs)
    so = PV.doc_so("dich")
    cn = sqlite3.connect(str(GOC / "data" / "ong_dan" / "tho_box.sqlite"), timeout=120)
    ds = [x for x in DL.danh_sach_cho(cn) if x["tep"] is not None]
    theo = {}
    for x in ds:
        theo.setdefault(DL.bam(x["tep"].read_bytes()[:800000]), []).append(x)
    lam = []
    for h in hs:
        if PV.cua_may_khac("dich", h, "box", so) or h not in theo:
            print("BO", h, "may khac nhan / khong con trong hang"); continue
        if ra[h]["kiem_tinh"] or ra[h]["kiem_spec"]:
            print("BO", h, "kiem tinh truot", ra[h]); continue
        lam.append(h)
    PV.nhan("dich", [(h, [x["the"]["id"] for x in theo[h]]) for h in lam], "box")
    for h in lam:
        d = doc(h)
        cu = DL._doc_cache(h) or {}
        hm = dict(cu.get("hong_theo_model") or {})
        for m in DL.model_khong_ra(cu):
            hm.setdefault(m, "KHONG_RA_SPEC_PY")
        vb = theo[h][0]["tep"].read_bytes()[:800000]
        moi = dict(d, trang_thai="OK", model=MODEL, nhan="dich tay (%s) - can MT5 xac nhan" % MODEL,
                   ngon_ngu=DL.ngon_ngu(theo[h][0]["the"], DL.NT.doc_vb(vb)), phien=LLM.PHIEN_PROMPT,
                   luc=time.strftime("%Y-%m-%dT%H:%M:%S"), token_vao=0, token_ra=0, ghi_chu="dich tay, khong goi API")
        if hm:
            moi["hong_theo_model"] = hm
        if cu:
            moi["cache_truoc"] = {k: cu.get(k) for k in ("model", "luc", "trang_thai")}
        DL._ghi_cache(h, moi)
    if not lam:
        return {}
    chon = [x for h in lam for x in theo[h]]
    goc = DL.danh_sach_cho
    DL.BAO_CAO = PV.THU_MUC / "DICH_LLM_BOX.md"
    DL.danh_sach_cho = lambda _cn, _c=chon: list(_c)
    try:
        dem = DL.buoc_dich_llm(cn, luong=1, c={"model": MODEL})
    finally:
        DL.danh_sach_cho = goc
        cn.close()
    with open(GOC / "data" / "tho_box" / "dich_tay.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "bam": lam, "dem": dem}, ensure_ascii=False) + "\n")
    return dem


def nhan_truoc(hs):
    """Nhan viec TRUOC khi doc ma (may khac thay khoa -> bo qua)."""
    import sqlite3
    so = PV.doc_so("dich")
    cn = sqlite3.connect(str(GOC / "data" / "ong_dan" / "tho_box.sqlite"), timeout=120)
    theo = {}
    for x in DL.danh_sach_cho(cn):
        if x["tep"] is not None:
            theo.setdefault(DL.bam(x["tep"].read_bytes()[:800000]), []).append(x["the"]["id"])
    cn.close()
    ok = [h for h in hs if h in theo and not PV.cua_may_khac("dich", h, "box", so)]
    print("nhan", PV.nhan("dich", [(h, theo[h]) for h in ok], "box"), "bo", sorted(set(hs) - set(ok)))


if __name__ == "__main__":
    {"thu": thu, "ghi": ghi, "nhan": nhan_truoc}[sys.argv[1]](sys.argv[2:])
