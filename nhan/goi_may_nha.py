# -*- coding: utf-8 -*-
"""goi_may_nha.py - DONG GOI ma EA ngoai cho may nha (19/10/2026).

Ma cua nguoi khac chi nam trong data/ (git bo qua), nen may nha khong lay duoc qua git. Ham nay doc hang cho
`reports/ong_dan/hang_cho_mt5.jsonl`, gom moi file can cho viec `ea=NGOAI` (ma .mq4/.mq5, cac .mqh no #include - do theo
duong dan tuong doi, .set, .ex4/.ex5) vao MOT zip `/workspace/goi_may_nha/goi_ea_ngoai_<ngay>.zip`, giu NGUYEN cau truc
`data/...` de giai nen thang vao goc repo tren may nha. Kem `MANIFEST.json` (viec -> file) va `HUONG_DAN.md`.
Chi doc va nen file, khong chay gi. Zip nam ngoai repo, khong vao git.
"""
from __future__ import annotations

import json
import re
import shutil
import time
import zipfile
from pathlib import Path

from nhan import nhap_tay as NT

GOC = Path(__file__).resolve().parent.parent
HANG_CHO = GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl"
RA = Path("/workspace/goi_may_nha")
_INC = re.compile(r'#include\s+"([^"]+)"')


def _kem(p: Path, gap: set[Path], sau: int = 0) -> None:
    """File + cac #include "..." (tuong doi theo thu muc file, roi theo thu muc cha) de quy."""
    if p in gap or not p.exists() or not p.is_file() or sau > 6:
        return
    gap.add(p)
    if p.suffix.lower() in (".mq4", ".mq5", ".mqh"):
        for inc in _INC.findall(NT.doc_vb(p.read_bytes())):
            inc = inc.replace("\\", "/")
            for goc in [p.parent] + list(p.parents)[:4]:
                q = (goc / inc).resolve()
                if q.exists() and GOC / "data" in q.parents:
                    _kem(q, gap, sau + 1)
                    break


def dong_goi(thu_muc: Path = RA, hang_cho: Path = HANG_CHO, tran_mb: float = 1500.0) -> dict:
    viec = [json.loads(x) for x in hang_cho.read_text(encoding="utf-8").splitlines() if x.strip()] if hang_cho.exists() else []
    viec = [v for v in viec if v.get("ea") == "NGOAI"]
    tep: set[Path] = set()
    bang = []
    for v in viec:
        cua = []
        for k in ("tep_box", "set_box"):
            if v.get(k):
                p = GOC / v[k]
                truoc = set(tep)
                _kem(p, tep)
                cua += [str(x.relative_to(GOC)) for x in sorted(tep - truoc)] or ([v[k]] if p.exists() else [])
        bang.append({"ten": v["ten"], "ea_file": v.get("ea_file"), "ma": v.get("ma"), "tf": v.get("tf"), "pha": v.get("pha"),
                     "tep_box": v.get("tep_box"), "set_box": v.get("set_box"), "url": v.get("url"),
                     "can_tai_ma": bool(v.get("can_tai_ma")), "file_trong_goi": cua})
    tong = sum(p.stat().st_size for p in tep)
    if tong > tran_mb * 1024 * 1024:
        raise RuntimeError("goi qua lon: %.0f MB" % (tong / 1048576))
    if shutil.disk_usage("/workspace").free - tong < 30 * 1024 ** 3:
        raise RuntimeError("o box se con < 30 GB trong -> dung")
    thu_muc.mkdir(parents=True, exist_ok=True)
    ten = thu_muc / ("goi_ea_ngoai_%s.zip" % time.strftime("%Y%m%d"))
    hd = ("# Gói mã EA ngoài cho máy nhà (%s)\n\n"
          "1. Giải nén zip này vào GỐC repo brain2 trên máy nhà (giữ nguyên thư mục `data/...`; `data/` không vào git).\n"
          "2. `git pull` để có `reports/ong_dan/hang_cho_mt5.jsonl` (việc `ea=NGOAI`).\n"
          "3. Mỗi việc: chép `tep_box` (và các .mqh đi kèm) vào `MQL5/Experts/NGOAI/` (MQL4 thì chuyển MT4 hoặc dịch), biên dịch "
          "bằng MetaEditor; nạp `set_box` nếu có; chạy Strategy Tester ký hiệu sàn (`{ma}micro` XM, `{ma}c` Exness), khung `tf`, "
          "khoảng `tu`–`den`; pha TOI_UU_SET thì bật Optimization theo cờ ||Y trong .set.\n"
          "4. Lưu báo cáo .htm (có danh sách lệnh) vào `reports/ong_dan/ket_qua_mt5/<ten>.htm`, rồi `python ong_dan.py doc_mt5`.\n"
          "5. Đọc mã trước khi chạy (mã của người khác). Việc `can_tai_ma=true`: box chưa có mã, tải theo `url` bằng Chrome.\n\n"
          "Số Python trong hàng chờ là MÔ PHỎNG, PHÍ TẠM; số tác giả (`so_tac_gia`) chưa đo.\n") % time.strftime("%d/%m/%Y")
    with zipfile.ZipFile(ten, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(tep):
            z.write(p, str(p.relative_to(GOC)))
        z.writestr("MANIFEST.json", json.dumps({"tao_luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "so_viec": len(bang),
                                                "so_file": len(tep), "viec": bang}, ensure_ascii=False, indent=1))
        z.writestr("HUONG_DAN.md", hd)
    return {"zip": str(ten), "so_viec": len(bang), "so_file": len(tep), "mb_goc": round(tong / 1048576, 1),
            "mb_zip": round(ten.stat().st_size / 1048576, 1), "can_tai_ma": sum(1 for b in bang if b["can_tai_ma"])}
