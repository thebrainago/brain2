# -*- coding: utf-8 -*-
"""Test 20/10/2026 toi (Grok Bot): so co che (metadata, khong ma ben thu ba), ghep cheo (khac phong cach, chong trung,
tran, danh muc tuong quan), vong lap (chon_viec_od, san o, terminal bo roi). Khong mang, khong khoa."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "mt5tools"))

from nhan import ghep_cheo as G  # noqa: E402
from nhan import so_co_che as SO  # noqa: E402

_sp = importlib.util.spec_from_file_location("dieu_phoi_may_nha_vl", GOC / "may_nha_toi_nay" / "dieu_phoi_may_nha.py")
DP = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(DP)
CFG = DP.cau_hinh(GOC / "config" / "dieu_phoi.json")

MA_BI_MAT = "def tin_hieu(df):\n    return SECRET_THIRD_PARTY_CODE\n"


def _db(p: Path) -> sqlite3.Connection:
    cn = sqlite3.connect(str(p))
    cn.execute("CREATE TABLE the (id TEXT PRIMARY KEY, json TEXT, loai TEXT, uu_tien INTEGER, duong TEXT, buoc TEXT, "
               "trang_thai TEXT, kq TEXT, cap_nhat TEXT)")
    cn.execute("CREATE TABLE nhat_ky (luc TEXT, buoc TEXT, the_id TEXT, ghi TEXT)")
    return cn


def _the(cn, id_, ho, ql, lai, dd, kieu="spec", ma="GBPCAD", buoc="loc", pc=None):
    th = {"kieu": kieu, "specs": [{"ten": id_, "ho": ho, "co_che": "mo ta " + id_}]} if kieu == "spec" else \
        {"kieu": "python_llm", "ma": MA_BI_MAT}
    t = {"id": id_, "ten": id_, "loai": "he_hoan_thien", "duong_dich": "spec_dsl", "tin_hieu": th, "ho": [ho],
         "seeker": {"phong_cach": pc or []}, "nguon": {"kho": "k", "tep": "data/x.mq5", "url": "https://x/" + id_}}
    kq = {"tot_nhat": {"thu": {"ma": ma, "khung": "H1", "tham": {}, "ql": ql},
                       "kq": {"lai_pct_nam": lai, "sut_giam_pct": dd, "so_stop_out": 0, "so_lenh": 100, "so_nam": 3}}}
    cn.execute("INSERT INTO the VALUES (?,?,?,?,?,?,?,?,?)", (id_, json.dumps(t), "he_hoan_thien", 1, "spec_dsl", buoc, "DAT_LOC",
                                                              json.dumps(kq), ""))


QL_DCA = {"tp_pct": 0.002, "dca_buoc_pct": 0.003, "dca_toi_da": 5, "dca_he_so_lot": 1.6, "hedge_khi_lo_pct": 0.0}
QL_TRON = {"tp_pct": 0.004, "dca_toi_da": 0, "hedge_khi_lo_pct": 0.0}
QL_HEDGE = {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 3, "dca_he_so_lot": 1.0, "hedge_khi_lo_pct": 10.0}


def _kho(tmp_path):
    p = tmp_path / "td.sqlite"
    cn = _db(p)
    _the(cn, "a_mr", "quay_ve_trung_binh", QL_DCA, 40, 40)
    _the(cn, "b_trend", "xu_huong", QL_TRON, 20, 30, ma="EURUSD")
    _the(cn, "c_hedge", "pha_vo", QL_HEDGE, 10, 50, kieu="python_llm", ma="GOLD")      # gan dat (10 >= 0.6*15)
    _the(cn, "d_truot", "xu_huong", QL_TRON, -5, 90)
    cn.commit()
    return p, cn


def test_so_co_che_schema_va_khong_chua_ma(tmp_path):
    p, cn = _kho(tmp_path)
    uv = tmp_path / "UNG_VIEN.md"
    uv.write_text("## Tất cả\n\n| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | PF | Lệnh | "
                  "Stop-out | Swap | Kỳ | Chất lượng tick | Lí do / nhãn |\n|---|\n"
                  "| ĐẠT | od_amr_XM_CSV | a_mr | GBPCADmicro | H1 | 100.0 | 30.5 | 31.0 | 40.0 | 2.0 | 120 | 0 | 1.0 | 2024–2026 | 99% |  |\n"
                  "| ĐẠT | od_x_XM_CSV | khong_co_cache | XAUUSDmicro | H4 | 1.0 | 12.0 | 12.0 | 20.0 | 2.0 | 40 | 0 | 0 | k | 99% |  |\n",
                  encoding="utf-8")
    ds = SO.xay(p, uv)
    by = {r["id"]: r for r in ds}
    assert by["a_mr"]["trang_thai"] == "DAT_MT5" and by["a_mr"]["mt5"][0]["lai_kep_pct_nam"] == 30.5
    assert by["b_trend"]["trang_thai"] == "DAT_PY"
    assert by["c_hedge"]["trang_thai"] == "GAN_DAT"
    assert by["d_truot"]["trang_thai"] == "TRUOT_PY"
    assert by["khong_co_cache"]["ma"] == ["GOLD"] and by["khong_co_cache"]["tai_san"] == ["kim_loai"]
    assert "mean_reversion" in by["a_mr"]["phong_cach"] and {"dca", "martingale"} <= set(by["a_mr"]["phong_cach_quan_li"])
    assert {"hedge", "recovery"} <= set(by["c_hedge"]["phong_cach_quan_li"])
    for k in ("id", "vao", "thoat", "quan_li", "khung", "ma", "phong_cach", "python", "mt5", "trang_thai", "nguon"):
        assert k in by["a_mr"]
    out = SO.luu(ds, tmp_path / "so.jsonl")
    txt = out.read_text(encoding="utf-8")
    assert "SECRET_THIRD_PARTY_CODE" not in txt and "data/x.mq5" not in txt      # chi metadata
    assert [r["id"] for r in SO.tim(SO.doc(out), tag_="martingale")] == ["a_mr"]
    assert [r["id"] for r in SO.tim(SO.doc(out), trang="DAT_MT5,DAT_PY")] == ["a_mr", "b_trend", "khong_co_cache"]
    assert SO.ma_goc("EURUSD#") == "EURUSD" and SO.ma_goc("GBPCADmicro") == "GBPCAD"


def test_ghep_cheo_khac_phong_cach_chong_trung_va_tran(tmp_path):
    p, cn = _kho(tmp_path)
    ds = SO.xay(p, tmp_path / "khong.md")
    kq = G.sinh(cn, ds, {"tran_moi_luot": 4, "tran_ton": 6, "toi_da_moi_he": 9}, in_ra=lambda *a: None)
    assert kq["moi"] == 4
    rows = [json.loads(r[0]) for r in cn.execute("SELECT json FROM the WHERE trang_thai='GHEP_CHEO' AND buoc='quyet_dinh'")]
    assert len(rows) == 4
    for t in rows:
        assert t["duong_dich"] == "noi_bo" and t["tin_hieu"]["kieu"] == "to_hop" and t["thu_goi_y"][0]["ql"]
        assert "d_truot" not in t["thanh_phan"]                                  # chi dat / gan dat
        a, b = (next(r for r in ds if r["id"] == x) for x in t["thanh_phan"])
        assert G.khac_phong_cach(a, b, t["ghep_cheo"]["kieu"])
    kq2 = G.sinh(cn, ds, {"tran_moi_luot": 4, "tran_ton": 6, "toi_da_moi_he": 9}, in_ra=lambda *a: None)
    assert kq2["moi"] == 2                                                       # tran ton 6
    assert G.sinh(cn, ds, {"tran_moi_luot": 4, "tran_ton": 6}, in_ra=lambda *a: None)["moi"] == 0
    ids = [r[0] for r in cn.execute("SELECT id FROM the WHERE trang_thai='GHEP_CHEO'")]
    assert len(ids) == len(set(ids)) == 6
    # cung phong cach (va cung quan li) -> khong ghep
    x = {"phong_cach": ["trend"], "phong_cach_quan_li": ["dca"], "tai_san": ["fx_chinh"]}
    assert not G.khac_phong_cach(x, dict(x), "vao_x_quan_li") and not G.khac_phong_cach(x, dict(x), "hai_nguon")


def test_toi_uu_dung_thu_goi_y_cua_the_ghep():
    src = (GOC / "nhan" / "ong_dan.py").read_text(encoding="utf-8")
    assert 't.get("thu_goi_y")' in src


def test_danh_muc_tuong_quan_va_do(tmp_path):
    d = pd.date_range("2023-01-01", periods=800, freq="D")
    r = np.random.default_rng(3)
    for ten, hat in (("od_a_XM_CSV", 1), ("od_b_XM_CSV", 2), ("od_c_XM_CSV", 1)):
        x = np.random.default_rng(hat).normal(2, 10, len(d))
        rows = ["thoi_gian;deal;position;vao_ra;chieu;khoi_luong;gia;loi;swap;hoa_hong;phu"]
        rows += ["%s;%d;%d;out;1;0.1;1.0;%.2f;0;0;" % (t.strftime("%Y.%m.%d 10:00:00"), i, i, v) for i, (t, v) in enumerate(zip(d, x))]
        (tmp_path / ("%s_vao.csv_lenh_mt5.csv" % ten)).write_text("\n".join(rows), encoding="utf-8")
    ds = [{"id": i, "trang_thai": "DAT_MT5", "ma": [m], "phong_cach": [pc], "mt5": [{"ket_luan": "ĐẠT", "ten": t, "lai_kep_pct_nam": 20}]}
          for i, m, pc, t in (("a", "GBPCAD", "trend", "od_a_XM_CSV"), ("b", "EURUSD", "mean_reversion", "od_b_XM_CSV"),
                              ("c", "GOLD", "breakout", "od_c_XM_CSV"))]
    dm = G.danh_muc(ds, {"tuong_quan_toi_da": 0.3, "nam_toi_thieu": 1.5}, thu_muc=tmp_path, in_ra=lambda *a: None)
    nhom = [set(m["he"]) for m in dm]
    assert {"a", "b"} in nhom and {"b", "c"} in nhom
    assert {"a", "c"} not in nhom                       # a va c cung chuoi -> tuong quan 1 -> loai
    m = next(m for m in dm if set(m["he"]) == {"a", "b"})
    assert m["von"] == 2000.0 and m["so_nam"] > 2 and 0 <= m["sut_giam_pct"] < 100 and "nhan_dat_cuoi_dd_dong_lenh" in m
    _ = r


def test_chon_viec_od_day_chuyen():
    now = time.time()
    tt = {}
    assert DP.chon_viec_od(5, 100, 10, 0, CFG, tt, now)[0] == "python"         # MT5 doi -> Python truoc
    assert DP.chon_viec_od(5, 100, 0, 0, CFG, tt, now)[0] == "ghep"            # het Python -> ghep cheo
    assert DP.chon_viec_od(5, 100, 0, 0, CFG, {"ghep_luc_xong": now - 60}, now)[0] == "dich"   # ghep dang nghi -> dich
    assert DP.chon_viec_od(5, 100, 0, 999, CFG, tt, now)[0] == "dich"          # ghep du tran ton
    assert DP.chon_viec_od(80, 100, 10, 0, CFG, tt, now)[0] == "dich"          # MT5 du -> dich
    assert DP.chon_viec_od(80, 0, 10, 0, CFG, tt, now)[0] == "python"
    assert DP.chon_viec_od(80, 0, 0, 0, CFG, tt, now)[0] == "ghep"
    assert DP.chon_viec_od(80, 0, 0, 0, CFG, {"ghep_luc_xong": now}, now)[0] is None
    tat = dict(CFG, vong_lap={"bat": False})
    assert DP.chon_viec_od(5, 3, 10, 0, tat, tt, now)[0] == "dich"
    assert "toi_uu" in " ".join(DP.lenh_od("python", CFG)) and "sinh_mt5" in " ".join(DP.lenh_od("python", CFG))
    assert DP.lenh_od("ghep", CFG)[:2] == ["-m", "nhan.ghep_cheo"]


def test_san_o_c_d_chan_seeker_va_e_khong_tinh():
    d = {"ram_trong_gb": 16.0, "cpu_pct": 40.0, "slot_ban": 0, "tai_ve_trong_gb": 200.0, "o_trong_gb": {"C:": 5.2, "D:": 30.0, "E:": 1.0}}
    assert DP.o_duoi_san(d, CFG) == ["C:"]
    ok, ly = DP.nen_chay_seeker(d, CFG, 5, 0, {}, False, time.time())
    assert not ok and "C:" in ly
    d["o_trong_gb"]["C:"] = 9.0
    assert DP.o_duoi_san(d, CFG) == []


def test_terminal_bo_roi_chi_tester_dung_pid():
    now = time.time()
    la = lambda exe, cmd: "mt5_tester" in exe.lower() or "/config:" in cmd.lower()      # noqa: E731
    ds = [{"pid": 1, "exe": r"D:\mt5_tester\p1\terminal64.exe", "cmd": "terminal64.exe /portable", "tao": now - 3600},
          {"pid": 2, "exe": r"D:\mt5_tester\p2\terminal64.exe", "cmd": "terminal64.exe /portable /config:x.ini", "tao": now - 3600},
          {"pid": 3, "exe": r"C:\Program Files\XM Global MT5\terminal64.exe", "cmd": "terminal64.exe", "tao": now - 99999},
          {"pid": 4, "exe": r"D:\mt5_tester\p3\terminal64.exe", "cmd": "/portable /config:y.ini", "tao": now - 8 * 3600},
          {"pid": 5, "exe": r"D:\mt5_tester\p4\terminal64.exe", "cmd": "terminal64.exe /portable", "tao": now - 60}]
    r = DP.terminal_bo_roi(ds, now, CFG, la_tester=la)
    assert sorted(x["pid"] for x in r) == [1, 4]            # XM chinh (3) khong bao gio; dang test (2), moi mo (5) giu
    src = (GOC / "may_nha_toi_nay" / "dieu_phoi_may_nha.py").read_text(encoding="utf-8")
    assert '"taskkill"' not in src and "'taskkill'" not in src          # khong goi taskkill (giet theo ten)
    assert "shutdown" not in src.lower()


def test_cau_hinh_vong_lap_giu_luat_cung():
    assert CFG["ram_toi_thieu_gb"] >= 4.0 and CFG["uu_tien"] == "Normal"
    assert CFG["suc_khoe"]["san_o_gb"] >= 6.0 and "E" in CFG["suc_khoe"]["o_lanh"]
    assert CFG["ghep_cheo"]["tran_ton"] > 0 and CFG["ghep_cheo"]["tran_moi_luot"] > 0


def test_so_co_che_commit_khong_chua_ma():
    p = SO.TEP
    if p.exists():
        for dong in p.read_text(encoding="utf-8").splitlines()[:2000]:
            r = json.loads(dong)
            assert "tin_hieu" not in r and "specs" not in json.dumps(r) and "def tin_hieu" not in dong
