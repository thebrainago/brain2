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
import os
from collections import Counter
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
# 17/10/2026 (chu du an: chi can giao dich co loi nhuan): ha tu pf 1,25 / 30 lenh (IS) va pf 1,15 / 15 lenh (OOS).
# He D1 chi 4-8 lenh/nam nen nguong 30 lenh IS tung chan nhieu cau hinh khong bao gio duoc chay OOS.
NGUONG_IS = {"pf": 1.0, "lenh": 10, "net": 0.0}
NGUONG_OOS = {"pf": 1.0, "lenh": 5, "net": 0.0}
# Ba yeu to cot loi cua chu du an (17/10/2026): lai sau phi, sut giam <= 80 %, lai >= 10 %/nam. Lot co gian (EA chay
# lot co dinh 0,01 tren von 10.000) -> quy tuyen tinh ve muc lot cho sut giam = 80 %.
# 18/10/2026: nguong doc tu MOT cho (config/nguong.json, tang "cuoi"). Phep nhan lot tuyen tinh o day chi la NHAN tham khao.
import sys as _sys  # noqa: E402
_sys.path.insert(0, str(GOC))
from nhan import nguong as _NG  # noqa: E402
VON, LAI_TOI_THIEU, SUT_GIAM_TOI_DA = 10000.0, _NG.lai_toi_thieu("cuoi"), _NG.sut_giam_toi_da("cuoi")


def _nam(pha: str) -> float:
    a, b = IS if pha == "IS" else OOS
    return (int(b[:4]) - int(a[:4])) + (int(b[5:7]) - int(a[5:7])) / 12.0 + (int(b[8:10]) - int(a[8:10])) / 365.0


def _nam_tu_ky_bc(ky_bc: str | None) -> float | None:
    """Parse MT5 Period string e.g. 'H1 (2019.01.01 - 2026.10.01)' -> years."""
    import re
    m = re.search(r"(\d{4}\.\d{2}\.\d{2})\s*-\s*(\d{4}\.\d{2}\.\d{2})", str(ky_bc or ""))
    if not m:
        return None
    a, b = m.group(1), m.group(2)
    yrs = (int(b[:4]) - int(a[:4])) + (int(b[5:7]) - int(a[5:7])) / 12.0 + (int(b[8:10]) - int(a[8:10])) / 365.0
    return yrs if yrs > 0.01 else None


def cot_loi(r: dict) -> dict | None:
    """Lai %/nam = net/von / years (ky_bc or IS/OOS window). Pass cuoi: net>0, DD<=80%, APY>=10%/yr (lot that)."""
    import re
    m = re.search(r"\(([\d.]+)%\)", str(r.get("dd") or ""))
    if r.get("lot_csv_nghi_ngo"):
        return None  # pre-patch CSV-lot inflate; ignore in learning
    if m is None or r.get("net") is None:
        return None
    pha = str(r.get("pha") or "")
    nam = _nam_tu_ky_bc(r.get("ky_bc"))
    if nam is None:
        if pha in ("IS", "OOS"):
            nam = _nam(pha)
        else:
            return None
    von = float(r.get("von") or VON) or VON
    lai = float(r["net"]) / von / nam * 100.0
    dd = float(m.group(1))
    o80 = lai * SUT_GIAM_TOI_DA / dd if dd > 0 else None
    dat_lt = bool(_NG.dat(lai, dd, "cuoi")["dat"] and float(r["net"]) > 0)
    return {"lai_pct_nam": round(lai, 3), "apy_pct": round(lai, 3), "nam": round(nam, 3), "von": von,
            "sut_giam_pct": dd, "lai_pct_nam_o_dd80": round(o80, 1) if o80 is not None else None,
            "he_so_lot_dd80": round(SUT_GIAM_TOI_DA / dd, 1) if dd > 0 else None,
            "dat": bool(lai > 0 and dd <= SUT_GIAM_TOI_DA and lai >= LAI_TOI_THIEU),
            "dat_pass_cuoi": dat_lt,  # net>0, DD<=80, APY>=10 at actual lot
            "kieu_dat": "net/von/years_ky_bc",
            "dat_lot_that": dat_lt}


def khoa(v: dict) -> str:
    d = {k: v.get(k) for k in ("ea", "ma", "tf", "ts", "pha")}
    if v.get("tang") == 1:          # 20/10/2026: viec loc tang 1 (OHLC M1) khac khoa voi viec real tick cung thong so
        d["tang"] = 1
    return json.dumps(d, sort_keys=True)


def la_viec_hai_tang(v: dict) -> bool:
    """Viec ong dan chay don (khong toi uu) cua BRAIN_XuLiLenh -> qua loc hai tang."""
    return v.get("nguon") == "ong_dan" and v.get("ea") == "XL" and not v.get("toi_uu") and v.get("pha") != "V2_GEN_KIEM"


def doc_so_cai(p: Path = SO_CAI) -> list[dict]:
    """Doc so_cai.jsonl; bo qua / quarantine dong JSON hong (ghi song song / cat nut)."""
    if not p.exists():
        return []
    out: list[dict] = []
    bad: list[str] = []
    try:
        text = p.read_text(encoding="utf-8-sig")
    except Exception:
        text = p.read_bytes().decode("utf-8", "replace")
        if text.startswith("\ufeff"):
            text = text[1:]
    for i, x in enumerate(text.splitlines(), 1):
        s = x.strip()
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except json.JSONDecodeError:
            bad.append("%d\t%s" % (i, s[:500]))
    if bad:
        q = p.with_name(p.stem + "_bad_lines.jsonl")
        try:
            with open(q, "a", encoding="utf-8", newline="\n") as fq:
                for b in bad:
                    fq.write(b + "\n")
        except Exception:
            pass
    return out


def ghi(r: dict, p: Path = SO_CAI) -> None:
    """Append 1 dong JSON; lock file (Windows msvcrt) de tranh cat dong khi nhieu slot ghi."""
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.stat().st_size:
        raw = p.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            p.write_bytes(raw[3:])
    line = json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        try:
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            try:
                f.seek(0, 2)
                f.write(line)
                f.flush()
            finally:
                try:
                    f.seek(0, 2)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
        except Exception:
            f.write(line)
            f.flush()




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


#: Mot bien the hong (khong bao cao / qua gio / 0 lenh trong vai giay) duoc thu lai toi so lan nay roi moi bo.
SO_LAN_THU_TOI_DA = 2


def lay_viec(n: int = 1, so_cai: list[dict] | None = None, dang_chay: set[str] | None = None, hat: int = 27,
             san: str | None = None, hai_tang: bool | None = None, chi_tang1: bool = False,
             dang_ten: set[str] | None = None) -> list[dict]:
    """`san` (19/10/2026): san cua SLOT se chay viec (doc tu config/common.ini cua slot). Co `san` -> chi lay viec
    ong dan cua san do; viec cu V24 (ma XM `#`) chi cho slot XM - tren slot Exness chung chi sinh loi "khong co ma"."""
    sc = doc_so_cai() if so_cai is None else so_cai
    # 20/10/2026: viec trong reports/ong_dan/chay_lai_mt5.json (vd chay sai symbol EURUSD# thay EURUSDmicro) -> bo cac
    # dong so cai TRUOC luc danh dau, viec duoc chay lai
    cl = doc_chay_lai()
    if cl:
        sc = [r for r in sc if not (r.get("ten") in cl and str(r.get("luc") or "") < str(cl[r["ten"]].get("luc") or ""))]
    # 18/10/2026: dong `loi` la CHUA_DO_DUOC, khong phai "da thu". Truoc day moi dong deu vao `xong` nen mot lan
    # chay hong (moi truong, slot treo) xoa bien the do vinh vien khoi hang viec.
    hong = Counter(khoa(r) for r in sc if r.get("loi") and all(r.get(k) is not None for k in ("ea", "ma", "tf", "pha")))
    hong_ten = Counter(r.get("ten") for r in sc if r.get("loi") and r.get("ten"))
    xong = {khoa(r) for r in sc if not r.get("loi") and not r.get("lot_csv_nghi_ngo")} | {k for k, c in hong.items() if c >= SO_LAN_THU_TOI_DA} \
        | (dang_chay or set())
    xong_ten = {t for t, c in hong_ten.items() if c >= SO_LAN_THU_TOI_DA}  # grok 30/10: cap retries by ten too (loi rows often miss ts)
    # grok 30/10 22:53: stub/soft_quarantine -> max 1 retry (shared_bases lock thrash); also lock in-flight by ten
    stub_ten = Counter(r.get("ten") for r in sc if r.get("ten") and (
        "stub_bao_cao" in str(r.get("loi") or "") or r.get("soft_quarantine") or str(r.get("don_bay_bc") or "") == "1:0"
        or "1970" in str(r.get("ky_bc") or "")))
    xong_ten |= {t for t, c in stub_ten.items() if c >= 1}
    # grok 30/10 23:22: also lock SUCCESS by ten — khoa() can drift (e.g. InpLot0 3.0 vs 0.03 after scale)
    xong_ten |= {r.get("ten") for r in sc if r.get("ten") and not r.get("loi") and not r.get("lot_csv_nghi_ngo")}
    if dang_ten:
        xong_ten |= set(dang_ten)
    # quarantine sidecar
    try:
        qp = GOC / "reports" / "vong2" / "xac_nhan_stub_quarantine.jsonl"
        if qp.exists():
            for line in qp.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line: continue
                try:
                    qr = json.loads(line)
                except Exception:
                    continue
                if qr.get("ten"):
                    xong_ten.add(qr["ten"])
    except Exception:
        pass
    # 20/10/2026 hai tang: ket qua tang 1 (dong so cai tang=1, khong loi) theo khoa tang 2
    if hai_tang is None:
        try:
            import quan_ly_slot as _QS
            hai_tang = _QS.hai_tang()
        except Exception:
            hai_tang = False
    tang1 = {}
    for r in sc:
        if r.get("tang") == 1 and not r.get("loi"):
            tang1[khoa(dict(r, tang=None))] = bool(r.get("tang1_qua", True))
    sc = [r for r in sc if not r.get("loi")]
    hang = []
    chi_ong_dan = bool(san) and san.lower() != "xm"
    if os.environ.get("BRAIN_CHI_ONG_DAN", "").strip() in ("1", "true", "True", "yes"):
        chi_ong_dan = True  # grok: chi viec ong_dan, bo so_cai/MRZ/python_box
    for r in ([] if chi_ong_dan else sc):   # 1) OOS cho bien the dat IS (cao nhat)
        if r.get("pha") == "IS" and dat(r, NGUONG_IS):
            v = {k: r[k] for k in ("ea", "ma", "tf", "ts")}; v.update(pha="OOS", diem=100 + (r.get("pf") or 0))
            hang.append(v)
        # 2) near-miss -> hang xom. 17/10: nguong IS ha xuong pf 1,0 nen near-miss la vung SAT HOA (pf 0,9-1,0), khong con 1,1-1,25
        elif r.get("pha") == "IS" and (r.get("pf") or 0) >= 0.9 and (r.get("lenh") or 0) >= NGUONG_IS["lenh"]:
            for h in hang_xom(r):
                h["diem"] = 10 + (r.get("pf") or 0)
                hang.append(h)
    if not chi_ong_dan:
        hang += tu_python_box()
    hang += tu_ong_dan(san=san)
    hang += tu_vong2(san=san)          # vong 2: mac dinh tat (BRAIN_VONG2=1 de bat)
    if not chi_ong_dan:
        hang += ung_vien(random.Random(hat + len(sc) // 500))
    hang.sort(key=lambda v: -v["diem"])
    hang = [v for v in hang if khoa(v) not in xong and v.get("ten") not in xong_ten]
    if hai_tang:
        moi = []
        for v in hang:
            if not la_viec_hai_tang(v):
                moi.append(v)
                continue
            k2 = khoa(v)
            if k2 in xong:
                continue                        # da co real tick (hoac so cai cu truoc hai tang)
            if k2 in tang1:
                if tang1[k2]:
                    moi.append(dict(v, diem=float(v.get("diem") or 0) + 300, tang=2))   # qua tang 1 -> real tick som
            else:
                moi.append(dict(v, tang=1))
        hang = sorted(moi, key=lambda v: -v["diem"])
    out, thay, thay_ten = [], set(), set()
    for v in hang:
        if chi_tang1 and v.get("tang") != 1:
            continue
        k = khoa(v)
        t = v.get("ten") or ""
        if k in xong or k in thay or t in xong_ten or t in thay_ten:
            continue
        thay.add(k)
        if t:
            thay_ten.add(t)
        out.append(v)
        if len(out) >= n:
            break
    return out


CHAY_LAI_OD = GOC / "reports" / "ong_dan" / "chay_lai_mt5.json"


def doc_chay_lai(p: Path | None = None) -> dict:
    try:
        return json.loads(Path(p or CHAY_LAI_OD).read_text(encoding="utf-8"))
    except Exception:
        return {}


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


HANG_CHO_OD = GOC / "reports" / "ong_dan" / "hang_cho_mt5.jsonl"


def tu_ong_dan(p: Path = HANG_CHO_OD, san: str | None = None) -> list[dict]:
    """18/10/2026: viec MT5 do ong dan sinh (`python ong_dan.py sinh_mt5`). Chi lay viec `ea=XL` (BRAIN_XuLiLenh, .set
    day du); viec `NGOAI` (EA nguoi khac) can tai ma theo url truoc nen KHONG tu chay o day."""
    if not Path(p).exists():
        return []
    import os
    # vd "XM": slot tester dang nhap XM thi chi lay viec XM. `san` (tung slot) thang bien moi truong (ca tien trinh)
    san = san or os.environ.get("BRAIN_SAN_TESTER", "")
    out = []
    for x in Path(p).read_text(encoding="utf-8").splitlines():
        try:
            v = json.loads(x)
        except ValueError:
            continue
        if san and v.get("san", "").lower() != san.lower():
            continue
        if v.get("ea") == "XL" and v.get("ma") and v.get("tf") in TF:
            if os.environ.get("BRAIN_UU_TIEN_CSV") and v.get("pha") == "KIEM_CSV":
                v["diem"] = float(v.get("diem") or 60) + 200     # may_nha_toi_nay: viec VAO_CSV cua he dat chay truoc
            out.append(v)
    # 20/10/2026 toi: viec box sinh (reports/phan_viec/hang_cho_mt5_box.jsonl, nhan/phan_viec.py). CHI khi dat
    # BRAIN_HANG_BOX=1 (phien sau) - phien dem 20/10 dang chay khong bi doi. Trung ten voi hang chinh -> bo.
    if os.environ.get("BRAIN_HANG_BOX") == "1" and Path(p) == HANG_CHO_OD:
        try:
            from nhan import phan_viec as PV
        except ImportError:
            import sys as _s
            _s.path.insert(0, str(GOC))
            from nhan import phan_viec as PV
        co = {v.get("ten") for v in out}
        for v in PV.doc_hang_box(san=san or None):
            if v.get("tf") in TF and v.get("ten") not in co:
                if os.environ.get("BRAIN_UU_TIEN_CSV") and v.get("pha") == "KIEM_CSV":
                    v["diem"] = float(v.get("diem") or 60) + 200
                out.append(v)
                co.add(v.get("ten"))
    return out


HANG_CHO_V2 = GOC / "reports" / "vong2" / "hang_cho_vong2.jsonl"


def tu_vong2(p: Path = HANG_CHO_V2, san: str | None = None) -> list[dict]:
    """20/10/2026: viec MT5 VONG 2 (nhan/vong2.py). MAC DINH TAT: chi lay khi bien moi truong BRAIN_VONG2=1.
    BRAIN_VONG2_UU_TIEN=1 -> cong 150 diem (chay truoc viec ong dan thuong)."""
    import os
    if os.environ.get("BRAIN_VONG2", "0") != "1":
        return []
    gen = os.environ.get("BRAIN_GEN", "0") == "1"       # 21/10/2026: viec toi uu di truyen chi khi bat co
    return [dict(v, diem=float(v.get("diem") or 60) + (150 if os.environ.get("BRAIN_VONG2_UU_TIEN") == "1" else 0))
            for v in tu_ong_dan(p, san=san) if gen or v.get("pha") != "V2_GEN"]


def file_set_ong_dan(v: dict) -> str:
    """.set cho viec ong dan: moi input cua EA; input co khoang toi uu -> `ten=gt||dau||buoc||cuoi||Y`."""
    ky = v.get("toi_uu") or {}
    dong = []
    for k, x in sorted(v["ts"].items()):
        if k in ky:
            a, b, c = ky[k]
            dong.append("%s=%s||%s||%s||%s||Y" % (k, x, a, b, c))
        else:
            dong.append("%s=%s" % (k, x))
    return "\n".join(dong) + "\n"


def thu_muc_common(common: Path | None = None) -> Path:
    """Common\\Files cua MetaTrader 5 (chung moi terminal, ke ca /portable va tester agent)."""
    import os
    if common is not None:
        return Path(common)
    return Path(os.environ.get("APPDATA", ".")) / "MetaQuotes" / "Terminal" / "Common" / "Files"




def scale_lot_for_hash_demo(v: dict, scale: float = 0.01) -> dict:
    """micro lot notionals on # / GOLD.i# need ~100x less size vs deposit. Idempotent via flag."""
    if v.get("lot_scaled_for_hash"):
        return v
    ma = str(v.get("ma") or "")
    need = ma.endswith("#") or "GOLD" in ma.upper() or v.get("demo_hash_remap") or v.get("ma_goc")
    if not need:
        return v
    ts = dict(v.get("ts") or {})
    lot0 = float(ts.get("InpLot0") or 0)
    if lot0 > 0.5:  # still micro-sized numeric
        ts["InpLot0"] = round(lot0 * scale, 4)
        v["ts"] = ts
        py = dict(v.get("python") or {})
        if "lot0" in py:
            py["lot0"] = round(float(py["lot0"]) * scale, 4)
            v["python"] = py
        pql = dict(v.get("python_ql") or {})
        if "lot_tren_1000" in pql:
            pql["lot_tren_1000"] = round(float(pql["lot_tren_1000"]) * scale, 4)
            v["python_ql"] = pql
    try:
        von = float(v.get("von") or 0)
    except Exception:
        von = 0
    if von < 10000:
        v["von"] = 10000
    v["lot_scaled_for_hash"] = True
    return v


def remap_ma_hash_demo(sym: str) -> str:
    """Demo XM 345930355 chi co # (khong *micro). Map CSV ma -> symbol tester."""
    s = (sym or "").strip()
    if not s:
        return s
    u = s.upper()
    if u in ("XAUUSD", "XAUUSDMICRO", "GOLDMICRO", "GOLD", "XAUUSD#", "GOLD#"):
        return "GOLD.i#"
    if u.endswith("MICRO"):
        return s[:-5] + "#"
    # cent suffix e.g. GBPCADc / EURUSDc -> GBPCAD# (demo hash)
    if len(s) >= 2 and s[-1] in ("c", "C") and s[-2].isalpha() and not u.endswith("#"):
        return s[:-1] + "#"
    return s


def dat_csv_vao(v: dict, goc: Path, common: Path | None = None) -> Path | None:
    """19/10/2026: viec VAO_CSV -> chep CSV lenh vao (trong repo) vao Common\\Files, xoa file ra cu cua lan truoc."""
    if not v.get("csv_vao"):
        return None
    import shutil
    c = thu_muc_common(common)
    c.mkdir(parents=True, exist_ok=True)
    nguon = Path(goc) / v["csv_vao"]
    dich = c / nguon.name
    shutil.copy2(str(nguon), str(dich))
    # grok 30/10: remap ma column micro-># for demo hash symbols
    try:
        lines = dich.read_text(encoding="utf-8", errors="replace").splitlines()
        if lines and "," in lines[0]:
            cols = [c.strip() for c in lines[0].split(",")]
            if "ma" in cols:
                ima = cols.index("ma")
                ilot = cols.index("lot") if "lot" in cols else -1
                out = [lines[0]]
                ch = 0
                # scale CSV lot when tester symbol is hash/# (InpLot0 scale alone is ignored by EA)
                job_ma = str(v.get("ma") or "")
                force_scale = job_ma.endswith("#") or "GOLD" in job_ma.upper() or bool(v.get("demo_hash_remap"))
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    parts = line.split(",")
                    if len(parts) > ima:
                        old_ma = parts[ima]
                        nw = remap_ma_hash_demo(old_ma)
                        if nw != old_ma:
                            parts[ima] = nw
                            ch += 1
                        if ilot >= 0 and len(parts) > ilot and (force_scale or nw != old_ma):
                            try:
                                lv = float(parts[ilot])
                                if lv > 0.5:
                                    parts[ilot] = str(round(lv * 0.01, 4))
                                    ch += 1
                            except ValueError:
                                pass
                        out.append(",".join(parts))
                    else:
                        out.append(line)
                if ch:
                    dich.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    except Exception:
        pass
    for duoi in ("_lenh_mt5.csv", "_gia.csv"):
        cu = c / (nguon.name + duoi)
        if cu.exists():
            cu.unlink()
    return dich


def lay_csv_ra(v: dict, dich: Path, common: Path | None = None) -> list[str]:
    """Sau khi tester xong: chep <csv>_lenh_mt5.csv va <csv>_gia.csv tu Common\\Files ve `dich` (de doc_mt5 doi chieu)."""
    if not v.get("csv_vao"):
        return []
    import shutil
    c = thu_muc_common(common)
    ten = Path(v["csv_vao"]).name
    ra = []
    Path(dich).mkdir(parents=True, exist_ok=True)
    for duoi in ("_lenh_mt5.csv", "_gia.csv"):
        f = c / (ten + duoi)
        if f.exists():
            shutil.copy2(str(f), str(Path(dich) / f.name))
            ra.append(f.name)
    return ra


def ini_ong_dan(v: dict, ten: str, don_bay_dong: str) -> str:
    """ini tester cho viec ong dan. Toi uu: Optimization=1 (vet can) neu it to hop, 2 (di truyen) neu nhieu; bao cao .xml."""
    n = 1
    for a, b, c in (v.get("toi_uu") or {}).values():
        n *= int(round((float(c) - float(a)) / float(b))) + 1 if float(b) else 1
    opt = 0 if not v.get("toi_uu") else (1 if n <= 2000 else 2)
    if v.get("optimization") is not None and v.get("toi_uu"):
        opt = int(v["optimization"])            # 21/10/2026 tang_toc: V2_GEN ep di truyen (2)
    model = int(v.get("model", 4))
    if v.get("tang") == 1:              # 20/10/2026: loc tang 1 nhanh, it RAM (OHLC M1 / gia mo nen)
        try:
            import quan_ly_slot as _QS
            model = _QS.model_tang1()
        except Exception:
            model = 1
    return ("[Tester]\nExpert=BRAIN\\%s.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=" + str(model) + "\nExecutionMode=0\n"
            "Optimization=%d\nOptimizationCriterion=%d\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=%d\nCurrency=%s\n%s"
            "Report=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n") % (
        v.get("ea_file", "BRAIN_XuLiLenh"), ten, v["ma"], v["tf"], opt, int(v.get("tieu_chi") or 0), v.get("tu") or IS[0], v.get("den") or OOS[1],
        int(v.get("von") or 1000), v.get("tien") or "USD", don_bay_dong, ten)


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
    oos = {khoa({**r, "pha": "IS"}): r for r in sc if r.get("pha") == "OOS" and not r.get("loi") and not r.get("lot_csv_nghi_ngo")}
    ung = []
    for r in sc:
        if r.get("pha") == "IS" and dat(r, NGUONG_IS):
            o = oos.get(khoa(r))
            if o and dat(o, NGUONG_OOS):
                ci, co = cot_loi(r), cot_loi(o)
                ung.append({"ea": r["ea"], "ma": r["ma"], "tf": r["tf"], "ts": r["ts"], "IS": {k: r.get(k) for k in ("net", "lenh", "pf", "dd")},
                            "OOS": {k: o.get(k) for k in ("net", "lenh", "pf", "dd")}, "holm": h.get(khoa(r), False),
                            "cot_loi_IS": ci, "cot_loi_OOS": co, "dat_cot_loi": bool(ci and co and ci["dat"] and co["dat"])})
    return {"so_lan_thu": len(sc), "so_IS": sum(r.get("pha") == "IS" for r in sc), "so_OOS": sum(r.get("pha") == "OOS" for r in sc),
            "dat_IS": sum(1 for r in sc if r.get("pha") == "IS" and dat(r, NGUONG_IS)),
            "dat_cot_loi_ca_hai": sum(u["dat_cot_loi"] for u in ung),
            "cap_ea_ma_dat_cot_loi": sorted({"%s %s" % (u["ea"], u["ma"]) for u in ung if u["dat_cot_loi"]}), "ung_vien_ca_hai": ung}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "tong-ket":
        print(json.dumps(tong_ket(), ensure_ascii=False, indent=1))
    else:
        for v in lay_viec(int(sys.argv[1]) if len(sys.argv) > 1 else 8):
            print(json.dumps(v, ensure_ascii=False))
