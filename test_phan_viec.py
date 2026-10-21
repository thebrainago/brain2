import json
from nhan import phan_viec as PV


def test_nhan_khong_trung(tmp_path):
    p = tmp_path / "so.jsonl"
    assert PV.nhan("dich", [("a", ["t1"]), ("b", ["t2"])], "box", p) == ["a", "b"]
    assert PV.nhan("dich", [("a", ["t1"]), ("c", [])], "nha", p) == ["c"]
    so = PV.doc_so("dich", p)
    assert so == {"a": "box", "b": "box", "c": "nha"}
    assert PV.cua_may_khac("dich", "a", "nha", so) and not PV.cua_may_khac("dich", "a", "box", so)
    assert PV.doc_so("thu_py", p) == {}


def test_hang_box(tmp_path):
    p = tmp_path / "h.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in [
        {"ea": "XL", "ma": "EURUSDmicro", "san": "XM", "ten": "a"},
        {"ea": "NGOAI", "ma": "X", "san": "XM", "ten": "b"},
        {"ea": "XL", "ma": "EURUSDm", "san": "Exness", "ten": "c"}]) + "\nrac\n")
    assert [v["ten"] for v in PV.doc_hang_box(p)] == ["a", "c"]
    assert [v["ten"] for v in PV.doc_hang_box(p, "xm")] == ["a"]


def test_sinh_viec_doc_hang_box(tmp_path, monkeypatch):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "mt5tools"))
    import sinh_viec as SV
    hc = tmp_path / "hc.jsonl"
    hc.write_text(json.dumps({"ea": "XL", "ma": "A", "tf": "H1", "ten": "x", "san": "XM"}) + "\n")
    hb = tmp_path / "hb.jsonl"
    hb.write_text(json.dumps({"ea": "XL", "ma": "B", "tf": "H1", "ten": "y", "san": "XM", "pha": "KIEM_CSV", "diem": 60}) + "\n"
                  + json.dumps({"ea": "XL", "ma": "A", "tf": "H1", "ten": "x", "san": "XM"}) + "\n")
    monkeypatch.setattr(SV, "HANG_CHO_OD", hc)
    monkeypatch.setattr(PV, "HANG_BOX", hb)
    monkeypatch.delenv("BRAIN_HANG_BOX", raising=False)
    assert [v["ten"] for v in SV.tu_ong_dan(hc, san="XM")] == ["x"]
    monkeypatch.setenv("BRAIN_HANG_BOX", "1")
    assert [v["ten"] for v in SV.tu_ong_dan(hc, san="XM")] == ["x", "y"]
