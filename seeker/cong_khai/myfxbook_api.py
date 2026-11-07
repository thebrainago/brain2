# -*- coding: utf-8 -*-
"""Hợp đồng API Myfxbook theo trang tài liệu chính thức, không gọi mạng.

Nguồn tài liệu (đọc một lần, không probe lại): https://www.myfxbook.com/api
Trang đó ghi: API để truy cập dữ liệu tài khoản của bạn; "The API allows access
to personal information only." get-history giới hạn 50 giao dịch gần nhất.
Không có phương thức bảng xếp hạng /systems. Không suy ra rằng session của mình
lấy được lịch sử chi tiết của trader khác.

HTML /systems đã Cloudflare 403 ngày 2026-11-03. `host_bi_chan()` = True.
Không VPN, không API ẩn, không đăng nhập từ mã này.

    python -m seeker.cong_khai.myfxbook_api --nhap tep.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
NGHIEN_CUU = GOC / "hang_doi" / "nghien_cuu"
TAI_LIEU = "https://www.myfxbook.com/api"
PHAM_VI = {
    "get-my-accounts": "tai_khoan_cua_minh",
    "get-watched-accounts": "tom_tat_tai_khoan_dang_theo_doi",
    "get-history": "lich_su_toi_da_50_neu_id_thuoc_phien",
    "get-community-outlook": "tam_ly_cong_dong_khong_phai_bang_xep_hang",
}


def host_bi_chan() -> bool:
    """Không gọi myfxbook.com. Bản 2026-11-03: /systems HTTP 403 Cloudflare."""
    return True


def trang_thai_ket_noi() -> dict:
    return {
        "ket_noi": False,
        "loai": "challenge",
        "http": 403,
        "host": "www.myfxbook.com",
        "ly_do": "Cloudflare 403 trên /systems (2026-11-03), kể cả robots.txt. Dừng, không gọi lại.",
        "tai_lieu_api": TAI_LIEU,
        "api_pham_vi_tai_lieu": "personal information only",
        "khong_phai_lich_su_ben_thu_ba": True,
    }


def _so(x):
    if x is None or x == "":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def phan_loai_tep(obj: dict) -> str:
    if not isinstance(obj, dict):
        return "parse"
    if obj.get("error") is True:
        msg = str(obj.get("message") or "").lower()
        if "session" in msg or "password" in msg or "email" in msg or "login" in msg:
            return "auth"
        return "auth" if "invalid" in msg else "parse"
    if "accounts" in obj and obj.get("accounts") and isinstance(obj["accounts"], list):
        mau = obj["accounts"][0] if obj["accounts"] else {}
        if isinstance(mau, dict) and "id" in mau:
            return "get-my-accounts"
        return "get-watched-accounts"
    if "history" in obj:
        return "get-history"
    if "communityOutlook" in obj or "symbols" in obj and "outlook" in json.dumps(obj).lower():
        return "get-community-outlook"
    return "parse"


def _khai_bao(gain, dd) -> dict:
    return {
        "gain_pct_khai_bao": _so(gain),
        "dd_pct_khai_bao": _so(dd),
        "la_khai_bao": True,
        "da_xac_minh": False,
        "dat": False,
        "ly_do_dat": "số trên Myfxbook là khai báo của trang/API, chưa phải ĐẠT của hệ mình",
    }


def doc_phan_hoi(obj: dict) -> dict:
    """Đọc JSON đã lưu. Không mạng. Số lãi/DD là khai báo, không phải ĐẠT."""
    loai = phan_loai_tep(obj)
    if loai == "auth":
        return {"loai": "auth", "ket_noi": False, "ly_do": str(obj.get("message") or "API từ chối phiên"),
                "pham_vi": None, "ho_so": [], "so_lenh": None}
    if loai == "parse":
        return {"loai": "parse", "ket_noi": False, "ly_do": "JSON không khớp get-my-accounts, watched, history hay outlook",
                "pham_vi": None, "ho_so": [], "so_lenh": None}
    pham = PHAM_VI[loai]
    if loai == "get-my-accounts":
        ho = []
        for a in obj.get("accounts") or []:
            if not isinstance(a, dict):
                continue
            ho.append({
                "id": str(a.get("id")),
                "ten": a.get("name"),
                "demo": a.get("demo"),
                "tien_te": a.get("currency"),
                **_khai_bao(a.get("gain"), a.get("drawdown")),
                "co_lich_su_lenh": False,
                "gioi_han": "get-my-accounts chỉ là số tổng của tài khoản mình, không phải lịch sử lệnh",
            })
        return {"loai": "ok", "phuong_thuc": loai, "pham_vi": pham, "ket_noi": False,
                "ho_so": ho, "so_lenh": None,
                "ly_do": "đây là tài khoản của phiên đăng nhập, không phải hồ sơ trader bên thứ ba"}
    if loai == "get-watched-accounts":
        ho = []
        for a in obj.get("accounts") or []:
            if not isinstance(a, dict):
                continue
            ho.append({
                "id": None if a.get("id") is None else str(a.get("id")),
                "ten": a.get("name"),
                "demo": a.get("demo"),
                **_khai_bao(a.get("gain"), a.get("drawdown")),
                "co_lich_su_lenh": False,
                "gioi_han": "mẫu tài liệu watched chỉ có gain/drawdown/demo/change, không có danh sách lệnh",
            })
        return {"loai": "ok", "phuong_thuc": loai, "pham_vi": pham, "ket_noi": False,
                "ho_so": ho, "so_lenh": None,
                "ly_do": "tóm tắt tài khoản đang theo dõi. Không suy ra lịch sử chi tiết của họ."}
    if loai == "get-history":
        rows = [x for x in (obj.get("history") or []) if isinstance(x, dict)]
        return {"loai": "ok", "phuong_thuc": loai, "pham_vi": pham, "ket_noi": False,
                "ho_so": [], "lenh": rows, "so_lenh": len(rows),
                "day_du": False,
                "ly_do": "tài liệu: history tối đa 50 giao dịch gần nhất của account id trong phiên. Không ghi là lịch sử trader khác.",
                **_khai_bao(None, None)}
    return {"loai": "ok", "phuong_thuc": loai, "pham_vi": pham, "ket_noi": False,
            "ho_so": [], "so_lenh": None,
            "ly_do": "community outlook là tâm lý thị trường, không phải bảng xếp hạng hệ"}


def viec_nghien_cuu(doc: dict, sha: str, tep: str) -> dict | None:
    """Việc nghiên cứu, không phải việc biên dịch MT5. None nếu không có hồ sơ/lệnh."""
    if doc.get("loai") != "ok":
        return None
    if doc.get("phuong_thuc") == "get-community-outlook":
        return None
    khoa = sha[:12]
    if doc.get("phuong_thuc") == "get-history":
        return {
            "id": "nc_mfb_h_" + khoa,
            "loai": "nghien_cuu_track_record",
            "khong_phai_viec_mt5": True,
            "nguon": "myfxbook",
            "pham_vi": doc["pham_vi"],
            "url_tai_lieu": TAI_LIEU,
            "tep": tep,
            "sha256": sha,
            "so_lenh": doc["so_lenh"],
            "day_du": False,
            "chien_luoc_giai_ma": False,
            "dat": False,
            "ghi_chu": doc["ly_do"],
        }
    if not doc.get("ho_so"):
        return None
    a = doc["ho_so"][0]
    return {
        "id": "nc_mfb_" + khoa,
        "loai": "nghien_cuu_track_record",
        "khong_phai_viec_mt5": True,
        "nguon": "myfxbook",
        "pham_vi": doc["pham_vi"],
        "url_tai_lieu": TAI_LIEU,
        "tep": tep,
        "sha256": sha,
        "ten": a.get("ten"),
        "gain_pct_khai_bao": a.get("gain_pct_khai_bao"),
        "dd_pct_khai_bao": a.get("dd_pct_khai_bao"),
        "la_khai_bao": True,
        "da_xac_minh": False,
        "so_lenh": None,
        "chien_luoc_giai_ma": False,
        "dat": False,
        "ghi_chu": doc["ly_do"],
    }


def nhap(duong: Path, thu_muc: Path = NGHIEN_CUU) -> dict:
    raw = Path(duong).read_bytes()
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return {"loai": "parse", "ly_do": str(e)[:160], "viec": None}
    if isinstance(obj, dict) and "Just a moment" in json.dumps(obj)[:500]:
        return {"loai": "challenge", "ly_do": "tệp là trang chặn, không phải JSON API", "viec": None}
    doc = doc_phan_hoi(obj)
    sha = hashlib.sha256(raw).hexdigest()
    viec = viec_nghien_cuu(doc, sha, str(duong))
    if viec is None:
        return {**doc, "viec": None, "quyet_dinh": "tu_choi"}
    thu_muc.mkdir(parents=True, exist_ok=True)
    da = list(thu_muc.glob(viec["id"] + ".json"))
    for p in thu_muc.glob("nc_mfb_*.json"):
        try:
            cu = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if cu.get("sha256") == sha:
            return {**doc, "viec": cu, "quyet_dinh": "trung", "ly_do": "cùng sha256 đã nhập"}
    (thu_muc / (viec["id"] + ".json")).write_text(json.dumps(viec, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**doc, "viec": viec, "quyet_dinh": "nhan", "da_co_file": bool(da)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhap")
    ap.add_argument("--trang-thai", action="store_true")
    a = ap.parse_args(argv)
    if a.trang_thai or not a.nhap:
        print(json.dumps(trang_thai_ket_noi(), ensure_ascii=False, indent=1))
        if not a.nhap:
            return 0
    r = nhap(Path(a.nhap))
    print(json.dumps({"quyet_dinh": r.get("quyet_dinh"), "loai": r.get("loai"),
                      "pham_vi": r.get("pham_vi"), "dat": False,
                      "id": None if not r.get("viec") else r["viec"].get("id")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
