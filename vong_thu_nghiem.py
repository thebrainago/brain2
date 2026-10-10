#!/usr/bin/env python3
"""Vòng thí nghiệm (chạy được trên Linux, không cần MT5).

    quét mẫu EA → bóc tách cơ chế → mô phỏng Python → tối ưu thông số → giữ cái tốt

    python vong_thu_nghiem.py                       # dữ liệu giả lập H1
    python vong_thu_nghiem.py --csv gia.csv         # dữ liệu thật (time,open,high,low,close)
    python vong_thu_nghiem.py --json ket_qua.json   # ghi kết quả

NHÃN (10/10/2026 khuya, không đổi GIỮ/BỎ): mỗi cơ chế in "đạt tiêu chí 25/09?" (tiêu chí của
chủ dự án: lãi sau phí phần kiểm > 0, maxDD < 80 %, không cháy) cạnh cổng hiện tại; hệ có rổ in
thêm dòng "mô phỏng lệch so với MT5" (P1, `hieu_chuan/P1_KET_QUA.md`).

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
  5. ĐỦ LỆNH Ở CẢ HAI PHẦN (10/10/2026 khuya): `--lenh-toi-thieu` (20) là mức
     cho phần KIỂM; phần tối ưu phải có ≥ 20·70/30 = 47 lệnh (cùng mật độ lệnh).
     Bộ tối ưu chỉ chọn tham số đạt mức đó (không nhìn phần kiểm); thiếu lệnh ở
     phần nào thì ghi `it_lenh` và KHÔNG giữ.
  6. Cơ chế mang `trong_bar` (EA kiểm lại MỖI tick → lệnh dừng khớp giữa bar,
     do `doc_ma._kiem_moi_tick` phát hiện) chạy bằng
     `mo_phong.chay_dung_trong_bar`; bản xấp xỉ tick đầu cũ chỉ ghi để so sánh.
  7. NHÓM (10/10/2026 đêm): các chân cùng `mot_lenh_ngay.nhom` (mua + bán của MỘT
     lệnh vào EA) chạy CHUNG bằng `mo_phong.chay_he`: một vị thế một lúc, một
     lệnh/ngày, SL/TP/kéo SL của EA (`sltp`), chặn chéo cờ/lọc. Tối ưu cả hệ,
     tham số chung (input EA) buộc lại; giữ/bỏ theo cả hệ, in thêm từng chân.
  8. CỔNG GIỮ CHO LƯỚI/MARTINGALE (10/10/2026, sau 57657761). Placebo random
     walk cho lưới Sharpe kiểm DƯƠNG 10/10 seed → Sharpe/t KHÔNG phải phép thử
     hợp lệ cho hệ có `ro.luoi`. Hệ lưới chỉ được GIỮ khi qua ĐỦ (ngưỡng t/lệnh
     cũ VẪN áp, không nới):
       a. SỐNG SÓT với tài khoản KHAI BÁO (`--von` 10.000 USD, `--don-bay` 100,
          `--stop-out` 0,5): 0 lần stop-out, không cháy, ở CẢ phần tối ưu lẫn kiểm
          (`mo_phong.chay_he(tai_khoan=...)`: ký quỹ, stop-out chính xác trong bar,
          từ chối lệnh thiếu ký quỹ). Bộ tối ưu loại bộ tham số có stop-out.
       b. Lời ròng (sau phí) phần kiểm > 0.
       c. THẮNG GIẢ DƯỢC CÙNG CẤU TRÚC trên CHÍNH phần kiểm: `placebo_cung_cau_truc`
          giữ nguyên rổ (lưới, chốt đỉnh, chuỗi lot, cổng bar, vào lại giữa bar,
          luật ngày, tài khoản) và thời điểm được phép vào, chỉ thay CHIỀU vào
          bằng tung đồng xu mỗi bar. Thước đo khai báo: `loi_log` ròng phần kiểm.
          p = (1 + #placebo ≥ thật)/(N + 1), N = `--n-placebo` (99); giữ khi
          p ≤ `--p-placebo` (0,05).
       d. (10/10/2026 tối) XÁC SUẤT CHÁY THEO NĂM ≤ `--p-chay-nam` (0,05):
          `ti_le_chay_nam` - stop-out ĐẦU TIÊN mỗi lần chạy, phơi nhiễm đến lúc
          đó, λ = max(thật, placebo cùng cấu trúc), P = 1 − e^(−λ). Chỉ SIẾT thêm.
       Stop-out mô phỏng kiểu MT5: đóng lệnh lỗ nhất trước, từng lệnh; trượt giá
       + qua đêm trừ thẳng vào vốn (`mo_phong.chay_he`).
  9. (10/10/2026 đêm) RỔ HEDGE CŨNG QUA CỔNG: mọi hệ có `ro` (rổ hedge Breakout2/
     2-2/3 lẫn lưới Breakout5) chạy với tài khoản khai báo và qua CÙNG cổng a-d ở
     mục 8 (`la_ro`; trước đây chỉ hệ `ro.luoi`). Rổ hedge mở lệnh ở tick đầu
     theo `cho` (không có chân lệnh dừng trong bar) nên placebo cùng cấu trúc chạy
     được y như lưới (đồng xu thay chiều lệnh đầu; hedge/chốt đỉnh/cắt lỗ giữ nguyên).
     Hệ `ro` có chân lệnh dừng trong bar (`muc`/`co`) - hiện KHÔNG có - thì
     `chan_placebo` vẫn NotImplementedError: bỏ phần placebo (c) có GHI LÝ DO
     `placebo_bo_qua`, vẫn áp a, b, d (d chỉ từ hệ thật) và ngưỡng t cũ.
     KHỐI LƯỢNG TỐI ĐA: `--lot-max` (SYMBOL_VOLUME_MAX, mặc định 100 lot/lệnh) và
     `--lot-tong-max` (SYMBOL_VOLUME_LIMIT, 0 = không giới hạn): sàn TỪ CHỐI lệnh
     vượt mức (không cắt lot) - `mo_phong.chay_he`.

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

# Tai khoan KHAI BAO cho he luoi/martingale (cong giu luoi). Lenh dau EA = 0,02 lot.
# 10.000 USD, don bay 1:100, stop-out 50% (muc ESMA/nhieu san; XM quoc te 20%,
# don bay toi 1:1000 - do nhay: --von/--don-bay/--stop-out).
# lot_max = SYMBOL_VOLUME_MAX (lot/lenh). 100 = muc pho bien cho EURUSD tai khoan
# chuan/ECN (nhieu san de 50-500; tai khoan micro/cent thap hon nhieu tinh theo lot
# chuan) - GIA DINH, khong doc tu san; do nhay: --lot-max. lot_tong_max =
# SYMBOL_VOLUME_LIMIT (tong cung chieu), None = khong gioi han (mac dinh MT5 = 0).
TAI_KHOAN_MAC_DINH = {"von": 10000.0, "don_bay": 100.0, "stop_out": 0.5,
                      "lot_max": 100.0, "lot_tong_max": None}

# `_Point` cua ma dang chay (them 11/10/2026): SL/TP/hedge/luoi tinh bang DIEM cua EA
# (`Stop_Loss*_Point`) can buoc gia. MAC DINH 1e-5 = EURUSD 5 so le (XM/Dukascopy) -
# GIA DINH khai bao, doi bang `--diem` (USDJPY 1e-3, XAUUSD 1e-2). Truoc day `chay_he`
# tu uoc tu muc gia (`_diem_tu_gia`, cung 1e-5 voi EURUSD). Co che dung no mang
# `gia_dinh_diem` va dong ket qua ghi `diem_gia_dinh`.
DIEM = 1e-5


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


def du_lieu_gia_lap_duong(n: int = 24 * 400, seed: int = 42, khung: str = "H1",
                          buoc: int = 60) -> pd.DataFrame:
    """Bước ngẫu nhiên ĐÚNG ĐƯỜNG GIÁ: mỗi bar dựng từ `buoc` bước con, nên
    high/low là cực trị THẬT của đường đi trong bar và open bar sau = close bar
    trước. Đây là placebo đúng cho lệnh dừng TRONG bar: theo định lý dừng tuỳ
    chọn, khớp ở mức L rồi giữ tới open bar sau có kỳ vọng lãi thô = 0.
    (`du_lieu_gia_lap` vẽ râu nến bằng nhiễu độc lập với đường giá - râu đó
    "chạm" mức rồi giá không hề đi qua, sai cho placebo trong bar.)"""
    rng = np.random.default_rng(seed)
    freq = "h" if khung == "H1" else "D"
    idx = pd.date_range("2021-01-04", periods=n, freq=freq)
    sd = (0.0007 if khung == "H1" else 0.006) / math.sqrt(buoc)
    duong = 1.10 * np.exp(np.cumsum(rng.normal(0, sd, n * buoc)))
    duong = np.r_[1.10, duong]
    o = duong[:-1:buoc][:n]
    khoi = np.lib.stride_tricks.sliding_window_view(duong, buoc + 1)[::buoc][:n]
    return pd.DataFrame({
        "open": o, "high": khoi.max(axis=1), "low": khoi.min(axis=1),
        "close": khoi[:, -1], "tick_volume": rng.integers(200, 2000, n),
    }, index=idx)


def doc_csv(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p)
    cot = {c.lower(): c for c in df.columns}
    tg = cot.get("time") or cot.get("date") or cot.get("datetime") or df.columns[0]
    df.index = pd.to_datetime(df[tg])
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close"]
              + (["tick_volume"] if "tick_volume" in df.columns else [])].astype(float)


def mo_hinh_chi_phi(df: pd.DataFrame, ma: str = "EURUSD",
                    khong_phi: bool = False, phi_cu: bool = False) -> CP.MoHinhChiPhi:
    """Chi phi THAT cua du an (`chi_phi.tu_du_lieu`: spread do tu bar/san, truot
    1/4 spread, phi qua dem do tu san).

    LOI TIM RA 10/10/2026 khuya: truoc do vong nay goi `CP.MoHinhChiPhi(ma=...)`
    - constructor TRAN, moi thanh phan = 0. Tuc MOI ket qua vong lap truoc day
    (ke ca bang so trong GHI_CHU) la KHONG PHI, du ghi "sau phi".
    `khong_phi=True` chi de so sanh voi so cu.

    P3 (11/10/2026): mac dinh PHI DUNG THOI KY (`chi_phi.ap_thoi_ky`): swap tinh theo LENH
    qua rollover nua dem gio server (x3 thu Tu), ti le swap theo THANG = chenh lai suat qua
    dem (FRED) + markup san do hom nay, spread theo NAM khi bar co cot spread (khong co ->
    CHUA DO DUOC, giu spread hom nay). `phi_cu=True` -> mo hinh truoc P3 (chi de so sanh).
    """
    if khong_phi:
        return CP.MoHinhChiPhi(ma=ma)
    cp = CP.tu_du_lieu(ma, df)
    return cp if phi_cu else CP.ap_thoi_ky(cp, df, ma)


def danh_gia(spec: dict, df: pd.DataFrame, khung: str, tick_dau: bool = False,
             cp: CP.MoHinhChiPhi | None = None) -> dict:
    """Chay mot co che. Co che mang `trong_bar` (EA kiem lai moi tick -> lenh
    dung khop giua bar) chay bang `mo_phong.chay_dung_trong_bar`; `tick_dau=True`
    ep chay ban xap xi tick dau (chi de so sanh)."""
    cp = cp if cp is not None else mo_hinh_chi_phi(df)
    if spec.get("trong_bar") and not tick_dau:
        cho, muc, huong = NP.sinh_trong_bar(spec, df)
        kq = MP.chay_dung_trong_bar(df, cho, muc, huong, int(spec.get("chieu", 1) or 1),
                                    int(spec.get("giu", 1) or 1), cp, ma="EURUSD",
                                    khung=khung)
    else:
        th = NP.sinh_tu_spec(spec, df)
        kq = MP.chay(df, th, cp, ma="EURUSD", khung=khung)
    loi = np.nan_to_num(np.asarray(kq.loi, dtype=float))
    sd = loi.std()
    sharpe = float(loi.mean() / sd * math.sqrt(BAR_NAM.get(khung, 260))) if sd > 0 else 0.0
    return {"so_lenh": int(kq.so_lenh), "phoi_nhiem": round(float(kq.phoi_nhiem), 4),
            "loi_log": round(float(loi.sum()), 5), "sharpe": round(sharpe, 3),
            "maxdd_pct": round(_maxdd_pct(loi), 2)}


def _sharpe(loi: np.ndarray, khung: str) -> float:
    loi = np.nan_to_num(np.asarray(loi, dtype=float))
    sd = loi.std()
    return float(loi.mean() / sd * math.sqrt(BAR_NAM.get(khung, 260))) if sd > 0 else 0.0


def _maxdd_pct(loi) -> float:
    """Sut giam lon nhat (%) cua duong von exp(cumsum(loi)) - o muc phoi nhiem MO PHONG
    (lenh don: von danh nghia 1 lenh = don bay 1). Dung cho NHAN 25/09, khong cho cong giu."""
    loi = np.nan_to_num(np.asarray(loi, dtype=float))
    if not len(loi):
        return 0.0
    eq = np.exp(np.concatenate([[0.0], np.cumsum(loi)]))
    return float(np.max(1.0 - eq / np.maximum.accumulate(eq)) * 100.0)


#: Tieu chi duyet cua chu du an (25/09/2026, nhac lai 10/10/2026): CO LAI SAU PHI + maxDD < 80 %
#: (don bay <= 10, tai khoan khong chay); luoi/martingale/DCA hop le. Brain2 GIU cong cu (t,
#: placebo, chay/nam) - day CHI LA NHAN in canh ket qua, KHONG doi GIU/BO.
DD_25_09 = 80.0
#: P1 (10/10/2026, hieu_chuan/P1_KET_QUA.md): 15 o MT5 tester sach chi do luoi TP-trung-binh
#: (`nhan/luoi.py` ThamSo). Ro cua EA (Breakout5 chot dinh / ro hedge) co luat thoat KHAC ->
#: chua co dap an MT5. Dong co duong-gia cung kieu (`_duong_bar`) lech -2,6..+4,3 diem %/nam
#: (co tia) / -9,5..+6,1 (khong tia) tren 15 o; ban cuc-tri `luoi.chay` lech +1,1..+32,8 (co tia).
CANH_BAO_MT5_RO = ("mô phỏng lệch so với MT5: CHƯA ĐO ĐƯỢC cho rổ EA này (P1 chỉ có đáp án "
                   "lưới TP-trung-bình; động cơ đường-giá cùng kiểu lệch -9,5…+6,1 điểm %/năm "
                   "trên 15 ô MT5) - số lãi rổ là MÔ PHỎNG, không phải tiền thật")


def nhan_25_09(kiem: dict) -> dict:
    """NHAN 'dat tieu chi 25/09?' tren phan KIEM: lai sau phi > 0, maxDD < 80 %, khong chay
    (tai khoan khai bao neu co). Chi la nhan; khong doi `giu_lai`."""
    tk = kiem.get("tai_khoan") or {}
    lai = float(kiem.get("loi_log", 0.0))
    if tk:
        von = float(tk.get("von_dau") or 0.0)
        dd = (1.0 - float(tk["von_rong_min"]) / von) * 100.0 if von > 0 else float("nan")
        nguon_dd = "tài khoản, từ vốn đầu"
        chay = bool(tk.get("chay")) or int(tk.get("so_stop_out", 0)) > 0
        lai = float(tk.get("von_cuoi", 0.0)) - von
    else:
        dd = float(kiem.get("maxdd_pct", float("nan")))
        nguon_dd = "đòn bẩy 1"
        chay = False
    ly = []
    if not lai > 0:
        ly.append("không lãi sau phí")
    if not dd < DD_25_09:
        ly.append(f"maxDD {dd:.0f}% ≥ {DD_25_09:.0f}%")
    if chay:
        ly.append("stop-out/cháy")
    return {"dat": not ly, "maxdd_pct": round(dd, 2), "nguon_dd": nguon_dd, "ly_do": ly}


def la_luoi(specs: list[dict]) -> bool:
    """He co luoi martingale (`ro.luoi`) -> cong giu luoi (xem docstring muc 8)."""
    return any((sp.get("ro") or {}).get("luoi") for sp in specs)


def la_ro(specs: list[dict]) -> bool:
    """He co RO lenh (`ro`: ro hedge Breakout2/2-2/3 hoac luoi Breakout5) -> tai
    khoan khai bao + cong ro/luoi (docstring muc 8-9)."""
    return any(sp.get("ro") for sp in specs)


def danh_gia_nhom(specs: list[dict], df: pd.DataFrame, khung: str,
                  cp: CP.MoHinhChiPhi | None = None, tai_khoan: dict | None = None,
                  chan: list[dict] | None = None) -> dict:
    """Chay CA NHOM chan (mua + ban cua mot lenh vao EA) chung mot tai khoan:
    mot vi the mot luc, luat mot lenh/ngay, SL/TP/keo SL - `mo_phong.chay_he`.
    `tai_khoan` (von/don_bay/stop_out) -> mo hinh ky quy cho ro lenh.
    `chan` - chan da dung san (placebo); None -> `NP.sinh_chan`."""
    cp = cp if cp is not None else mo_hinh_chi_phi(df)
    if chan is None:
        chan = [NP.sinh_chan(sp, df) for sp in specs]
    kq = MP.chay_he(df, chan, cp, ma="EURUSD", khung=khung, tai_khoan=tai_khoan, diem=DIEM)
    loi = np.nan_to_num(np.asarray(kq.loi, dtype=float))
    chan = [{"chieu": c["chieu"], "so_lenh": int(c["so_lenh"]),
             "so_hedge": int(c.get("so_hedge", 0)),
             "loi_log": round(float(np.sum(c["loi"])), 5),
             "sharpe": round(_sharpe(c["loi"], khung), 3)} for c in kq.chi_tiet["chan"]]
    ra = {"so_lenh": int(kq.so_lenh), "phoi_nhiem": round(float(kq.phoi_nhiem), 4),
          "loi_log": round(float(loi.sum()), 5), "sharpe": round(_sharpe(loi, khung), 3),
          "maxdd_pct": round(_maxdd_pct(loi), 2), "chan": chan}
    if kq.chi_tiet.get("ro_bat_thuong"):
        ra["ro_bat_thuong"] = int(kq.chi_tiet["ro_bat_thuong"])
    if kq.chi_tiet.get("luoi"):
        # luoi martingale: so lenh / lot lon nhat trong mot ro, lo tha noi lon nhat ($)
        # - EA KHONG gioi han; ky quy + SYMBOL_VOLUME_MAX/LIMIT o `tai_khoan` (tu_choi_*)
        lu = kq.chi_tiet["luoi"]
        ra["luoi"] = {"max_lenh": int(lu["max_lenh"]), "max_lot": round(float(lu["max_lot"]), 2),
                      "lo_tha_noi_max_usd": round(float(lu["lo_tha_noi_max"]), 2),
                      "vuot_chuoi": int(lu["vuot_chuoi"])}
    if kq.chi_tiet.get("tai_khoan"):
        t = kq.chi_tiet["tai_khoan"]
        mk = float(t["muc_ky_quy_min"])
        ra["tai_khoan"] = {"von_dau": round(float(t["von_dau"]), 2),
                           "von_cuoi": round(float(t["von"]), 2),
                           "von_rong_min": round(float(t["von_rong_min"]), 2),
                           "muc_ky_quy_min": round(mk, 3) if math.isfinite(mk) else None,
                           "so_stop_out": int(t["so_stop_out"]),
                           "so_lenh_stop_out": int(t.get("so_lenh_stop_out", 0)),
                           "bar_stop_out_dau": (int(t["bar_stop_out"][0])
                                                if t.get("bar_stop_out") else None),
                           "so_bar": int(len(df)),
                           "phi_truot_usd": round(float(t.get("phi_truot_usd", 0.0)), 2),
                           "phi_qua_dem_usd": round(float(t.get("phi_qua_dem_usd", 0.0)), 2),
                           "tu_choi_ky_quy": int(t["tu_choi_ky_quy"]),
                           "tu_choi_lot_max": int(t.get("tu_choi_lot_max", 0)),
                           "chay": bool(t["chay"])}
    return ra


def song_sot(r: dict) -> bool:
    """Ket qua `danh_gia_nhom` co tai khoan: 0 stop-out va khong chay."""
    t = r.get("tai_khoan")
    return t is None or (t["so_stop_out"] == 0 and not t["chay"])


def chan_placebo(specs: list[dict], df: pd.DataFrame, rng: np.random.Generator) -> list[dict]:
    """Chan GIA DUOC CUNG CAU TRUC: giu MOI thu cua `sinh_chan` (ro/luoi, chot
    dinh, chuoi lot, cong bar, luat ngay, SL/TP) va THOI DIEM duoc phep vao
    (`cho` cua bat ky chan nao), chi thay CHIEU bang tung dong xu moi bar:
    bar i tung dong xu chon CHIEU (+1/-1, deu), roi chon deu mot chan cua chieu
    do; chi chan do duoc vao. He phai co chan CA HAI chieu (khong thi khong
    co null "chieu ngau nhien" -> NotImplementedError).
    Vao lai giua bar (`muc_lai`) giu nguyen co che, chieu = chieu dong xu cua bar.
    Chan vao bang lenh dung trong bar (`muc`) -> NotImplementedError (muc gia
    gan voi tin hieu that; chua co null tuong ung)."""
    goc = [NP.sinh_chan(sp, df) for sp in specs]
    if any(c.get("muc") is not None or c.get("co") is not None for c in goc):
        raise NotImplementedError("placebo cung cau truc: chua ho tro chan lenh dung trong bar")
    n = len(df)
    cho_bat_ky = np.zeros(n, dtype=bool)
    for c in goc:
        cho_bat_ky |= np.asarray(c["cho"], dtype=bool)
    mua = [k for k, c in enumerate(goc) if c["chieu"] > 0]
    ban = [k for k, c in enumerate(goc) if c["chieu"] < 0]
    if not mua or not ban:
        raise NotImplementedError("placebo cung cau truc: can chan ca hai chieu")
    dau = rng.integers(0, 2, n)
    chon = np.where(dau == 1, np.asarray(mua)[rng.integers(0, len(mua), n)],
                    np.asarray(ban)[rng.integers(0, len(ban), n)])
    ra = []
    for k, c in enumerate(goc):
        c = dict(c)
        bat = cho_bat_ky & (chon == k)
        c["cho"] = bat
        if c.get("muc_lai") is not None:
            # _so(gia, phep_lai, muc): muc rat lon/nho de dung khi bat, sai khi tat
            dung_khi_lon = c["phep_lai"] in ("<", "<=")
            to, nho = 1e12, -1e12
            c["muc_lai"] = np.where(bat, to if dung_khi_lon else nho,
                                    nho if dung_khi_lon else to).astype(float)
        ra.append(c)
    return ra


def placebo_cung_cau_truc(specs: list[dict], df: pd.DataFrame, khung: str,
                          cp: CP.MoHinhChiPhi, tai_khoan: dict | None, n: int = 99,
                          seed: int = 0) -> list[dict]:
    """N lan chay he voi `chan_placebo` (seed co dinh -> tai lap)."""
    rng = np.random.default_rng(seed)
    return [danh_gia_nhom(specs, df, khung, cp=cp, tai_khoan=tai_khoan,
                          chan=chan_placebo(specs, df, rng)) for _ in range(n)]


def ti_le_chay_nam(ds: list[dict], nam: float) -> dict:
    """Tan suat CHAY (stop-out DAU TIEN) theo nam tren cac lan chay dai `nam` nam.

    Chi dem lan stop-out DAU TIEN moi lan chay (sau do tai khoan da tan, stop-out
    tung lenh lap lai khong phai "rui ro moi"); thoi gian phoi nhiem cua lan chay
    co su kien = den bar stop-out dau (`bar_stop_out_dau / so_bar * nam`; thieu ->
    ca `nam`, bao thu nhe). MLE mu: lambda = so lan chay co su kien / tong phoi
    nhiem; P(chay trong 1 nam) = 1 - exp(-lambda). `p_tren95` = can tren 95% mot
    phia (xap xi Poisson (k + 1.645*sqrt(k+1) + 1) / phoi nhiem) - chi bao cao."""
    k, T = 0, 0.0
    for r in ds:
        t = r.get("tai_khoan") or {}
        if int(t.get("so_stop_out", 0)) > 0 or t.get("chay"):
            k += 1
            b, n = t.get("bar_stop_out_dau"), t.get("so_bar")
            T += float(nam) * (b / n if b is not None and n else 1.0)
        else:
            T += float(nam)
    if T <= 0:
        return {"so_stop_out": k, "nam_phoi_nhiem": 0.0, "lambda": None, "p_nam": None,
                "p_tren95": None}
    lam = k / T
    lam_tr = (k + 1.645 * math.sqrt(k + 1) + 1) / T
    return {"so_stop_out": k, "nam_phoi_nhiem": round(T, 3), "lambda": round(lam, 5),
            "p_nam": round(1 - math.exp(-lam), 5), "p_tren95": round(1 - math.exp(-lam_tr), 5)}


def cong_luoi(that_tu: dict, that_kiem: dict, placebo: list[dict],
              p_nguong: float = 0.05, nam_kiem: float | None = None,
              p_chay_nam: float = 0.05, placebo_bo_qua: str | None = None) -> dict:
    """Cong giu cho he luoi (docstring muc 8). Thuoc do: `loi_log` rong phan kiem.
    p mot phia = (1 + #placebo >= that) / (N + 1).

    THEM (10/10/2026 toi) - XAC SUAT CHAY THEO NAM (chi SIET them): song sot tren
    MOT duong gia ~0,8 nam la phep thu yeu cho duoi martingale (placebo EURUSD
    song 96%). Cau truc ro/luoi giong het placebo; placebo cho N x nam_kiem
    nam-mau cua CHINH cau truc do (chi khac chieu). P_nam = 1 - exp(-lambda),
    lambda = max(tan suat stop-out that, tan suat stop-out placebo) / nam.
    Loai khi P_nam > `p_chay_nam` (0,05). Ly do dung placebo: mot chieu "co edge"
    thay tren vai nam kiem khong du bang chung de xoa rui ro duoi CUA CAU TRUC;
    he that ma it chay hon placebo thi van bi loai neu chinh cau truc chay > 5%/nam
    (bao thu, dung huong "chi siet").

    `placebo_bo_qua` (ly do): KHONG dung duoc placebo cung cau truc (he ro co
    chan lenh dung trong bar -> `chan_placebo` NotImplementedError). Khi do bo
    dieu kien (c), ghi ly do; (a), (b), (d - chi tu he that) van ap."""
    x = float(that_kiem["loi_log"])
    pl = np.array([float(r["loi_log"]) for r in placebo])
    N = len(pl)
    p = float((1 + np.sum(pl >= x)) / (N + 1)) if N else 1.0
    ss_pl = float(np.mean([song_sot(r) for r in placebo])) if N else float("nan")
    ly_do = []
    if not song_sot(that_tu):
        ly_do.append("stop_out_toi_uu")
    if not song_sot(that_kiem):
        ly_do.append("stop_out_kiem")
    if x <= 0:
        ly_do.append("lo_rong_kiem")
    if placebo_bo_qua is None and p > p_nguong:
        ly_do.append(f"khong_thang_placebo p={p:.3f}>{p_nguong}")
    chay = None
    if nam_kiem:
        c_that = ti_le_chay_nam([that_kiem], nam_kiem)
        c_pl = ti_le_chay_nam(placebo, nam_kiem) if N else {
            "so_stop_out": 0, "nam_phoi_nhiem": 0.0, "lambda": None, "p_nam": None,
            "p_tren95": None}
        lam = max(c_that["lambda"] or 0.0, c_pl["lambda"] or 0.0)
        p_nam = 1 - math.exp(-lam)
        chay = {"that": c_that, "placebo": c_pl, "p_nam": round(p_nam, 5),
                "nguong": p_chay_nam}
        if p_nam > p_chay_nam:
            ly_do.append(f"xac_suat_chay_nam {p_nam:.3f}>{p_chay_nam}")
    return {"thuoc_do": "loi_log_rong_kiem", "that": round(x, 5), "n_placebo": N,
            "chay_nam": chay,
            "placebo_tb": round(float(pl.mean()), 5) if N else None,
            "placebo_q95": round(float(np.quantile(pl, 0.95)), 5) if N else None,
            "placebo_duong": round(float(np.mean(pl > 0)), 3) if N else None,
            "placebo_song_sot": round(ss_pl, 3) if N else None,
            "p": round(p, 4) if placebo_bo_qua is None else None, "p_nguong": p_nguong,
            "placebo_bo_qua": placebo_bo_qua,
            "dat": not ly_do, "ly_do": ly_do}


def buoc_tham_so(spec: dict) -> list[list[str]]:
    """Nhom khoa tham so (ten nhu `NP.tham_so_cua`) PHAI di CUNG nhau vi la MOT
    input cua EA (them 11/10/2026). Bo toi uu chi doi ca nhom mot luc - CHI SIET
    (it bac tu do hon), khong bao gio noi.

    (a) `n` cua cac nut chi bao GIONG HET nhau trong mot co che (vd `rsi21` o bar
        da dong va `rsi21` song trong `muc_song` - cung mot handle `iRSI`; ema10
        o hai do tre). Tach roi thi giao cat `rsi[1]>=30 && rsi[0]<30` thanh
        `rsi42>=24 va rsi26_song<33` - mot chien luoc KHAC, them bac tu do.
    (b) nguong cua `muc_song{cua: C, nguong: v}` va hang `v` cua dieu kien khac co
        ve trai la C (bo boc `tre`): cung muc `100-RSI_Level` cua EA.
    Hai input tinh co bang nhau cung bi buoc - chap nhan (chi siet)."""
    nut: dict = {}

    def _di(n, duong):
        if isinstance(n, dict):
            for k, v in n.items():
                if k in NP.KHOA_CHINH_DUOC and isinstance(v, (int, float)) and \
                        not isinstance(v, bool):
                    nut[f"{duong}_{k}" if duong else k] = (n, k)
                else:
                    _di(v, f"{duong}_{k}" if duong else str(k))
        elif isinstance(n, list):
            for i, v in enumerate(n):
                _di(v, f"{duong}{i}")
    _di(spec, "")
    nhom: dict = {}
    for duong, (d, k) in nut.items():
        if k == "n" and d.get("chi_bao") not in (None, "tre"):
            # bo `lay`: cac buffer cua MOT handle (iBands duoi/tren/giua, iIchimoku
            # tenkan/kijun) chung mot chu ky input (them 11/10/2026)
            d_ = {x: y for x, y in d.items() if x != "lay"}
            nhom.setdefault(("cb", json.dumps(d_, sort_keys=True)), []).append(duong)

    def _goc(t):
        while isinstance(t, dict) and t.get("chi_bao") == "tre":
            t = t.get("cua")
        return t
    vao = spec.get("vao") or []
    for k, dk in enumerate(vao):
        ph = (dk or {}).get("phai") or {}
        ng = ph.get("nguong") if ph.get("chi_bao") == "muc_song" else None
        if not isinstance(ng, dict) or "hang" not in ng:
            continue
        C = json.dumps(ph.get("cua"), sort_keys=True)
        for j, d2 in enumerate(vao):
            if j != k and json.dumps(_goc((d2 or {}).get("trai")), sort_keys=True) == C \
                    and (d2 or {}).get("phai") == {"hang": ng["hang"]}:
                g = nhom.setdefault(("hang", k), [f"vao{k}_phai_nguong_hang"])
                g.append(f"vao{j}_phai_hang")
    return [sorted(set(g)) for g in nhom.values()
            if len(set(g)) > 1 and all(x in nut for x in g)]


def khoa_tre(spec: dict) -> set:
    """Khoa `n` cua nut `tre` (do tre bar) - KHONG toi uu (them 11/10/2026, chi siet).

    Do tre la CHI SO BAR trong ma EA (`MA[1] > MA[2]`, `CopyBuffer(..,1,2,..)`), khong
    phai input: doi no la doi DINH NGHIA tin hieu (giao cat `ema10 tre1 < ema30 tre2`
    khong con la giao cat) va them bac tu do. Do tren 015/017: bo toi uu chon tre 2
    cho mot ve, tre 1 cho ve kia. Ca dich `ma_shift` la input cung bi giu nguyen."""
    ra: set = set()

    def _di(n, duong):
        if isinstance(n, dict):
            for k, v in n.items():
                if k == "n" and n.get("chi_bao") == "tre" and isinstance(v, int) \
                        and not isinstance(v, bool):
                    ra.add(f"{duong}_{k}" if duong else k)
                elif k not in NP.KHOA_CHINH_DUOC:
                    _di(v, f"{duong}_{k}" if duong else str(k))
        elif isinstance(n, list):
            for i, v in enumerate(n):
                _di(v, f"{duong}{i}")
    _di(spec, "")
    return ra


def _gop_buoc(ts: dict, ax: dict, specs: list[dict]) -> tuple[dict, dict]:
    """Gop cac khoa `ts` cua cung mot nhom `buoc_tham_so` (moi chan) thanh mot."""
    for c, sp in enumerate(specs):
        for g in buoc_tham_so(sp):
            khoa = [k for k in ts if any((c, m) in ax[k] for m in g)]
            if len(khoa) < 2 or len({ts[k] for k in khoa}) != 1:
                continue
            dau = khoa[0]
            for k in khoa[1:]:
                ax[dau] = ax[dau] + [x for x in ax[k] if x not in ax[dau]]
                del ts[k], ax[k]
    return ts, ax


def tham_so_nhom(specs: list[dict]) -> tuple[dict, dict]:
    """Tham so CHUNG cua nhom: khoa co mat o moi chan voi CUNG gia tri la mot
    input cua EA (gio, chu ky MA, TPFactor...) -> mot tham so; con lai tach
    rieng `c{k}.<khoa>`. Tra (tham so, anh xa khoa -> [(chan, khoa chan)])."""
    rieng = [{k: v for k, v in NP.tham_so_cua(sp).items() if k not in khoa_tre(sp)}
             for sp in specs]
    ts, ax = {}, {}
    chung = set(rieng[0]).intersection(*rieng[1:]) if rieng else set()
    for k in sorted(chung):
        if all(r[k] == rieng[0][k] for r in rieng):
            ts[k] = rieng[0][k]
            ax[k] = [(c, k) for c in range(len(specs))]
    for c, r in enumerate(rieng):
        for k, v in r.items():
            if k not in ts:
                ts[f"c{c}.{k}"] = v
                ax[f"c{c}.{k}"] = [(c, k)]
    return _gop_buoc(ts, ax, specs)


def ap_tham_so_nhom(specs: list[dict], ax: dict, ts: dict) -> list[dict]:
    moi = [dict() for _ in specs]
    for k, v in ts.items():
        for c, kc in ax.get(k, []):
            moi[c][kc] = v
    return [NP.ap_tham_so(sp, m) for sp, m in zip(specs, moi)]


def _ung_vien(khoa: str, v) -> list:
    if khoa == "giu":
        return sorted({1, 2, 3, 5, 8, 13, int(v)})
    if khoa.endswith("sltp_tp"):                    # TP = R x he so
        return sorted({0.5, 0.75, 1.0, 1.5, 2.0, 3.0, float(v)})
    if khoa.endswith(("sltp_sl_diem", "sltp_tp_diem")):  # SL/TP = N x _Point (input EA)
        return sorted({max(1, int(round(float(v) * f))) for f in (0.5, 0.75, 1, 1.25, 1.5, 2)})
    if khoa.endswith(("sltp_sl_he", "sltp_tp_he")):  # SL/TP = he so x ATR
        return sorted({round(float(v) * f, 4) for f in (0.5, 0.75, 1, 1.25, 1.5, 2)})
    if isinstance(v, (int, np.integer)) or (khoa.endswith("_n") and float(v).is_integer()):
        return sorted({max(1, int(round(v * f))) for f in (0.5, 0.75, 1, 1.25, 1.5, 2)})
    v = float(v)
    if v.is_integer() and 0 <= v <= 23:            # ngưỡng giờ: dịch ±1, ±2
        return sorted({min(23.0, max(0.0, v + d)) for d in (-2, -1, 0, 1, 2)})
    return sorted({v * f for f in (0.8, 0.9, 1, 1.1, 1.25)})


def _diem(r: dict, lenh_min: int) -> float:
    # bo tham so lam tai khoan khai bao bi stop-out / chay -> loai (cong luoi)
    if not song_sot(r):
        return -1e9
    return r["sharpe"] if r["so_lenh"] >= lenh_min else -1e9


def toi_uu(spec: dict, df: pd.DataFrame, khung: str, lenh_min: int,
           luot: int = 2, cp: CP.MoHinhChiPhi | None = None) -> tuple[dict, dict, int]:
    """Dò từng toạ độ. Trả (tham số tốt nhất, kết quả trên phần tối ưu, số lần chạy).
    Khoá cùng một input EA (`buoc_tham_so`) dò chung; kết quả trả về đủ mọi khoá."""
    cp = cp if cp is not None else mo_hinh_chi_phi(df)
    tre = khoa_tre(spec)
    ts0 = {k: v for k, v in NP.tham_so_cua(spec).items() if k not in tre}
    ts, ax = _gop_buoc(dict(ts0), {k: [(0, k)] for k in ts0}, [spec])
    tot, kq, so = _do_toa_do(
        ts, lambda t: danh_gia(ap_tham_so_nhom([spec], ax, t)[0], df, khung, cp=cp),
        lenh_min, luot)
    return {m: tot[k] for k, ds in ax.items() for _, m in ds}, kq, so


def toi_uu_nhom(specs: list[dict], df: pd.DataFrame, khung: str, lenh_min: int,
                luot: int = 2, cp: CP.MoHinhChiPhi | None = None,
                tai_khoan: dict | None = None) -> tuple[dict, dict, int, dict]:
    """Như `toi_uu` cho CẢ NHÓM (mục tiêu = Sharpe của cả EA). Trả thêm ánh xạ."""
    cp = cp if cp is not None else mo_hinh_chi_phi(df)
    ts, ax = tham_so_nhom(specs)
    tot, kq, so = _do_toa_do(
        ts, lambda t: danh_gia_nhom(ap_tham_so_nhom(specs, ax, t), df, khung, cp=cp,
                                    tai_khoan=tai_khoan),
        lenh_min, luot)
    return tot, kq, so, ax


def _do_toa_do(ts: dict, ham, lenh_min: int, luot: int) -> tuple[dict, dict, int]:
    tot, kq_tot = dict(ts), ham(dict(ts))
    so_chay = 1
    for _ in range(luot):
        doi = False
        for khoa in list(ts):
            for v in _ung_vien(khoa.split(".")[-1], tot[khoa]):
                if v == tot[khoa]:
                    continue
                thu = dict(tot, **{khoa: v})
                try:
                    r = ham(thu)
                except Exception:
                    continue
                so_chay += 1
                if _diem(r, lenh_min) > _diem(kq_tot, lenh_min) + 1e-9:
                    tot, kq_tot, doi = thu, r, True
        if not doi:
            break
    return tot, kq_tot, so_chay


def lenh_min_phan_tu(lenh_min: int, n_tu: int, n_kiem: int) -> int:
    """So lenh TOI THIEU tren phan TOI UU de phan KIEM ky vong du `lenh_min`.

    Bo toi uu KHONG duoc nhin phan kiem, nen khong the doi "du lenh tren phan
    kiem" trong luc chon tham so. Nhung no CO THE doi MAT DO lenh: voi chia
    70/30, can >= lenh_min * 70/30 lenh tren phan toi uu thi cung mat do do
    cho ~lenh_min lenh tren phan kiem. Do 10/10/2026: chi doi `lenh_min` (20)
    tren phan toi uu thi Breakout5-2-2 mua chon `giu=8`, dung 20 lenh tren phan
    toi uu (phoi nhiem 99,6% - thuc chat mua-giu) va 5 lenh tren phan kiem.
    """
    if n_kiem <= 0:
        return lenh_min
    return max(lenh_min, int(math.ceil(lenh_min * n_tu / n_kiem)))


def chay_mot_file(path: Path, df: pd.DataFrame, khung: str = "H1",
                  toi_uu_bat: bool = True, lenh_min: int = 20,
                  t_tu: float = 2.0, t_kiem: float = 1.5,
                  da_thay: set | None = None,
                  cp: CP.MoHinhChiPhi | None = None,
                  tai_khoan: dict | None = None, n_placebo: int = 99,
                  p_placebo: float = 0.05, p_chay_nam: float = 0.05) -> list[dict]:
    vb = path.read_text(encoding="utf-8", errors="ignore")
    r = DM.doc_chien_luoc(vb, nguon=path.name)
    cat = int(len(df) * 0.7)
    df_tu, df_kiem = df.iloc[:cat], df.iloc[cat:]
    lenh_min_tu = lenh_min_phan_tu(lenh_min, len(df_tu), len(df_kiem))
    cp = cp if cp is not None else mo_hinh_chi_phi(df)
    ra = []
    # NHOM (10/10/2026 dem): cac chan cua CUNG mot lenh vao co luat mot lenh/ngay
    # -> mo phong chung (`danh_gia_nhom`), khong tach rieng tung chieu.
    nhom: dict[str, list[dict]] = {}
    don = []
    for spec in r.get("co_che", []):
        # `nhom_he`: cac chan dong theo RO / SL-TP khoang cach cua CUNG mot EA
        # (mot vi the mot luc) ma khong co luat mot lenh/ngay.
        g = (spec.get("mot_lenh_ngay") or {}).get("nhom") or spec.get("nhom_he")
        if not g and (spec.get("sltp") or spec.get("dong_mo_bar")):
            # SL/TP / dong lenh cua EA (11/10/2026): `danh_gia` (giu N bar) BO QUA chung
            # -> chay rieng mot chan bang `mo_phong.chay_he` (nhom mot phan tu)
            g = f"rieng@{len(nhom)}:{spec.get('ten')}"
        if g:
            nhom.setdefault(g, []).append(spec)
        else:
            don.append(spec)
    for g, specs in nhom.items():
        ra.append(_chay_nhom(path, g, specs, df_tu, df_kiem, khung, toi_uu_bat,
                             lenh_min, lenh_min_tu, t_tu, t_kiem, da_thay, cp,
                             tai_khoan=tai_khoan, n_placebo=n_placebo,
                             p_placebo=p_placebo, p_chay_nam=p_chay_nam))
    for spec in don:
        dong = {"file": path.name, "ten": spec.get("ten"), "chieu": spec.get("chieu"),
                "ho": spec.get("ho"), "so_dieu_kien": spec.get("so_dieu_kien")}
        vt = NP.van_tay_dieu_kien(spec) + f"|{spec.get('chieu')}" + \
            (f"|tb{json.dumps(spec['trong_bar'], sort_keys=True)}"
             if spec.get("trong_bar") else "")
        if spec.get("trong_bar"):
            dong["trong_bar"] = spec["trong_bar"]
        if da_thay is not None:
            if vt in da_thay:
                dong["trung"] = True
                ra.append(dong)
                continue
            da_thay.add(vt)
        try:
            loi_cp = NP.kiem_khai_bao(spec)
            dong["kiem_cu_phap"] = loi_cp
            goc_tu = danh_gia(spec, df_tu, khung, cp=cp)
            goc_kiem = danh_gia(spec, df_kiem, khung, cp=cp)
            dong.update(goc_tu=goc_tu, goc_kiem=goc_kiem)
            if spec.get("trong_bar"):
                # ban xap xi tick dau cu - chi de thay mo hinh trong bar doi gi
                dong["goc_kiem_tick_dau"] = danh_gia(spec, df_kiem, khung, tick_dau=True,
                                                     cp=cp)
            spec_tot, ts = spec, NP.tham_so_cua(spec)
            if toi_uu_bat and ts:
                ts_tot, kq_tu, so_chay = toi_uu(spec, df_tu, khung, lenh_min_tu, cp=cp)
                spec_tot = NP.ap_tham_so(spec, ts_tot)
                dong.update(tham_so_goc=ts, tham_so_tot=ts_tot, so_lan_chay=so_chay,
                            tot_tu=kq_tu)
            kiem = danh_gia(spec_tot, df_kiem, khung, cp=cp)
            tu = dong.get("tot_tu", goc_tu)
            dong["tot_kiem"] = kiem
            dong["tieu_chi_25_09"] = nhan_25_09(kiem)
            nam_tu = len(df_tu) / BAR_NAM.get(khung, 260)
            nam_kiem = len(df_kiem) / BAR_NAM.get(khung, 260)
            dong["t_tu"] = round(tu["sharpe"] * math.sqrt(nam_tu), 2)
            dong["t_kiem"] = round(kiem["sharpe"] * math.sqrt(nam_kiem), 2)
            # DU LENH tren CA HAI phan, khong chi phan toi uu. Thieu lenh thi t
            # cua phan do khong co nghia thong ke -> bao cao `it_lenh` va khong giu.
            it = []
            if tu["so_lenh"] < lenh_min_tu:
                it.append(f"toi_uu {tu['so_lenh']}<{lenh_min_tu}")
            if kiem["so_lenh"] < lenh_min:
                it.append(f"kiem {kiem['so_lenh']}<{lenh_min}")
            if it:
                dong["it_lenh"] = it
            dong["giu_lai"] = bool(dong["t_tu"] >= t_tu and dong["t_kiem"] >= t_kiem
                                   and not it and not loi_cp)
        except Exception as e:                       # noqa: BLE001
            if type(e).__name__ == "KhungThieuGio":
                dong["khong_hop_khung"] = str(e)[:80]   # cơ chế theo giờ trên D1
            else:
                dong["loi"] = f"{type(e).__name__}: {e}"
            dong["giu_lai"] = False
        ra.append(dong)
    return ra


def _van_tay_nhom(specs: list[dict]) -> str:
    phan = []
    for sp in specs:
        mln = dict(sp.get("mot_lenh_ngay") or {})
        mln.pop("nhom", None)
        phan.append(NP.van_tay_dieu_kien(sp) + f"|{sp.get('chieu')}|" + json.dumps(
            {"tb": sp.get("trong_bar"), "sltp": sp.get("sltp"), "mln": mln,
             "ro": sp.get("ro"), "dmb": sp.get("dong_mo_bar")},
            sort_keys=True))
    return "NHOM:" + "||".join(sorted(phan))


def _chay_nhom(path: Path, g: str, specs: list[dict], df_tu, df_kiem, khung: str,
               toi_uu_bat: bool, lenh_min: int, lenh_min_tu: int, t_tu: float,
               t_kiem: float, da_thay: set | None, cp,
               tai_khoan: dict | None = None, n_placebo: int = 99,
               p_placebo: float = 0.05, p_chay_nam: float = 0.05) -> dict:
    dong = {"file": path.name, "nhom": g,
            "ten": "HE " + " + ".join(str(sp.get("ten"))[:28] for sp in specs),
            "chieu": 0, "ho": specs[0].get("ho"),
            "so_dieu_kien": sum(int(sp.get("so_dieu_kien") or 0) for sp in specs),
            "chan": [{"ten": sp.get("ten"), "chieu": sp.get("chieu"),
                      "trong_bar": sp.get("trong_bar"), "sltp": sp.get("sltp"),
                      "ro": sp.get("ro")}
                     for sp in specs]}
    if any(sp.get("gia_dinh_diem") for sp in specs):
        dong["diem_gia_dinh"] = DIEM
    if any(sp.get("dong_mo_bar") for sp in specs):
        dong["dong_mo_bar"] = [sp.get("dong_mo_bar") for sp in specs]
    vt = _van_tay_nhom(specs)
    if da_thay is not None:
        if vt in da_thay:
            dong["trung"] = True
            return dong
        da_thay.add(vt)
    luoi = la_luoi(specs)
    ro = la_ro(specs)
    # tai khoan khai bao cho MOI he co ro (luoi + ro hedge; muc 9). He khac
    # (lenh don SL/TP/giu N bar): so lieu y het truoc.
    tk = (tai_khoan or TAI_KHOAN_MAC_DINH) if ro else None
    if luoi:
        dong["luoi"] = True
    if ro:
        dong["loai_ro"] = "luoi" if luoi else "hedge"
        dong["tai_khoan_khai_bao"] = dict(tk)
    try:
        loi_cp = [e for sp in specs for e in NP.kiem_khai_bao(sp)]
        dong["kiem_cu_phap"] = loi_cp
        goc_tu = danh_gia_nhom(specs, df_tu, khung, cp=cp, tai_khoan=tk)
        goc_kiem = danh_gia_nhom(specs, df_kiem, khung, cp=cp, tai_khoan=tk)
        dong.update(goc_tu=goc_tu, goc_kiem=goc_kiem)
        # mo hinh CU (tung chan rieng, giu N bar, khong luat ngay) - de so sanh
        dong["goc_kiem_rieng_cu"] = [danh_gia(sp, df_kiem, khung, cp=cp) for sp in specs]
        tot_specs = specs
        ts, _ = tham_so_nhom(specs)
        if toi_uu_bat and ts:
            ts_tot, kq_tu, so_chay, ax = toi_uu_nhom(specs, df_tu, khung, lenh_min_tu, cp=cp,
                                                     tai_khoan=tk)
            tot_specs = ap_tham_so_nhom(specs, ax, ts_tot)
            dong.update(tham_so_goc=ts, tham_so_tot=ts_tot, so_lan_chay=so_chay,
                        tot_tu=kq_tu)
        kiem = danh_gia_nhom(tot_specs, df_kiem, khung, cp=cp, tai_khoan=tk)
        tu = dong.get("tot_tu", goc_tu)
        dong["tot_kiem"] = kiem
        dong["tieu_chi_25_09"] = nhan_25_09(kiem)
        if ro:
            dong["canh_bao_mt5"] = CANH_BAO_MT5_RO
        nam_tu = len(df_tu) / BAR_NAM.get(khung, 260)
        nam_kiem = len(df_kiem) / BAR_NAM.get(khung, 260)
        dong["t_tu"] = round(tu["sharpe"] * math.sqrt(nam_tu), 2)
        dong["t_kiem"] = round(kiem["sharpe"] * math.sqrt(nam_kiem), 2)
        it = []
        if tu["so_lenh"] < lenh_min_tu:
            it.append(f"toi_uu {tu['so_lenh']}<{lenh_min_tu}")
        if kiem["so_lenh"] < lenh_min:
            it.append(f"kiem {kiem['so_lenh']}<{lenh_min}")
        if it:
            dong["it_lenh"] = it
        dat_cu = bool(dong["t_tu"] >= t_tu and dong["t_kiem"] >= t_kiem
                      and not it and not loi_cp)
        if ro:
            # Sharpe/t KHONG du cho luoi (placebo duong 10/10): them cong luoi; ro
            # hedge qua CUNG cong (muc 9). Nguong cu van ap (khong noi) - cong chi SIET.
            bo_qua = None
            try:
                pl = placebo_cung_cau_truc(tot_specs, df_kiem, khung, cp, tk, n=n_placebo)
            except NotImplementedError as e:
                pl, bo_qua = [], str(e)
            cl = cong_luoi(tu, kiem, pl, p_placebo, nam_kiem=nam_kiem,
                           p_chay_nam=p_chay_nam, placebo_bo_qua=bo_qua)
            cl["dat_nguong_t_cu"] = dat_cu
            dong["cong_luoi"] = cl
            dong["giu_lai"] = bool(dat_cu and cl["dat"])
        else:
            dong["giu_lai"] = dat_cu
    except Exception as e:                           # noqa: BLE001
        if type(e).__name__ == "KhungThieuGio":
            dong["khong_hop_khung"] = str(e)[:80]
        else:
            dong["loi"] = f"{type(e).__name__}: {e}"
        dong["giu_lai"] = False
    return dong


def main(argv=None) -> int:
    global DIEM
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mau", default=str(LAB / "mau_thu"))
    ap.add_argument("--csv", help="chuỗi giá thật (time,open,high,low,close)")
    ap.add_argument("--khung", default="H1", choices=sorted(BAR_NAM))
    ap.add_argument("--n", type=int, default=24 * 400, help="số bar giả lập")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--gia-lap-duong", action="store_true",
                    help="giả lập dựng bar từ đường giá thật (placebo cho lệnh trong bar)")
    ap.add_argument("--khong-toi-uu", action="store_true")
    ap.add_argument("--lenh-toi-thieu", type=int, default=20)
    ap.add_argument("--t-tu", type=float, default=2.0)
    ap.add_argument("--t-kiem", type=float, default=1.5)
    ap.add_argument("--json", help="ghi kết quả ra file này")
    ap.add_argument("--ma", default="EURUSD", help="mã để lấy chi phí thật")
    ap.add_argument("--khong-phi", action="store_true",
                    help="KHÔNG tính phí (chỉ để so với số cũ trước 10/10 khuya)")
    ap.add_argument("--von", type=float, default=TAI_KHOAN_MAC_DINH["von"],
                    help="vốn KHAI BÁO (USD) cho hệ lưới/martingale")
    ap.add_argument("--don-bay", type=float, default=TAI_KHOAN_MAC_DINH["don_bay"])
    ap.add_argument("--stop-out", type=float, default=TAI_KHOAN_MAC_DINH["stop_out"],
                    help="mức ký quỹ stop-out (0.5 = 50%%)")
    ap.add_argument("--lot-max", type=float, default=TAI_KHOAN_MAC_DINH["lot_max"],
                    help="SYMBOL_VOLUME_MAX (lot/lệnh) - sàn từ chối lệnh lớn hơn; 0 = không giới hạn")
    ap.add_argument("--lot-tong-max", type=float, default=0.0,
                    help="SYMBOL_VOLUME_LIMIT (tổng lot cùng chiều); 0 = không giới hạn")
    ap.add_argument("--n-placebo", type=int, default=99,
                    help="số placebo cùng cấu trúc cho cổng lưới")
    ap.add_argument("--p-placebo", type=float, default=0.05)
    ap.add_argument("--p-chay-nam", type=float, default=0.05,
                    help="loại hệ lưới khi P(stop-out trong 1 năm) ước từ placebo/thật > mức này")
    ap.add_argument("--loc-file", default="*.mq5", help="mẫu tên file EA (vd '*Breakout5*')")
    ap.add_argument("--diem", type=float, default=DIEM,
                    help="_Point của mã (mặc định 1e-5 = EURUSD 5 số, GIẢ ĐỊNH; JPY 1e-3)")
    ap.add_argument("--phi-cu", action="store_true",
                    help="mô hình phí TRƯỚC P3 (swap liên tục, tỉ lệ hôm nay cho mọi năm) - chỉ để so")
    ap.add_argument("--he-so-spread", type=float, default=1.0,
                    help="nhân spread đo được (XM micro) - ĐỘ NHẠY, vd 0.33 ~ tài khoản "
                         "ECN (chưa cộng hoa hồng). Mặc định 1 = phí thật hiện có")
    a = ap.parse_args(argv)
    DIEM = float(a.diem)

    if a.csv:
        df = doc_csv(Path(a.csv))
    elif a.gia_lap_duong:
        df = du_lieu_gia_lap_duong(a.n, a.seed, a.khung)
    else:
        df = du_lieu_gia_lap(a.n, a.seed, a.khung)
    tong, da_thay = [], set()
    tk = {"von": a.von, "don_bay": a.don_bay, "stop_out": a.stop_out,
          "lot_max": a.lot_max or None, "lot_tong_max": a.lot_tong_max or None}
    cp = mo_hinh_chi_phi(df, a.ma, a.khong_phi, a.phi_cu)
    if not a.khong_phi and a.he_so_spread != 1.0:
        cp = cp.bien_the(spread=cp.spread_frac_chung * a.he_so_spread)
    for f in sorted(Path(a.mau).glob(a.loc_file)):
        tong.extend(chay_mot_file(f, df, a.khung, not a.khong_toi_uu, a.lenh_toi_thieu,
                                  a.t_tu, a.t_kiem, da_thay, cp=cp, tai_khoan=tk,
                                  n_placebo=a.n_placebo, p_placebo=a.p_placebo,
                                  p_chay_nam=a.p_chay_nam))

    for x in tong:
        x.setdefault("mo_hinh_phi", "khong_phi" if a.khong_phi else cp.phien_ban())
    loi = [x for x in tong if "loi" in x]
    giu = [x for x in tong if x.get("giu_lai")]
    trung = [x for x in tong if x.get("trung")]
    lech = [x for x in tong if x.get("khong_hop_khung")]
    cat = int(len(df) * 0.7)
    print(f"Dữ liệu: {'CSV ' + a.csv if a.csv else 'giả lập'} {a.khung}, {len(df)} bar "
          f"(tối ưu 70% đầu, kiểm 30% sau); đủ lệnh = ≥"
          f"{lenh_min_phan_tu(a.lenh_toi_thieu, cat, len(df) - cat)} lệnh phần tối ưu "
          f"VÀ ≥{a.lenh_toi_thieu} lệnh phần kiểm")
    uoc = MP._diem_tu_gia(float(np.nanmedian(df["close"])))
    print(f"_Point giả định = {DIEM:g} (--diem)" + (
        "" if abs(uoc - DIEM) < 1e-15 else
        f"  CẢNH BÁO: mức giá gợi ý _Point {uoc:g} - SL/TP theo điểm có thể sai"))
    print(f"Chi phí {a.ma}: " + ("KHÔNG PHÍ (--khong-phi)" if a.khong_phi else
          f"spread {cp.spread_frac_chung * 1e4:.2f} bps/chiều, trượt "
          f"{cp.truot_gia_frac * 1e4:.2f} bps, qua đêm mua {cp.phi_nam_mua:+.4f}/bán "
          f"{cp.phi_nam_ban:+.4f} /năm ({cp.do_tin})"
          + (f" [ĐỘ NHẠY: spread x{a.he_so_spread:g}]" if a.he_so_spread != 1.0 else "")
          + f" | mô hình phí {cp.phien_ban()}"))
    if not a.khong_phi:
        for c_ in cp.canh_bao:
            if c_.startswith("P3 "):
                print(f"  {c_}")
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
              + ("" if not x.get("kiem_cu_phap") else "  [không qua kiểm cú pháp]")
              + ("" if not x.get("it_lenh") else f"  [ít lệnh: {', '.join(x['it_lenh'])}]")
              + ("" if not x.get("diem_gia_dinh") else f"  [SL/TP theo _Point={x['diem_gia_dinh']:g}]")
              + ("" if not x.get("trong_bar") else
                 f"  [lệnh dừng trong bar; tick đầu gốc sh="
                 f"{x['goc_kiem_tick_dau']['sharpe']:+.2f}/{x['goc_kiem_tick_dau']['so_lenh']}l]"))
        if x.get("tieu_chi_25_09"):
            n25 = x["tieu_chi_25_09"]
            print(f"        nhãn: đạt tiêu chí 25/09? {'CÓ' if n25['dat'] else 'KHÔNG'} (cần: lãi kiểm sau phí, "
                  f"maxDD < {DD_25_09:.0f}%, không cháy; đo: maxDD {n25['maxdd_pct']:.1f}% [{n25['nguon_dd']}])"
                  + ("" if n25["dat"] else f" [{'; '.join(n25['ly_do'])}]")
                  + " - chỉ là NHÃN, không đổi GIỮ/BỎ")
        if x.get("canh_bao_mt5"):
            print(f"        {x['canh_bao_mt5']}")
        if x.get("cong_luoi"):
            cl = x["cong_luoi"]
            tkk = x["tot_kiem"].get("tai_khoan") or {}
            kb = x["tai_khoan_khai_bao"]
            if cl.get("placebo_bo_qua"):
                pl_txt = f"placebo BỎ QUA ({cl['placebo_bo_qua']})"
            else:
                pl_txt = (f"vs placebo TB {cl['placebo_tb']:+.3f} q95 {cl['placebo_q95']:+.3f} "
                          f"(dương {cl['placebo_duong']:.0%}, sống {cl['placebo_song_sot']:.0%}) "
                          f"p={cl['p']:.3f}")
            print(f"        CỔNG {'LƯỚI' if x.get('loai_ro') == 'luoi' else 'RỔ HEDGE'} "
                  f"({'ĐẠT' if cl['dat'] else 'KHÔNG ĐẠT'}): tài khoản "
                  f"{kb['von']:g} USD 1:{kb['don_bay']:g} stop-out {kb['stop_out']:.0%}"
                  f" lot max {kb.get('lot_max') or '∞'} → "
                  f"stop-out tối ưu/kiểm {(x.get('tot_tu') or x['goc_tu']).get('tai_khoan', {}).get('so_stop_out')}"
                  f"/{tkk.get('so_stop_out')}, mức KQ min kiểm {tkk.get('muc_ky_quy_min')}, từ chối "
                  f"KQ/lot {tkk.get('tu_choi_ky_quy')}/{tkk.get('tu_choi_lot_max')}; "
                  f"loi_log kiểm {cl['that']:+.3f} {pl_txt}"
                  + ("" if not cl.get("chay_nam") else
                     f"; P(stop-out/năm) {cl['chay_nam']['p_nam']:.1%} (placebo "
                     f"{cl['chay_nam']['placebo']['so_stop_out']} lần chạy cháy/"
                     f"{cl['chay_nam']['placebo']['nam_phoi_nhiem']:.0f} năm-mẫu)")
                  + ("" if cl["dat"] else f"  [{'; '.join(cl['ly_do'])}]"))
        if x.get("nhom"):
            print("        từng chân (kiểm, sau tối ưu): " + "  ".join(
                f"chieu={c['chieu']:+d} sh={c['sharpe']:+.2f}/{c['so_lenh']}l"
                + (f" ({c['so_hedge']} hedge)" if c.get("so_hedge") else "")
                for c in tk["chan"])
                + "  | mô hình cũ riêng (giu, không luật ngày): " + "  ".join(
                f"sh={c['sharpe']:+.2f}/{c['so_lenh']}l" for c in x["goc_kiem_rieng_cu"]))
    if a.json:
        Path(a.json).write_text(json.dumps(tong, ensure_ascii=False, indent=1,
                                           default=str), encoding="utf-8")
        print(f"Đã ghi {a.json}")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
