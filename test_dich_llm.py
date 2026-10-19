# -*- coding: utf-8 -*-
"""test_dich_llm.py - cau LLM (thu tu lay khoa, model du phong, khong lo khoa) + buoc dich_llm (cache, kiem tu dong,
ghi trang thai) + goi zip may nha. MOI loi goi mang dung CLIENT GIA; khong doc cc-switch that."""
import json
import sqlite3
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from nhan import cau_llm as LLM
from nhan import dich_llm as DL
from nhan import hop_cat_llm as HC
from nhan import ong_dan as OD

KHOA_GIA = "khoa-gia-cho-test-0123456789"


@pytest.fixture(autouse=True)
def _sach(monkeypatch, tmp_path):
    monkeypatch.setattr(LLM, "CC_SWITCH_DB", tmp_path / "khong_co_cc_switch.db")
    for k in ("AIBOX_API_KEY", "BRAIN_LLM_PROXY", "AIBOX_BASE_URL", "BRAIN_LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)
    for k in list(LLM.THONG_KE):
        LLM.THONG_KE[k] = {} if k == "theo_model" else 0


def _gia(n=1500, hat=7):
    r = np.random.default_rng(hat)
    x = 1.0 + np.cumsum(r.normal(0, 0.0012, n))
    i = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": x, "high": x + 4e-4, "low": x - 4e-4, "close": x}, index=i)


def _db_cc(p: Path, ten="AI Box (aibox)", khoa="khoa-cc-gia"):
    cn = sqlite3.connect(str(p))
    cn.execute("CREATE TABLE providers (name TEXT, settings_config TEXT)")
    cn.execute("INSERT INTO providers VALUES (?,?)", ("khac", json.dumps({"auth": {"OPENAI_API_KEY": "x"}})))
    cn.execute("INSERT INTO providers VALUES (?,?)", (ten, json.dumps(
        {"auth": {"OPENAI_API_KEY": khoa}, "config": 'base_url = "http://127.0.0.1:8317/v1"\nmodel = "qwen-cc"\n'})))
    cn.commit(); cn.close()


# ------------------------------------------------------------------ cau hinh + khoa
def test_cau_hinh_qwen_truoc_tri_tue(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "tri_tue.json").write_text(json.dumps({"model_openai": "m_tt", "max_tokens": 5, "timeout_giay": 7}))
    c = LLM.cau_hinh(tmp_path)
    assert c["model"] == "m_tt" and c["max_tokens"] == 5 and c["model_du_phong"] == "qwen3.6-flash" and c["temperature"] == 0
    (tmp_path / "config" / "qwen.json").write_text(json.dumps({"model": "qwen3.7-flash", "model_du_phong": "qwen3.6-flash",
                                                               "max_tokens": 32000, "timeout_giay": 600, "temperature": 0}))
    c = LLM.cau_hinh(tmp_path)
    assert (c["model"], c["model_du_phong"], c["max_tokens"], c["timeout_giay"]) == ("qwen3.7-flash", "qwen3.6-flash", 32000, 600)
    # cau hinh that cua repo: dung model chinh / du phong nhu chu du an dat
    r = LLM.cau_hinh()
    assert r["model"] == "qwen3.7-flash" and r["model_du_phong"] == "qwen3.6-flash" and r["temperature"] == 0


def test_thu_tu_lay_khoa(tmp_path, monkeypatch):
    c = dict(LLM.MAC_DINH)
    assert LLM.duong(c)["nguon"] == "" and not LLM.co_khoa(c)
    monkeypatch.setenv("BRAIN_LLM_PROXY", "https://proxy.vd/v1/")
    d = LLM.duong(c)
    assert d["nguon"] == "proxy" and d["khoa"] == "" and d["base_url"] == "https://proxy.vd/v1"
    db = tmp_path / "cc.db"; _db_cc(db)
    monkeypatch.setattr(LLM, "CC_SWITCH_DB", db)
    d = LLM.duong(c)
    assert d["nguon"].startswith("cc_switch") and d["khoa"] == "khoa-cc-gia"
    assert d["base_url"] == "https://api.ai-box.vn/v1"            # bo cau noi 127.0.0.1:8317 nhu qwen/mo_hinh.py
    monkeypatch.setenv("AIBOX_API_KEY", KHOA_GIA)
    d = LLM.duong(c)
    assert d["nguon"] == "bien_moi_truong" and d["khoa"] == KHOA_GIA
    # provider khac ten -> khong lay
    db2 = tmp_path / "cc2.db"; _db_cc(db2, ten="deepseek")
    assert LLM.tu_cc_switch("aibox", db2) == {}


class Client:
    """Client gia: ghi lai moi lan goi; `tra(model, noi_dung) -> (ma, json|str)`."""
    def __init__(self, tra):
        self.tra, self.lan = tra, []

    def __call__(self, url, headers, body, timeout):
        b = json.loads(body.decode())
        self.lan.append({"url": url, "auth": headers.get("Authorization"), "model": b["model"], "temperature": b["temperature"],
                         "max_tokens": b["max_tokens"]})
        return self.tra(b["model"], b["messages"][-1]["content"])


def _ok(txt, tv=100, tr=50):
    return 200, {"choices": [{"message": {"content": txt}}], "usage": {"prompt_tokens": tv, "completion_tokens": tr}}


def test_goi_403_sang_du_phong_va_khong_lo_khoa(monkeypatch):
    monkeypatch.setenv("AIBOX_API_KEY", KHOA_GIA)
    c = dict(LLM.MAC_DINH, so_lan_thu_lai=2)
    cl = Client(lambda m, nd: (403, "forbidden for key %s" % KHOA_GIA) if m == "qwen3.7-flash" else _ok('{"a": 1}'))
    r = LLM.goi("xin chao", client=cl, c=c)
    assert r["trang_thai"] == "OK" and r["model"] == "qwen3.6-flash" and "(du phong)" in r["ghi_chu"]
    assert [x["model"] for x in cl.lan] == ["qwen3.7-flash", "qwen3.6-flash"]      # 403: khong thu lai cung model
    assert cl.lan[0]["auth"] == "Bearer " + KHOA_GIA and cl.lan[0]["temperature"] == 0
    assert LLM.THONG_KE["doi_du_phong"] == 1 and LLM.THONG_KE["so_lan_goi"] == 2 and LLM.THONG_KE["token_ra"] == 50
    # het quota o ca hai -> LOI, thong bao da che khoa
    cl2 = Client(lambda m, nd: (429, "insufficient quota, key=%s" % KHOA_GIA))
    r2 = LLM.goi("x", client=cl2, c=c)
    assert r2["trang_thai"] == "LOI" and KHOA_GIA not in r2["ghi_chu"] and "***" in r2["ghi_chu"] and len(cl2.lan) == 2
    # loi tam (500) -> thu lai cung model
    n = {"k": 0}

    def tam(m, nd):
        n["k"] += 1
        return (500, "loi tam") if n["k"] == 1 else _ok("{}")
    cl3 = Client(tam)
    assert LLM.goi("x", client=cl3, c=c)["model"] == "qwen3.7-flash" and len(cl3.lan) == 2


def test_khong_khoa_khong_goi_mang():
    cl = Client(lambda m, nd: _ok("{}"))
    assert LLM.goi("x", client=cl)["trang_thai"] == "CHUA_CHAY_DUOC" and cl.lan == []


# ------------------------------------------------------------------ hop cat + kiem tu dong
def test_hop_cat_chan_ma_nguy_hiem_va_nhin_truoc():
    df = _gia(800)
    assert HC.kiem_ast("import os\ndef tin_hieu(df):\n    return 0")
    assert any("open" in x for x in HC.kiem_ast("def tin_hieu(df):\n    open('x')\n    return 0"))
    assert any("shift am" in x for x in HC.kiem_ast("def tin_hieu(df):\n    return df.close.shift(-1)"))
    assert any("__class__" in x for x in HC.kiem_ast("def tin_hieu(df):\n    return df.__class__"))
    assert any("to_csv" in x for x in HC.kiem_ast("def tin_hieu(df):\n    df.to_csv('a')\n    return 0"))
    ok = "def tin_hieu(df):\n    m = df['close'].rolling(30).mean()\n    return np.where(df['close'] > m, 1, -1)\n"
    assert DL.kiem_tra({"python": ok}, df)["dat"]
    nhin = "def tin_hieu(df):\n    x = df['close'].to_numpy()\n    return np.sign(np.roll(x, -1) - x)\n"
    k = DL.kiem_tra({"python": nhin}, df)
    assert not k["dat"] and any("NHIN TRUOC" in x for x in k["ly_do"])
    it = "def tin_hieu(df):\n    return np.zeros(len(df))\n"
    assert any("lenh" in x for x in DL.kiem_tra({"python": it}, df)["ly_do"])
    # tien trinh con KHONG thay bien moi truong co khoa
    import os
    os.environ["AIBOX_API_KEY"] = KHOA_GIA
    try:
        doc = "def tin_hieu(df):\n    return np.ones(len(df))\n"
        assert HC.chay(doc, df.iloc[:50], [])["ok"]
        env_ma = "def tin_hieu(df):\n    return [len(str(globals))] * len(df)\n"
        assert not HC.chay(env_ma, df.iloc[:50], [])["ok"]
    finally:
        del os.environ["AIBOX_API_KEY"]


SPEC_RSI = [{"ten": "mua", "chieu": 1, "vao": [{"trai": {"chi_bao": "rsi", "n": 14}, "phep": "<", "phai": {"hang": 30}}]},
            {"ten": "ban", "chieu": -1, "vao": [{"trai": {"chi_bao": "rsi", "n": 14}, "phep": ">", "phai": {"hang": 70}}]}]
PY_SMA = "def tin_hieu(df):\n    m = df['close'].rolling(40).mean()\n    return np.where(df['close'] > m, 1, np.where(df['close'] < m, -1, 0))\n"


def _tra_theo_ma(m, nd):
    if "MARKER_SPEC" in nd:
        return _ok(json.dumps({"loai": "he_hoan_thien", "spec": SPEC_RSI, "chua_dich": []}), 900, 300)
    if "MARKER_PY" in nd:
        return _ok("Day la ket qua:\n" + json.dumps({"loai": "he_hoan_thien", "spec": [], "python": PY_SMA}), 800, 200)
    if "MARKER_NHIN" in nd:
        return _ok(json.dumps({"spec": [], "python": "def tin_hieu(df):\n    return np.sign(df['close'].shift(-2) - df['close'])\n"}))
    return _ok("khong phai json")


def _the(cn, goc, id_, noi_dung, ten_tep, nen_tang="Python", tt="LLM", duong="llm", top=False, ly=""):
    f = goc / "data" / "seeker" / ten_tep
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(noi_dung, encoding="utf-8")
    t = {"id": id_, "loai": "he_hoan_thien", "nen_tang": nen_tang, "uu_tien": 2, "duong_dich": duong, "ly_do_duong": ly,
         "nguon": {"tep": "data/seeker/" + ten_tep}, "seeker": {"top28": top}}
    with cn:
        OD._luu(cn, t, "quyet_dinh", tt)
    return t


def test_dich_llm_cache_kiem_va_ghi_trang_thai(tmp_path, monkeypatch):
    monkeypatch.setattr(DL, "GOC", tmp_path)
    monkeypatch.setattr(DL, "CACHE", tmp_path / "data" / "ong_dan" / "dich_llm")
    monkeypatch.setattr(DL, "BAO_CAO", tmp_path / "DICH_LLM.md")
    monkeypatch.setattr(DL, "gia_mau", lambda cfg=None, n=3000: (_gia(1500), "gia gia lap test"))
    monkeypatch.setenv("AIBOX_API_KEY", KHOA_GIA)
    cn = OD._db(tmp_path / "tt.sqlite")
    _the(cn, tmp_path, "py_spec", "class S(IStrategy): MARKER_SPEC", "a.py")
    _the(cn, tmp_path, "py_py", "MARKER_PY strategy", "b.py", top=True)
    _the(cn, tmp_path, "pine_nhin", "//@version=5 MARKER_NHIN", "c.pine", nen_tang="TradingView")
    _the(cn, tmp_path, "ea_cung_ma", "class S(IStrategy): MARKER_SPEC", "d.mq5", nen_tang="MQL5", tt="MT5_TRUC_TIEP",
         duong="mt5_truc_tiep", ly="bo dich khong ra chan (x) -> chay thang")
    _the(cn, tmp_path, "rac", "MARKER_KHAC", "e.py")
    t_thieu = {"id": "thieu_ma", "loai": "he_hoan_thien", "nen_tang": "Python", "duong_dich": "llm",
               "nguon": {"tep": "data/khong_co.py"}}
    with cn:
        OD._luu(cn, t_thieu, "quyet_dinh", "LLM")
    ds = DL.danh_sach_cho(cn)
    assert [x["the"]["id"] for x in ds][0] == "py_py"                     # top 28 truoc
    ids = [x["the"]["id"] for x in ds]
    assert ids[-1] == "ea_cung_ma" and ids.index("thieu_ma") > ids.index("rac")      # LLM truoc EA; thieu ma cuoi nhom
    assert {x["nhom"] for x in ds} == {"llm", "ea_bo_qua"}
    cl = Client(_tra_theo_ma)
    r = DL.buoc_dich_llm(cn, client=cl, luong=2, in_ra=lambda *a: None)
    assert r["cho"] == 6 and r["thieu_ma"] == 1
    assert len(cl.lan) == 4                                                # 2 the cung ma (a.py, d.mq5) -> 1 lan goi
    assert r["dat"] == 3 and r["hong"] == 1 and r["loi_llm"] == 1 and r["goi_moi"] == 4
    assert r["so_lan_goi"] == 4 and r["token_vao"] == 900 + 800 + 100 + 100 and r["token_ra"] == 300 + 200 + 50 + 50
    st = {t["id"]: (b, tt, t) for t, b, tt, _ in OD.cac_the(cn)}
    assert st["py_spec"][:2] == ("quyet_dinh", "SPEC_DSL") and st["py_spec"][2]["tin_hieu"]["kieu"] == "spec"
    assert st["ea_cung_ma"][:2] == ("quyet_dinh", "SPEC_DSL") and st["ea_cung_ma"][2]["duong_dich"] == "spec_dsl"
    assert st["py_py"][:2] == ("quyet_dinh", "PYTHON_LLM") and st["py_py"][2]["tin_hieu"]["kieu"] == "python_llm"
    assert st["pine_nhin"][1] == "LLM" and st["pine_nhin"][2]["dich_llm"]["trang_thai"] == "HONG"
    assert st["rac"][1] == "LLM" and "dich_llm" not in st["rac"][2]          # loi LLM -> thu lai lan sau
    # toi_uu nhan the python_llm: tin hieu chay qua hop cat
    s = OD.tin_hieu(st["py_py"][2], _gia(600), {}, "EURUSD")
    assert len(s) == 600 and set(np.unique(s)) <= {-1, 0, 1} and np.count_nonzero(s) > 0
    # bao cao + nhat ky, khong co khoa
    md = (tmp_path / "DICH_LLM.md").read_text(encoding="utf-8")
    assert "Số lần gọi API | 4" in md and "Token ra | 600" in md and KHOA_GIA not in md
    nk = (tmp_path / "data" / "ong_dan" / "dich_llm" / "nhat_ky.jsonl").read_text(encoding="utf-8")
    assert KHOA_GIA not in nk
    for f in (tmp_path / "data" / "ong_dan" / "dich_llm").glob("*.json"):
        assert KHOA_GIA not in f.read_text(encoding="utf-8")
    # chay lai: the da dich bo qua; the loi LLM goi lai 1 lan; ma da cache khong goi
    cl2 = Client(_tra_theo_ma)
    r2 = DL.buoc_dich_llm(cn, client=cl2, in_ra=lambda *a: None)
    assert len(cl2.lan) == 1 and r2["cho"] == 2
    # the moi cung ma voi the da dich -> lay cache, khong goi
    _the(cn, tmp_path, "py_spec_2", "class S(IStrategy): MARKER_SPEC", "f.py")
    cl3 = Client(_tra_theo_ma)
    r3 = DL.buoc_dich_llm(cn, client=cl3, gioi_han=1, in_ra=lambda *a: None)
    assert cl3.lan == [] and r3["tu_cache"] == 1 and r3["dat"] == 1


def test_dich_llm_khong_khoa_chua_chay_duoc(tmp_path, monkeypatch):
    monkeypatch.setattr(DL, "GOC", tmp_path)
    monkeypatch.setattr(DL, "BAO_CAO", tmp_path / "DICH_LLM.md")
    cn = OD._db(tmp_path / "tt.sqlite")
    _the(cn, tmp_path, "a", "x", "a.py")
    r = DL.buoc_dich_llm(cn, in_ra=lambda *a: None)
    assert r["chua_chay_duoc"] == 1 and "CHƯA CHẠY ĐƯỢC" in (tmp_path / "DICH_LLM.md").read_text(encoding="utf-8")


def test_quyet_dinh_python_cho_dich_llm_khong_goi_mang(tmp_path, monkeypatch):
    monkeypatch.setattr(OD, "GOC", tmp_path)
    f = tmp_path / "data" / "s.py"; f.parent.mkdir(parents=True); f.write_text("def populate_entry_trend(): pass")
    t = OD.quyet_dinh_mot({"id": "x", "loai": "he_hoan_thien", "nen_tang": "Python", "nguon": {"tep": "data/s.py"}})
    assert t["duong_dich"] == "llm" and "dich_llm" in t["ly_do_duong"]


def test_goi_may_nha_kem_the_llm_va_db(tmp_path, monkeypatch):
    from nhan import goi_may_nha as GM
    monkeypatch.setattr(GM, "GOC", tmp_path)
    monkeypatch.setattr(DL, "GOC", tmp_path)
    cn = OD._db(tmp_path / "tt.sqlite")
    _the(cn, tmp_path, "p1", "MARKER_PY", "p1.py", top=True)
    _the(cn, tmp_path, "p2", "MARKER_SPEC", "p2.pine", nen_tang="TradingView")
    h = tmp_path / "hang.jsonl"; h.write_text("")
    r = GM.dong_goi(tmp_path / "goi", h, cn=cn, kem_gia=False)
    assert r["so_the_cho_dich_llm"] == 2
    with zipfile.ZipFile(r["zip"]) as z:
        n = set(z.namelist())
        man = json.loads(z.read("MANIFEST.json"))
        hd = z.read("HUONG_DAN.md").decode("utf-8")
        db = z.read("data/ong_dan/trang_thai.sqlite")
    assert {"data/seeker/p1.py", "data/seeker/p2.pine", "data/ong_dan/trang_thai.sqlite"} <= n
    assert man["so_the_cho_dich_llm"] == 2 and man["the_cho_dich_llm"][0]["the"] == "p1"
    assert "dich_llm" in hd and "git pull" in hd and "ong_dan.py chay" in hd
    p = tmp_path / "chup.sqlite"; p.write_bytes(db)
    assert sqlite3.connect(str(p)).execute("SELECT COUNT(*) FROM the").fetchone()[0] == 2


def test_gia_goi_cho_may_nha(tmp_path, monkeypatch):
    df = _gia(400)
    monkeypatch.setattr(OD, "GIA_GOI", tmp_path)
    df.to_csv(tmp_path / "ZZZUSD_H1.csv.gz", index_label="time", compression="gzip")
    cfg = {"du_lieu": {"ZZZUSD": "/khong/co.csv"}}
    assert OD.ma_co_du_lieu(cfg) == ["ZZZUSD"]
    g = OD.gia("ZZZUSD", "H1", cfg)
    assert len(g) == 400 and abs(g["close"].iloc[-1] - df["close"].iloc[-1]) < 1e-9
