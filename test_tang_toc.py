# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "mt5tools"))
import tang_toc as TT  # noqa: E402
import sinh_viec as SV  # noqa: E402


def _v(**k):
    v = {"ten": "od_v2cn_abc_XM_CSV", "ea": "XL", "nguon": "ong_dan", "ma": "GBPNZDmicro", "tf": "H1", "pha": "V2_CAO_NGUYEN",
         "tu": "2023.12.26", "den": "2026.10.01", "von": 1000, "diem": 70,
         "ts": {"InpTPPct": 0.005, "InpBuocPct": 0.008, "InpMaxTang": 6, "InpLot0": 3.0, "InpTPATR": 0.0}}
    v.update(k); return v


def test_ram_dong(monkeypatch):
    for k in ("BRAIN_RAM_TICK_GB", "BRAIN_RAM_OHLC_GB", "BRAIN_RAM_DU_TRU_GB", "BRAIN_RAM_HE_THONG_GB", "BRAIN_GEN_AGENT_MAX"):
        monkeypatch.delenv(k, raising=False)
    assert TT.du_ram_dong(_v(), 9.0)[0] is False and TT.du_ram_dong(_v(), 10.5)[0] is True      # 6 + 4 du tru
    assert TT.du_ram_dong(_v(tang=1), 6.0)[0] is True
    assert TT.so_agent(20.0, 20) == 10 and TT.so_agent(5.0, 20) == 1 and TT.so_agent(100.0, 8) == 7
    assert TT.slot_toi_da_dong(32.0, 5) == 4 and TT.slot_toi_da_dong(16.0, 5) == 1
    assert TT.du_ram_dong(_v(gen=True, so_agent=6), 14.0)[0] is True and TT.du_ram_dong(_v(gen=True, so_agent=8), 14.0)[0] is False


def test_cong_tang1_moi(monkeypatch):
    monkeypatch.delenv("BRAIN_CONG_LAI_MIN", raising=False); monkeypatch.delenv("BRAIN_CONG_DD_MAX", raising=False)
    v = _v()
    assert TT.phan_xu_tang1_moi({"net": 300.0, "dd": "500.00 (40.00%)"}, v)[0]            # ~10%/nam
    assert not TT.phan_xu_tang1_moi({"net": 150.0, "dd": "1 (40%)"}, v)[0]                  # ~5%/nam
    assert not TT.phan_xu_tang1_moi({"net": 3000.0, "dd": "1 (90.1%)"}, v)[0]
    assert TT.phan_xu_tang1_moi({"net": None, "dd": None}, v)[0]


def test_ghi_lech_va_hieu_chinh(tmp_path):
    sc, ra = tmp_path / "so_cai.jsonl", tmp_path / "lech.jsonl"
    b = _v(pha="KIEM_CSV")
    sc.write_text(json.dumps(dict(b, tang=1, net=400.0, dd="1 (30.0%)")) + "\n")
    d = TT.ghi_lech(dict(b, net=300.0, dd="1 (35.0%)"), sc, ra)
    assert d["lech_dd"] == 5.0 and d["lech_lai_kep"] < 0 and ra.exists()
    assert TT.hieu_chinh_cong(ra)["goi_y"] is None
    for _ in range(12):
        TT.ghi_lech(dict(b, net=300.0, dd="1 (35.0%)"), sc, ra)
    g = TT.hieu_chinh_cong(ra)
    assert g["so_cap"] == 13 and g["goi_y"]["BRAIN_CONG_DD_MAX"] == 75.0 and g["goi_y"]["BRAIN_CONG_LAI_MIN"] > 10


def test_khoa_tick(tmp_path):
    assert TT.lay_khoa("GOLDmicro", "p1", tmp_path) and TT.lay_khoa("GOLDmicro", "p1", tmp_path)
    assert not TT.lay_khoa("GOLDmicro", "p3", tmp_path)
    assert not TT.duoc_chay_tick({"ma": "GOLDmicro"}, "p3", tmp_path)
    assert TT.duoc_chay_tick({"ma": "GOLDmicro", "tang": 1}, "p3", tmp_path)
    TT.tra_khoa("GOLDmicro", "p3", tmp_path); assert not TT.lay_khoa("GOLDmicro", "p3", tmp_path)   # khong phai chu
    TT.tra_khoa("GOLDmicro", "p1", tmp_path); assert TT.lay_khoa("GOLDmicro", "p3", tmp_path)
    TT.danh_dau_am("EURUSDmicro", tmp_path)
    assert TT.duoc_chay_tick({"ma": "EURUSDmicro"}, "p9", tmp_path)
    f = tmp_path / "khoa" / "X.lock"; f.write_text(json.dumps({"chu": "p1", "luc": 0}))
    assert TT.lay_khoa("X", "p2", tmp_path) and (tmp_path / "khoa" / "X.lock.cu").exists()        # khoa chet -> doi ten


def test_slot_an_toan():
    assert TT.kiem_slot_an_toan(r"C:\Program Files\XM Global MT5")
    assert TT.kiem_slot_an_toan(r"D:\mt5_tester\p1") is None


def test_viec_gen_va_ini(monkeypatch):
    g = TT.viec_gen(_v(), so_agent_=6)
    assert g["pha"] == "V2_GEN" and set(g["toi_uu"]) == {"InpTPPct", "InpBuocPct", "InpMaxTang", "InpLot0"}
    a, b, c = g["toi_uu"]["InpTPPct"]
    assert abs(a - 0.0025) < 1e-9 and abs(c - 0.0075) < 1e-9 and g["toi_uu"]["InpMaxTang"] == (3, 1, 9)
    ini = SV.ini_ong_dan(g, g["ten"], "Leverage=1:500\n")
    assert "Optimization=2" in ini and "Model=1" in ini and "OptimizationCriterion=4" in ini
    st = SV.file_set_ong_dan(g)
    assert "InpTPPct=0.005||0.0025||" in st and "||Y" in st
    ini0 = SV.ini_ong_dan(_v(), "x", "")
    assert "Optimization=0" in ini0 and "Model=4" in ini0 and "OptimizationCriterion=0" in ini0
    assert not SV.la_viec_hai_tang(dict(_v(), pha="V2_GEN_KIEM")) and SV.la_viec_hai_tang(_v())


def test_chon_tam_cao_nguyen_khong_lay_dinh():
    ps = []
    for i in range(10):
        for j in range(10):
            rf = 2.0 if (3 <= i <= 6 and 3 <= j <= 6) else 0.5
            if (i, j) == (0, 9):
                rf = 9.0                          # dinh co lap
            ps.append({"InpTPPct": i * 0.001, "InpMaxTang": float(j), "Recovery Factor": rf, "Equity DD %": 40.0, "Profit": 100.0})
    c = TT.chon_tam_cao_nguyen(ps, ["InpTPPct", "InpMaxTang"], top=2)
    assert all(3 <= round(x["InpTPPct"] / 0.001) <= 6 for x in c) and c[0]["cao_nguyen_median_rf"] == 2.0
    g = TT.viec_gen(_v(), so_agent_=4)
    k = TT.viec_kiem_tick(g, dict(c[0], InpLot0=3.0), 1)
    assert k["pha"] == "V2_GEN_KIEM" and isinstance(k["ts"]["InpMaxTang"], int) and "toi_uu" not in k


def test_sau_toi_uu_doc_xml(tmp_path):
    hdr = ["Pass", "Result", "Profit", "Recovery Factor", "Equity DD %", "Trades", "InpTPPct", "InpMaxTang"]
    rows = [hdr] + [[str(n), "1", "100", str(1 + (n % 3)), "30", "50", str(0.004 + 0.001 * (n % 3)), str(5 + n % 2)] for n in range(12)]
    x = "<Workbook>" + "".join("<Row>" + "".join("<Cell><Data>%s</Data></Cell>" % c for c in r) + "</Row>" for r in rows) + "</Workbook>"
    f = tmp_path / "r.xml"; f.write_text(x, encoding="utf-8")
    h = tmp_path / "h.jsonl"
    g = TT.viec_gen(_v(), so_agent_=2)
    g["toi_uu"] = {"InpTPPct": g["toi_uu"]["InpTPPct"], "InpMaxTang": g["toi_uu"]["InpMaxTang"]}
    moi = TT.sau_toi_uu(f, g, h, top=2)
    assert len(moi) == 2 and len(h.read_text().splitlines()) == 2


def test_tu_vong2_loc_gen(tmp_path, monkeypatch):
    h = tmp_path / "h.jsonl"
    h.write_text(json.dumps(_v(san="XM")) + "\n" + json.dumps(TT.viec_gen(_v(san="XM"), 2)) + "\n")
    monkeypatch.setenv("BRAIN_VONG2", "1"); monkeypatch.delenv("BRAIN_GEN", raising=False)
    assert [v["pha"] for v in SV.tu_vong2(h)] == ["V2_CAO_NGUYEN"]
    monkeypatch.setenv("BRAIN_GEN", "1")
    assert len(SV.tu_vong2(h)) == 2


def test_chay_lien_tuc_import_co_tang_toc():
    import ast
    t = (Path(__file__).resolve().parent / "mt5tools" / "chay_lien_tuc.py").read_text(encoding="utf-8")
    ast.parse(t)
    for co in ("BRAIN_GEN", "BRAIN_CONG_MOI", "BRAIN_RAM_DONG", "BRAIN_TICK_CHUNG"):
        assert co in t
