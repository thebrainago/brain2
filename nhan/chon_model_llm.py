# -*- coding: utf-8 -*-
"""Chon MOT model LLM manh, co dinh cho dich_llm (20/10/2026 09:56, chu du an: hieu qua hon chi phi).

Chay tren MAY NHA (khoa chi co o do), dau phien:
    python nhan/chon_model_llm.py              # liet ke + A/B + khoa model thang vao config/llm_dich.json
    python nhan/chon_model_llm.py --chi_liet_ke
    python nhan/chon_model_llm.py --neu_cu_hon_gio 24   # bo qua neu da chon trong 24 gio
1) GET <base_url>/models voi khoa (AIBOX_API_KEY hoac cc-switch) - KHONG in / ghi khoa (moi loi qua cau_llm._che).
2) Loc theo config/llm_dich.json "uu_tien" (regex, thu tu = uu tien), bo ten chua "loai_tru" (flash/mini...).
3) A/B tren "so_mau" EA mau co dinh (thu tu sha1) tu hang cho dich: moi ung vien boc_tach + kiem_tra tu dong ->
   ti le DAT, ti le tra JSON, thoi gian, token. Thang: DAT cao nhat, hoa -> nhanh hon.
4) Ghi model thang (+ du phong = ung vien thu hai, chi dung khi loi 5xx) vao config/llm_dich.json,
   reports/ong_dan/CHON_MODEL_LLM.json + .md (bao_cao_phien in lai). Khong goi duoc -> ghi CHUA CHAY DUOC.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
from nhan import cau_llm as LLM  # noqa: E402

CFG = GOC / "config" / LLM.LLM_DICH
KQ_JSON = GOC / "reports" / "ong_dan" / "CHON_MODEL_LLM.json"
KQ_MD = GOC / "reports" / "ong_dan" / "CHON_MODEL_LLM.md"


def doc_cfg(p: Path = CFG) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def _get(url: str, khoa: str, timeout: float = 30) -> tuple[int, dict | str]:
    h = {"Authorization": "Bearer " + khoa} if khoa else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, LLM._che(e.read().decode("utf-8", "replace")[:300], khoa)
        except Exception:
            return e.code, LLM._che(str(e), khoa)
    except Exception as e:  # noqa: BLE001
        return 0, LLM._che(str(e)[:300], khoa)


def liet_ke(get=_get) -> tuple[list[str], str]:
    """-> (ten model, ghi chu). Khong co khoa -> ([], 'CHUA CHAY DUOC ...')."""
    d = LLM.duong()
    if not d["nguon"]:
        return [], "CHUA CHAY DUOC: khong co khoa tren may nay"
    ma, kq = get(d["base_url"] + "/models", d["khoa"])
    if ma != 200 or not isinstance(kq, dict):
        return [], "GET /models HTTP %s: %s" % (ma, LLM._che(str(kq), d["khoa"])[:200])
    ds = sorted({str(x.get("id")) for x in (kq.get("data") or []) if isinstance(x, dict) and x.get("id")})
    return ds, "%d model (nguon khoa: %s)" % (len(ds), d["nguon"].split(":")[0])


def xep_hang(ds: list[str], cfg: dict) -> list[str]:
    """Ung vien theo thu tu 'uu_tien'; trong cung mot mau, so phien ban cao hon dung truoc."""
    loai = [x.lower() for x in cfg.get("loai_tru") or []]
    ra = []

    def _phien(t):
        return [int(x) for x in re.findall(r"\d+", t)]
    for mau in cfg.get("uu_tien") or []:
        r = re.compile(mau, re.I)
        khop = [m for m in ds if r.search(m) and m not in ra and not any(l in m.lower() for l in loai)]
        ra += sorted(khop, key=_phien, reverse=True)
    return ra


def mau_ea(n: int, uu_tien_hong: bool = True) -> list[dict]:
    """n EA co dinh (thu tu sha1 cua noi dung -> lap lai duoc). Uu tien the da HONG truoc day (kho nhat), roi hang cho."""
    from nhan import dich_llm as DL
    from nhan import ong_dan as OD
    cn = OD._db()
    try:
        ds = []
        if uu_tien_hong:
            for t, b, tt, kq in OD.cac_the(cn):
                if (t.get("dich_llm") or {}).get("trang_thai") in ("HONG", "BO_QUA") and DL._tep(t) is not None \
                        and (t["dich_llm"].get("nhom_ly_do") or DL.nhom_ly_do(t["dich_llm"].get("ly_do"))) != "NHIN_TRUOC":
                    ds.append({"the": t, "tep": DL._tep(t)})
        if len(ds) < n:
            ds += [x for x in DL.danh_sach_cho(cn) if x["tep"] is not None]
    finally:
        cn.close()
    if len(ds) < n:                                     # it the cho -> lay them the da dich (bat ky trang thai)
        cn = OD._db()
        try:
            for t, b, tt, kq in OD.cac_the(cn):
                if (t.get("dich_llm") or {}) and DL._tep(t) is not None:
                    ds.append({"the": t, "tep": DL._tep(t)})
        finally:
            cn.close()
    vu = {}
    for x in ds:
        b = x["tep"].read_bytes()[:800000]
        vu.setdefault(hashlib.sha1(b).hexdigest(), (x, b))
    hong_k = [k for k in sorted(vu) if (vu[k][0]["the"].get("dich_llm") or {}).get("trang_thai") in ("HONG", "BO_QUA")]
    khac = [k for k in sorted(vu) if k not in hong_k]
    chon = [vu[k] for k in (hong_k + khac)[:n]]
    return [{"id": x["the"]["id"], "vb": DL.NT.doc_vb(b), "nn": DL.ngon_ngu(x["the"], DL.NT.doc_vb(b))} for x, b in chon]


LUU_AB = GOC / "data" / "ong_dan" / "ab_model"


def ab(ung_vien: list[str], mau: list[dict], cfg: dict, client=None, luu: Path | None = None) -> list[dict]:
    from nhan import dich_llm as DL
    df, _ = DL.gia_mau()
    a = cfg.get("ab") or {}
    ra = []
    for m in ung_vien:
        c = LLM.cau_hinh()
        c.update(model=m, model_du_phong="", han_giay=None)
        c["timeout_giay"] = int(a.get("han_giay_moi_mau", c.get("timeout_giay", 900)))

        def _mot(x):
            t0 = time.time()
            d = LLM.boc_tach(x["vb"], x["nn"], client=client, c=c)
            if luu:                                     # luu dau ra de kiem lai offline (data/ git bo qua)
                f = luu / m.replace("/", "_") / ("%s.json" % x.get("id"))
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            k = DL.kiem_tra(d, df) if d.get("trang_thai") == "OK" else {"dat": False, "ly_do": ["LOI_LLM " + str(d.get("ghi_chu"))[:120]]}
            return {"ok": d.get("trang_thai") == "OK", "dat": bool(k.get("dat")), "giay": time.time() - t0,
                    "nhom": None if k.get("dat") else DL.nhom_ly_do(k.get("ly_do")), "id": x.get("id"),
                    "tr": int(d.get("token_ra") or 0), "tran": "CHAM_TRAN_TOKEN" in str(d.get("ghi_chu"))}
        with ThreadPoolExecutor(max_workers=max(1, int(a.get("luong", 4)))) as ex:
            kq = list(ex.map(_mot, mau))
        n = len(kq) or 1
        ra.append({"model": m, "so_mau": len(kq), "dat": sum(r["dat"] for r in kq), "ok_json": sum(r["ok"] for r in kq),
                   "ti_le_dat_pct": round(100.0 * sum(r["dat"] for r in kq) / n, 1),
                   "giay_tb": round(sum(r["giay"] for r in kq) / n, 1),
                   "token_ra_tb": round(sum(r["tr"] for r in kq) / n), "cham_tran": sum(r["tran"] for r in kq),
                   "ly_do_hong": dict(__import__("collections").Counter(r["nhom"] for r in kq if r["nhom"])),
                   "chi_tiet": [{"id": r["id"], "dat": r["dat"], "nhom": r["nhom"], "giay": round(r["giay"], 1)} for r in kq]})
        print("A/B %s: DAT %d/%d, JSON %d, %.1fs/mau" % (m, ra[-1]["dat"], n, ra[-1]["ok_json"], ra[-1]["giay_tb"]), flush=True)
    return ra


def chon(kq: list[dict]) -> tuple[str, str]:
    """-> (thang, du phong). Model 0 JSON hop le thi khong duoc lam du phong."""
    xh = sorted([r for r in kq if r["ok_json"] > 0], key=lambda r: (-r["dat"], -r["ok_json"], r["giay_tb"]))
    return (xh[0]["model"] if xh else ""), (xh[1]["model"] if len(xh) > 1 else "")


def khoa_vao_cfg(thang: str, du_phong: str, p: Path = CFG) -> None:
    d = doc_cfg(p)
    d["model"], d["model_du_phong"] = thang, du_phong
    d["chon_luc"] = dt.datetime.now().isoformat(timespec="seconds")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def ghi_bao_cao(r: dict) -> None:
    KQ_JSON.parent.mkdir(parents=True, exist_ok=True)
    KQ_JSON.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    d = ["# Chọn model LLM cho dich_llm", "", "Lúc %s (giờ máy nhà). Sinh bởi `nhan/chon_model_llm.py`; số đo thật trên %s EA mẫu "
         "(kiểm tự động trên giá mẫu — tín hiệu là MÔ PHỎNG)." % (r.get("luc"), r.get("so_mau", "?")), "",
         "- Model có trên ai-box: %s" % r.get("ghi_chu_liet_ke"), "- Ứng viên (theo ưu tiên): %s" % (", ".join(r.get("ung_vien") or []) or "không có"),
         "- **Chọn: %s** (dự phòng chỉ khi lỗi 5xx: %s)" % (r.get("thang") or "CHƯA CHỌN ĐƯỢC", r.get("du_phong") or "không"), ""]
    if r.get("ab"):
        d += ["| Model | ĐẠT | JSON hợp lệ | Tỉ lệ ĐẠT | Giây/mẫu | Token ra TB | Chạm trần token |", "|---|---|---|---|---|---|---|"]
        d += ["| %s | %d/%d | %d | %s%% | %s | %s | %d |" % (x["model"], x["dat"], x["so_mau"], x["ok_json"], x["ti_le_dat_pct"],
                                                         x["giay_tb"], x["token_ra_tb"], x["cham_tran"]) for x in r["ab"]]
        d += ["", "Lý do hỏng theo nhóm (bộ kiểm của dich_llm):", ""]
        d += ["- %s: %s" % (x["model"], ", ".join("%s %d" % kv for kv in sorted((x.get("ly_do_hong") or {}).items(), key=lambda z: -z[1])) or "—")
              for x in r["ab"]]
    if r.get("ghi_chu"):
        d += ["", r["ghi_chu"]]
    else:
        d.append("A/B: CHƯA ĐO ĐƯỢC (%s)" % r.get("ly_do", ""))
    KQ_MD.write_text("\n".join(d) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chi_liet_ke", action="store_true")
    ap.add_argument("--neu_cu_hon_gio", type=float, default=0)
    ap.add_argument("--so_mau", type=int)
    a = ap.parse_args(argv)
    cfg = doc_cfg()
    if a.neu_cu_hon_gio and cfg.get("model") and cfg.get("chon_luc"):
        tuoi = (dt.datetime.now() - dt.datetime.fromisoformat(cfg["chon_luc"])).total_seconds() / 3600
        if tuoi < a.neu_cu_hon_gio:
            print("da chon %s %.1f gio truoc - bo qua" % (cfg["model"], tuoi))
            return 0
    ds, gc = liet_ke()
    print(gc)
    uv = xep_hang(ds, cfg)
    print("ung vien:", ", ".join(uv[:8]) or "khong co")
    if a.chi_liet_ke:
        return 0
    r = {"luc": dt.datetime.now().isoformat(timespec="seconds"), "ghi_chu_liet_ke": gc, "tat_ca_model": ds, "ung_vien": uv}
    if not uv:
        r["ly_do"] = "không có ứng viên mạnh khớp 'uu_tien' (%s)" % gc
        ghi_bao_cao(r)
        return 1
    n = int(a.so_mau or (cfg.get("ab") or {}).get("so_mau", 20))
    mau = mau_ea(n)
    r["so_mau"] = len(mau)
    r["ab"] = ab(uv[:int((cfg.get("ab") or {}).get("so_ung_vien", 3))], mau, cfg, luu=LUU_AB)
    r["thang"], r["du_phong"] = chon(r["ab"])
    if r["thang"]:
        khoa_vao_cfg(r["thang"], r["du_phong"])
    else:
        r["ly_do"] = "không ứng viên nào trả JSON hợp lệ"
    ghi_bao_cao(r)
    print("CHON:", r["thang"] or "CHUA CHON DUOC", "| du phong 5xx:", r["du_phong"] or "-")
    return 0 if r["thang"] else 1


if __name__ == "__main__":
    sys.exit(main())
