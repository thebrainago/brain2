# -*- coding: utf-8 -*-
import json
import tempfile
from pathlib import Path
from nhan import kham_pha_sau as K


def test_chuan_hoa_khu_trung():
    a = K.chuan_hoa("https://www.Example.com/a/?utm_source=x&id=3#top")
    b = K.chuan_hoa("http://example.com/a?id=3")
    assert a == b == "https://example.com/a?id=3"
    assert K.chuan_hoa("javascript:void(0)") == ""


def test_phan_loai():
    g = "https://www.forexfactory.com/forum/71"
    assert K.phan_loai("https://github.com/u/repo", g) == "ma"
    assert K.phan_loai("https://www.forexfactory.com/thread/123-x?page=2", g) == "phan_trang"
    assert K.phan_loai("https://www.myfxbook.com/members/abc", g) == "tac_gia"
    assert K.phan_loai("https://www.forexfactory.com/thread/123-x", g) == "bai"
    assert K.phan_loai("https://someblog.net/x", g) == "ngoai"
    assert K.phan_loai("https://www.forexfactory.com/login", g) is None
    assert K.phan_loai("https://www.forexfactory.com/calendar", g) is None
    assert K.phan_loai("https://www.fxblue.com/users/thebrainalgo/analysis", g) is None


def test_diem_giam_theo_do_sau():
    assert K.cham_diem("https://a.com/thread/rsi-strategy", "RSI strategy", "bai", 0) > \
           K.cham_diem("https://a.com/thread/rsi-strategy", "RSI strategy", "bai", 2)


def test_bfs_gioi_han_va_nhip():
    web = {
        "https://a.com/forum": ("strategy", [("RSI strategy thread", "https://a.com/thread/1"),
                                            ("code", "https://github.com/x/ea"),
                                            ("blog backtest", "https://b.net/blog/trend-system")]),
        "https://a.com/thread/1": ("rules entry exit", [("page 2", "https://a.com/thread/1?page=2"),
                                                       ("author", "https://a.com/members/joe")]),
    }
    goi, ngu = [], []
    def lay(u):
        goi.append(u)
        if u not in web:
            raise IOError("404")
        return web[u]
    t = [0.0]
    kp = K.KhamPha(lay, sau=1, ngan_sach=3, giay=999, nhip=4, ngu=lambda s: (ngu.append(s), t.__setitem__(0, t[0] + s)),
                   dong_ho=lambda: t[0])
    kq = kp.chay(["https://a.com/forum"])
    assert len(kq["trang"]) <= 3
    assert "https://github.com/x/ea" not in goi          # link ma khong bi crawl
    assert all(K.chuan_hoa(u) != K.chuan_hoa("https://a.com/thread/1?page=2") for u in goi)  # vuot do sau
    assert any(s > 0 for s in ngu)                        # nhip cung mien
    loai = {u["loai"] for u in kq["ung_vien"]}
    assert {"ma", "bai", "tac_gia"} <= loai and any(u["mien"] == "b.net" for u in kq["ung_vien"])


def test_them_vao_so_khu_trung():
    tmp_path = Path(tempfile.mkdtemp(prefix='kps_'))
    so = tmp_path / "so.json"; hd = tmp_path / "hd.json"
    so.write_text(json.dumps({"nguon": {"cu": {"url": "https://b.net/blog/trend-system/"}}}), encoding="utf-8")
    uv = [{"url": "https://b.net/blog/trend-system", "khoa": K.chuan_hoa("https://b.net/blog/trend-system"),
           "loai": "ngoai", "diem": 5, "chu": "x", "tu": "s"},
          {"url": "https://c.org/research/carry", "khoa": K.chuan_hoa("https://c.org/research/carry"),
           "loai": "bai", "diem": 4, "chu": "carry", "tu": "s"},
          {"url": "https://github.com/x/ea", "khoa": K.chuan_hoa("https://github.com/x/ea"),
           "loai": "ma", "diem": 9, "chu": "", "tu": "s"}]
    r = K.them_vao_so(uv, so, hd, bay_gio="t")
    assert len(r["them_so"]) == 1 and r["them_hang_doi"] == 3
    d = json.loads(so.read_text(encoding="utf-8"))
    assert d["tong"] == 2 and all(v.get("trang_thai", "THU") == "THU" for k, v in d["nguon"].items() if k != "cu")
    r2 = K.them_vao_so(uv, so, hd, bay_gio="t")
    assert r2 == {"them_so": [], "them_hang_doi": 0}


def test_quet_lai_den_han():
    tmp_path = Path(tempfile.mkdtemp(prefix='kps_'))
    p = tmp_path / "td.json"
    p.write_text(json.dumps({"nguon": [{"url": "https://a.com", "chu_ky_gio": 24, "quet_cuoi": 0},
                                       {"url": "https://b.com", "chu_ky_gio": 24, "quet_cuoi": 1000}]}), encoding="utf-8")
    assert [n["url"] for n in K.den_han_quet_lai(p, bay_gio=86400 + 500)] == ["https://a.com"]
    K.danh_dau_da_quet(["https://a.com/"], p, bay_gio=90000)
    assert "https://a.com" not in [n["url"] for n in K.den_han_quet_lai(p, bay_gio=90000 + 3600)]


def test_khoa_nguon_gom_thread():
    a = K.khoa_nguon("https://www.forexfactory.com/thread/1190104-m1-scalp?page=7#post123")
    b = K.khoa_nguon("https://forexfactory.com/thread/1190104-m1-scalp/page-3")
    assert a == b == "https://forexfactory.com/thread/1190104"


def test_khong_them_phan_trang_va_trung_thread():
    tmp_path = Path(tempfile.mkdtemp(prefix='kps_'))
    so = tmp_path / "so.json"; hd = tmp_path / "hd.json"
    so.write_text(json.dumps({"nguon": {}}), encoding="utf-8")
    uv = [{"url": f"https://www.forexfactory.com/thread/1190104-x?page={i}", "khoa": K.chuan_hoa(f"https://www.forexfactory.com/thread/1190104-x?page={i}"),
           "loai": "bai" if i == 1 else "phan_trang", "diem": 5, "chu": "x", "tu": "s"} for i in range(1, 6)]
    uv.append({"url": "https://www.forexfactory.com/thread/1190104-x#post9", "khoa": "k9", "loai": "bai", "diem": 5, "chu": "x", "tu": "s"})
    r = K.them_vao_so(uv, so, hd, bay_gio="t")
    assert len(r["them_so"]) == 1
