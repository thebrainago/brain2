# -*- coding: utf-8 -*-
"""Quét tín hiệu đơn + tổ hợp trên các khung. Chạy: python -m vang.ma.chay_quet (từ gốc repo)."""
from __future__ import annotations
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

# cho phép chạy file trực tiếp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from vang.ma import du_lieu, tin_hieu, mo_phong

GOC = Path(__file__).resolve().parents[1]
KET_QUA = GOC / "ket_qua"
BAO_CAO = GOC / "bao_cao"
KET_QUA.mkdir(parents=True, exist_ok=True)
BAO_CAO.mkdir(parents=True, exist_ok=True)

PHI = (
    "Phí XM GOLD.i# (micro quy về #): spread trung vị H1 16 điểm (0,16 USD/ounce) khi cột spread nến = 0; "
    "khi có cột spread (từ 2018-10-10) dùng spread nến. Mỗi chiều = nửa spread + trượt 0,5×spread "
    "(giả định thận trọng, chưa đo demo). Hoa hồng 0. Mặc định swap = 0 như tester Ultra Low (DISABLED); "
    "một phần tổ hợp tốt nhất được chạy lại với swap đủ (long −83,83 USD/lot/đêm, short +20,64, nhân 3 thứ Tư)."
)


def _ghi_csv(rows, path):
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def quet_khung(ten_khung: str, day_du=True, tinh_swap=False):
    t0 = time.time()
    df, nguon, tz = du_lieu.tai_khung(ten_khung)
    tz_may_chu = "máy chủ XM" in tz
    df = du_lieu.them_cot_thoi_gian(df, tz_may_chu=tz_may_chu)
    print(f"=== {ten_khung} {len(df)} nến | {df.time.iloc[0]} → {df.time.iloc[-1]} | {nguon} | {tz}", flush=True)

    ho_vao = tin_hieu.HO_VAO if day_du else tin_hieu.HO_VAO_NHO
    ho_loc = tin_hieu.HO_LOC if day_du else tin_hieu.HO_LOC_NHO
    ho_qt = tin_hieu.HO_QT if day_du else tin_hieu.HO_QT_NHO

    # bỏ phiên/ORB trên D1 (không có cấu trúc giờ)
    if ten_khung == "D1":
        ho_vao = [x for x in ho_vao if not x.startswith("orb_")]
        ho_loc = [x for x in ho_loc if not x.startswith("phien_")]
        ho_qt = [q for q in ho_qt if q[0] != "atr_sl20_eod"]

    cache_vao = {}
    cache_loc = {}
    for ten in ho_vao:
        try:
            cache_vao[ten] = tin_hieu.tin_vao(df, ten)
        except Exception:
            print("Lỗi tín hiệu", ten, traceback.format_exc()[-400:], flush=True)
    for ten in ho_loc:
        try:
            cache_loc[ten] = tin_hieu.bo_loc(df, ten)
        except Exception:
            print("Lỗi lọc", ten, traceback.format_exc()[-400:], flush=True)

    rows = []
    # mua giữ
    r = mo_phong.mua_giu(df)
    r.update(khung=ten_khung, vao="mua_giu", loc="khong", nguon=nguon, tz=tz, ho="nen")
    rows.append(r)
    print(f"  mua_giu CAGR={r['cagr']*100:.2f}% DD={r['dd']*100:.2f}%", flush=True)

    tong_to_hop = len(cache_vao) * len(cache_loc) * len(ho_qt)
    k = 0
    for ten_v, sig in cache_vao.items():
        for ten_l, loc in cache_loc.items():
            for qt in ho_qt:
                k += 1
                try:
                    r = mo_phong.mo_phong_df(df, sig, loc, qt, tinh_swap=tinh_swap, khung=ten_khung)
                except Exception:
                    print("Lỗi mô phỏng", ten_v, ten_l, qt[0], traceback.format_exc()[-400:], flush=True)
                    continue
                r.update(khung=ten_khung, vao=ten_v, loc=ten_l, nguon=nguon, tz=tz, ho="nen")
                rows.append(r)
        if k % 200 == 0:
            print(f"  ... {k}/{tong_to_hop} tổ hợp, {time.time()-t0:.1f}s", flush=True)

    # Lưới / DCA / hedge chiều mua
    for ten_l, loc in cache_loc.items():
        if ten_l not in ("khong", "ema_trend_55", "ema_trend_200", "chi_mua", "adx_25", "mua_vu_8_2"):
            continue
        for buoc, chan, tp, sl in ((1.0, 4, 1.0, 5.0), (1.0, 6, 0.8, 6.0), (1.5, 4, 1.2, 5.0)):
            try:
                r = mo_phong.mo_phong_luoi(
                    df, loc, buoc_atr=buoc, max_chan=chan, tp_atr_tb=tp, sl_tong_atr=sl,
                    tinh_swap=tinh_swap, khung=ten_khung,
                )
            except Exception:
                print("Lỗi lưới", ten_l, traceback.format_exc()[-400:], flush=True)
                continue
            r.update(khung=ten_khung, vao="luoi_dca", loc=ten_l, nguon=nguon, tz=tz, ho="luoi")
            rows.append(r)

    dt = time.time() - t0
    print(f"  xong {ten_khung}: {len(rows)} dòng, {dt:.1f}s", flush=True)
    return rows


def bang_md(rows, tieu_de, path, top=30):
    df = pd.DataFrame(rows)
    if df.empty:
        path.write_text(tieu_de + "\n\nKhông có dòng kết quả.\n", encoding="utf-8")
        return df
    df = df.sort_values(["dat", "cagr"], ascending=[False, False])
    dat = df[df["dat"] == True]  # noqa: E712
    lines = [
        f"# {tieu_de}",
        "",
        f"Viết lúc 2026-11-27, giờ Việt Nam (UTC+7). {PHI}",
        "",
        f"- Tổng tổ hợp đã đo: **{len(df)}**",
        f"- Tổ hợp ĐẠT (CAGR kép > 10%/năm, DD tối đa < 80%, ≥ 20 lệnh, vốn cuối > 0): **{len(dat)}**",
        "",
        "## Mua giữ (không đòn bẩy, đã trừ spread+trượt vào/ra)",
        "",
    ]
    mg = df[df["vao"] == "mua_giu"]
    if len(mg):
        lines.append("| Khung | Từ | Đến | Năm | CAGR | DD | Lợi nhuận |")
        lines.append("|---|---|---|---:|---:|---:|---:|")
        for _, r in mg.iterrows():
            lines.append(
                f"| {r['khung']} | {str(r['tu'])[:10]} | {str(r['den'])[:10]} | {r['nam']:.2f} | "
                f"{r['cagr']*100:.2f}% | {r['dd']*100:.2f}% | {r['loi_nhuan_lai']*100:.1f}% |"
            )
        lines.append("")
    lines += [
        "## Tổ hợp tốt nhất (sắp theo ĐẠT, rồi CAGR)",
        "",
        "| Hạng | Khung | Vào | Lọc | Quản trị | CAGR | DD | Lệnh | Thắng | PF | Từ | Đến | Swap | Đạt |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|",
    ]
    for i, r in df.head(top).iterrows():
        lines.append(
            f"| {i} | {r['khung']} | {r['vao']} | {r['loc']} | {r['quan_tri']} | "
            f"{r['cagr']*100:.2f}% | {r['dd']*100:.2f}% | {int(r['n_lenh'])} | {r['winrate']*100:.1f}% | "
            f"{r['pf']:.2f} | {str(r['tu'])[:10]} | {str(r['den'])[:10]} | {r['swap']} | {'có' if r['dat'] else 'không'} |"
        )
    # top theo từng họ
    lines += ["", "## Tín hiệu vào — tổ hợp tốt nhất mỗi tín hiệu (mọi lọc/QT)", ""]
    lines += ["| Vào | Khung | Lọc | Quản trị | CAGR | DD | Lệnh | Đạt |", "|---|---|---|---|---:|---:|---:|---|"]
    for v, g in df.groupby("vao"):
        r = g.sort_values(["dat", "cagr"], ascending=[False, False]).iloc[0]
        lines.append(
            f"| {v} | {r['khung']} | {r['loc']} | {r['quan_tri']} | {r['cagr']*100:.2f}% | "
            f"{r['dd']*100:.2f}% | {int(r['n_lenh'])} | {'có' if r['dat'] else 'không'} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return df


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # mặc định: D1, H4, H1 đầy đủ; M15/M5 bộ thu gọn
    khung = ["D1", "H4", "H1", "M15", "M5"]
    if argv:
        khung = [a.upper() for a in argv]
    all_rows = []
    t0 = time.time()
    for k in khung:
        day_du = k in {"D1", "H4", "H1"}
        try:
            rows = quet_khung(k, day_du=day_du, tinh_swap=False)
        except Exception:
            print("LỖI KHUNG", k, traceback.format_exc(), flush=True)
            continue
        _ghi_csv(rows, KET_QUA / f"quet_{k}_khong_swap.csv")
        all_rows.extend(rows)

    ts = time.strftime("%Y-%m-%d_%H%M", time.localtime())
    _ghi_csv(all_rows, KET_QUA / f"quet_gop_khong_swap_{ts}.csv")
    df = bang_md(all_rows, "Kết quả quét tín hiệu vàng — XM GOLD CFD (chưa tính swap)", BAO_CAO / "QUET_TIN_HIEU.md", top=40)

    # chạy lại top đạt với swap đầy đủ (cùng khung/tín hiệu)
    dat = df[(df["dat"] == True) & (df["vao"] != "mua_giu")].head(15) if not df.empty else df  # noqa
    swap_rows = []
    if len(dat):
        print("=== Chạy lại top ĐẠT với swap đầy đủ ===", flush=True)
        cache_df = {}
        for _, r in dat.iterrows():
            k = r["khung"]
            if k not in cache_df:
                d, nguon, tz = du_lieu.tai_khung(k)
                d = du_lieu.them_cot_thoi_gian(d, tz_may_chu=("máy chủ XM" in tz))
                cache_df[k] = (d, nguon, tz)
            d, nguon, tz = cache_df[k]
            if r["ho"] == "luoi":
                loc = tin_hieu.bo_loc(d, r["loc"])
                # parse quan_tri luoi_b1.0_c4_tp1.0_sl5.0
                try:
                    parts = r["quan_tri"].replace("luoi_", "").split("_")
                    buoc = float(parts[0][1:])
                    chan = int(parts[1][1:])
                    tp = float(parts[2][2:])
                    sl = float(parts[3][2:])
                except Exception:
                    continue
                rr = mo_phong.mo_phong_luoi(d, loc, buoc, chan, tp, sl, tinh_swap=True, khung=k)
            else:
                # tìm qt tuple
                qt = None
                for q in tin_hieu.HO_QT + tin_hieu.HO_QT_NHO:
                    if q[0] == r["quan_tri"]:
                        qt = q
                        break
                if qt is None:
                    continue
                sig = tin_hieu.tin_vao(d, r["vao"])
                loc = tin_hieu.bo_loc(d, r["loc"])
                rr = mo_phong.mo_phong_df(d, sig, loc, qt, tinh_swap=True, khung=k)
            rr.update(khung=k, vao=r["vao"], loc=r["loc"], nguon=nguon, tz=tz, ho=r["ho"])
            swap_rows.append(rr)
            print(f"  SWAP {k} {r['vao']}/{r['loc']}/{r['quan_tri']} CAGR={rr['cagr']*100:.2f}% DD={rr['dd']*100:.2f}% dat={rr['dat']}", flush=True)
        if swap_rows:
            _ghi_csv(swap_rows, KET_QUA / f"quet_top_co_swap_{ts}.csv")
            bang_md(swap_rows, "Top tổ hợp ĐẠT — chạy lại có swap đầy đủ", BAO_CAO / "QUET_TOP_CO_SWAP.md", top=20)

    # tóm tắt JSON số đo
    tomtat = {
        "viet_luc_vn": time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.localtime()),
        "giay": round(time.time() - t0, 1),
        "n_to_hop": len(all_rows),
        "n_dat_khong_swap": int(df["dat"].sum()) if len(df) else 0,
        "phi": PHI,
        "von_dau_usd": mo_phong.VON_DAU,
        "rui_ro_moi_lenh": mo_phong.RUI_RO,
        "khung": khung,
    }
    if len(df):
        top = df.sort_values(["dat", "cagr"], ascending=[False, False]).head(10)
        tomtat["top10"] = top[["khung", "vao", "loc", "quan_tri", "cagr", "dd", "n_lenh", "winrate", "pf", "tu", "den", "dat", "swap"]].to_dict(orient="records")
    (KET_QUA / "tom_tat.json").write_text(json.dumps(tomtat, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("XONG", tomtat["giay"], "s, tổ hợp", tomtat["n_to_hop"], "đạt", tomtat["n_dat_khong_swap"], flush=True)


if __name__ == "__main__":
    main()
