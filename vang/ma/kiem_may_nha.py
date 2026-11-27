# -*- coding: utf-8 -*-
"""Kiểm máy nhà: RAM, CPU, cổng Fxaurum, slot p3/p4. Không tắt tiến trình, không đổi nguồn điện."""
from __future__ import annotations
import json, os, socket, time
from pathlib import Path

def main():
    import psutil
    mem = psutil.virtual_memory()
    out = {
        "host": os.environ.get("COMPUTERNAME"),
        "luc_vn_utc7": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_pct": psutil.cpu_percent(1),
        "ram_trong_gb": round(mem.available / 1024**3, 2),
        "ram_tong_gb": round(mem.total / 1024**3, 2),
        "o_trong_gb": {},
        "cong_9001": None,
        "slot": {},
        "tien_trinh_lien_quan": [],
    }
    for letter in "CDEF":
        p = f"{letter}:/"
        if os.path.exists(p):
            u = os.statvfs(p) if hasattr(os, "statvfs") else None
            if u:
                out["o_trong_gb"][letter] = round(u.f_bavail * u.f_frsize / 1024**3, 1)
            else:
                import shutil
                out["o_trong_gb"][letter] = round(shutil.disk_usage(p).free / 1024**3, 1)
    s = socket.socket(); s.settimeout(2)
    r = s.connect_ex(("127.0.0.1", 9001)); s.close()
    out["cong_9001"] = "mo" if r == 0 else f"dong({r})"
    for slot in [r"E:\mt5_tester\p3", r"E:\mt5_tester\p4", r"E:\mt5_tester\p1", r"E:\mt5_tester\p6"]:
        out["slot"][slot] = os.path.exists(slot)
    keys = ("terminal64", "metatester64", "fxaurum", "rithmic", "sierra", "python")
    for p in psutil.process_iter(["pid", "name", "memory_info", "exe", "cmdline"]):
        try:
            n = (p.info.get("name") or "").lower()
            exe = (p.info.get("exe") or "").lower()
            if any(k in n or k in exe for k in keys):
                rss = p.info["memory_info"].rss / 1024**3 if p.info.get("memory_info") else 0
                cmd = " ".join(p.info.get("cmdline") or [])
                # cắt, không in đường dẫn bí mật
                out["tien_trinh_lien_quan"].append({
                    "pid": p.info["pid"], "ten": p.info.get("name"), "ram_gb": round(rss, 2),
                    "exe": (p.info.get("exe") or "")[:120],
                    "cmd_dau": cmd[:180],
                })
        except (psutil.Error, TypeError):
            continue
    out["duoc_mo_tester_p3_p4"] = out["ram_trong_gb"] >= 11.0  # 6 GB giữ + ~5 GB một test
    print(json.dumps(out, ensure_ascii=False, indent=2))
    dest = Path(r"E:\brain2_tmp\vang")
    try:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "kiem_may_nha.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print("khong_ghi_duoc", e)

if __name__ == "__main__":
    main()
