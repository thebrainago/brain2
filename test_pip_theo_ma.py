"""03/11/2026: pip theo mã (port 41052c33)."""
from nhan.dich_nguoc.phan_tich import pip


def test_pip_theo_ma():
    assert pip("EURUSD") == 0.0001 and pip("GBPCAD#") == 0.0001 and pip("CADJPYmicro") == 0.01
    assert pip("XAUUSD") == 0.1 and pip("GOLD.i#") == 0.1 and pip("XAGUSD") == 0.01
    assert pip("USOIL") == 0.01 and pip("OILCash") == 0.01 and pip("NGAS") == 0.001
    for m in ("UK100", "FRA40", "JP225", "AUS200", "HK50", "US500", "USTEC", "DE40", "GER40", "US30", "NAS100", "BTCUSD"):
        assert pip(m) == 1.0, m
    assert pip("ETHUSD") == 0.1
