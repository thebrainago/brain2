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


def tep_dich_llm(cn) -> tuple[set[Path], list[dict]]:
    """19/10/2026: ma nguon cua cac the CHO DICH LLM (nhan/dich_llm.danh_sach_cho) - de may nha chay `dich_llm`."""
    from nhan import dich_llm as DL
    tep: set[Path] = set()
    bang = []
    for x in DL.danh_sach_cho(cn):
        if x["tep"] is None:
            continue
        truoc = set(tep)
        _kem(x["tep"], tep)
        bang.append({"the": x["the"]["id"], "nhom": x["nhom"], "top28": x["top28"], "nen_tang": x["the"].get("nen_tang"),
                     "tep": str(x["tep"].relative_to(GOC)),
                     "file_trong_goi": [str(p.relative_to(GOC)) for p in sorted(tep - truoc)]})
    return tep, bang


def _chup_db(cn, dich: Path) -> Path:
    """Ban chup nhat quan cua CSDL trang thai (sqlite backup), khong khoa CSDL dang chay."""
    import sqlite3
    dich.parent.mkdir(parents=True, exist_ok=True)
    if dich.exists():
        dich.unlink()
    d = sqlite3.connect(str(dich))
    with d:
        cn.backup(d)
    d.close()
    return dich


def dong_goi(thu_muc: Path = RA, hang_cho: Path = HANG_CHO, tran_mb: float = 1500.0, cn=None, kem_gia: bool = True) -> dict:
    """cn (CSDL ong dan) -> them: ma nguon the cho dich LLM, ban chup trang_thai.sqlite, cache dich LLM, gia H1 (kem_gia)."""
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
    bang_llm, phu = [], []
    if cn is not None:
        t_llm, bang_llm = tep_dich_llm(cn)
        tep |= t_llm
        ch = GOC / "data" / "ong_dan" / "dich_llm"
        if ch.exists():
            tep |= {p for p in ch.glob("*.json")}          # cache dich: may nha khong goi lai ma da dich
        import tempfile
        tam = Path(tempfile.mkdtemp())
        phu.append((_chup_db(cn, tam / "trang_thai.sqlite"), "data/ong_dan/trang_thai.sqlite"))
        if kem_gia:
            from nhan import ong_dan as OD
            for f in OD.xuat_gia_goi():
                tep.add(f)
    tong = sum(p.stat().st_size for p in tep) + sum(p.stat().st_size for p, _ in phu)
    if tong > tran_mb * 1024 * 1024:
        raise RuntimeError("goi qua lon: %.0f MB" % (tong / 1048576))
    if shutil.disk_usage("/workspace").free - tong < 30 * 1024 ** 3:
        raise RuntimeError("o box se con < 30 GB trong -> dung")
    thu_muc.mkdir(parents=True, exist_ok=True)
    ten = thu_muc / ("goi_ea_ngoai_%s.zip" % time.strftime("%Y%m%d"))
    hd = ("# Gói cho máy nhà (%s): mã EA ngoài + thẻ chờ dịch LLM\n\n"
          "## Dịch bằng LLM (khoá ai-box chỉ có trên máy nhà)\n\n"
          "1. `git pull` trong repo brain2.\n"
          "2. Giải nén zip này vào GỐC repo (giữ nguyên `data/...`; `data/` không vào git). Gói có: mã nguồn %d thẻ chờ dịch, "
          "bản chụp `data/ong_dan/trang_thai.sqlite` (ghi đè trạng thái ống dẫn cũ trên máy nhà nếu có), cache dịch, "
          "giá H1 `data/ong_dan/gia_goi/`.\n"
          "3. `python ong_dan.py dich_llm` (thêm `--gioi_han 50` để chạy thử ít thẻ trước). Khoá lấy từ biến AIBOX_API_KEY, "
          "hoặc từ cc-switch (provider 'aibox'); không cần chép khoá đi đâu. Model `qwen3.7-flash`, hết quota hay 403 thì "
          "sang `qwen3.6-flash` (config/qwen.json). Mã đã dịch có cache theo hash nên chạy lại không tốn thêm.\n"
          "4. `python ong_dan.py chay` để tối ưu, lọc 65/15 và sinh việc MT5 cho các thẻ dịch đạt.\n"
          "5. Kết quả: `reports/ong_dan/DICH_LLM.md` (số lần gọi, token, đạt / hỏng), `TRANG_THAI.md`, hàng chờ MT5. Commit "
          "các file trong `reports/` rồi push (không đưa `data/` vào git).\n\n"
          "## Chạy EA ngoài trên MT5\n\n"
          "1. Giải nén như trên.\n"
          "2. `git pull` để có `reports/ong_dan/hang_cho_mt5.jsonl` (việc `ea=NGOAI`).\n"
          "3. Mỗi việc: chép `tep_box` (và các .mqh đi kèm) vào `MQL5/Experts/NGOAI/` (MQL4 thì chuyển MT4 hoặc dịch), biên dịch "
          "bằng MetaEditor; nạp `set_box` nếu có; chạy Strategy Tester ký hiệu sàn (`{ma}micro` XM, `{ma}c` Exness), khung `tf`, "
          "khoảng `tu`–`den`; pha TOI_UU_SET thì bật Optimization theo cờ ||Y trong .set.\n"
          "4. Lưu báo cáo .htm (có danh sách lệnh) vào `reports/ong_dan/ket_qua_mt5/<ten>.htm`, rồi `python ong_dan.py doc_mt5`.\n"
          "5. Đọc mã trước khi chạy (mã của người khác). Việc `can_tai_ma=true`: box chưa có mã, tải theo `url` bằng Chrome.\n\n"
          "Số Python trong hàng chờ là MÔ PHỎNG, PHÍ TẠM; số tác giả (`so_tac_gia`) chưa đo.\n") % (time.strftime("%d/%m/%Y"),
                                                                                       len(bang_llm))
    with zipfile.ZipFile(ten, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(tep):
            z.write(p, str(p.relative_to(GOC)))
        for p, ten_z in phu:
            z.write(p, ten_z)
        z.writestr("MANIFEST.json", json.dumps({"tao_luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "so_viec": len(bang),
                                                "so_file": len(tep) + len(phu), "viec": bang,
                                                "so_the_cho_dich_llm": len(bang_llm), "the_cho_dich_llm": bang_llm},
                                               ensure_ascii=False, indent=1))
        z.writestr("HUONG_DAN.md", hd)
    for p, _ in phu:
        try:
            p.unlink()
        except OSError:
            pass
    return {"zip": str(ten), "so_viec": len(bang), "so_file": len(tep) + len(phu), "so_the_cho_dich_llm": len(bang_llm), "mb_goc": round(tong / 1048576, 1),
            "mb_zip": round(ten.stat().st_size / 1048576, 1), "can_tai_ma": sum(1 for b in bang if b["can_tai_ma"])}
