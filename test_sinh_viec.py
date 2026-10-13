import sys
sys.path.insert(0, "mt5tools")
import sinh_viec as SV


def _r(**k):
    r = {"ea": "MRZ", "ma": "GBPUSD#", "tf": "D1", "ts": SV._ts("MRZ", {}), "pha": "IS", "pf": 1.0, "lenh": 50, "net": 1.0, "p": 0.5}
    r.update(k); return r


def test_khong_bao_gio_can_va_khong_trung():
    a = SV.lay_viec(50, so_cai=[])
    assert len(a) == 50 and len({SV.khoa(v) for v in a}) == 50
    b = SV.lay_viec(50, so_cai=[dict(v, pf=0.9, lenh=10, net=-1) for v in a])
    assert len(b) == 50 and not ({SV.khoa(v) for v in a} & {SV.khoa(v) for v in b})


def test_oos_uu_tien_khi_dat_is():
    v = SV.lay_viec(1, so_cai=[_r(pf=1.5, net=100)])[0]
    assert v["pha"] == "OOS" and v["ma"] == "GBPUSD#"


def test_near_miss_sinh_hang_xom():
    v = SV.lay_viec(3, so_cai=[_r(pf=1.15, net=10)])
    assert all(x["pha"] == "IS" and x["diem"] >= 10 for x in v)


def test_khung_ngan_khong_gio_vao():
    assert all(v["ts"]["InpGioVao"] == 0 for v in SV.ung_vien(__import__("random").Random(1), 500) if v["tf"] != "D1")


def test_holm_va_tong_ket():
    sc = [_r(p=0.001, pf=1.5, net=50), _r(ma="AUDUSD#", p=0.04), _r(ma="EURGBP#", p=0.5)]
    h = SV.holm(sc)
    assert h[SV.khoa(sc[0])] and not h[SV.khoa(sc[1])]
    sc.append(dict(sc[0], pha="OOS", pf=1.3, lenh=20, net=10))
    t = SV.tong_ket(sc)
    assert t["so_lan_thu"] == 4 and len(t["ung_vien_ca_hai"]) == 1 and t["ung_vien_ca_hai"][0]["holm"]


def test_file_set():
    s = SV.file_set(dict(_r(), tf="H4", ts=SV._ts("MRZ", {"InpNguongZ": 2.5})), "InpGioVao=2\nInpLogChung=true\nInpLots=0.01\n")
    assert "InpNguongZ=2.5" in s and "InpTF=16388" in s and "InpLogChung=false" in s and s.count("InpGioVao") == 1
