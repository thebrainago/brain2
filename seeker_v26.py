# -*- coding: utf-8 -*-
"""Seeker vong 26 (tren box): tu reports/seeker_may_nha (tieu de+URL quet o may nha) -> tai ma CONG KHAI truy cap duoc
(mql5 Code Base: trang bai; GitHub: API qua `gh`), doc bang nhan.doc_ma (cung bo doc vong 25, khong tune), gan nhan
phong cach/tai san/khung/quan tri bang nhan.nguon_seeker.gan_nhan. KHONG vuot Cloudflare: TradingView/fxblue/... 403 -> ghi
'CHUA DO DUOC'. Ma nguon EA ben thu ba chi luu o data/cau_kho/ (git bo qua); repo chi nhan TOM TAT luat + URL."""
from __future__ import annotations
import base64, glob, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nhan import doc_ma as DM, cau_kho_ma as CK, mql4_chuan as MQ4, ma_nguon as MN, nguon_seeker as NS

SRC = "reports/seeker_may_nha/SEEKER_MAY_NHA_20261013.json"
G5 = "data/cau_kho/goi_mql5/"; GG = "data/cau_kho/goi_github_v26/"; RA = "reports/seeker_v26/"
DUOI = (".mq5", ".mq4", ".mqh", ".set")


def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 else None


def tai_mql5(T, log):
    for x in T:
        m = re.search(r"/code/(\d+)$", x["url"])
        if not m: log.append({"url": x["url"], "tt": "khong_phai_bai"}); continue
        i = m.group(1); d = G5 + i
        if os.path.isdir(d): log.append({"url": x["url"], "tt": "da_co"}); continue
        r = MN.tai_goi_ma_nguon({"id": int(i), "url": x["url"], "tieu_de": x["tieu_de"]}, nghi_giay=1.0)
        if r is None: log.append({"url": x["url"], "tt": "CHUA DO DUOC (trang hong/chan)"}); continue
        os.makedirs(d, exist_ok=True)
        for ten, vb in r["tep"].items(): open(d + "/" + re.sub(r"[^A-Za-z0-9_.-]+", "_", ten)[:100], "w").write(vb)
        json.dump({"id": i, "url": x["url"], "tieu_de": x["tieu_de"], "tep": sorted(r["tep"])}, open(d + "/GOI.json", "w"), ensure_ascii=False)
        log.append({"url": x["url"], "tt": "tai_moi", "so_tep": len(r["tep"])})


def tai_github(T, log, tran=12):
    for x in T:
        m = re.match(r"https://github.com/([^/]+)/([^/#?]+)", x["url"])
        if not m: continue
        o, r = m.group(1), m.group(2); d = GG + f"{o}__{r}"
        if os.path.isdir(d): log.append({"url": x["url"], "tt": "da_co"}); continue
        info = gh(f"repos/{o}/{r}")
        if not info: log.append({"url": x["url"], "tt": "CHUA DO DUOC (api)"}); continue
        tr = gh(f"repos/{o}/{r}/git/trees/{info['default_branch']}?recursive=1") or {}
        fs = [t["path"] for t in tr.get("tree", []) if t["type"] == "blob" and t["path"].lower().endswith(DUOI + (".pine",)) and t.get("size", 0) < 400000]
        if not fs: log.append({"url": x["url"], "tt": "khong_co_ma_mql_pine"}); continue
        os.makedirs(d, exist_ok=True)
        for p in fs[:tran]:
            c = gh(f"repos/{o}/{r}/contents/{p}?ref={info['default_branch']}")
            if c and c.get("content"):
                open(d + "/" + re.sub(r"[^A-Za-z0-9_.-]+", "_", p)[-100:], "wb").write(base64.b64decode(c["content"]))
        json.dump({"url": x["url"], "tep": fs[:tran], "tong_tep": len(fs)}, open(d + "/GOI.json", "w"))
        log.append({"url": x["url"], "tt": "tai_moi", "so_tep": min(len(fs), tran)})


def tom_tat(s):
    return {k: s.get(k) for k in ("vao", "ra", "chieu", "giu", "sltp", "trong_bar", "khung", "loc") if s.get(k) is not None}


def doc(d, url, tieu_de):
    out = []
    for f in glob.glob(d + "/*"):
        if not f.lower().endswith((".mq5", ".mq4")): continue
        vb = open(f, encoding="utf-8", errors="ignore").read()
        if "OnTick" not in vb and "start()" not in vb: continue
        m4 = CK.la_mql4(vb) or f.lower().endswith(".mq4")
        try:
            dd = DM.doc_chien_luoc(MQ4.chuan_hoa(vb) if m4 else vb, nguon=f); sp = dd.get("co_che") or []
            ly = [str(z)[:100] for z in (dd.get("chua_dien_dat_duoc") or [])][:3]
        except Exception as e:
            sp, ly = [], ["loi " + type(e).__name__]
        nh = NS.gan_nhan({"ten": tieu_de + " " + os.path.basename(f), "url": url, "ghi_chu": " ".join(json.dumps(tom_tat(s), default=str) for s in sp)[:3000]})
        out.append({"url": url, "tieu_de": tieu_de, "tep": os.path.basename(f), "mql4": bool(m4), "so_luat": len(sp),
                    "luat": [tom_tat(s) for s in sp], "ly_do_chua_dich": ly, "nhan": nh, "xep_hang_doi": bool(sp)})
    return out


def main():
    T = json.load(open(SRC))["tai_lieu"]; log = []
    m5 = [x for x in T if x["nguon"] in ("mql5_code", "mql5_ma_expert")]
    gi = [x for x in T if x["nguon"] in ("github",)]
    chan = [x for x in T if x["nguon"] in ("tradingview_scripts", "tradingview_pine", "tradingview_ideas", "fxblue", "quantpedia")]
    t0 = time.time(); tai_mql5(m5, log); print("mql5", time.time() - t0, flush=True)
    t0 = time.time(); tai_github(gi, log); print("github", time.time() - t0, flush=True)
    R = []
    for x in m5:
        m = re.search(r"/code/(\d+)$", x["url"])
        if m and os.path.isdir(G5 + m.group(1)): R += doc(G5 + m.group(1), x["url"], x["tieu_de"])
    for x in gi:
        m = re.match(r"https://github.com/([^/]+)/([^/#?]+)", x["url"])
        if m and os.path.isdir(GG + f"{m.group(1)}__{m.group(2)}"): R += doc(GG + f"{m.group(1)}__{m.group(2)}", x["url"], x["tieu_de"])
    tk = {"tai_lieu_vao": len(T), "mql5_bai": len(m5), "github_repo": len(gi), "tep_ea_doc": len(R),
          "tep_dich_duoc": sum(r["so_luat"] > 0 for r in R), "so_luat": sum(r["so_luat"] for r in R),
          "khong_tai_tren_box_CHUA_DO_DUOC": {"so": len(chan), "ly_do": "TradingView/fxblue/quantpedia 403/Cloudflare tren box - khong vuot; Pine nguon dong/khong API cong khai"},
          "trang_thai_tai": {k: sum(1 for z in log if z["tt"].startswith(k)) for k in ("tai_moi", "da_co", "CHUA", "khong")}}
    json.dump({"nhan": "TOM TAT LUAT + URL (khong chua ma nguon ben thu ba)", "tong_ket": tk, "tai": log, "luat": R},
              open(RA + "LUAT_TRICH.json", "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(tk, ensure_ascii=False))


if __name__ == "__main__":
    main()
