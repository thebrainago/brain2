"""03/11/2026: slot XM chỉ có mã '#' -> thợ đổi mã; việc HONG trả lại can_test."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "may_nha"))
import tho_mt5 as T


def _slot(tmp, ten):
    d = tmp / "bases" / "XMGlobal-MT5 10" / "symbols"; d.mkdir(parents=True)
    (d / "symbols-1.dat").write_bytes(b"xx" + "".join(t + "\0" for t in ten).encode("utf-16-le") + b"\0\0")
    return tmp


def test_doi_micro_sang_hash(tmp_path):
    s = _slot(tmp_path, ["GBPNZD#", "GOLD.i#"])
    assert T.ky_hieu_slot(s, "GBPNZDmicro") == "GBPNZD#"
    assert T.ky_hieu_slot(s, "GOLDmicro") == "GOLD.i#"


def test_giu_ma_co_san(tmp_path):
    s = _slot(tmp_path, ["GBPNZDmicro", "GBPNZD#"])
    assert T.ky_hieu_slot(s, "GBPNZDmicro") == "GBPNZDmicro"


def test_doi_ma_csv():
    c = "thoi_gian,ma,chieu,gia,nguon,lot\n2025.01.01 00:00:00,GBPNZDmicro,1,1.1,x,30.0\n"
    o = T.nhan_csv(T.doi_ma_csv(c, "GBPNZDmicro", "GBPNZD#"), 2.0, True)
    assert "GBPNZD#" in o and ",0.6" in o


def test_suy_theo_lich_su(tmp_path):
    for t in ("EURUSD#", "GOLD.i#", "EURUSD"):
        (tmp_path / "bases" / "XM" / "history" / t).mkdir(parents=True)
    assert T.ky_hieu_slot(tmp_path, "GBPNZDmicro") == "GBPNZD#"
    (tmp_path / "bases" / "XM" / "history" / "EURUSDmicro").mkdir()
    assert T.ky_hieu_slot(tmp_path, "GBPNZDmicro") == "GBPNZDmicro"


def test_slot_moi_chua_lich_su(tmp_path):
    assert T.ky_hieu_slot(tmp_path, "USDCADmicro") == "USDCAD#"


def test_journal_bao_khong_co(tmp_path):
    import time
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "20261103.log").write_bytes("x\tTester\tsymbol USDCADmicro not exist\r\n".encode("utf-16"))
    assert T.symbol_khong_co(tmp_path, "USDCADmicro", time.time() - 60)
    (tmp_path / "bases" / "XM" / "history" / "EURUSDmicro").mkdir(parents=True)
    assert T.ky_hieu_slot(tmp_path, "USDCADmicro") == "USDCADmicro"
    T._SLOT_CHI_HASH.add(str(tmp_path))
    assert T.ky_hieu_slot(tmp_path, "USDCADmicro") == "USDCAD#"
