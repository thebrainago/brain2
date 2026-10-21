# -*- coding: utf-8 -*-
"""tang_toc.py - TANG TOC MT5 may nha (21/10/2026, Grok Bot). BACKTEST, khong phai tien that. Moi thu MAC DINH TAT.

Co (bien moi truong):
  BRAIN_GEN=1            viec TOI UU DI TRUYEN vong 2 (Optimization=2, Model=1 OHLC M1, tieu chi Recovery Factor = lai/DD)
                         -> doc XML -> chon TAM CAO NGUYEN (khong phai dinh) -> viec KIEM real tick (top N).
  BRAIN_CONG_MOI=1       cong tang 1 (OHLC M1) moi: lai kep >= BRAIN_CONG_LAI_MIN (8 %/nam) va DD <= BRAIN_CONG_DD_MAX (85 %);
                         ghi cap (OHLC, real tick) vao reports/mt5_lien_tuc/lech_ohlc_tick.jsonl de hieu chinh cong.
  BRAIN_RAM_DONG=1       phong viec theo RAM DO duoc: can = BRAIN_RAM_TICK_GB (6) real tick / BRAIN_RAM_OHLC_GB (1,5) moi agent
                         OHLC; giu BRAIN_RAM_DU_TRU_GB (4) du tru. So agent toi uu = floor((trong - du tru) / 1,5).
  BRAIN_TICK_CHUNG=1     kho tick chung (E:\\mt5_tick_chung\\bases, junction - xem dung_chung_tick.ps1) + KHOA theo symbol:
                         hai slot khong tai cung symbol mot luc (symbol chua 'am' -> chi 1 viec real tick).
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
LECH = GOC / "reports" / "mt5_lien_tuc" / "lech_ohlc_tick.jsonl"
HANG_V2 = GOC / "reports" / "vong2" / "hang_cho_vong2.jsonl"
KHO_TICK = Path(os.environ.get("BRAIN_KHO_TICK") or r"E:\mt5_tick_chung")
XM_GIAO_DICH = r"c:\program files\xm global mt5"


def bat(ten: str) -> bool:
    return os.environ.get(ten, "0").strip() in ("1", "true", "True", "yes")


def _f(ten: str, md: float) -> float:
    try:
        return float(os.environ.get(ten, "") or md)
    except ValueError:
        return md


# ------------------------------------------------------------------------------------------- 4. RAM
def ram_gb() -> tuple[float, float]:
    """(tong, trong) GB. Khong co psutil -> (inf, inf)."""
    try:
        import psutil
        m = psutil.virtual_memory()
        return m.total / 1024 ** 3, m.available / 1024 ** 3
    except Exception:
        return float("inf"), float("inf")


def can_ram(v: dict) -> float:
    """RAM uoc tinh cho mot viec (GB). Toi uu: so agent x RAM/agent OHLC."""
    if v.get("gen") or v.get("toi_uu"):
        return max(1, int(v.get("so_agent") or 1)) * _f("BRAIN_RAM_OHLC_GB", 1.5) + 1.0
    if v.get("tang") == 1:
        return _f("BRAIN_RAM_OHLC_GB", 1.5) + 0.5
    return _f("BRAIN_RAM_TICK_GB", 6.0)


def du_ram_dong(v: dict, trong: float | None = None) -> tuple[bool, str]:
    trong = ram_gb()[1] if trong is None else trong
    can = can_ram(v) + _f("BRAIN_RAM_DU_TRU_GB", 4.0)
    return trong >= can, "RAM trống %.1f GB %s cần %.1f GB (%s)" % (trong, ">=" if trong >= can else "<", can,
                                                                 "tối ưu" if v.get("gen") or v.get("toi_uu") else "tầng %s" % v.get("tang", 2))


def so_agent(trong: float | None = None, nhan: int | None = None) -> int:
    trong = ram_gb()[1] if trong is None else trong
    nhan = nhan or (os.cpu_count() or 4)
    if math.isinf(trong):
        return max(1, nhan // 2)
    n = int((trong - _f("BRAIN_RAM_DU_TRU_GB", 4.0) - 1.0) // _f("BRAIN_RAM_OHLC_GB", 1.5))
    return max(1, min(n, nhan - 1, int(_f("BRAIN_GEN_AGENT_MAX", 16))))


def slot_toi_da_dong(tong: float | None = None, so_slot: int = 5) -> int:
    """So viec real tick dong thoi toi da theo RAM TONG do duoc (khong phai so cung)."""
    tong = ram_gb()[0] if tong is None else tong
    if math.isinf(tong):
        return so_slot
    return max(1, min(so_slot, int((tong - _f("BRAIN_RAM_HE_THONG_GB", 6.0)) // _f("BRAIN_RAM_TICK_GB", 6.0))))


# ------------------------------------------------------------------------------------------- 3. cong tang 1
def _dd(x) -> float | None:
    m = re.search(r"\(([\d.]+)%\)", str(x or ""))
    if m:
        return float(m.group(1))
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def so_nam(v: dict) -> float:
    import datetime as dt
    try:
        a = dt.datetime.strptime(str(v.get("tu")), "%Y.%m.%d"); b = dt.datetime.strptime(str(v.get("den")), "%Y.%m.%d")
        return max((b - a).days / 365.25, 1e-3)
    except (TypeError, ValueError):
        return float("nan")


def lai_kep(net: float, von: float, nam: float) -> float | None:
    if net is None or not von or not (nam > 0):
        return None
    return ((1 + net / von) ** (1 / nam) - 1) * 100 if net / von > -1 else -100.0


def phan_xu_tang1_moi(r: dict, v: dict) -> tuple[bool, str]:
    lai = lai_kep(r.get("net"), float(v.get("von") or 1000), so_nam(v))
    dd = _dd(r.get("dd"))
    lmin, dmax = _f("BRAIN_CONG_LAI_MIN", 8.0), _f("BRAIN_CONG_DD_MAX", 85.0)
    if lai is None or dd is None:
        return True, "tầng 1 thiếu số (lãi=%s, DD=%s) -> cho qua tầng 2" % (lai, r.get("dd"))
    if dd > dmax:
        return False, "tầng 1 TRƯỢT: DD %.1f%% > %.0f%%" % (dd, dmax)
    if lai < lmin:
        return False, "tầng 1 TRƯỢT: lãi kép %.1f%%/năm < %.0f%%" % (lai, lmin)
    return True, "tầng 1 QUA: lãi kép %.1f%%/năm, DD %.1f%%" % (lai, dd)


def khoa_goc(v: dict) -> str:
    return json.dumps({k: v.get(k) for k in ("ea", "ma", "tf", "ts", "pha")}, sort_keys=True, default=str)


def ghi_lech(rec_t2: dict, so_cai: Path, ra: Path = LECH) -> dict | None:
    """Viec real tick vua xong -> tim ban ghi tang 1 cung khoa trong so cai -> ghi cap lech OHLC/tick."""
    k = khoa_goc(rec_t2)
    t1 = None
    try:
        for x in Path(so_cai).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(x)
            except ValueError:
                continue
            if r.get("tang") == 1 and not r.get("loi") and khoa_goc(r) == k:
                t1 = r
    except OSError:
        return None
    if not t1 or rec_t2.get("net") is None or t1.get("net") is None:
        return None
    von, nam = float(rec_t2.get("von") or 1000), so_nam(rec_t2)
    d = {"ten": rec_t2.get("ten"), "ma": rec_t2.get("ma"), "tf": rec_t2.get("tf"),
         "ohlc": {"net": t1["net"], "dd": _dd(t1.get("dd")), "lai_kep": lai_kep(t1["net"], von, nam)},
         "tick": {"net": rec_t2["net"], "dd": _dd(rec_t2.get("dd")), "lai_kep": lai_kep(rec_t2["net"], von, nam)},
         "luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "nhan": "ĐO THẬT (2 lần chạy MT5)"}
    a, b = d["ohlc"]["lai_kep"], d["tick"]["lai_kep"]
    d["lech_lai_kep"] = None if a is None or b is None else round(b - a, 2)
    d["lech_dd"] = None if d["ohlc"]["dd"] is None or d["tick"]["dd"] is None else round(d["tick"]["dd"] - d["ohlc"]["dd"], 2)
    ra.parent.mkdir(parents=True, exist_ok=True)
    with open(ra, "a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return d


def hieu_chinh_cong(p: Path = LECH, phan_vi: float = 0.9) -> dict:
    """Tu cac cap da do: de khong loat he tick dat (>=10 %/nam, DD<=80), cong OHLC can noi bao nhieu (phan vi)."""
    ds = []
    try:
        ds = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    except OSError:
        pass
    ok = [d for d in ds if d.get("lech_lai_kep") is not None and d.get("lech_dd") is not None]
    if len(ok) < 10:
        return {"so_cap": len(ok), "goi_y": None, "nhan": "CHƯA ĐO ĐƯỢC (cần >= 10 cặp)"}
    import numpy as np
    ll = np.array([d["lech_lai_kep"] for d in ok]); ld = np.array([d["lech_dd"] for d in ok])
    return {"so_cap": len(ok), "lech_lai_kep_p50": float(np.median(ll)), "lech_dd_p50": float(np.median(ld)),
            "goi_y": {"BRAIN_CONG_LAI_MIN": round(10 - float(np.quantile(ll, phan_vi)), 1),
                      "BRAIN_CONG_DD_MAX": round(80 - float(np.quantile(ld, 1 - phan_vi)), 1)}, "nhan": "ĐO THẬT"}


# ------------------------------------------------------------------------------------------- 2. khoa tick
def _ten_khoa(sym: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", sym)


def tick_am(sym: str, kho: Path = KHO_TICK) -> bool:
    return (kho / "da_co" / (_ten_khoa(sym) + ".txt")).exists()


def danh_dau_am(sym: str, kho: Path = KHO_TICK) -> None:
    d = kho / "da_co"; d.mkdir(parents=True, exist_ok=True)
    (d / (_ten_khoa(sym) + ".txt")).write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")


def lay_khoa(sym: str, chu: str, kho: Path = KHO_TICK, cu_giay: float = 3 * 3600) -> bool:
    """Khoa nguyen tu (O_EXCL). Khoa cu hon cu_giay (tien trinh chet) -> doi ten sang .cu roi lay lai (khong xoa)."""
    d = kho / "khoa"; d.mkdir(parents=True, exist_ok=True)
    f = d / (_ten_khoa(sym) + ".lock")
    for _ in range(2):
        try:
            fd = os.open(str(f), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"chu": chu, "luc": time.time()}).encode()); os.close(fd)
            return True
        except FileExistsError:
            try:
                x = json.loads(f.read_text())
                if x.get("chu") == chu:
                    return True
                if time.time() - float(x.get("luc", 0)) > cu_giay:
                    f.replace(f.with_suffix(".lock.cu")); continue
            except (OSError, ValueError):
                pass
            return False
    return False


def tra_khoa(sym: str, chu: str, kho: Path = KHO_TICK) -> None:
    f = kho / "khoa" / (_ten_khoa(sym) + ".lock")
    try:
        if json.loads(f.read_text()).get("chu") == chu:
            f.unlink()
    except (OSError, ValueError):
        pass


def duoc_chay_tick(v: dict, chu: str, kho: Path = KHO_TICK) -> bool:
    """Viec real tick: symbol da am -> chay tu do; chua am -> phai giu khoa symbol (1 slot tai)."""
    if v.get("tang") == 1 or v.get("gen") or tick_am(v["ma"], kho):
        return True
    return lay_khoa(v["ma"], chu, kho)


def kiem_slot_an_toan(slot: str) -> str | None:
    p = slot.replace("/", "\\").lower()
    if p.startswith(XM_GIAO_DICH) or "xm global mt5" in p:
        return "từ chối: %s là terminal XM giao dịch" % slot
    return None


# ------------------------------------------------------------------------------------------- 1. toi uu di truyen
THAM_GEN = {"InpTPPct": "f", "InpBuocPct": "f", "InpMoKhoaPct": "f", "InpHedgeKhiLoPct": "f", "InpMaxTang": "i", "InpLot0": "f",
            "InpTPATR": "f", "InpBuocATR": "f", "InpHeSoLot": "f"}


def khoang_quanh(x: float, kieu: str, nac: int = 4, rong: float = 0.5) -> tuple | None:
    """Khoang [x(1-rong) .. x(1+rong)] voi 2*nac+1 nac quanh TAM CAO NGUYEN x. x = 0 -> khong toi uu (tat)."""
    if not x:
        return None
    if kieu == "i":
        a, c = max(1, int(round(x * (1 - rong)))), max(int(round(x * (1 + rong))), int(x) + 1)
        return (a, 1, c)
    b = abs(x) * rong / nac
    return (round(x - b * nac, 8), round(b, 8), round(x + b * nac, 8))


def viec_gen(v: dict, so_agent_: int | None = None) -> dict:
    """Viec V2 (tam cao nguyen) -> viec toi uu di truyen OHLC M1."""
    tu = {}
    for k, kieu in THAM_GEN.items():
        x = v.get("ts", {}).get(k)
        try:
            r = khoang_quanh(float(x), kieu) if x is not None else None
        except (TypeError, ValueError):
            r = None
        if r:
            tu[k] = r
    ten = ("od_gen_" + v["ten"][3:])[:60]
    return dict(v, ten=ten, pha="V2_GEN", gen=True, toi_uu=tu, optimization=2, model=1, tieu_chi=4,
                so_agent=so_agent_ or so_agent(), goc_gen=v["ten"], diem=float(v.get("diem") or 60) + 5)


def chon_tam_cao_nguyen(pass_: list[dict], tham: list[str], top: int = 3, dd_max: float = 85.0, ban_kinh: float = 1.01) -> list[dict]:
    """Pass toi uu -> top N theo MEDIAN Recovery cua hang xom (khoang cach chuan hoa <= ban_kinh nac), khong theo dinh.
    Cot MT5: 'Recovery Factor', 'Equity DD %', 'Profit', 'Trades' + cot tham so."""
    import numpy as np
    ok = [p for p in pass_ if isinstance(p.get("Recovery Factor"), float) and all(isinstance(p.get(t), float) for t in tham)
          and (p.get("Equity DD %") or 0) <= dd_max and (p.get("Profit") or 0) > 0]
    if not ok:
        return []
    X = np.array([[p[t] for t in tham] for p in ok], float)
    nac = np.array([np.min(np.diff(np.unique(X[:, j]))) if len(np.unique(X[:, j])) > 1 else 1.0 for j in range(len(tham))])
    R = np.array([p["Recovery Factor"] for p in ok])
    diem = []
    for i in range(len(ok)):
        d = np.max(np.abs((X - X[i]) / nac), axis=1)
        hx = R[d <= ban_kinh]
        diem.append((float(np.median(hx)), len(hx), i))
    diem.sort(key=lambda z: (-z[0], -z[1]))
    ra = []
    for m, n, i in diem[:top]:
        ra.append(dict(ok[i], cao_nguyen_median_rf=round(m, 3), so_hang_xom=n))
    return ra


def viec_kiem_tick(v_gen: dict, c: dict, j: int) -> dict:
    ts = dict(v_gen["ts"])
    for k in v_gen.get("toi_uu") or {}:
        if k in c:
            ts[k] = int(c[k]) if THAM_GEN.get(k) == "i" else c[k]
    ten = ("od_gk%d_" % j + v_gen["goc_gen"][3:])[:60]
    v = {k: x for k, x in v_gen.items() if k not in ("toi_uu", "gen", "optimization", "model", "tieu_chi", "so_agent")}
    return dict(v, ten=ten, ts=ts, pha="V2_GEN_KIEM", tang=2, nguon_gen=v_gen["ten"], diem=float(v_gen.get("diem") or 60) + 10,
                gen_ket_qua={k: c.get(k) for k in ("Profit", "Recovery Factor", "Equity DD %", "Trades", "cao_nguyen_median_rf",
                                                    "so_hang_xom")}, nhan_gen="OHLC M1 (tối ưu) — cần real tick xác nhận")


def sau_toi_uu(xml: Path, v_gen: dict, hang: Path = HANG_V2, top: int | None = None) -> list[dict]:
    import sys
    sys.path.insert(0, str(GOC))
    from nhan.ong_dan import doc_xml_toi_uu
    c = chon_tam_cao_nguyen(doc_xml_toi_uu(xml), list(v_gen.get("toi_uu") or {}), top=top or int(_f("BRAIN_GEN_TOP", 3)))
    moi = [viec_kiem_tick(v_gen, x, j) for j, x in enumerate(c, 1)]
    if moi:
        with open(hang, "a", encoding="utf-8") as f:
            for v in moi:
                f.write(json.dumps(v, ensure_ascii=False, sort_keys=True, default=str) + "\n")
    return moi


def sinh_gen(hang: Path = HANG_V2, top: int = 10) -> list[dict]:
    """Them viec V2_GEN cho top viec V2_CAO_NGUYEN (theo diem) chua co ban gen."""
    ds = [json.loads(x) for x in hang.read_text(encoding="utf-8").splitlines() if x.strip()] if hang.exists() else []
    co = {v.get("goc_gen") for v in ds if v.get("pha") == "V2_GEN"}
    goc = sorted([v for v in ds if v.get("pha") == "V2_CAO_NGUYEN" and v["ten"] not in co], key=lambda v: -float(v.get("diem") or 0))
    moi = [viec_gen(v, so_agent_=None) for v in goc[:top]]
    moi = [v for v in moi if v["toi_uu"]]
    if moi:
        with open(hang, "a", encoding="utf-8") as f:
            for v in moi:
                f.write(json.dumps(v, ensure_ascii=False, sort_keys=True, default=str) + "\n")
    return moi


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("lenh", choices=["sinh-gen", "hieu-chinh-cong", "ram"]); ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    if a.lenh == "sinh-gen":
        print("thêm %d việc V2_GEN" % len(sinh_gen(top=a.top)))
    elif a.lenh == "hieu-chinh-cong":
        print(json.dumps(hieu_chinh_cong(), ensure_ascii=False, indent=1))
    else:
        t, f = ram_gb(); print("RAM tổng %.1f, trống %.1f GB; agent tối ưu %d; real tick tối đa %d" % (t, f, so_agent(f), slot_toi_da_dong(t)))
