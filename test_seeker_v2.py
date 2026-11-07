# -*- coding: utf-8 -*-
"""Kiểm thử Seeker v2 (không mạng): đồ thị khái niệm, rút ý tưởng, parser Telegram, bộ tải lịch sự, động cơ, lớp an toàn MXH."""
import json
import pytest
from seeker import van_ban as VB, y_tuong as YT, telegram as TG
from seeker.do_thi import DoThi
from seeker.thu_thap import ThuThap
from seeker.dong_co import DongCo
from seeker.mxh.an_toan import AnToan, DungLai, HanhDongCam

pytestmark = pytest.mark.timeout(60)
HG = {"grid": {"en": ["grid trading"], "zh": ["网格交易"]}, "martingale": {"en": ["martingale"]}}


def test_do_thi_tu_kham_pha_cum_moi():
    d = DoThi(HG)
    for i in range(4):
        d.hoc(f"grid trading with adaptive spacing works; adaptive spacing uses ATR bands version {i}", "en")
    d.hoc("cooking recipes pasta tomato sauce", "en")
    moi = d.thang_cap(toi_da=5, nguong=0.0)
    assert "adaptive spacing" in moi
    assert d.da_biet["adaptive spacing"]["khai_niem"] == "grid"
    assert d.hoc("grid trading with adaptive spacing works; adaptive spacing uses ATR bands version 0", "en") == []  # khử trùng
    assert "adaptive spacing" in d.truy_van("en", 3)


def test_token_cjk():
    t = VB.token("网格交易 策略")
    assert "网格" in t and "交易" in t


def test_rut_y_tuong_tham_so():
    y = YT.rut("Grid EA on XAUUSD H1: 20 pips step, multiplier 1.5, TP 30. Live statement https://www.myfxbook.com/members/abc/123",
               ["grid", "martingale"], "x", "en", "https://e.com/1", None)
    assert y["tham_so"]["buoc_luoi_pip"] == ["20"] and y["tham_so"]["he_so_lot"] == ["1.5"]
    assert y["bang_chung"]["lien_ket"] and y["do_tin_cay"] > 0.6
    assert YT.rut("hello", [], "x", "en", "u", None) is None


TG_HTML = """<div class="tgme_channel_info"></div>
<div class="tgme_widget_message" data-post="kenhA/101"><a class="tgme_widget_message_forwarded_from_name" href="https://t.me/kenhGoc">Goc</a>
<div class="tgme_widget_message_text">Grid EA moi, xem @kenh_ban_be va https://t.me/kenhLink</div>
<div class="tgme_widget_message_document_title">GridMaster_v3.ex5</div><time datetime="2026-10-01T10:00:00+00:00"></time></div>
<div class="tgme_widget_message" data-post="kenhA/100"><div class="tgme_widget_message_text">martingale x2</div>
<div class="tgme_widget_message_document_title">anh.jpg</div></div>"""


def test_parser_telegram():
    r = TG.doc_trang(TG_HTML, "kenha")
    assert r["id_nho_nhat"] == 100 and len(r["tin"]) == 2
    assert set(r["kenh_moi"]) == {"kenhgoc", "kenh_ban_be", "kenhlink"} and r["kenh_moi"]["kenhgoc"] == 3
    assert [t["ten_tep"] for t in r["tep"]] == ["GridMaster_v3.ex5"]


class _R:
    def __init__(self, code, text): self.status_code, self.text = code, text


class _Phien:
    def __init__(self, bang): self.bang, self.headers, self.goi = bang, {}, []
    def get(self, url, timeout=None, stream=False):
        self.goi.append(url)
        return _R(*self.bang.get(url, (404, "")))


def test_thu_thap_robots_chan_cache(tmp_path):
    ph = _Phien({"https://a.com/robots.txt": (200, "User-agent: *\nDisallow: /cam"),
                 "https://a.com/ok": (200, "<html>ok</html>"), "https://a.com/cf": (403, "Just a moment...")})
    tt = ThuThap(tmp_path, gian_cach_s=0, phien=ph)
    assert tt.tai("https://a.com/cam") is None and tt.dem["robots_cam"] == 1
    assert tt.tai("https://a.com/ok") == "<html>ok</html>"
    assert tt.tai("https://a.com/ok") == "<html>ok</html>" and tt.dem["cache"] == 1
    truoc = ph.goi.count("https://a.com/ok")
    assert tt.tai("https://a.com/cf") is None and tt.dem["bi_chan"] == 1
    assert tt.tai("https://a.com/ok") is None and ph.goi.count("https://a.com/ok") == truoc


def test_dong_co_chay_va_tiep_tuc(tmp_path):
    rss = """<?xml version="1.0"?><feed><entry><title>Grid trading with 25 pips step on EURUSD</title>
    <link href="https://www.reddit.com/r/algotrading/comments/x1/"/><content>grid trading martingale recovery t.me/kenhTest</content>
    <updated>2026-10-01</updated></entry></feed>"""
    ph = _Phien({"https://www.reddit.com/r/algotrading/new/.rss": (200, rss), "https://www.reddit.com/robots.txt": (404, ""),
                 "https://www.reddit.com/r/algotrading/comments/x1/": (200, "<html><title>t</title>grid trading martingale 1.5x</html>")})
    tt = ThuThap(tmp_path / "c", gian_cach_s=0, phien=ph)
    dc = DongCo(tmp_path, thu_thap=tt)
    dc.gieo(["reddit_algotrading"], so_truy_van=0)
    r = dc.chay(ngan_sach=5, sau_toi_da=1)
    assert r["so_yeu_cau"] >= 2 and dc.dem["y_tuong"] >= 1
    assert "kenhtest" in dc.tg_bien
    tk = dc.bao_cao(tmp_path / "bc")
    assert tk["so_y_tuong"] >= 1 and (tmp_path / "bc" / "DIGEST.md").exists()
    dc2 = DongCo(tmp_path, thu_thap=tt)          # chạy tiếp: nhớ URL đã thăm
    assert "https://www.reddit.com/r/algotrading/new/.rss" in dc2.da_tham


def _at(tmp_path, **k):
    ch = {"chay_thu": True, "gioi_han_ngay": {"theo_doi": 2, "xin_vao_nhom": 1}, "nhip": {"giua_thao_tac": [0, 0], "sau_follow_join": [0, 0]},
          "hanh_dong_cho_phep": ["tim", "doc", "theo_doi", "xin_vao_nhom", "trang_doc", "tai_tep"], **k}
    return AnToan(ch, tmp_path / "gh.json", ngu=lambda s: None, hom_nay=lambda: "2026-11-03")


def test_an_toan_chay_thu_va_tran(tmp_path):
    at = _at(tmp_path); bam = []
    assert at.thuc_hien("facebook", "xin_vao_nhom", "g1", lambda: bam.append(1)) == "chay_thu" and not bam
    assert at.thuc_hien("facebook", "xin_vao_nhom", "g2", lambda: bam.append(1)) == "vuot_tran"
    at2 = _at(tmp_path / "b", chay_thu=False)
    assert at2.thuc_hien("x", "theo_doi", "a", lambda: bam.append(1)) == "da_lam"
    at2.thuc_hien("x", "theo_doi", "b", lambda: bam.append(1))
    assert at2.thuc_hien("x", "theo_doi", "c", lambda: bam.append(1)) == "vuot_tran" and len(bam) == 2
    assert json.loads((tmp_path / "b" / "gh.json").read_text())["2026-11-03"]["x"]["theo_doi"] == 2


@pytest.mark.parametrize("hd", ["dang_bai", "binh_luan", "nhan_tin", "nhap_mat_khau"])
def test_an_toan_cam_tuyet_doi(tmp_path, hd):
    at = _at(tmp_path, hanh_dong_cho_phep=["dang_bai", "binh_luan", "nhan_tin", "nhap_mat_khau"])
    with pytest.raises(HanhDongCam):
        at.thuc_hien("facebook", hd, "x", lambda: None)


def test_an_toan_dung_khi_captcha(tmp_path):
    at = _at(tmp_path)
    with pytest.raises(DungLai):
        at.kiem_trang("Please complete the security check", "https://facebook.com/x")
    with pytest.raises(DungLai):
        at.kiem_trang("", "https://www.facebook.com/checkpoint/123")
    at.kiem_trang("Grid EA 20 pips", "https://facebook.com/groups/1")


def test_cau_hinh_mac_dinh_an_toan():
    from seeker.mxh.an_toan import doc_cau_hinh
    import yaml, pathlib
    ch = yaml.safe_load(pathlib.Path("seeker/mxh/cau_hinh.yaml").read_text(encoding="utf-8"))
    assert ch["chay_thu"] is True and ch["gioi_han_ngay"]["xin_vao_nhom"] <= 10
    assert not set(ch["hanh_dong_cho_phep"]) & {"dang_bai", "binh_luan", "nhan_tin", "nhap_mat_khau"}
