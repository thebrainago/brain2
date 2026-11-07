# -*- coding: utf-8 -*-
"""Kho 83 tín hiệu đã lọc chặt (bản chụp reports/MQL5_LOC_CHAT.md, 03/11/2026).

Không tải mạng, không cần mật khẩu. CSV chỉ được nhận khi là tệp xuất hợp lệ
kèm đúng URL tín hiệu. Replay CSV không phải hệ giao dịch của mình.
Thiếu tệp = thieu_du_lieu, không phải no_data (không có lệnh).

    python -m seeker.cong_khai.kho_83
    python -m seeker.cong_khai.kho_83 --nhap seeker/fixtures/mql5_history.csv --id 2394758 --url https://www.mql5.com/en/signals/2394758
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from seeker.khop_trung import gan_nghi

GOC = Path(__file__).resolve().parents[2]
BAO_CAO = GOC / "reports" / "MQL5_LOC_CHAT.md"
RA_JSON = GOC / "reports" / "seeker_nguon" / "KHO_83.json"
RA_MD = GOC / "reports" / "seeker_nguon" / "KHO_83.md"
CSV_DIR = GOC / "data" / "cong_khai" / "csv"

_HANG = re.compile(
    r"^\| (\d+) \| \[(\d+)\]\((https://www\.mql5\.com/en/signals/\d+)\) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \|",
    re.M)
_USD = ("USD", "XAU", "GOLD", "US500", "NAS", "BTC", "ETH", "DOW", "UKOIL", "BRENT", "COFFEE", "US30", "GER40", "SPX")


def _so(s: str):
    t = (s or "").strip().replace(" ", "")
    if not t or "ĐO" in t:
        return None
    t = t.replace(".", "").replace(",", ".") if t.count(",") == 1 and t.count(".") > 1 else t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def _lien_usd(ma: str) -> bool:
    u = ma.upper()
    return any(k in u for k in _USD)


def nhom_uu_tien(ma: list[str]) -> int:
    """0 = toàn bộ mã không dính USD (ưu tiên), 1 = lẫn, 2 = toàn USD. Không bỏ nhóm nào."""
    if not ma:
        return 2
    co = [_lien_usd(m) for m in ma]
    if not any(co):
        return 0
    if all(co):
        return 2
    return 1


def doc_bang(text: str) -> list[dict]:
    """Chỉ bảng xếp hạng trước mục EA Market."""
    than = text.split("## EA trên", 1)[0]
    ra = []
    for m in _HANG.finditer(than):
        ma = [x for x in m.group(5).split() if x]
        ra.append({
            "hang": int(m.group(1)), "id": m.group(2), "url": m.group(3),
            "ten": m.group(4).strip(), "ma": ma, "tuoi_thang": _so(m.group(6)),
            "cagr_pct": _so(m.group(7)), "dd_pct": _so(m.group(8)),
            "sut_growth_pct": _so(m.group(9)), "luoi_trong_bao_cao": m.group(10).strip(),
            "may_chu": m.group(12).strip(),
            "cap": "man_hinh_lich_su_cong_khai",
            "giao_dich_duoc": False,
            "ly_do_cap": "Màn hình lịch sử công khai của người khác (bản lọc 03/11). Chưa giải mã điểm vào, chưa OOS. Không phải ĐẠT của hệ mình.",
            "nhom_uu_tien": nhom_uu_tien(ma),
        })
    return ra


def _csv_san(duong: Path) -> dict:
    raw = duong.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8", "replace")
    dau = text.lstrip("\ufeff")
    if "<html" in dau[:500].lower() or "please log in" in dau[:2000].lower():
        return {"loai": "auth", "ly_do": "tệp là HTML đăng nhập, không phải CSV lệnh", "so_dong": None}
    dong = [x for x in dau.splitlines() if x.strip()]
    if not dong:
        return {"loai": "parse", "ly_do": "tệp rỗng", "so_dong": None}
    head = dong[0].lower()
    if "time" not in head or "symbol" not in head:
        return {"loai": "parse", "ly_do": "thiếu cột Time và Symbol — không nhận", "so_dong": None}
    if len(dong) <= 1:
        return {"loai": "no_data", "ly_do": "CSV hợp lệ nhưng không có dòng lệnh", "so_dong": 0}
    return {"loai": "ok", "ly_do": "CSV có cột Time/Symbol", "so_dong": len(dong) - 1,
            "dau": dong[1][:40], "cuoi": dong[-1][:40], "sha256": hashlib.sha256(raw).hexdigest()}


def trang_thai_csv(sid: str, thu_muc: Path) -> dict:
    for ten in (f"{sid}.history.csv", f"{sid}.csv"):
        f = thu_muc / ten
        if f.exists():
            k = _csv_san(f)
            k.update(tep=str(f), co_tep=True)
            return k
    return {"loai": "thieu_du_lieu", "ly_do": "chưa có CSV xuất tay. Endpoint history của MQL5 đòi đăng nhập; phiên này không tải và không coi đó là 0 lệnh.",
            "so_dong": None, "co_tep": False}


def kiem_ke(bao_cao: Path = BAO_CAO, thu_muc_csv: Path = CSV_DIR, cu: dict | None = None) -> dict:
    ds = doc_bang(bao_cao.read_text(encoding="utf-8"))
    if len(ds) != 83 and bao_cao == BAO_CAO:
        pass
    da = {str(x.get("id")): x for x in (cu or {}).get("tin_hieu") or []}
    for x in ds:
        st = trang_thai_csv(x["id"], thu_muc_csv)
        truoc = da.get(x["id"]) or {}
        if st["loai"] == "thieu_du_lieu" and truoc.get("csv_sha256") and not st.get("co_tep"):
            st = {"loai": "thieu_du_lieu", "ly_do": st["ly_do"], "so_dong": None, "co_tep": False,
                  "csv_sha256_cu": truoc.get("csv_sha256")}
        x["csv"] = {k: st.get(k) for k in ("loai", "ly_do", "so_dong", "co_tep", "sha256", "tep")}
        if st.get("loai") == "ok":
            x["cap"] = "replay_csv"
            x["giao_dich_duoc"] = False
            x["ly_do_cap"] = "Đã nhập CSV xuất hợp lệ. Replay lịch sử người khác không phải chiến lược giao dịch và chưa phải ĐẠT."
        x["csv_sha256"] = st.get("sha256")
    gan_nghi(ds)
    uutien = sorted(ds, key=lambda r: (r["nhom_uu_tien"], r["hang"]))
    dem_csv = {}
    for x in ds:
        dem_csv[x["csv"]["loai"]] = dem_csv.get(x["csv"]["loai"], 0) + 1
    return {
        "luc": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nguon_bang": str(bao_cao.relative_to(GOC)) if str(bao_cao).startswith(str(GOC)) else str(bao_cao),
        "nguon_luc": "2026-11-03",
        "so": len(ds),
        "giao_dich_duoc": 0,
        "quy_tac_dung_duoc": 0,
        "ghi_chu": "83 là màn hình lịch sử công khai sau lọc chặt cũ, không phải 83 hệ ĐẠT của mình. Ưu tiên cặp không USD nhưng giữ cặp USD. Trùng tên chỉ là nghi.",
        "csv": dem_csv,
        "uu_tien": {"khong_usd": sum(x["nhom_uu_tien"] == 0 for x in ds),
                    "lan": sum(x["nhom_uu_tien"] == 1 for x in ds),
                    "co_usd": sum(x["nhom_uu_tien"] == 2 for x in ds)},
        "thu_tu_uu_tien": [x["id"] for x in uutien],
        "tin_hieu": ds,
    }


def ghi(kho: dict, json_path: Path = RA_JSON, md_path: Path = RA_MD) -> dict:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(kho, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Kho 83 tín hiệu — kiểm kê, không phải ĐẠT", "",
         f"Sinh {kho['luc']} từ `{kho['nguon_bang']}` (bản lọc {kho['nguon_luc']}).",
         "", kho["ghi_chu"], "",
         f"- Số tín hiệu: **{kho['so']}**",
         f"- Quy tắc dùng được (điểm vào đã giải mã + OOS): **{kho['quy_tac_dung_duoc']}**",
         f"- Được phép gọi là giao dịch được: **{kho['giao_dich_duoc']}**",
         f"- CSV: {kho['csv']}",
         f"- Ưu tiên mã: không USD {kho['uu_tien']['khong_usd']}, lẫn {kho['uu_tien']['lan']}, có USD {kho['uu_tien']['co_usd']} (giữ cả ba)",
         "", "| Ưu tiên | Hạng cũ | ID | Mã | CSV | Cấp | Nghi trùng |", "|---|---|---|---|---|---|---|"]
    by = {x["id"]: x for x in kho["tin_hieu"]}
    for sid in kho["thu_tu_uu_tien"]:
        x = by[sid]
        nghi = ",".join(str(n["id"]) for n in x.get("trung_nghi_ngo") or []) or "—"
        L.append("| %d | %d | [%s](%s) | %s | %s | %s | %s |" % (
            x["nhom_uu_tien"], x["hang"], x["id"], x["url"], " ".join(x["ma"]),
            x["csv"]["loai"], x["cap"], nghi))
    md_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return kho


def nhap(duong: Path, sid: str, url: str, thu_muc_csv: Path = CSV_DIR, bao_cao: Path = BAO_CAO) -> dict:
    sid = str(sid)
    url = url.rstrip("/")
    dung = f"https://www.mql5.com/en/signals/{sid}"
    if url != dung:
        raise ValueError(f"url phải là {dung} — không nhận tệp không rõ nguồn")
    ds = doc_bang(bao_cao.read_text(encoding="utf-8"))
    if sid not in {x["id"] for x in ds}:
        raise ValueError(f"id {sid} không nằm trong 83 tín hiệu của bản lọc")
    k = _csv_san(Path(duong))
    if k["loai"] != "ok":
        raise ValueError(k["ly_do"])
    thu_muc_csv.mkdir(parents=True, exist_ok=True)
    dich = thu_muc_csv / f"{sid}.history.csv"
    if Path(duong).resolve() != dich.resolve():
        shutil.copyfile(duong, dich)
    meta = {"id": sid, "url": dung, "sha256": k["sha256"], "so_dong": k["so_dong"],
            "luc_nhap": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cap": "replay_csv", "giao_dich_duoc": False,
            "ly_do": "CSV xuất hợp lệ gắn link tín hiệu. Replay không phải hệ của mình; chưa giải mã điểm vào, chưa OOS."}
    (thu_muc_csv / f"{sid}.nguon.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhap")
    ap.add_argument("--id")
    ap.add_argument("--url")
    a = ap.parse_args(argv)
    if a.nhap:
        if not a.id or not a.url:
            raise SystemExit("nhập CSV cần --id và --url đúng trang tín hiệu")
        print(json.dumps(nhap(Path(a.nhap), a.id, a.url), ensure_ascii=False))
    cu = None
    if RA_JSON.exists():
        try:
            cu = json.loads(RA_JSON.read_text(encoding="utf-8"))
        except ValueError:
            cu = None
    kho = ghi(kiem_ke(cu=cu))
    print(json.dumps({k: kho[k] for k in ("so", "quy_tac_dung_duoc", "giao_dich_duoc", "csv", "uu_tien")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
