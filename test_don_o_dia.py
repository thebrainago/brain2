import os, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "may_nha"))
import tho_mt5 as T


def _cu(f, ngay=3):
    t = time.time() - ngay * 86400; os.utime(f, (t, t))


def test_don_slot(tmp_path):
    s = tmp_path / "g1"; (s / "Tester" / "cache").mkdir(parents=True); (s / "Tester" / "logs").mkdir(); (s / "logs").mkdir()
    kho = tmp_path / "kho"; kho.mkdir()
    for f in [s / "Tester/cache/a.tst", s / "Tester/logs/x.log", s / "logs/y.log", s / "r1.htm", s / "r2.htm"]:
        f.write_text("x"); _cu(f)
    (s / "moi.htm").write_text("x"); (kho / "moi.htm").write_text("x"); (kho / "r1.htm").write_text("x")
    (s / "accounts.dat").write_text("x"); _cu(s / "accounts.dat")
    kq = T.don_slot(s, kho)
    assert kq == {"cache": 1, "tester_logs": 1, "logs": 1, "agent": 0, "bao_cao": 1}
    assert (s / "r2.htm").exists() and (s / "moi.htm").exists() and (s / "accounts.dat").exists()


def test_canh_bao_va_uu_tien():
    do = {"E:\\": 5.0, "D:\\": 20.0, "C:\\": 30.0}.get
    assert T.canh_bao_o_day(10, do=do) == [("E:\\", 5.0)]
    assert str(T.thu_muc_lam_viec("x", do=do)).startswith("D:")
    do2 = {"E:\\": 50.0, "D:\\": 20.0, "C:\\": 30.0}.get
    assert str(T.thu_muc_lam_viec("x", do=do2)).startswith("E:")


def test_don_agent_tester(tmp_path):
    import os, time
    d = tmp_path / "Tester" / "Agent-127.0.0.1-3001" / "temp" / "x"; d.mkdir(parents=True)
    cu = d / "a.tmp"; cu.write_text("1"); moi = d / "b.tmp"; moi.write_text("1")
    os.utime(cu, (time.time() - 3600, time.time() - 3600))
    assert T.don_agent_tester(tmp_path, 10) == 1
    assert moi.exists() and not cu.exists()
