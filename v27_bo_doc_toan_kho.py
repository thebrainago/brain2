# -*- coding: utf-8 -*-
"""Vong 27 chu ky 3: do ty le dich cua bo doc tren TOAN KHO EA da tai (data/cau_kho, git bo qua).
Ghi tong ket + phan loai ly do (khong ghi ma EA). Dung: python v27_bo_doc_toan_kho.py [nhan_ra]"""
import glob, hashlib, json, os, re, signal, sys, time, collections
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nhan import tien_xu_ly_ea as TX, doc_ma as DM, mql4_chuan as MQ4, cau_kho_ma as CK

_DAT = re.compile(r"\b(OrderSend|PositionOpen|\.Buy|\.Sell|\.BuyLimit|\.SellLimit|\.BuyStop|\.SellStop|OrderOpen)\s*\(")


def _het(*a): raise TimeoutError


def loai_ly_do(s):
    s = str(s)
    if s.startswith("loi "): return s
    for k, rx in [("huong_bien_cuc_bo", r"^!?\s*\w+\s*(>|<|!=|==)\s*-?\d|^!\s*\w+$|^\w+$"),
                  ("goi_ham", r"^goi ham"), ("khong_guard", r"khong tim duoc guard"), ("loc_thoat_som", r"^loc thoat som"),
                  ("huong_int", r"^huong int"), ("chieu_lenh", r"khong xac dinh duoc chieu")]:
        if re.search(rx, s): return k
    return "dieu_kien_khac"


def mot(f):
    signal.signal(signal.SIGALRM, _het); signal.alarm(20)
    try:
        vb = open(f, encoding="utf-8", errors="ignore").read()
        if "OnTick" not in vb and "start()" not in vb and "OnTimer" not in vb: return {"tep": f, "loai": "khong_ea"}
        cong_cu = not _DAT.search(vb)
        m4 = CK.la_mql4(vb) or f.lower().endswith(".mq4")
        if m4: vb = MQ4.chuan_hoa(vb)
        vb, log = TX.bien_doi(vb)
        dd = DM.doc_chien_luoc(vb, nguon=f); sp = dd.get("co_che") or []
        ly = [str(z)[:100] for z in (dd.get("chua_dien_dat_duoc") or [])][:2]
        return {"tep": f, "loai": "cong_cu" if cong_cu else "ea", "so_luat": len(sp), "ly_do": ly, "bien_doi": log}
    except Exception as e:
        return {"tep": f, "loai": "ea", "so_luat": 0, "ly_do": ["loi " + type(e).__name__]}
    finally:
        signal.alarm(0)


def main(nhan="sau"):
    T = sorted(f for f in set(glob.glob("data/cau_kho/**/*.mq[45]", recursive=True)) if os.path.isfile(f))
    seen, F = set(), []
    for f in T:
        h = hashlib.md5(open(f, "rb").read()).hexdigest()
        if h not in seen: seen.add(h); F.append(f)
    t0 = time.time()
    with ProcessPoolExecutor(8) as ex: R = list(ex.map(mot, F, chunksize=8))
    ea = [r for r in R if r["loai"] == "ea"]; cc = [r for r in R if r["loai"] == "cong_cu"]
    ld = collections.Counter(loai_ly_do(r["ly_do"][0]) if r.get("ly_do") else "khong_ly_do" for r in ea if r["so_luat"] == 0)
    tk = {"tep_duy_nhat": len(F), "khong_ea": sum(r["loai"] == "khong_ea" for r in R), "cong_cu_khong_lenh": len(cc),
          "ea_co_lenh": len(ea), "dich_duoc": sum(r["so_luat"] > 0 for r in ea), "so_luat": sum(r["so_luat"] for r in ea),
          "ty_le_tren_ea_co_lenh": round(sum(r["so_luat"] > 0 for r in ea) / max(1, len(ea)), 4),
          "ly_do_hong": dict(ld.most_common()), "giay": round(time.time() - t0, 1)}
    os.makedirs("data/bo_doc_do", exist_ok=True)
    json.dump({"nhan": nhan, "tong_ket": tk, "tep": [{"tep": os.path.basename(r["tep"]), "loai": r["loai"], "so_luat": r.get("so_luat", 0), "ly_do": r.get("ly_do", [])} for r in R]},
              open(f"data/bo_doc_do/TOAN_KHO_{nhan}.json", "w"), ensure_ascii=False, indent=0)
    print(json.dumps(tk, ensure_ascii=False))


if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["sau"]))
