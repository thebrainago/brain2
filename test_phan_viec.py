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
