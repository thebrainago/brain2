import json, os
from nhan import nguon_seeker as NS, may_nha_tuy_chon as MN


def test_so_dang_ky_du_va_khong_bi_mat():
    d = NS.nap()
    assert len(d) >= 200
    raw = open(NS.SO_DANG_KY, encoding="utf-8").read().lower()
    for x in ("password", "mat_khau\":", "api_key\":", "token\":", "secret\":"):
        assert x not in raw
    for s in d.values():
        assert {"phong_cach", "tai_san", "khung", "quan_tri"} <= set(s)


def test_gan_nhan():
    n = NS.gan_nhan({"ten": "grid martingale EA mt4", "url": ""})
    assert "luoi_dca" in n["phong_cach"] and "fx" in n["tai_san"] and "luoi_martingale" in n["quan_tri"]
    assert NS.gan_nhan({"ten": "x"})["phong_cach"] == ["tong_hop"]


def test_phan_loai_chan_va_dang_nhap():
    assert NS.phan_loai({"ma": 403, "text": ""}, "https://a.com")[0] == NS.BI_CHAN
    assert NS.phan_loai({"ma": 200, "text": "<title>Just a moment...</title>"}, "https://a.com")[0] == NS.BI_CHAN
    assert NS.phan_loai({"ma": 200, "text": "x", "url_cuoi": "https://a.com/login"}, "https://a.com/p")[0] == NS.CAN_DANG_NHAP
    assert NS.phan_loai({"ma": 200, "text": "ok" * 20000}, "https://a.com")[0] == NS.DOC_DUOC


def test_robots_va_nhip_va_dung_mien_bi_chan():
    goi, ngu = [], []
    def get(u):
        goi.append(u)
        if u.endswith("robots.txt"):
            return {"ma": 200, "text": "User-agent: *\nDisallow: /cam\n"}
        return {"ma": 429, "text": ""} if "/b" in u else {"ma": 200, "text": "x" * 40000, "url_cuoi": u}
    m = NS.Mang(get=get, ngu=ngu.append, dong_ho=lambda: 0.0)
    assert m.lay("https://a.com/cam")["trang_thai"] == NS.ROBOTS_CAM
    assert m.lay("https://a.com/b")["trang_thai"] == NS.BI_CHAN
    n = len(goi)
    assert m.lay("https://a.com/c")["trang_thai"] == NS.BI_CHAN and len(goi) == n   # khong goi lai mien bi chan
    assert ngu and min(ngu) > 0


def test_kham_pha_va_rss():
    h = '<link rel="alternate" type="application/rss+xml" href="/feed/"> <a href="https://t.me/ForexFreeEA">t</a> https://github.com/abc/def'
    k = NS.kham_pha(h, "https://x.com/p")
    assert k["feed"] == ["https://x.com/feed/"] and "ForexFreeEA" in k["xa_hoi"]["telegram"] and "abc/def" in k["xa_hoi"]["github"]
    assert NS.boc_rss("<rss><item><title>T</title><link>https://u</link></item></rss>") == [{"tieu_de": "T", "url": "https://u"}]


def test_may_nha_tat_mac_dinh(monkeypatch):
    monkeypatch.delenv("BRAIN_MAY_NHA", raising=False)
    assert not MN.duoc_bat() and MN.bat_warp() is False
    monkeypatch.setenv("BRAIN_MAY_NHA", "1")
    assert MN.duoc_bat() == (os.name == "nt")


def test_chuyen_dien_dan():
    c = NS.chuyen_dien_dan({"url": "https://www.mql5.com/ru/forum", "mau_trang": "{base}/page{n}", "cach": "http", "loc_lien_ket": "forum/\\d+"})
    assert c["mau_trang"] == "https://www.mql5.com/ru/forum/page{n}" and c["mo"] == "tu_dong"
