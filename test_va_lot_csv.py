"""03/11/2026: port vá lot CSV ~100x (vong2/kiem-sau 47430f3d)."""
from pathlib import Path
import mt5tools.sinh_viec as SV


def test_scale_lot_ma_hash_va_idempotent():
    v = {"ma": "GBPCAD#", "ts": {"InpLot0": 30.0}, "von": 1000}
    SV.scale_lot_for_hash_demo(v)
    assert v["ts"]["InpLot0"] == 0.3 and v["von"] == 10000 and v["lot_scaled_for_hash"]
    SV.scale_lot_for_hash_demo(v)
    assert v["ts"]["InpLot0"] == 0.3


def test_khong_scale_ma_thuong():
    v = {"ma": "GBPCAD", "ts": {"InpLot0": 30.0}}
    assert SV.scale_lot_for_hash_demo(v)["ts"]["InpLot0"] == 30.0


def test_dat_csv_vao_scale_cot_lot(tmp_path):
    goc = tmp_path / "g"; goc.mkdir(); (goc / "a.csv").write_text("t,ma,lot\n1,GBPCADmicro,30\n2,GBPCAD#,0.1\n")
    d = SV.dat_csv_vao({"csv_vao": "a.csv", "ma": "GBPCAD#"}, goc, tmp_path / "c")
    dong = d.read_text().splitlines()
    assert dong[1] == "1,GBPCAD#,0.3" and dong[2] == "2,GBPCAD#,0.1"


def test_cot_loi_bo_dong_nghi_ngo():
    assert SV.cot_loi({"dd": "1 (10.0%)", "net": 5, "pha": "IS", "lot_csv_nghi_ngo": True}) is None
