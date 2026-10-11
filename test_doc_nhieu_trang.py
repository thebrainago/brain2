# -*- coding: utf-8 -*-
"""Doc danh sach NHIEU TRANG co con tro (the-brain DIEN_DAN_DOC 08/10) + bang diem nguon (A5)."""
import json

from nhan import bang_diem_nguon as BDN
from nhan import doc_nhieu_trang as D

GOC = "https://forum.vd.com/f/"


def _trang(n, rel=True, so_bai=3, bat_dau=None):
    b = bat_dau if bat_dau is not None else n * 100
    bai = "".join(f'<a href="/t/bai-{b + i}.{b + i}/">Bai so {b + i} he thong</a>' for i in range(so_bai))
    ke = f'<link rel="next" href="/f/page-{n + 1}">' if rel else ""
    return f"<html><head>{ke}</head><body>{bai}" + "x" * 30000 + "</body></html>"


class Mang:
    def __init__(self, trang):
        self.trang, self.goi = trang, []

    def __call__(self, url):
        self.goi.append(url)
        v = self.trang.get(url)
        if v is None:
            return {"ma": 404, "html": "", "url_cuoi": url, "loi": None}
        if isinstance(v, dict):
            return dict({"url_cuoi": url, "loi": None}, **v)
        return {"ma": 200, "html": v, "url_cuoi": url, "loi": None}


def _cfg(**k):
    c = {"loai": "dien_dan", "trang": [GOC], "loc_lien_ket": r"vd\.com/t/[^/]+\.\d+/?$",
         "trang_moi_luot": 2, "trang_toi_da": 10, "chu_ky_gio": 6, "mo": "tu_dong", "nhom": "dien_dan"}
    c.update(k)
    return {"f": c}


class Dong:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t

    def ngu(self, s):
        self.t += s


def _chay(mang, tmp_path, dong, cfg=None, luu=None, han=999):
    return D.mot_luot(han, lay=mang, luu=luu, ngu=dong.ngu, cau_hinh=cfg or _cfg(),
                      goc=tmp_path, bay_gio=dong)


def _ct(tmp_path):
    return json.loads((tmp_path / "CON_TRO.json").read_text())["f#0"]


def test_di_nhieu_trang_va_tiep_tuc_tu_con_tro(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2), GOC + "page-3": _trang(3),
              GOC + "page-4": _trang(4)})
    dong, da_luu = Dong(), []
    r = _chay(m, tmp_path, dong, luu=lambda ma, c, ds: da_luu.extend(ds) or len(ds))
    assert r["tien"] == 2 and r["moi"] == 6
    assert _ct(tmp_path)["so"] == 3 and _ct(tmp_path)["trang_thai"] == "DANG_DI"
    assert m.goi == [GOC, GOC + "page-2"]
    dong.t += 30                                     # chua du 1 gio -> khong chay
    assert _chay(m, tmp_path, dong)["nguon"]["f#0"]["ly_do"] == "chua_den_chu_ky"
    dong.t += 3600
    _chay(m, tmp_path, dong)
    assert m.goi[2] == GOC + "page-3"                # tiep tuc, khong ve trang 1
    assert all(x["url"].startswith("https://forum.vd.com/t/") for x in da_luu)


def test_doc_lai_trang_dau_khi_qua_chu_ky_khong_doi_con_tro(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2), GOC + "page-3": _trang(3),
              GOC + "page-4": _trang(4)})
    dong = Dong()
    _chay(m, tmp_path, dong)
    dong.t += 7 * 3600
    _chay(m, tmp_path, dong)
    assert m.goi[2] == GOC and m.goi[3] == GOC + "page-3"
    assert _ct(tmp_path)["so"] == 5


def test_tai_hong_con_tro_dung_yen(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": {"ma": None, "html": "", "loi": "Timeout"}})
    dong = Dong()
    _chay(m, tmp_path, dong)
    c = _ct(tmp_path)
    assert c["trang_thai"] == "LOI_TAI" and c["so"] == 2 and c["url"] == GOC + "page-2"


def test_403_dung_ten_mien_24_gio(tmp_path):
    m = Mang({GOC: {"ma": 403, "html": "<title>Just a moment...</title>"}})
    dong = Dong()
    r = _chay(m, tmp_path, dong)
    assert _ct(tmp_path)["trang_thai"] == "BI_CHAN" and r["tien"] == 0
    dong.t += 3600 * 5
    assert _chay(m, tmp_path, dong)["nguon"]["f#0"]["ly_do"] == "bi_chan_tam"
    assert len(m.goi) == 1


def test_trang_1_khong_thay_trang_ke_la_loi_cau_hinh(tmp_path):
    m = Mang({GOC: _trang(1, rel=False)})
    r = _chay(m, tmp_path, Dong())
    assert _ct(tmp_path)["trang_thai"] == "KHONG_THAY_TRANG_TIEP"
    assert r["loi_cau_hinh"]


def test_phan_trang_false_la_mot_trang_khong_loi(tmp_path):
    m = Mang({GOC: _trang(1, rel=False)})
    r = _chay(m, tmp_path, Dong(), cfg=_cfg(phan_trang=False, trang_moi_luot=1))
    assert _ct(tmp_path)["trang_thai"] == "MOT_TRANG" and not r["loi_cau_hinh"]


def test_qua_bien_tra_lai_trang_truoc_la_het_trang(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2, bat_dau=100)})   # page-2 == page-1
    _chay(m, tmp_path, Dong())
    c = _ct(tmp_path)
    assert c["trang_thai"] == "HET_TRANG" and c["so"] == 1


def test_het_trang_quet_lai_sau_168_gio(tmp_path):
    # page-2 khong co rel_next -> doan page-3 (mau_suy_ra) -> 404 = qua bien -> HET_TRANG
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2, rel=False)})
    dong = Dong()
    _chay(m, tmp_path, dong, cfg=_cfg(trang_moi_luot=3))
    assert m.goi[-1] == GOC + "page-3"
    assert _ct(tmp_path)["trang_thai"] == "HET_TRANG"
    dong.t += 100 * 3600
    assert _chay(m, tmp_path, dong)["nguon"]["f#0"]["ly_do"] == "chua_den_han_quet_lai"
    dong.t += 70 * 3600
    _chay(m, tmp_path, dong, cfg=_cfg(trang_moi_luot=3))
    assert m.goi[-3] == GOC


def test_trang_toi_da_xong_vong(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2)})
    _chay(m, tmp_path, Dong(), cfg=_cfg(trang_toi_da=2))
    assert _ct(tmp_path)["trang_thai"] == "XONG_VONG"


def test_chuyen_huong_khac_mien_khong_theo(tmp_path):
    m = Mang({GOC: {"ma": 200, "html": _trang(1), "url_cuoi": "https://spam.vd2.com/"}})
    _chay(m, tmp_path, Dong())
    assert _ct(tmp_path)["trang_thai"] == "LOI_TAI"


def test_can_dang_nhap_ghi_chua_do_duoc_khong_tai(tmp_path):
    m = Mang({})
    r = _chay(m, tmp_path, Dong(), cfg={"dx": {"mo": "can_dang_nhap", "trang": [],
                                               "can_dang_nhap_cho": "xep hang"}})
    assert r["chua_do_duoc"] == {"dx": "xep hang"} and m.goi == []


def test_het_gio_dung_lai(tmp_path):
    m = Mang({GOC: _trang(1), GOC + "page-2": _trang(2)})
    r = _chay(m, tmp_path, Dong(), han=0)
    assert r["tai"] == 0 and r["nguon"]["f#0"].get("het_gio")


def test_tim_trang_ke_thu_tu():
    h = '<a href="/f/page-3">3</a><a href="/f/page-2">2</a><a href="/f/x">Next</a>'
    assert D.tim_trang_ke(h, GOC, 1, {}) == (GOC + "page-2", "neo_so")
    assert D.tim_trang_ke(h, GOC, 1, {"mau_trang": GOC + "?page={n}"})[1] == "mau_trang"
    assert D.tim_trang_ke('<a href="/f/x">Next</a>', GOC, 1, {}) == ("https://forum.vd.com/f/x", "chu_tiep")
    assert D.tim_trang_ke("", GOC + "?page=4", 4, {}) == (GOC + "?page=5", "mau_suy_ra")
    assert D.tim_trang_ke('<a href="/f/x">‹</a>', GOC, 1, {}) == (None, "khong_thay")


def test_boc_lien_ket_khu_trung_query_va_tai_khoan_ff():
    h = ('<a href="/thread/12-abc?goto=lastpost&userid=9">x</a><a href="/thread/12-abc">ABC he</a>'
         '<a href="radjans#acct.47-tab.graph-explorer.1-yaxis">radjans</a>')
    ds = D.boc_lien_ket(h, "https://www.forexfactory.com/trades", r"forexfactory\.com/thread/\d+")
    assert ds == [{"url": "https://www.forexfactory.com/thread/12-abc", "tieu_de": "ABC he"}]
    ds = D.boc_lien_ket(h, "https://www.forexfactory.com/trades",
                        r"forexfactory\.com/[A-Za-z0-9_.-]+#acct\.\d+")
    assert ds[0]["url"] == "https://www.forexfactory.com/radjans#acct.47"


def test_cau_hinh_that_5_nguon_lich_su_lenh():
    ch = D.doc_cau_hinh()
    ls = {m for m, c in ch.items() if c["nhom"] == "lich_su_lenh"}
    assert ls == {"mql5_signals_mt4", "signalstart", "ff_trade_explorer", "darwinex", "fxstat"}
    for m in ("darwinex", "fxstat"):
        assert ch[m]["mo"] == "can_dang_nhap" and "CHUA DO DUOC" in ch[m]["can_dang_nhap_cho"]


# ---------------------------------------------------------------- bang diem nguon
def test_bang_diem_chi_tinh_gia_that_va_ket_qua_moi_nhat(tmp_path):
    sc = tmp_path / "so.jsonl"
    mau = tmp_path / "mau"
    mau.mkdir()
    (mau / "NGUON.json").write_text(json.dumps([{"file": "a.mq5", "nguon": "mql5_code"}]))
    tong = [{"file": "a.mq5", "ten": "A", "giu_lai": False}, {"file": "b.mq5", "ten": "B", "giu_lai": True},
            {"file": "c.mq5", "ten": "C", "loi": "x"}, {"file": "d.mq5", "ten": "D", "trung": True}]
    assert BDN.ghi_tu_vong(tong, mau, "/x/eurusd.csv", so_cai=sc) == 2
    BDN.ghi_tu_vong(tong, mau, None, so_cai=sc)                  # gia lap: khong tinh
    BDN.ghi_tu_vong([{"file": "a.mq5", "ten": "A", "giu_lai": True}], mau, "e.csv", so_cai=sc)
    b = {g["nguon"]: g for g in BDN.bang(sc, them_nguon={"github": 17})}
    assert b["mql5_code"]["da_thu"] == 1 and b["mql5_code"]["dat"] == 1
    assert b["noi_bo:mau"]["dat"] == 1
    assert b["github"]["da_thu"] == 0 and b["github"]["suat_tien"] == 0.1
    assert b["mql5_code"]["suat_tien"] == round(2 / 11, 4)
    md = "\n".join(BDN.bang_md(list(b.values())))
    assert "CHUA DO DUOC" in md and "suat tien" in md
