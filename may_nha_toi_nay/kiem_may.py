# -*- coding: utf-8 -*-
"""kiem_may.py - Bước 0 của may_nha_toi_nay: kiểm tra máy nhà, CHỈ BÁO CÓ/KHÔNG cho khoá, không in giá trị khoá.

    python may_nha_toi_nay/kiem_may.py [--terminal "D:\\mt5_tester\\xm_micro\\terminal64.exe" ...] [--mt5]

In ra JSON: ổ đĩa (GB trống), Python, gói cần thiết, terminal MT5 tìm thấy (server đăng nhập lần cuối đọc từ
config\\common.ini, KHÔNG đọc login hay mật khẩu), khoá LLM có/không, tiến trình game đang chạy.
`--mt5`: gắn vào từng terminal bằng gói MetaTrader5 (không dùng mật khẩu) để xem tài khoản hedging hay netting.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
GOI_CAN = ["numpy", "pandas", "MetaTrader5", "psutil", "pyarrow", "requests"]


def o_dia() -> dict:
    ra = {}
    for o in ("C:\\", "D:\\", "E:\\", "/"):
        if os.path.exists(o):
            try:
                u = shutil.disk_usage(o)
                ra[o] = {"trong_gb": round(u.free / 1024 ** 3, 1), "tong_gb": round(u.total / 1024 ** 3, 1)}
            except OSError:
                pass
    return ra


def server_cuoi(terminal: Path) -> str:
    """Server ghi trong config\\common.ini của terminal portable (chỉ dòng Server=)."""
    for f in (terminal.parent / "config" / "common.ini",):
        if f.exists():
            for enc in ("utf-16", "utf-8", "cp1252"):
                try:
                    for dong in f.read_text(encoding=enc).splitlines():
                        if dong.strip().lower().startswith("server="):
                            return dong.split("=", 1)[1].strip()
                    break
                except (UnicodeError, OSError):
                    continue
    return ""


def tim_terminal(them: list[str]) -> list[Path]:
    ds = [Path(x) for x in them if x]
    for goc in (r"D:\mt5_tester", r"E:\mt5_tester", r"C:\Program Files"):
        g = Path(goc)
        if g.exists():
            for p in list(g.glob("*/terminal64.exe")):
                ds.append(p)
    ra, da = [], set()
    for p in ds:
        k = str(p).lower()
        if k not in da and p.exists():
            da.add(k); ra.append(p)
    return ra


def khoa_llm() -> dict:
    """Có/không - không bao giờ trả giá trị."""
    co_env = bool(os.environ.get("AIBOX_API_KEY"))
    co_cc = False
    try:
        from nhan import cau_llm as LLM
        co_cc = bool(LLM.tu_cc_switch((LLM.cau_hinh().get("cc_switch_provider") or "aibox")).get("khoa"))
    except Exception:
        co_cc = False
    return {"AIBOX_API_KEY": "CÓ" if co_env else "KHÔNG", "cc_switch_aibox": "CÓ" if co_cc else "KHÔNG",
            "BRAIN_LLM_PROXY": "CÓ" if os.environ.get("BRAIN_LLM_PROXY") else "KHÔNG"}


def game() -> list[str]:
    try:
        import psutil
        sys.path.insert(0, str(GOC / "mt5tools"))
        import dieu_phoi_song_song as DP
        return sorted({(p.info["name"] or "") for p in psutil.process_iter(["name"]) if (p.info["name"] or "").lower() in DP.GAME})
    except Exception:
        return []


def _pid_terminal(p: Path) -> set[int]:
    """PID terminal64 dang chay dung tep exe p (khong doc duoc exe -> bo qua)."""
    try:
        import psutil
    except Exception:
        return set()
    ra = set()
    for q in psutil.process_iter(["name", "exe"]):
        try:
            if (q.info["name"] or "").lower() == "terminal64.exe" and q.info["exe"] and \
                    os.path.normcase(q.info["exe"]) == os.path.normcase(str(p)):
                ra.add(q.pid)
        except Exception:
            pass
    return ra


def _dong_terminal_moi(p: Path, truoc: set[int]) -> None:
    """20/10/2026: mt5.initialize mo terminal neu chua chay, mt5.shutdown KHONG dong no -> terminal slot
    tester ngoi khong ca dem va buoc 7 tuong 'co phien khac'. Chi dong terminal do chinh lan kiem nay mo."""
    try:
        import psutil
    except Exception:
        return
    for pid in _pid_terminal(p) - truoc:
        try:
            q = psutil.Process(pid)
            q.terminate()
            q.wait(15)
        except Exception:
            pass


def mt5_tai_khoan(p: Path) -> dict:
    try:
        import MetaTrader5 as mt5
    except Exception:
        return {"loi": "chưa cài gói MetaTrader5"}
    truoc = _pid_terminal(p)
    try:
        if not mt5.initialize(path=str(p), timeout=60000):
            return {"loi": "initialize lỗi %s" % (mt5.last_error(),)}
        a = mt5.account_info()
        if a is None:
            return {"loi": "terminal chưa đăng nhập"}
        return {"server": a.server, "tien": a.currency, "don_bay": a.leverage,
                "hedging": a.margin_mode == mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING,
                "demo": a.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO}
    except Exception as e:  # noqa: BLE001
        return {"loi": str(e)[:120]}
    finally:
        try:
            mt5.shutdown()
        except Exception:
            pass
        _dong_terminal_moi(p, truoc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terminal", action="append", default=[])
    ap.add_argument("--mt5", action="store_true")
    a = ap.parse_args()
    tm = []
    for p in tim_terminal(a.terminal):
        x = {"duong_dan": str(p), "server_cuoi": server_cuoi(p), "metaeditor": (p.parent / "metaeditor64.exe").exists()}
        if a.mt5:
            x["tai_khoan"] = mt5_tai_khoan(p)
        tm.append(x)
    ra = {"may": platform.node(), "he_dieu_hanh": platform.platform(), "python": sys.version.split()[0],
          "python_exe": sys.executable, "goi": {g: bool(importlib.util.find_spec(g)) for g in GOI_CAN},
          "o_dia": o_dia(), "terminal": tm, "khoa_llm": khoa_llm(), "game_dang_chay": game(),
          "thu_muc_nhap_tay": os.path.exists(r"E:\brain2_nhap")}
    print(json.dumps(ra, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
