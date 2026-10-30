# -*- coding: utf-8 -*-
"""thu_thap_tin_hieu_cong_khai.py - Thu thập lịch sử lệnh CÔNG KHAI (trade-level).

Ngách: dịch ngược chiến lược từ nền tảng công bố hệ + lịch sử lệnh
(open/close, symbol, chiều, lot, SL/TP) — không cần đăng nhập, không vượt robots.

Nền tảng ưu tiên (xếp hạng xem reports/HE_TIN_HIEU_CONG_KHAI.md §6):
  1. FXBlue  — CSV công khai /users/<user>/csv (Allow /; Disallow /user/)
  2. MQL5    — CSV sau đăng nhập (máy nhà); parser dùng chung cho file đã tải

Dữ liệu ghi dưới BRAIN_DATA/tin_hieu_cong_khai/ (gitignore qua data/), KHÔNG commit.
"""
from __future__ import annotations

import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

from nhan import duong_dan as DD

UA = ("Mozilla/5.0 (compatible; BrainResearch/1.0; +research; "
      "research-only public trade history)")
FXBLUE_CSV = "https://www.fxblue.com/users/{user}/csv"
#: Khoảng nghỉ giữa request (lịch sự). FXBlue không ghi rate limit công khai.
NGHI_GIAY = 4.0

#: Tài khoản FXBlue đã xác nhận có CSV công khai (probe 30/10/2026).
FXBLUE_MAU = ("example", "fluidtrader-demo", "memberforex42", "673", "demo_20230303")


def thu_muc_goc() -> Path:
    """BRAIN_DATA/tin_hieu_cong_khai — không commit."""
    g = DD.kho_gia() / "tin_hieu_cong_khai"
    g.mkdir(parents=True, exist_ok=True)
    return g


def _parse_luc(s: str) -> str | None:
    """FXBlue '2024/08/01 23:01:22' → ISO; bỏ epoch 1970."""
    t = (s or "").strip()
    if not t or t.startswith("1970"):
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y.%m.%d %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
        try:
            dt = datetime.strptime(t, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    return None


def _f(x, mac=None):
    try:
        if x is None or str(x).strip() == "":
            return mac
        return float(str(x).replace(",", "").replace(" ", ""))
    except (TypeError, ValueError):
        return mac


def _chieu(buy_sell: str) -> int | None:
    t = (buy_sell or "").strip().lower()
    if t.startswith("buy") and "limit" not in t and "stop" not in t:
        return 1
    if t.startswith("sell") and "limit" not in t and "stop" not in t:
        return -1
    return None


def chuan_hoa_hang_fxblue(row: dict, *, he_id: str, nguon: str = "fxblue") -> dict | None:
    """Một hàng CSV FXBlue → dict chuẩn (Closed position only)."""
    typ = (row.get("Type") or "").strip().lower()
    if typ not in ("closed position", "closed trade", "trade"):
        return None
    ch = _chieu(row.get("Buy/sell") or row.get("Buy/Sell") or "")
    if ch is None:
        return None
    luc_vao = _parse_luc(row.get("Open time") or "")
    luc_ra = _parse_luc(row.get("Close time") or "")
    if not luc_vao:
        return None
    sym = (row.get("Symbol") or "").strip()
    if not sym:
        return None
    lot = _f(row.get("Lots"), 0.0) or 0.0
    if lot <= 0:
        return None
    sl = _f(row.get("S/L"))
    tp = _f(row.get("T/P"))
    # FXBlue đôi khi ghi 0 khi không có SL/TP
    if sl is not None and abs(sl) < 1e-12:
        sl = None
    if tp is not None and abs(tp) < 1e-12:
        tp = None
    giu = _f(row.get("Trade duration (hours)"))
    return {
        "nguon": nguon,
        "he_id": he_id,
        "ticket": str(row.get("Ticket") or "").strip(),
        "symbol": sym,
        "chieu": ch,
        "lot": lot,
        "gia_vao": _f(row.get("Open price")),
        "gia_ra": _f(row.get("Close price")),
        "luc_vao": luc_vao,
        "luc_ra": luc_ra,
        "sl": sl,
        "tp": tp,
        "loi": _f(row.get("Net profit"), _f(row.get("Profit"))),
        "swap": _f(row.get("Swap"), 0.0),
        "commission": _f(row.get("Commission"), 0.0),
        "pips": _f(row.get("Pips")),
        "giu_gio": giu,
        "mae": _f(row.get("Maximum adverse excursion (pips)")),
        "mfe": _f(row.get("Maximum favorable excursion (pips)")),
    }


def doc_csv_fxblue(duong: Path | str, *, he_id: str) -> list[dict]:
    """Đọc file CSV FXBlue (đã tải) → list lệnh chuẩn."""
    p = Path(duong)
    raw = p.read_text(encoding="utf-8-sig", errors="replace")
    if raw.lstrip().lower().startswith("<!doctype") or "<html" in raw[:200].lower():
        return []
    lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.startswith("sep=")]
    if not lines:
        return []
    rdr = csv.DictReader(lines)
    ra = []
    for row in rdr:
        h = chuan_hoa_hang_fxblue(row, he_id=he_id)
        if h:
            ra.append(h)
    return ra


def doc_csv_mql5_statement(duong: Path | str, *, he_id: str) -> list[dict]:
    """Parser CSV statement MT5/MQL5 đã export (máy nhà) — cột gần giống FXBlue.

    Chấp nhận header tiếng Anh phổ biến từ Report/Statement MT5.
    """
    p = Path(duong)
    raw = p.read_text(encoding="utf-8-sig", errors="replace")
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    # Bỏ dòng meta đầu nếu không phải header
    while lines and not re.search(r"(Symbol|Ticket|Order)", lines[0], re.I):
        lines.pop(0)
    if not lines:
        return []
    # Thử delimiter
    delim = "\t" if "\t" in lines[0] else ","
    rdr = csv.DictReader(lines, delimiter=delim)
    ra = []
    for row in rdr:
        # map alias
        alias = {
            "Type": row.get("Type") or row.get("Entry") or "Closed position",
            "Ticket": row.get("Ticket") or row.get("Order") or row.get("Deal") or "",
            "Symbol": row.get("Symbol") or row.get("Item") or "",
            "Lots": row.get("Lots") or row.get("Volume") or row.get("Size") or "",
            "Buy/sell": row.get("Buy/sell") or row.get("Type") or row.get("Direction") or "",
            "Open price": row.get("Open price") or row.get("Price") or row.get("Open") or "",
            "Close price": row.get("Close price") or row.get("Price") or row.get("Close") or "",
            "Open time": row.get("Open time") or row.get("Time") or row.get("Opening time") or "",
            "Close time": row.get("Close time") or row.get("Closing time") or "",
            "Profit": row.get("Profit") or row.get("Net profit") or "",
            "Net profit": row.get("Net profit") or row.get("Profit") or "",
            "S/L": row.get("S/L") or row.get("SL") or row.get("Stop Loss") or "",
            "T/P": row.get("T/P") or row.get("TP") or row.get("Take Profit") or "",
            "Swap": row.get("Swap") or "0",
            "Commission": row.get("Commission") or "0",
            "Pips": row.get("Pips") or "",
            "Trade duration (hours)": row.get("Trade duration (hours)") or "",
        }
        # Direction may be in Type for MT5 deals (buy/sell)
        if alias["Buy/sell"].lower() in ("buy", "sell"):
            alias["Type"] = "Closed position"
        h = chuan_hoa_hang_fxblue(alias, he_id=he_id, nguon="mql5_csv")
        if h:
            ra.append(h)
    return ra


def tai_csv_fxblue(user: str, timeout: int = 45) -> tuple[bytes | None, str]:
    """Tải CSV công khai. Trả (bytes|None, ly_do). Tôn trọng robots (Allow /users/)."""
    url = FXBLUE_CSV.format(user=user.strip())
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "text/csv,*/*"})
        with urlopen(req, timeout=timeout) as r:
            data = r.read()
            ctype = (r.headers.get("Content-Type") or "").lower()
    except Exception as e:  # noqa: BLE001
        return None, "loi_mang: %s" % str(e)[:120]
    if not data:
        return None, "rong"
    head = data[:80].lstrip().lower()
    if head.startswith(b"<!doctype") or b"<html" in head or b"no data published" in data[:2000].lower():
        return None, "chua_cong_khai_hoac_html"
    if b"Type,Ticket,Symbol" not in data[:500] and b"Type\tTicket" not in data[:500]:
        if b"sep=," in data[:20]:
            pass  # OK
        else:
            return None, "khong_phai_csv_fxblue"
    return data, "ok"


def luu_he(nguon: str, he_id: str, trades: list[dict], *, raw: bytes | None = None,
           meta: dict | None = None) -> Path:
    """Ghi raw + trades.jsonl + meta.json dưới thu_muc_goc()/nguon/he_id/."""
    thu = thu_muc_goc() / nguon / he_id
    thu.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        (thu / "raw.csv").write_bytes(raw)
    with (thu / "trades.jsonl").open("w", encoding="utf-8") as f:
        for t in trades:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    m = {
        "nguon": nguon,
        "he_id": he_id,
        "so_lenh": len(trades),
        "cap_nhat": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "symbols": sorted({t["symbol"] for t in trades}),
        **(meta or {}),
    }
    (thu / "meta.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    return thu


def thu_thap_fxblue(users: Iterable[str] | None = None, *, nghi: float = NGHI_GIAY,
                    in_ra=print) -> dict:
    """Thu thập CSV FXBlue cho danh sách user. Lưu dưới BRAIN_DATA."""
    ds = list(users) if users is not None else list(FXBLUE_MAU)
    ket = {"nguon": "fxblue", "he": [], "loi": []}
    for i, u in enumerate(ds):
        if i:
            time.sleep(nghi)
        data, ly = tai_csv_fxblue(u)
        if data is None:
            ket["loi"].append({"he_id": u, "ly_do": ly})
            in_ra("[fxblue] %s: %s" % (u, ly))
            continue
        tmp = thu_muc_goc() / "fxblue" / u
        tmp.mkdir(parents=True, exist_ok=True)
        raw_p = tmp / "raw.csv"
        raw_p.write_bytes(data)
        trades = doc_csv_fxblue(raw_p, he_id=u)
        thu = luu_he("fxblue", u, trades, raw=data,
                     meta={"url": FXBLUE_CSV.format(user=u), "ly_do_tai": ly})
        ket["he"].append({"he_id": u, "so_lenh": len(trades), "thu_muc": str(thu)})
        in_ra("[fxblue] %s: %d lenh -> %s" % (u, len(trades), thu))
    tong = thu_muc_goc() / "fxblue" / "tong_hop.json"
    tong.write_text(json.dumps(ket, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ket


def doc_he_da_luu(nguon: str, he_id: str) -> list[dict]:
    p = thu_muc_goc() / nguon / he_id / "trades.jsonl"
    if not p.exists():
        return []
    ra = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            ra.append(json.loads(ln))
    return ra


def liet_ke_he() -> list[dict]:
    g = thu_muc_goc()
    ra = []
    if not g.exists():
        return ra
    for nguon in sorted(p.name for p in g.iterdir() if p.is_dir()):
        for he in sorted(p.name for p in (g / nguon).iterdir() if p.is_dir()):
            meta = g / nguon / he / "meta.json"
            if meta.exists():
                try:
                    ra.append(json.loads(meta.read_text(encoding="utf-8")))
                except Exception:
                    ra.append({"nguon": nguon, "he_id": he})
    return ra


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Thu thap tin hieu cong khai (FXBlue CSV)")
    ap.add_argument("--users", nargs="*", default=None, help="Danh sach user FXBlue")
    ap.add_argument("--nghi", type=float, default=NGHI_GIAY)
    ap.add_argument("--liet-ke", action="store_true")
    a = ap.parse_args()
    if a.liet_ke:
        for h in liet_ke_he():
            print(json.dumps(h, ensure_ascii=False))
    else:
        thu_thap_fxblue(a.users, nghi=a.nghi)
