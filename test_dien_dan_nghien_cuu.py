# -*- coding: utf-8 -*-
"""Chẩn đoán diễn đàn: 200 không phải parser chạy; robots có chữ captcha không phải chặn."""
from seeker import dien_dan_nghien_cuu as D

MQL = '<a href="https://www.mql5.com/ru/forum/457258">bài</a>'
VO = '<a href="https://ctrader.com/fr/copy">fr</a><a href="https://ctrader.com/copy">en</a>'
ROBOTS_CAPTCHA = "User-agent: *\nDisallow: /captcha\nAllow: /ru/forum\n"


def test_host_cam_khong_goi():
    goi = []
    r = D.doc_mot({"id": "x", "url": "https://www.myfxbook.com/systems"}, lambda u: goi.append(u) or {})
    assert r["truy_cap"] == "challenge" and r["parser"] == "khong_chay" and r["khong_tao_viec"] and goi == []


def test_robots_co_chu_captcha_van_mo_trang():
    goi = []

    def lay(u):
        goi.append(u)
        if u.endswith("robots.txt"):
            return {"loai": "challenge", "http": 200, "text": ROBOTS_CAPTCHA, "ly_do": "dấu hiệu captcha"}
        return {"loai": "ok", "http": 200, "text": MQL, "url_cuoi": u}
    r = D.doc_mot({"id": "mql5_forum_ru", "url": "https://www.mql5.com/ru/forum"}, lay)
    assert r["truy_cap"] == "ok" and r["parser"] == "ra_url_danh_sach" and r["so_lien_ket"] == 1
    assert any(u.endswith("/ru/forum") for u in goi)


def test_robots_disallow_captcha_khong_phai_chan():
    from seeker.phan_loai_loi import phan_loai_http
    assert phan_loai_http(200, ROBOTS_CAPTCHA, "https://www.mql5.com/robots.txt")["loai"] == "ok"
    assert phan_loai_http(200, "<title>Just a moment...</title>cf-chl", "https://x")["loai"] == "challenge"


def test_copy_nav_khong_phai_ho_so():
    html = '<a href="https://ctrader.com/copy/brokers">b</a><a href="https://ctrader.com/copy/strategies/55">s</a>'
    lk = D.rut_lien_ket(html, "https://ctrader.com/copy", "ctrader_copy")
    assert [x["url"] for x in lk] == ["https://ctrader.com/copy/strategies/55"]


def test_http_200_khong_co_ho_so_la_parser_hong():
    def lay(u):
        if u.endswith("robots.txt"):
            return {"loai": "ok", "http": 200, "text": "User-agent: *\nDisallow:\n"}
        return {"loai": "ok", "http": 200, "text": VO, "url_cuoi": u}
    r = D.doc_mot({"id": "ctrader_copy", "url": "https://ctrader.com/copy"}, lay)
    assert r["truy_cap"] == "ok" and r["parser"] == "khong_ra_url" and r["so_lien_ket"] == 0


def test_robots_cam_khong_mo_trang():
    goi = []

    def lay(u):
        goi.append(u)
        return {"loai": "ok", "http": 200, "text": "User-agent: *\nDisallow: /forums/\n"}
    r = D.doc_mot({"id": "traderviet", "url": "https://traderviet.tv/forums/he-thong.11/"}, lay)
    assert r["truy_cap"] == "robots" and r["parser"] == "khong_chay"
    assert not any("he-thong" in u for u in goi)


def test_than_bai_xenforo_va_mql5():
    tv = '<title>Nhật ký</title><div class="bbWrapper">Nội dung bài viết đủ dài để parser nhận là thân bài chứ không phải menu.</div><time data-time="1700000000"></time>'
    mq = '''<div id="comment_1" class="comment-box"><time class="comment__date" data-date-create="1700000000"></time>
<div class="content" id="content1"><p>Một bài đủ dài để được tính là thân bài diễn đàn, không phải vỏ trang.</p></div></div>'''
    a = D.phan_than_bai(tv, "xenforo")
    b = D.phan_than_bai(mq, "mql5")
    assert a["parser"] == "co_than_bai" and a["so_bai"] == 1 and a["co_ngay"]
    assert b["parser"] == "co_than_bai" and b["so_bai"] == 1 and b["co_ngay"]
    assert D.phan_than_bai("<html><title>Zulu</title><a href='/leaders'>x</a></html>", "xenforo")["parser"] == "khong_co_than"


def test_chu_captcha_khong_phai_chan():
    from seeker.phan_loai_loi import phan_loai_http
    assert phan_loai_http(200, "Bài viết nhắc cách giải captcha của sàn. " * 3, "https://forum.example/t/1")["loai"] == "ok"


def test_trang_dang_nhap_khong_nuot_dien_dan():
    khoa = '<title>Welcome - Log In, Sign Up</title><input type="password"><a href="/help">h</a>'
    dien = '<title>Log in to post</title><input type="password"><a href="/threads/nhat-ky.12/">b</a>'
    assert D.chi_la_cua_dang_nhap(khoa)
    assert not D.chi_la_cua_dang_nhap(dien)
    assert not D.chi_la_cua_dang_nhap("<title>Bảng</title><a href='/users/a'>a</a>")


def test_mot_mien_khong_tinh_ba_nguon():
    assert D.khoa_mien("traderviet", "https://traderviet.com/") == D.khoa_mien("traderviet_ea", "https://traderviet.tv/t/a.1")
    assert D.khoa_mien("fxblue", "https://www.fxblue.com/users") == D.khoa_mien("fxblue_market", "https://www.fxblue.com/market")
    assert D.khoa_mien("forexfactory", "https://www.forexfactory.com/") == D.khoa_mien("forexfactory_trade_explorer", "https://www.forexfactory.com/trades")
    assert D.khoa_mien("fxon", "https://fx-on.com/") == D.khoa_mien("gogojungle", "https://www.gogojungle.co.jp/systemtrade/fx")
    assert D.khoa_mien("mql5_forum_ru", "https://www.mql5.com/ru/forum") == D.khoa_mien("tqtj_ru", "https://www.mql5.com/ru/forum")
    assert D.khoa_mien("myfxbook", "https://www.myfxbook.com/") == D.khoa_mien("tu_myfxbook_com_systems_2", "https://www.myfxbook.com/systems")
    assert D.khoa_mien("arabictrader", "https://www.arabictrader.com/") == "arabictrader.com"
    assert D.khoa_mien("ctrader_copy", "https://ctrader.com/copy") == "ctrader.com"


def test_dot2_khong_trung_dot1_va_khong_goi_api():
    cu = {D.host(s["url"]) for s in D.NGUON} | D.HOST_CAM
    moi = [D.host(s["url"]) for s in D.NGUON_DOT2]
    assert len(moi) == len(set(moi)) == 6
    assert not (set(moi) & cu)
    assert all("/sapi/" not in s["url"] for s in D.NGUON_DOT2)
    assert D.KHONG_GOI[0]["id"] == "etoro" and "/sapi/" in D.KHONG_GOI[0]["url"]


def test_ho_so_dot2_khong_nuot_trang_chu():
    ss = '<a href="/search-signals">ds</a><a href="https://www.signalstart.com/analysis/ten-he/12345">h</a>'
    fb = '<a href="/users">ds</a><a href="https://www.fxblue.com/users/alice">a</a><a href="https://www.fxblue.com/market">m</a>'
    gg = '<a href="/systemtrade/fx">ds</a><a href="https://www.gogojungle.co.jp/systemtrade/fx/998877">sp</a>'
    fx = '<a href="/">home</a><a href="https://fx-on.com/systemtrade/ea-ten-42">ea</a>'
    assert [x["url"] for x in D.rut_lien_ket(ss, "https://www.signalstart.com/search-signals", "signalstart")] == [
        "https://www.signalstart.com/analysis/ten-he/12345"]
    assert [x["url"] for x in D.rut_lien_ket(fb, "https://www.fxblue.com/users", "fxblue")] == [
        "https://www.fxblue.com/users/alice"]
    assert len(D.rut_lien_ket(gg, "https://www.gogojungle.co.jp/systemtrade/fx", "gogojungle")) == 1
    assert len(D.rut_lien_ket(fx, "https://fx-on.com/", "fxon")) == 1
    rac = '<a href="/systemtrade/search/?sort=0profit&amp;page=1">s</a><a href="/systemtrade/fx/77038?via=x&amp;via=y">p</a>'
    lk = D.rut_lien_ket(rac, "https://www.gogojungle.co.jp/systemtrade/fx", "gogojungle")
    assert [x["url"] for x in lk] == ["https://www.gogojungle.co.jp/systemtrade/fx/77038"]


def test_fxon_chuyen_gogojungle_khong_tinh_nguon_moi():
    html = '<a href="https://www.gogojungle.co.jp/systemtrade/fx/77038">a</a>' * 2

    def lay(u):
        if u.endswith("robots.txt"):
            return {"loai": "ok", "http": 200, "text": "User-agent: *\nDisallow:\n"}
        return {"loai": "ok", "http": 200, "text": html, "url_cuoi": "https://www.gogojungle.co.jp/"}
    r = D.doc_mot({"id": "fxon", "url": "https://fx-on.com/"}, lay)
    assert r["parser"] == "trung_nguon" and r["trung_voi"] == "gogojungle" and r["so_lien_ket"] == 0
    assert r["so_ho_so_trung"] == 1


def test_nextjs_khong_co_ho_so_la_can_trinh_duyet():
    html = '<html data-next-head=""><a href="/about">a</a><script src="/_next/static/chunks/a.js"></script></html>'

    def lay(u):
        if u.endswith("robots.txt"):
            return {"loai": "ok", "http": 200, "text": "User-agent: *\nDisallow:\n"}
        return {"loai": "ok", "http": 200, "text": html, "url_cuoi": u}
    r = D.doc_mot({"id": "duplitrade", "url": "https://www.duplitrade.com/"}, lay)
    assert r["truy_cap"] == "ok" and r["parser"] == "js_can_trinh_duyet" and r["so_lien_ket"] == 0
    assert D.rut_lien_ket('<a href="https://www.duplitrade.com/">x</a>', "https://www.duplitrade.com/", "duplitrade") == []


def test_chuyen_login_la_auth():
    def lay(u):
        if u.endswith("robots.txt"):
            return {"loai": "ok", "http": 200, "text": "User-agent: *\nDisallow:\n"}
        return {"loai": "auth", "http": 200, "text": "login", "ly_do": "chuyển hướng /login", "url_cuoi": "https://www.darwinex.com/login"}
    r = D.doc_mot({"id": "darwinex", "url": "https://www.darwinex.com/data/darwin-api"}, lay)
    assert r["truy_cap"] == "auth" and r["parser"] == "khong_chay"
