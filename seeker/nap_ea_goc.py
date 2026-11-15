# -*- coding: utf-8 -*-
"""Đưa EA gốc nguyên vẹn vào hàng đợi biên dịch/test demo — không chờ dịch Python.

Worker (`may_nha/tho_mt5.tai_ma_nguon`) chỉ tải MỘT file qua `url_ma_nguon` và
biên dịch `.mq5`. Vì vậy việc mới chỉ nhận EA một file, include thuộc thư viện
chuẩn MT5. Include riêng nằm trong manifest và bị từ chối, không xếp hàng.

OnTick/start + lời gọi lệnh là heuristic, không phải chứng minh. Không có
MetaEditor trên máy này thì `bien_dich` = CHUA_BIEN_DICH. Không chạy tester,
không live. Trần cứng 5 việc mới / lần.

    python -m seeker.nap_ea_goc --toi-da 3
    python -m seeker.nap_ea_goc --toi-da 2 --mau-cong-khai
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from nhan.cau_kho_ma import tep_include_ngoai
from seeker.nguon_file.quet import tham_so_lot

GOC = Path(__file__).resolve().parents[1]
KHO = GOC / "data" / "cau_kho"
HANG = GOC / "hang_doi"
BAO = GOC / "reports" / "seeker_nguon" / "NAP_EA_GOC.json"
TRAN_VIEC = 5
TRAN_XEM = 40
_LENH = re.compile(r"\bOrderSend(?:Async)?\s*\(|\.\s*Buy\s*\(|\.\s*Sell\s*\(|\bPositionOpen\s*\(")
_VAO = re.compile(r"\bOnTick\s*\(|\bint\s+start\s*\(")
_CAP = ("AUDCAD", "AUDNZD", "NZDCAD", "EURGBP", "EURCHF", "GBPCAD", "GBPNZD",
        "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "NZDUSD", "AUDUSD")


def doc_ma(path: Path) -> str:
    b = path.read_bytes()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16", "ignore")
    return b.decode("utf-8", "replace")


def heuristic(src: str) -> dict:
    return {
        "co_ontick_hoac_start": bool(_VAO.search(src or "")),
        "co_loi_goi_lenh": bool(_LENH.search(src or "")),
        "la_chung_minh_ea": False,
        "ly_do": "OnTick/start và lời gọi lệnh chỉ là heuristic, không chứng minh EA biên dịch hay có lãi",
    }


def url_tai(meta: dict, ten_goc: str) -> str | None:
    san = str(meta.get("url_tai_san") or "")
    if san.startswith("http") and ten_goc.lower().endswith(".mq5"):
        return san.split("?")[0]
    u = str(meta.get("url") or "")
    if "raw.githubusercontent.com/" in u or "/code/download/" in u:
        return u.split("?")[0]
    m = re.search(r"github\.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)$", u)
    if m and ten_goc.lower().endswith(".mq5"):
        return "https://raw.githubusercontent.com/%s/%s/%s" % m.groups()
    m = re.search(r"mql5\.com/(?:[a-z]{2}/)?code/(\d+)(?:/|$)", u)
    if m and ten_goc.lower().endswith(".mq5"):
        return "https://www.mql5.com/en/code/download/%s/%s" % (m.group(1), ten_goc)
    return None


def ma_thu(src: str) -> tuple[str, str]:
    thay = [c for c in _CAP if re.search(r"\b%s\b" % c, src)]
    khong_usd = [c for c in thay if "USD" not in c]
    chon = (khong_usd or thay)
    if len(chon) == 1:
        return chon[0] + "micro", "một cặp viết trong mã — gán để tester demo, chưa phải bằng chứng cặp tác giả"
    if chon:
        return chon[0] + "micro", "nhiều cặp trong mã; lấy cặp đầu (ưu tiên không USD) để thử demo"
    return "AUDCADmicro", "mã không khóa cặp; gán AUDCADmicro cho một lần tester demo"


def khoa_da_co(hang: Path) -> tuple[set, set, set]:
    url, sha, ids = set(), set(), set()
    if not hang.exists():
        return url, sha, ids
    for p in hang.glob("*/*.json"):
        try:
            v = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ids.add(str(v.get("id") or p.stem))
        for k in ("url_ma_nguon", "nguon", "url"):
            if v.get(k):
                url.add(str(v[k]).split("?")[0])
        if v.get("noi_dung_sha256"):
            sha.add(v["noi_dung_sha256"])
    return url, sha, ids


def xet_file(path: Path, meta: dict, url_co: set, sha_co: set) -> dict:
    src = doc_ma(path)
    ten_goc = path.name
    for t in meta.get("tep") or []:
        if Path(str(t)).name == path.name or str(t).endswith(path.name):
            ten_goc = Path(str(t)).name
            break
    sha = hashlib.sha256(src.encode("utf-8", "replace")).hexdigest()
    h = heuristic(src)
    ngoai = tep_include_ngoai(src)
    ut = url_tai(meta, ten_goc)
    ban = {
        "ten": path.name, "url_trang": meta.get("url") or "", "url_tai": ut,
        "sha256": sha, "heuristic": h, "include_ngoai": ngoai,
        "dich_python": "khong_yeu_cau", "bien_dich": "CHUA_BIEN_DICH",
        "nguyen_ven_mot_file": not ngoai and path.suffix.lower() == ".mq5",
    }
    if path.suffix.lower() != ".mq5":
        return {**ban, "quyet_dinh": "tu_choi", "ly_do": "worker chỉ lưu và biên dịch .mq5"}
    if not (h["co_ontick_hoac_start"] and h["co_loi_goi_lenh"]):
        return {**ban, "quyet_dinh": "tu_choi", "ly_do": "heuristic không thấy cả điểm vào hàm và lời gọi lệnh"}
    if ngoai:
        return {**ban, "quyet_dinh": "tu_choi",
                "ly_do": "có include ngoài thư viện chuẩn; worker chỉ tải một file nên chưa xếp hàng"}
    if not ut:
        return {**ban, "quyet_dinh": "tu_choi", "ly_do": "không dựng được URL tải thẳng file .mq5"}
    if ut in url_co or (meta.get("url") or "") in url_co or sha in sha_co:
        return {**ban, "quyet_dinh": "trung", "ly_do": "trùng URL hoặc sha256 với việc đã có trong hang_doi"}
    lot = tham_so_lot(src)
    ma, ly_ma = ma_thu(src)
    vid = "na_" + sha[:12]
    spec = {
        "id": vid, "loai": "mt5_backtest", "lan": "co_ma_nguon", "uu_tien": 25,
        "che_do": "ea_goc", "ea_file": "NA_" + sha[:12], "url_ma_nguon": ut,
        "ma": ma, "tf": "H1", "tu": "2016.01.01", "den": "2026.10.01", "model": 4,
        "von": 10000, "tien": "USD", "don_bay": 500,
        "he_so_lot": [1.0], "uoc_phut": 30, "nguon": meta.get("url") or ut,
        "noi_dung_sha256": sha, "phu_thuoc": [], "include_ngoai": [],
        "kieu_ea": "heuristic_ontick_lenh", "kieu_ea_la_chung": False,
        "dich_python": "khong_yeu_cau", "bien_dich": "CHUA_BIEN_DICH",
        "che_do_tai_khoan": "demo_only",
        "ghi_chu": "Ứng viên biên dịch demo, một hệ số lot. %s. %s" % (h["ly_do"], ly_ma),
    }
    if lot:
        spec["tham_so_lot"] = lot[0]
        spec["ts"] = {lot[0]: lot[1]}
    return {**ban, "quyet_dinh": "nhan", "ly_do": "một file .mq5, include chỉ thư viện chuẩn, chưa trùng",
            "spec": spec, "ma_ly_do": ly_ma}


def quet_kho(goc: Path, hang: Path, toi_da: int, tran_xem: int = TRAN_XEM) -> dict:
    if not goc.exists():
        return {"kho": "khong_co", "duong": str(goc),
                "ly_do": "không thấy kho local; không bịa số gói; không tạo việc",
                "da_xem": 0, "nhan": [], "tu_choi": [], "trung": []}
    url_co, sha_co, _ = khoa_da_co(hang)
    nhan, tu_choi, trung = [], [], []
    xem = 0
    files = []
    for p in sorted(goc.rglob("*.mq5")):
        if p.is_file():
            files.append(p)
            if len(files) >= tran_xem:
                break
    for p in files:
        xem += 1
        meta = {}
        gj = p.parent / "GOI.json"
        if gj.is_file():
            try:
                meta = json.loads(gj.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                meta = {}
        kq = xet_file(p, meta, url_co, sha_co)
        if kq["quyet_dinh"] == "nhan" and len(nhan) < toi_da:
            nhan.append(kq)
            url_co.add(kq["url_tai"])
            sha_co.add(kq["sha256"])
        elif kq["quyet_dinh"] == "nhan":
            kq = {**kq, "quyet_dinh": "tu_choi", "ly_do": "đã đủ trần việc mới"}
            tu_choi.append(kq)
        elif kq["quyet_dinh"] == "trung":
            trung.append(kq)
        else:
            tu_choi.append(kq)
    return {"kho": "co", "duong": str(goc), "da_xem": xem, "tran_xem": tran_xem,
            "nhan": nhan, "tu_choi": tu_choi, "trung": trung}


def ghi_viec(specs: list[dict], hang: Path) -> list[str]:
    from may_nha.hang_doi_git import kiem_spec
    d = hang / "can_test"
    d.mkdir(parents=True, exist_ok=True)
    ids = {p.stem for p in hang.glob("*/*.json")}
    ra = []
    so = hang / "so_cai.jsonl"
    for v in specs:
        loi = kiem_spec(v)
        if loi:
            raise ValueError("%s: %s" % (v.get("id"), loi))
        if v["id"] in ids:
            continue
        (d / (v["id"] + ".json")).write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
        with so.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"may": "box", "su_kien": "them", "id": v["id"], "loai": v["loai"],
                                "bien_dich": "CHUA_BIEN_DICH"}, ensure_ascii=False) + "\n")
        ids.add(v["id"])
        ra.append(v["id"])
    return ra


def _rut(kq: dict) -> dict:
    return {k: kq.get(k) for k in ("ten", "url_trang", "url_tai", "sha256", "quyet_dinh", "ly_do",
                                   "include_ngoai", "dich_python", "bien_dich", "nguyen_ven_mot_file")}


def bao_cao(q: dict, viec_id: list[str]) -> dict:
    return {
        "kho": q.get("kho"), "duong": q.get("duong"), "ly_do_kho": q.get("ly_do"),
        "da_xem": q.get("da_xem", 0), "tran_xem": q.get("tran_xem"),
        "viec_moi": viec_id,
        "nhan": [_rut(x) for x in q.get("nhan") or []],
        "tu_choi": [_rut(x) for x in q.get("tu_choi") or []],
        "trung": [_rut(x) for x in q.get("trung") or []],
        "bien_dich": "CHUA_BIEN_DICH",
        "nguon_khac": q.get("nguon_khac") or [],
        "ghi_chu": "Không chạy MT5. Heuristic không phải chứng minh. Dịch Python không phải cổng. Kho local vắng thì không bịa số gói.",
    }


def mau_cong_khai(cache: Path, toi_da_viec: int, hang: Path) -> dict:
    """Tối đa 2 EA công khai: một file GitHub .mq5 và một file Code Base. Không quét danh sách."""
    from seeker.nhip_tai import NhipTai
    nip = NhipTai(cache, gian_cach=4.0)
    url_co, sha_co, _ = khoa_da_co(hang)
    nhan, tu_choi = [], []
    # GitHub: một repo đã biết, không search.
    api = "https://api.github.com/repos/EarnForex/News-Trader/contents/"
    k = nip.lay(api)
    if k.get("loai") != "ok":
        tu_choi.append({"ten": "EarnForex/News-Trader", "url_trang": api, "quyet_dinh": "tu_choi",
                        "ly_do": k.get("ly_do"), "loai_mang": k.get("loai")})
    else:
        try:
            items = json.loads(k.get("text") or "[]")
        except json.JSONDecodeError:
            items = []
            tu_choi.append({"ten": "EarnForex/News-Trader", "quyet_dinh": "tu_choi", "ly_do": "JSON contents không đọc được"})
        mq = [x for x in items if isinstance(x, dict) and str(x.get("name", "")).lower().endswith(".mq5")
              and x.get("download_url")]
        if not mq and k.get("loai") == "ok":
            dirs = [x for x in items if isinstance(x, dict) and x.get("type") == "dir" and x.get("url")]
            dirs.sort(key=lambda x: (0 if re.search(r"mql|expert|ea", str(x.get("name")), re.I) else 1, str(x.get("name"))))
            if dirs:
                k2 = nip.lay(dirs[0]["url"])
                try:
                    sub = json.loads(k2.get("text") or "[]") if k2.get("loai") == "ok" else []
                except json.JSONDecodeError:
                    sub = []
                mq = [x for x in sub if isinstance(x, dict) and str(x.get("name", "")).lower().endswith(".mq5")
                      and x.get("download_url")]
            if not mq:
                tu_choi.append({"ten": "EarnForex/News-Trader", "url_trang": "https://github.com/EarnForex/News-Trader",
                                "quyet_dinh": "tu_choi", "ly_do": "không thấy .mq5 ở gốc hoặc thư mục con đầu tiên"})
        for x in mq[:1]:
            raw = nip.lay(x["download_url"])
            if raw.get("loai") != "ok" or "<html" in (raw.get("text") or "")[:200].lower():
                tu_choi.append({"ten": x["name"], "url_tai": x["download_url"], "quyet_dinh": "tu_choi",
                                "ly_do": raw.get("ly_do") or "không phải mã nguồn"})
                continue
            p = cache / x["name"]
            p.write_text(raw["text"], encoding="utf-8")
            meta = {"url": "https://github.com/EarnForex/News-Trader/blob/main/" + x["name"],
                    "url_tai_san": x["download_url"], "tep": [x["name"]]}
            kq = xet_file(p, meta, url_co, sha_co)
            (nhan if kq["quyet_dinh"] == "nhan" else tu_choi).append(kq)
    if len(nhan) < toi_da_viec:
        url = "https://www.mql5.com/en/code/download/77653/EMA_Cross_Demo_EA.mq5"
        if url not in url_co:
            r = nip.lay(url)
            than = r.get("text") or ""
            if r.get("loai") != "ok" or "<html" in than[:300].lower() or "OnTick" not in than:
                tu_choi.append({"ten": "EMA_Cross_Demo_EA.mq5", "url_trang": "https://www.mql5.com/en/code/77653",
                                "url_tai": url, "quyet_dinh": "tu_choi", "ly_do": r.get("ly_do") or "không phải .mq5",
                                "loai_mang": r.get("loai")})
            else:
                p = cache / "EMA_Cross_Demo_EA.mq5"
                p.write_text(than, encoding="utf-8")
                kq = xet_file(p, {"url": "https://www.mql5.com/en/code/77653", "url_tai_san": url,
                                 "tep": ["EMA_Cross_Demo_EA.mq5"]}, url_co, sha_co)
                (nhan if kq["quyet_dinh"] == "nhan" else tu_choi).append(kq)
        else:
            tu_choi.append({"ten": "EMA_Cross_Demo_EA.mq5", "url_tai": url, "quyet_dinh": "trung",
                            "ly_do": "URL đã có trong hang_doi"})
    khac = []
    # Một trang TradingView và một trang LiteFinance. Không phải .mq5 thì không xếp việc tester.
    for ten, url in (
        ("tradingview", "https://www.tradingview.com/script/LkgKT3TG-Displaced-Donchian-Decycler-Trend-Breakout-Strategy-with-MFI/"),
        ("litefinance", "https://my.litefinance.org/en/traders"),
    ):
        r = nip.lay(url)
        muc = {"ten": ten, "url": url, "loai": r.get("loai"), "http": r.get("http"),
               "ly_do": (r.get("ly_do") or "")[:400], "quyet_dinh": "tu_choi"}
        if r.get("loai") == "ok":
            from seeker.nguon_file.phan_tich import boc_pine
            from seeker.cong_khai.nen_tang_khac import litefinance_danh_sach_ro
            if ten == "tradingview":
                pine = boc_pine(r.get("text") or "")
                muc["pine"] = pine.get("loai")
                muc["ly_do"] = "Pine %s. Không xếp hàng MT5 vì worker chỉ biên dịch .mq5. %s" % (pine.get("loai"), pine.get("ly_do"))
            else:
                ds = litefinance_danh_sach_ro(r.get("text") or "")
                muc["loai_trang"] = ds.get("loai")
                muc["so_ho_so"] = ds.get("so_ho_so")
                muc["ly_do"] = "LiteFinance không có file EA. %s" % ds.get("ly_do")
        khac.append(muc)
        if r.get("loai") == "challenge":
            continue
    return {"kho": "mau_cong_khai", "duong": str(cache), "da_xem": 2, "nhan": nhan[:toi_da_viec],
            "tu_choi": [x for x in tu_choi if x.get("quyet_dinh") != "trung"],
            "trung": [x for x in tu_choi if x.get("quyet_dinh") == "trung"],
            "nguon_khac": khac}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kho", default=str(KHO))
    ap.add_argument("--hang", default=str(HANG))
    ap.add_argument("--toi-da", type=int, default=3)
    ap.add_argument("--mau-cong-khai", action="store_true")
    ap.add_argument("--khong-ghi-viec", action="store_true")
    a = ap.parse_args(argv)
    if a.toi_da < 1 or a.toi_da > TRAN_VIEC:
        raise SystemExit("toi-da phải từ 1 đến %d" % TRAN_VIEC)
    hang, kho = Path(a.hang), Path(a.kho)
    if a.mau_cong_khai:
        q = mau_cong_khai(GOC / "data" / "nguon_seeker" / "nap_ea", a.toi_da, hang)
    else:
        q = quet_kho(kho, hang, a.toi_da)
    specs = [x["spec"] for x in q.get("nhan") or [] if x.get("spec")][:a.toi_da]
    ids = [] if a.khong_ghi_viec else ghi_viec(specs, hang)
    bc = bao_cao(q, ids)
    co = []
    for p in sorted((hang / "can_test").glob("na_*.json")):
        try:
            v = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        co.append({k: v.get(k) for k in ("id", "url_ma_nguon", "nguon", "noi_dung_sha256", "ma",
                                        "he_so_lot", "bien_dich", "dich_python", "che_do_tai_khoan")})
    bc["viec_dang_co"] = co
    BAO.parent.mkdir(parents=True, exist_ok=True)
    BAO.write_text(json.dumps(bc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"viec_moi": ids, "kho": bc["kho"], "da_xem": bc["da_xem"],
                      "tu_choi": len(bc["tu_choi"]), "trung": len(bc["trung"]),
                      "bien_dich": bc["bien_dich"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
