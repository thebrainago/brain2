# -*- coding: utf-8 -*-
"""Nhan THIEU TEP (bai hoc the-brain D10): #include ngoai thu vien chuan MT5 - chi NHAN."""
from nhan import cau_kho_ma as C


def test_chuan_khong_tinh():
    src = '#include <Trade/Trade.mqh>\n#include <Indicators\\\\Trend.mqh>\n#include <MovingAverages.mqh>\n'
    assert C.tep_include_ngoai(src) == []


def test_ngoai_va_cung_thu_muc():
    src = '#include "MultiPivots.mqh"\n#include <MyLib/Signal.mqh>\n#include "MultiPivots.mqh"\n'
    assert C.tep_include_ngoai(src) == ["MultiPivots.mqh", "MyLib/Signal.mqh"]


def test_bo_chu_thich():
    assert C.tep_include_ngoai('// #include "X.mqh"\n/* #include <Y/Z.mqh> */\n') == []


def test_nhan_trong_pheu_khong_doi_so():
    ea = ('#include "Missing.mqh"\n#include <Trade/Trade.mqh>\nCTrade t;\n'
          'void OnTick(){ if(iClose(_Symbol,PERIOD_CURRENT,1)>iClose(_Symbol,PERIOD_CURRENT,2)) '
          't.Buy(0.1); }\n' + "//" + "x" * 300)
    r = C.do_kho([C._ban_ghi("a.mq5", ea)], bo_mau_thu=False)
    assert r["pheu"].get("thieu_tep") == 1
    d = [x for x in r["ds"] if x["ten"] == "a.mq5"][0]
    assert d["thieu_tep"] == ["Missing.mqh"]


def test_seeker_cdp_can_cho_phep_ngoai_windows(monkeypatch):
    import tru.seeker as S
    monkeypatch.delenv("BRAIN_CDP_CHO_PHEP", raising=False)
    monkeypatch.setattr(S.os, "name", "posix")
    assert S.cdp_duoc_phep() is False
    r = S.quet_trinh_duyet(ngan_sach_giay=1)
    assert r.get("bo_qua") and r["da_quet"] == 0
    monkeypatch.setenv("BRAIN_CDP_CHO_PHEP", "1")
    assert S.cdp_duoc_phep() is True
    monkeypatch.delenv("BRAIN_CDP_CHO_PHEP")
    monkeypatch.setattr(S.os, "name", "nt")
    assert S.cdp_duoc_phep() is True
