# -*- coding: utf-8 -*-
"""Telegram công khai qua bản xem trước https://t.me/s/<kenh> (không đăng nhập).
- Đọc tin (văn bản, ngày, link), ghi tên tệp đính kèm (ex4/ex5/mq4/mq5/set/pdf...) + link bài.
  Bản xem trước KHÔNG cho tải tệp; tải thật làm qua seeker/mxh (Telegram Web, trình duyệt riêng).
- Khám phá kênh mới từ tin chuyển tiếp (forwarded from), @nhắc tên và link t.me/<ten>."""
from __future__ import annotations
import re
from bs4 import BeautifulSoup

TEN_HOP_LE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")
BO_QUA = {"joinchat", "share", "addstickers", "proxy", "socks", "iv", "s", "c", "login", "setlanguage", "addtheme", "contact"}


def chuan_ten(x: str) -> str | None:
    x = x.strip().lstrip("@").split("?")[0].split("/")[0]
    return x.lower() if TEN_HOP_LE.match(x) and x.lower() not in BO_QUA else None


def doc_trang(html: str, kenh: str, duoi_tep=(".ex4", ".ex5", ".mq4", ".mq5", ".mqh", ".set", ".pdf", ".zip", ".rar")) -> dict:
    kenh = kenh.lower()
    sp = BeautifulSoup(html, "html.parser")
    tin, kenh_moi, tep = [], {}, []
    for m in sp.select("div.tgme_widget_message[data-post]"):
        post = m["data-post"]; pid = int(post.split("/")[-1]) if post.split("/")[-1].isdigit() else None
        t = m.select_one(".tgme_widget_message_text")
        txt = t.get_text("\n", strip=True) if t else ""
        tg = m.select_one("time[datetime]")
        fw = m.select_one("a.tgme_widget_message_forwarded_from_name")
        if fw and fw.get("href"):
            n = chuan_ten(fw["href"].split("t.me/")[-1])
            if n and n != kenh: kenh_moi[n] = kenh_moi.get(n, 0) + 3          # chuyển tiếp: tín hiệu mạnh
        for a in (t.find_all("a", href=True) if t else []):
            if "t.me/" in a["href"]:
                n = chuan_ten(a["href"].split("t.me/")[-1])
                if n and n != kenh: kenh_moi[n] = kenh_moi.get(n, 0) + 2
        for mm in re.findall(r"t\.me/(?:s/)?([A-Za-z][A-Za-z0-9_]{4,31})", txt):
            n = chuan_ten(mm)
            if n and n != kenh: kenh_moi[n] = kenh_moi.get(n, 0) + 2
        for mm in re.findall(r"(?<![\w@])@([A-Za-z][A-Za-z0-9_]{4,31})", txt):
            n = chuan_ten(mm)
            if n and n != kenh: kenh_moi[n] = kenh_moi.get(n, 0) + 1
        for d in m.select(".tgme_widget_message_document_title"):
            ten = d.get_text(strip=True)
            if ten.lower().endswith(tuple(duoi_tep)):
                tep.append({"ten_tep": ten, "bai": f"https://t.me/{post}", "ngay": tg["datetime"] if tg else None})
        tin.append({"id": pid, "url": f"https://t.me/{post}", "ngay": tg["datetime"] if tg else None,
                    "van_ban": txt, "chuyen_tiep_tu": fw.get_text(strip=True) if fw else None})
    ids = [x["id"] for x in tin if x["id"]]
    return {"tin": tin, "kenh_moi": kenh_moi, "tep": tep, "id_nho_nhat": min(ids) if ids else None,
            "ton_tai": bool(sp.select_one(".tgme_channel_info")) or bool(tin)}


def url_trang(kenh: str, truoc: int | None = None) -> str:
    return f"https://t.me/s/{kenh}" + (f"?before={truoc}" if truoc else "")
