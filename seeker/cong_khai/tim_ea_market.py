# -*- coding: utf-8 -*-
"""Top tín hiệu lọc chặt -> tác giả có bán EA trên MQL5 Market không, có Free Demo không, giá bao nhiêu.
Đọc trang tín hiệu (link tác giả + link product trong mô tả) và trang /users/<id>/seller (mục Products). curl công khai,
không đăng nhập. Ra data/cong_khai/ea_market.json + chèn bảng vào reports/MQL5_LOC_CHAT.md.
    python -m seeker.cong_khai.tim_ea_market [--top 30]
"""
from __future__ import annotations
import argparse, html, json, re, subprocess, time
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
LOC = GOC / "data/cong_khai/loc_chat.json"
RA = GOC / "data/cong_khai/ea_market.json"
MD = GOC / "reports/MQL5_LOC_CHAT.md"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def tai(url: str) -> str:
    time.sleep(1.5)
    r = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def product_links(t: str) -> list[str]:
    return sorted({m for m in re.findall(r"mql5\.com/[a-z]{2}/market/product/(\d+|[a-z0-9_-]+)", t) + re.findall(r'href="/[a-z]{2}/market/product/([a-z0-9_-]+)', t)})


TU_LOAI = re.compile(r"\b(tool|manager|copier|copy|panel|utility|utilities|indicator|library|dashboard|calculator|sizer|"
                     r"account details|info|spread|trade assistant|assistant|closer|news filter|telegram|equity protector|risk manager)\b", re.I)


def la_ea_giao_dich(tieu_de: str) -> bool:
    """Chỉ giữ mục Experts thật sự vào lệnh: tiêu đề MQL5 'Trading Robot (Expert Advisor)' và tên không là công cụ."""
    if not re.search(r"Trading Robot \(Expert Advisor\)", tieu_de):
        return False
    ten = tieu_de.split("|")[0]
    return not TU_LOAI.search(ten)


def doc_product(pid: str) -> dict:
    t = tai("https://www.mql5.com/en/market/product/%s" % pid)
    tit = re.search(r"<title>([^<]*)", t)
    gia = re.search(r'"price"\s*:\s*"?([\d.]+)', t) or re.search(r'class="price[^"]*"[^>]*>\s*([\d.,]+)', t)
    demo = bool(re.search(r"Free Demo|Download demo|Demo version", t, re.I))
    ti = tit.group(1) if tit else ""
    loai = "MT5" if "MetaTrader 5" in ti else ("MT4" if "MetaTrader 4" in ti else "CHƯA ĐO ĐƯỢC")
    ea = la_ea_giao_dich(ti)
    return {"url": "https://www.mql5.com/en/market/product/%s" % pid, "ten": html.unescape(tit.group(1).strip()) if tit else "CHƯA ĐO ĐƯỢC",
            "gia_usd": gia.group(1) if gia else "CHƯA ĐO ĐƯỢC", "free_demo": demo, "nen_tang": loai, "la_ea": ea}


def kiem(sig: dict) -> dict:
    t = tai(sig["url"])
    u = re.search(r"/en/users/([A-Za-z0-9_.-]+)", t)
    ids = product_links(t)
    tac_gia = u.group(1) if u else None
    if tac_gia:
        ids = sorted(set(ids) | set(product_links(tai("https://www.mql5.com/en/users/%s/seller" % tac_gia))))
    sp = [p for p in (doc_product(x) for x in ids[:40]) if p["la_ea"]]
    return {"id": sig["id"], "ten": sig["ten"], "tac_gia": tac_gia, "san_pham": sp,
            "co_ea": bool(sp), "co_demo_mt5": any(p["free_demo"] and p["nen_tang"] == "MT5" for p in sp)}


def chen_md(kq: list[dict]) -> None:
    L = ["", "## EA trên MQL5 Market của tác giả (top %d, quét 03/11/2026 bằng curl công khai)" % len(kq), "",
         "| ID tín hiệu | Tên | Tác giả | EA Market | Free Demo | Giá USD | Nền tảng |", "|---|---|---|---|---|---|---|"]
    for x in kq:
        if not x["san_pham"]:
            L.append("| %s | %s | %s | không thấy | — | — | — |" % (x["id"], x["ten"], x["tac_gia"] or "CHƯA ĐO ĐƯỢC"))
        for p in x["san_pham"]:
            L.append("| %s | %s | %s | [%s](%s) | %s | %s | %s |" % (x["id"], x["ten"], x["tac_gia"], p["ten"].replace("|", "/")[:60], p["url"],
                     "có" if p["free_demo"] else "không thấy", p["gia_usd"], p["nen_tang"]))
    t = MD.read_text(encoding="utf-8").split("\n## EA trên MQL5 Market")[0].rstrip("\n")
    MD.write_text(t + "\n" + "\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--top", type=int, default=30); a = ap.parse_args()
    top = json.loads(LOC.read_text(encoding="utf-8"))[:a.top]
    kq = []
    for s in top:
        try:
            kq.append(kiem(s))
        except Exception as e:
            kq.append({"id": s["id"], "ten": s["ten"], "tac_gia": None, "san_pham": [], "co_ea": False, "co_demo_mt5": False, "loi": str(e)[:200]})
        print(kq[-1]["id"], kq[-1]["co_ea"], kq[-1]["co_demo_mt5"], flush=True)
    RA.write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
    chen_md(kq)
