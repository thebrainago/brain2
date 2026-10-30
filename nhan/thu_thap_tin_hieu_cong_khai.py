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
                "%Y.%m.%d %H:%M:%S", "%d.%m.%Y %H:%M:%S",
                "%m.%d.%Y %H:%M", "%m.%d.%Y %H:%M:%S",
                "%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M"):
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
    while lines and not re.search(r"(Symbol|Ticket|Order|Volume|Time)", lines[0], re.I):
        lines.pop(0)
    if not lines:
        return []
    # Thử delimiter (MQL5 Export to CSV: History dùng ';')
    header = lines[0]
    if "\t" in header:
        delim = "\t"
    elif header.count(";") >= max(2, header.count(",")):
        delim = ";"
    else:
        delim = ","
    rdr = csv.DictReader(lines, delimiter=delim)
    # MQL5 history Export often: Time;Type;Volume;Symbol;Price;...
    fieldnames = list(rdr.fieldnames or [])
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
        bs = (alias["Buy/sell"] or "").strip().lower()
        if bs in ("buy", "sell", "buy deal", "sell deal"):
            alias["Buy/sell"] = "Buy" if bs.startswith("buy") else "Sell"
            alias["Type"] = "Closed position"
        # Skip pure balance rows (no symbol)
        if not alias["Symbol"] and bs in ("balance", "credit", "deposit", "withdrawal"):
            continue
        h = chuan_hoa_hang_fxblue(alias, he_id=he_id, nguon="mql5_csv")
        if h:
            ra.append(h)
    return ra


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
    ds = list(users) if users is not None else list(FXBLUE_SEED)
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
    tong.parent.mkdir(parents=True, exist_ok=True)
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



def tai_csv_fxblue(user: str, timeout: int = 45) -> tuple[bytes | None, str]:
    """Tải CSV công khai (theo api.fxblue.com, fallback www). Tôn trọng robots."""
    for url in (FXBLUE_CSV_API.format(user=user.strip()),
                FXBLUE_CSV.format(user=user.strip())):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "text/csv,*/*"})
            with urlopen(req, timeout=timeout) as r:
                data = r.read()
        except Exception as e:  # noqa: BLE001
            last = "loi_mang: %s" % str(e)[:120]
            continue
        if not data:
            last = "rong"
            continue
        head = data[:80].lstrip().lower()
        if head.startswith(b"<!doctype") or b"<html" in head:
            last = "html"
            continue
        if b"no data published" in data[:2000].lower():
            return None, "chua_cong_khai"
        if b"Type,Ticket,Symbol" not in data[:800] and b"sep=," not in data[:20]:
            last = "khong_phai_csv_fxblue"
            continue
        return data, "ok"
    return None, last if "last" in dir() else "loi"


def kham_pha_user_fxblue(*, nghi: float = NGHI_GIAY, in_ra=print) -> list[str]:
    """Khám phá username FXBlue: seed + DuckDuckGo HTML (public) + sitemap."""
    found: set[str] = set(FXBLUE_SEED)
    # sitemap
    try:
        req = Request("https://www.fxblue.com/sitemap.xml",
                      headers={"User-Agent": UA})
        with urlopen(req, timeout=45) as r:
            sm = r.read().decode("utf-8", "replace")
        for u in re.findall(r"fxblue\.com/users/([A-Za-z0-9_\-]{2,40})", sm, re.I):
            if u.lower() not in JUNK_USER:
                found.add(u)
    except Exception as e:  # noqa: BLE001
        in_ra("[kham_pha] sitemap: %s" % e)
    # DDG HTML (polite)
    time.sleep(nghi)
    try:
        from urllib.parse import quote
        q = quote("site:fxblue.com/users/")
        req = Request("https://html.duckduckgo.com/html/?q=" + q,
                      headers={"User-Agent": UA})
        with urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
        for u in re.findall(r"fxblue\.com/users/([A-Za-z0-9_\-]{2,40})", html, re.I):
            if u.lower() not in JUNK_USER:
                found.add(u)
    except Exception as e:  # noqa: BLE001
        in_ra("[kham_pha] ddg: %s" % e)
    ra = sorted(found)
    in_ra("[kham_pha] %d user FXBlue" % len(ra))
    return ra


def liet_ke_mql5_signals(*, tuoi_min_ngay: int = 365, dd_max: float = 50.0,
                         growth_min: float = 0.0, real: bool = True,
                         nghi: float = NGHI_GIAY, toi_da_trang: int = 3,
                         in_ra=print) -> list[dict]:
    """Liệt kê tín hiệu MQL5 công khai (trang /en/signals) — không login.

    Lịch sử lệnh CSV cần session đăng nhập + export GUI (máy nhà); hàm này chỉ
    lấy danh sách id + meta thô từ HTML public.
    """
    base = ("https://www.mql5.com/en/signals?period={period}&risk={risk}"
            "&profit={profit}&type={typ}&sort=rating&direction=desc&page={page}")
    period = max(1, tuoi_min_ngay)
    typ = "real" if real else "demo"
    ra: list[dict] = []
    seen: set[str] = set()
    for page in range(1, toi_da_trang + 1):
        if page > 1:
            time.sleep(nghi)
        url = base.format(period=period, risk=int(dd_max), profit=int(growth_min),
                          typ=typ, page=page)
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
            with urlopen(req, timeout=45) as r:
                html = r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            in_ra("[mql5] page %d: %s" % (page, e))
            break
        if "Just a moment" in html or "cf-browser" in html.lower():
            in_ra("[mql5] cloudflare — cần máy nhà/browser")
            break
        ids = re.findall(r"/en/signals/(\d+)", html)
        for i in ids:
            if i in seen:
                continue
            seen.add(i)
            ra.append({
                "signal_id": i,
                "url": "https://www.mql5.com/en/signals/%s" % i,
                "nguon": "mql5",
                "filter": {"tuoi_min_ngay": tuoi_min_ngay, "dd_max": dd_max,
                           "growth_min": growth_min, "real": real},
            })
        in_ra("[mql5] page %d: +%d (tong %d)" % (page, len(ids), len(ra)))
    thu = thu_muc_goc() / "mql5"
    thu.mkdir(parents=True, exist_ok=True)
    (thu / "danh_sach_signals.json").write_text(
        json.dumps({"cap_nhat": time.strftime("%Y-%m-%dT%H:%M:%S"), "he": ra},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ra


def tai_myfxbook_public(system_path: str, timeout: int = 45) -> tuple[bytes | None, str]:
    """Tải trang/export công khai Myfxbook (thử từ IP nhà — box thường bị CF 403).

    system_path ví dụ: 'members/xxx/yyy' hoặc full URL. Không login, không cookie.
    """
    if system_path.startswith("http"):
        url = system_path
    else:
        url = "https://www.myfxbook.com/" + system_path.lstrip("/")
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/csv,*/*"})
        with urlopen(req, timeout=timeout) as r:
            data = r.read()
            code = getattr(r, "status", 200)
    except Exception as e:  # noqa: BLE001
        return None, "loi_mang: %s" % str(e)[:160]
    if not data:
        return None, "rong"
    low = data[:500].lower()
    if b"just a moment" in low or b"cf-browser" in low or b"attention required" in low:
        return None, "cloudflare"
    return data, "ok status=%s" % code


HUONG_DAN_MQL5_EXPORT = """
## MQL5 Signals — tải lịch sử lệnh (máy nhà, session đã login)

KHÔNG trích cookie/token từ profile browser. Dùng GUI bình thường:

1. Mở Chrome/Edge đã login https://www.mql5.com (user đã cấp).
2. Vào từng signal trong `data/tin_hieu_cong_khai/mql5/danh_sach_signals.json`.
3. Tab **History** (hoặc Trading History) → nút **Export** / **CSV** / **Download**.
4. Lưu file vào `E:\\brain2_grok_tin_hieu\\data\\mql5_csv\\<signal_id>.csv`.
5. Chạy: `python -m nhan.thu_thap_tin_hieu_cong_khai --nap-mql5-csv E:\\brain2_grok_tin_hieu\\data\\mql5_csv`
6. Sau đó: `python -m nhan.dich_nguoc_tin_hieu --chi-xep mql5_csv <signal_id> --track auto`

Nếu trang không có Export CSV: dùng MT5 terminal → Signal → History → Report CSV
(cùng tài khoản demo/signal đã subscribe — chỉ demo 345930355).
"""



def doc_csv_myfxbook_history(duong: Path | str, *, he_id: str) -> list[dict]:
    """Parser CSV rebuilt from Myfxbook HTML History tab (tools/tai_lich_su_trinh_duyet)."""
    p = Path(duong)
    raw = p.read_text(encoding="utf-8-sig", errors="replace")
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return []
    rdr = csv.DictReader(lines)
    ra = []
    for row in rdr:
        alias = {
            "Type": "Closed position",
            "Ticket": "",
            "Symbol": row.get("Symbol") or "",
            "Lots": row.get("Lots") or "",
            "Buy/sell": row.get("Buy/sell") or row.get("Action") or "",
            "Open price": row.get("Open price") or "",
            "Close price": row.get("Close price") or "",
            "Open time": row.get("Open time") or "",
            "Close time": row.get("Close time") or "",
            "Profit": row.get("Profit") or "",
            "Net profit": row.get("Profit") or "",
            "Pips": row.get("Pips") or "",
            "S/L": "",
            "T/P": "",
            "Swap": "0",
            "Commission": "0",
            "Trade duration (hours)": "",
        }
        h = chuan_hoa_hang_fxblue(alias, he_id=he_id, nguon="myfxbook")
        if h:
            ra.append(h)
    return ra


def nap_myfxbook_csv_thu_muc(thu: Path | str, *, in_ra=print) -> dict:
    """Nạp CSV/jsonl lịch sử Myfxbook (HTML History scrape) vào kho chuẩn."""
    thu = Path(thu)
    ket = {"nguon": "myfxbook", "he": [], "loi": []}
    if not thu.exists():
        return {"loi": [{"ly_do": "khong_co_thu_muc", "thu": str(thu)}]}
    files = sorted(set(list(thu.glob("*_history.csv")) + list(thu.glob("*.csv"))))
    for p in files:
        he_id = p.stem.replace("_history", "")
        trades = doc_csv_myfxbook_history(p, he_id=he_id)
        if not trades:
            ket["loi"].append({"he_id": he_id, "ly_do": "0_lenh", "file": str(p)})
            continue
        luu_he("myfxbook", he_id, trades, raw=p.read_bytes(),
               meta={"file": str(p), "phuong_thuc": "html_history"})
        ket["he"].append({"he_id": he_id, "so_lenh": len(trades)})
        in_ra("[myfxbook] %s: %d lenh" % (he_id, len(trades)))
    return ket


def nap_mql5_csv_thu_muc(thu: Path | str, *, in_ra=print) -> dict:
    """Nạp các CSV statement MQL5/MT5 đã export thủ công."""
    thu = Path(thu)
    ket = {"nguon": "mql5_csv", "he": [], "loi": []}
    if not thu.exists():
        return {"loi": [{"ly_do": "khong_co_thu_muc", "thu": str(thu)}]}
    for p in sorted(thu.glob("*.csv")):
        he_id = p.stem
        trades = doc_csv_mql5_statement(p, he_id=he_id)
        if not trades:
            ket["loi"].append({"he_id": he_id, "ly_do": "0_lenh"})
            continue
        luu_he("mql5_csv", he_id, trades, raw=p.read_bytes(),
               meta={"file": str(p)})
        ket["he"].append({"he_id": he_id, "so_lenh": len(trades)})
        in_ra("[mql5_csv] %s: %d lenh" % (he_id, len(trades)))
    return ket

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Thu thap tin hieu cong khai (FXBlue CSV)")
    ap.add_argument("--users", nargs="*", default=None, help="Danh sach user FXBlue")
    ap.add_argument("--nghi", type=float, default=NGHI_GIAY)
    ap.add_argument("--liet-ke", action="store_true")
    ap.add_argument("--kham-pha", action="store_true", help="Kham pha user FXBlue roi thu thap")
    ap.add_argument("--mql5-list", action="store_true", help="Liet ke signal MQL5 public")
    ap.add_argument("--nap-mql5-csv", default="", help="Thu muc CSV MQL5 da export")
    ap.add_argument("--nap-myfxbook-csv", default="", help="Thu muc CSV Myfxbook HTML history")
    ap.add_argument("--seed", action="store_true", help="Dung FXBLUE_SEED")
    a = ap.parse_args()
    if a.liet_ke:
        for h in liet_ke_he():
            print(json.dumps(h, ensure_ascii=False))
    elif a.mql5_list:
        liet_ke_mql5_signals(nghi=a.nghi)
    elif a.nap_mql5_csv:
        print(json.dumps(nap_mql5_csv_thu_muc(a.nap_mql5_csv), ensure_ascii=False, indent=2))
    elif a.nap_myfxbook_csv:
        print(json.dumps(nap_myfxbook_csv_thu_muc(a.nap_myfxbook_csv), ensure_ascii=False, indent=2))
    elif a.kham_pha:
        users = kham_pha_user_fxblue(nghi=a.nghi)
        thu_thap_fxblue(users, nghi=a.nghi)
    else:
        users = list(FXBLUE_SEED) if a.seed and not a.users else a.users
        thu_thap_fxblue(users, nghi=a.nghi)


# =============================================================================
# Mass discovery + Myfxbook + MQL5 public list (30/10/2026 scale-up)
# =============================================================================

FXBLUE_CSV_API = "https://api.fxblue.com/users/{user}/csv"
#: Public Myfxbook system paths (member/system/account) for HTML History scrape.
MYFXBOOK_SEED = (
    "rodrigo122/13139634/12285522",
)

#: Seed + đã xác nhận có CSV công khai (probe 30/10/2026).
FXBLUE_SEED = (
    "example", "fluidtrader-demo", "memberforex42", "673", "demo_20230303",
    "artificial-quant-1", "66367297", "eshuu2025", "managed-forex", "20429853",
    "area_bursatil", "forexrobotinfo_160",
)
JUNK_USER = frozenset({
    "account_info", "portfolio", "stats", "widgets", "printable", "rss", "csv",
    "overviewscript", "banner", "system_isp", "xxxxx",
})
