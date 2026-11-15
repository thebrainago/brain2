# -*- coding: utf-8 -*-
"""Chẩn đoán phủ sóng nguồn SEEKER — không quét hàng loạt.

Đọc sổ `config/nguon_seeker.json` và các bản chụp đã commit. Nguồn chưa có
phép đo là `unknown`, bản cũ hơn 3 ngày là `stale`. Không biến hai trạng thái
đó thành số 0. `--smoke N` chỉ gọi tối đa N URL công khai (trần cứng 5), dừng
host khi gặp challenge.

    python -m seeker.chan_doan
    python -m seeker.chan_doan --smoke 2
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
HAN_NGAY = 3
RA = GOC / "reports" / "seeker_nguon" / "CHAN_DOAN.json"
RA_MD = GOC / "reports" / "seeker_nguon" / "CHAN_DOAN.md"
SMOKE_URL = (
    ("mql5_tin_hieu_mot", "https://www.mql5.com/en/signals/1862128"),
    ("exness_mot", "https://social-trading.exness.com/strategy/110170778"),
)


def _ngay(s: str | None):
    if not s:
        return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _tuoi(luc, bay: datetime) -> int | None:
    d = _ngay(luc)
    if not d:
        return None
    return (bay.date() - d.date()).days


def _map_trang(tt: str) -> str:
    return {
        "ĐỌC ĐƯỢC": "ok",
        "KHÔNG CÓ MỤC": "no_data",
        "LỖI PHÂN TÍCH": "parse",
        "BỊ CHẶN — cần chạy máy nhà": "challenge",
        "CẦN ĐĂNG NHẬP": "auth",
        "LỖI MẠNG / HẾT HẠN": "network",
        "ROBOTS.TXT CẤM — không đọc": "robots",
        "CHƯA CÓ URL": "not_implemented",
        "THỦ CÔNG (chủ dự án)": "not_implemented",
    }.get(tt or "", "unknown")


def _ap_tuoi(loai_ban: str, tuoi: int | None, luc: str | None, ly: str) -> dict:
    thanh = luc if loai_ban == "ok" else None
    if tuoi is None:
        return {"loai": "unknown", "loai_ban_chup": loai_ban, "do": "khong_ro_ngay",
                "lan_thanh_cong": thanh, "ly_do": ly}
    if tuoi > HAN_NGAY:
        return {"loai": "stale", "loai_ban_chup": loai_ban, "do": "ban_chup",
                "lan_thanh_cong": thanh, "tuoi_ngay": tuoi,
                "ly_do": f"bản {luc} ({tuoi} ngày) — không phải phép đo hôm nay. {ly}"}
    return {"loai": loai_ban, "loai_ban_chup": loai_ban, "do": "ban_chup",
            "lan_thanh_cong": thanh, "tuoi_ngay": tuoi, "ly_do": ly}


def _doc_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def lap(goc: Path = GOC, bay: datetime | None = None) -> dict:
    bay = bay or datetime.now()
    so = json.loads((goc / "config" / "nguon_seeker.json").read_text(encoding="utf-8"))
    nguon = so["nguon"]
    quet = _doc_json(goc / "reports" / "SEEKER_QUET_NGUON.json") or {}
    theo = {r.get("ma"): r for r in quet.get("nguon") or []}
    tep = _doc_json(goc / "seeker" / "nguon" / "nguon_file.json") or []
    if isinstance(tep, dict):
        tep = tep.get("nguon") or []
    dem_tep = Counter((x.get("nguon"), x.get("lan")) for x in tep)
    md_tep = (goc / "reports" / "NGUON_CO_FILE.md").read_text(encoding="utf-8") if (goc / "reports" / "NGUON_CO_FILE.md").exists() else ""
    mngay = re.search(r"quét (\d{2})/(\d{2})/(\d{4})", md_tep)
    luc_tep = f"{mngay.group(3)}-{mngay.group(2)}-{mngay.group(1)}" if mngay else None
    ck = (goc / "reports" / "NGUON_CONG_KHAI_DAT.md").read_text(encoding="utf-8") if (goc / "reports" / "NGUON_CONG_KHAI_DAT.md").exists() else ""
    luc_ck = (re.search(r"Đo lúc (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", ck) or type("x", (), {"group": lambda *_: None})()).group(1)
    so_id = re.search(r"id_tim_thay=(\d+), doc_duoc=(\d+), khong_doc=(\d+)", ck)
    man_hinh = re.search(r"Tỉ lệ ĐẠT MQL5: (\d+)/(\d+)", ck)

    def ban_tep(loai_ban: str, ly: str, quy_tac: int = 0, **them):
        o = _ap_tuoi(loai_ban, _tuoi(luc_tep, bay), luc_tep, ly)
        o.update(quy_tac_dung_duoc=quy_tac, **them)
        return o

    ff = next((x for x in tep if x.get("nguon") == "forexfactory"), None)
    fs = next((x for x in tep if x.get("nguon") == "forex_station"), None)
    tv_n = sum(1 for x in tep if x.get("nguon") == "tradingview" and x.get("lan") != "loai")
    gh_ma = dem_tep.get(("github", "co_ma_nguon"), 0)
    cb_ma = dem_tep.get(("mql5_codebase", "co_ma_nguon"), 0)

    chuyen = {
        "github": ban_tep("ok", f"bản danh mục GitHub: {gh_ma} repo có tệp mã giấy phép tự do. Đó là mã nguồn, chưa phải quy tắc đã giải mã.",
                          ma_nguon_ban_chup=gh_ma),
        "github_mql5": ban_tep("ok", "cùng bản quét GitHub  — mã tải về không phải luật đã giải mã.", ma_nguon_ban_chup=gh_ma),
        "mql5_codebase": ban_tep("ok", f"Code Base bản chụp: {cb_ma} EA làn A (có mã). Chưa dịch thành quy tắc đã kiểm OOS.",
                                 ma_nguon_ban_chup=cb_ma),
        "tradingview_strategies": ban_tep("not_implemented", f"{tv_n} script mở trong danh mục; Pine chưa tải/dịch.", so_script=tv_n),
        "tradingview_scripts": ban_tep("not_implemented", f"{tv_n} script; Pine do JS vẽ, bộ đọc tĩnh chưa có mã.", so_script=tv_n),
        "tradingview_pine": ban_tep("not_implemented", "Pine chưa dịch.", so_script=tv_n),
        "mql5_signals": _ap_tuoi("ok", _tuoi(luc_ck, bay), luc_ck,
                                 "trang tín hiệu đọc được trong bản chụp. %s/%s màn hình DD<80 & CAGR>10 là lịch sử người khác, không phải quy tắc của mình."
                                 % (man_hinh.group(1) if man_hinh else "?", man_hinh.group(2) if man_hinh else "?")),
        "mql5_tin_hieu_mt5": _ap_tuoi("ok", _tuoi(luc_ck, bay), luc_ck, "cùng bản quét tín hiệu MQL5; không phải ĐẠT của hệ mình."),
    }
    if ff:
        loai_ff = "parse" if ff.get("so_chu_de") in (0, None) and str(ff.get("trang_thai", "")).endswith("200") else "challenge"
        chuyen["forexfactory"] = ban_tep(loai_ff, "bản diễn đàn: %s, chủ đề=%s. 0 chủ đề sau HTTP 200 không phải diễn đàn rỗng." % (ff.get("trang_thai"), ff.get("so_chu_de")))
        chuyen["forexfactory_ea_threads"] = chuyen["forexfactory"]
    if "bi_chan" in ck and "myfxbook" in ck:
        chuyen["myfxbook"] = _ap_tuoi("challenge", _tuoi(luc_ck, bay), luc_ck, "bản 03/11: HTTP 403 Cloudflare. Dừng, không vượt.")
        chuyen["myfxbook_autotrade"] = chuyen["myfxbook"]
    for _k, v in chuyen.items():
        v.setdefault("quy_tac_dung_duoc", 0)
    for k in ("mql5_signals", "mql5_tin_hieu_mt5"):
        if k in chuyen:
            chuyen[k]["man_hinh_lich_su"] = int(man_hinh.group(1)) if man_hinh else None
            chuyen[k]["quy_tac_dung_duoc"] = 0

    hang = []
    for ma, s in nguon.items():
        cach = s.get("cach") or ""
        url = s.get("url") or ""
        rec = {"ma": ma, "cach": cach, "url": url[:180], "quy_tac_dung_duoc": 0,
               "adapter": None, "loai": "unknown", "loai_ban_chup": None, "do": "chua_do",
               "lan_thanh_cong": None, "ly_do": "chưa có phép đo trong bản chụp đã commit"}
        if cach in ("rss", "http", "api", "telegram_web") and url.startswith("http"):
            rec["adapter"] = "nhan.nguon_seeker.quet_mot"
        elif cach == "dang_nhap" or (cach == "trinh_duyet" and s.get("can_dang_nhap")):
            rec.update(loai="auth", do="khai_bao", ly_do="sổ nguồn khai báo cần đăng nhập hoặc trình duyệt đã đăng nhập — không đo từ box này")
        elif cach in ("tay", "trinh_duyet") or not url.startswith("http"):
            rec.update(loai="not_implemented", do="khai_bao",
                       ly_do="chưa có bộ đọc tự động an toàn (thủ công, trình duyệt, hoặc chưa có URL)")
        if ma in chuyen:
            c = chuyen[ma]
            rec.update({k: c.get(k) for k in ("loai", "loai_ban_chup", "do", "lan_thanh_cong", "ly_do", "quy_tac_dung_duoc",
                                              "tuoi_ngay", "ma_nguon_ban_chup", "so_script", "man_hinh_lich_su") if k in c or k in ("loai",)})
            rec["adapter"] = rec["adapter"] or "ban_chup_chuyen_biet"
        elif ma in theo:
            r = theo[ma]
            loai_ban = r.get("loai") or _map_trang(r.get("trang_thai"))
            ap = _ap_tuoi(loai_ban, _tuoi(r.get("luc") or quet.get("luc"), bay), r.get("luc") or quet.get("luc"),
                          "sổ quét: %s — %s" % (r.get("trang_thai"), r.get("ly_do")))
            rec.update(ap)
            if loai_ban == "ok":
                rec["muc_ban_chup"] = r.get("muc")
        hang.append(rec)

    dem = Counter(r["loai"] for r in hang)
    chuyen_biet = []
    if fs:
        chuyen_biet.append({"ma": "forex_station", "adapter": "seeker.nguon_file.quet",
                            **ban_tep("parse" if fs.get("so_chu_de") in (0, None) else "ok",
                                      "không nằm trong 311 dòng sổ. Bản: %s, chủ đề=%s." % (fs.get("trang_thai"), fs.get("so_chu_de")))})
    if ck:
        chuyen_biet.append({"ma": "litefinance", "adapter": "seeker.cong_khai.nen_tang_khac",
                            **_ap_tuoi("no_data", _tuoi(luc_ck, bay), luc_ck,
                                       "bản ghi 16 hồ sơ danh sách CHƯA ĐO (thiếu DD/tuổi) và chi tiết không công khai. Không phải 0 trader.")})
        ex_loai = "network" if re.search(r"exness.com/strategy/\d+` — loi", ck) or "social-trading.exness.com" in ck else "unknown"
        chuyen_biet.append({"ma": "exness", "adapter": "seeker.cong_khai.nen_tang_khac",
                            **_ap_tuoi(ex_loai, _tuoi(luc_ck, bay), luc_ck,
                                       "bản ghi 'loi', không phải challenge và không phải 0 chiến lược. Giả thuyết DNS 198.18.0.1 chưa được bản này chứng minh.")})
    if so_id:
        for x in chuyen_biet:
            if x["ma"] == "litefinance":
                x["so_ho_so_ban_chup"] = 16
                x["da_danh_gia"] = 0
    return {
        "luc": bay.strftime("%Y-%m-%d %H:%M"),
        "han_ban_chup_ngay": HAN_NGAY,
        "so_nguon": len(hang),
        "quy_tac_dung_duoc": sum(int(r.get("quy_tac_dung_duoc") or 0) for r in hang),
        "theo_loai": dict(dem),
        "ghi_chu": "unknown = chưa đo. stale = bản chụp cũ, không phải số 0 mới. no_data chỉ khi bộ đọc chạy đúng và nguồn rỗng. 1065/83 màn hình MQL5 không phải quy tắc dùng được.",
        "cong_khai": {"luc": luc_ck, "id_tim_thay": int(so_id.group(1)) if so_id else None,
                      "doc_duoc": int(so_id.group(2)) if so_id else None,
                      "man_hinh_dat": int(man_hinh.group(1)) if man_hinh else None},
        "nguon": hang,
        "ngoai_so": chuyen_biet,
        "da_xet_trong_SEEKER_QUET_NGUON": quet.get("da_xet"),
        "luc_quet_so": quet.get("luc"),
    }


def ghi(k: dict, json_path: Path = RA, md_path: Path = RA_MD) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    nhe = {**k, "nguon": [{kk: vv for kk, vv in r.items() if kk != "url" or True} for r in k["nguon"]]}
    json_path.write_text(json.dumps(nhe, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Chẩn đoán nguồn SEEKER", "",
         f"Lúc {k['luc']}. Hạn bản chụp: {k['han_ban_chup_ngay']} ngày. Không quét 311 URL.",
         "", k["ghi_chu"], "",
         f"- Nguồn trong sổ: **{k['so_nguon']}**",
         f"- Quy tắc dùng được (đã giải mã điểm vào và OOS): **{k['quy_tac_dung_duoc']}**",
         f"- Lần quét sổ gần nhất: {k.get('luc_quet_so')} — đã xét {k.get('da_xet_trong_SEEKER_QUET_NGUON')}",
         "", "## Theo loại", ""]
    for ten, n in sorted(k["theo_loai"].items(), key=lambda kv: -kv[1]):
        L.append(f"- {ten}: {n}")
    ck = k.get("cong_khai") or {}
    L += ["", "## Bản lịch sử công khai (không phải ĐẠT của mình)", "",
          f"- Lúc {ck.get('luc')}: id {ck.get('id_tim_thay')}, đọc {ck.get('doc_duoc')}, màn hình đạt ngưỡng {ck.get('man_hinh_dat')}."]
    if k.get("smoke"):
        L += ["", "## Smoke có giới hạn", ""]
        for s in k["smoke"]:
            L.append(f"- {s.get('ten')}: {s.get('loai')} — {s.get('ly_do')}")
    L += ["", "## Ngoài sổ 311", ""]
    for x in k.get("ngoai_so") or []:
        L.append(f"- {x['ma']}: {x.get('loai')} / bản {x.get('loai_ban_chup')} — {x.get('ly_do')}")
    L += ["", "## Nguồn (rút gọn)", "",
          "| mã | loại | bản | adapter | lần thành công | quy tắc |",
          "|---|---|---|---|---|---|"]
    for r in k["nguon"]:
        if r["loai"] in ("unknown", "stale", "auth", "not_implemented", "challenge", "parse", "network", "robots", "no_data"):
            L.append("| %s | %s | %s | %s | %s | %s |" % (
                r["ma"], r["loai"], r.get("loai_ban_chup") or "—", r.get("adapter") or "—",
                r.get("lan_thanh_cong") or "—", r.get("quy_tac_dung_duoc")))
    md_path.write_text("\n".join(L) + "\n", encoding="utf-8")


def smoke(n: int = 2, cache: Path | None = None) -> list[dict]:
    """Tối đa 5 GET công khai. Challenge dừng host. Không lưu thân trang vào báo cáo."""
    from seeker.nhip_tai import NhipTai
    n = max(0, min(int(n), 5))
    nip = NhipTai(cache or (GOC / "data" / "nguon_seeker" / "nhip_smoke"), gian_cach=4.0)
    ra = []
    for ten, url in SMOKE_URL[:n]:
        k = nip.lay(url)
        muc = {"ten": ten, "url": url, "loai": k.get("loai"), "http": k.get("http"),
               "ly_do": (k.get("ly_do") or "")[:900], "stale": k.get("stale"),
               "nguon": k.get("nguon"), "ky_tu": len(k.get("text") or ""), "dung_mien": k.get("dung_mien")}
        if k.get("loai") == "ok" and "/signals/" in url and k.get("text"):
            from seeker.cong_khai import mql5
            from seeker.cong_khai.chay import cham
            sid = url.rstrip("/").rsplit("/", 1)[-1]
            t = cham(mql5.phan_tich(k["text"], sid))
            muc["man_hinh"] = {x: t.get(x) for x in ("ten", "tang_truong_pct", "dd_pct", "cagr_pct", "tuoi_thang",
                                                      "that_demo", "so_lenh", "symbol", "trang_thai")}
            muc["man_hinh"]["cap"] = "man_hinh_lich_su_cong_khai"
            muc["man_hinh"]["khong_phai_dat_cua_he"] = True
        ra.append(muc)
        nip.danh_dau("smoke:" + url)
    return ra


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=int, default=0, help="số URL công khai, trần 5, mặc định 0")
    a = ap.parse_args(argv)
    k = lap()
    if a.smoke:
        k["smoke"] = smoke(a.smoke)
    ghi(k)
    print(json.dumps({"so_nguon": k["so_nguon"], "theo_loai": k["theo_loai"],
                      "quy_tac_dung_duoc": k["quy_tac_dung_duoc"],
                      "smoke": k.get("smoke")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
