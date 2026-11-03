# -*- coding: utf-8 -*-
"""Nâng lot cho hệ TRƯỢT CHỈ VÌ CAGR<=10% (DD<80%) — luật của Anh: "CAGR không cao thì nâng lot, miễn DD không quá".
Hệ đạt nếu TỒN TẠI hệ số lot k để CAGR>10%/năm VÀ max DD<80% (equity<=0 = cháy = trượt).

Cách đo theo dữ liệu có sẵn (ưu tiên từ trên xuống):
  1. MO_PHONG_CHAY_LAI: hệ mô phỏng Python (nhan/dich_nguoc) -> chạy lại đúng mô phỏng với lot×k (lot theo vốn = lãi kép,
     có swap, margin, stop-out) -> CAGR/DD thật của mô phỏng. Vẫn là MÔ PHỎNG, không phải tester MT5.
  2. MT5_PHAT_LAI_LENH: có báo cáo MT5 .htm (bảng Deals) -> phát lại số dư với lãi/lỗ mỗi deal ×k trên cùng vốn đầu
     (lot cố định: pnl×k). DD số dư đo từ đường phát lại; DD EQUITY lấy max(DD số dư phát lại, k×DD equity báo cáo) = XẤP XỈ.
  3. XAP_XI: chỉ có số tổng -> net_k = k×net, DD_k ≈ k×DD (lot cố định, tuyến tính). Ghi nhãn XẤP XỈ.
Chu kỳ < 2 năm = 'quá ngắn'.
    python -m nhan.nang_lot            # đo + ghi reports/NANG_LOT_DAT.md + cột k_nang_lot trong sổ
"""
from __future__ import annotations
import csv, json, math, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
SO = GOC / "TRI_NHO/so_ket_qua/ket_qua.csv"
BAO_CAO = GOC / "reports/NANG_LOT_DAT.md"
CACHE = GOC / "data/nang_lot_ket_qua.json"
CAGR_MIN, DD_MAX, NAM_NGAN = 10.0, 80.0, 2.0
K_LUOI = (1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0)


def _so(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------- bộ nhân lot (hàm thuần, có test) ----------------
def cagr_pct(cuoi, von, nam):
    if cuoi is None or von <= 0 or not nam or nam <= 0:
        return None
    if cuoi <= 0:
        return -100.0
    return ((cuoi / von) ** (1 / nam) - 1) * 100


def phat_lai_co_dinh(von, pnl, k, nam):
    """Lot cố định: mỗi lãi/lỗ ×k trên cùng vốn đầu. Trả {cagr, dd (theo số dư, %), chay}."""
    bal = dinh = von; dd = 0.0
    for p in pnl:
        bal += p * k
        if bal <= 0:
            return {"cagr": -100.0, "dd": 100.0, "chay": True}
        dinh = max(dinh, bal); dd = max(dd, (1 - bal / dinh) * 100)
    return {"cagr": cagr_pct(bal, von, nam), "dd": dd, "chay": False}


def phat_lai_lai_kep(von, loi_suat, k, nam):
    """Lãi kép (lot theo số dư): mỗi lệnh lãi r% số dư -> k·r%. Cháy nếu k·r <= -100%."""
    bal = dinh = von; dd = 0.0
    for r in loi_suat:
        bal *= 1 + r * k
        if bal <= 0:
            return {"cagr": -100.0, "dd": 100.0, "chay": True}
        dinh = max(dinh, bal); dd = max(dd, (1 - bal / dinh) * 100)
    return {"cagr": cagr_pct(bal, von, nam), "dd": dd, "chay": False}


def xap_xi_tuyen_tinh(net, von, nam, dd, k):
    """Chỉ có số tổng, lot cố định: net_k=k·net, DD_k≈k·DD. Cháy nếu von+k·net<=0 hoặc k·DD>=100."""
    ddk = dd * k
    cuoi = von + k * net
    if cuoi <= 0 or ddk >= 100:
        return {"cagr": -100.0, "dd": min(ddk, 100.0), "chay": True}
    return {"cagr": cagr_pct(cuoi, von, nam), "dd": ddk, "chay": False}


def dat(kq):
    return (not kq["chay"]) and kq["cagr"] is not None and kq["cagr"] > CAGR_MIN and kq["dd"] < DD_MAX


def tim_k(do, k_luoi=K_LUOI):
    """do(k)->{cagr,dd,chay}. Trả (k_min_cagr, k_max_dd, k_dat_list, bang). Dừng khi đã cháy/DD>=80 hai lần liên tiếp."""
    bang = {}; hong = 0
    for k in k_luoi:
        kq = do(k); bang[k] = kq
        hong = hong + 1 if (kq["chay"] or kq["dd"] >= DD_MAX) else 0
        if hong >= 2:
            break
    k_cagr = next((k for k in sorted(bang) if not bang[k]["chay"] and (bang[k]["cagr"] or -1e9) > CAGR_MIN), None)
    ok_dd = [k for k in sorted(bang) if not bang[k]["chay"] and bang[k]["dd"] < DD_MAX]
    k_dd = max(ok_dd) if ok_dd else None
    k_dat = [k for k in sorted(bang) if dat(bang[k])]
    return k_cagr, k_dd, k_dat, bang


# ---------------- đọc báo cáo MT5 ----------------
def doc_deals_htm(raw: bytes):
    t = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "ignore")
    bal = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(c) >= 12 and re.match(r"\d{4}\.\d\d\.\d\d", c[0]):
            v = _so(c[-2].replace(" ", "").replace("\xa0", ""))
            if v is not None:
                bal.append(v)
    if len(bal) < 2:
        return None, None
    return bal[0], [b - a for a, b in zip(bal[:-1], bal[1:])]


def _git(*a):
    return subprocess.run(["git", "-C", str(GOC), *a], capture_output=True).stdout


def tim_htm(ten):
    p = f"reports/ong_dan/ket_qua_mt5/{ten}"
    f = GOC / p
    if f.exists():
        return f.read_bytes(), p
    h = _git("log", "--all", "--format=%H", "-1", "--", p).decode().strip()
    if h:
        return _git("show", f"{h}:{p}"), f"{p}@{h[:8]}"
    return None, None


# ---------------- chạy lại mô phỏng ----------------
_DL = {}


def _luoi(arg):
    sym, uv, kb, lot0, k = arg
    import nhan.dich_nguoc.backtest_luoi as B
    if sym not in _DL:
        _DL[sym] = B.doc_dai(sym)
    cap = next(c for c in B.CAP if c[0] == sym); sw = B._swap(sym)
    bt = max(abs(sw[0]), abs(sw[1]))
    sm, sb = {"swap_do": sw[:2], "swap_bao_thu": (-bt, -bt), "swap_0_lac_quan": (0.0, 0.0)}[kb]
    r = B.chay(_DL[sym], pip=cap[1], spread=cap[2], gia_tri_pip_lot=cap[3], lot_moi_1000=lot0 * k, swap_mua=sm, swap_ban=sb,
               base_usd=cap[4], **B.UNG_VIEN[uv])
    return {"cagr": r["cagr"] * 100, "dd": r["dd_max_equity"] * 100, "chay": bool(r["chay_tai_khoan"]), "nam": r["so_nam"]}


def _vang(arg):
    ea, kb, k = arg
    import nhan.dich_nguoc.backtest_vang as V
    kh, f = V.EA[ea]
    if kh not in _DL:
        _DL[kh] = V.doc_xau(kh)
    g = _DL[kh]
    rr = {"ea1": 1.5, "ea2": 1.5, "ea3": 2.0, "ea4": 1.5, "ea5": 1.0, "clmca_c_v1": 1.0}[f.__name__]
    sm, sb = {"swap_do_XM": (-83.83, 20.64), "swap_bao_thu": (-83.83, -83.83), "swap_0_lac_quan": (0.0, 0.0)}[kb]
    r = V.mo_phong(g, f(g, rui_ro=rr * k), ea, swap_mua=sm, swap_ban=sb)
    return {"cagr": r["cagr"] * 100, "dd": r["dd_max_equity"] * 100, "chay": bool(r["chay_tai_khoan"]), "nam": r["so_nam"]}


def _chay_mot(job):
    loai, arg = job
    ham = _luoi if loai == "luoi" else _vang
    k_cagr, k_dd, k_dat, bang = tim_k(lambda k: ham((*arg, k)))
    return {"k_cagr": k_cagr, "k_dd": k_dd, "k_dat": k_dat, "bang": {str(k): v for k, v in bang.items()}}


# ---------------- chọn dòng ----------------
def chon_dong(ds):
    ra = []
    for r in ds:
        c, d = _so(r["cagr_pct"]), _so(r["dd_pct"])
        if r["trang_thai"] in ("BI_THAY_THE",) or c is None or d is None:
            continue
        if c <= CAGR_MIN and d < DD_MAX:
            ra.append(r)
    return ra


def phan_loai(r):
    g = r["tep_goc"]
    m = re.match(r"DichNguoc:(UV\d):(swap_\w+?):lot([\d.]+)/1000$", r["he"])
    if "backtest_luoi_v2" in g and m:
        uv = next(u for u in ("UV1_luoi_hedge_tp35_(2330430)", "UV2_ro_dca_hedge_15pip_(2262642)") if u.startswith(m.group(1)))
        return "luoi", (r["symbol"], uv, m.group(2), float(m.group(3)))
    m = re.match(r"Telegram:(.+):(swap_do_XM|swap_bao_thu|swap_0_lac_quan)$", r["he"])
    if "backtest_vang" in g and m:
        return "vang", (m.group(1), m.group(2))
    if ".htm" in g and "#" in g:
        return "mt5", g.split("#")[-1]
    return "tong", None


def do_tat_ca(so=SO, song_song=6):
    ds = list(csv.DictReader(open(so, encoding="utf-8")))
    cand = chon_dong(ds)
    jobs = {}
    for r in cand:
        loai, arg = phan_loai(r)
        if loai in ("luoi", "vang"):
            jobs[(loai, arg)] = None
    cache = json.load(open(CACHE)) if CACHE.exists() else {}
    can = [j for j in jobs if json.dumps(j) not in cache]
    if can:
        with ProcessPoolExecutor(song_song) as ex:
            for j, kq in zip(can, ex.map(_chay_mot, can)):
                cache[json.dumps(j)] = kq; print(j, kq["k_cagr"], kq["k_dd"], kq["k_dat"], flush=True)
                CACHE.parent.mkdir(exist_ok=True); json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
    ket = []
    for r in cand:
        loai, arg = phan_loai(r)
        nam = _so(r["so_nam"]); von = _so(r["von"]); net = _so(r["net"]); dd0 = _so(r["dd_pct"])
        e = {"id": r["id"], "he": r["he"], "symbol": r["symbol"], "tf": r["timeframe"], "nam": nam, "nguon": r["nguon"],
             "real_tick": r["real_tick_pct"], "cagr0": _so(r["cagr_pct"]), "dd0": dd0, "loai": loai}
        if loai in ("luoi", "vang"):
            kq = cache[json.dumps([loai, list(arg)])] if json.dumps([loai, list(arg)]) in cache else cache[json.dumps((loai, arg))]
            e.update(kq); e["cach"] = "MO_PHONG_CHAY_LAI"
        elif loai == "mt5":
            raw, p = tim_htm(arg)
            von_h, pnl = doc_deals_htm(raw) if raw else (None, None)
            if pnl and nam:
                def do(k, von_h=von_h, pnl=pnl):
                    a = phat_lai_co_dinh(von_h, pnl, k, nam)
                    a["dd_so_du"] = a["dd"]; a["dd"] = max(a["dd"], k * dd0)
                    if a["dd"] >= 100: a["chay"] = True
                    return a
                e["cach"] = "MT5_PHAT_LAI_LENH"; e["htm"] = p; e["so_deal"] = len(pnl)
            elif net is not None and von and nam:
                do = lambda k: xap_xi_tuyen_tinh(net, von, nam, dd0, k); e["cach"] = "XAP_XI"
            else:
                do = None
        else:
            do = (lambda k: xap_xi_tuyen_tinh(net, von, nam, dd0, k)) if (net is not None and von and nam) else None
            e["cach"] = "XAP_XI" if do else "THIEU_SO"
        if loai in ("mt5", "tong"):
            if do is None:
                e.update(cach="THIEU_SO", k_cagr=None, k_dd=None, k_dat=[], bang={})
            else:
                kc, kd, kdat, bang = tim_k(do)
                e.update(k_cagr=kc, k_dd=kd, k_dat=kdat, bang={str(k): v for k, v in bang.items()})
        ket.append(e)
    return ket


# ---------------- ghi ----------------
NHAN = {"MO_PHONG_CHAY_LAI": "MÔ PHỎNG chạy lại lot×k", "MT5_PHAT_LAI_LENH": "MT5 phát lại deal×k (DD equity XẤP XỈ)",
        "XAP_XI": "XẤP XỈ tuyến tính", "THIEU_SO": "THIẾU SỐ"}


def _f(x, n=2):
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",")


def ghi_bao_cao(ket, ra=BAO_CAO):
    dat_ = [e for e in ket if e["k_dat"]]
    L = ["# Nâng lot: hệ trượt chỉ vì CAGR ≤ 10% (DD < 80%)", "",
         "Luật Anh (03/11/2026): *CAGR không cao thì nâng lot, miễn DD không quá* → hệ ĐẠT nếu có hệ số lot k cho CAGR > 10%/năm và max DD < 80% (equity ≤ 0 = cháy = trượt).",
         "", "Sinh bởi `python -m nhan.nang_lot`. Chỉ số đo/chạy lại thật; ô '—' = CHƯA ĐO ĐƯỢC. k thử trên lưới " + ", ".join(_f(k, 2).rstrip("0").rstrip(",") for k in K_LUOI) + " (dừng khi hỏng 2 mức liền).", "",
         "Cách đo:",
         "- **MÔ PHỎNG chạy lại lot×k**: chạy lại đúng mô phỏng Python (nhan/dich_nguoc, lot theo vốn = lãi kép, có swap/margin/stop-out). Vẫn là MÔ PHỎNG, chưa phải tester MT5.",
         "- **MT5 phát lại deal×k**: bảng Deals trong báo cáo MT5 .htm, lãi/lỗ mỗi deal ×k trên cùng vốn (lot cố định). DD = max(DD số dư phát lại, k × DD equity báo cáo) → phần equity là XẤP XỈ.",
         "- **XẤP XỈ tuyến tính**: chỉ có số tổng; net_k = k·net, DD_k ≈ k·DD.",
         "- Chu kỳ < 2 năm = **quá ngắn** (không đủ để tin).", "",
         f"Tổng dòng xét: {len(ket)}; có k đạt: {len(dat_)}; không k nào đạt: {len(ket) - len(dat_)}.", "",
         "## Hệ đạt sau nâng lot", "",
         "| Hệ | Mã | Năm | Nguồn | CAGR gốc % | DD gốc % | k nhỏ nhất CAGR>10 | k lớn nhất DD<80 | k đạt chọn | CAGR @k % | DD @k % | Cách đo | Ghi chú |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(dat_, key=lambda e: (-(e["nam"] or 0), e["he"])):
        k = e["k_dat"][0]; b = e["bang"][str(k)]
        gc = []
        if e["nam"] is not None and e["nam"] < NAM_NGAN: gc.append("quá ngắn")
        if e["real_tick"] and _so(e["real_tick"]) is not None and _so(e["real_tick"]) < 90: gc.append(f"real tick {e['real_tick']}%")
        if e["nguon"].startswith("mo_phong"): gc.append("MÔ PHỎNG")
        L.append(f"| {e['he']} | {e['symbol']} | {_f(e['nam'])} | {e['nguon']} | {_f(e['cagr0'])} | {_f(e['dd0'])} | {_f(e['k_cagr'])} | {_f(e['k_dd'])} | {_f(k)} | {_f(b['cagr'])} | {_f(b['dd'])} | {NHAN[e['cach']]} | {'; '.join(gc)} |")
    L += ["", "## Không có k nào đạt", "", "| Hệ | Mã | Năm | CAGR gốc % | DD gốc % | k nhỏ nhất CAGR>10 | k lớn nhất DD<80 | Cách đo |", "|---|---|---|---|---|---|---|---|"]
    for e in sorted([e for e in ket if not e["k_dat"]], key=lambda e: e["he"]):
        L.append(f"| {e['he']} | {e['symbol']} | {_f(e['nam'])} | {_f(e['cagr0'])} | {_f(e['dd0'])} | {_f(e['k_cagr'])} | {_f(e['k_dd'])} | {NHAN[e['cach']]} |")
    ra.write_text("\n".join(L) + "\n", encoding="utf-8")


def chuoi_k(e):
    if e["k_dat"]:
        return f"{_f(min(e['k_dat']))}-{_f(max(e['k_dat']))}"
    return "khong_co"


def ghi_so_cot(ket, so=SO):
    from nhan import so_ket_qua as S
    ds = S.doc_so(so); m = {e["id"]: e for e in ket}
    for r in ds:
        e = m.get(r["id"])
        if e:
            r["k_nang_lot"] = chuoi_k(e)
            r["nang_lot_ghi_chu"] = (f"{NHAN[e['cach']]}; k_min_CAGR>10={_f(e['k_cagr'])}; k_max_DD<80={_f(e['k_dd'])}"
                                     + ("; quá ngắn" if e["nam"] is not None and e["nam"] < NAM_NGAN else "") + "; reports/NANG_LOT_DAT.md")
    S.ghi_so(ds, so)


def main(argv=None):
    ket = do_tat_ca()
    ghi_bao_cao(ket); ghi_so_cot(ket)
    print(f"{sum(1 for e in ket if e['k_dat'])}/{len(ket)} dòng có k đạt -> {BAO_CAO}")


if __name__ == "__main__":
    main(sys.argv[1:])
