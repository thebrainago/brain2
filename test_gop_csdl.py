# -*- coding: utf-8 -*-
"""test_gop_csdl.py - goi may nha GOP (khong ghi de) trang_thai.sqlite + cache dich; the DAT khong bi ha cap."""
import json
import sqlite3
import zipfile

from nhan import gop_csdl as G
from nhan import ong_dan as OD


def _the(cn, i, buoc, tt, dich=None, luc="2026-10-20T10:00:00"):
    t = {"id": i, "loai": "he_hoan_thien"}
    if dich:
        t["dich_llm"] = {"trang_thai": dich}
    with cn:
        OD._luu(cn, t, buoc, tt)
        cn.execute("UPDATE the SET cap_nhat=? WHERE id=?", (luc, i))


def _doc(p, i):
    cn = sqlite3.connect(str(p))
    r = cn.execute("SELECT buoc, json FROM the WHERE id=?", (i,)).fetchone()
    cn.close()
    return r[0], json.loads(r[1])


def test_gop_db_khong_ha_cap_dat_va_giu_nhat_ky(tmp_path):
    nha, box = tmp_path / "nha.sqlite", tmp_path / "box.sqlite"
    cn, cb = OD._db(nha), OD._db(box)
    _the(cn, "dat_nha", "quyet_dinh", "PYTHON_LLM", "DAT", "2026-10-20T20:30:00")   # nha da DAT
    _the(cb, "dat_nha", "sinh_mt5", "CHO", None, "2026-10-20T23:00:00")             # box: xa hon, moi hon, chua DAT
    _the(cn, "tien", "dich_llm", "LLM", "HONG")
    _the(cb, "tien", "toi_uu", "XONG", "HONG")                                       # box tien xa hon -> thang
    _the(cn, "moi_hon", "toi_uu", "A", None, "2026-10-20T10:00:00")
    _the(cb, "moi_hon", "toi_uu", "B", None, "2026-10-20T12:00:00")                  # cung buoc, moi hon -> thang
    _the(cn, "cu_hon", "toi_uu", "A", None, "2026-10-20T12:00:00")
    _the(cb, "cu_hon", "toi_uu", "B", None, "2026-10-20T10:00:00")
    _the(cb, "chi_box", "nhan", "MOI")
    _the(cb, "box_dat", "quyet_dinh", "SPEC_DSL", "DAT")
    _the(cn, "box_dat", "loc", "X", "HONG")                                          # DAT o box thang buoc xa hon
    OD._ghi_nk(cn, "dich_llm", "dat_nha", "DAT nha"); OD._ghi_nk(cb, "dich_llm", "x", "DAT box")
    cn.commit(); cb.commit(); cn.close(); cb.close()
    r = G.gop_db(nha, box)
    assert r["the_moi"] == 1 and r["giu_vi_dat"] == 1 and r["nhat_ky_them"] == 1 and "sao_luu" in r
    assert _doc(nha, "dat_nha")[1]["dich_llm"]["trang_thai"] == "DAT"
    assert _doc(nha, "tien")[0] == "toi_uu"
    assert _doc(nha, "box_dat")[1]["dich_llm"]["trang_thai"] == "DAT"
    c = sqlite3.connect(str(nha))
    assert dict(c.execute("SELECT id, trang_thai FROM the WHERE id IN ('moi_hon','cu_hon')").fetchall()) == \
        {"moi_hon": "B", "cu_hon": "A"}
    assert {x[0] for x in c.execute("SELECT ghi FROM nhat_ky")} == {"DAT nha", "DAT box"}
    c.close()
    r2 = G.gop_db(nha, box, sao_luu=False)                                           # gop lai: khong nhan doi
    assert r2["the_moi"] == 0 and r2["the_thay"] == 0 and r2["nhat_ky_them"] == 0


def test_gop_cache_giu_ban_tot_va_lich_su(tmp_path):
    d, n = tmp_path / "d", tmp_path / "n"
    d.mkdir(); n.mkdir()
    w = lambda p, x: p.write_text(json.dumps(x), encoding="utf-8")  # noqa: E731
    w(d / "a.json", {"trang_thai": "OK", "luc": "2026-10-20T20:00", "model": "max", "python": "def tin_hieu(df): pass",
                     "hong_theo_model": {"max": "IT_LENH"}})
    w(n / "a.json", {"trang_thai": "OK", "luc": "2026-10-19T20:00", "model": "flash", "spec": [],
                     "hong_theo_model": {"flash": "KHONG_RA_SPEC_PY"}})                # cu hon -> giu ban nha
    w(d / "b.json", {"trang_thai": "OK", "luc": "2026-10-19", "spec": [{"x": 1}]})
    w(n / "b.json", {"trang_thai": "OK", "luc": "2026-10-21", "spec": []})            # moi hon nhung mat ma -> giu
    w(n / "c.json", {"trang_thai": "OK", "luc": "2026-10-21"})
    r = G.gop_cache(d, n)
    a = json.loads((d / "a.json").read_text())
    assert a["model"] == "max" and a["hong_theo_model"] == {"max": "IT_LENH", "flash": "KHONG_RA_SPEC_PY"}
    assert json.loads((d / "b.json").read_text())["spec"] == [{"x": 1}]
    assert r["cache_moi"] == 1 and (d / "c.json").exists()


def test_goi_va_nhap_goi_qua_duong_gop_ca_tho_box(tmp_path, monkeypatch):
    from nhan import dich_llm as DL
    from nhan import goi_may_nha as GM
    box = tmp_path / "box"
    (box / "data" / "ong_dan" / "dich_llm").mkdir(parents=True)
    monkeypatch.setattr(GM, "GOC", box); monkeypatch.setattr(DL, "GOC", box)
    cb = OD._db(box / "tt.sqlite")
    _the(cb, "x", "nhan", "MOI")
    cb.commit()
    tb = OD._db(box / "data" / "ong_dan" / "tho_box.sqlite")                       # executor phu tren box
    _the(tb, "x", "quyet_dinh", "PYTHON_LLM", "DAT")
    tb.commit(); tb.close()
    (box / "data" / "ong_dan" / "dich_llm" / "h.json").write_text('{"trang_thai": "OK", "luc": "1"}')
    h = tmp_path / "hang.jsonl"; h.write_text("")
    r = GM.dong_goi(tmp_path / "goi", h, cn=cb, kem_gia=False)
    nha = tmp_path / "nha"
    with zipfile.ZipFile(r["zip"]) as z:
        n = set(z.namelist())
        assert "data/ong_dan/trang_thai.sqlite" not in n and "data/ong_dan/goi_vao/tho_box.sqlite" in n
        z.extractall(nha)
    tt = nha / "data" / "ong_dan" / "trang_thai.sqlite"
    cn = OD._db(tt)
    _the(cn, "nha_rieng", "toi_uu", "XONG", "DAT")
    cn.commit(); cn.close()
    ra = G.nhap_goi(nha / "data" / "ong_dan" / "goi_vao", tt, nha / "data" / "ong_dan" / "dich_llm")
    assert len(ra["db"]) == 2 and ra["cache"]["cache_moi"] == 1
    assert _doc(tt, "x")[1]["dich_llm"]["trang_thai"] == "DAT" and _doc(tt, "nha_rieng")[0] == "toi_uu"
