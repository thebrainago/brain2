# -*- coding: utf-8 -*-
"""dich_nguoc_tin_hieu.py - Tái tạo đặc trưng + xếp hang_cho dich_boc từ lịch sử lệnh.

Luồng:
  trades.jsonl (chuẩn) + H1 parquet → bảng đặc trưng tại vào/ra
  → lọc martingale/grid/không-SL (cờ hoặc từ chối)
  → prompt gọn (text/bảng) → hang_cho_llm loai_viec=dich_boc (cùng schema NGHI)

Không gọi API; dùng BRAIN_LLM_PROVIDER=hang_cho / xep_hang trực tiếp.

Hai track (30/10/2026):
  - thuong: he KHONG martingale/grid → dich_boc loai he/co_che
  - dca: he martingale/grid/DCA → KHONG loai; trich module recovery → dich_boc loai=dca_go_lenh
Pass rule ket qua test van: loi sau phi, DD<=80%, >=10%/nam.

"""
from __future__ import annotations

import json
import re
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import duong_dan as DD
from nhan import thu_thap_tin_hieu_cong_khai as TT

# ----- ngưỡng lọc (khớp chỉ thị DD <= 80%, tránh grid/martingale) -----
TY_LE_SL_TOI_THIEU = 0.55          # < 55% lệnh có SL → cờ khong_sl
HE_SO_MARTINGALE = 1.6             # lot sau / lot trước >= 1.6 trong chuỗi lỗ → martingale
CUA_SO_GRID_GIAY = 6 * 3600        # cùng symbol+chiều trong 6h, >= 3 lệnh → nghi grid
SO_LENH_GRID = 3
LOT_LECH_CV = 0.45                 # CV lot cao + nhiều lệnh chồng → nghi grid


HE_THONG_DICH = (
    "Ban la ky su dich chien luoc giao dich. Doc HO SO DICH NGUOC (bang dac trung tu "
    "lich su lenh cong khai + trang thai chi bao tai thoi diem vao/ra) va tra ve DUY NHAT "
    "mot JSON dung schema dich_boc (nhu cau_llm.MAU_BOC), khong giai thich. Khong bia: "
    "phan nao khong chac thi de trong va ghi vao 'chua_dich'. Neu he la luoi/martingale/"
    "khong SL: dien 'luoi' (spec=[] python=\"\"), ghi ro vao chua_dich; KHONG bia tin hieu."
)


def _iso_to_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    t = str(s).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(t)
    except ValueError:
        return None


def _phien(gio_utc: int) -> str:
    # Phiên FX粗略: Asia 0-7, London 7-15, NY 13-21 (UTC)
    if 0 <= gio_utc < 7:
        return "asia"
    if 7 <= gio_utc < 13:
        return "london"
    if 13 <= gio_utc < 21:
        return "ny"
    return "late"


def phat_hien_martingale_grid(trades: list[dict]) -> dict:
    """Cờ hành vi nguy hiểm từ pattern lot / chồng lệnh."""
    co = {"martingale": False, "grid": False, "khong_sl": False,
          "chi_tiet": [], "ty_le_co_sl": 0.0, "cv_lot": 0.0}
    if not trades:
        return co
    co_sl = sum(1 for t in trades if t.get("sl") is not None)
    co["ty_le_co_sl"] = round(co_sl / len(trades), 3)
    if co["ty_le_co_sl"] < TY_LE_SL_TOI_THIEU:
        co["khong_sl"] = True
        co["chi_tiet"].append("ty_le_sl=%.2f < %.2f" % (co["ty_le_co_sl"], TY_LE_SL_TOI_THIEU))

    lots = [float(t["lot"]) for t in trades if t.get("lot")]
    if len(lots) >= 5 and statistics.mean(lots) > 0:
        co["cv_lot"] = round(statistics.pstdev(lots) / statistics.mean(lots), 3)

    # Martingale: sau lệnh lỗ, lot tăng mạnh cùng symbol
    theo_sym: dict[str, list] = defaultdict(list)
    for t in sorted(trades, key=lambda x: x.get("luc_vao") or ""):
        theo_sym[t["symbol"]].append(t)
    for sym, ds in theo_sym.items():
        for i in range(1, len(ds)):
            truoc, sau = ds[i - 1], ds[i]
            loi = truoc.get("loi")
            if loi is None or loi >= 0:
                continue
            l0, l1 = float(truoc["lot"]), float(sau["lot"])
            if l0 > 0 and l1 / l0 >= HE_SO_MARTINGALE and sau.get("chieu") == truoc.get("chieu"):
                co["martingale"] = True
                co["chi_tiet"].append(
                    "martingale %s lot %.3f->%.3f sau lo" % (sym, l0, l1))
                break

    # Grid: nhiều lệnh cùng symbol+chiều mở trong cửa sổ ngắn
    for sym, ds in theo_sym.items():
        for ch in (1, -1):
            mo = []
            for t in ds:
                if t.get("chieu") != ch:
                    continue
                dt = _iso_to_dt(t.get("luc_vao"))
                if dt:
                    mo.append(dt.timestamp())
            mo.sort()
            for i in range(len(mo)):
                j = i
                while j < len(mo) and mo[j] - mo[i] <= CUA_SO_GRID_GIAY:
                    j += 1
                if j - i >= SO_LENH_GRID:
                    co["grid"] = True
                    co["chi_tiet"].append(
                        "grid %s chieu=%s %d lenh/%dh" % (sym, ch, j - i, CUA_SO_GRID_GIAY // 3600))
                    break
            if co["grid"]:
                break
        if co["grid"]:
            break

    if co["cv_lot"] >= LOT_LECH_CV and not co["martingale"] and len(trades) >= 30:
        # CV lot cao thường đi kèm grid/DCA
        co["chi_tiet"].append("cv_lot=%.2f cao" % co["cv_lot"])
    return co


def loc_he(trades: list[dict], *, tu_choi_nguy_hiem: bool = True) -> dict:
    """Trả quyết định: chap_nhan | canh_bao | tu_choi + cờ.

    Lưu ý (t23u): martingale/grid KHÔNG bị loại khỏi pipeline — dùng track DCA.
    `tu_choi_nguy_hiem=True` chỉ còn ý nghĩa cho track thuong (bỏ qua, chuyển DCA).
    """
    co = phat_hien_martingale_grid(trades)
    nguy = co["martingale"] or co["grid"] or co["khong_sl"]
    if nguy and tu_choi_nguy_hiem:
        qd = "tu_choi"   # track thuong bỏ; caller chuyển sang DCA
    elif nguy:
        qd = "canh_bao"
    else:
        qd = "chap_nhan"
    return {"quyet_dinh": qd, **co}


def xep_hang_he(trades: list[dict], *, meta: dict | None = None) -> dict:
    """Lọc tuổi / DD / số lệnh / lãi ước lượng trước khi dich.

    meta có thể có: tuoi_ngay, dd_pct, growth_pct, real (bool).
    Ngưỡng: tuoi >= 365n (hoặc suy từ lệnh), DD <= 80% (ưu tiên <30%),
    so_lenh >= 30, loi ròng > 0 sau commission+swap nếu có.
    """
    meta = meta or {}
    n = len(trades)
    loi = sum(float(t.get("loi") or 0) for t in trades)
    phi = sum(float(t.get("commission") or 0) + float(t.get("swap") or 0) for t in trades)
    loi_sau_phi = loi  # FXBlue Net profit thường đã trừ; cộng thêm nếu commission tách
    # tuổi từ lệnh
    lucs = sorted(t.get("luc_vao") for t in trades if t.get("luc_vao"))
    tuoi_ngay = meta.get("tuoi_ngay")
    if tuoi_ngay is None and len(lucs) >= 2:
        from datetime import datetime
        def _p(s):
            return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        try:
            tuoi_ngay = (_p(lucs[-1]) - _p(lucs[0])).days
        except Exception:
            tuoi_ngay = None
    dd = meta.get("dd_pct")
    ly_do = []
    ok = True
    if n < 30:
        ok = False; ly_do.append("so_lenh=%d<30" % n)
    if tuoi_ngay is not None and tuoi_ngay < 365:
        ok = False; ly_do.append("tuoi_ngay=%s<365" % tuoi_ngay)
    if dd is not None and dd > 80:
        ok = False; ly_do.append("dd=%.1f>80" % dd)
    if loi_sau_phi <= 0 and n >= 10:
        ok = False; ly_do.append("loi_sau_phi=%.2f<=0" % loi_sau_phi)
    uu_tien = 0
    if dd is not None and dd < 30:
        uu_tien += 2
    elif dd is not None and dd < 50:
        uu_tien += 1
    if tuoi_ngay and tuoi_ngay >= 365:
        uu_tien += 1
    if n >= 100:
        uu_tien += 1
    return {
        "ok": ok, "ly_do": ly_do, "uu_tien": uu_tien,
        "so_lenh": n, "tuoi_ngay": tuoi_ngay, "dd_pct": dd,
        "loi_sau_phi": round(loi_sau_phi, 2), "phi": round(phi, 2),
    }


def doc_nen_h1(symbol: str, kho: Path | None = None) -> pd.DataFrame | None:
    """Đọc {symbol}_H1.parquet từ BRAIN_DATA / data lab."""
    kho = Path(kho) if kho else DD.kho_gia()
    # thử tên chuẩn + biến thể
    ung = [kho / ("%s_H1.parquet" % symbol),
           kho / ("%s_H1.parquet" % symbol.upper()),
           kho / ("%s#_H1.parquet" % symbol)]
    for p in ung:
        if p.exists():
            df = pd.read_parquet(p)
            if "time" in df.columns:
                df = df.copy()
                df["time"] = pd.to_datetime(df["time"], utc=True)
                df = df.set_index("time").sort_index()
            return df
    return None


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).rolling(n, min_periods=n).mean()
    down = (-d.clip(upper=0)).rolling(n, min_periods=n).mean()
    rs = up / down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean()


def trang_thai_chi_bao(df: pd.DataFrame, luc: datetime) -> dict:
    """Trạng thái chỉ báo tại nến H1 đóng gần nhất trước/tại luc (không nhìn trước)."""
    if df is None or df.empty or luc is None:
        return {}
    if luc.tzinfo is None:
        luc = luc.replace(tzinfo=timezone.utc)
    # nến pad
    idx = df.index.get_indexer([pd.Timestamp(luc)], method="pad")
    i = int(idx[0]) if len(idx) else -1
    if i < 0:
        return {}
    # cần đủ lịch sử
    if i < 55:
        return {"nen_idx": i, "thieu_lich_su": True}
    win = df.iloc[: i + 1]
    close = win["close"]
    sma20 = float(_sma(close, 20).iloc[-1])
    sma50 = float(_sma(close, 50).iloc[-1])
    rsi = float(_rsi(close, 14).iloc[-1])
    atr = float(_atr(win, 14).iloc[-1])
    gia = float(close.iloc[-1])
    hi20 = float(win["high"].iloc[-20:].max())
    lo20 = float(win["low"].iloc[-20:].min())
    trend = "len" if gia > sma50 and sma20 > sma50 else ("xuong" if gia < sma50 and sma20 < sma50 else "ngang")
    breakout = None
    if gia >= hi20:
        breakout = "pha_cao_20"
    elif gia <= lo20:
        breakout = "pha_thap_20"
    return {
        "nen": str(win.index[-1]),
        "gia": round(gia, 6),
        "sma20": round(sma20, 6),
        "sma50": round(sma50, 6),
        "rsi14": round(rsi, 2) if not math.isnan(rsi) else None,
        "atr14": round(atr, 6) if not math.isnan(atr) else None,
        "atr_pct": round(100 * atr / gia, 4) if atr and gia else None,
        "trend": trend,
        "breakout": breakout,
        "gia_vs_sma20_pct": round(100 * (gia - sma20) / gia, 4) if gia else None,
    }


def tai_tao_dac_trung(trades: list[dict], *, toi_da: int = 80,
                      kho_gia: Path | None = None) -> list[dict]:
    """Căn mỗi lệnh với H1 + đặc trưng vào/ra. Giới hạn mẫu để prompt gọn."""
    # ưu tiên lệnh có SL, đa dạng symbol
    ds = list(trades)
    ds.sort(key=lambda t: (0 if t.get("sl") is not None else 1, t.get("luc_vao") or ""))
    # lấy mẫu đều theo thời gian nếu quá dài
    if len(ds) > toi_da:
        buoc = max(1, len(ds) // toi_da)
        ds = ds[::buoc][:toi_da]

    cache: dict[str, pd.DataFrame | None] = {}
    ra = []
    for t in ds:
        sym = t["symbol"]
        # chuẩn hóa symbol broker suffix
        sym_chuan = re_chuan_symbol(sym)
        if sym_chuan not in cache:
            cache[sym_chuan] = doc_nen_h1(sym_chuan, kho_gia)
        df = cache[sym_chuan]
        lv = _iso_to_dt(t.get("luc_vao"))
        lr = _iso_to_dt(t.get("luc_ra"))
        gio = lv.hour if lv else None
        hang = {
            "ticket": t.get("ticket"),
            "symbol": sym,
            "symbol_chuan": sym_chuan,
            "chieu": t.get("chieu"),
            "lot": t.get("lot"),
            "luc_vao": t.get("luc_vao"),
            "luc_ra": t.get("luc_ra"),
            "giu_gio": t.get("giu_gio"),
            "sl": t.get("sl"),
            "tp": t.get("tp"),
            "loi": t.get("loi"),
            "gio_utc": gio,
            "phien": _phien(gio) if gio is not None else None,
            "thu": lv.weekday() if lv else None,
            "vao": trang_thai_chi_bao(df, lv) if df is not None else {"thieu_gia": True},
            "ra": trang_thai_chi_bao(df, lr) if (df is not None and lr) else {},
        }
        # khoảng SL/TP theo ATR nếu có
        atr = (hang["vao"] or {}).get("atr14")
        gia = t.get("gia_vao")
        if atr and gia and t.get("sl") is not None:
            hang["sl_atr"] = round(abs(float(gia) - float(t["sl"])) / atr, 2)
        if atr and gia and t.get("tp") is not None:
            hang["tp_atr"] = round(abs(float(t["tp"]) - float(gia)) / atr, 2)
        ra.append(hang)
    return ra


def re_chuan_symbol(tho: str) -> str:
    s = str(tho or "").strip()
    s = s.split(".")[0].split("#")[0]
    m = re.fullmatch(r"([A-Z0-9]{3,})([a-z]{1,5})", s)
    if m:
        s = m.group(1)
    u = s.upper()
    if u.startswith(("GOLD", "XAUUSD")):
        return "XAUUSD"
    if u.startswith(("SILVER", "XAGUSD")):
        return "XAGUSD"
    return u


def tong_hop_ho_so(trades: list[dict], dac_trung: list[dict], loc: dict) -> dict:
    """Hồ sơ gọn cho LLM: thống kê + mẫu bảng."""
    sym = Counter(t["symbol"] for t in trades)
    chieu = Counter(t["chieu"] for t in trades)
    phien = Counter(d.get("phien") for d in dac_trung if d.get("phien"))
    trend = Counter((d.get("vao") or {}).get("trend") for d in dac_trung if (d.get("vao") or {}).get("trend"))
    giu = [t["giu_gio"] for t in trades if t.get("giu_gio") is not None]
    rsi_vao = [(d.get("vao") or {}).get("rsi14") for d in dac_trung
               if (d.get("vao") or {}).get("rsi14") is not None]
    return {
        "so_lenh": len(trades),
        "symbols": sym.most_common(8),
        "ty_le_buy": round(chieu.get(1, 0) / max(1, sum(chieu.values())), 3),
        "phien": phien.most_common(),
        "trend_vao": trend.most_common(),
        "giu_gio_tb": round(statistics.mean(giu), 2) if giu else None,
        "giu_gio_median": round(statistics.median(giu), 2) if giu else None,
        "rsi_vao_tb": round(statistics.mean(rsi_vao), 1) if rsi_vao else None,
        "loc": {k: loc[k] for k in ("quyet_dinh", "martingale", "grid", "khong_sl",
                                     "ty_le_co_sl", "cv_lot", "chi_tiet")},
        "mau_lenh": dac_trung[:25],  # gọn
    }


def _bang_text(ho_so: dict) -> str:
    """Prompt gọn: text/bảng, không HTML."""
    lines = []
    lines.append("## Thong ke")
    lines.append("so_lenh=%s ty_buy=%s giu_gio_tb=%s giu_gio_med=%s rsi_vao_tb=%s"
                 % (ho_so["so_lenh"], ho_so["ty_le_buy"], ho_so["giu_gio_tb"],
                    ho_so["giu_gio_median"], ho_so["rsi_vao_tb"]))
    lines.append("symbols=" + ", ".join("%s:%d" % (a, b) for a, b in ho_so["symbols"]))
    lines.append("phien=" + ", ".join("%s:%d" % (a, b) for a, b in ho_so["phien"]))
    lines.append("trend_vao=" + ", ".join("%s:%d" % (a, b) for a, b in ho_so["trend_vao"]))
    loc = ho_so["loc"]
    lines.append("loc: qd=%s martingale=%s grid=%s khong_sl=%s ty_sl=%s cv_lot=%s"
                 % (loc["quyet_dinh"], loc["martingale"], loc["grid"], loc["khong_sl"],
                    loc["ty_le_co_sl"], loc["cv_lot"]))
    if loc.get("chi_tiet"):
        lines.append("loc_chi_tiet: " + " | ".join(loc["chi_tiet"][:6]))
    lines.append("")
    lines.append("## Mau lenh (toi da 25)")
    lines.append("sym|chieu|lot|gio|phien|giu_h|sl_atr|tp_atr|loi|trend|rsi|breakout")
    for d in ho_so["mau_lenh"]:
        v = d.get("vao") or {}
        lines.append("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
            d.get("symbol_chuan") or d.get("symbol"),
            d.get("chieu"), d.get("lot"), d.get("gio_utc"), d.get("phien"),
            d.get("giu_gio"), d.get("sl_atr"), d.get("tp_atr"),
            round(d["loi"], 2) if isinstance(d.get("loi"), (int, float)) else d.get("loi"),
            v.get("trend"), v.get("rsi14"), v.get("breakout"),
        ))
    return "\n".join(lines)


def tao_nhac_dich_boc(ho_so: dict, *, nguon: str, he_id: str, url: str = "") -> str:
    """Nhắc dich_boc — cùng schema MAU_BOC, nguồn là hồ sơ dịch ngược (không phải mã)."""
    bang = _bang_text(ho_so)
    return (
        "Tra JSON dang:\n"
        '{"loai": "he_hoan_thien|co_che|tien_ich|mo_ta",'
        ' "spec": [ {"ten": str, "chieu": 1|-1, "vao": [{"trai": {...}, "phep": ">"|"<"|">="|"<="|"cheo_len"|"cheo_xuong", "phai": {...}}]} ],'
        ' "python": "def tin_hieu(df):\\n    ...",'
        ' "luoi": {}, "co_che": [], "quan_tri": {}, "tham_so": {}, "chua_dich": []}\n'
        "Uu tien 'spec'. Chi bao co san: gia, sma, ema, rsi, atr, macd, bollinger, donchian, "
        "stochastic, cci, adx, gio, ngay_trong_tuan. Neu martingale/grid/khong SL: "
        "dien luoi, spec=[], python=\"\", ghi chua_dich.\n"
        "NGUON dich nguoc: %s/%s %s\n"
        "HO SO:\n```\n%s\n```"
    ) % (nguon, he_id, url or "", bang)



def _danh_dau_superseded(HCL, *, nguon: str, he_id: str, track: str, id_moi: str) -> list[str]:
    """Doi cho/ cu cung nguon+he_id+track → superseded/ (tranh worker lam lai)."""
    da = []
    thu = HCL.CHO / "superseded"
    for p in list(HCL.CHO.glob("*.json")):
        if p.stem == id_moi:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        them = d.get("them") or {}
        if them.get("nguon") == nguon and them.get("he_id") == he_id and them.get("track") == track:
            thu.mkdir(parents=True, exist_ok=True)
            dest = thu / p.name
            try:
                d["superseded_boi"] = id_moi
                d["superseded_luc"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S")
                dest.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                p.unlink()
                da.append(p.stem)
            except OSError:
                pass
    return da


def xep_dich_boc(nguon: str, he_id: str, trades: list[dict] | None = None, *,
                 tu_choi_nguy_hiem: bool = False, kho_gia: Path | None = None,
                 url: str = "", track: str | None = None) -> dict:
    """Tái tạo đặc trưng + xếp hang_cho dich_boc.

    track=None → tự chọn: nguy hiểm → "dca", ngược lại "thuong".
    track="thuong": dich entry/spec thường (có thể bỏ nếu tu_choi).
    track="dca": luôn xếp module DCA (loai=dca_go_lenh), không loại martingale.
    """
    from nhan import hang_cho_llm as HCL
    from nhan import phan_tich_dca as DCA

    if trades is None:
        trades = TT.doc_he_da_luu(nguon, he_id)
    if not trades:
        return {"trang_thai": "LOI", "ghi_chu": "khong co lenh"}

    loc = loc_he(trades, tu_choi_nguy_hiem=False)  # luôn lấy cờ, không loại ở đây
    nguy = loc["martingale"] or loc["grid"]
    if track is None:
        track = "dca" if nguy else "thuong"

    thu = TT.thu_muc_goc() / nguon / he_id
    thu.mkdir(parents=True, exist_ok=True)

    if track == "dca":
        ho_dca = DCA.thong_ke_dca(trades)
        (thu / "ho_so_dca.json").write_text(
            json.dumps(ho_dca, ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8")
        if ho_dca.get("do_tin") == "LOAI" or ho_dca.get("so_multi", 0) < 1:
            return {
                "trang_thai": "BO_QUA",
                "ghi_chu": "ho_so_dca do_tin=%s so_multi=%s sanity=%s" % (
                    ho_dca.get("do_tin"), ho_dca.get("so_multi"), ho_dca.get("sanity_ly_do")),
                "track": "dca", "loc": loc,
                "ho_so_path": str(thu / "ho_so_dca.json"),
                "so_lenh": len(trades), "so_multi": ho_dca.get("so_multi"),
                "do_tin": ho_dca.get("do_tin"),
            }
        nhac = DCA.tao_nhac_dca(ho_dca, nguon=nguon, he_id=he_id, url=url)
        kq = HCL.xep_hang(
            "dich_boc", DCA.HE_THONG_DCA, nhac,
            tru="dich_nguoc_dca",
            ep_json=True,
            them={"nguon": nguon, "he_id": he_id, "loc": loc["quyet_dinh"],
                  "loai": "dca_go_lenh", "track": "dca",
                  "do_tin": ho_dca.get("do_tin"),
                  "pip_fix": "xm_per_instrument_v2"},
        )
        if kq.get("id"):
            kq["superseded"] = _danh_dau_superseded(
                HCL, nguon=nguon, he_id=he_id, track="dca", id_moi=kq["id"])
        kq["track"] = "dca"
        kq["loc"] = loc
        kq["ho_so_path"] = str(thu / "ho_so_dca.json")
        kq["so_lenh"] = len(trades)
        kq["so_multi"] = ho_dca.get("so_multi")
        kq["do_tin"] = ho_dca.get("do_tin")
        return kq

    # track thuong
    if tu_choi_nguy_hiem and nguy:
        return {"trang_thai": "CHUYEN_DCA", "loc": loc, "he_id": he_id, "nguon": nguon,
                "track": "thuong"}

    dac = tai_tao_dac_trung(trades, kho_gia=kho_gia)
    ho = tong_hop_ho_so(trades, dac, loc)
    (thu / "ho_so_dich_nguoc.json").write_text(
        json.dumps(ho, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    nhac = tao_nhac_dich_boc(ho, nguon=nguon, he_id=he_id, url=url)
    kq = HCL.xep_hang(
        "dich_boc", HE_THONG_DICH, nhac,
        tru="dich_nguoc_tin_hieu",
        ep_json=True,
        them={"nguon": nguon, "he_id": he_id, "loc": loc["quyet_dinh"], "track": "thuong"},
    )
    kq["track"] = "thuong"
    kq["loc"] = loc
    kq["ho_so_path"] = str(thu / "ho_so_dich_nguoc.json")
    kq["so_lenh"] = len(trades)
    kq["so_mau"] = len(dac)
    return kq


def chay_ong(
    users: list[str] | None = None,
    *,
    nghi: float = 4.0,
    tu_choi_nguy_hiem: bool = False,
    kho_gia: Path | None = None,
    in_ra=print,
    ca_hai_track: bool = True,
) -> dict:
    """Thu thập FXBlue → lọc xếp hạng → dual-track dich_boc (thuong + dca)."""
    ket_thu = TT.thu_thap_fxblue(users, nghi=nghi, in_ra=in_ra)
    ra = {"thu_thap": ket_thu, "dich": [], "bo_qua": []}
    for h in ket_thu.get("he") or []:
        he_id = h["he_id"]
        url = TT.FXBLUE_CSV.format(user=he_id)
        trades = TT.doc_he_da_luu("fxblue", he_id)
        xh = xep_hang_he(trades)
        if not xh["ok"]:
            # vẫn cho DCA nếu có multi-basket; track thuong thì bỏ
            loc = loc_he(trades, tu_choi_nguy_hiem=False)
            if not (loc["martingale"] or loc["grid"]):
                ra["bo_qua"].append({"he_id": he_id, "ly_do": xh["ly_do"], "xep_hang": xh})
                in_ra("[bo_qua] %s %s" % (he_id, xh["ly_do"]))
                continue
        loc = loc_he(trades, tu_choi_nguy_hiem=False)
        tracks = []
        if loc["martingale"] or loc["grid"]:
            tracks.append("dca")
            if ca_hai_track:
                # entry đầu vẫn có thể hữu ích nếu muốn — chỉ DCA theo chỉ thị
                pass
        else:
            tracks.append("thuong")
        for tr in tracks:
            kq = xep_dich_boc("fxblue", he_id, trades, tu_choi_nguy_hiem=tu_choi_nguy_hiem,
                              kho_gia=kho_gia, url=url, track=tr)
            ra["dich"].append({"he_id": he_id, "track": tr,
                               **{k: kq.get(k) for k in
                                  ("trang_thai", "id", "ghi_chu", "loc", "so_lenh",
                                   "so_mau", "so_multi", "ho_so_path")}})
            in_ra("[dich_nguoc/%s] %s -> %s id=%s" % (
                tr, he_id, kq.get("trang_thai"), kq.get("id")))
    return ra



if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Dich nguoc tin hieu cong khai → hang_cho")
    ap.add_argument("--users", nargs="*", default=["example", "fluidtrader-demo"])
    ap.add_argument("--tu-choi-nguy-hiem", action="store_true")
    ap.add_argument("--chi-xep", nargs=2, metavar=("NGUON", "HE_ID"),
                    help="Chi xep hang_cho tu he da luu")
    ap.add_argument("--track", choices=["thuong", "dca", "auto"], default="auto")
    ap.add_argument("--kho-gia", default="", help="Thu muc parquet H1")
    a = ap.parse_args()
    kho = Path(a.kho_gia) if a.kho_gia else None
    if a.chi_xep:
        tr = None if a.track == "auto" else a.track
        print(json.dumps(xep_dich_boc(a.chi_xep[0], a.chi_xep[1], kho_gia=kho,
                                      tu_choi_nguy_hiem=a.tu_choi_nguy_hiem, track=tr),
                         ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps(chay_ong(a.users, tu_choi_nguy_hiem=a.tu_choi_nguy_hiem,
                                  kho_gia=kho), ensure_ascii=False, indent=2, default=str))
