# -*- coding: utf-8 -*-
"""sinh_viec.py - SINH VIEC MT5 TU DONG de hang doi KHONG BAO GIO CAN (vong 27, 13/10/2026). BACKTEST, khong phai tien that.

- Luoi bien the EA `BRAIN_V24_{MRZ,RSI}_Trail_D1` (input moi: InpTF, InpNguongZ, InpRsiThap/Cao, InpMrzN, InpSlATR, InpTrATR, InpGiuToiDa, InpGioVao)
  x moi ma XM co lich su M1 (FX chinh/cheo, kim loai, chi so) x khung D1/H4/H1.
- Hai pha: IS 2016-01-01..2022-12-31 -> chi bien the DAT IS moi duoc xep OOS 2023-01-01..2026-10-01 (giu ngoai mau, khong toi uu tren OOS).
- Uu tien theo gia tri ky vong: diem goc (gan cau hinh da co lai) + thuong "hang xom" cua bien the gan dat (near-miss) + OOS truoc.
- Chong trung: khoa = JSON chuan hoa (ea, ma, khung, tham so, pha). So cai `reports/mt5_lien_tuc/so_cai.jsonl`: MOI lan thu deu ghi -> dem Holm.
"""
from __future__ import annotations

import itertools
import json
import math
import random
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SO_CAI = GOC / "reports" / "mt5_lien_tuc" / "so_cai.jsonl"
IS = ("2016.01.01", "2022.12.31")
OOS = ("2023.01.01", "2026.10.01")
TF = {"D1": 16408, "H4": 16388, "H1": 16385}
MA = ["GBPUSD#", "AUDUSD#", "EURGBP#", "USDCAD#", "EURUSD#", "USDJPY#", "USDCHF#", "NZDUSD#", "AUDCAD#", "EURCAD#",
      "EURJPY#", "GBPJPY#", "AUDNZD#", "AUDCHF#", "GBPAUD#", "NZDCAD#", "EURAUD#", "GBPCAD#", "CADJPY#", "AUDJPY#",
      "EURCHF#", "GBPCHF#", "GOLD.i#", "SILVER.i#", "US500Cash#", "GER40Cash#", "US100Cash#"]
# Ma da do 13/10 co lai (MRZ D1 g2): uu tien cao hon
MA_TOT = {"GBPUSD#": 1.0, "AUDUSD#": 1.0, "EURGBP#": 1.0, "USDCAD#": 0.6}
LUOI = {
    "MRZ": {"InpNguongZ": [1.5, 2.0, 2.5], "InpMrzN": [20, 50, 100]},
    "RSI": {"InpRsiThap": [20, 25, 30], "InpRsiCao": [70, 75, 80]},
    "CHUNG": {"InpTrATR": [1.5, 2.0, 2.5, 3.0], "InpGiuToiDa": [5, 20, 72], "InpGioVao": [0, 1, 2, 3, 4], "InpSlATR": [1.0, 1.5, 2.0]},
}
MAC_DINH = {"InpNguongZ": 2.0, "InpMrzN": 50, "InpRsiThap": 30, "InpRsiCao": 70, "InpTrATR": 2.0, "InpGiuToiDa": 72, "InpGioVao": 2, "InpSlATR": 1.5}
NGUONG_IS = {"pf": 1.25, "lenh": 30, "net": 0.0}
NGUONG_OOS = {"pf": 1.15, "lenh": 15, "net": 0.0}


def khoa(v: dict) -> str:
    return json.dumps({k: v[k] for k in ("ea", "ma", "tf", "ts", "pha")}, sort_keys=True)


def doc_so_cai(p: Path = SO_CAI) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def ghi(r: dict, p: Path = SO_CAI) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def _ts(ea: str, chon: dict) -> dict:
    t = dict(MAC_DINH); t.update(chon)
    keep = ["InpTrATR", "InpGiuToiDa", "InpGioVao", "InpSlATR"] + list(LUOI[ea])
    return {k: t[k] for k in sorted(keep)}


def dat(r: dict, ng: dict) -> bool:
    return (r.get("pf") or 0) >= ng["pf"] and (r.get("lenh") or 0) >= ng["lenh"] and (r.get("net") or -1) > ng["net"]


def diem_goc(ea: str, ma: str, tf: str, ts: dict) -> float:
    d = MA_TOT.get(ma, 0.3) + (0.5 if ea == "MRZ" else 0.3) + {"D1": 0.6, "H4": 0.4, "H1": 0.2}[tf]
    d -= 0.08 * sum(1 for k, v in ts.items() if MAC_DINH.get(k) != v)      # cang xa cau hinh goc cang it ky vong
    if tf != "D1" and ts.get("InpGioVao", 0) not in (0,):
        d -= 5    # gio vao chi co nghia voi D1
    return d


def ung_vien(rng: random.Random, n: int = 4000) -> list[dict]:
    """Mau ngau nhien co dinh hat giong tu khong gian luoi (khong liet ke het ~10^6)."""
    out = []
    for _ in range(n):
        ea = rng.choice(["MRZ", "RSI"]); ma = rng.choice(MA); tf = rng.choices(list(TF), [0.6, 0.25, 0.15])[0]
        chon = {}
        for k, vs in itertools.chain(LUOI[ea].items(), LUOI["CHUNG"].items()):
            if rng.random() < 0.35:
                chon[k] = rng.choice(vs)
        if tf != "D1":
            chon["InpGioVao"] = 0
        ts = _ts(ea, chon)
        out.append({"ea": ea, "ma": ma, "tf": tf, "ts": ts, "pha": "IS", "diem": diem_goc(ea, ma, tf, ts)})
    return out


def hang_xom(v: dict) -> list[dict]:
    """Bien the lech mot tham so mot nac quanh mot near-miss."""
    out = []
    for k, cur in v["ts"].items():
        vs = (LUOI.get(v["ea"], {}) | LUOI["CHUNG"]).get(k)
        if not vs or cur not in vs:
            continue
        i = vs.index(cur)
        for j in (i - 1, i + 1):
            if 0 <= j < len(vs):
                ts = dict(v["ts"]); ts[k] = vs[j]
                if v["tf"] != "D1" and k == "InpGioVao" and vs[j] != 0:
                    continue
                out.append({"ea": v["ea"], "ma": v["ma"], "tf": v["tf"], "ts": ts, "pha": "IS"})
    return out


def lay_viec(n: int = 1, so_cai: list[dict] | None = None, dang_chay: set[str] | None = None, hat: int = 27) -> list[dict]:
    sc = doc_so_cai() if so_cai is None else so_cai
    xong = {khoa(r) for r in sc} | (dang_chay or set())
    hang = []
    for r in sc:   # 1) OOS cho bien the dat IS (cao nhat)
        if r.get("pha") == "IS" and dat(r, NGUONG_IS):
            v = {k: r[k] for k in ("ea", "ma", "tf", "ts")}; v.update(pha="OOS", diem=100 + (r.get("pf") or 0))
            hang.append(v)
        elif r.get("pha") == "IS" and (r.get("pf") or 0) >= 1.1 and (r.get("lenh") or 0) >= 20:   # 2) near-miss -> hang xom
            for h in hang_xom(r):
                h["diem"] = 10 + (r.get("pf") or 0)
                hang.append(h)
    hang += tu_python_box()
    hang += ung_vien(random.Random(hat + len(sc) // 500))
    hang.sort(key=lambda v: -v["diem"])
    out, thay = [], set()
    for v in hang:
        k = khoa(v)
        if k in xong or k in thay:
            continue
        thay.add(k); out.append(v)
        if len(out) >= n:
            break
    return out


BOX = GOC / "reports" / "mt5_lien_tuc" / "box_luoi_python.json"


def tu_python_box(p: Path = BOX, toi_da: int = 300) -> list[dict]:
    """Ung vien DAT ca IS va OOS trong mo phong Python tren box -> xac nhan bang MT5 real ticks (diem 50+)."""
    try:
        u = json.loads(p.read_text(encoding="utf-8"))["tong_ket"]["ung_vien_ca_hai"]
    except Exception:
        return []
    out = []
    for x in u[:toi_da]:
        ts = _ts(x["ea"], {k: v for k, v in x["ts"].items()})
        out.append({"ea": x["ea"], "ma": x["ma"], "tf": x["tf"], "ts": ts, "pha": "IS", "diem": 50 + min(x["IS"]["pf"], x["OOS"]["pf"])})
    return out


def file_set(v: dict, goc: str) -> str:
    """Noi dung .set: .set goc cua EA + tham so bien the + khung."""
    dong = [x for x in goc.splitlines() if x.strip() and x.split("=")[0] not in v["ts"] and not x.startswith("InpTF=")]
    dong += ["%s=%s" % kv for kv in sorted(v["ts"].items())] + ["InpTF=%d" % TF[v["tf"]], "InpLogChung=false"]
    return "\n".join(x for x in dong if not x.startswith("InpLogChung=true")) + "\n"


def p_gia_tri(r_lenh: list[float]) -> float:
    """p mot phia (TB > 0) xap xi chuan tu loi tung lenh."""
    n = len(r_lenh)
    if n < 5:
        return 1.0
    m = sum(r_lenh) / n; sd = math.sqrt(sum((x - m) ** 2 for x in r_lenh) / (n - 1)) or 1e-12
    return 0.5 * math.erfc((m / (sd / math.sqrt(n))) / math.sqrt(2))


def holm(so_cai: list[dict], alpha: float = 0.05) -> dict:
    """Holm tren MOI lan thu IS (m = tong so lan thu). Tra {khoa: dat_holm}."""
    is_ = sorted([r for r in so_cai if r.get("pha") == "IS"], key=lambda r: r.get("p", 1.0))
    m = len(is_); out = {}; dung = False
    for i, r in enumerate(is_):
        ok = (not dung) and r.get("p", 1.0) <= alpha / (m - i)
        dung = dung or not ok
        out[khoa(r)] = ok
    return out


def tong_ket(so_cai: list[dict] | None = None) -> dict:
    sc = doc_so_cai() if so_cai is None else so_cai
    h = holm(sc)
    oos = {khoa({**r, "pha": "IS"}): r for r in sc if r.get("pha") == "OOS"}
    ung = []
    for r in sc:
        if r.get("pha") == "IS" and dat(r, NGUONG_IS):
            o = oos.get(khoa(r))
            if o and dat(o, NGUONG_OOS):
                ung.append({"ea": r["ea"], "ma": r["ma"], "tf": r["tf"], "ts": r["ts"], "IS": {k: r.get(k) for k in ("net", "lenh", "pf", "dd")},
                            "OOS": {k: o.get(k) for k in ("net", "lenh", "pf", "dd")}, "holm": h.get(khoa(r), False)})
    return {"so_lan_thu": len(sc), "so_IS": sum(r.get("pha") == "IS" for r in sc), "so_OOS": sum(r.get("pha") == "OOS" for r in sc),
            "dat_IS": sum(1 for r in sc if r.get("pha") == "IS" and dat(r, NGUONG_IS)), "ung_vien_ca_hai": ung}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "tong-ket":
        print(json.dumps(tong_ket(), ensure_ascii=False, indent=1))
    else:
        for v in lay_viec(int(sys.argv[1]) if len(sys.argv) > 1 else 8):
            print(json.dumps(v, ensure_ascii=False))
