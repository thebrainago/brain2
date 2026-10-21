# -*- coding: utf-8 -*-
"""Test vong 2 (nhan/vong2.py): tai dung equity tu lenh MT5, stress, MC, xep tang, danh muc, co BRAIN_VONG2, ghep cung cap."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nhan import vong2 as V  # noqa: E402
from nhan import ong_dan as OD  # noqa: E402


def _ghi(d: Path, ten: str, deals: list, gia: list):
    l = d / (ten + "_vao.csv_lenh_mt5.csv")
    l.write_text("thoi_gian;deal;position;vao_ra;chieu;khoi_luong;gia;loi;swap;hoa_hong;phu\n" +
                 "".join(";".join(map(str, x)) + "\n" for x in deals), encoding="utf-8")
    g = d / (ten + "_vao.csv_gia.csv")
    g.write_text("time,open,high,low,close,spread_point\n" + "".join(",".join(map(str, x)) + "\n" for x in gia), encoding="utf-8")


def _gia(n=60, p0=1.10000, buoc=-0.001):
    t0 = pd.Timestamp("2024-01-01 00:00")
    ra = []
    for i in range(n):
        c = p0 + buoc * i if i < n // 2 else p0 + buoc * (n - i)
        ra.append(((t0 + pd.Timedelta(hours=i)).strftime("%Y.%m.%d %H:%M:%S"), "%.5f" % c, "%.5f" % (c + 0.0005),
                   "%.5f" % (c - 0.0005), "%.5f" % c, 10))
    return ra


def test_equity_tinh_lenh_dang_mo(tmp_path):
    # mot lenh mua 1.10000 luc 0h, dong 1.10000+ o gio 59 (gia giam 30 pip roi hoi) -> DD dong lenh 0, DD equity > 0
    g = _gia()
    deals = [("2024.01.01 00:00:00", 2, 2, "in", 0, 1.0, 1.10000, 0, 0, 0, "XL_B#0"),
             ("2024.01.01 59:00:00".replace("59:00", "23:00"), 3, 2, "out", 1, 1.0, 1.09000, -100.0, 0, 0, "tp")]
    deals[1] = (g[59][0], 3, 2, "out", 1, 1.0, 1.10100, 10.0, 0, 0, "tp")
    _ghi(tmp_path, "od_x", deals, g)
    m = V.phan_tich_mt5("od_x", tmp_path)
    assert m["so_lenh"] == 1 and m["dd_dong_pct"] == 0.0
    # k = 10 USD / 0.001 = 10000 USD/gia; day -0.030 -> noi -300 USD, gia bat loi (low) them 5 pip -> ~ -305
    assert 25.0 < m["dd_equity_pct"] < 35.0
    assert m["dd_equity_stress_pct"] >= m["dd_equity_pct"]
    assert m["lai_kep_stress_pct_nam"] <= m["lai_kep_pct_nam"]


def test_lenh_mo_cuoi_ky_va_khop_net(tmp_path):
    g = _gia()
    deals = [("2024.01.01 00:00:00", 2, 2, "in", 0, 1.0, 1.10000, 0, 0, 0, "XL_B#0"),
             (g[5][0], 3, 2, "out", 1, 1.0, 1.09600, -40.0, 0, 0, "x"),
             (g[10][0], 4, 4, "in", 0, 1.0, 1.09000, 0, 0, 0, "XL_B#0")]          # khong co out -> mo cuoi ky
    _ghi(tmp_path, "od_y", deals, g)
    p = V.doc_vi_the(tmp_path / "od_y_vao.csv_lenh_mt5.csv")
    assert len(p) == 2 and p["het_ky"].sum() == 1 and p["k"].notna().all()
    m = V.phan_tich_mt5("od_y", tmp_path, net_bao_cao=-25.0)
    assert m["so_lenh_het_ky"] == 1 and abs(m["lech_net_khop_cuoi_ky"]) > 0


def test_spread_hong_bi_thay(tmp_path):
    g = _gia(); g[3] = g[3][:5] + (-170927,)
    deals = [("2024.01.01 03:00:00", 2, 2, "in", 0, 1.0, 1.097, 0, 0, 0, "a"), (g[8][0], 3, 2, "out", 1, 1.0, 1.098, 10.0, 0, 0, "b")]
    _ghi(tmp_path, "od_z", deals, g)
    p = V.doc_vi_the(tmp_path / "od_z_vao.csv_lenh_mt5.csv")
    c = V.chi_phi_stress(p, V.doc_gia_mt5(tmp_path / "od_z_vao.csv_gia.csv"))
    assert (c > 0).all()


def test_monte_carlo_equity_khong_qua_100():
    t = pd.date_range("2024-01-01", periods=24 * 200, freq="h")
    rng = np.random.default_rng(0)
    eq = 1000 * np.cumprod(1 + rng.normal(0.0002, 0.003, len(t)))
    dv = pd.DataFrame({"dong": eq, "equity": eq, "equity_xau": eq * 0.995}, index=t)
    mc = V.monte_carlo_equity(dv, lan=50)
    assert 0 <= mc["dd_equity_p50"] <= mc["dd_equity_p95"] <= 100
    assert "MÔ PHỎNG" in mc["nhan"]


def test_xep_tang():
    m = {"so_nam": 2.8, "lai_kep_stress_pct_nam": 30, "dd_equity_stress_pct": 40, "so_lenh": 200,
         "monte_carlo": {"equity": {"dd_equity_p95": 60}}, "walk_forward": [{"lai_kep_pct_nam": 20}, {"lai_kep_pct_nam": 8}]}
    py = {"py_mt5": 1.0, "ti_le_cap_khac_khong_lo": 0.6, "oos_lai": 20, "cao_nguyen": 0.8}
    assert V.xep_tang(m, py)["tang"] == "A"
    assert V.xep_tang(dict(m, dd_equity_stress_pct=70), py)["tang"] == "B"
    assert V.xep_tang(m, dict(py, py_mt5=None))["tang"] == "C"          # thieu so do -> khong dat


def test_huong_gan_nhat_va_xac_nhan():
    s = np.array([0, 1, 0, 0, 0, -1, 0])
    assert list(OD.huong_gan_nhat(s)) == [0, 1, 1, 1, 1, -1, -1]
    assert list(OD.huong_gan_nhat(s, 2)) == [0, 1, 1, 1, 0, -1, -1]


def test_nhan_chu_ky():
    t = {"id": "a", "tin_hieu": {"kieu": "spec", "specs": [{"vao": [{"trai": {"chi_bao": "tre", "n": 1, "cua": {"chi_bao": "ema", "n": 20}},
                                                                      "phai": {"chi_bao": "ema", "n": 50}}]}]}}
    x = V.nhan_chu_ky(t, 1.5)["tin_hieu"]["specs"][0]["vao"][0]
    assert x["trai"]["n"] == 1 and x["trai"]["cua"]["n"] == 30 and x["phai"]["n"] == 75
    assert V.nhan_chu_ky(t, 1.0) is t


def test_the_ghep_kieu():
    a, b = {"id": "a", "tin_hieu": {"kieu": "spec", "specs": []}}, {"id": "b", "tin_hieu": {"kieu": "spec", "specs": []}}
    assert V.the_ghep(a, b, "xac_nhan")["tin_hieu"]["bo_loc"][0]["tham"]["kieu"] == "xac_nhan"
    assert V.the_ghep(a, b, "nguoc")["tin_hieu"]["kieu_b"] == "nguoc"
    assert V.the_ghep(a, b, "them_lenh")["tin_hieu"]["nguon_b"] == b["tin_hieu"]


def test_danh_muc_dd_equity_khong_chi_lenh_dong():
    t = pd.date_range("2024-01-01", periods=24 * 600, freq="h")
    x = np.sin(np.arange(len(t)) / 300.0) * 200
    def he(dau):
        eq = 1000 + np.arange(len(t)) * 0.05 + dau * x
        dv = pd.DataFrame({"dong": 1000 + np.arange(len(t)) * 0.05, "equity": eq, "equity_xau": eq}, index=t)
        ngay = dv["equity"].resample("1D").last().diff().dropna()
        return {"so_nam": 1.64, "_dv": dv, "lai_kep_stress_pct_nam": 30, "dd_equity_pct": 20,
                "lai_ngay": {str(k.date()): float(v) for k, v in ngay.items()}}
    dm = V.danh_muc_v2({"a": he(1), "b": he(-1)}, tq_max=0.5)
    assert dm and dm[0]["dd_equity_pct"] < 5        # hai he nguoc pha -> DD equity danh muc nho
    assert "EQUITY" in dm[0]["nhan"]


def test_co_vong2_mac_dinh_tat(tmp_path, monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "mt5tools"))
    import sinh_viec as SV
    p = tmp_path / "h.jsonl"
    p.write_text(json.dumps({"ten": "od_v2cn_x", "ea": "XL", "ma": "EURUSDmicro", "tf": "H1", "san": "XM", "diem": 70}) + "\n", encoding="utf-8")
    monkeypatch.delenv("BRAIN_VONG2", raising=False)
    assert SV.tu_vong2(p) == []
    monkeypatch.setenv("BRAIN_VONG2", "1")
    assert [v["ten"] for v in SV.tu_vong2(p)] == ["od_v2cn_x"]
