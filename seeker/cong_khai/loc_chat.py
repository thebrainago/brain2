# -*- coding: utf-8 -*-
"""Lọc CHẶT tín hiệu MQL5 công khai đã quét (data/cong_khai/tin_hieu.jsonl) — hướng mới 03/11/2026 (Anh duyệt).

Giữ: tuổi >= 24 tháng, tài khoản THẬT, <= 3 mã, max DD < 80 %, CAGR > 10 %/năm, đường growth không cháy
(sụt đỉnh-đáy trên đường (1+growth) < 80 %, tháng tệ nhất > -50 %). Hệ kiểu lưới/martingale/DCA (từ trang, phong cách,
hoặc lịch sử lệnh CSV nếu đã tải) phải SỐNG QUA giai đoạn biến động: có dữ liệu phủ năm 2022 (hoặc 03/2020) và năm đó không lỗ > 50 %.
Chỉ dùng số ĐO trên trang; thiếu -> 'CHƯA ĐO ĐƯỢC'.
    python -m seeker.cong_khai.loc_chat     -> reports/MQL5_LOC_CHAT.md + data/cong_khai/loc_chat.json
"""
from __future__ import annotations
import csv, json, math, re
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
VAO = GOC / "data/cong_khai/tin_hieu.jsonl"
CSV_DIR = GOC / "data/cong_khai/csv"
RA_MD = GOC / "reports/MQL5_LOC_CHAT.md"
RA_JSON = GOC / "data/cong_khai/loc_chat.json"
KIEU_LUOI = {"grid", "martingale", "dca"}


def ma_goc(s: str) -> str:
    s = re.sub(r"[^A-Z0-9]", "", str(s).upper())
    return s[:6] if re.match(r"^[A-Z]{6}", s) else s


def sut_duong_growth(mau) -> float | None:
    """Sụt đỉnh-đáy lớn nhất (%) trên đường vốn tương đối 1+growth/100 (growth MQL5 tính cả nạp/rút đã khử)."""
    if not mau:
        return None
    dinh, dd = None, 0.0
    for _, g in mau:
        v = 1 + float(g) / 100
        if v <= 0:
            return 100.0
        dinh = v if dinh is None else max(dinh, v)
        dd = max(dd, (1 - v / dinh) * 100)
    return dd


def luoi_tu_csv(sid: str) -> bool | None:
    """Lịch sử lệnh đã tải: >= 3 lệnh cùng chiều cùng mã mở chồng nhau = kiểu lưới/DCA. Không có tệp -> None."""
    f = CSV_DIR / ("%s.history.csv" % sid)
    if not f.exists():
        return None
    dong = list(csv.DictReader(f.open(encoding="utf-8", errors="replace"), delimiter=";"))
    dong.sort(key=lambda r: r.get("Time", ""))
    mo: dict = {}
    for r in dong:
        k = (r.get("Symbol"), r.get("Type"))
        if r.get("Direction") == "In":
            mo[k] = mo.get(k, 0) + 1
            if mo[k] >= 3:
                return True
        elif r.get("Direction") == "Out":
            k2 = (r.get("Symbol"), "Sell" if r.get("Type") == "Buy" else "Buy")
            mo[k2] = max(0, mo.get(k2, 0) - 1)
    return False


def la_luoi(r: dict) -> tuple[bool, str]:
    t = luoi_tu_csv(str(r.get("id")))
    if t is not None:
        return t, "lịch sử lệnh CSV"
    k = set(r.get("kieu") or []) | set((r.get("phong_cach") or {}).get("goi_y") or [])
    return bool(k & KIEU_LUOI), "từ khoá trang/phong cách"


def song_qua_bien_dong(r: dict) -> tuple[bool, str]:
    nam = (r.get("duong_cong") or {}).get("theo_nam_pct") or {}
    bd = str(r.get("bat_dau") or "9999")
    phu = [y for y in ("2020", "2022") if y in nam]
    if bd > "2022.01.31" or not phu:
        return False, "không có dữ liệu phủ 03/2020 hay 2022"
    xau = [y for y in phu if float(nam[y]) <= -50]
    if xau:
        return False, "năm %s lỗ <= -50 %%" % ",".join(xau)
    return True, "sống qua " + ", ".join("%s (%+.1f %%)" % (y, float(nam[y])) for y in phu)


def danh_gia(r: dict) -> dict:
    ly = []
    if r.get("nen_tang") != "MQL5":
        ly.append("không phải MQL5")
    if r.get("that_demo") != "that":
        ly.append("không chắc tài khoản thật")
    tuoi = r.get("tuoi_thang") or 0
    if tuoi < 24:
        ly.append("tuổi < 24 tháng")
    ma = sorted({ma_goc(s) for s in r.get("symbol") or []})
    if not ma or len(ma) > 3:
        ly.append("> 3 mã" if ma else "không rõ mã")
    dd = r.get("dd_pct"); cagr = r.get("cagr_pct")
    if dd is None or dd >= 80:
        ly.append("DD >= 80 % hoặc chưa đo")
    if cagr is None or cagr <= 10:
        ly.append("CAGR <= 10 %/năm hoặc chưa đo")
    dc = r.get("duong_cong") or {}
    sd = sut_duong_growth(dc.get("growth_mau"))
    if sd is None:
        ly.append("không có đường growth")
    elif sd >= 80:
        ly.append("đường growth sụt >= 80 % (cháy)")
    te = dc.get("thang_te_nhat_pct")
    if te is not None and float(te) <= -50:
        ly.append("tháng tệ nhất <= -50 %")
    luoi, nguon_luoi = la_luoi(r)
    bd_ok, bd_ghi = (True, "không áp dụng")
    if luoi:
        bd_ok, bd_ghi = song_qua_bien_dong(r)
        if not bd_ok:
            ly.append("lưới/martingale nhưng " + bd_ghi)
    diem = None
    if not ly:
        diem = round(min(float(cagr), 200) / max(float(dd), 5) * math.log2(tuoi / 12 + 1) * (0.8 if luoi else 1.0), 3)
    return {"id": str(r.get("id")), "ten": r.get("ten"), "url": r.get("url"), "tuoi_thang": tuoi, "ma": ma, "cagr_pct": cagr,
            "dd_pct": dd, "sut_growth_pct": None if sd is None else round(sd, 2), "luoi": luoi, "nguon_luoi": nguon_luoi,
            "bien_dong": bd_ghi, "may_chu": r.get("may_chu"), "mt": r.get("mt"), "bat_dau": r.get("bat_dau"),
            "dat": not ly, "ly_do_loai": ly, "diem": diem}


def chay(vao: Path = VAO) -> list[dict]:
    rows = [json.loads(x) for x in vao.read_text(encoding="utf-8").splitlines() if x.strip()]
    gap = {}
    for r in rows:                         # trùng id: giữ bản tuổi lớn nhất (quét mới nhất)
        k = str(r.get("id"))
        if k not in gap or (r.get("tuoi_thang") or 0) >= (gap[k].get("tuoi_thang") or 0):
            gap[k] = r
    return [danh_gia(r) for r in gap.values()]


def _s(x, f="%.2f"):
    return "CHƯA ĐO ĐƯỢC" if x is None else (f % x).replace(".", ",")


def ghi(kq: list[dict]) -> list[dict]:
    dat = sorted([x for x in kq if x["dat"]], key=lambda x: -x["diem"])
    from collections import Counter
    c = Counter(l for x in kq for l in x["ly_do_loai"])
    L = ["# Lọc CHẶT tín hiệu MQL5 công khai (03/11/2026)", "",
         "Nguồn: `data/cong_khai/tin_hieu.jsonl` (đã quét). Số liệu đo trên trang tín hiệu MQL5; Growth MQL5 đã khử nạp/rút.",
         "Tiêu chí: tuổi >= 24 tháng, tài khoản thật, <= 3 mã, DD < 80 %, CAGR > 10 %/năm, đường growth không cháy;"
         " lưới/martingale/DCA phải sống qua 03/2020 hoặc 2022.", "",
         "- Tổng tín hiệu (sau gộp trùng): **%d**" % len(kq), "- ĐẠT lọc chặt: **%d**" % len(dat), "",
         "## Lý do loại (một tín hiệu có thể nhiều lý do)", ""]
    L += ["- %s: %d" % (k, v) for k, v in c.most_common()]
    L += ["", "## Xếp hạng tín hiệu đạt", "",
          "| # | ID | Tên | Mã | Tuổi (tháng) | CAGR %/năm | DD % | Sụt growth % | Lưới? | Biến động | Máy chủ |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(dat, 1):
        L.append("| %d | [%s](%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, x["id"], x["url"], str(x["ten"]).replace("|", "/"), " ".join(x["ma"]), _s(x["tuoi_thang"], "%.1f"), _s(x["cagr_pct"]),
            _s(x["dd_pct"]), _s(x["sut_growth_pct"]), "có (%s)" % x["nguon_luoi"] if x["luoi"] else "không", x["bien_dong"], x["may_chu"]))
    RA_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    RA_JSON.write_text(json.dumps(dat, ensure_ascii=False, indent=1), encoding="utf-8")
    return dat


if __name__ == "__main__":
    d = ghi(chay())
    print("dat", len(d))
