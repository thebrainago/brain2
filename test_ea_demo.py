# -*- coding: utf-8 -*-
"""Vong 13: EA demo - logic Python mirror khop voi mo phong (mua_vu / IBS); file EA va .set day du."""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent / "ea_demo"))
import ea_logic_py as EL   # noqa: E402
import mua_vu as MV        # noqa: E402

D = Path(__file__).parent / "ea_demo"


def test_mua_vu_khop_mo_phong_tren_ngay_thuong():
    # lich ngay thuong (khong le) -> EA va mo phong phai khop TUYET DOI
    idx = pd.bdate_range("2018-11-01", "2024-02-29")
    g = pd.Series(100.0, index=idx)
    e = np.mean([MV.phoi_nhiem(k, g) for k in ("CHU_KY_BAU_CU_NAM3", "HALLOWEEN", "DAU_CUOI_THANG", "SANTA")], axis=0) * 4
    for i in range(1, len(idx)):
        # EA kiem o ngay idx[i-1], dat khoi luong cho phien ke tiep idx[i]
        assert EL.so_quy_tac_bat(EL.ngay_thuong_ke(idx[i - 1].date())) == int(round(e[i])), idx[i]


def test_mua_vu_tren_lich_that_khop_cao():
    p = Path("/workspace/du_lieu_ngay/spx_d1_yahoo.csv")
    if not p.exists():
        pytest.skip("khong co du lieu")
    g = MV.doc(p.name, "2000-01-01")
    e = np.mean([MV.phoi_nhiem(k, g) for k in ("CHU_KY_BAU_CU_NAM3", "HALLOWEEN", "DAU_CUOI_THANG", "SANTA")], axis=0) * 4
    ea = [EL.so_quy_tac_bat(EL.ngay_thuong_ke(g.index[i - 1].date())) for i in range(1, len(g))]
    khop = np.mean(np.array(ea) == np.round(e[1:]).astype(int))
    assert khop > 0.97          # lech chi do ngay le My (EA dung lich thu 2-6)


def test_ibs_khop():
    assert EL.ibs_tin(10, 0, 1.9) is True and EL.ibs_tin(10, 0, 2.0) is False and EL.ibs_tin(5, 5, 5) is None


def test_file_ea_va_set():
    for ten in ("BRAIN_IBS_Demo", "BRAIN_MuaVu_SPX"):
        src = (D / f"{ten}.mq5").read_text()
        assert "OnTimer" in src and "OnTradeTransaction" in src and "DEAL_SWAP" in src
        assert src.count("{") == src.count("}") and src.count("(") == src.count(")")
        ins = set(re.findall(r"^input\s+\w+\s+(\w+)", src, re.M))
        st = {l.split("=")[0] for l in (D / f"{ten}.set").read_text().splitlines() if "=" in l}
        assert st == ins
