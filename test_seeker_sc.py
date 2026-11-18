# -*- coding: utf-8 -*-
"""Nhan dien study Sierra Chart ACSIL trong Seeker (18/11/2026)."""
from tru import seeker as S


def test_acsil_chi_bao():
    d = S.dau_hieu_van_hanh("SCSFExport scsf_X(SCStudyInterfaceRef sc){ sc.Subgraph[0][0]=1; }", "x.cpp")
    assert d["nen_tang"] == "SierraChart" and d["loai"] == "chi_bao"


def test_acsil_ea():
    d = S.dau_hieu_van_hanh("SCSFExport scsf_X(SCStudyInterfaceRef sc){ s_SCNewOrder o; sc.BuyEntry(o); }", "x.cpp")
    assert d["loai"] == "ea"


def test_cpp_thuong_khong_phai_sierra():
    assert S.dau_hieu_van_hanh("int main(){return 0;}", "x.cpp")["nen_tang"] is None
