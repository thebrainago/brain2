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


def test_near_miss_sinh_hang_xom(monkeypatch):
    # 18/10/2026: hang cho ong dan (diem 60+) dung truoc near-miss; tach ra de test nay chi xet near-miss
    monkeypatch.setattr(SV, "tu_ong_dan", lambda *a, **k: [])
    v = SV.lay_viec(3, so_cai=[_r(pf=0.95, net=-1)])
    assert all(x["pha"] == "IS" and x["diem"] >= 10 for x in v)


def test_lai_mong_van_duoc_chay_oos():
    # 17/10/2026: chi can co lai -> pf 1,15 / 12 lenh tung bi chan o IS, nay duoc chay OOS
    v = SV.lay_viec(1, so_cai=[_r(pf=1.15, net=10, lenh=12)])[0]
    assert v["pha"] == "OOS"


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


def test_python_box_uu_tien(tmp_path):
    import json
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"tong_ket": {"ung_vien_ca_hai": [{"ea": "RSI", "ma": "EURJPY#", "tf": "D1", "ts": {"InpRsiThap": 30, "InpRsiCao": 75, "InpSlATR": 1.0},
                                                                "IS": {"pf": 2.2}, "OOS": {"pf": 2.3}}]}}))
    v = SV.tu_python_box(p)
    assert v[0]["diem"] > 50 and v[0]["ts"]["InpRsiCao"] == 75 and v[0]["ts"]["InpTrATR"] == 2.0


def test_cot_loi_lai_10_o_sut_giam_80():
    # IS 7 nam: +700 USD tren 10.000 = 1 %/nam, DD 4 % -> tang lot x20 -> 20 %/nam o DD 80 % -> DAT
    c = SV.cot_loi(_r(net=700.0, dd="400 (4.00%)"))
    assert abs(c["lai_pct_nam"] - 1.0) < 0.01 and c["he_so_lot_dd80"] == 20.0 and c["dat"]
    # 0,1 %/nam voi DD 10 % -> 0,8 %/nam o DD 80 % -> KHONG dat; lo -> khong dat
    assert not SV.cot_loi(_r(net=70.0, dd="1000 (10.00%)"))["dat"]
    assert not SV.cot_loi(_r(net=-5.0, dd="10 (0.10%)"))["dat"]
    assert SV.cot_loi(_r(dd=None)) is None



def test_viec_ong_dan_vao_hang_cho(tmp_path, monkeypatch):
    import json
    p = tmp_path / "h.jsonl"
    v = {"ten": "od_x", "ea": "XL", "ea_file": "BRAIN_XuLiLenh", "ma": "AUDCADmicro", "tf": "H4", "ts": {"InpVao": 1},
         "pha": "KIEM", "nguon": "ong_dan", "san": "XM", "diem": 62}
    p.write_text(json.dumps(v) + "\n" + json.dumps(dict(v, ten="od_y", ea="NGOAI")) + "\n", encoding="utf-8")
    monkeypatch.delenv("BRAIN_SAN_TESTER", raising=False)
    assert [x["ten"] for x in SV.tu_ong_dan(p)] == ["od_x"]          # viec NGOAI khong tu chay
    monkeypatch.setenv("BRAIN_SAN_TESTER", "Exness")
    assert SV.tu_ong_dan(p) == []
