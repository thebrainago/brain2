# -*- coding: utf-8 -*-
"""Nguồn SEEKER: loại lỗi, nhịp, parser, 83 tín hiệu, chẩn đoán. Không gọi mạng."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from nhan import loc_trung_tai as LT
from nhan import nguon_seeker as NS
from seeker import chan_doan, khop_trung
from seeker.cong_khai import kho_83, loc_chat, mql5
from seeker.cong_khai import nen_tang_khac as NK
from seeker.cong_khai import myfxbook
from seeker.nguon_file import phan_tich as PT
from seeker.nhip_tai import NhipTai
from seeker.phan_loai_loi import phan_loai_http

GOC = Path(__file__).resolve().parent
FX = GOC / "seeker" / "fixtures"
pytestmark = pytest.mark.timeout(60)


def _doc(ten):
    return (FX / ten).read_text(encoding="utf-8")


def test_phan_loai_http_khong_tron_loai():
    assert phan_loai_http(403, "Just a moment... cf-chl", "https://x")["loai"] == "challenge"
    assert phan_loai_http(403, "Just a moment... cf-chl", "https://x")["dung_mien"] is True
    assert phan_loai_http(200, "<title>Just a moment...</title>", "https://x")["loai"] == "challenge"
    assert phan_loai_http(401, "", "https://x")["loai"] == "auth"
    assert phan_loai_http(200, "ok", "https://a/p", "https://a/login")["loai"] == "auth"
    loi = phan_loai_http(None, "", "https://social-trading.exness.com/strategy/1",
                         loi="SSLError: hostname 198.18.0.1")
    assert loi["loai"] == "network" and "198.18.0.1" in loi["ly_do"] and "không" in loi["ly_do"].lower() or "KHONG" in loi["ly_do"] or "Không" in loi["ly_do"]
    assert phan_loai_http(200, "x" * 100, "https://a")["loai"] == "ok"


def test_quet_mot_khong_thanh_cong_im():
    rss = _doc("rss_rong.xml")
    html = "<html><body>" + ("không có link " * 400) + "</body></html>"

    def get(u):
        if u.endswith("robots.txt"):
            return {"ma": 404, "text": "missing"}
        if u.endswith("/rss"):
            return {"ma": 200, "text": rss, "url_cuoi": u}
        return {"ma": 200, "text": html, "url_cuoi": u}

    mang = NS.Mang(get=get, ngu=lambda s: None, dong_ho=lambda: 1e9)
    rong = NS.quet_mot("r", {"cach": "rss", "url": "https://a.com/rss", "can_dang_nhap": False}, mang)
    assert rong["loai"] == "no_data" and rong["trang_thai"] != NS.DOC_DUOC and rong["muc"] == 0
    sai = NS.quet_mot("h", {"cach": "http", "url": "https://a.com/trang", "can_dang_nhap": False}, mang)
    assert sai["loai"] == "parse" and sai["trang_thai"] != NS.DOC_DUOC
    assert NS.link_ma("xem https://github.com/a/b/blob/main/ea.mq5 xong") == ["https://github.com/a/b/blob/main/ea.mq5"]


def test_nhip_cache_429_challenge_stale_resume(tmp_path):
    dong = {"t": 0.0}
    ngu = []

    def dong_ho():
        return dong["t"]

    def ngu_fn(s):
        ngu.append(s)
        dong["t"] += s

    goi = []

    def get(u):
        goi.append(u)
        return {"ma": 200, "text": "than " + u, "url_cuoi": u}

    n = NhipTai(tmp_path, get=get, ngu=ngu_fn, dong_ho=dong_ho, gian_cach=4, het_han=100)
    assert n.lay("https://h.com/a")["loai"] == "ok"
    assert n.lay("https://h.com/b")["loai"] == "ok"
    assert ngu and ngu[0] >= 4
    assert n.lay("https://h.com/a")["nguon"] == "cache" and len(goi) == 2

    goi.clear()

    def get429(u):
        goi.append(u)
        if len(goi) < 3:
            return {"ma": 429, "text": "slow down", "url_cuoi": u}
        return {"ma": 200, "text": "xong", "url_cuoi": u}

    n429 = NhipTai(tmp_path / "b", get=get429, ngu=ngu_fn, dong_ho=dong_ho, gian_cach=4, het_han=10, lan_429=2)
    assert n429.lay("https://r.com/q")["loai"] == "ok" and len(goi) == 3

    goi.clear()

    def get403(u):
        goi.append(u)
        return {"ma": 403, "text": "Just a moment cf-chl", "url_cuoi": u}

    nc = NhipTai(tmp_path / "c", get=get403, ngu=ngu_fn, dong_ho=dong_ho, gian_cach=0, het_han=10)
    assert nc.lay("https://c.com/1")["loai"] == "challenge"
    assert nc.lay("https://c.com/2")["khong_goi"] is True and len(goi) == 1

    ns = NhipTai(tmp_path / "s", get=get, ngu=ngu_fn, dong_ho=dong_ho, gian_cach=0, het_han=5)
    assert ns.lay("https://s.com/a")["loai"] == "ok"
    dong["t"] += 100

    def get_hong(u):
        return {"ma": None, "text": "", "loi": "ConnectTimeout: 198.18.0.1", "url_cuoi": u}

    ns.get = get_hong
    st = ns.lay("https://s.com/a")
    assert st["loai"] == "stale" and st["stale"] is True and "198.18.0.1" in st["ly_do"]
    ns.danh_dau("khoa-1")
    assert NhipTai(tmp_path / "s", get=get, ngu=ngu_fn, dong_ho=dong_ho).da_xong("khoa-1")


def test_litefinance_va_csv_mql5():
    ro = NK.litefinance_danh_sach_ro(_doc("litefinance_danh_sach.html"))
    assert ro["so_ho_so"] == 2 and ro["da_danh_gia"] == 0 and ro["loai"] == "no_data"
    assert "0 trader" in ro["ly_do"] and "không phải 0 trader" in ro["ly_do"]
    vo = NK.litefinance_danh_sach_ro(_doc("litefinance_vo_js.html"))
    assert vo["loai"] == "parse" and vo["so_ho_so"] == 0
    ct = NK.litefinance_chi_tiet(_doc("litefinance_danh_sach.html"),
                                "https://my.litefinance.org/en/traders/info?id=11",
                                "https://my.litefinance.org/en/traders")
    assert ct["loai"] == "auth" and ct["da_danh_gia"] is False
    tot = NK.litefinance_chi_tiet(_doc("litefinance_chi_tiet.html"),
                                 "https://my.litefinance.org/en/traders/info?id=11",
                                 "https://my.litefinance.org/en/traders/info?id=11")
    assert tot["da_danh_gia"] is True and tot["dd_pct"] == 22.5 and tot["tuoi_thang"] == 30
    login = _doc("mql5_history_login.html")
    assert mql5.phan_loai_xuat_csv(302, login, "https://www.mql5.com/en/signals/1/export/history",
                                  "https://www.mql5.com/en/auth_login")["loai"] == "auth"
    assert mql5.phan_loai_xuat_csv(200, login, "https://www.mql5.com/en/signals/1/export/history")["so_dong"] is None
    csv = _doc("mql5_history.csv")
    assert mql5.phan_loai_xuat_csv(200, csv, "https://www.mql5.com/en/signals/1/export/history")["so_dong"] == 2
    assert myfxbook.phan_tich(_doc("forexfactory_challenge.html"), "https://www.myfxbook.com/systems")["loai"] == "challenge"


def test_adapter_file_va_khong_im():
    tv = PT.boc_tradingview(200, _doc("tradingview_scripts.html"), "https://www.tradingview.com/scripts/")
    assert tv["loai"] == "ok" and len(tv["script"]) == 2 and all(s["da_dich"] is False for s in tv["script"])
    assert PT.boc_tradingview(200, _doc("tradingview_js.html"), "https://www.tradingview.com/scripts/")["loai"] == "parse"
    pine = PT.boc_pine(_doc("tradingview_pine.html"))
    assert pine["loai"] == "ok" and pine["da_dich"] is False and "strategy" in pine["pine"]
    assert PT.boc_pine("<html>enable javascript</html>")["loai"] == "not_implemented"
    gh = PT.boc_github_tim(200, _doc("github_search_ok.json"), "https://api.github.com/search/repositories")
    assert gh["loai"] == "ok" and gh["items"][0]["full_name"] == "example/GridEA"
    rate = PT.boc_github_tim(403, _doc("github_rate.json"), "https://api.github.com/search/repositories")
    assert rate["loai"] == "challenge" and rate["items"] == []
    assert PT.boc_github_tim(200, '{"total_count": 0, "items": []}', "https://api.github.com/x")["loai"] == "no_data"
    cb = PT.boc_trang_codebase(200, _doc("mql5_codebase.html"), "42")
    assert cb["loai"] == "ok" and cb["ten"] == "AUDCAD Sample" and cb["tep_mq5"]
    assert PT.boc_trang_codebase(200, "<html><title>x</title></html>", "42")["loai"] == "parse"
    ff = PT.boc_dien_dan(200, _doc("forexfactory_challenge.html"), "https://www.forexfactory.com/forum/71", "forexfactory")
    assert ff["loai"] == "challenge"
    assert PT.boc_dien_dan(200, "<html><body>forum</body></html>", "https://www.forexfactory.com/x", "forexfactory")["loai"] == "parse"


def _ho_so(**kw):
    r = {"nen_tang": "MQL5", "id": "1", "ten": "Grid words only", "url": "https://www.mql5.com/en/signals/1",
         "that_demo": "that", "tuoi_thang": 30, "symbol": ["AUDCAD"], "dd_pct": 20, "cagr_pct": 15,
         "kieu": ["grid"], "bat_dau": "2024.01.01", "may_chu": "X",
         "duong_cong": {"growth_mau": [("2024-01-01", 10), ("2024-06-01", 20)], "thang_te_nhat_pct": -5,
                        "theo_nam_pct": {"2024": 10}}}
    r.update(kw)
    return r


def test_luoi_tu_khoa_khong_loai(tmp_path, monkeypatch):
    monkeypatch.setattr(loc_chat, "CSV_DIR", tmp_path)
    d = loc_chat.danh_gia(_ho_so())
    assert d["dat"] is True and d["nhan_luoi"] == "nghi_ngo_tu_khoa"
    assert not any("lưới" in x for x in d["ly_do_loai"])
    (tmp_path / "9.history.csv").write_text(
        "Time;Symbol;Type;Direction;Volume;Price\n"
        "2020.03.01 00:00:00;AUDCAD;Buy;In;0.01;0.9\n"
        "2020.03.01 01:00:00;AUDCAD;Buy;In;0.02;0.89\n"
        "2020.03.01 02:00:00;AUDCAD;Buy;In;0.04;0.88\n", encoding="utf-8")
    d2 = loc_chat.danh_gia(_ho_so(id="9", kieu=[]))
    assert d2["dat"] is True and d2["nhan_luoi"] == "chung_minh_lenh" and d2["canh_bao_luoi"]


def test_khop_trung_than_trong():
    assert khop_trung.la_chung_minh_vi_khop_ten(0.7) is False
    a = {"id": "1", "ten": "Alpha Beta Gamma Delta", "ma": [], "may_chu": ""}
    b = {"id": "2", "ten": "Alpha Beta Gamma Epsilon", "ma": [], "may_chu": ""}
    assert khop_trung.trung_chac(a, b) is None and khop_trung.trung_nghi(a, b) is None
    c = {"id": "3", "ten": "Harmonizer High Risk", "ma": ["AUDCAD", "NZDCAD"], "may_chu": "Alpari-MT5"}
    e = {"id": "4", "ten": "Harmonizer Extreme", "ma": ["AUDCAD", "NZDCAD"], "may_chu": "Alpari-MT5"}
    assert "nghi" in khop_trung.trung_nghi(c, e)
    assert khop_trung.trung_chac({"id": "9"}, {"id": "9", "ten": "khac"}) == "cùng id"
    assert khop_trung.trung_nghi({"ten_tep": "a.mq5", "repo": "a/x", "ten": "", "ma": []},
                                 {"ten_tep": "a.mq5", "repo": "b/y", "ten": "", "ma": []})


def test_kho_83_nhap_va_uu_tien(tmp_path, monkeypatch):
    monkeypatch.setattr(kho_83, "GOC", tmp_path)
    ds = kho_83.doc_bang((GOC / "reports" / "MQL5_LOC_CHAT.md").read_text(encoding="utf-8"))
    assert len(ds) == 83 and ds[0]["id"] == "1862128" and ds[-1]["id"] == "2356275"
    assert all(x["giao_dich_duoc"] is False and x["cap"] == "man_hinh_lich_su_cong_khai" for x in ds)
    khong = [x for x in ds if x["nhom_uu_tien"] == 0]
    co = [x for x in ds if x["nhom_uu_tien"] == 2]
    assert khong and co and any(x["id"] == "2394758" for x in khong) and any(x["id"] == "1862128" for x in co)
    kho = kho_83.kiem_ke(GOC / "reports" / "MQL5_LOC_CHAT.md", tmp_path / "csv")
    assert kho["so"] == 83 and kho["quy_tac_dung_duoc"] == 0
    assert all(x["csv"]["loai"] == "thieu_du_lieu" for x in kho["tin_hieu"])
    assert not any(x["csv"]["loai"] == "no_data" for x in kho["tin_hieu"])
    meta = kho_83.nhap(FX / "mql5_history.csv", "2394758", "https://www.mql5.com/en/signals/2394758",
                      tmp_path / "csv", GOC / "reports" / "MQL5_LOC_CHAT.md")
    assert meta["giao_dich_duoc"] is False and meta["cap"] == "replay_csv" and meta["so_dong"] == 2
    lai = kho_83.kiem_ke(GOC / "reports" / "MQL5_LOC_CHAT.md", tmp_path / "csv")
    mot = next(x for x in lai["tin_hieu"] if x["id"] == "2394758")
    assert mot["cap"] == "replay_csv" and mot["csv"]["loai"] == "ok" and mot["giao_dich_duoc"] is False
    with pytest.raises(ValueError):
        kho_83.nhap(FX / "mql5_history.csv", "2394758", "https://example.com/khong", tmp_path / "csv2",
                    GOC / "reports" / "MQL5_LOC_CHAT.md")
    (tmp_path / "login.html").write_text("<html>Please log in</html>", encoding="utf-8")
    with pytest.raises(ValueError):
        kho_83.nhap(tmp_path / "login.html", "2394758", "https://www.mql5.com/en/signals/2394758",
                    tmp_path / "csv3", GOC / "reports" / "MQL5_LOC_CHAT.md")


def test_chan_doan_311_khong_goi_so_0():
    k = chan_doan.lap(GOC, bay=datetime(2026, 11, 7, 12, 0))
    assert k["so_nguon"] == 311
    assert k["quy_tac_dung_duoc"] == 0
    loai = {r["ma"]: r for r in k["nguon"]}
    assert k["theo_loai"].get("unknown", 0) > 100
    assert k["theo_loai"].get("no_data", 0) == 0
    q = loai["quantconnect"]
    assert q["loai"] == "stale" and q["loai_ban_chup"] == "ok" and str(q["lan_thanh_cong"]).startswith("2026-10-20")
    assert loai["arxiv"]["loai"] == "stale" and loai["arxiv"]["loai_ban_chup"] == "robots"
    assert loai["arxiv"]["lan_thanh_cong"] is None
    assert loai["myfxbook"]["loai"] == "stale" and loai["myfxbook"]["loai_ban_chup"] == "challenge"
    assert loai["mql5_codebase"]["quy_tac_dung_duoc"] == 0 and loai["mql5_codebase"]["ma_nguon_ban_chup"] == 99
    assert loai["tradingview_strategies"]["loai_ban_chup"] == "not_implemented"
    assert loai["forexfactory"]["loai_ban_chup"] == "parse"
    assert loai["mql5_signals"]["man_hinh_lich_su"] == 1065 and loai["mql5_signals"]["quy_tac_dung_duoc"] == 0
    ngoai = {x["ma"]: x for x in k["ngoai_so"]}
    assert ngoai["litefinance"]["loai"] == "stale" and ngoai["exness"]["loai_ban_chup"] == "network"
    assert "198.18" in ngoai["exness"]["ly_do"]


def test_loc_trung_challenge_khong_tai():
    ok, ly, m = LT.nen_tai("a/ea", get=lambda u: (403, {"message": "API rate limit exceeded"}), so=[])
    assert ok is False and m["loai"] == "challenge" and "CHALLENGE" in ly
    ok2, ly2, _ = LT.nen_tai("a/ea", get=lambda u: (0, None), so=[])
    assert ok2 is True and "CHUA_DO_DUOC" in ly2
