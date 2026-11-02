# -*- coding: utf-8 -*-
"""Chạy bộ thao tác MXH trên máy nhà.

  python -m seeker.mxh.chay --dang-nhap                       # mở trình duyệt riêng để Anh tự đăng nhập, rồi đóng
  python -m seeker.mxh.chay --nen-tang telegram --kenh-tu-file  # đọc kênh trong seeker/nguon/telegram.yaml + tải tệp
  python -m seeker.mxh.chay --nen-tang facebook --tim 5         # tìm nhóm theo 5 từ khóa đầu của đồ thị, đọc, xin vào (chạy thử)
  thêm --that  để tắt chế độ chạy thử (follow/join thật, vẫn theo trần ngày)
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import yaml
from .. import GOC, LAB, TRANG_THAI, y_tuong as YT
from ..do_thi import DoThi
from .an_toan import AnToan, DungLai, doc_cau_hinh
from .nen_tang.facebook import Facebook
from .nen_tang.x import X
from .nen_tang.reddit import Reddit
from .nen_tang.discord import Discord
from .nen_tang.telegram_web import TelegramWeb

LOP = {"facebook": Facebook, "x": X, "reddit": Reddit, "discord": Discord, "telegram": TelegramWeb}
URL_DANG_NHAP = ["https://web.telegram.org/k/", "https://www.facebook.com/", "https://x.com/login",
                 "https://www.reddit.com/login", "https://discord.com/login"]


def luu_y_tuong(ds, nen_tang, do_thi: DoThi):
    p = TRANG_THAI / "y_tuong.jsonl"; p.parent.mkdir(parents=True, exist_ok=True); n = 0
    with open(p, "a", encoding="utf-8") as f:
        for b in ds:
            do_thi.hoc(b["van_ban"], "*")
            y = YT.rut(b["van_ban"], do_thi.khai_niem_trong(b["van_ban"]), "mxh:" + nen_tang, "*", b["url"], None)
            if y: f.write(json.dumps(y, ensure_ascii=False) + "\n"); n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dang-nhap", action="store_true"); ap.add_argument("--nen-tang", choices=sorted(LOP))
    ap.add_argument("--tim", type=int, default=0, help="số từ khóa từ đồ thị để tìm")
    ap.add_argument("--kenh-tu-file", action="store_true"); ap.add_argument("--url", nargs="*", default=[])
    ap.add_argument("--that", action="store_true", help="tắt chạy thử")
    ap.add_argument("--ngon-ngu", default="vi")
    a = ap.parse_args(argv)
    ch = doc_cau_hinh()
    if a.that: ch["chay_thu"] = False
    from .trinh_duyet import mo
    pw, ctx = mo(ch)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        if a.dang_nhap:
            for u in URL_DANG_NHAP:
                ctx.new_page().goto(u)
            input("Anh tự đăng nhập từng tab (tool KHÔNG đọc mật khẩu). Xong bấm Enter để đóng...")
            return
        at = AnToan(ch, TRANG_THAI / "mxh" / "gioi_han.json")
        nt = LOP[a.nen_tang](page, at)
        st_p = TRANG_THAI / "trang_thai.json"
        dt = DoThi(yaml.safe_load((GOC / "tu_khoa_hat_giong.yaml").read_text(encoding="utf-8")),
                   (json.loads(st_p.read_text(encoding="utf-8")).get("do_thi") if st_p.exists() else None))
        muc_tieu = list(a.url)
        if a.kenh_tu_file:
            cfg = yaml.safe_load((GOC / "nguon" / "telegram.yaml").read_text(encoding="utf-8")) or {}
            muc_tieu += [k.get("ten") or k["ten_hien_thi"] for k in cfg.get("kenh") or []]
        for tu in dt.truy_van(a.ngon_ngu, a.tim) if a.tim else []:
            for kq in nt.tim(tu)[:10]:
                muc_tieu.append(kq["url"])
        bao = {"doc": 0, "y_tuong": 0, "tep": [], "kham_pha": [], "xin_vao": []}
        for u in dict.fromkeys(muc_tieu):
            bai = nt.doc(u); bao["doc"] += len(bai)
            bao["y_tuong"] += luu_y_tuong(bai, nt.ten, dt)
            if isinstance(nt, TelegramWeb):
                bao["tep"] += nt.tai_tep(u.split("/")[-1], bai, LAB / ch["thu_muc_tai_ve"])
            bao["kham_pha"] += nt.lien_quan(u)
            if nt.cho_phep_xin_vao and ("/groups/" in u or "/r/" in u):
                bao["xin_vao"].append({u: nt.xin_vao(u)})
        print(json.dumps(bao, ensure_ascii=False, indent=1))
    except DungLai as e:
        print("DỪNG LẠI (captcha/checkpoint/hạn chế):", e, "— Anh mở trình duyệt riêng xử lý tay, tool không vượt.", file=sys.stderr)
    finally:
        ctx.close(); pw.stop()


if __name__ == "__main__":
    main()
