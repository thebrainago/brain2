# -*- coding: utf-8 -*-
"""Vong 27: doc lai cac EA Seeker v26 (data/cau_kho) VOI tien xu ly nhan/tien_xu_ly_ea; so truoc/sau. Chi ghi TOM TAT luat + URL."""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seeker_v26 as S
from nhan import tien_xu_ly_ea as TX, doc_ma as DM, mql4_chuan as MQ4, cau_kho_ma as CK


def doc_tep(f, tx):
    vb = open(f, encoding="utf-8", errors="ignore").read()
    if "OnTick" not in vb and "start()" not in vb and "OnTimer" not in vb: return None
    m4 = CK.la_mql4(vb) or f.lower().endswith(".mq4"); log = []
    if m4: vb = MQ4.chuan_hoa(vb)
    if tx: vb, log = TX.bien_doi(vb)
    try:
        dd = DM.doc_chien_luoc(vb, nguon=f); sp = dd.get("co_che") or []; ly = [str(z)[:100] for z in (dd.get("chua_dien_dat_duoc") or [])][:2]
    except Exception as e:
        sp, ly = [], ["loi " + type(e).__name__]
    return {"tep": os.path.basename(f), "so_luat": len(sp), "luat": [S.tom_tat(s) for s in sp], "ly_do": ly, "bien_doi": log}


def main():
    L = json.load(open(S.RA + "LUAT_TRICH.json"))["luat"]; R = []
    for r in L:
        m = re.search(r"/code/(\d+)$", r["url"]); g = re.match(r"https://github.com/([^/]+)/([^/#?]+)", r["url"])
        d = S.G5 + m.group(1) if m else S.GG + f"{g.group(1)}__{g.group(2)}"
        f = os.path.join(d, re.sub(r"[^A-Za-z0-9_.-]+", "_", r["tep"])[:100])
        if not os.path.exists(f):
            c = [x for x in glob.glob(d + "/*") if os.path.basename(x) == r["tep"]]; f = c[0] if c else None
        if not f: continue
        a, b = doc_tep(f, False), doc_tep(f, True)
        if a and b: R.append({"url": r["url"], "truoc": a["so_luat"], "sau": b["so_luat"], "luat": b["luat"], "bien_doi": b["bien_doi"], "ly_do_sau": b["ly_do"], "tep": r["tep"]})
    tk = {"tep": len(R), "dich_truoc": sum(x["truoc"] > 0 for x in R), "dich_sau": sum(x["sau"] > 0 for x in R),
          "luat_truoc": sum(x["truoc"] for x in R), "luat_sau": sum(x["sau"] for x in R),
          "mat": [x["tep"] for x in R if x["truoc"] > 0 and x["sau"] == 0], "moi": [x["tep"] for x in R if x["truoc"] == 0 and x["sau"] > 0]}
    os.makedirs("reports/seeker_v27", exist_ok=True)
    json.dump({"nhan": "TOM TAT LUAT + URL", "tong_ket": tk, "tep": R}, open("reports/seeker_v27/DOC_LAI.json", "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(tk, ensure_ascii=False))


if __name__ == "__main__":
    main()
