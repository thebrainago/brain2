# -*- coding: utf-8 -*-
"""Chạy làn lịch sử công khai.
python3 -m seeker.cong_khai.chay --trang 3 --gian-cach 3
Đầu ra: data/cong_khai/tin_hieu.jsonl (gitignored), reports/NGUON_CONG_KHAI_DAT.md, reports/cong_khai/THONG_KE.json,
sổ kết quả (nguon=CONG_KHAI) cho tín hiệu ĐẠT."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path

from seeker.thu_thap import ThuThap
from . import mql5, myfxbook, nen_tang_khac as NK
from .cham_diem import dat, diem_xep_hang, DD_MAX, CAGR_MIN

GOC = Path(__file__).resolve().parents[2]
DATA = GOC / "data" / "cong_khai"
BAO_CAO = GOC / "reports" / "NGUON_CONG_KHAI_DAT.md"
THONG_KE = GOC / "reports" / "cong_khai" / "THONG_KE.json"
DS_CU = GOC / "reports" / "HE_TIN_HIEU_CONG_KHAI.md"


def id_tu_bao_cao_cu(p=DS_CU) -> list[str]:
    return sorted(set(re.findall(r"mql5\.com/en/signals/(\d{5,9})", p.read_text(encoding="utf-8")))) if p.exists() else []


def cham(t: dict) -> dict:
    t["trang_thai"] = dat(t.get("dd_pct"), t.get("cagr_pct"))
    t["diem_xep_hang"] = diem_xep_hang(t) if t["trang_thai"] == "DAT" else None
    return t


def quet(tt: ThuThap, so_trang: int = 3, them_id=(), log=print, muc_tieu: int = 0) -> tuple[list[dict], dict]:
    ra, dem = [], {}
    # MQL5: nhiều cách sắp × mt4/mt5 × nhiều trang, dừng khi đủ muc_tieu id
    ids = list(dict.fromkeys(list(them_id) + id_tu_bao_cao_cu()))
    theo_sap = {}
    for p in range(1, so_trang + 1):
        for sap in mql5.SAP_XEP:
            for mt in ("mt5", "mt4"):
                if muc_tieu and len(ids) >= muc_tieu: break
                h = tt.tai(mql5.url_danh_sach(mt, p, sap))
                if h:
                    moi = [i for i in mql5.id_tu_danh_sach(h) if i not in ids]; ids += moi
                    theo_sap[sap or "mac_dinh"] = theo_sap.get(sap or "mac_dinh", 0) + len(moi)
        log(f"danh sách trang {p}: {len(ids)} id")
    dem["MQL5"] = {"id_tim_thay": len(ids), "doc_duoc": 0, "khong_doc": 0, "id_moi_theo_cach_sap": theo_sap}
    for i, sid in enumerate(ids):
        h = tt.tai(f"{mql5.GOC}/en/signals/{sid}")
        if not h:
            dem["MQL5"]["khong_doc"] += 1; continue
        ra.append(cham(mql5.phan_tich(h, sid))); dem["MQL5"]["doc_duoc"] += 1
        if i % 50 == 0: log(f"MQL5 {i}/{len(ids)}")
    # Myfxbook
    dem["Myfxbook"] = {"doc_duoc": 0, "khong_doc": 0}
    for u in myfxbook.DS:
        h = tt.tai(u)
        if not h:
            dem["Myfxbook"]["khong_doc"] += 1; continue
        for link in myfxbook.link_he_thong(h)[:50]:
            hh = tt.tai(link)
            if hh: ra.append(cham(myfxbook.phan_tich(hh, link))); dem["Myfxbook"]["doc_duoc"] += 1
            else: dem["Myfxbook"]["khong_doc"] += 1
    # LiteFinance
    dem["LiteFinance"] = {"doc_duoc": 0, "khong_doc": 0}
    h = tt.tai(NK.LITEFINANCE_DS)
    if h:
        ds = [cham(x) for x in NK.litefinance_danh_sach(h)]; ra += ds; dem["LiteFinance"]["doc_duoc"] = len(ds)
    else:
        dem["LiteFinance"]["khong_doc"] += 1
    for sid in ("2104574", "2107238", "2589240"):
        h = tt.tai(NK.LITEFINANCE_CT.format(id=sid))
        if not h or "Profitability (All time)" in h and "traders/info?id=" + sid not in h[:3000]:
            dem["LiteFinance"]["chi_tiet_khong_cong_khai"] = dem["LiteFinance"].get("chi_tiet_khong_cong_khai", 0) + 1
    # Exness
    dem["Exness"] = {"doc_duoc": 0, "khong_doc": 0}
    if not tt.tai(NK.EXNESS_CT.format(id="110170778")):
        dem["Exness"]["khong_doc"] += 1
    return ra, dem


def ghi_so(dat_ds: list[dict], ngay: str):
    from nhan.so_ket_qua import ghi_ket_qua
    dong = []
    for t in dat_ds:
        dong.append({"id": f"ck_{t['nen_tang']}_{t['id']}_{ngay}".lower(), "he": f"{t['nen_tang']}:{t['id']} {t.get('ten') or ''}".strip(),
                     "symbol": " ".join(t.get("symbol") or [])[:80], "so_nam": round((t.get("tuoi_thang") or 0) / 12, 3),
                     "nguon": "CONG_KHAI", "cagr_pct": t["cagr_pct"], "dd_pct": t["dd_pct"], "so_lenh": t.get("so_lenh"),
                     "tep_goc": t["url"], "ghi_chu": f"{t.get('that_demo')}; tăng trưởng {t.get('tang_truong_pct')}%; " + (t.get("ghi_chu") or "")})
    return ghi_ket_qua(dong) if dong else []


def _o(x, d=2):
    return "CHƯA ĐO ĐƯỢC" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def viet_bao_cao(ds: list[dict], dem: dict, chan: list, luc: str, p: Path = BAO_CAO):
    dat_ds = sorted([t for t in ds if t["trang_thai"] == "DAT"], key=lambda t: -t["diem_xep_hang"])
    L = [f"# Nguồn công khai ĐẠT — lịch sử xác minh công khai",
         "", f"Đo lúc {luc} (giờ Việt Nam, UTC+7). Sinh bởi `python3 -m seeker.cong_khai.chay`.",
         "", f"**Tiêu chí ĐẠT duy nhất:** max DD < {DD_MAX:.0f}% VÀ CAGR > {CAGR_MIN:.0f}%/năm. Không có tiêu chí nào khác.",
         "", "- CAGR = (1 + tăng trưởng)^(12 / tuổi tháng) − 1. MQL5: tăng trưởng (Growth) **bỏ qua nạp/rút**, tuổi = số tuần lịch sử (Weeks).",
         "- DD MQL5 = max(DD tương đối theo số dư, theo vốn).",
         "- Thật/demo MQL5 suy từ tên máy chủ (có 'Demo'/'Contest' → demo).",
         "- **Điểm xếp hạng chỉ để sắp thứ tự** giữa các tín hiệu đã ĐẠT (tuổi 40%, tài khoản thật 25%, DD thấp 20%, CAGR chặn trần 200% 15%). Không phải cổng.",
         "- Tuổi ngắn (< 12 tháng) cho CAGR phóng đại; đây là lịch sử công khai, chưa phải kiểm chứng dữ liệu dài nhiều năm.",
         "- **Thiên lệch sống sót:** danh sách mặc định của MQL5 (`/en/signals/mt5/list`, `/mt4/list`) chỉ hiện tín hiệu thật xếp hạng cao, "
         "nên tỉ lệ ĐẠT trên mẫu này KHÔNG đại diện cho toàn bộ tín hiệu. Tín hiệu đã cháy/ẩn không có trong mẫu.",
         "", "## Số lượng quét", "", "| Nền tảng | Kết quả |", "|---|---|"]
    for k, v in dem.items():
        L.append(f"| {k} | {', '.join(f'{a}={b}' for a, b in v.items())} |")
    tong = {}
    for t in ds: tong.setdefault(t["nen_tang"], {}).setdefault(t["trang_thai"], 0); tong[t["nen_tang"]][t["trang_thai"]] += 1
    L += ["", "Trạng thái: " + "; ".join(f"{k}: {v}" for k, v in tong.items()), ""]
    for k, v in tong.items():
        n = sum(v.values()); co_so = n - v.get("CHUA_DO", 0)
        L.append(f"- Tỉ lệ ĐẠT {k}: {v.get('DAT', 0)}/{co_so} tín hiệu đo được" + (f" = {100 * v.get('DAT', 0) / co_so:.1f}%" if co_so else " (CHƯA ĐO ĐƯỢC)"))
    L += ["",
          f"## Tín hiệu ĐẠT ({len(dat_ds)}), sắp theo điểm xếp hạng", "",
          "| # | Tên | Nền tảng | Link | CAGR %/năm | Max DD % | Tuổi (tháng) | Thật/demo | Tăng trưởng % | Số lệnh | Symbol | Kiểu (từ trong trang) | Lệnh cuối | Điểm xếp hạng |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, t in enumerate(dat_ds, 1):
        L.append(f"| {i} | {(t.get('ten') or '').replace('|', '/')} | {t['nen_tang']} | [{t['id']}]({t['url']}) | {_o(t['cagr_pct'])} | {_o(t['dd_pct'])} | {_o(t['tuoi_thang'])} | {t['that_demo']} | {_o(t['tang_truong_pct'])} | {_o(t.get('so_lenh'))} | {' '.join(t.get('symbol') or [])[:40] or 'CHƯA ĐO ĐƯỢC'} | {', '.join(t.get('kieu') or []) or '—'} | {t.get('cap_nhat_cuoi') or 'CHƯA ĐO ĐƯỢC'} | {t['diem_xep_hang']} |")
    L += ["", "## Phong cách suy từ dữ liệu công khai — 20 tín hiệu ĐẠT đầu bảng", "",
          "Nguồn: bảng Growth năm/tháng và đường Growth nhúng trong trang công khai, thời gian giữ lệnh, tải ký quỹ tối đa, symbol. "
          "Khung thời gian chỉ ghi khi trang có nhắc (M1…W1). Gợi ý phong cách là suy luận, KHÔNG phải tiêu chí.", "",
          "| # | Tên | Growth theo năm % | Tháng âm % | Tháng tệ nhất % | Giữ lệnh | Lệnh/tuần | Tải ký quỹ max % | Symbol | Khung nhắc đến | Gợi ý phong cách |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, t in enumerate(dat_ds[:20], 1):
        dc = t.get("duong_cong") or {}; pc = t.get("phong_cach") or {}
        nam = ", ".join(f"{y}: {v}" for y, v in (dc.get("theo_nam_pct") or {}).items()) or "CHƯA ĐO ĐƯỢC"
        L.append(f"| {i} | [{(t.get('ten') or '').replace('|', '/')}]({t['url']}) | {nam} | {_o(dc.get('thang_am_pct'), 1)} | {_o(dc.get('thang_te_nhat_pct'))} | {t.get('giu_lenh') or 'CHƯA ĐO ĐƯỢC'} | {_o(t.get('lenh_moi_tuan'), 0)} | {_o(t.get('tai_ky_quy_max_pct'))} | {' '.join(t.get('symbol') or [])[:40] or 'CHƯA ĐO ĐƯỢC'} | {', '.join(pc.get('khung_nhac_den') or []) or 'CHƯA ĐO ĐƯỢC'} | {'; '.join(pc.get('goi_y') or []) or '—'} |")
    L += ["", "Đường Growth đầy đủ (lấy mẫu ≤ 40 điểm) của mọi tín hiệu nằm trong `reports/cong_khai/DUONG_CONG_TOP.json` (top 50) và `data/cong_khai/tin_hieu.jsonl`.", ""]
    L += ["", "## Chặn / không đọc được", ""]
    for c in chan[:60]:
        L.append(f"- `{c.get('url')}` — {c.get('tt')} {c.get('http', '')}")
    L += ["", "## Dịch ngược (`nhan/dich_nguoc`)", "",
          "Lịch sử lệnh CSV của MQL5 (`/export/history`) chuyển hướng sang đăng nhập → **không có CSV công khai** cho tín hiệu ĐẠT nào; "
          "chưa đưa được vào dịch ngược từ box. Cách làm tiếp: Anh đăng nhập MQL5 trên máy nhà, tải CSV vào `data/cong_khai/csv/<id>.csv`, rồi "
          "`python -m nhan.dich_nguoc --lich-su data/cong_khai/csv/<id>.csv --ten mql5_<id> --url <link>`.", ""]
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text("\n".join(L), encoding="utf-8")
    return dat_ds


def dua_dich_nguoc(dat_ds: list[dict]) -> list[dict]:
    """Chạy dịch ngược cho tín hiệu ĐẠT có CSV đã tải sẵn trong data/cong_khai/csv/<id>.csv (tải tay khi cần đăng nhập)."""
    ra = []
    for t in dat_ds:
        f = DATA / "csv" / f"{t['id']}.csv"
        if f.exists():
            from nhan.dich_nguoc.__main__ import chay
            try:
                ra.append({"id": t["id"], "ket_qua": "ok", "the": str(chay(str(f), None, t["url"], f"{t['nen_tang']}_{t['id']}"))[:200]})
            except Exception as e:
                ra.append({"id": t["id"], "ket_qua": f"loi: {e}"[:200]})
    return ra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trang", type=int, default=3); ap.add_argument("--gian-cach", type=float, default=3.0)
    ap.add_argument("--khong-ghi-so", action="store_true"); ap.add_argument("--muc-tieu", type=int, default=0)
    a = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    luc = datetime.now().strftime("%Y-%m-%d %H:%M")
    tt = ThuThap(DATA / "cache", gian_cach_s=a.gian_cach, het_han_cache_s=72 * 3600)  # cache 72h: chạy lại sau gián đoạn không tải lại
    ds, dem = quet(tt, a.trang, muc_tieu=a.muc_tieu, log=lambda x: print(x, flush=True))
    with open(DATA / "tin_hieu.jsonl", "w", encoding="utf-8") as o:
        for t in ds: o.write(json.dumps(t, ensure_ascii=False) + "\n")
    chan = [x for x in tt.nhat_ky if x.get("tt") != "ok"]
    dat_ds = viet_bao_cao(ds, dem, chan, luc)
    so = [] if a.khong_ghi_so else ghi_so(dat_ds, datetime.now().strftime("%Y%m%d"))
    dn = dua_dich_nguoc(dat_ds)
    tk = {"luc": luc, "dem": dem, "thu_thap": tt.dem, "so_dat": len(dat_ds), "so_dong_so_moi": len(so), "dich_nguoc": dn,
          "ty_le_dat": {k: round(sum(1 for t in ds if t["nen_tang"] == k and t["trang_thai"] == "DAT") / max(1, sum(1 for t in ds if t["nen_tang"] == k and t["trang_thai"] != "CHUA_DO")), 4) for k in dem}, "top10": [{k: t.get(k) for k in ("ten", "url", "cagr_pct", "dd_pct", "tuoi_thang", "that_demo", "diem_xep_hang")} for t in dat_ds[:10]]}
    THONG_KE.parent.mkdir(parents=True, exist_ok=True)
    (THONG_KE.parent / "DUONG_CONG_TOP.json").write_text(json.dumps([{k: t.get(k) for k in ("ten", "url", "cagr_pct", "dd_pct", "tuoi_thang", "symbol", "giu_lenh", "tai_ky_quy_max_pct", "phong_cach", "duong_cong")} for t in dat_ds[:50]], ensure_ascii=False, indent=1), encoding="utf-8")
    THONG_KE.parent.mkdir(parents=True, exist_ok=True); THONG_KE.write_text(json.dumps(tk, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(tk, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
