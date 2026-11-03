"""Dọn ổ đĩa định kỳ cho slot MT5 của brain2 (máy nhà Windows).

Chỉ dọn slot KHÔNG có terminal64.exe đang chạy từ thư mục đó và không nằm trong BRAIN_SLOT_BO_QUA
(mặc định g3;g6). Xoá: Tester/cache, Tester/logs, logs (*.log) cũ hơn 2 ngày, báo cáo *.htm cũ đã có
bản trong hang_doi/bao_cao. Cảnh báo ổ nào trống < BRAIN_O_TRONG_MIN_GB (mặc định 10).
Chạy: python may_nha\\don_o_dia.py [--thu]  (--thu = chỉ in, không xoá)
"""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tho_mt5 as T  # noqa: E402

GOC_SLOT = [Path(p) for p in os.environ.get("BRAIN_GOC_SLOT", r"E:\brain2_grok\mt5_slots;E:\mt5_tester;D:\mt5_tester;C:\MT5slots;C:\mt5_tester").split(";") if p]
BO_QUA = set(os.environ.get("BRAIN_SLOT_BO_QUA", "g3;g6").lower().split(";"))


def thu_muc_terminal_dang_chay() -> set:
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process -Filter \"Name='terminal64.exe' or Name='metatester64.exe'\" | % ExecutablePath"],
                           capture_output=True, text=True, timeout=60)
        return {str(Path(x.strip()).parent).lower() for x in r.stdout.splitlines() if x.strip()}
    except Exception:
        return None


def main(argv=None) -> int:
    thu = "--thu" in (argv or sys.argv[1:])
    dang = thu_muc_terminal_dang_chay()
    if dang is None:
        print("không đọc được tiến trình -> không dọn"); dang_ok = False
    else:
        dang_ok = True
    kho = T.GOC / "hang_doi" / "bao_cao"
    for g in GOC_SLOT:
        if not g.is_dir() or not dang_ok:
            continue
        for s in sorted(p for p in g.iterdir() if p.is_dir() and (p / "terminal64.exe").exists()):
            if s.name.lower() in BO_QUA or str(s).lower() in dang:
                print("bỏ qua", s); continue
            print(s, "(thử)" if thu else T.don_slot(s, kho))
    for o, gb in T.canh_bao_o_day(float(os.environ.get("BRAIN_O_TRONG_MIN_GB", "10"))):
        print("CẢNH BÁO: ổ %s chỉ còn %.1f GB trống" % (o, gb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
