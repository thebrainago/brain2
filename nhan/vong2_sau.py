# -*- coding: utf-8 -*-
"""vong2_sau.py - VONG 2 SAU (21/10/2026, Grok Bot): chi dung LENH MT5 THAT cua ca 78 he DAT (khong can tin hieu Python).

Khong goi LLM. Phan:
  1. tf_tu_htm        : dien cot TF trong (doc 'Period:' trong bao cao MT5 .htm).
  2. stress_phi       : nhieu muc phi (spread x1.5/x2/x3, hoa hong 0/7/14 USD/100k khu hoi) -> lai kep sau phi. MÔ PHỎNG.
  3. canh_bao_qua_khop: lich su ngan, it lenh, 1 doan WF ganh lai, doan WF am, MC DD p95 cao, phu thuoc 1 cap.
  4. ghep_cung_cap    : cong equity 2 he MT5 cung cap (A + B co phong cach khac: nguoc chieu / cung chieu / them lenh)
                        -> DD equity that cua tong. MÔ PHỎNG phan tuong tac ky quy (2 EA chay rieng da do that).
  5. danh_muc_sau     : tim danh muc 2..5 he (tham lam + ngau nhien) theo tuong quan ngay & DD equity theo gio,
                        nhieu muc tran DD (20/30/40/60 %), co stress phi.
  6. hang_cho         : viec MT5 xac minh danh muc / ghep (chay dong thoi cac EA goc tren cung tai khoan).
So MT5 = ĐO THẬT; stress, MC, ghep, danh muc = MÔ PHỎNG (cong equity tai dung).
"""
from __future__ import annotations

import itertools
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import vong2 as V

RA = V.RA
MUC_PHI = [(1.0, 0.0), (1.5, 7.0), (2.0, 7.0), (3.0, 14.0)]       # (he so spread, hoa hong USD/100k khu hoi)
TRAN_DD = [20.0, 30.0, 40.0, 60.0]


def tf_tu_htm(ten: str, thu_muc: Path = V.KQ_MT5) -> str | None:
    f = thu_muc / (ten + ".htm")
    if not f.exists():
        return None
    b = f.read_bytes()
    try:
        s = b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8", "ignore")
    except UnicodeDecodeError:
        s = b.decode("utf-8", "ignore")
    s = re.sub(r"<[^>]*>", "|", s)
    m = re.search(r"Period:\|[\s|]*([MHDWN][0-9N]{1,2})\s*\(", s)
    return m.group(1) if m else None


def stress_phi(ten: str, von: float = 1000.0, lech: float = 0.0) -> list[dict]:
    tl, tg = V.KQ_MT5 / (ten + "_vao.csv_lenh_mt5.csv"), V.KQ_MT5 / (ten + "_vao.csv_gia.csv")
    p, g = V.doc_vi_the(tl), V.doc_gia_mt5(tg)
    nam = (g.index[-1] - g.index[0]).days / 365.25
    ra, cu = [], dict(V.STRESS)
    try:
        for sp, hh in MUC_PHI:
            V.STRESS.update({"spread_he_so": sp, "hoa_hong_usd_100k_khu_hoi": hh})
            cp = V.chi_phi_stress(p, g)
            dv = V._khop_net(V.duong_von(p, g, von, cp), lech)
            ra.append({"spread_x": sp, "hoa_hong": hh, "phi_usd": round(float(cp.sum()), 2),
                       "lai_kep_pct_nam": round(V.lai_kep(von, dv["equity"].iloc[-1], nam), 2),
                       "dd_equity_pct": round(V.dd_pct(dv["equity_xau"]), 2)})
    finally:
        V.STRESS.clear(); V.STRESS.update(cu)
    return ra


def canh_bao_qua_khop(m: dict, so_cung_cap: int) -> list[str]:
    c = []
    if m["so_nam"] < 2.0:
        c.append("lịch sử ngắn %.1f năm" % m["so_nam"])
    if m["so_lenh"] < 30:
        c.append("ít lệnh %d" % m["so_lenh"])
    wf = [d["lai_kep_pct_nam"] for d in m.get("walk_forward") or []]
    if wf:
        if min(wf) < 0:
            c.append("có đoạn WF âm (%.0f%%/năm)" % min(wf))
        tong = sum(max(x, 0) for x in wf)
        if tong > 0 and max(wf) / tong > 0.6:
            c.append("1 đoạn WF gánh %.0f%% lãi" % (100 * max(wf) / tong))
    p95 = (m.get("monte_carlo") or {}).get("equity", {}).get("dd_equity_p95")
    if p95 is not None and p95 > 80:
        c.append("MC DD p95 %.0f%% > 80%%" % p95)
    if m.get("so_lenh_het_ky", 0) > 0:
        c.append("%d lệnh còn mở cuối kỳ" % m["so_lenh_het_ky"])
    if so_cung_cap <= 1:
        c.append("chỉ đo trên 1 cặp (chưa có chuyển cặp MT5)")
    return c


def _eq(m: dict, cot: str = "equity_xau") -> pd.Series:
    return m["_dv"][cot] - 1000.0


def do_nhom(pt: dict, nhom, von: float = 1000.0) -> dict:
    x = pd.DataFrame({k: _eq(pt[k]) for k in nhom}).sort_index().ffill().fillna(0.0)
    xc = pd.DataFrame({k: _eq(pt[k], "equity") for k in nhom}).sort_index().ffill().fillna(0.0)
    v0 = von * len(nhom)
    eq, eqc = v0 + x.sum(axis=1), v0 + xc.sum(axis=1)
    nam = (eq.index[-1] - eq.index[0]).days / 365.25
    lai, dd = V.lai_kep(v0, eqc.iloc[-1], nam), V.dd_pct(eq)
    return {"he": list(nhom), "lai_kep_pct_nam": round(lai, 2), "dd_equity_pct": round(dd, 2), "von": v0,
            "so_nam": round(nam, 2), "diem": lai / max(dd, 5.0)}


def ghep_cung_cap(pt: dict) -> list[dict]:
    """Moi cap symbol: moi doi he -> equity cong. 'bu_tru' = DD tong < DD lon hon cua 2 he."""
    theo = {}
    for k, m in pt.items():
        theo.setdefault(m["symbol"], []).append(k)
    ra = []
    for sym, ds in theo.items():
        for a, b in itertools.combinations(sorted(ds), 2):
            g = do_nhom(pt, [a, b])
            ca = pt[a]["lai_ngay_s"].corr(pt[b]["lai_ngay_s"]) if len(pt[a]["lai_ngay_s"]) > 3 else None
            ra.append(dict(g, symbol=sym, tuong_quan_ngay=None if ca is None or np.isnan(ca) else round(float(ca), 3),
                           dd_a=pt[a]["dd_equity_pct"], dd_b=pt[b]["dd_equity_pct"],
                           lai_a=pt[a]["lai_kep_pct_nam"], lai_b=pt[b]["lai_kep_pct_nam"],
                           bu_tru=bool(g["dd_equity_pct"] < max(pt[a]["dd_equity_pct"], pt[b]["dd_equity_pct"]) - 5),
                           nhan="MÔ PHỎNG (cộng equity 2 lần chạy MT5 thật)"))
    ra.sort(key=lambda r: -r["diem"])
    return ra


def danh_muc_sau(pt: dict, ung: list[str], tq_max: float = 0.3, toi_da: int = 5, lan_ngau_nhien: int = 3000,
                 hat: int = 5) -> dict:
    ngay = pd.DataFrame({k: pt[k]["lai_ngay_s"] for k in ung}).fillna(0.0)
    tq = ngay.corr().fillna(0.0)
    cache = {}

    def do(n):
        k = tuple(sorted(n))
        if k not in cache:
            cache[k] = do_nhom(pt, k)
        return cache[k]

    def ok_tq(n):
        return all(tq.at[a, b] <= tq_max for a, b in itertools.combinations(n, 2))

    def ok_cap(n):   # moi cap toi da 2 he (tranh phu thuoc 1 cap)
        s = [pt[k]["symbol"] for k in n]
        return max(s.count(x) for x in s) <= 2

    rng = np.random.default_rng(hat)
    thu = set()
    for goc in ung:                                     # tham lam tu moi goc
        n = [goc]
        while len(n) < toi_da:
            tot = None
            for k in ung:
                if k in n or not ok_tq(n + [k]) or not ok_cap(n + [k]):
                    continue
                r = do(n + [k])
                if tot is None or r["diem"] > tot[1]["diem"]:
                    tot = (k, r)
            if not tot or tot[1]["diem"] <= do(n)["diem"]:
                break
            n.append(tot[0])
        thu.add(tuple(sorted(n)))
    for _ in range(lan_ngau_nhien):
        sz = int(rng.integers(2, min(toi_da, len(ung)) + 1))
        n = list(rng.choice(ung, sz, replace=False))
        if ok_tq(n) and ok_cap(n):
            do(n); thu.add(tuple(sorted(n)))
    tat = [cache[k] for k in thu if len(k) >= 2 and k in cache] + [v for k, v in cache.items() if len(k) >= 2]
    uniq = {tuple(sorted(r["he"])): r for r in tat}
    tat = list(uniq.values())
    theo_tran = {}
    for t in TRAN_DD:
        c = [r for r in tat if r["dd_equity_pct"] <= t]
        c.sort(key=lambda r: -r["lai_kep_pct_nam"])
        theo_tran[str(int(t))] = c[:3]
    tat.sort(key=lambda r: -r["diem"])
    return {"tot_theo_diem": tat[:8], "theo_tran_dd": theo_tran, "so_nhom_da_do": len(cache),
            "tuong_quan_max": tq_max, "nhan": "MÔ PHỎNG (cộng equity tái dựng của các lần chạy MT5 thật, vốn 1.000 USD/hệ)"}


def stress_nhom(pt: dict, nhom, stress_eq: dict) -> dict:
    v0 = 1000.0 * len(nhom)
    eq, eqc = [v0 + pd.DataFrame({k: stress_eq[k][c] - 1000.0 for k in nhom}).sort_index().ffill().fillna(0.0).sum(axis=1)
               for c in ("equity_xau", "equity")]
    nam = (eq.index[-1] - eq.index[0]).days / 365.25
    return {"lai_kep_pct_nam": round(V.lai_kep(v0, eqc.iloc[-1], nam), 2), "dd_equity_pct": round(V.dd_pct(eq), 2)}


def _cat(m: dict, a=None, b=None) -> dict:
    dv = m["_dv"]
    dv = dv[(dv.index >= a) if a is not None else slice(None)]
    dv = dv[(dv.index < b) if b is not None else slice(None)]
    if len(dv):
        dv = dv - (dv["equity"].iloc[0] - 1000.0)          # dat lai goc 1.000 USD dau doan (cong, khong lai kep)
    ls = m["lai_ngay_s"]
    ls = ls[((ls.index >= a) if a is not None else True) & ((ls.index < b) if b is not None else True)]
    return dict(m, _dv=dv, lai_ngay_s=ls, dd_equity_pct=V.dd_pct(dv["equity_xau"]) if len(dv) else 0.0)


def danh_muc_oos(pt: dict, ung: list[str], ti_le: float = 0.6, lan: int = 1500) -> dict:
    """Chong qua khop khi CHON danh muc: chon tren 60% dau ky, do tren 40% sau (chua thay luc chon). MÔ PHỎNG."""
    t0 = min(pt[k]["_dv"].index[0] for k in ung); t1 = max(pt[k]["_dv"].index[-1] for k in ung)
    moc = t0 + (t1 - t0) * ti_le
    is_ = {k: _cat(pt[k], b=moc) for k in ung}
    os_ = {k: _cat(pt[k], a=moc) for k in ung}
    ok = [k for k in ung if len(is_[k]["_dv"]) > 100 and len(os_[k]["_dv"]) > 100]
    d = danh_muc_sau(is_, ok, lan_ngau_nhien=lan)
    ra = []
    for r in d["tot_theo_diem"][:5]:
        o = do_nhom(os_, r["he"])
        ra.append({"he": r["he"], "is_lai": r["lai_kep_pct_nam"], "is_dd": r["dd_equity_pct"],
                   "oos_lai": o["lai_kep_pct_nam"], "oos_dd": o["dd_equity_pct"]})
    # moc so sanh: chia deu 1/N tat ca ung vien (khong chon)
    deu = do_nhom(os_, ok)
    return {"moc": str(moc.date()), "chon": ra, "deu_tat_ca_oos": {"lai": deu["lai_kep_pct_nam"], "dd": deu["dd_equity_pct"],
            "so_he": len(ok)}, "nhan": "MÔ PHỎNG (chọn trên IS, đo OOS)"}


def chay(in_ra=print) -> dict:
    uv = V.ung_vien_dat()
    pt, loi = {}, {}
    for r in uv:
        m = V.phan_tich_mt5(r["ten"], net_bao_cao=r.get("lai_rong"))
        if m.get("loi"):
            loi[r["ten"]] = m["loi"]; continue
        m["symbol"] = r["symbol"]; m["tf"] = r["tf"] or tf_tu_htm(r["ten"]) or "CHƯA ĐO ĐƯỢC"
        m["tf_nguon"] = "UNG_VIEN" if r["tf"] else "htm MT5"
        m["lai_bao_cao"], m["dd_bao_cao"] = r["lai_kep_pct_nam"], r["dd_von_pct"]
        m["lai_ngay_s"] = pd.Series({pd.Timestamp(k): v for k, v in m["lai_ngay"].items()}, dtype=float)
        pt[r["ten"]] = m
    in_ra("vong2_sau: %d hệ đo được, %d lỗi" % (len(pt), len(loi)), flush=True)
    the_cap = {}
    for k, m in pt.items():
        the_cap.setdefault(re.sub(r"^od_|_XM_CSV$", "", k), set()).add(m["symbol"])
    bang, stress_eq = [], {}
    for k, m in pt.items():
        sp = stress_phi(k, lech=m.get("lech_net_khop_cuoi_ky") or 0.0)
        p, g = V.doc_vi_the(V.KQ_MT5 / (k + "_vao.csv_lenh_mt5.csv")), V.doc_gia_mt5(V.KQ_MT5 / (k + "_vao.csv_gia.csv"))
        stress_eq[k] = V._khop_net(V.duong_von(p, g, 1000.0, V.chi_phi_stress(p, g)), m.get("lech_net_khop_cuoi_ky") or 0.0)
        cb = canh_bao_qua_khop(m, 1)
        s15 = next(x for x in sp if x["spread_x"] == 1.5)
        dat = bool(s15["lai_kep_pct_nam"] >= 10 and m["dd_equity_stress_pct"] <= 80)
        bang.append({"ten": k, "symbol": m["symbol"], "tf": m["tf"], "tf_nguon": m["tf_nguon"], "so_nam": m["so_nam"],
                     "so_lenh": m["so_lenh"], "lai_bao_cao": m["lai_bao_cao"], "lai_kep": m["lai_kep_pct_nam"],
                     "dd_equity": m["dd_equity_pct"], "dd_bao_cao": m["dd_bao_cao"],
                     "wf": [d["lai_kep_pct_nam"] for d in m["walk_forward"]],
                     "mc_p95": (m["monte_carlo"].get("equity") or {}).get("dd_equity_p95"),
                     "mc_chay": (m["monte_carlo"].get("equity") or {}).get("ti_le_chay"),
                     "stress": sp, "canh_bao": cb, "dat_sau_phi": dat,
                     "ben": bool(dat and not any(c.startswith(("lịch sử", "ít lệnh", "có đoạn", "MC")) for c in cb))})
    bang.sort(key=lambda b: -(b["stress"][1]["lai_kep_pct_nam"] / max(b["dd_equity"], 5)))
    ung = [b["ten"] for b in bang if b["dat_sau_phi"] and b["so_nam"] >= 1.5]
    gc = ghep_cung_cap(pt)
    dm = danh_muc_sau(pt, ung)
    ben = [b["ten"] for b in bang if b["ben"]]
    dm_ben = danh_muc_sau(pt, ben) if len(ben) >= 2 else None
    for d in (dm, dm_ben):
        if not d:
            continue
        for r in d["tot_theo_diem"] + [x for v in d["theo_tran_dd"].values() for x in v]:
            r["stress"] = stress_nhom(pt, r["he"], stress_eq)
            r["phu_thuoc_cap"] = sorted({pt[k]["symbol"] for k in r["he"]})
    oos = danh_muc_oos(pt, ung)
    kq = {"danh_muc_oos": oos, "luc": time.strftime("%Y-%m-%d %H:%M"), "bang": bang, "loi": loi, "ghep_cung_cap": gc[:30],
          "so_doi_ghep": len(gc), "danh_muc": dm, "danh_muc_ben": dm_ben, "ung_vien_danh_muc": ung, "ben": ben}
    (RA / "ket_qua_vong2_sau.json").write_text(json.dumps(V._so(kq), ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return kq




def uu_tien_hang_cho(thanh_phan: set, tep: Path = V.HANG_CHO_V2, cong: float = 10.0) -> list[str]:
    """Viec vong 2 co he goc nam trong danh muc tot nhat -> +diem (chay truoc), danh dau 'danh_muc_v2_sau'. Idempotent."""
    if not tep.exists():
        return []
    ra, dong = [], []
    for x in tep.read_text(encoding="utf-8").splitlines():
        try:
            v = json.loads(x)
        except ValueError:
            continue
        if v.get("vong2_goc") in thanh_phan and not v.get("danh_muc_v2_sau"):
            v["diem"] = float(v.get("diem") or 60) + cong; v["danh_muc_v2_sau"] = True
        if v.get("danh_muc_v2_sau"):
            ra.append(v["ten"])
        dong.append(json.dumps(v, ensure_ascii=False, sort_keys=True, default=str))
    tep.write_text("".join(d + "\n" for d in dong), encoding="utf-8")
    return ra


def _f(x, d=1):
    return "—" if x is None else ("%." + str(d) + "f") % x


def _ds(he):
    return "<br>".join("`%s`" % h for h in he)


def ghi_md(kq: dict) -> str:
    L = ["## 6. Vòng 2 SÂU — cả 78 hệ ĐẠT, chỉ dùng lệnh MT5 thật (`python -m nhan.vong2_sau`)", "",
         "Lúc chạy: %s (giờ box, UTC+7). Đo được %d/78 hệ (lỗi: %d). Cột TF trống trong `UNG_VIEN.md` được điền từ dòng "
         "*Period* của báo cáo MT5 `.htm`. **Stress phí, ghép, danh mục, Monte Carlo = MÔ PHỎNG** (cộng equity tái dựng từ "
         "lệnh MT5 thật, vốn 1.000 USD/hệ). Hoa hồng thật XM micro: **CHƯA ĐO ĐƯỢC** (báo cáo = 0) → thử 0 / 7 / 14 USD/100k." % (
             kq["luc"], len(kq["bang"]), len(kq["loi"])), "",
         "Tóm tắt: %d/%d hệ vẫn ≥ 10%%/năm và DD equity ≤ 80%% sau stress spread ×1,5 + hoa hồng 7 USD; %d/%d sau spread ×3 + "
         "14 USD. %d hệ “bền” (qua stress, ≥ 2 năm, ≥ 30 lệnh, không đoạn WF âm, MC DD p95 ≤ 80%%)." % (
             sum(b["dat_sau_phi"] for b in kq["bang"]), len(kq["bang"]),
             sum(b["stress"][3]["lai_kep_pct_nam"] >= 10 and b["stress"][3]["dd_equity_pct"] <= 80 for b in kq["bang"]),
             len(kq["bang"]), len(kq["ben"])), "",
         "### 6.1 Stress phí + cảnh báo quá khớp (xếp theo lãi sau stress ×1,5 / DD)", "",
         "| id | Symbol | TF | Năm | Lệnh | %/năm MT5 | DD equity % | ×1,5+7 | ×2+7 | ×3+14 | WF 3 đoạn | MC DD p95 | Bền | Cảnh báo |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in kq["bang"]:
        s = b["stress"]
        L.append("| %s | %s | %s | %.2f | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            b["ten"], b["symbol"], b["tf"] + ("*" if b["tf_nguon"] != "UNG_VIEN" else ""), b["so_nam"], b["so_lenh"],
            _f(b["lai_kep"]), _f(b["dd_equity"]), _f(s[1]["lai_kep_pct_nam"]), _f(s[2]["lai_kep_pct_nam"]), _f(s[3]["lai_kep_pct_nam"]),
            " / ".join(_f(x, 0) for x in b["wf"]), _f(b["mc_p95"]), "✔" if b["ben"] else "", "; ".join(b["canh_bao"]) or "—"))
    L += ["", "\\* TF lấy từ báo cáo MT5 `.htm`.", "",
          "### 6.2 Ghép cùng cặp từ lệnh MT5 thật (2 hệ chạy song song, MÔ PHỎNG)", "",
          "Đã đo %d đôi. “Bù trừ” = DD tổng thấp hơn DD lớn hơn của 2 hệ ít nhất 5 điểm." % kq["so_doi_ghep"], "",
          "| Symbol | Hệ | %/năm | DD % | A %/năm / DD | B %/năm / DD | Tương quan ngày | Bù trừ |", "|---|---|---|---|---|---|---|---|"]
    for g in kq["ghep_cung_cap"][:15]:
        L.append("| %s | %s | %s | %s | %s / %s | %s / %s | %s | %s |" % (
            g["symbol"], _ds(g["he"]), _f(g["lai_kep_pct_nam"]), _f(g["dd_equity_pct"]), _f(g["lai_a"]), _f(g["dd_a"]),
            _f(g["lai_b"]), _f(g["dd_b"]), _f(g["tuong_quan_ngay"], 2), "có" if g["bu_tru"] else "không"))
    for ten, key in (("tất cả hệ qua stress", "danh_muc"), ("chỉ hệ “bền”", "danh_muc_ben")):
        d = kq.get(key)
        if not d:
            continue
        L += ["", "### 6.3 Danh mục (%s) — tương quan ngày ≤ %.1f, tối đa 2 hệ/cặp, đã đo %d nhóm (MÔ PHỎNG)" % (
            ten, d["tuong_quan_max"], d["so_nhom_da_do"]), "",
              "| Loại | Hệ | Cặp | Vốn USD | %/năm | DD equity % | Sau stress ×1,5+7: %/năm / DD |", "|---|---|---|---|---|---|---|"]
        for r in d["tot_theo_diem"][:3]:
            L.append("| điểm lãi/DD | %s | %s | %d | %s | %s | %s / %s |" % (_ds(r["he"]), ", ".join(r["phu_thuoc_cap"]), r["von"],
                     _f(r["lai_kep_pct_nam"]), _f(r["dd_equity_pct"]), _f(r["stress"]["lai_kep_pct_nam"]), _f(r["stress"]["dd_equity_pct"])))
        for t, v in d["theo_tran_dd"].items():
            for r in v[:1]:
                L.append("| lãi cao nhất, DD ≤ %s%% | %s | %s | %d | %s | %s | %s / %s |" % (t, _ds(r["he"]), ", ".join(r["phu_thuoc_cap"]),
                         r["von"], _f(r["lai_kep_pct_nam"]), _f(r["dd_equity_pct"]), _f(r["stress"]["lai_kep_pct_nam"]),
                         _f(r["stress"]["dd_equity_pct"])))
    o = kq["danh_muc_oos"]
    L += ["", "### 6.4 Kiểm tra quá khớp khi CHỌN danh mục: chọn trên đoạn trước %s, đo đoạn sau (MÔ PHỎNG)" % o["moc"], "",
          "| Hệ (chọn trên IS) | IS %/năm | IS DD % | OOS %/năm | OOS DD % |", "|---|---|---|---|---|"]
    for r in o["chon"]:
        L.append("| %s | %s | %s | %s | %s |" % (_ds(r["he"]), _f(r["is_lai"]), _f(r["is_dd"]), _f(r["oos_lai"]), _f(r["oos_dd"])))
    L += ["| *Chia đều cả %d hệ (không chọn)* | | | %s | %s |" % (o["deu_tat_ca_oos"]["so_he"], _f(o["deu_tat_ca_oos"]["lai"]),
                                                                _f(o["deu_tat_ca_oos"]["dd"])), "",
          "→ DD của danh mục “tốt nhất trong mẫu” tăng mạnh ngoài mẫu: số DD 7–20 % ở bảng 6.3 là **lạc quan**, cần cộng biên an toàn.", "",
          "### 6.5 Hàng chờ", "", "Việc MT5 vòng 2 có hệ gốc nằm trong các danh mục trên được cộng 10 điểm ưu tiên "
          "(`danh_muc_v2_sau=true`): %d việc. Hệ không có tín hiệu Python trên box (bản dịch ở máy nhà) → không sinh được việc chuyển "
          "cặp/khung: **CHƯA ĐO ĐƯỢC**." % len(kq.get("uu_tien") or []), ""]
    return "\n".join(L)


def ghi_vao_ket_qua(md: str, tep: Path = RA / "KET_QUA_VONG2.md") -> None:
    cu = tep.read_text(encoding="utf-8") if tep.exists() else ""
    i = cu.find("## 6. Vòng 2 SÂU")
    tep.write_text((cu[:i] if i >= 0 else cu.rstrip() + "\n\n") + md, encoding="utf-8")


def main() -> int:
    k = chay()
    tp = {h for d in (k["danh_muc"], k.get("danh_muc_ben")) if d
          for r in d["tot_theo_diem"][:4] + [x for v in d["theo_tran_dd"].values() for x in v] for h in r["he"]}
    k["uu_tien"] = uu_tien_hang_cho(tp)
    ghi_vao_ket_qua(ghi_md(k))
    print(len(k["bang"]), len(k["ung_vien_danh_muc"]), len(k["ben"]), len(k["uu_tien"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
