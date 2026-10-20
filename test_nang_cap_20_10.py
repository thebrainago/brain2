# -*- coding: utf-8 -*-
"""Test nang cap 20/10/2026 (Grok Bot): dich_llm (chuan hoa spec, hop cat, BO_QUA, kiem lai tu cache, rut gon ma),
Python/MT5 (quy doi cap cheo, vao lai cung nen, lai MT5 tu .htm, sai symbol, %/nam theo ky bao cao), loc hai tang,
o dia / RAM / slot, robots, bao cao phien. Khong goi mang, khong co khoa that."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "mt5tools"))

from nhan import cau_llm as LLM  # noqa: E402
from nhan import dich_llm as DL  # noqa: E402
from nhan import hop_cat_llm as HC  # noqa: E402
from nhan import ong_dan as OD  # noqa: E402
from nhan import tai_khoan as TK  # noqa: E402
from nhan import nguon_lenh as NL  # noqa: E402
from nhan.nguon_seeker import QuyTacRobots  # noqa: E402
import quan_ly_slot as QS  # noqa: E402
import sinh_viec as SV  # noqa: E402
import bao_cao_phien as BCP  # noqa: E402

KQ = GOC / "reports" / "ong_dan" / "ket_qua_mt5"


@pytest.fixture(autouse=True)
def _sach(monkeypatch, tmp_path):
    monkeypatch.setattr(LLM, "CC_SWITCH_DB", tmp_path / "khong_co.db")
    for k in ("AIBOX_API_KEY", "BRAIN_LLM_PROXY", "AIBOX_BASE_URL", "BRAIN_LLM_MODEL", "BRAIN_SLOTS", "BRAIN_O_SSD",
              "BRAIN_SAN_TRONG_GB", "BRAIN_HAI_TANG", "BRAIN_RAM_MIN_GB", "BRAIN_RAM_TANG2_GB", "BRAIN_TANG1_MODEL"):
        monkeypatch.delenv(k, raising=False)


def _gia(n=1500, hat=7):
    r = np.random.default_rng(hat)
    x = 1.0 + np.cumsum(r.normal(0, 0.0012, n))
    i = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": np.r_[x[0], x[:-1]], "high": x + 4e-4, "low": x - 4e-4, "close": x}, index=i)


# ------------------------------------------------------------------ dich_llm: chuan hoa spec
def test_spec_cat_len_va_bi_danh_chay_duoc():
    df = _gia()
    sp = [{"ten": "a", "chieu": "buy", "vao": [{"trai": {"chi_bao": "sma", "n": 10}, "phep": "cat_len",
                                                "phai": {"chi_bao": "sma", "n": 30}}]},
          {"ten": "b", "chieu": -1, "vao": [{"trai": {"chi_bao": "ema", "n": 10}, "phep": "cross_below",
                                             "phai": {"chi_bao": "ema", "n": 30}}]}]
    k = DL.kiem_tra({"spec": sp}, df)
    assert k["dat"], k
    assert k["spec"][0]["vao"][0]["phep"] == "cheo_len" and k["spec"][0]["chieu"] == 1
    # toan tu bien doi thieu "cua" -> mac dinh gia dong cua
    sp2 = [{"ten": "c", "chieu": 1, "vao": [{"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">",
                                             "phai": {"chi_bao": "tre", "n": 1, "cua": {"chi_bao": "cao_nhat", "n": 20}}}]}]
    assert DL.kiem_tra({"spec": sp2}, df)["dat"]
    assert LLM.kiem_spec(LLM.chuan_hoa_spec(sp[0])) == []


def test_hop_cat_cho_cot_open_import_np_fstring_nhung_van_chan_nguy_hiem():
    df = _gia()
    ok = ("import numpy as np\nimport pandas as pd\ndef tin_hieu(df):\n    n = 5\n    t = f'n{n}'\n"
          "    try:\n        s = np.where(df['close'] > df['open'], 1, -1)\n    except Exception:\n        s = np.zeros(len(df))\n"
          "    return s\n")
    assert DL.kiem_tra({"python": ok}, df)["dat"]
    assert HC.kiem_ast("import os\ndef tin_hieu(df):\n    return 0")
    assert HC.kiem_ast("def tin_hieu(df):\n    return df.open")              # thuoc tinh .open van cam
    assert HC.kiem_ast("def tin_hieu(df):\n    open('x')\n    return 0")
    assert HC.kiem_ast("def tin_hieu(df):\n    pd.HDFStore('x')\n    return 0")
    assert HC.kiem_ast("def tin_hieu(df):\n    return df.apply('to_csv')")


def test_nhom_ly_do():
    assert DL.nhom_ly_do(["spec khong chay duoc: x"]) == "SPEC_KHONG_CHAY"
    assert DL.nhom_ly_do(["python: cam cu phap Import"]) == "PY_CAM_CU_PHAP"
    assert DL.nhom_ly_do(["python: NameError: x"]) == "PY_LOI_CHAY"
    assert DL.nhom_ly_do(["NHIN TRUOC: cat o nen 9"]) == "NHIN_TRUOC"
    assert DL.nhom_ly_do(["chi ra 1 lenh tren gia mau (< 3)"]) == "IT_LENH"
    assert DL.nhom_ly_do(["LLM khong ra spec hay python dung ()"]) == "KHONG_RA_SPEC_PY"


def test_rut_gon_giu_ontick():
    dau = "//+--+\n" + "\n".join("double bien_%d = %d; // khai bao dai dong" % (i, i) for i in range(1500))
    ma = dau + "\ninput int InpN = 20;\nvoid OnTick()\n{\n   if(iMA(NULL,0,InpN,0,MODE_SMA,PRICE_CLOSE,0) > Close[1]) OrderSend(1);\n}\n"
    assert "OnTick" not in ma[:LLM.TRAN_MA]
    r = LLM.rut_gon_ma(ma, LLM.TRAN_MA)
    assert len(r) <= LLM.TRAN_MA and "OnTick" in r and "input int InpN" in r
    assert LLM.rut_gon_ma("ngan", 100) == "ngan"


def _the(cn, goc, id_, noi_dung, ten_tep):
    f = goc / "data" / "seeker" / ten_tep
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(noi_dung, encoding="utf-8")
    t = {"id": id_, "loai": "he_hoan_thien", "nen_tang": "Python", "uu_tien": 2, "duong_dich": "llm",
         "nguon": {"tep": "data/seeker/" + ten_tep}, "seeker": {}}
    with cn:
        OD._luu(cn, t, "quyet_dinh", "LLM")
    return t


def _moi_truong(monkeypatch, tmp_path):
    monkeypatch.setattr(DL, "GOC", tmp_path)
    monkeypatch.setattr(DL, "CACHE", tmp_path / "data" / "ong_dan" / "dich_llm")
    monkeypatch.setattr(DL, "BAO_CAO", tmp_path / "DICH_LLM.md")
    monkeypatch.setattr(DL, "gia_mau", lambda cfg=None, n=3000: (_gia(1500), "gia gia lap test"))
    return OD._db(tmp_path / "tt.sqlite")


class _Cl:
    def __init__(self, tra):
        self.tra, self.lan = tra, 0

    def __call__(self, url, h, body, timeout):
        self.lan += 1
        return self.tra


def test_loi_llm_lap_lai_thanh_bo_qua(monkeypatch, tmp_path):
    monkeypatch.setenv("AIBOX_API_KEY", "khoa-gia-test")
    cn = _moi_truong(monkeypatch, tmp_path)
    _the(cn, tmp_path, "x", "MARKER", "x.py")
    cl = _Cl((200, {"choices": [{"message": {"content": "khong phai json"}}], "usage": {}}))
    for _ in range(DL.SO_LAN_TOI_DA):
        DL.buoc_dich_llm(cn, client=cl, in_ra=lambda *a: None)
    t = {t["id"]: t for t, *_ in OD.cac_the(cn)}["x"]
    assert t["dich_llm"]["trang_thai"] == "BO_QUA" and t["dich_llm"]["nhom_ly_do"] == "LOI_LLM"
    n = cl.lan
    r = DL.buoc_dich_llm(cn, client=cl, in_ra=lambda *a: None)
    assert cl.lan == n and r["cho"] == 0                         # khong goi lai the BO_QUA
    md = (tmp_path / "DICH_LLM.md").read_text(encoding="utf-8")
    assert "LOI_LLM" in md and "Vì sao hàng chờ lớn lên" in md


def test_hong_phien_cu_kiem_lai_tu_cache_khong_can_khoa(monkeypatch, tmp_path):
    cn = _moi_truong(monkeypatch, tmp_path)
    t = _the(cn, tmp_path, "y", "MA_Y", "y.py")
    h = DL.bam(b"MA_Y")
    sp = [{"ten": "a", "chieu": 1, "vao": [{"trai": {"chi_bao": "sma", "n": 10}, "phep": "cat_len", "phai": {"chi_bao": "sma", "n": 30}}]}]
    DL._ghi_cache(h, {"trang_thai": "OK", "spec": sp, "python": "", "model": "gia"})          # cache phien 1 (khong 'phien')
    t["dich_llm"] = {"trang_thai": "HONG", "bam": h, "ly_do": ["spec khong chay duoc: \"phep so sanh khong biet: 'cat_len'\""]}
    with cn:
        OD._luu(cn, t)
    r = DL.buoc_dich_llm(cn, in_ra=lambda *a: None)              # KHONG co khoa, khong client
    assert r["dat"] == 1 and r["so_lan_goi"] == 0
    st = {x["id"]: (b, tt, x) for x, b, tt, _ in OD.cac_the(cn)}
    assert st["y"][1] == "SPEC_DSL" and st["y"][2]["tin_hieu"]["specs"][0]["vao"][0]["phep"] == "cheo_len"


def test_nhin_truoc_khong_vao_lai_hang(monkeypatch, tmp_path):
    monkeypatch.setenv("AIBOX_API_KEY", "khoa-gia-test")
    cn = _moi_truong(monkeypatch, tmp_path)
    _the(cn, tmp_path, "z", "MA_Z", "z.py")
    nhin = "def tin_hieu(df):\n    c = df['close']\n    return (c.shift(-1) > c).astype(int) * 2 - 1\n"
    cl = _Cl((200, {"choices": [{"message": {"content": json.dumps({"spec": [], "python": nhin})}}], "usage": {}}))
    r = DL.buoc_dich_llm(cn, client=cl, in_ra=lambda *a: None)
    t = {t["id"]: t for t, *_ in OD.cac_the(cn)}["z"]
    assert r["ly_do_hong"] == {"NHIN_TRUOC": 1} and t["dich_llm"]["trang_thai"] == "HONG"
    n = cl.lan
    assert DL.buoc_dich_llm(cn, client=cl, in_ra=lambda *a: None)["cho"] == 0 and cl.lan == n   # khong goi lai


# ------------------------------------------------------------------ Python / MT5
def test_quy_doi_cap_cheo_tu_phi_do():
    hs = TK.ho_so_phi("GBPNZD", "XM")
    if not hs.nhan.startswith("ĐO"):
        pytest.skip("khong co reports/phi_san do that")
    assert 0.5 < hs.qd(2.3) < 0.7 and "QUY ĐỔI NZD" in hs.nhan
    assert TK.ho_so_phi("EURUSD", "XM").qd(1.1) == 1.0


def test_khong_vao_lai_cung_nen_khi_ro_vua_cham_tp():
    i = pd.date_range("2024-01-01", periods=6, freq="h")
    df = pd.DataFrame({"open": [1.0, 1.0, 1.004, 1.0, 1.0, 1.0], "high": [1.0, 1.001, 1.02, 1.0, 1.0, 1.0],
                       "low": [1.0, 0.999, 1.0, 1.0, 1.0, 1.0], "close": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, index=i)
    ev = [NL.LenhVao("csv", 1, 1.0, 1, "", 1.0), NL.LenhVao("csv", 2, 1.004, 1, "", 1.0)]
    q = TK.QuanLi(lot0=1.0, tp_pct=0.005)
    q.mot_ro_moi_chieu = True
    hs = TK.HoSoPhi(ma="EURUSD", spread_gio=[0.0] * 24)
    kq = TK.chay_tk({"": df}, ev, q, TK.TaiKhoan(von=1000.0, don_bay=500.0), {"": hs}, ghi_lenh=True)
    assert len(kq["lenh"]) == 1        # ro 1 cham TP trong nen 2 -> lenh vao o OPEN nen 2 bi bo (EA: ro con mo)


def test_doc_htm_ky_va_lai_nam_theo_ky():
    f = KQ / "od_skea0ca971ac32_XM_CSV.htm"
    if not f.exists():
        pytest.skip("thieu bao cao mau")
    r = OD.doc_htm(f)
    assert r["symbol"] == "GBPNZDmicro" and r["tu_bc"] == "2023.12.28" and r["den_bc"] == "2026.10.01"
    ph = OD._cot_loi_mt5(r["net"], r["dd"], 1000.0, OD._nam_bc(r, {}, OD.cau_hinh()))
    assert ph["dat"] and 2.7 < ph["so_nam"] < 2.8 and ph["lai_kep_pct_nam"] < ph["lai_pct_nam"]


def _viec(ten):
    for x in (GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl").read_text(encoding="utf-8").splitlines():
        if ('"%s"' % ten) in x:
            v = json.loads(x)
            if v["ten"] == ten:
                return v
    pytest.skip("thieu viec %s" % ten)


def test_doi_chieu_lai_mt5_tu_htm_va_sai_symbol():
    v = _viec("od_skst299b0817f66d4096_XM_CSV")
    r = OD.doi_chieu_viec(v, KQ)
    assert r["ket_luan"] == "SAI_SYMBOL" and r["lai_mt5"] == pytest.approx(-967.16)    # CSV cong duoc +332
    assert r["so_khop"] > 0                                                              # lot 0,30 x 100 = 30
    assert OD.he_so_hop_dong("EURUSD#", "EURUSDmicro") == 100.0 and OD.he_so_hop_dong("EURUSDmicro", "EURUSDmicro") == 1.0
    v2 = _viec("od_skea0ca971ac32_XM_CSV")
    r2 = OD.doi_chieu_viec(v2, KQ)
    assert r2["lai_mt5"] == pytest.approx(4533.59) and abs(r2["lai_python"] - r2["lai_mt5"]) < 1500   # truoc: 12.296 vs 4.591


def test_chay_lai_bo_so_cai_cu(tmp_path, monkeypatch):
    p = tmp_path / "cl.json"
    OD.ghi_chay_lai({"od_a": "sai_symbol"}, p)
    monkeypatch.setattr(SV, "CHAY_LAI_OD", p)
    cl = SV.doc_chay_lai()
    assert "od_a" in cl and cl["od_a"]["ly_do"] == "sai_symbol"
    v = {"ea": "XL", "ma": "EURUSDmicro", "tf": "H1", "ts": {"a": 1}, "pha": "KIEM_CSV", "nguon": "ong_dan", "ten": "od_a",
         "diem": 60, "san": "XM"}
    hang = tmp_path / "h.jsonl"
    hang.write_text(json.dumps(v) + "\n", encoding="utf-8")
    monkeypatch.setattr(SV, "HANG_CHO_OD", hang)
    monkeypatch.setattr(SV, "tu_ong_dan", lambda p=hang, san=None: [dict(v)])
    sc = [dict(v, luc="2026-10-19T23:00:00", net=1.0)]
    out = SV.lay_viec(5, so_cai=sc, san="Exness2", hai_tang=False)
    assert [x["ten"] for x in out] == ["od_a"]                            # dong so cai cu (truoc luc danh dau) bi bo


# ------------------------------------------------------------------ hai tang
def test_hai_tang_lay_viec(monkeypatch):
    v = {"ea": "XL", "ma": "EURUSDmicro", "tf": "H1", "ts": {"a": 1}, "pha": "KIEM_CSV", "nguon": "ong_dan", "ten": "od_b",
         "diem": 60, "san": "XM", "toi_uu": {}}
    monkeypatch.setattr(SV, "tu_ong_dan", lambda p=None, san=None: [dict(v)])
    monkeypatch.setattr(SV, "doc_chay_lai", lambda p=None: {})
    o = SV.lay_viec(1, so_cai=[], san="ExnessX", hai_tang=True)
    assert o[0]["tang"] == 1 and "Model=1" in SV.ini_ong_dan(o[0], "od_b_T1", "")
    assert "Model=4" in SV.ini_ong_dan(dict(v), "od_b", "")
    qua = dict(v, tang=1, tang1_qua=True, net=5.0, luc="x")
    o2 = SV.lay_viec(1, so_cai=[qua], san="ExnessX", hai_tang=True)
    assert o2[0].get("tang") == 2 and o2[0]["diem"] >= 360
    truot = dict(v, tang=1, tang1_qua=False, net=-5.0, luc="x")
    assert SV.lay_viec(1, so_cai=[truot], san="ExnessX", hai_tang=True) == []
    assert SV.lay_viec(1, so_cai=[qua], san="ExnessX", hai_tang=True, chi_tang1=True) == []
    xong = dict(v, net=3.0, luc="y")                                      # da co real tick (so cai cu) -> khong chay lai
    assert SV.lay_viec(1, so_cai=[xong], san="ExnessX", hai_tang=True) == []


def test_phan_xu_tang1(monkeypatch):
    assert QS.phan_xu_tang1({"net": -10.0, "dd": "500 (40.0%)"})[0] is False
    assert QS.phan_xu_tang1({"net": 10.0, "dd": "1 500.00 (97.5%)"})[0] is False
    assert QS.phan_xu_tang1({"net": 10.0, "dd": "500 (60.0%)"})[0] is True
    assert QS.phan_xu_tang1({"net": None, "dd": None})[0] is True
    monkeypatch.setenv("BRAIN_TANG1_DD_MAX", "50")
    assert QS.phan_xu_tang1({"net": 10.0, "dd": "500 (60.0%)"})[0] is False


# ------------------------------------------------------------------ slot / o dia / RAM
def test_slot_theo_bien_moi_truong(monkeypatch):
    assert QS.ds_slot()[:2] == [r"D:\mt5_tester\p1", r"C:\mt5_tester\p7"]
    monkeypatch.setenv("BRAIN_SLOTS", r"E:\a; D:\b")
    assert QS.ds_slot() == [r"E:\a", r"D:\b"]
    assert QS.la_ssd(r"D:\b") and not QS.la_ssd(r"E:\a") and QS.san_trong(r"D:\b") == 6.0


def test_dam_bao_cho_don_theo_bac(tmp_path, monkeypatch):
    s = tmp_path / "p1"
    (s / "logs").mkdir(parents=True); (s / "logs" / "a.log").write_bytes(b"x" * 100)
    (s / "bases" / "XM" / "ticks").mkdir(parents=True); (s / "bases" / "XM" / "ticks" / "t.dat").write_bytes(b"x" * 100)
    (s / "bases" / "XM" / "history").mkdir(parents=True)
    monkeypatch.setattr(QS, "o_cua", lambda x: "D")
    trong = {"gb": 5.0}

    class U:
        pass

    def du(_):
        u = U()
        u.free = trong["gb"] * 1024 ** 3
        return u
    goi = []

    def don(slot, bac):
        goi.append(bac)
        if bac == 1:
            trong["gb"] = 7.0
        return QS.BAC_DON and 0
    monkeypatch.setattr(QS, "don_bac", don)
    assert QS.dam_bao_cho(str(s), [str(s)], log=lambda *a: None, disk_usage=du)
    assert goi == [0, 1]                                  # dung sau bac tick, khong xoa lich su
    trong["gb"] = 1.0; goi.clear()
    monkeypatch.setattr(QS, "don_bac", lambda slot, bac: goi.append(bac) or 0)
    assert not QS.dam_bao_cho(str(s), [str(s)], log=lambda *a: None, disk_usage=du) and goi == [0, 1, 2]


def test_don_bac_va_sau_viec(tmp_path):
    s = tmp_path / "p1"
    (s / "logs").mkdir(parents=True); (s / "logs" / "a.log").write_text("x")
    (s / "bases" / "XM" / "ticks").mkdir(parents=True); (s / "bases" / "XM" / "ticks" / "t.dat").write_text("x")
    (s / "MQL5" / "Profiles" / "Tester").mkdir(parents=True)
    (s / "od_x.ini").write_text("i"); (s / "MQL5" / "Profiles" / "Tester" / "od_x.set").write_text("s")
    com = tmp_path / "Common"; com.mkdir()
    for d in ("od_x_vao.csv", "od_x_vao.csv_lenh_mt5.csv", "od_x_vao.csv_gia.csv", "khac.csv"):
        (com / d).write_text("c")
    QS.don_sau_viec(str(s), "od_x", com, r"reports\ong_dan\viec_mt5\t\od_x_vao.csv")
    assert not (s / "od_x.ini").exists() and not (s / "logs" / "a.log").exists()
    assert (s / "bases" / "XM" / "ticks" / "t.dat").exists()                       # tick giu lai
    assert sorted(p.name for p in com.iterdir()) == ["khac.csv"]


def test_du_ram(monkeypatch):
    assert QS.du_ram(1, ram=4.5)[0] and not QS.du_ram(2, ram=4.5)[0] and not QS.du_ram(1, ram=3.0)[0]
    monkeypatch.setenv("BRAIN_RAM_TANG2_GB", "4")
    assert QS.du_ram(2, ram=4.5)[0]


def test_chuyen_bao_cao_cu(tmp_path):
    rep, lanh = tmp_path / "rep", tmp_path / "lanh"
    rep.mkdir()
    (rep / "cu.htm").write_text("a"); os.utime(rep / "cu.htm", (time.time() - 3600,) * 2)
    (rep / "moi.htm").write_text("b")
    assert QS.chuyen_bao_cao_cu(rep, lanh, truoc=time.time() - 60, log=lambda *a: None) == 1
    assert (lanh / "cu.htm").exists() and (rep / "moi.htm").exists()


# ------------------------------------------------------------------ robots
def test_robots_disallow_dau_hoi_khong_cam_ca_trang():
    q = QuyTacRobots("User-agent: *\nCrawl-delay: 10\nDisallow: /?\nDisallow: /*.pdf\nDisallow: /blog/*?*\n"
                     "Allow: /blog/ok?x\nUser-agent: badbot\nDisallow: /\n", "TheBrainSeeker/1.0")
    u = "https://www.earnforex.com"
    assert q.can_fetch("x", u + "/metatrader-expert-advisors/")
    assert not q.can_fetch("x", u + "/?s=ea") and not q.can_fetch("x", u + "/a/b.pdf")
    assert not q.can_fetch("x", u + "/blog/post?p=1") and q.can_fetch("x", u + "/blog/ok?x")
    assert q.tre_giay == 10.0
    assert not QuyTacRobots("User-agent: badbot\nDisallow: /\n", "badbot/2").can_fetch("b", u + "/x")
    assert QuyTacRobots("User-agent: *\nDisallow:\n", "a").can_fetch("a", u + "/x")


# ------------------------------------------------------------------ bao cao phien
def test_ung_vien_va_day_git_chi_tep_bao_cao(tmp_path, monkeypatch):
    if not (KQ / "od_skea0ca971ac32_XM_CSV.htm").exists():
        pytest.skip("thieu bao cao mau")
    ds = BCP.ung_vien()
    r = {x["ten"]: x for x in ds}
    assert r["od_skea0ca971ac32_XM_CSV"]["ket_luan"] == "ĐẠT"
    assert r["od_skst299b0817f66d4096_XM_CSV"]["ket_luan"] == "CHƯA ĐO ĐƯỢC"            # sai symbol
    tep = BCP.ghi_ung_vien(ds, tmp_path / "UNG_VIEN.md")
    assert "%/năm" in Path(tep).read_text(encoding="utf-8")
    lenh = []

    class R:
        returncode, stdout, stderr = 1, "", ""

    def chay(a, **k):
        lenh.append(a)
        return R()
    goc_phien = BCP.GOC / "reports" / "phien" / "PHIEN_TEST.md"
    BCP.day_git([goc_phien, BCP.GOC / "data" / "bi_mat.txt", BCP.GOC / "config" / "x.json"], "t", chay=chay)
    for a in lenh:
        assert not any("data/" in str(x) or "config" in str(x) for x in a)


# ------------------------------------------------------------------ bo dieu phoi tai nguyen (09:31)
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("dieu_phoi_may_nha", GOC / "may_nha_toi_nay" / "dieu_phoi_may_nha.py")
DP = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(DP)              # ten module rieng: goc repo da co dieu_phoi.py khac (qwen)

CFG_DP = DP.cau_hinh(GOC / "config" / "dieu_phoi.json")


def _d(**k):
    d = {"ram_trong_gb": 16.0, "cpu_pct": 40.0, "slot_ban": 0, "tai_ve_trong_gb": 200.0}
    d.update(k)
    return d


def test_dp_muc_mt5_theo_ram_va_game():
    m = DP.muc_mt5(_d(), CFG_DP)
    assert m["tong"] == 5 and m["tang2"] == 3 and m["nang_moi"]
    m = DP.muc_mt5(_d(ram_trong_gb=7.0), CFG_DP)                 # du 3 GB: 2 viec nhe, 1 real tick
    assert m["tong"] == 2 and m["tang2"] == 1
    m = DP.muc_mt5(_d(ram_trong_gb=3.5), CFG_DP)
    assert m["tong"] == 0 and not m["nang_moi"] and "< 4.0" in m["ly_do"]
    m = DP.muc_mt5(_d(game="League of Legends.exe"), CFG_DP)      # 09:50: khong giam tai theo game
    assert m["tong"] == 5 and m["tang2"] == 3
    m = DP.muc_mt5(_d(cpu_pct=96.0), CFG_DP)
    assert m["tong"] == 1 and "CPU" in m["ly_do"]
    assert DP.muc_mt5(_d(cpu_pct=90.0), CFG_DP)["tong"] == 5
    m = DP.muc_mt5(_d(ram_trong_gb=6.0, slot_ban=3), CFG_DP)     # viec dang chay giu nguyen, chi them theo RAM con du
    assert m["tong"] == 4
    assert QS.slot_toi_da(True, muc={"tong": 1, "tang2": 0}) == (1, 0)
    assert QS.slot_toi_da(False, muc={"tong": 4, "tang2": 2}) == (2, 2)


def test_dp_khong_con_giam_tai_game_va_co_tat(tmp_path, monkeypatch):
    assert not hasattr(DP, "dang_choi") and "game" not in CFG_DP
    assert CFG_DP["cpu_cao_pct"] >= 90 and CFG_DP["uu_tien"] == "Normal"
    monkeypatch.setattr(DP, "CO_TAT", tmp_path / "TAT_THE_BRAIN.co")
    assert not DP.co_lenh_tat()
    (tmp_path / "TAT_THE_BRAIN.co").write_text("x")
    assert DP.co_lenh_tat()
    monkeypatch.setattr(DP, "PID_DIR", tmp_path / "pid")
    DP.ghi_pid("dich_llm", 1234)
    assert (tmp_path / "pid" / "dich_llm.pid").read_text() == "1234"


def test_429_lui_va_thu_them(monkeypatch):
    monkeypatch.setenv("AIBOX_API_KEY", "khoa-gia-test")
    tra = [(429, "rate limit, slow down")] * 4 + [(200, {"choices": [{"message": {"content": "ok"}}], "usage": {}})]
    lan = []

    def cl(url, h, body, timeout):
        lan.append(1)
        return tra[len(lan) - 1]
    c = dict(LLM.MAC_DINH, so_lan_thu_lai=2)
    r = LLM.goi("x", client=cl, c=c)
    assert r["trang_thai"] == "OK" and len(lan) == 5 and LLM.THONG_KE.get("so_lan_429", 0) >= 4
    lan.clear()
    tra[:] = [(500, "loi")] * 5
    assert LLM.goi("x", client=cl, c=c)["trang_thai"] == "LOI" and len(lan) == 2 * (1 + bool(LLM.duong(c).get("model_du_phong")))


def test_dp_seeker_chi_chay_khi_hang_can_va_o_du():
    tt = {}
    now = time.time()
    ok, ly = DP.nen_chay_seeker(_d(), CFG_DP, 150, 900, tt, False, now)
    assert not ok and "con du" in ly
    ok, ly = DP.nen_chay_seeker(_d(), CFG_DP, 5, 900, tt, False, now)
    assert ok
    assert not DP.nen_chay_seeker(_d(tai_ve_trong_gb=12.0), CFG_DP, 5, 900, tt, False, now)[0]
    assert not DP.nen_chay_seeker(_d(), CFG_DP, 5, 0, {"seeker_luc_xong": now - 60}, False, now)[0]
    assert not DP.nen_chay_seeker(_d(), CFG_DP, 5, 0, {"seeker_gb_tong": 61}, False, now)[0]
    assert not DP.nen_chay_seeker(_d(ram_trong_gb=2.0), CFG_DP, 5, 0, tt, False, now)[0]


def test_dp_dich_song_song():
    now = time.time()
    assert DP.nen_chay_dich(_d(), CFG_DP, 10, False, 0, now)[0]
    assert not DP.nen_chay_dich(_d(), CFG_DP, 0, False, 0, now)[0]
    assert not DP.nen_chay_dich(_d(), CFG_DP, 10, True, 0, now)[0]
    assert not DP.nen_chay_dich(_d(), CFG_DP, 10, False, now + 100, now)[0]


def test_dp_don_tho_giu_tep_the_tro_toi(tmp_path):
    g = tmp_path / "tai_ve"
    (g / "a").mkdir(parents=True)
    (g / "a" / "x.zip").write_bytes(b"z" * 10)
    (g / "a" / "giu.rar").write_bytes(b"r" * 10)
    (g / "a" / "ea.mq4").write_bytes(b"m" * 5000)
    (g / "a" / "ea_ban_sao.mq4").write_bytes(b"m" * 5000)
    (g / "a" / "lon.ex4").write_bytes(b"e" * (6 * 1024 * 1024))
    (g / "a" / "nho.ex4").write_bytes(b"e" * 100)
    cu = time.time() - 7200
    for p in (g / "a").iterdir():
        os.utime(p, (cu, cu))
    tc = {str(DP.thu_muc_that(g / "a" / "giu.rar")).lower(), str(DP.thu_muc_that(g / "a" / "ea.mq4")).lower()}
    kq = DP.don_tho(g, CFG_DP, tc, log=lambda *a: None)
    con = sorted(p.name for p in (g / "a").iterdir())
    assert con == ["ea.mq4", "giu.rar", "nho.ex4"] and kq["xoa"] == 3 and kq["trung"] == 1
    (g / "moi.zip").write_bytes(b"z")                            # moi tai (< 30 phut) -> chua xoa
    DP.don_tho(g, CFG_DP, set(), log=lambda *a: None)
    assert (g / "moi.zip").exists()


def test_dp_tom_tat_su_dung(tmp_path):
    p = tmp_path / "su.jsonl"
    for i, (cpu, ban) in enumerate([(50, 2), (70, 4)]):
        DP._ghi_dong(p, {"luc": DP._bay_gio(), "cpu_pct": cpu, "ram_trong_gb": 8.0, "ram_tong_gb": 32.0, "slot_tong": 5,
                         "slot_ban": ban, "o_trong_gb": {"D": 50.0}, "tai_ve_trong_gb": 300.0,
                         "dang_chay": {"dich_llm": True, "seeker": None}})
    t = DP.tom_tat_su_dung(time.time() - 3600, p)
    assert t["cpu_pct"] == 60.0 and t["slot_ban_pct"] == 60.0 and t["dich_llm_pct"] == 100.0
    assert DP.tom_tat_su_dung(time.time() + 10, p) is None


# ------------------------------------------------------------------ chon model LLM manh (09:56)
from nhan import chon_model_llm as CM  # noqa: E402

CFG_LD = json.loads((GOC / "config" / "llm_dich.json").read_text(encoding="utf-8"))


def test_xep_hang_model_bo_flash():
    ds = ["qwen3.7-flash", "qwen3.6-flash", "qwen3-coder-plus", "deepseek-v3.2", "deepseek-v3.1", "qwen3-max",
          "qwen-plus", "deepseek-r1", "text-embedding-v3", "qwen3-vl-plus"]
    cfg = dict(CFG_LD, uu_tien=["^deepseek-v3\\.[0-9]", "^qwen3(\\.[0-9])?-coder(-plus)?$", "^qwen3(\\.[0-9])?-max",
                                "^deepseek-r1", "^qwen-plus", "^qwen3(\\.[0-9])?-plus"])
    xh = CM.xep_hang(ds, cfg)
    assert xh[:2] == ["deepseek-v3.2", "deepseek-v3.1"] and "qwen3.7-flash" not in xh and "qwen3-vl-plus" not in xh
    assert xh.index("qwen3-coder-plus") < xh.index("qwen3-max") < xh.index("deepseek-r1") < xh.index("qwen-plus")


def test_chon_thang_theo_dat_roi_toc_do():
    kq = [{"model": "a", "dat": 12, "ok_json": 19, "giay_tb": 40}, {"model": "b", "dat": 15, "ok_json": 18, "giay_tb": 90},
          {"model": "c", "dat": 15, "ok_json": 18, "giay_tb": 60}, {"model": "d", "dat": 0, "ok_json": 0, "giay_tb": 1}]
    assert CM.chon(kq) == ("c", "b")
    assert CM.chon([{"model": "d", "dat": 0, "ok_json": 0, "giay_tb": 1}]) == ("", "")


def test_liet_ke_khong_lo_khoa(monkeypatch):
    k = "sk-khoabimat0123456789"
    monkeypatch.setenv("AIBOX_API_KEY", k)
    ds, gc = CM.liet_ke(get=lambda url, khoa: (200, {"data": [{"id": "deepseek-v3.2"}, {"id": "qwen3.7-flash"}]}))
    assert ds == ["deepseek-v3.2", "qwen3.7-flash"] and k not in gc
    ds, gc = CM.liet_ke(get=lambda url, khoa: (401, "bad key %s" % khoa))
    assert ds == [] and k not in gc


def test_cau_hinh_llm_dich_khoa_model_khong_lui_flash(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "qwen.json").write_text(json.dumps({"model": "qwen3.7-flash", "model_du_phong": "qwen3.6-flash"}))
    c = LLM.cau_hinh(tmp_path)
    assert c["model"] == "qwen3.7-flash"
    (tmp_path / "config" / "llm_dich.json").write_text(json.dumps({"model": "deepseek-v3.2", "max_tokens": 32000,
                                                                   "timeout_giay": 900, "tran_ma": 60000}))
    c = LLM.cau_hinh(tmp_path)
    assert c["model"] == "deepseek-v3.2" and c["model_du_phong"] == "" and c["tran_ma"] == 60000 and c["timeout_giay"] == 900


def test_du_phong_chi_khi_5xx(monkeypatch):
    monkeypatch.setenv("AIBOX_API_KEY", "khoa-gia-test")
    c = dict(LLM.MAC_DINH, model="manh", model_du_phong="manh2", chi_du_phong_khi_5xx=True, so_lan_thu_lai=2)
    goi = []

    def cl(tra):
        def f(url, h, body, timeout):
            m = json.loads(body.decode())["model"]
            goi.append(m)
            return tra(m)
        return f
    ok = (200, {"choices": [{"message": {"content": "x"}}], "usage": {}})
    r = LLM.goi("x", client=cl(lambda m: (503, "busy") if m == "manh" else ok), c=c)
    assert r["trang_thai"] == "OK" and goi == ["manh", "manh", "manh2"]
    goi.clear()
    r = LLM.goi("x", client=cl(lambda m: (403, "quota exceeded") if m == "manh" else ok), c=c)
    assert r["trang_thai"] == "LOI" and goi == ["manh"]                 # het quota: KHONG lui sang model khac


def test_ab_voi_client_gia(monkeypatch):
    monkeypatch.setenv("AIBOX_API_KEY", "khoa-gia-test")
    from nhan import dich_llm as DL
    monkeypatch.setattr(DL, "gia_mau", lambda cfg=None, n=3000: (_gia(1500), "gia"))
    sp = json.dumps({"spec": [{"ten": "a", "chieu": 1, "vao": [{"trai": {"chi_bao": "sma", "n": 10}, "phep": "cheo_len",
                                                                 "phai": {"chi_bao": "sma", "n": 30}}]}], "python": ""})

    def cl(url, h, body, timeout):
        m = json.loads(body.decode())["model"]
        return (200, {"choices": [{"message": {"content": sp if m == "tot" else "khong json"}}], "usage": {"completion_tokens": 10}})
    mau = [{"id": str(i), "vb": "void OnTick(){}", "nn": "MQL4"} for i in range(3)]
    kq = CM.ab(["tot", "do"], mau, {"ab": {"luong": 2}}, client=cl)
    assert [x["dat"] for x in kq] == [3, 0] and CM.chon(kq)[0] == "tot"


def test_hop_cat_numpy_import_noi_bo_nhung_cam_os():
    df = _gia()
    ma = ("def tin_hieu(df):\n    import numpy as np\n    c = df['close'].values\n    w = np.arange(1, 6)\n"
          "    out = np.zeros(len(c))\n    for i in range(5, len(c)):\n        v = np.dot(c[i - 5:i], w) / w.sum()\n"
          "        out[i] = 1 if c[i - 1] > v else -1\n    return out\n")
    assert DL.kiem_tra({"python": ma}, df)["dat"]              # truoc: KeyError '__import__' trong np.dot
    assert HC.chay("def tin_hieu(df):\n    return __import__('os')", df)["ok"] is False
