# -*- coding: utf-8 -*-
"""TELEGRAM CONG KHAI theo TRUY VAN (11/10/2026) - buoc Telegram cua vong SEEKER/CAU KHO.

Chu du an: Telegram la nguon chinh cua nhom chia se EA/.set, nhung phai biet TIM GI. Buoc nay:
  1. lay truy van tu `truy_van_seeker.sinh` (hat giong MT4/MT5+.set + tu dao tu goi da tai);
  2. DOC kenh da biet qua xem truoc web CONG KHAI `t.me/s/<kenh>` (khong dang nhap): kenh chu
     du an (`telegram.KENH_CHU_DU_AN`), kenh da tung quet (`config/telegram_con_tro.json`),
     kenh duoc nhac trong kho (`telegram.kenh_duoc_nhac`, neu co so cai);
  3. cham tung bai (`truy_van_seeker.khop`): dinh kem .set/.mq5 la tin hieu manh nhat;
  4. TIM KENH MOI bang o tim kiem Telegram CHI KHI co phien MTProto (`san_sang_mtproto`) va
     `BRAIN_TG_TIM=1`: chi tra DE XUAT (khong tham gia nhom nao, khong tu them vao danh sach).
     Khong co phien -> `tim_kenh: CHUA DO DUOC (<ly do>)`, khong ghi la 0.
  File dinh kem: xem truoc web chi cho TEN file; tai file can MTProto -> CHUA DO DUOC tren box.
KHONG: tham gia nhom, nhan tin, dang nhap. Chi doc trang cong khai.
"""
from __future__ import annotations

import json
import os
import time

from nhan import telegram as TG
from nhan import truy_van_seeker as TV


def kenh_da_biet(gioi_han: int = 12) -> list[str]:
    ra = list(TG.KENH_CHU_DU_AN)
    try:
        ra += list(TG.doc_con_tro())
    except Exception:
        pass
    try:
        ra += list(TG.kenh_duoc_nhac())[:6]
    except Exception:
        pass
    return list(dict.fromkeys(k.strip().lstrip("@") for k in ra if k))[:gioi_han]


def mot_luot(truy_van: list[dict], han_giay: float = 60.0, so_trang: int = 2,
             doc_trang=None, kenh=None) -> dict:
    doc_trang = doc_trang or TG.doc_trang
    t0 = time.time()
    kenh = kenh if kenh is not None else kenh_da_biet()
    ra = {"kenh": {}, "bai_khop": [], "tim_kenh": None}
    for k in kenh:
        if time.time() - t0 > han_giay:
            ra["kenh"][k] = {"trang_thai": "het_gio"}
            continue
        bao = {"bai": 0, "khop": 0, "co_set": 0, "co_ma": 0}
        truoc = None
        for _ in range(so_trang):
            try:
                tr = doc_trang(k, truoc)
            except Exception as e:                          # noqa: BLE001
                bao["loi"] = "%s: %s" % (type(e).__name__, str(e)[:80])
                break
            if tr.get("loi"):
                bao["loi"] = tr["loi"]                      # vd kenh tat xem truoc -> can MTProto
                break
            for b in tr.get("bai", []):
                bao["bai"] += 1
                m = TV.khop(b.get("van_ban", ""), b.get("dinh_kem"), truy_van)
                if m["diem"] <= 0:
                    continue
                bao["khop"] += 1
                bao["co_set"] += int(m["co_set"])
                bao["co_ma"] += int(m["co_ma"])
                ra["bai_khop"].append({
                    "kenh": k, "url": b.get("url"), "luc": b.get("luc"), **m,
                    "ten": next((d["ten"] for d in b.get("dinh_kem", [])
                                 if str(d.get("ten", "")).lower().endswith((".set", ".mq5", ".mq4"))),
                                b.get("url")),
                    "tep_set": [d["ten"] for d in b.get("dinh_kem", [])
                                if str(d.get("ten", "")).lower().endswith(".set")],
                    "trich": (b.get("van_ban") or "")[:160]})
            truoc = tr.get("truoc_tiep")
            if not truoc:
                break
        bao["trang_thai"] = "loi" if bao.get("loi") else "ok"
        ra["kenh"][k] = bao
    try:
        duoc, ly = TG.san_sang_mtproto()
    except Exception as e:                                  # noqa: BLE001
        duoc, ly = False, "%s" % type(e).__name__
    if not duoc:
        ra["tim_kenh"] = "CHUA DO DUOC (%s)" % ly
        ra["tai_file"] = "CHUA DO DUOC (can phien MTProto: %s)" % ly
    elif os.environ.get("BRAIN_TG_TIM") == "1":
        ds = TG.tim_kenh(TV.cho_telegram(truy_van, 8), gioi_han=10, in_ra=lambda *_: None)
        ra["tim_kenh"] = {"de_xuat": ds[:30], "luu_y": "DE XUAT - khong tham gia, nguoi duyet"}
    else:
        ra["tim_kenh"] = "co phien nhung BRAIN_TG_TIM chua bat (khong tim)"
    ra["bai_khop"].sort(key=lambda x: -x["diem"])
    ra["giay"] = round(time.time() - t0, 1)
    return ra


def tom_tat(ra: dict) -> dict:
    k = ra.get("kenh", {})
    return {"kenh": len(k), "kenh_doc_duoc": sum(1 for v in k.values() if v.get("trang_thai") == "ok"),
            "bai": sum(v.get("bai", 0) for v in k.values()),
            "bai_khop": len(ra.get("bai_khop", [])),
            "co_set": sum(1 for b in ra.get("bai_khop", []) if b["co_set"]),
            "co_ma": sum(1 for b in ra.get("bai_khop", []) if b["co_ma"]),
            "tim_kenh": ra.get("tim_kenh") if isinstance(ra.get("tim_kenh"), str) else "de_xuat",
            "kenh_khong_doc": {n: v.get("loi") for n, v in k.items() if v.get("loi")}}


if __name__ == "__main__":
    r = mot_luot(TV.sinh())
    print(json.dumps(tom_tat(r), ensure_ascii=False, indent=1))
