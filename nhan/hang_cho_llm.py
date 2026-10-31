# -*- coding: utf-8 -*-
"""hang_cho_llm.py - LLM qua hang cho FILE (khong can API key).

Bat bang bien moi truong: BRAIN_LLM_PROVIDER=hang_cho

Thay vi goi mang, ghi yeu cau vao hang_cho_llm/cho/<id>.json. Worker (Evolution
bot / LLM) doc, tra loi bang CLI `tra_loi`, ghi hang_cho_llm/xong/<id>.json.
Lan goi sau cung bam (prompt+task) doc tu xong/ va tra van_ban.

Trang thai tra ve:
  - CHO  / pending=True  : dang cho worker
  - OK                 : da co tra loi hop le
  - LOI                : worker ghi loi/ hoac tra loi khong hop le
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

GOC_LAB = Path(__file__).resolve().parent.parent
GOC = GOC_LAB / "hang_cho_llm"
CHO = GOC / "cho"
XONG = GOC / "xong"
LOI = GOC / "loi"

#: Ten bien moi truong. Gia tri chap nhan: hang_cho | file | queue
BIEN_PROVIDER = "BRAIN_LLM_PROVIDER"
GIA_TRI_HANG_CHO = frozenset({"hang_cho", "file", "queue"})

#: Schema mong doi theo loai viec (HUONG_DAN.md mo rong).
SCHEMA_THEO_LOAI = {
    "nghi_de_xuat": {
        "mo_ta": "JSON object voi de_xuat[] va ly_do_chon",
        "kieu": "json_object",
        "bat_buoc": ["de_xuat"],
        "mau": {"de_xuat": [{"ten": "str", "ho": "str", "co_che": "str", "vao": [], "nguon": ""}],
                "ly_do_chon": "str"},
    },
    "dich_boc": {
        "mo_ta": "JSON dich chien luoc (spec/python/luoi/...) nhu cau_llm.MAU_BOC",
        "kieu": "json_object",
        "bat_buoc": [],
        "mau": {"loai": "co_che", "spec": [], "python": "", "luoi": {}, "chua_dich": []},
    },
    "dich_sua": {
        "mo_ta": "JSON sua lai sau khi bo kiem that bai (cung dang dich_boc)",
        "kieu": "json_object",
        "bat_buoc": [],
        "mau": {"loai": "co_che", "spec": [], "python": "", "luoi": {}, "chua_dich": []},
    },
    "tri_tue_hoi": {
        "mo_ta": "Van ban tu do hoac JSON neu ep_json",
        "kieu": "text_or_json",
        "bat_buoc": [],
    },
    "khac": {"mo_ta": "Van ban tu do", "kieu": "text", "bat_buoc": []},
}


def dang_bat() -> bool:
    return (os.environ.get(BIEN_PROVIDER) or "").strip().lower() in GIA_TRI_HANG_CHO


def dam_bao_thu_muc() -> None:
    for p in (CHO, XONG, LOI):
        p.mkdir(parents=True, exist_ok=True)


def bam_yeu_cau(loai_viec: str, he_thong: str, nhac: str) -> str:
    """id = sha256(loai|he_thong|nhac)[:24] — cung prompt+task -> cung id."""
    raw = (str(loai_viec or "") + "\0" + str(he_thong or "") + "\0" + str(nhac or "")).encode("utf-8", "replace")
    return hashlib.sha256(raw).hexdigest()[:24]


def _doc_json(p: Path) -> dict | None:
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _ghi_json(p: Path, d: dict) -> None:
    dam_bao_thu_muc()
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(p)


def duong_cho(i: str) -> Path:
    return CHO / ("%s.json" % i)


def duong_xong(i: str) -> Path:
    return XONG / ("%s.json" % i)


def duong_loi(i: str) -> Path:
    return LOI / ("%s.json" % i)


def _trich_van_ban(d: dict) -> str:
    if not isinstance(d, dict):
        return ""
    for k in ("van_ban", "tra_loi", "content", "text", "answer"):
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    if isinstance(d.get("json"), (dict, list)):
        return json.dumps(d["json"], ensure_ascii=False)
    # Worker co the ghi thang object ket qua (de_xuat / spec) khong boc van_ban
    if any(k in d for k in ("de_xuat", "spec", "python", "loai")):
        skip = {"id", "bam", "tra_loi_luc", "nguoi_tra", "ok", "ghi_chu"}
        body = {k: v for k, v in d.items() if k not in skip}
        if body:
            return json.dumps(body, ensure_ascii=False)
    return ""


def doc_tra_loi(i: str) -> dict | None:
    """Doc xong/<id> neu co. Tra dict chuan hoa hoac None."""
    p = duong_xong(i)
    if not p.exists():
        return None
    d = _doc_json(p)
    if not d:
        return {"trang_thai": "LOI", "van_ban": "", "id": i, "ghi_chu": "xong/%s.json khong doc duoc" % i,
                "duong": "hang_cho"}
    vb = _trich_van_ban(d)
    if not vb:
        return {"trang_thai": "LOI", "van_ban": "", "id": i, "ghi_chu": "xong/%s.json thieu van_ban/json" % i,
                "duong": "hang_cho", "pending": False}
    ra = {"trang_thai": "OK", "van_ban": vb, "id": i, "bam": d.get("bam") or i,
          "duong": "hang_cho", "model": d.get("model") or "hang_cho",
          "token_vao": 0, "token_ra": 0, "ghi_chu": "tu hang_cho_llm/xong",
          "pending": False}
    if isinstance(d.get("json"), (dict, list)):
        ra["json"] = d["json"]
    return ra


def dang_cho(i: str) -> bool:
    return duong_cho(i).exists() and not duong_xong(i).exists()


def xep_hang(loai_viec: str, he_thong: str, nhac: str, *, tru: str = "",
             schema: dict | None = None, model_goi_y: str = "",
             ep_json: bool = False, max_tokens: int | None = None,
             them: dict | None = None) -> dict:
    """Ghi cho/<id>.json neu chua co; neu da co xong -> tra OK; neu dang cho -> CHO.

    Khong crash, khong goi mang, khong retry storm (cung id chi ghi 1 lan).
    """
    dam_bao_thu_muc()
    loai = str(loai_viec or "khac")
    i = bam_yeu_cau(loai, he_thong or "", nhac or "")
    x = doc_tra_loi(i)
    if x and x.get("trang_thai") == "OK":
        return x
    if x and x.get("trang_thai") == "LOI" and duong_xong(i).exists():
        return x

    pc = duong_cho(i)
    if pc.exists():
        return {"trang_thai": "CHO", "van_ban": "", "id": i, "bam": i, "pending": True,
                "duong": "hang_cho", "model": "hang_cho", "token_vao": 0, "token_ra": 0,
                "ghi_chu": "dang cho worker (hang_cho_llm/cho/%s.json)" % i}

    sch = schema if schema is not None else SCHEMA_THEO_LOAI.get(loai, SCHEMA_THEO_LOAI["khac"])
    yc = {
        "id": i,
        "bam": i,
        "tao_luc": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tru": tru or "",
        "loai_viec": loai,
        "he_thong": he_thong or "",
        "nhac": nhac or "",
        "ep_json": bool(ep_json),
        "schema_mong_doi": sch,
        "model_goi_y": model_goi_y or "",
        "max_tokens": int(max_tokens or 0) or None,
    }
    if them:
        yc["them"] = them
    _ghi_json(pc, yc)
    return {"trang_thai": "CHO", "van_ban": "", "id": i, "bam": i, "pending": True,
            "duong": "hang_cho", "model": "hang_cho", "token_vao": 0, "token_ra": 0,
            "ghi_chu": "da xep hang_cho_llm/cho/%s.json" % i}


# ------------------------------------------------------------------ KIEM TRA
def _json_trong_vb(van_ban: str) -> dict | list | None:
    t = (van_ban or "").strip()
    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) >= 2:
            t = parts[1]
            if t.lower().startswith("json"):
                t = t[4:]
            t = t.strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def kiem_tra_loi(loai_viec: str, van_ban: str, ep_json: bool = False) -> list[str]:
    """Tra list loi (rong = hop le)."""
    loi: list[str] = []
    if not (van_ban or "").strip():
        return ["van_ban rong"]
    sch = SCHEMA_THEO_LOAI.get(loai_viec) or SCHEMA_THEO_LOAI["khac"]
    kieu = sch.get("kieu") or "text"
    can_json = bool(ep_json) or kieu in ("json_object",) or loai_viec in ("nghi_de_xuat", "dich_boc", "dich_sua")
    if can_json:
        js = _json_trong_vb(van_ban)
        if js is None:
            loi.append("khong parse duoc JSON")
        elif not isinstance(js, dict):
            loi.append("JSON khong phai object")
        else:
            for k in sch.get("bat_buoc") or []:
                if k not in js:
                    loi.append("thieu khoa bat buoc: %s" % k)
            if loai_viec == "nghi_de_xuat" and not isinstance(js.get("de_xuat"), list):
                loi.append("de_xuat phai la list")
    return loi


# ----------------------------------------------------------------------- CLI
def liet_ke() -> int:
    dam_bao_thu_muc()
    ds = []
    for p in CHO.glob("*.json"):
        if p.name.startswith("."):
            continue
        d = _doc_json(p) or {}
        st = p.stat()
        ds.append({
            "id": d.get("id") or p.stem,
            "tao_luc": d.get("tao_luc") or time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
            "tru": d.get("tru") or "",
            "loai_viec": d.get("loai_viec") or "",
            "bytes": st.st_size,
            "nhac_ky_tu": len(d.get("nhac") or ""),
            "he_thong_ky_tu": len(d.get("he_thong") or ""),
        })
    ds.sort(key=lambda x: x.get("tao_luc") or "")
    print(json.dumps({"cho": len(ds), "danh_sach": ds}, ensure_ascii=False, indent=1))
    return 0


def xem(i: str) -> int:
    p = duong_cho(i)
    if not p.exists():
        # thu xong/loi de debug
        for alt in (duong_xong(i), duong_loi(i)):
            if alt.exists():
                print(alt.read_text(encoding="utf-8"))
                return 0
        print(json.dumps({"loi": "khong thay id %s trong cho/xong/loi" % i}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(p.read_text(encoding="utf-8"))
    return 0


def tra_loi(i: str, tep: str) -> int:
    dam_bao_thu_muc()
    yc_p = duong_cho(i)
    yc = _doc_json(yc_p) if yc_p.exists() else None
    if yc is None and not duong_xong(i).exists():
        # Cho phep tra loi neu co ban ghi o loi/ (thu lai) hoac chi co id
        yc = {"id": i, "bam": i, "loai_viec": "khac", "ep_json": False}

    src = Path(tep)
    if not src.exists():
        print(json.dumps({"loi": "khong thay file %s" % tep}, ensure_ascii=False), file=sys.stderr)
        return 1
    raw = src.read_text(encoding="utf-8-sig")
    # File tra loi: JSON {"van_ban":...} / {"json":...} / hoac van ban thuan / hoac object ket qua
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = None

    if isinstance(parsed, dict) and any(k in parsed for k in ("van_ban", "tra_loi", "content", "text", "answer", "json")):
        vb = _trich_van_ban(parsed)
        meta = {k: parsed[k] for k in ("model", "nguoi_tra", "ghi_chu") if k in parsed}
        js = parsed.get("json")
    elif isinstance(parsed, dict):
        vb = json.dumps(parsed, ensure_ascii=False)
        meta = {}
        js = parsed
    else:
        vb = raw.strip()
        meta = {}
        js = None

    loai = (yc or {}).get("loai_viec") or "khac"
    ep = bool((yc or {}).get("ep_json"))
    loi = kiem_tra_loi(loai, vb, ep_json=ep)
    if loi:
        out = {"id": i, "bam": (yc or {}).get("bam") or i, "ok": False, "loi": loi,
               "van_ban": vb[:2000], "tra_loi_luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
        _ghi_json(duong_loi(i), out)
        print(json.dumps({"trang_thai": "LOI", "id": i, "loi": loi, "ghi": str(duong_loi(i))},
                         ensure_ascii=False, indent=1))
        return 2

    out = {"id": i, "bam": (yc or {}).get("bam") or i, "ok": True, "van_ban": vb,
           "tra_loi_luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "nguoi_tra": meta.get("nguoi_tra") or "evo",
           "model": meta.get("model") or "hang_cho"}
    if js is not None:
        out["json"] = js
    elif ep or loai in ("nghi_de_xuat", "dich_boc", "dich_sua"):
        j2 = _json_trong_vb(vb)
        if isinstance(j2, (dict, list)):
            out["json"] = j2
    _ghi_json(duong_xong(i), out)
    # bo khoi cho/ sau khi xong (giu id o xong/)
    try:
        if yc_p.exists():
            yc_p.unlink()
    except OSError:
        pass
    print(json.dumps({"trang_thai": "OK", "id": i, "ghi": str(duong_xong(i)), "van_ban_ky_tu": len(vb)},
                     ensure_ascii=False, indent=1))
    return 0


#: Cho qua lau trong cho/ ma chua co tra loi -> canh bao Evo/mach.
HAN_CHO_STALE_GIAY = 30 * 60


def suc_khoe(stale_giay: int | None = None) -> dict:
    """Do suc khoe hang cho LLM (thay cho kiem OPENAI_API_KEY).

    Khi `BRAIN_LLM_PROVIDER=hang_cho`, thieu API key KHONG phai loi. Loi that
    la: (1) yeu cau nam trong `cho/` qua lau (worker khong tra loi), (2) co
    file trong `loi/` (tra loi khong hop le / worker bao loi).
    """
    dam_bao_thu_muc()
    han = int(HAN_CHO_STALE_GIAY if stale_giay is None else stale_giay)
    now = time.time()
    cho, loi, stale = [], [], []
    for pth in CHO.glob("*.json"):
        if pth.name.startswith("."):
            continue
        cho.append(pth)
        try:
            if (now - pth.stat().st_mtime) > han:
                stale.append(pth.name)
        except OSError:
            stale.append(pth.name)
    for pth in LOI.glob("*.json"):
        if not pth.name.startswith("."):
            loi.append(pth.name)
    ok = (len(stale) == 0 and len(loi) == 0)
    return {
        "provider": "hang_cho",
        "dang_bat": dang_bat(),
        "cho_n": len(cho),
        "loi_n": len(loi),
        "cho_stale_n": len(stale),
        "stale_giay": han,
        "cho_stale": stale[:20],
        "loi": loi[:20],
        "ok": ok,
        "mo_ta": ("hang_cho khoe (cho=%d stale=%d loi=%d)" % (len(cho), len(stale), len(loi))
                  if ok else
                  "hang_cho HONG: cho=%d stale=%d (>%ds) loi=%d" % (
                      len(cho), len(stale), han, len(loi))),
    }


def thong_ke() -> int:
    dam_bao_thu_muc()

    def _dem(thu: Path) -> dict:
        theo = {}
        n, byt = 0, 0
        for p in thu.glob("*.json"):
            if p.name.startswith("."):
                continue
            n += 1
            byt += p.stat().st_size
            d = _doc_json(p) or {}
            lv = d.get("loai_viec") or "(khong ro)"
            theo[lv] = theo.get(lv, 0) + 1
        return {"so": n, "bytes": byt, "theo_loai": theo}

    ra = {"cho": _dem(CHO), "xong": _dem(XONG), "loi": _dem(LOI),
          "provider_bat": dang_bat(), "bien": BIEN_PROVIDER,
          "gia_tri": os.environ.get(BIEN_PROVIDER) or ""}
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hang_cho_llm", description="Hang cho LLM bang file (Evolution worker)")
    sub = ap.add_subparsers(dest="lenh", required=True)
    sub.add_parser("liet_ke", help="Liet ke yeu cau dang cho (cu nhat truoc)")
    p_xem = sub.add_parser("xem", help="In yeu cau theo id")
    p_xem.add_argument("id")
    p_tl = sub.add_parser("tra_loi", help="Ghi cau tra loi (validate + xong/)")
    p_tl.add_argument("id")
    p_tl.add_argument("file", help="File van ban hoac JSON tra loi")
    sub.add_parser("thong_ke", help="Dem cho/xong/loi")
    a = ap.parse_args(argv)
    if a.lenh == "liet_ke":
        return liet_ke()
    if a.lenh == "xem":
        return xem(a.id)
    if a.lenh == "tra_loi":
        return tra_loi(a.id, a.file)
    if a.lenh == "thong_ke":
        return thong_ke()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
