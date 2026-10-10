#!/usr/bin/env python3
"""Vòng thí nghiệm (chạy được trên Linux, không cần MT5).

    quét mẫu EA → bóc tách cơ chế → mô phỏng Python → tối ưu thông số → giữ cái tốt

    python vong_thu_nghiem.py                       # dữ liệu giả lập H1
    python vong_thu_nghiem.py --csv gia.csv         # dữ liệu thật (time,open,high,low,close)
    python vong_thu_nghiem.py --json ket_qua.json   # ghi kết quả

Cách làm (cập nhật 10/10/2026):
  1. Chia chuỗi theo THỜI GIAN: 70% đầu để TỐI ƯU, 30% sau để KIỂM. Không bao
     giờ chọn tham số trên phần kiểm.
  2. Tối ưu = dò theo từng toạ độ (coordinate descent) trên các hằng số mà
     `ngu_phap.tham_so_cua` phơi ra (chu kỳ, ngưỡng, số bar giữ), 2 lượt.
     Mục tiêu: Sharpe năm hoá trên phần tối ưu, cần ≥ `--lenh-toi-thieu` lệnh.
  3. GIỮ LẠI chỉ khi CẢ phần tối ưu LẪN phần KIỂM (ngoài mẫu) đều có ý nghĩa
     thống kê: t = Sharpe_năm × sqrt(số năm) ≥ `--t-tu` (2,0) trên phần tối ưu
     và ≥ `--t-kiem` (1,5) trên phần kiểm, và đủ lệnh. Đo 10/10/2026: ngưỡng
     "Sharpe kiểm > 0" giữ 3-5 cơ chế trên dữ liệu NGẪU NHIÊN (5 seed), ngưỡng
     "Sharpe ≥ 0,5 cả hai phần" vẫn giữ 0-3 - tức là đồng xu, vì nửa năm dữ
     liệu thì sai số chuẩn của Sharpe năm đã ~1,5. Cơ chế trùng vân tay (cùng
     điều kiện ở nhiều file) chỉ chạy 1 lần.
  4. Dùng đúng `chieu` của cơ chế (bản cũ bỏ qua nên lệnh bán chạy như lệnh mua).

Trên dữ liệu giả lập (bước ngẫu nhiên, không có lợi thế) gần như KHÔNG cơ chế
nào nên được giữ - đó là phép thử placebo của chính vòng lặp. Nếu thấy nhiều
cơ chế "tốt" trên dữ liệu ngẫu nhiên thì vòng lặp đang tự lừa mình.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from nhan import doc_ma as DM          # noqa: E402
from nhan import ngu_phap as NP        # noqa: E402
from nhan import mo_phong as MP        # noqa: E402
from nhan import chi_phi as CP         # noqa: E402

BAR_NAM = {"H1": 24 * 260, "D1": 260}


def du_lieu_gia_lap(n: int = 24 * 400, seed: int = 42, khung: str = "H1") -> pd.DataFrame:
    """Bước ngẫu nhiên có biến động theo giờ - KHÔNG có lợi thế nào cài sẵn."""
    rng = np.random.default_rng(seed)
    freq = "h" if khung == "H1" else "D"
    idx = pd.date_range("2021-01-04", periods=n, freq=freq)
    sd = 0.0007 if khung == "H1" else 0.006
    r = rng.normal(0, sd, n)
    close = 1.10 * np.exp(np.cumsum(r))
    open_ = np.r_[close[0], close[:-1]]
    rong = np.abs(rng.normal(0, sd * 0.6, n))
    return pd.DataFrame({
        "open": open_,
        "high": np.maximum(open_, close) + rong,
        "low": np.minimum(open_, close) - rong,
        "close": close,
        "tick_volume": rng.integers(200, 2000, n),
    }, index=idx)


def doc_csv(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p)
    cot = {c.lower(): c for c in df.columns}
    tg = cot.get("time") or cot.get("date") or cot.get("datetime") or df.columns[0]
    df.index = pd.to_datetime(df[tg])
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close"]
              + (["tick_volume"] if "tick_volume" in df.columns else [])].astype(float)


def danh_gia(spec: dict, df: pd.DataFrame, khung: str) -> dict:
    th = NP.sinh_tu_spec(spec, df)
    kq = MP.chay(df, th, CP.MoHinhChiPhi(ma="EURUSD"), ma="EURUSD", khung=khung)
    loi = np.nan_to_num(np.asarray(kq.loi, dtype=float))
    sd = loi.std()
    sharpe = float(loi.mean() / sd * math.sqrt(BAR_NAM.get(khung, 260))) if sd > 0 else 0.0
    return {"so_lenh": int(kq.so_lenh), "phoi_nhiem": round(float(kq.phoi_nhiem), 4),
            "loi_log": round(float(loi.sum()), 5), "sharpe": round(sharpe, 3)}


def _ung_vien(khoa: str, v) -> list:
    if khoa == "giu":
        return sorted({1, 2, 3, 5, 8, 13, int(v)})
    if isinstance(v, (int, np.integer)) or (khoa.endswith("_n") and float(v).is_integer()):
        return sorted({max(1, int(round(v * f))) for f in (0.5, 0.75, 1, 1.25, 1.5, 2)})
    v = float(v)
    if v.is_integer() and 0 <= v <= 23:            # ngưỡng giờ: dịch ±1, ±2
        return sorted({min(23.0, max(0.0, v + d)) for d in (-2, -1, 0, 1, 2)})
    return sorted({v * f for f in (0.8, 0.9, 1, 1.1, 1.25)})


def _diem(r: dict, lenh_min: int) -> float:
    return r["sharpe"] if r["so_lenh"] >= lenh_min else -1e9


def toi_uu(spec: dict, df: pd.DataFrame, khung: str, lenh_min: int,
           luot: int = 2) -> tuple[dict, dict, int]:
    """Dò từng toạ độ. Trả (tham số tốt nhất, kết quả trên phần tối ưu, số lần chạy)."""
    ts = NP.tham_so_cua(spec)
    tot, kq_tot = dict(ts), danh_gia(spec, df, khung)
    so_chay = 1
    for _ in range(luot):
        doi = False
        for khoa in list(ts):
            for v in _ung_vien(khoa, tot[khoa]):
                if v == tot[khoa]:
                    continue
                thu = dict(tot, **{khoa: v})
                try:
                    r = danh_gia(NP.ap_tham_so(spec, thu), df, khung)
                except Exception:
                    continue
                so_chay += 1
                if _diem(r, lenh_min) > _diem(kq_tot, lenh_min) + 1e-9:
                    tot, kq_tot, doi = thu, r, True
        if not doi:
            break
    return tot, kq_tot, so_chay


def chay_mot_file(path: Path, df: pd.DataFrame, khung: str = "H1",
                  toi_uu_bat: bool = True, lenh_min: int = 20,
                  t_tu: float = 2.0, t_kiem: float = 1.5,
                  da_thay: set | None = None) -> list[dict]:
    vb = path.read_text(encoding="utf-8", errors="ignore")
    r = DM.doc_chien_luoc(vb, nguon=path.name)
    cat = int(len(df) * 0.7)
    df_tu, df_kiem = df.iloc[:cat], df.iloc[cat:]
    ra = []
    for spec in r.get("co_che", []):
        dong = {"file": path.name, "ten": spec.get("ten"), "chieu": spec.get("chieu"),
                "ho": spec.get("ho"), "so_dieu_kien": spec.get("so_dieu_kien")}
        vt = NP.van_tay_dieu_kien(spec) + f"|{spec.get('chieu')}"
        if da_thay is not None:
            if vt in da_thay:
                dong["trung"] = True
                ra.append(dong)
                continue
            da_thay.add(vt)
        try:
            loi_cp = NP.kiem_khai_bao(spec)
            dong["kiem_cu_phap"] = loi_cp
            goc_tu = danh_gia(spec, df_tu, khung)
            goc_kiem = danh_gia(spec, df_kiem, khung)
            dong.update(goc_tu=goc_tu, goc_kiem=goc_kiem)
            spec_tot, ts = spec, NP.tham_so_cua(spec)
            if toi_uu_bat and ts:
                ts_tot, kq_tu, so_chay = toi_uu(spec, df_tu, khung, lenh_min)
                spec_tot = NP.ap_tham_so(spec, ts_tot)
                dong.update(tham_so_goc=ts, tham_so_tot=ts_tot, so_lan_chay=so_chay,
                            tot_tu=kq_tu)
            kiem = danh_gia(spec_tot, df_kiem, khung)
            tu = dong.get("tot_tu", goc_tu)
            dong["tot_kiem"] = kiem
            nam_tu = len(df_tu) / BAR_NAM.get(khung, 260)
            nam_kiem = len(df_kiem) / BAR_NAM.get(khung, 260)
            dong["t_tu"] = round(tu["sharpe"] * math.sqrt(nam_tu), 2)
            dong["t_kiem"] = round(kiem["sharpe"] * math.sqrt(nam_kiem), 2)
            dong["giu_lai"] = bool(dong["t_tu"] >= t_tu and dong["t_kiem"] >= t_kiem
                                   and kiem["so_lenh"] >= lenh_min and not loi_cp)
        except Exception as e:                       # noqa: BLE001
            if type(e).__name__ == "KhungThieuGio":
                dong["khong_hop_khung"] = str(e)[:80]   # cơ chế theo giờ trên D1
            else:
                dong["loi"] = f"{type(e).__name__}: {e}"
            dong["giu_lai"] = False
        ra.append(dong)
    return ra


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mau", default=str(LAB / "mau_thu"))
    ap.add_argument("--csv", help="chuỗi giá thật (time,open,high,low,close)")
    ap.add_argument("--khung", default="H1", choices=sorted(BAR_NAM))
    ap.add_argument("--n", type=int, default=24 * 400, help="số bar giả lập")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--khong-toi-uu", action="store_true")
    ap.add_argument("--lenh-toi-thieu", type=int, default=20)
    ap.add_argument("--t-tu", type=float, default=2.0)
    ap.add_argument("--t-kiem", type=float, default=1.5)
    ap.add_argument("--json", help="ghi kết quả ra file này")
    a = ap.parse_args(argv)

    df = doc_csv(Path(a.csv)) if a.csv else du_lieu_gia_lap(a.n, a.seed, a.khung)
    tong, da_thay = [], set()
    for f in sorted(Path(a.mau).glob("*.mq5")):
        tong.extend(chay_mot_file(f, df, a.khung, not a.khong_toi_uu, a.lenh_toi_thieu,
                                  a.t_tu, a.t_kiem, da_thay))

    loi = [x for x in tong if "loi" in x]
    giu = [x for x in tong if x.get("giu_lai")]
    trung = [x for x in tong if x.get("trung")]
    lech = [x for x in tong if x.get("khong_hop_khung")]
    print(f"Dữ liệu: {'CSV ' + a.csv if a.csv else 'giả lập'} {a.khung}, {len(df)} bar "
          f"(tối ưu 70% đầu, kiểm 30% sau)")
    chay = len(tong) - len(loi) - len(trung) - len(lech)
    print(f"Cơ chế: {len(tong)} bóc được, {len(trung)} trùng, {len(lech)} không hợp "
          f"khung, {len(loi)} lỗi, {chay} chạy được   → giữ lại: {len(giu)}")
    for x in tong:
        if x.get("trung") or x.get("khong_hop_khung"):
            continue
        if "loi" in x:
            print(f"  LỖI {x['file'][:38]:38s} {x['ten']}: {x['loi']}")
            continue
        gk, tk = x["goc_kiem"], x["tot_kiem"]
        print(f"  {'GIỮ' if x['giu_lai'] else '   '} {x['file'][:38]:38s} "
              f"{str(x['ten'])[:34]:34s} chieu={x['chieu']:+d} "
              f"kiểm: gốc sh={gk['sharpe']:+.2f}/{gk['so_lenh']}l → tối ưu "
              f"sh={tk['sharpe']:+.2f}/{tk['so_lenh']}l  t={x['t_tu']:+.1f}/{x['t_kiem']:+.1f}"
              + ("" if not x.get("kiem_cu_phap") else "  [không qua kiểm cú pháp]"))
    if a.json:
        Path(a.json).write_text(json.dumps(tong, ensure_ascii=False, indent=1,
                                           default=str), encoding="utf-8")
        print(f"Đã ghi {a.json}")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
