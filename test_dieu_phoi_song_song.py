import sys
sys.path.insert(0, "mt5tools")
import dieu_phoi_song_song as D


def test_chon_muc():
    assert D.chon_muc(True, False, 0) == "THAP"
    assert D.chon_muc(False, True, 0) == "THAP"
    assert D.chon_muc(False, False, 50) == "VUA"
    assert D.chon_muc(False, False, 20) == "CAO"
    assert D.chon_muc(False, False, 5) == "MAX"
    assert D.chon_muc(True, False, 0, ep="MAX") == "MAX"


def test_muc_giam_dan():
    t = [D.MUC[k] for k in ("MAX", "CAO", "VUA", "THAP")]
    assert all(a.tran_cpu > b.tran_cpu and a.mt5 >= b.mt5 for a, b in zip(t, t[1:]))
    assert D.MUC["MAX"].tran_cpu == 90 and D.MUC["MAX"].mt5 == 4 and D.MUC["THAP"].mt5 == 0


def test_phan_viec():
    assert D.phan_viec("THAP")["may_nha"]["mt5"] == 0 and D.phan_viec("MAX")["box"]["python"] > 0
