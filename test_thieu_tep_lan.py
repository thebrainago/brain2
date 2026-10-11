# -*- coding: utf-8 -*-
"""A2 (11/10/2026): EA co #include ngoai KHONG co trong kho -> lan THIEU_TEP, khong vao mau so
ty le dich, khong xuat ra vong lap (khong gia vo la da dich). Co tep canh file -> doc binh thuong."""
import tempfile
from pathlib import Path

from nhan import cau_kho_ma as C

EA = ('#include <Trade/Trade.mqh>\n{inc}CTrade t;\n'
      'void OnTick(){ if(iClose(_Symbol,PERIOD_CURRENT,1)>iClose(_Symbol,PERIOD_CURRENT,2)) '
      't.Buy(0.1); }\n' + "//" + "x" * 300)


def test_thieu_that_tach_khoi_mau_so_va_khong_xuat():
    co = C._ban_ghi("ok.mq5", EA.replace('{inc}', ''))
    thieu = C._ban_ghi("thieu.mq5", EA.replace('{inc}', '#include "Missing.mqh"\n') + "\n//khac")
    r = C.do_kho([co, thieu], bo_mau_thu=False)
    assert r["pheu"]["thieu_tep"] == 1 and r["pheu"]["lan_thieu_tep"] == 1
    d = {x["ten"]: x for x in r["ds"]}
    assert d["thieu.mq5"]["ket_qua"] == "thieu_tep"
    assert d["thieu.mq5"]["thieu_tep_that"] == ["Missing.mqh"]
    assert [x["ten"] for x in r["xuat"]] == [x["ten"] for x in r["xuat"] if x["ten"] == "ok.mq5"]
    assert r["so"]["vao_lenh"] == d["ok.mq5"]["vao_lenh"]          # mau so chi tu EA du tep
    assert r["so_thieu_tep"]["vao_lenh"] == d["thieu.mq5"]["vao_lenh"]
    assert "lan THIEU_TEP" in C.bao_cao_md(r)


def test_tep_nam_canh_file_thi_khong_thieu():
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "a.mq5").write_text(EA.replace('{inc}', '#include "Lib.mqh"\n'), encoding="utf-8")
        (Path(td) / "Lib.mqh").write_text("int f(){return 1;}", encoding="utf-8")
        r = C.do_kho(C.gom_tu_thu_muc(td), bo_mau_thu=False)
    assert r["pheu"].get("thieu_tep") == 1                         # van la include ngoai (nhan)
    assert r["pheu"].get("lan_thieu_tep", 0) == 0                  # nhung co tep -> doc binh thuong
    assert r["ds"][0]["ket_qua"] != "thieu_tep"


def test_multipivots_bo_doc_da_biet():
    assert C.tep_thieu_that('#include <MultiPivots.mqh>\n') == []


def test_tep_co_trong_kho_theo_ten():
    assert C.tep_thieu_that('#include <My/Sig.mqh>\n', co_san={"sig.mqh"}) == []
    assert C.tep_thieu_that('#include <My/Sig.mqh>\n') == ["My/Sig.mqh"]
    assert C.tep_thieu_that('#include <Trade/Trade.mqh>\n') == []
