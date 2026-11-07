# -*- coding: utf-8 -*-
"""EA gốc vào hàng đợi: không cần dịch Python, không xếp EA thiếu include, không bịa kho."""
import json
from pathlib import Path

import pytest

from may_nha.hang_doi_git import kiem_spec
from seeker import nap_ea_goc as N

pytestmark = pytest.mark.timeout(30)

EA = """#include <Trade/Trade.mqh>
CTrade trade;
input double InpLots = 0.01;
void OnTick()
{
   trade.Buy(InpLots);
}
"""

THIEU = EA.replace("#include <Trade/Trade.mqh>", '#include "MyGrid.mqh"')
CHI_BAO = """#property indicator_chart_window
int OnCalculate(const int rates_total,const int prev_calculated,const datetime &time[],
 const double &open[],const double &high[],const double &low[],const double &close[],
 const long &tick_volume[],const long &volume[],const int &spread[]){ return rates_total; }
"""


def _goi(thu, ten, src, url):
    thu.mkdir(parents=True, exist_ok=True)
    n = 1 + sum(1 for p in thu.glob("g*") if p.is_dir())
    d = thu / ("g%d" % n)
    d.mkdir()
    (d / ten).write_text(src, encoding="utf-8")
    (d / "GOI.json").write_text(json.dumps({"url": url, "tep": [ten]}), encoding="utf-8")
    return d / ten


def test_nhan_ea_mot_file_khong_can_dich(tmp_path):
    kho, hang = tmp_path / "kho", tmp_path / "hang"
    _goi(kho, "GridDemo.mq5", EA, "https://www.mql5.com/en/code/424242")
    q = N.quet_kho(kho, hang, toi_da=3)
    assert len(q["nhan"]) == 1 and not q["tu_choi"]
    spec = q["nhan"][0]["spec"]
    assert kiem_spec(spec) == []
    assert spec["dich_python"] == "khong_yeu_cau"
    assert spec["bien_dich"] == "CHUA_BIEN_DICH"
    assert spec["che_do_tai_khoan"] == "demo_only"
    assert spec["kieu_ea_la_chung"] is False
    assert spec["he_so_lot"] == [1.0]
    assert spec["url_ma_nguon"].endswith("/424242/GridDemo.mq5")
    ids = N.ghi_viec([spec], hang)
    assert ids == [spec["id"]]
    assert json.loads((hang / "can_test" / (spec["id"] + ".json")).read_text())["id"] == spec["id"]


def test_tu_choi_include_ngoai_va_khong_phai_ea(tmp_path):
    kho, hang = tmp_path / "kho", tmp_path / "hang"
    _goi(kho, "Thieu.mq5", THIEU, "https://www.mql5.com/en/code/1")
    d2 = kho / "g2"
    d2.mkdir()
    (d2 / "ChiBao.mq5").write_text(CHI_BAO, encoding="utf-8")
    (d2 / "GOI.json").write_text(json.dumps({"url": "https://www.mql5.com/en/code/2", "tep": ["ChiBao.mq5"]}), encoding="utf-8")
    q = N.quet_kho(kho, hang, 3)
    assert q["nhan"] == []
    ly = " ".join(x["ly_do"] for x in q["tu_choi"])
    assert "include" in ly and "heuristic" in ly
    assert N.ghi_viec([], hang) == []


def test_trung_url_va_tran_viec(tmp_path):
    kho, hang = tmp_path / "kho", tmp_path / "hang"
    url = "https://www.mql5.com/en/code/download/9/GridDemo.mq5"
    _goi(kho, "A.mq5", EA, "https://www.mql5.com/en/code/9")
    spec = N.quet_kho(kho, hang, 3)["nhan"][0]["spec"]
    N.ghi_viec([spec], hang)
    q2 = N.quet_kho(kho, hang, 3)
    assert q2["nhan"] == [] and q2["trung"]
    # trần: hai gói khác nhau, chỉ nhận 1
    kho2 = tmp_path / "kho2"
    _goi(kho2, "A.mq5", EA.replace("0.01", "0.02"), "https://www.mql5.com/en/code/11")
    d = kho2 / "g3"
    d.mkdir()
    (d / "B.mq5").write_text(EA.replace("InpLots", "LotsX").replace("0.01", "0.03"), encoding="utf-8")
    (d / "GOI.json").write_text(json.dumps({"url": "https://www.mql5.com/en/code/12", "tep": ["B.mq5"]}), encoding="utf-8")
    q3 = N.quet_kho(kho2, hang, toi_da=1)
    assert len(q3["nhan"]) == 1
    assert any("trần" in x["ly_do"] for x in q3["tu_choi"])


def test_kho_khong_co_khong_bia(tmp_path):
    q = N.quet_kho(tmp_path / "khong", tmp_path / "hang", 3)
    assert q["kho"] == "khong_co" and q["da_xem"] == 0 and q["nhan"] == []
    bc = N.bao_cao(q, [])
    assert bc["viec_moi"] == [] and "không bịa" in bc["ly_do_kho"]
