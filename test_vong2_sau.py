# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from nhan import vong2_sau as S


def _m(nam=2.7, lenh=100, wf=(20, 25, 22), p95=50, het=0):
    return {"so_nam": nam, "so_lenh": lenh, "walk_forward": [{"lai_kep_pct_nam": x} for x in wf],
            "monte_carlo": {"equity": {"dd_equity_p95": p95}}, "so_lenh_het_ky": het}


def test_canh_bao_qua_khop():
    assert S.canh_bao_qua_khop(_m(), 3) == []
    c = S.canh_bao_qua_khop(_m(nam=1.3, lenh=15, wf=(200, 5, -3), p95=90, het=2), 1)
    assert any("lịch sử ngắn" in x for x in c) and any("ít lệnh" in x for x in c)
    assert any("WF âm" in x for x in c) and any("gánh" in x for x in c) and any("MC" in x for x in c)
    assert any("còn mở" in x for x in c) and any("1 cặp" in x for x in c)


def _pt(sym, v):
    t = pd.date_range("2024-01-01", periods=len(v), freq="D")
    e = pd.Series(np.asarray(v, float) + 1000.0, index=t)
    return {"_dv": pd.DataFrame({"equity": e, "equity_xau": e}), "symbol": sym, "dd_equity_pct": S.V.dd_pct(e),
            "lai_kep_pct_nam": 0.0, "lai_ngay_s": e.diff().dropna()}


def test_ghep_bu_tru_hedge():
    a = [0, -300, 0, -300, 0, 200]; b = [0, 300, 0, 300, 0, 200]       # nguoc pha -> DD tong ~0
    pt = {"A": _pt("X", a), "B": _pt("X", b), "C": _pt("Y", a)}
    g = S.ghep_cung_cap(pt)
    assert len(g) == 1 and g[0]["symbol"] == "X" and g[0]["bu_tru"] and g[0]["dd_equity_pct"] < 1
    assert g[0]["tuong_quan_ngay"] < -0.5


def test_danh_muc_chan_tuong_quan_va_cap():
    import itertools
    rng = np.random.default_rng(1)
    pt = {}
    for i, sym in enumerate("XXXYZ"):
        pt["h%d" % i] = _pt(sym, np.cumsum(rng.normal(2, 10, 300)))
    d = S.danh_muc_sau(pt, list(pt), tq_max=0.3, lan_ngau_nhien=200)
    for r in d["tot_theo_diem"]:
        s = [pt[k]["symbol"] for k in r["he"]]
        assert max(s.count(x) for x in s) <= 2
    assert d["so_nhom_da_do"] > 0 and set(d["theo_tran_dd"]) == {"20", "30", "40", "60"}


def test_tf_tu_htm(tmp_path):
    (tmp_path / "x.htm").write_bytes("<td>Period:</td><td><b>H4 (2023.12.26 - 2026.10.01)</b></td>".encode("utf-16"))
    assert S.tf_tu_htm("x", tmp_path) == "H4" and S.tf_tu_htm("khong", tmp_path) is None


def test_danh_muc_oos_chia_doan():
    rng = np.random.default_rng(2)
    pt = {"h%d" % i: _pt("S%d" % i, np.cumsum(rng.normal(1, 5, 400))) for i in range(4)}
    r = S.danh_muc_oos(pt, list(pt), lan=50)
    assert r["chon"] and r["moc"] > "2024-01-01" and r["deu_tat_ca_oos"]["so_he"] == 4


def test_uu_tien_hang_cho_idempotent(tmp_path):
    import json
    f = tmp_path / "h.jsonl"
    f.write_text(json.dumps({"ten": "a", "vong2_goc": "X", "diem": 60}) + "\n" + json.dumps({"ten": "b", "vong2_goc": "Y", "diem": 60}) + "\n")
    assert S.uu_tien_hang_cho({"X"}, f) == ["a"] and S.uu_tien_hang_cho({"X"}, f) == ["a"]
    d = [json.loads(x) for x in f.read_text().splitlines()]
    assert d[0]["diem"] == 70 and d[1]["diem"] == 60


def test_ghi_vao_ket_qua_thay_muc_cu(tmp_path):
    f = tmp_path / "k.md"; f.write_text("# a\n\n## 5. x\n")
    S.ghi_vao_ket_qua("## 6. Vòng 2 SÂU v1\n", f); S.ghi_vao_ket_qua("## 6. Vòng 2 SÂU v2\n", f)
    t = f.read_text(); assert "v2" in t and "v1" not in t and "## 5. x" in t
