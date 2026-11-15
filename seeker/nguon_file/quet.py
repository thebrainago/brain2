# -*- coding: utf-8 -*-
"""Quét nguồn CÓ FILE (03/11/2026): MQL5 Code Base (Experts, mã nguồn), GitHub (repo EA MQL4/MQL5 + .set/backtest),
TradingView (script chiến lược mã mở — chỉ danh mục), forex-station, Forex Factory (chỉ ghi trạng thái truy cập).
Không đăng nhập, không vượt chống bot (403 = ghi 'bị chặn'), nghỉ >= 2 giây giữa các yêu cầu.
Tải mã về data/nguon_file/ (gitignore). Danh mục + điểm chất lượng: seeker/nguon/nguon_file.json + reports/NGUON_CO_FILE.md.
    python -m seeker.nguon_file.quet [--trang-codebase 5] [--repo-github 25]
"""
from __future__ import annotations
import argparse, html, json, math, re, subprocess, time
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
TAI = GOC / "data/nguon_file"
DM = GOC / "seeker/nguon/nguon_file.json"
MD = GOC / "reports/NGUON_CO_FILE.md"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BrainSeeker/1.0 (+lich su cong khai)"
NGHI = 2.0
_lan = [0.0]


def lay(url: str, nhi_phan: bool = False):
    cho = NGHI - (time.time() - _lan[0])
    if cho > 0:
        time.sleep(cho)
    _lan[0] = time.time()
    r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    body, _, ma = r.stdout.rpartition(b"\n")
    try:
        code = int(ma)
    except ValueError:
        code = 0
    return code, (body if nhi_phan else body.decode("utf-8", errors="replace"))


# ---------------- phân tích mã MQL (hàm thuần, có test) ----------------
LOT_TEN = re.compile(r"^\s*(?:input|extern|sinput)\s+double\s+(\w*(?:lot|Lot|LOT|volume|Volume)\w*)\s*=\s*([\d.]+)", re.M)


def tham_so_lot(ma: str) -> tuple[str, float] | None:
    m = LOT_TEN.search(ma)
    return (m.group(1), float(m.group(2))) if m else None


def la_ea_giao_dich(ma: str) -> bool:
    return bool(re.search(r"\bOnTick\s*\(", ma)) and bool(re.search(r"OrderSend|\.Buy\s*\(|\.Sell\s*\(|PositionOpen|trade\.", ma))


def de_dich_python(ma: str) -> bool:
    """Đơn giản để dịch tay/tự động sang Python: chỉ chỉ báo phổ biến, không include ngoài thư viện chuẩn, < 400 dòng."""
    inc = [x for x in re.findall(r'#include\s*[<"]([^>"]+)', ma) if not x.startswith(("Trade\\", "Trade/", "Indicators", "Arrays", "Expert"))]
    chi_bao = set(re.findall(r"\bi(MA|RSI|ATR|Bands|MACD|Stochastic|CCI|ADX|Envelopes|Momentum|SAR)\s*\(", ma))
    la = set(re.findall(r"\bi(Custom|Ichimoku|Fractals|Alligator|Gator|AO|AC)\s*\(", ma))
    return not inc and not la and ma.count("\n") < 400 and bool(chi_bao)


def diem_codebase(rating: float | None, tai: int | None, co_lot: bool) -> float:
    return round((rating or 0) * math.log10((tai or 0) + 10) * (1.0 if co_lot else 0.6), 3)


def _chuoi(body) -> str:
    return body if isinstance(body, str) else body.decode("utf-8", "replace")


# ---------------- MQL5 Code Base ----------------
def codebase(so_trang: int) -> list[dict]:
    from seeker.nguon_file.phan_tich import boc_trang_codebase
    from seeker.phan_loai_loi import phan_loai_http
    ids, out = [], []
    for p in range(1, so_trang + 1):
        url = "https://www.mql5.com/en/code/mt5/experts/best" + ("" if p == 1 else "/page%d" % p)
        code, t = lay(url)
        pl = phan_loai_http(code, _chuoi(t), url)
        if pl["loai"] != "ok":
            out.append({"nguon": "mql5_codebase", "id": "cb_loi_ds_%d" % p, "url": url, "ten": "danh sach",
                        "loai": pl["loai"], "ly_do": pl["ly_do"], "lan": "loi", "diem": 0, "tep": []})
            break
        ids += [x for x in re.findall(r'href="/en/code/(\d+)"', _chuoi(t)) if x not in ids]
    for cid in ids:
        url = "https://www.mql5.com/en/code/%s" % cid
        code, t = lay(url)
        pt = boc_trang_codebase(code, _chuoi(t), cid)
        if pt["loai"] != "ok":
            out.append({"nguon": "mql5_codebase", "id": "cb%s" % cid, "url": url, "ten": cid,
                        "loai": pt["loai"], "ly_do": pt["ly_do"], "lan": "loi", "diem": 0, "tep": []})
            if pt.get("dung_mien"):
                break
            continue
        tit_ten, tac_gia = pt["ten"], pt["tac_gia"]
        tep = pt["tep_mq5"]
        rec = {"nguon": "mql5_codebase", "id": "cb%s" % cid, "url": pt["url"],
               "ten": tit_ten, "tac_gia": tac_gia, "rating": pt["rating"], "tai_ve": pt["tai_ve"],
               "loai": "ok", "giay_phep": "MQL5 Code Base (mã mở, dùng tự do)", "tep": []}
        if len(tep) == 1:                              # 1 tệp .mq5 = tự chứa, biên dịch được
            c2, b = lay("https://www.mql5.com" + tep[0], nhi_phan=True)
            if c2 == 200 and b:
                d = TAI / "codebase" / cid; d.mkdir(parents=True, exist_ok=True)
                f = d / tep[0].rsplit("/", 1)[1]; f.write_bytes(b)
                ma = b.decode("utf-16", errors="ignore") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8", errors="replace")
                lot = tham_so_lot(ma)
                rec.update({"tep": [str(f.relative_to(GOC))], "url_ma_nguon": "https://www.mql5.com" + tep[0],
                            "ea_giao_dich": la_ea_giao_dich(ma), "tham_so_lot": lot[0] if lot else None, "de_dich_python": de_dich_python(ma)})
        rec["diem"] = diem_codebase(rec["rating"], rec["tai_ve"], bool(rec.get("tham_so_lot")))
        rec["lan"] = "co_ma_nguon" if rec.get("ea_giao_dich") else "loai"
        out.append(rec)
    return out


# ---------------- GitHub ----------------
def github(so_repo: int) -> list[dict]:
    from seeker.nguon_file.phan_tich import boc_github_tim
    out, seen = [], set()
    for q in ("expert+advisor+language:MQL5", "expert+advisor+language:MQL4", "mt5+ea+backtest+set"):
        url = "https://api.github.com/search/repositories?q=%s&sort=stars&per_page=%d" % (q, so_repo)
        code, t = lay(url)
        kq = boc_github_tim(code, _chuoi(t), url)
        if kq["loai"] != "ok":
            out.append({"nguon": "github", "id": "gh_loi", "url": url, "ten": q, "loai": kq["loai"],
                        "ly_do": kq["ly_do"], "lan": "loi", "diem": 0, "tep": [], "sao": None})
            if kq.get("dung_mien"):
                break
            continue
        for r in kq["items"]:
            if r["full_name"] in seen or len(seen) >= so_repo:
                continue
            seen.add(r["full_name"])
            url_cay = "https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (r["full_name"], r["default_branch"])
            c2, tr = lay(url_cay)
            if c2 != 200:
                from seeker.phan_loai_loi import phan_loai_http
                pl = phan_loai_http(c2, _chuoi(tr), url_cay)
                out.append({"nguon": "github", "id": "gh_" + re.sub(r"[^A-Za-z0-9]", "_", r["full_name"])[:50],
                            "url": r["html_url"], "ten": r["full_name"], "loai": pl["loai"], "ly_do": pl["ly_do"],
                            "lan": "loi", "diem": 0, "tep": [], "sao": r.get("stargazers_count")})
                if pl.get("dung_mien"):
                    return out
                continue
            cay = [x["path"] for x in json.loads(_chuoi(tr)).get("tree", [])]
            mq = [p for p in cay if p.lower().endswith((".mq5", ".mq4"))]
            st = [p for p in cay if p.lower().endswith(".set")]
            bt = [p for p in cay if re.search(r"backtest|report|strategytester", p, re.I) and p.lower().endswith((".htm", ".html", ".png", ".csv", ".xlsx", ".md"))]
            lic = (r.get("license") or {}).get("spdx_id")
            tu_do = lic in ("MIT", "Apache-2.0", "GPL-3.0", "GPL-2.0", "BSD-3-Clause", "BSD-2-Clause", "Unlicense", "MPL-2.0", "LGPL-3.0", "AGPL-3.0")
            rec = {"nguon": "github", "id": "gh_" + re.sub(r"[^A-Za-z0-9]", "_", r["full_name"])[:50], "url": r["html_url"],
                   "ten": r["full_name"], "sao": r["stargazers_count"], "giay_phep": lic or "không ghi", "so_mq": len(mq),
                   "so_set": len(st), "so_backtest": len(bt), "cap_nhat": r.get("pushed_at"), "tep": []}
            rec["diem"] = round(math.log10(r["stargazers_count"] + 10) * (1 + 0.5 * bool(st) + 0.5 * bool(bt)) * (1 if mq else 0), 3)
            if tu_do and mq:
                d = TAI / "github" / rec["id"]; d.mkdir(parents=True, exist_ok=True)
                for p in (mq + st)[:30]:
                    c3, b = lay("https://raw.githubusercontent.com/%s/%s/%s" % (r["full_name"], r["default_branch"], p), nhi_phan=True)
                    if c3 == 200:
                        f = d / p.replace("/", "__"); f.write_bytes(b); rec["tep"].append(str(f.relative_to(GOC)))
            rec["lan"] = "co_ma_nguon" if rec["tep"] else ("chi_danh_muc" if mq else "loai")
            out.append(rec)
    return out


# ---------------- TradingView / forex-station / Forex Factory ----------------
def tradingview() -> list[dict]:
    from seeker.nguon_file.phan_tich import boc_tradingview
    url = "https://www.tradingview.com/scripts/?script_type=strategies&script_access=open"
    code, t = lay(url)
    kq = boc_tradingview(code, _chuoi(t), url)
    if kq["loai"] != "ok":
        return [{"nguon": "tradingview", "id": "tv_loi", "url": url, "loai": kq["loai"], "ly_do": kq["ly_do"],
                 "trang_thai": kq["loai"], "lan": "loi", "diem": 0}]
    for s in kq["script"]:
        s["giay_phep"] = "Mozilla Public License 2.0 (mặc định TV mã mở) — chưa kiểm từng script"
        s["diem"] = 0.5
        s["ghi_chu"] = s["ly_do"]
    return kq["script"][:60]


def dien_dan() -> list[dict]:
    from seeker.nguon_file.phan_tich import boc_dien_dan
    out = []
    for nid, url in (("forexfactory", "https://www.forexfactory.com/forum/71-trading-systems"),
                     ("forex_station", "https://forex-station.com/viewforum.php?f=579496")):
        code, t = lay(url)
        kq = boc_dien_dan(code, _chuoi(t), url, nid)
        out.append({"nguon": nid, "id": nid, "url": url, "trang_thai": "HTTP %s" % code, "so_chu_de": kq.get("so_chu_de"),
                    "loai": kq["loai"], "lan": kq["lan"], "diem": 0, "ghi_chu": kq["ly_do"]})
    return out


def ghi(ds: list[dict]) -> None:
    DM.write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    c = Counter((x["nguon"], x["lan"]) for x in ds)
    L = ["# Nguồn có file (quét 03/11/2026 từ box, không đăng nhập)", "", "| Nguồn | Làn | Số |", "|---|---|---|"]
    L += ["| %s | %s | %d |" % (a, b, n) for (a, b), n in sorted(c.items())]
    for ng in ("mql5_codebase", "github"):
        top = sorted([x for x in ds if x["nguon"] == ng and x["lan"] == "co_ma_nguon"], key=lambda x: -x["diem"])[:20]
        L += ["", "## Top %s (làn A — có mã nguồn)" % ng, "", "| Điểm | Tên | Rating/Sao | Tải về | Lot input | Dịch Python? | .set | Link |", "|---|---|---|---|---|---|---|---|"]
        for x in top:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (str(x["diem"]).replace(".", ","), str(x["ten"]).replace("|", "/")[:50],
                     x.get("rating", x.get("sao")), x.get("tai_ve", "—"), x.get("tham_so_lot") or "CHƯA ĐO ĐƯỢC",
                     "có" if x.get("de_dich_python") else "không", x.get("so_set", "—"), x["url"]))
    L += ["", "## Truy cập diễn đàn", ""] + ["- %s: %s, %s chủ đề — %s" % (x["nguon"], x["trang_thai"], x["so_chu_de"], x["ghi_chu"]) for x in ds if x["nguon"] in ("forexfactory", "forex_station")]
    tv = [x for x in ds if x["nguon"] == "tradingview"]
    L += ["", "- TradingView chiến lược mã mở: %d script vào danh mục (làn B, cần dịch Pine)." % len([x for x in tv if x["lan"] != "loai"])]
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--trang-codebase", type=int, default=5); ap.add_argument("--repo-github", type=int, default=25)
    a = ap.parse_args()
    ds = dien_dan(); print("dien_dan", [(x["id"], x["trang_thai"]) for x in ds], flush=True)
    ds += tradingview(); print("tv", len(ds), flush=True)
    ds += github(a.repo_github); print("github", len(ds), flush=True)
    ds += codebase(a.trang_codebase); print("codebase", len(ds), flush=True)
    ghi(ds)
