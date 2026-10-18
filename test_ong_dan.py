# -*- coding: utf-8 -*-
"""test_ong_dan.py - kiem phan moi 18/10/2026: nguong chung, engine cap tai khoan (chay_tk), nguon_lenh, kho co che,
cau LLM (khong khoa), gio san (D8), loc terminal tester (D7), ong dan (tung buoc + chay tiep)."""
import json
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import pytest

from nhan import nguong as NG
from nhan import tai_khoan as TK
from nhan import nguon_lenh as NL
from nhan import kho_co_che as KHO
from nhan import gio_san as GS
from nhan import cau_llm as LLM
from nhan import khoa_tester as KT
from nhan import ong_dan as OD


def _df(gia, tu="2024-01-01 00:00"):     # 2024-01-01 la thu Hai
    gia = np.asarray(gia, float)
    i = pd.date_range(tu, periods=len(gia), freq="h")
    return pd.DataFrame({"open": gia, "high": gia, "low": gia, "close": gia}, index=i)


def _phi(**kw):
    x = dict(ma="EURUSD", quy_doi_usd=1.0, point=1e-5, hop_dong=1000.0, spread_gio=[0.0] * 24, lot_max=1000.0)
    x.update(kw)
    return TK.HoSoPhi(**x)


# ------------------------------------------------------------------ nguong
def test_nguong_mot_cho_hai_tang():
    assert NG.sut_giam_toi_da("loc_python") == 65 and NG.lai_toi_thieu("loc_python") == 15
    assert NG.sut_giam_toi_da("cuoi") == 80 and NG.lai_toi_thieu("cuoi") == 10
    assert NG.dat(16, 64)["dat"] and not NG.dat(15, 10)["dat"] and not NG.dat(30, 65)["dat"]
    assert not NG.dat(40, 20, so_stop_out=1)["dat"]
    assert NG.dat(10, 80, "cuoi")["dat"] and not NG.dat(None, 5)["dat"]


def test_cham_diem_va_sinh_viec_doc_cung_nguong():
    from nhan import cham_diem as CD
    import sys
    sys.path.insert(0, str(OD.GOC / "mt5tools"))
    import sinh_viec as SV
    assert CD.MUC_LAI == NG.lai_toi_thieu("cuoi") and CD.TRAN_SUT_GIAM == NG.sut_giam_toi_da("cuoi")
    assert SV.LAI_TOI_THIEU == NG.lai_toi_thieu("cuoi") and SV.SUT_GIAM_TOI_DA == NG.sut_giam_toi_da("cuoi")


# ------------------------------------------------------------------ chay_tk
def test_tp_chot_lai():
    g = [1.0] * 5 + [1.0 + 0.0001 * k for k in range(1, 40)]
    ev = [TK.LenhVao("a", 1, 1.0, 1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df(g)}, ev, TK.QuanLi(lot0=1.0, tp_pct=0.001), TK.TaiKhoan(von=1000), {"EURUSD": _phi()})
    assert kq["so_tp"] == 1 and kq["lai_tien"] > 0.9 and kq["nhan"] == "MÔ PHỎNG"


def test_thieu_ky_quy_bi_tu_choi():
    ev = [TK.LenhVao("a", 1, 1.0, 1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df([1.0] * 30)}, ev, TK.QuanLi(lot0=1.0, tp_pct=0.01),
                    TK.TaiKhoan(von=10, don_bay=1), {"EURUSD": _phi()})
    assert kq["tu_choi_ky_quy"] >= 1 and kq["so_lenh"] == 0


def test_stop_out_khi_lo_qua_von():
    g = [1.0] * 3 + list(np.linspace(1.0, 0.98, 30))
    ev = [TK.LenhVao("a", 1, 1.0, 1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df(g)}, ev, TK.QuanLi(lot0=20.0, tp_pct=0.05), TK.TaiKhoan(von=100, don_bay=500),
                    {"EURUSD": _phi()})
    assert kq["so_stop_out"] >= 1 and kq["sut_giam_pct"] > 50


def _swap(tu):
    ev = [TK.LenhVao("a", 1, 1.0, 1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df([1.0] * 25, tu)}, ev, TK.QuanLi(lot0=1.0, tp_pct=0.5), TK.TaiKhoan(von=1000),
                    {"EURUSD": _phi(swap_mua_diem=-10.0, ngay_x3=2)})
    return kq["phi"]["swap"]


def test_swap_x3_dem_thu_tu():
    thuong = _swap("2024-01-02 12:00")      # giu qua dem thu Ba -> thu Tu
    ba = _swap("2024-01-03 12:00")          # giu qua dem thu Tu -> thu Nam (x3)
    assert thuong > 0 and ba == pytest.approx(3 * thuong, rel=1e-6)


def test_lenh_ban_tra_spread():
    ev = [TK.LenhVao("a", 1, 1.0, -1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df([1.0] * 30)}, ev, TK.QuanLi(lot0=1.0, tp_pct=0.01), TK.TaiKhoan(von=1000),
                    {"EURUSD": _phi(spread_gio=[0.0002] * 24)})
    assert kq["so_lenh"] == 1 and kq["phi"]["spread"] > 0 and kq["von_cuoi"] < 1000


def test_hedge_khoa_khi_lo():
    g = [1.0] * 3 + list(np.linspace(1.0, 0.95, 60))
    ev = [TK.LenhVao("a", 1, 1.0, 1, "EURUSD", None)]
    kq = TK.chay_tk({"EURUSD": _df(g)}, ev, TK.QuanLi(lot0=2.0, tp_pct=0.01, hedge_khi_lo_pct=5.0),
                    TK.TaiKhoan(von=1000, don_bay=500), {"EURUSD": _phi()})
    assert kq["so_khoa"] >= 1 and kq["so_stop_out"] == 0


# ------------------------------------------------------------------ nguon_lenh
def test_tin_hieu_brain_mrz_va_vao_o_nen_sau():
    g = [1.0 + 0.001 * np.sin(k / 3) for k in range(80)] + [0.95] + [1.0] * 10
    df = _df(g)
    s = NL.tin_hieu_brain(df, "MRZ", n=20, nguong_z=2.0)
    assert s[80] == 1
    ev = NL.lenh_vao(df, s, "x", "EURUSD")
    assert any(e.chi_so == 81 for e in ev)


def test_bo_loc_gio_va_doi_khung():
    df = _df([1.0] * 48)
    ok = NL.bo_loc_gio(df, 2, 23)
    assert not ok[22] and ok[2] and NL.doi_khung(df, "H4").shape[0] == 12


# ------------------------------------------------------------------ kho co che
def test_kho_co_che_them_va_lay(tmp_path):
    tep = tmp_path / "kho.sqlite"
    a = KHO.co_che("bo_loc", "loc thu", tham={"kieu": "gio", "tu": 7, "den": 20}, tu_the="t1")
    assert KHO.them([a, a], tep) == 1 and KHO.them([a], tep) == 0
    assert [x["ten"] for x in KHO.lay("bo_loc", tep)] == ["loc thu"]
    with pytest.raises(ValueError):
        KHO.co_che("sai", "x")


# ------------------------------------------------------------------ LLM, gio san, terminal
def test_llm_khong_khoa_bo_qua(monkeypatch):
    monkeypatch.delenv("AIBOX_API_KEY", raising=False)
    assert not LLM.co_khoa() and LLM.boc_tach("int OnTick(){}")["trang_thai"] == "CHUA_CHAY_DUOC"


def test_gio_san_exness_gmt0():
    assert GS.cam_doi_ngay("Exness-MT5Real8") == (20, 0) and GS.cam_doi_ngay("XMGlobal-MT5 6") == (23, 2)
    assert 21 in GS.gio_doi_ngay("Exness") and 23 in GS.gio_doi_ngay("XM")


def test_chi_giet_terminal_tester(monkeypatch):
    monkeypatch.setenv("BRAIN_TERMINAL_GIAO_DICH", r"C:\Program Files\XM Global MT5")
    assert KT.la_terminal_tester(r"D:\mt5_tester\p1\terminal64.exe", "terminal64.exe /portable /config:x.ini")
    assert not KT.la_terminal_tester(r"C:\Program Files\XM Global MT5\terminal64.exe", "/config:x.ini")
    assert not KT.la_terminal_tester(r"C:\Program Files\Exness MT5\terminal64.exe", "terminal64.exe")


# ------------------------------------------------------------------ ong dan
@pytest.fixture
def od_tam(tmp_path, monkeypatch):
    rng = np.random.default_rng(1)
    n = 24 * 400
    g = 0.9 + np.cumsum(rng.normal(0, 0.0008, n))
    i = pd.date_range("2016-01-04", periods=n, freq="h")
    pd.DataFrame({"time": i, "open": g, "high": g + 0.0005, "low": g - 0.0005, "close": g}).to_csv(tmp_path / "x.csv", index=False)
    cfg = json.loads(OD.CAU_HINH.read_text(encoding="utf-8"))
    cfg.update(du_lieu={"AUDCAD": str(tmp_path / "x.csv")}, khung=["H1"], tu_ngay="2016-01-01")
    (tmp_path / "c.json").write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(OD, "CAU_HINH", tmp_path / "c.json")
    monkeypatch.setattr(OD, "RA", tmp_path / "ra")
    monkeypatch.setattr(OD, "HANG_CHO", tmp_path / "ra" / "hang.jsonl")
    monkeypatch.setattr(OD, "VIEC", tmp_path / "ra" / "viec")
    monkeypatch.setattr(OD, "KET_QUA_MT5", tmp_path / "ra" / "kq")
    monkeypatch.setattr(KHO, "KHO", tmp_path / "kho.sqlite")
    monkeypatch.setattr(KHO, "TOM_TAT", tmp_path / "ra" / "KHO.md")
    OD._GIA.clear()
    cn = OD._db(tmp_path / "tt.sqlite")
    t = dict(OD.THE_BRAIN[0], loai="he_hoan_thien", uu_tien=0, duong_dich="noi_bo")
    with cn:
        OD._luu(cn, t, "quyet_dinh", "NOI_BO")
    return cn, tmp_path


def test_phan_loai_uu_tien_he_hoan_thien():
    assert OD.phan_loai_mot({"nen_tang": "BRAIN"})[:2] == ("he_hoan_thien", 0)
    assert OD.phan_loai_mot({"loai_kiem_ke": "thu_vien", "nguon": {}})[0] == "tien_ich"


def test_toi_uu_chay_tiep_khong_lam_lai(od_tam):
    cn, _ = od_tam
    OD.buoc_toi_uu(cn, 1, 2, in_ra=lambda *_: None)
    assert cn.execute("SELECT COUNT(*) FROM thu").fetchone()[0] == 2
    with cn:     # gia lap dung giua chung: the quay lai buoc truoc, cac phep thu da luu van con
        cn.execute("UPDATE the SET buoc='quyet_dinh'")
    OD.buoc_toi_uu(cn, 1, 3, in_ra=lambda *_: None)
    assert cn.execute("SELECT COUNT(*) FROM thu").fetchone()[0] == 3
    tt = OD.cac_the(cn, "toi_uu")[0]
    assert tt[3]["so_thu"] == 3 and tt[3]["tot_nhat"]["kq"]["nhan"] == "MÔ PHỎNG"


def test_loc_sinh_mt5_boc_doc_xml(od_tam):
    cn, tmp = od_tam
    OD.buoc_toi_uu(cn, 1, 2, in_ra=lambda *_: None)
    OD.buoc_loc(cn, in_ra=lambda *_: None)
    t, b, st, kq = OD.cac_the(cn, "loc")[0]
    assert st in ("DAT_LOC", "TRUOT_LOC")
    with cn:    # ep DAT de kiem file viec MT5 (khong phai so do)
        OD._luu(cn, t, "loc", "DAT_LOC", kq)
    assert OD.buoc_sinh_mt5(cn, in_ra=lambda *_: None, toi_da_ngoai=0) == 4      # 2 san x (KIEM, TOI_UU)
    rows = [json.loads(x) for x in OD.HANG_CHO.read_text(encoding="utf-8").splitlines()]
    toi = [r for r in rows if r["pha"] == "TOI_UU" and r["san"] == "XM"][0]
    assert toi["ma"] == "AUDCADmicro" and toi["toi_uu"] and toi["ts"]["InpTF"] == 16385
    st_ = (OD.VIEC / t["id"] / (toi["ten"] + ".set")).read_text()
    ini = (OD.VIEC / t["id"] / (toi["ten"] + ".ini")).read_text()
    assert "||Y" in st_ and ("Optimization=1" in ini or "Optimization=2" in ini) and "Leverage=1:500" in ini
    ex = [r for r in rows if r["san"] == "Exness"][0]
    assert ex["ts"]["InpGioCamTu"] == 20 and ex["tien"] == "USC"
    assert OD.buoc_sinh_mt5(cn, in_ra=lambda *_: None, toi_da_ngoai=0) == 0       # khong nhan doi
    # ket qua MT5 tra ve: XML optimizer
    OD.KET_QUA_MT5.mkdir(parents=True)
    xml = ("<Workbook><Table><Row><Cell><Data>Pass</Data></Cell><Cell><Data>Profit</Data></Cell>"
           "<Cell><Data>Equity DD %</Data></Cell></Row><Row><Cell><Data>1</Data></Cell><Cell><Data>2000</Data></Cell>"
           "<Cell><Data>40.5</Data></Cell></Row></Table></Workbook>")
    (OD.KET_QUA_MT5 / (toi["ten"] + ".xml")).write_text(xml, encoding="utf-8")
    d = OD.buoc_doc_mt5(cn, in_ra=lambda *_: None)
    assert d["DAT_CUOI"] == 1      # 2000/1000/10 nam = 20 %/nam, DD 40,5 % -> dat 80/10


def test_boc_co_che_tu_the_truot(od_tam):
    cn, _ = od_tam
    OD.buoc_toi_uu(cn, 1, 2, in_ra=lambda *_: None)
    with cn:
        cn.execute("UPDATE the SET buoc='loc', trang_thai='TRUOT_LOC'")
    OD.buoc_boc(cn, in_ra=lambda *_: None)
    vai = {c["vai_tro"] for c in KHO.lay()}
    assert {"nguon_lenh", "bo_loc", "go_lenh"} <= vai


def test_set_va_ini_cho_hang_cho_may_nha():
    import sys
    sys.path.insert(0, str(OD.GOC / "mt5tools"))
    import sinh_viec as SV
    v = {"ea": "XL", "ea_file": "BRAIN_XuLiLenh", "ma": "AUDCADmicro", "tf": "H1", "pha": "TOI_UU", "ts": {"InpTPGia": 0.002},
         "toi_uu": {"InpTPGia": [0.001, 0.0005, 0.004]}, "von": 1000, "tien": "USD"}
    assert SV.file_set_ong_dan(v) == "InpTPGia=0.002||0.001||0.0005||0.004||Y\n"
    assert "Optimization=1" in SV.ini_ong_dan(v, "od_x", "Leverage=1:500\n")


# ------------------------------------------------------------------ thu muc nhap tay
_EA = "input double Lot=0.01;\nint OnInit(){return 0;}\nvoid OnTick(){ if(iClose(_Symbol,0,1)>iOpen(_Symbol,0,1)) {} }\n"
_MT5 = ("<html><body><div>Strategy Tester Report</div><table><tr><td>Total Net Profit:</td><td>120.5</td></tr>"
        "<tr><th>Deals</th></tr>"
        "<tr><td>2016.03.01 10:00:00</td><td>2</td><td>AUDCADmicro</td><td>buy</td><td>in</td><td>0.10</td><td>0.97</td><td>2</td><td>0</td><td>0</td><td>0</td><td>1000</td><td></td></tr>"
        "<tr><td>2016.03.01 14:00:00</td><td>3</td><td>AUDCADmicro</td><td>buy</td><td>in</td><td>0.20</td><td>0.96</td><td>3</td><td>0</td><td>0</td><td>0</td><td>1000</td><td></td></tr>"
        "<tr><td>2016.03.01 18:00:00</td><td>4</td><td>AUDCADmicro</td><td>buy</td><td>in</td><td>0.40</td><td>0.95</td><td>4</td><td>0</td><td>0</td><td>0</td><td>1000</td><td></td></tr>"
        "<tr><td>2016.03.02 09:00:00</td><td>5</td><td>AUDCADmicro</td><td>sell</td><td>out</td><td>0.30</td><td>0.97</td><td>5</td><td>0</td><td>0</td><td>9</td><td>1009</td><td></td></tr>"
        "<tr><td>2016.03.02 09:30:00</td><td>6</td><td>AUDCADmicro</td><td>sell</td><td>in</td><td>0.10</td><td>0.97</td><td>6</td><td>0</td><td>0</td><td>0</td><td>1009</td><td></td></tr>"
        "</table><div>Profit</div></body></html>")
_MT4 = ("<html><b>Statement</b><table><tr><td>Ticket</td><td>Open Time</td><td>Type</td><td>Size</td><td>Item</td></tr>"
        "<tr><td>101</td><td>2016.05.02 08:00</td><td>sell</td><td>0.05</td><td>eurusd</td><td>1.14</td><td>0</td><td>0</td>"
        "<td>2016.05.02 12:00</td><td>1.13</td><td>0</td><td>0</td><td>0</td><td>5</td></tr></table>Profit</html>")


@pytest.fixture
def thu_muc_nhap(tmp_path, monkeypatch):
    from nhan import nhap_tay as NT
    d = tmp_path / "brain2_nhap"
    d.mkdir()
    (d / "Ua1b2c3_luoi.mq5").write_text(_EA, encoding="utf-8")
    (d / "Ua1b2c3_luoi.set").write_text("Lot=0.02||0.01||0.01||0.1||Y\nStep=150\n", encoding="utf-8")
    (d / "rieng.set").write_text("Grid=200\n", encoding="utf-8")
    (d / "bao_cao.htm").write_bytes(_MT5.encode("utf-16"))
    (d / "st_mt4.htm").write_text(_MT4, encoding="utf-8")
    (d / "trang.html").write_text("<html><pre>" + _EA.replace("<", "&lt;").replace(">", "&gt;") + "</pre></html>", encoding="utf-8")
    (d / "chi_ex.ex5").write_bytes(b"\x00binary")
    (d / "ghi_chu.txt").write_text("he thong tay", encoding="utf-8")
    monkeypatch.setattr(NT, "TACH", tmp_path / "_tach")
    monkeypatch.setenv("BRAIN_NHAP_TAY", str(d))
    return NT, d


def test_nhap_tay_doc_va_phan_loai(thu_muc_nhap):
    NT, d = thu_muc_nhap
    assert NT.thu_muc() == [d]
    ds = {Path(t["nhap_tay"]["tep"]).name: t for t in NT.quet(NT.thu_muc())}
    assert "Ua1b2c3_luoi.set" not in ds                                    # gan vao EA cung ten
    ea = ds["Ua1b2c3_luoi.mq5"]
    assert ea["nen_tang"] == "MQL5" and ea["set_goc"]["Lot"] == "0.02" and ea["nhap_tay"]["ma_url"] == "Ua1b2c3"
    assert ds["rieng.set"]["nen_tang"] == "SET"
    bc = ds["bao_cao.htm"]
    assert bc["nen_tang"] == "STATEMENT" and bc["dau_hieu"]["so_lenh_vao"] == 4
    assert {"dca", "martingale", "hedge"} <= set(bc["dau_hieu"]["ky_thuat"]) and bc["tin_hieu"]["ma"] == ["AUDCAD"]
    assert ds["st_mt4.htm"]["dau_hieu"]["ma"] == ["EURUSD"]
    tr = ds["trang.html"]
    assert tr["nen_tang"] == "MQL5" and Path(tr["nguon"]["tep"]).read_text().count("OnTick") == 1
    assert ds["chi_ex.ex5"]["chi_bien_dich"]
    assert OD.phan_loai_mot(bc)[:2] == ("he_hoan_thien", 1)
    assert OD.phan_loai_mot(ds["ghi_chu.txt"])[0] == "mo_ta"
    assert OD.quyet_dinh_mot(dict(ds["chi_ex.ex5"], loai="he_hoan_thien"))["duong_dich"] == "mt5_truc_tiep"


def test_statement_vao_chuoi_python(thu_muc_nhap, od_tam):
    NT, d = thu_muc_nhap
    cn, tmp = od_tam
    cfg = json.loads(OD.CAU_HINH.read_text(encoding="utf-8"))
    cfg["thu_muc_nhap_tay"] = []
    OD.CAU_HINH.write_text(json.dumps(cfg), encoding="utf-8")
    bc = [t for t in NT.quet(NT.thu_muc()) if t["nen_tang"] == "STATEMENT" and "AUDCAD" in t["dau_hieu"]["ma"]][0]
    bc["loai"], bc["uu_tien"], _ = OD.phan_loai_mot(bc)
    bc = OD.quyet_dinh_mot(bc)
    assert bc["duong_dich"] == "noi_bo"
    with cn:
        cn.execute("DELETE FROM the")
        OD._luu(cn, bc, "quyet_dinh", "NOI_BO")
    OD.buoc_toi_uu(cn, 1, 2, in_ra=lambda *_: None)
    tot = OD.cac_the(cn, "toi_uu")[0][3]["tot_nhat"]
    assert tot["thu"]["ma"] == "AUDCAD" and tot["kq"]["so_lenh"] >= 1


def test_url_bi_chan_ghi_danh_sach(tmp_path):
    import sys
    sys.path.insert(0, str(OD.GOC))
    from tru import seeker as SK
    r = SK.url_bi_chan(tmp_path / "U.md", toi_da_mo_tay=5)
    assert "URL_BI_CHAN_THEM" in SK.url_bi_chan.__defaults__[0]
    vb = (tmp_path / "U.md").read_text(encoding="utf-8")
    assert r["mo_tay"] <= 5 and "vượt Cloudflare" in vb and SK.ma_url("x").startswith("U")


def test_nhap_tay_csv_tin_hieu_va_zip(tmp_path, monkeypatch):
    import zipfile
    from nhan import nhap_tay as NT
    d = tmp_path / "nhap" / "mql5_signals"
    d.mkdir(parents=True)
    (d / "926651.csv").write_text(
        "Time;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit;Comment\n"
        "2016.01.04 10:00:00;Buy;0.10;AUDCAD;0.97;;;2016.01.05 10:00:00;0.98;0;0;7;\n"
        "2016.01.04 12:00:00;Sell;0.10;AUDCAD;0.97;;;2016.01.04 15:00:00;0.96;0;0;7;\n"
        "2016.01.04 13:00:00;Balance;;;;;;;;;;100;\n", encoding="utf-8")
    with zipfile.ZipFile(d / "goi.zip", "w") as z:
        z.writestr("ea/grid.mq4", "int start(){return 0;}\nvoid OnTick(){}\n")
        z.writestr("../thoat.mq5", "void OnTick(){}")
        z.writestr("chay.exe", "MZ")
    monkeypatch.setattr(NT, "TACH", tmp_path / "_tach")
    ds = NT.quet([tmp_path / "nhap"])
    csv = [t for t in ds if t["nhap_tay"]["loai_tep"] == "CSV"][0]
    assert csv["nen_tang"] == "STATEMENT" and csv["dau_hieu"]["so_lenh_vao"] == 2 and "hedge" in csv["dau_hieu"]["ky_thuat"]
    assert csv["nhap_tay"]["ten_goc"] == "926651" and csv["nhap_tay"]["nguon_tay"] == "mql5_signals"
    ten = sorted(Path(t["nhap_tay"]["tep"]).name for t in ds)
    assert "grid.mq4" in ten and "thoat.mq5" not in ten and "chay.exe" not in ten
    df = _df([1.0] * 48, "2016-01-04 00:00")
    s = NT.tin_hieu_lenh_ngoai(csv["tin_hieu"], df, "AUDCAD")
    assert s[9] == 1 and s[11] == -1 and s.sum() == 0


# ------------------------------------------------------------------ nguon Seeker da nguon + do nguoc statement (19/10/2026)
_MT4_TESTER = ("<html><title>Strategy Tester: X</title><table><tr><td>Symbol</td><td>EURJPY (Euro vs Yen)</td></tr>"
               "<tr><td>Period</td><td>1 Hour (H1)  2016.01.04 00:00 - 2016.03.01 00:00</td></tr>"
               "<tr><td>Initial deposit</td><td>1000.00</td><td>Total net profit</td><td>55.10</td></tr>"
               "<tr><td>#</td><td>Time</td><td>Type</td><td>Order</td><td>Size</td><td>Price</td></tr>"
               "<tr><td>1</td><td>2016.01.04 08:00</td><td>buy</td><td>1</td><td>0.01</td><td>130.00</td><td>0</td><td>0</td><td></td></tr>"
               "<tr><td>2</td><td>2016.01.05 08:00</td><td>buy</td><td>2</td><td>0.02</td><td>129.00</td><td>0</td><td>0</td><td></td></tr>"
               "<tr><td>3</td><td>2016.01.06 08:00</td><td>buy</td><td>3</td><td>0.04</td><td>128.00</td><td>0</td><td>0</td><td></td></tr>"
               "<tr><td>4</td><td>2016.01.07 09:00</td><td>close</td><td>1</td><td>0.01</td><td>128.90</td><td>0</td><td>0</td><td>1</td><td>1001</td></tr>"
               "<tr><td>5</td><td>2016.01.07 09:00</td><td>close</td><td>2</td><td>0.02</td><td>128.90</td><td>0</td><td>0</td><td>1</td><td>1002</td></tr>"
               "<tr><td>6</td><td>2016.01.07 09:00</td><td>t/p</td><td>3</td><td>0.04</td><td>128.90</td><td>0</td><td>0</td><td>1</td><td>1003</td></tr>"
               "<tr><td>7</td><td>2016.01.08 08:00</td><td>sell</td><td>4</td><td>0.01</td><td>129.00</td><td>0</td><td>0</td><td></td></tr>"
               "<tr><td>8</td><td>2016.01.08 12:00</td><td>t/p</td><td>4</td><td>0.01</td><td>128.50</td><td>0</td><td>0</td><td>1</td><td>1004</td></tr>"
               "</table>Profit</html>")


def test_mt4_tester_va_do_nguoc():
    from nhan import nhap_tay as NT
    df = NT.doc_lenh_html(_MT4_TESTER)
    assert len(df) == 4 and set(df["ma"]) == {"EURJPY"} and df["gia_dong"].notna().all()
    dn = NT.do_nguoc(df)
    assert dn["tang_max"] == 3 and dn["he_so_lot"] == 2.0 and dn["ty_le_buoc_nguoc"] == 1.0
    assert abs(dn["buoc_dca_pip"] - 100) < 1 and dn["gio_hoat_dong"] == [8]
    q = dn["ql_goi_y"]
    assert q["dca_toi_da"] >= 1 and q["dca_he_so_lot"] == 2.0 and 0.003 < q["tp_pct"] < 0.005
    tg = NT.so_tac_gia_bao_cao(_MT4_TESTER)
    assert tg["nhan"].startswith("SỐ TÁC GIẢ") and tg["lai_rong"] == "55.10" and tg["khung"] == "H1"


def test_doc_nguon_seeker(tmp_path, monkeypatch):
    from nhan import doc_seeker_da_nguon as SKN
    from nhan import nhap_tay as NT
    monkeypatch.setattr(NT, "TACH", tmp_path / "_tach")
    monkeypatch.setattr(SKN, "GOC", tmp_path)
    r = tmp_path / "data" / "seeker_da_nguon" / "tai_ve" / "github" / "a__b"
    (r / "EA").mkdir(parents=True)
    (r / "EA" / "GridEURJPY.mq5").write_text("input double Lot=0.01;\nvoid OnTick(){ /* grid martingale */ }\n", encoding="utf-8")
    (r / "EA" / "GridEURJPY_v1.set").write_text("Lot=0.02||0.01||0.01||0.1||Y\nTimeframe=16388\n", encoding="utf-8")
    (r / "EA" / "lib.mqh").write_text("int f(){return 1;}", encoding="utf-8")
    (r / "EA" / "StrategyTester.htm").write_text(_MT4_TESTER, encoding="utf-8")
    js = {"ung_vien": [
        {"id": "gh_a__b", "ten": "a/b", "nguon": "github", "url": "https://github.com/a/b", "loai": "ea_hoan_thien",
         "nen_tang": "mt5", "tai_san": [], "khung": ["H1"], "duong_dan_tai": ["data/seeker_da_nguon/tai_ve/github/a__b"],
         "bang_chung_lai": {"co": True, "nguon": "theo tác giả", "so": {"lai": 10}}, "tra_phi": False, "diem_uu_tien": 70},
        {"id": "sig_1", "ten": "Sig", "nguon": "mql5_signals", "url": "https://x/s/1", "loai": "lich_su_giao_dich",
         "nen_tang": "mt5", "duong_dan_tai": [], "bang_chung_lai": {"co": True, "so": {"lai_nam_quy_doi_pct": 20}}},
        {"id": "tra", "ten": "T", "url": "u", "loai": "ea_hoan_thien", "tra_phi": True, "duong_dan_tai": []}]}
    (tmp_path / "S.json").write_text(json.dumps(js), encoding="utf-8")
    (tmp_path / "S.md").write_text("## Xếp hạng ứng viên hoàn thiện đáng test nhất\n\n| # | Tên | Nguồn | URL | Chạy | Vì sao |\n"
                                   "|---|---|---|---|---|---|\n| 1 | a/b | github | https://github.com/a/b | MT5 | x |\n", encoding="utf-8")
    ds = SKN.doc(nguon=tmp_path / "S.json")
    ten = {t["id"][:6]: t for t in ds}
    assert set(ten) == {"sk_st_", "sk_ea_", "sk_uv_"}                       # tra_phi bi bo
    ea = ten["sk_ea_"]
    assert ea["seeker"]["top28"] == 1 and ea["ma_goi_y"] == ["EURJPY"] and ea["set_goc"]["Lot"] == "0.02"
    assert ea["so_tac_gia"]["nhan"].startswith("SỐ TÁC GIẢ") and ea["sets"]
    st = ten["sk_st_"]
    assert st["nen_tang"] == "STATEMENT" and st["do_nguoc"]["tang_max"] == 3 and st["ql_goi_y"]
    assert ten["sk_uv_"]["chi_doi_chieu"] and OD.phan_loai_mot(ten["sk_uv_"])[0] == "mo_ta"
    # viec MT5 cho EA ngoai: mot viec / .set, khung lay tu Timeframe=16388, ma tu ten file
    monkeypatch.setattr(OD, "GOC", tmp_path)
    v = OD.viec_ngoai(ea, {"mt5_tu": "2016.01.01", "mt5_den": "2026.10.01"})
    assert len(v) == 1 and v[0]["pha"] == "TOI_UU_SET" and v[0]["tf"] == "H4" and v[0]["ma"] == "EURJPY"
    assert v[0]["tep_box"].endswith("GridEURJPY.mq5") and v[0]["so_tac_gia"]


def test_goi_may_nha_kem_include(tmp_path, monkeypatch):
    import zipfile
    from nhan import goi_may_nha as GM
    monkeypatch.setattr(GM, "GOC", tmp_path)
    d = tmp_path / "data" / "x"
    (d / "Include").mkdir(parents=True)
    (d / "ea.mq5").write_text('#include "Include/a.mqh"\nvoid OnTick(){}\n', encoding="utf-8")
    (d / "Include" / "a.mqh").write_text('#include "b.mqh"\n', encoding="utf-8")
    (d / "Include" / "b.mqh").write_text('int b;\n', encoding="utf-8")
    (d / "ea.set").write_text("Lot=0.1\n", encoding="utf-8")
    h = tmp_path / "hang.jsonl"
    h.write_text(json.dumps({"ten": "v1", "ea": "NGOAI", "tep_box": "data/x/ea.mq5", "set_box": "data/x/ea.set"}) + "\n"
                 + json.dumps({"ten": "v2", "ea": "XL"}) + "\n", encoding="utf-8")
    r = GM.dong_goi(tmp_path / "goi", h)
    assert r["so_viec"] == 1 and r["so_file"] == 4
    with zipfile.ZipFile(r["zip"]) as z:
        n = set(z.namelist())
    assert {"data/x/ea.mq5", "data/x/Include/a.mqh", "data/x/Include/b.mqh", "data/x/ea.set", "MANIFEST.json", "HUONG_DAN.md"} <= n
