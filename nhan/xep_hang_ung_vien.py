# -*- coding: utf-8 -*-
"""XEP HANG UNG VIEN (11/10/2026): goi EA nao vao vong thu TRUOC.

Uu tien cua chu du an (t30u): (1) bot MT4/MT5 CONG KHAI co san chien luoc + `.set`;
(2) he da ra tien (lich su lenh) khi co dang nhap. File nay xep (1); (2) van CHUA DO DUOC
(can dang nhap MQL5/Darwinex/FXStat).

DIEM (chot TRUOC khi do kho, KHONG chinh theo ket qua vong thu; chi la thu tu, khong phai cong):
  ket qua bo doc `doc_ma` (cau_kho_ma.do_kho):
    ra_co_che (diem vao dich duoc)          +40
    chua_dich (thay diem vao, chua dich)    +15
    khong_thay_diem_vao                     -20   co lenh (vd chi PositionModify) ma khong co
                                                  diem vao -> gan nhu quan ly lenh
    thieu_tep (include ngoai khong co)      -30   dieu kien vao co the nam trong tep thieu
    loi_bo_doc                                0   (+ nhan, la viec sua bo doc)
    khong_dat_lenh: lan quan_tri/tien_ich   -40   chi quan ly lenh / cong cu
                    lan chi_bao             -50
  goi:   co `.set` cua tac gia +20 | co SL/TP trong ma +10 (chi khi co diem vao) | include du (khong co include
         ngoai, hoac co du tep trong goi) +10 | anh ket qua tester trong bai +5 (yeu: tac gia tu
         dang) | chi co .zip (khong lay, khong giai nen) -10
  MQL4: KHONG cham bang bo doc (bo doc chi hieu MQL5) -> lan rieng `mql4`, diem chi tu goi
        (set/sltp/include); ghi `mql4_chua_doc` - khong dem la bo doc that bai.
  Telegram (xem truoc cong khai): bai co dinh kem .set/.mq5 nhung file CHUA lay duoc (can
        MTProto) -> hang `T`, diem = diem khop - 20 (chua co ma trong tay < goi co ma).
  Bai dien dan / Telegram KHONG co ma va KHONG co dinh kem: khong vao hang doi nay.

HANG: A = ra_co_che va du tep (-> `vong_thu_nghiem --theo-hang`); B = thay diem vao nhung
chua dich / MQL4 co .set (-> viec cua bo doc); C = con lai; T = Telegram can MTProto.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from nhan import truy_van_seeker as TV

DIEM_KQ = {"ra_co_che": 40, "chua_dich": 15, "khong_thay_diem_vao": -20, "thieu_tep": -30,
           "loi_bo_doc": 0}
_RX_SLTP = re.compile(
    r"^[ \t]*(?:input|extern|sinput)\b[^;\n]*?\b\w*(?:StopLoss|TakeProfit|Stop_Loss|Take_Profit"
    r"|\bSL\w*|\bTP\w*|_SL\b|_TP\b|Sl\b|Tp\b)\w*\s*=", re.M | re.I)
_RX_SLTP_LENH = re.compile(r"\.(?:Buy|Sell|PositionOpen|PositionModify)\s*\([^;]*\b\w*(?:sl|tp)\w*\b",
                           re.I)


def co_sltp(src: str) -> bool:
    return bool(_RX_SLTP.search(src or "") or _RX_SLTP_LENH.search(src or ""))


def thong_tin_goi(nguon: str) -> dict:
    """Ban ghi `tep:<duong>` nam trong goi (thu muc co GOI.json) -> meta goi + .set canh file."""
    if not str(nguon).startswith("tep:"):
        return {}
    cha = Path(nguon[4:]).parent
    meta = {}
    p = cha / "GOI.json"
    if p.exists():
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
    sets = sorted(cha.glob("*.set"))
    khoa = []
    for s in sets[:5]:
        try:
            khoa += list(TV.doc_set(s.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            pass
    return {"meta": meta, "tep_set": [s.name for s in sets], "khoa_set": khoa[:80]}


def cham(dong: dict, src: str) -> dict:
    kq = dong.get("ket_qua", "")
    g = thong_tin_goi(dong.get("nguon", ""))
    meta = g.get("meta") or {}
    lan = "mql4" if kq == "mql4_bo_qua" else "mql5"
    d, ly = 0, []
    if lan == "mql5":
        if dong.get("lan") in ("quan_tri", "tien_ich") and kq != "ra_co_che":
            v = -40
        elif kq == "khong_dat_lenh":
            v = -50 if dong.get("lan") == "chi_bao" else -40
        else:
            v = DIEM_KQ.get(kq, 0)
        d += v
        ly.append("%s%+d" % (kq or "?", v))
    else:
        ly.append("mql4_chua_doc")
    co_set = bool(g.get("tep_set"))
    if co_set:
        d += 20
        ly.append("set+20")
    # SL/TP chi cong khi co diem vao (cong cu trailing cung goi PositionModify(sl,...))
    sltp = co_sltp(src) and (lan == "mql4" or int(dong.get("vao_lenh") or 0) > 0)
    if sltp:
        d += 10
        ly.append("sltp+10")
    if not dong.get("thieu_tep_that") and kq != "thieu_tep":
        d += 10
        ly.append("du_tep+10")
    if meta.get("anh_ket_qua"):
        d += 5
        ly.append("anh_kq+5")
    if meta.get("chi_zip"):
        d -= 10
        ly.append("chi_zip-10")
    if lan == "mql5" and kq == "ra_co_che" and not dong.get("thieu_tep_that"):
        hang = "A"
    elif (lan == "mql5" and kq in ("chua_dich", "loi_bo_doc")) or (lan == "mql4" and co_set):
        hang = "B"
    else:
        hang = "C"
    return {"ten": dong.get("ten"), "url": dong.get("url", ""), "van_tay": dong.get("van_tay"),
            "nguon": dong.get("nguon"), "lan_doc": lan, "ket_qua": kq, "diem": d, "hang": hang,
            "ly_do": ly, "co_set": co_set, "tep_set": g.get("tep_set", []),
            "khoa_set": g.get("khoa_set", []), "sltp": sltp, "ho": dong.get("ho", []),
            "vao": [dong.get("vao_co", 0), dong.get("vao_lenh", 0)],
            "tieu_de": meta.get("tieu_de", "")}


def xep(r: dict, ban_ghi: list[dict], telegram: list[dict] | None = None) -> list[dict]:
    """Ket qua `do_kho` + ban ghi (co src) -> hang doi da xep (diem giam dan).
    Ban sao / trung mau_thu khong vao hang."""
    src = {b["nguon"]: b.get("src", "") for b in ban_ghi}
    ra = [cham(x, src.get(x.get("nguon"), "")) for x in r.get("ds", [])
          if x.get("ket_qua") not in ("trung_mau_thu", None)]
    for t in telegram or []:
        if t.get("co_set") or t.get("co_ma"):
            ra.append({"ten": t.get("ten") or t.get("url"), "url": t.get("url"), "lan_doc": "telegram",
                       "ket_qua": "can_mtproto", "diem": int(t.get("diem", 0)) - 20, "hang": "T",
                       "ly_do": ["telegram_khop%+d" % t.get("diem", 0), "chua_co_ma-20"],
                       "co_set": bool(t.get("co_set")), "tep_set": t.get("tep_set", []),
                       "khoa_set": [], "sltp": False, "ho": [], "vao": [0, 0]})
    thu = {"A": 0, "B": 1, "T": 2, "C": 3}
    ra.sort(key=lambda x: (thu[x["hang"]], -x["diem"], str(x["ten"])))
    for i, x in enumerate(ra, 1):
        x["thu_tu"] = i
    return ra


def tom_tat(hang: list[dict]) -> dict:
    from collections import Counter
    c = Counter(x["hang"] for x in hang)
    return {"tong": len(hang), "hang": dict(c),
            "co_set": sum(1 for x in hang if x["co_set"]),
            "co_set_mql5": sum(1 for x in hang if x["co_set"] and x["lan_doc"] == "mql5"),
            "mql4": sum(1 for x in hang if x["lan_doc"] == "mql4"),
            "sltp": sum(1 for x in hang if x["sltp"])}


def bang_md(hang: list[dict], toi_da: int = 25) -> str:
    L = ["## Hang doi uu tien (xep_hang_ung_vien; THU TU, khong phai cong)", "",
         "tom tat: `%s`" % json.dumps(tom_tat(hang), ensure_ascii=False), "",
         "| # | hang | diem | ten | lan | .set | ly do |", "|---|---|---|---|---|---|---|"]
    for x in hang[:toi_da]:
        L.append("| %d | %s | %d | `%s` | %s | %s | %s |" % (
            x["thu_tu"], x["hang"], x["diem"], str(x["ten"])[:60], x["lan_doc"],
            ",".join(x["tep_set"])[:50] or "-", " ".join(x["ly_do"])))
    return "\n".join(L) + "\n"
