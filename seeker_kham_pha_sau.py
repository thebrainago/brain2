# -*- coding: utf-8 -*-
"""seeker_kham_pha_sau.py - Chay KHAM PHA SAU qua Chrome may nha (CDP 9224) hoac HTTP.

  python seeker_kham_pha_sau.py --cdp 9224 [--sau 2] [--ngan-sach 60] [--giay 900] [--hat URL ...] [--ghi]
  python seeker_kham_pha_sau.py --quet-lai   : hat = nguon theo doi den han (config/nguon_theo_doi.json)
Ket qua: data/nguon_seeker/kham_pha_sau_<ngay>.json (gitignore). `--ghi`: them vao so dang ky + hang doi.
CHI DOC: khong dang bai/like/nhan tin/tham gia nhom. Khong luu cookie/mat khau.
"""
import argparse, json, time
from pathlib import Path
from nhan import kham_pha_sau as K

LAB = Path(__file__).resolve().parent


def lay_cdp(cong):
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{cong}", timeout=20000)
    c = b.contexts[0]

    def lay(url):
        pg = c.new_page()
        try:
            pg.goto(url, timeout=45000, wait_until="domcontentloaded")
            time.sleep(4)
            pg.mouse.wheel(0, 4000); time.sleep(1.5)
            text = pg.inner_text("body", timeout=8000)
            links = pg.evaluate("()=>[...document.querySelectorAll('a[href]')].map(a=>[a.innerText.trim().slice(0,120),a.href]).slice(0,600)")
            return text, links
        finally:
            pg.close()
    return lay, p


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--cdp", default="9224"); a.add_argument("--sau", type=int, default=2)
    a.add_argument("--ngan-sach", type=int, default=60); a.add_argument("--giay", type=float, default=900)
    a.add_argument("--hat", nargs="*", default=[]); a.add_argument("--ghi", action="store_true")
    a.add_argument("--quet-lai", action="store_true")
    o = a.parse_args()
    hat = list(o.hat)
    if o.quet_lai or not hat:
        hat += [n["url"] for n in K.den_han_quet_lai()]
    if not hat:
        print("khong co hat"); return
    lay, p = lay_cdp(o.cdp)
    try:
        kq = K.KhamPha(lay, sau=o.sau, ngan_sach=o.ngan_sach, giay=o.giay).chay(hat)
    finally:
        p.stop()
    K.danh_dau_da_quet(hat)
    out = LAB / "data" / "nguon_seeker" / time.strftime("kham_pha_sau_%Y%m%d_%H%M.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
    print("trang", len(kq["trang"]), "ung vien", len(kq["ung_vien"]), "->", out)
    if o.ghi:
        print(K.them_vao_so(kq["ung_vien"]))


if __name__ == "__main__":
    main()
