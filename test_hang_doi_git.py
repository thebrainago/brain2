# -*- coding: utf-8 -*-
"""Test hàng đợi git + hàm thuần của thợ MT5 (03/11/2026). Dùng repo git thật trong tmp (bare origin + 2 clone)."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "may_nha"))
import hang_doi_git as HD  # noqa: E402
import tho_mt5 as T  # noqa: E402


def g(cwd, *a):
    subprocess.run(["git", *a], cwd=str(cwd), check=True, capture_output=True)


def _repo(tmp):
    o = tmp / "o.git"; g(tmp, "init", "--bare", "-b", "main", str(o))
    a = tmp / "a"; g(tmp, "clone", str(o), str(a))
    for c in ("user.email", "user.name"):
        g(a, "config", c, "t@t")
    (a / "x").write_text("x"); g(a, "add", "x"); g(a, "commit", "-m", "i"); g(a, "push", "origin", "HEAD:main")
    b = tmp / "b"; g(tmp, "clone", str(o), str(b))
    for c in ("user.email", "user.name"):
        g(b, "config", c, "t@t")
    return a, b


def _spec(i, ut=1):
    return {"id": i, "loai": "myfxbook_fetch", "lan": "co_ma_nguon", "url": "https://x", "uu_tien": ut}


def test_kiem_spec():
    assert HD.kiem_spec(_spec("a1")) == []
    assert HD.kiem_spec({"id": "a", "loai": "la"})
    assert any("he_so_lot" in x for x in HD.kiem_spec({"id": "a", "loai": "mt5_backtest", "ea_file": "E", "ma": "M", "tf": "H1",
                                                        "tu": "2020.01.01", "den": "2021.01.01", "he_so_lot": [0]}))
    assert HD.kiem_spec({"id": "../x", "loai": "myfxbook_fetch", "url": "u"})
    b = {"id": "b1", "loai": "mt5_backtest", "lan": "dich_phuong_phap", "ea_file": "E", "ma": "M", "tf": "H1", "tu": "2020.01.01",
         "den": "2021.01.01", "he_so_lot": [1], "lich_su_dat": True}
    assert any("70" in x for x in HD.kiem_spec(b))                       # làn B chưa đo khớp -> loại
    assert any("70" in x for x in HD.kiem_spec({**b, "khop_vao_pct": 69.9}))
    assert HD.kiem_spec({**b, "khop_vao_pct": 70}) == []
    assert HD.kiem_spec({**b, "lan": None})
    assert any("lịch sử" in x for x in HD.kiem_spec({**b, "khop_vao_pct": 90, "lich_su_dat": False}))


def test_lan_a_truoc(tmp_path):
    a, _ = _repo(tmp_path)
    h = HD.HangDoi(a, "m", log=lambda s: None)
    h.them([{**_spec("b1", 99), "lan": "dich_phuong_phap"}, _spec("a1", 1)])
    assert h.nhan()["id"] == "a1"


def test_khop_vao():
    from nhan.dich_nguoc.khop_vao import ty_le_khop, dat
    that = [(0, 1), (10000, -1), (20000, 1), (30000, 1)]
    assert ty_le_khop(that, [(100, 1), (10500, -1), (20000, -1)]) == 50.0
    from nhan.dich_nguoc.khop_vao import cong_lich_su
    assert cong_lich_su(30, 15)[0] and not cong_lich_su(85, 50)[0] and not cong_lich_su(None, 20)[0]
    assert cong_lich_su(10, 3)[0] and not cong_lich_su(40, -5)[0] and not cong_lich_su(20, 30, that=False)[0]
    assert ty_le_khop([], []) is None and not dat(None) and dat(70.0) and not dat(69.99)


def test_nhan_hai_may_khong_trung(tmp_path):
    a, b = _repo(tmp_path)
    ha, hb = HD.HangDoi(a, "may_a", log=lambda s: None), HD.HangDoi(b, "may_b", log=lambda s: None)
    assert ha.them([_spec("j1", 5), _spec("j2", 1)]) == 2
    va = ha.nhan(); vb = hb.nhan()
    assert va["id"] == "j1" and vb["id"] == "j2"          # ưu tiên cao trước, không trùng
    assert hb.nhan() is None                              # hết việc
    assert ha.xong(va, {"tom_tat": "ok"})
    hb.dong_bo()
    d = json.loads((b / "hang_doi/da_test/j1.json").read_text(encoding="utf-8"))
    assert d["trang_thai"] == "XONG" and d["may"] == "may_a"
    so = (b / "hang_doi/so_cai.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(x)["su_kien"] for x in so].count("nhan") == 2


def test_push_bi_tu_choi_thi_lam_lai(tmp_path):
    a, b = _repo(tmp_path)
    ha, hb = HD.HangDoi(a, "may_a", log=lambda s: None), HD.HangDoi(b, "may_b", log=lambda s: None)
    ha.them([_spec("j1"), _spec("j2")])
    hb.dong_bo()
    (a / "y").write_text("y"); g(a, "add", "y"); g(a, "commit", "-m", "y"); g(a, "push", "origin", "HEAD:main")  # máy khác đẩy trước
    v = hb.nhan()
    assert v and v["id"] in ("j1", "j2")
    assert (b / "y").exists()                              # đã đồng bộ ff, không mất commit của máy khác


def test_them_bo_trung(tmp_path):
    a, _ = _repo(tmp_path)
    h = HD.HangDoi(a, "m", log=lambda s: None)
    assert h.them([_spec("j1")]) == 1 and h.them([_spec("j1")]) == 0


def test_ham_thuan():
    assert T.dd_pct("1 234.56 (12.34%)") == 12.34 and T.dd_pct(None) is None
    assert abs(T.cagr(1000, 1000, 1.0) - 100) < 1e-6 and T.cagr(1000, -2000, 1) == -100.0
    csv = "thoi_gian,ma,chieu,gia,nguon,lot\n2025.01.01 00:00:00,EURUSDmicro,1,1.1,x,30.0\n"
    assert T.nhan_csv(csv, 2).splitlines()[1].endswith(",60")
    assert T.nhan_csv(csv, 2, chia_hash=True).splitlines()[1].endswith(",0.6")
    kq = T.danh_gia([{"k": 1, "cagr_pct": 5, "dd_pct": 10}, {"k": 2, "cagr_pct": 12, "dd_pct": 30}, {"k": 4, "cagr_pct": 30, "dd_pct": 90}])
    assert kq["dat"] and kq["k_tot"] == 2 and kq["k_an_toan_max"] == 2
    tc = T.tinh_chinh({"id": "x", "he_so_lot": [1, 2, 4]}, kq)
    assert tc["he_so_lot"] == [2.5, 3.0, 3.5] and tc["id"] == "x_tc1"
    assert T.danh_gia([])["tom_tat"] == "CHƯA ĐO ĐƯỢC"


def test_hang_doi_gieo_hop_le():
    goc = Path(__file__).resolve().parent / "hang_doi" / "can_test"
    vs = [json.loads(f.read_text(encoding="utf-8")) for f in goc.glob("*.json")]
    assert vs and all(HD.kiem_spec(v) == [] for v in vs)
    assert sum(HD.uoc_gio(v) for v in vs) >= 12
