import pytest
from nhan import so_ket_qua as s

pytestmark = pytest.mark.timeout(60) if hasattr(pytest.mark, "timeout") else []


def test_cagr():
    assert s.tinh_cagr(1000, 1000, 1) == 100.0
    assert s.tinh_cagr(None, 1000, 1) is None
    assert s.tinh_cagr(-2000, 1000, 1) == -100.0


def test_trang_thai():
    assert s.xet_trang_thai({"luc_chay": "2026-10-30T10:00:00", "cagr_pct": 50, "dd_pct": 10}) == "BI_THAY_THE"
    assert s.xet_trang_thai({"luc_chay": "2026-11-01T10:00:00", "cagr_pct": 25, "dd_pct": 79.9}) == "DAT"
    assert s.xet_trang_thai({"luc_chay": "2026-11-01T10:00:00", "cagr_pct": 10, "dd_pct": 10}) == "KHONG_DAT"
    assert s.xet_trang_thai({"luc_chay": "2026-11-01T10:00:00", "cagr_pct": 30, "dd_pct": 80}) == "KHONG_DAT"
    assert s.xet_trang_thai({"luc_chay": "2026-11-01T10:00:00", "cagr_pct": 30}) == "CHUA_DO"
    assert s.xet_trang_thai({"luc_chay": "2026-11-01T10:00:00", "cagr_pct": 30, "dd_pct": 5,
                             "nguon": "python_mo_phong"}) == "CHUA_DO"


def test_ghi_va_khu_trung(tmp_path):
    p = tmp_path / "so.csv"
    d = {"he": "X", "nguon": "mt5_real_tick", "net": 500, "von": 1000, "so_nam": 1,
         "dd_pct": 30, "luc_chay": "2026-11-02T10:00:00", "commit": "abc"}
    moi = s.ghi_ket_qua(dict(d), p)
    assert len(moi) == 1 and moi[0]["trang_thai"] == "DAT" and float(moi[0]["cagr_pct"]) == 50.0
    assert s.ghi_ket_qua(dict(d), p) == []
    assert len(s.doc_so(p)) == 1
    with pytest.raises(ValueError):
        s.ghi_ket_qua({"net": 1}, p)


def test_khong_tu_gan_dat_sai(tmp_path):
    p = tmp_path / "so.csv"
    r = s.ghi_ket_qua({"he": "Y", "nguon": "mt5", "cagr_pct": 5, "dd_pct": 10,
                       "luc_chay": "2026-11-02T00:00:00", "trang_thai": "DAT", "commit": "x"}, p)
    assert r[0]["trang_thai"] == "KHONG_DAT"


def test_thu_so_cai(tmp_path):
    f = tmp_path / "so_cai.jsonl"
    f.write_text('{"chat_luong":"99%","dd":"305.18 (28.27%)","ky_bc":"H1 (2023.12.26 - 2026.10.01)",'
                 '"lenh":425,"luc":"2026-10-20T20:18:11","ma":"GBPNZDmicro","net":887.39,"tf":"H1",'
                 '"ten":"od_x","von":1000.0,"file":"a.htm"}\nrac\n', encoding="utf-8")
    r = s.thu_so_cai_mt5(f)
    assert len(r) == 1 and r[0]["dd_pct"] == 28.27 and r[0]["tu"] == "2023-12-26"
    c = s.chuan_hoa(r[0])
    assert c["trang_thai"] == "BI_THAY_THE" and c["cagr_pct"] != ""
