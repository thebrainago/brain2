# -*- coding: utf-8 -*-
"""xuong_tach.py - BOC TACH CO CHE de dung cho chien luoc khac (22/10/2026, Claude).

Mot he dat = TIN HIEU VAO + QUAN LI LENH (+ bo loc). Muon cay phan quan li sang tin hieu khac (hay nguoc lai) thi phai biet
phan nao THAT SU sinh loi. Chu du an: "quan li lenh quan trong hon entry"; do 05/09 tren luoi, entry co tinh SAI van cho 92-97 %/nam.
Nhung voi tung he cu the thi sao? Module nay do bang hai phep tren engine that, o cung lot:

  1. QUAN LI TREN NHIEU: giu NGUYEN bo quan li, thay tin hieu bang tin hieu THAY THE (dich vong chuoi su kien di ngau nhien: giu so lenh,
     ti le mua/ban, cum su kien; mat quan he voi gia). Neu van lai ~ nhu he goc -> quan li (hoac thi truong thuan) gánh.
  2. TIN HIEU TREN QUAN LI TRUNG TINH: giu NGUYEN tin hieu, thay quan li bang hai bo trung tinh (chi TP; luoi chung). Neu van lai ->
     tin hieu gánh.
Nhan (chi la nhan, khong phai cong): QUAN_LI_GANH · TIN_HIEU_GANH · CA_HAI_DEU_LAI (moi thu deu lai: thuong la thi truong thuan,
vd mot chieu tren cap dang xu huong) · CAN_CA_HAI (chi lai khi di cung nhau) · KHONG_LAI.
Sau do TACH THANH NGUYEN TU vao kho (`kho_co_che`): nguon_lenh (tin hieu), quan_li, go_lenh (hedge / go), bo_loc - kem so do va nhan,
de `xuong_toan_tu` cay cheo. Moi so la MÔ PHỎNG.
"""
from __future__ import annotations

import math
import random

import numpy as np
import pandas as pd

from nhan import kho_co_che as KHO
from nhan import xuong_may as XM
from nhan import xuong_tin_hieu as XT

QL_TRUNG_TINH = {
    "tp_chi": {"tp_pct": 0.003, "dca_toi_da": 0, "hedge_khi_lo_pct": 0.0, "trail_kich_pct": 0.0},
    "luoi_chung": {"tp_pct": 0.002, "dca_buoc_pct": 0.005, "dca_toi_da": 3, "dca_he_so_lot": 1.3, "hedge_khi_lo_pct": 0.0,
                   "trail_kich_pct": 0.0},
}


def dac_trung_vao(s: np.ndarray, index: pd.DatetimeIndex) -> dict:
    """Chu ky so cua chuoi tin hieu: so lenh/nam, ti le mua, gian cach trung vi (nen), gio / thu doi hoi nhieu nhat."""
    s = np.sign(np.asarray(s, float))
    i = np.nonzero(s)[0]
    nam = max((index[-1] - index[0]).days / 365.25, 1e-6)
    if not len(i):
        return {"so_lenh_nam": 0.0, "ti_le_mua": None, "gian_cach_nen": None, "gio_top": [], "thu_top": []}
    gio = pd.DatetimeIndex(index[i]).hour.value_counts(normalize=True).sort_values(ascending=False)
    thu = pd.DatetimeIndex(index[i]).dayofweek.value_counts(normalize=True).sort_values(ascending=False)
    return {"so_lenh_nam": round(len(i) / nam, 1), "ti_le_mua": round(float((s[i] > 0).mean()), 3),
            "gian_cach_nen": int(np.median(np.diff(i))) if len(i) > 1 else None,
            "gio_top": [(int(h), round(float(v), 2)) for h, v in gio.head(3).items()],
            "thu_top": [(int(h), round(float(v), 2)) for h, v in thu.head(2).items()]}


def tuong_quan_vao(a: np.ndarray, b: np.ndarray, cua_so: int = 24) -> float | None:
    """Tuong quan giua hai chuoi tin hieu qua CHIEU DANG GIU (chieu su kien gan nhat, het han sau `cua_so` nen): cao = hai he vao
    cung huong cung luc (it da dang), am = hay vao nguoc nhau (co the hedge / bu tru)."""
    ha, hb = XT._huong_gan_nhat(a, cua_so), XT._huong_gan_nhat(b, cua_so)
    if ha.std() == 0 or hb.std() == 0:
        return None
    return round(float(np.corrcoef(ha, hb)[0, 1]), 3)


def quan_li_hieu_dung(r: dict) -> dict:
    """Tinh cach quan li THUC TE tu ket qua engine: do sau trung binh cua ro, ti le TP, ngay ket lau nhat, hedge / go."""
    ro = max(int(r.get("so_ro") or 0), 1)
    return {"so_ro": int(r.get("so_ro") or 0), "lenh_moi_ro": round(float(r.get("so_lenh") or 0) / ro, 2),
            "ti_le_tp": round(float(r.get("so_tp") or 0) / ro, 2), "so_khoa": int(r.get("so_khoa") or 0),
            "so_go": int(r.get("so_go") or 0), "ket_nen_max": r.get("ket_nen_max"), "lot_mo_max": r.get("lot_mo_max")}


def _diem(r: dict) -> float:
    return XM.diem_tho(r)


def phan_ra(may: XM.May, t: dict, thu: dict, lot: float | None = None, so_mau: int = 6, hat: int = 1) -> dict:
    """Phan ra dong gop tin hieu vs quan li cua mot cau hinh tren IS, o cung `lot` (None -> lot keo theo sut giam muc tieu cua may)."""
    if lot is None:
        cl = may.chuan_lot(t, thu)
        if cl["tinh_trang"] not in ("vua", "tran_lot"):
            return {"nhan": "KHONG_LAI", "ly_do": "khong keo duoc lot (%s)" % cl["tinh_trang"]}
        lot = cl["lot"]
    thu = {**thu, "ql": XM.chuan_hoa_ql(thu.get("ql"))}
    doan = (0.0, may.cuoi_is)
    goc = may.chay(t, thu, doan, lot)
    if goc.get("loi"):
        return {"nhan": "KHONG_LAI", "ly_do": goc["loi"]}
    d_goc = _diem(goc)
    df = may.gia(thu["ma"], thu["khung"])
    t2 = may.the_cua(t, thu)
    s = may.tin_hieu(t2, thu, df)
    if s is None:                                                        # luoi: tin hieu = bo loc chieu, khong tach duoc
        return {"nhan": "KHONG_TACH_DUOC", "ly_do": "the luoi: vao theo bo cho phep, khong co chuoi tin hieu de thay the"}
    cuoi = int(len(df) * may.cuoi_is)
    rng = random.Random("%s|%s" % (t["id"], hat))
    # 1. quan li tren nhieu: tin hieu thay the (dich vong CA chuoi roi cat IS -> khong cat vao giua cum)
    mau = []
    viec = []
    for _ in range(so_mau):
        lech = rng.randrange(int(len(df) * 0.15), int(len(df) * 0.85))
        th = XT.thay_the_dich_vong(s, df.index, lech)
        tn = {"id": "nhieu_%s_%d" % (t["id"][:20], lech), "loai": "he_hoan_thien", "tin_hieu": th}
        viec.append((tn, thu, doan, lot))
    ql_nhieu = may.chay_lo(viec)
    d_nhieu = [_diem(r) for r in ql_nhieu]
    # 2. tin hieu tren quan li trung tinh
    d_tt = {}
    rs = may.chay_lo([(t, {**thu, "ql": q}, doan, lot) for q in QL_TRUNG_TINH.values()])
    for k, r in zip(QL_TRUNG_TINH, rs):
        d_tt[k] = _diem(r)
    m = float(np.mean(d_nhieu)) if d_nhieu else None
    e = max(d_tt.values()) if d_tt else None
    ra = {"lot": lot, "diem_goc": round(d_goc, 3), "lai_goc": goc.get("lai_pct_nam"), "dd_goc": goc.get("sut_giam_pct"),
          "quan_li_tren_nhieu": {"trung_binh": round(m, 3), "tot_nhat": round(max(d_nhieu), 3), "te_nhat": round(min(d_nhieu), 3),
                                 "ti_le_lai": round(sum(1 for x in d_nhieu if x > 0) / len(d_nhieu), 2), "so_mau": len(d_nhieu)},
          "tin_hieu_tren_ql_trung_tinh": {k: round(v, 3) for k, v in d_tt.items()},
          "dac_trung_vao": dac_trung_vao(s[:cuoi], df.index[:cuoi]), "quan_li_hieu_dung": quan_li_hieu_dung(goc)}
    ra["nhan"], ra["giai_thich"] = _nhan(d_goc, m, e)
    return ra


def _nhan(d_goc: float, m: float, e: float) -> tuple[str, str]:
    if d_goc <= 0:
        return "KHONG_LAI", "cấu hình gốc không có lãi/sụt giảm dương trên IS"
    cao_m, cao_e = m >= 0.6 * d_goc, e >= 0.6 * d_goc
    if cao_m and cao_e:
        return "CA_HAI_DEU_LAI", "cả tín hiệu thay thế lẫn quản lí trung tính đều giữ ≥ 60 % điểm: thường là thị trường thuận (một chiều trên cặp đang xu hướng); cơ chế này khó cấy đi nơi khác"
    if cao_m:
        return "QUAN_LI_GANH", "quản lí giữ ≥ 60 % điểm khi tín hiệu bị thay bằng nhiễu, còn tín hiệu gốc trên quản lí trung tính thì không: phần ĐÁNG CẤY là quản lí lệnh"
    if cao_e:
        return "TIN_HIEU_GANH", "tín hiệu giữ ≥ 60 % điểm trên quản lí trung tính, quản lí trên nhiễu thì không: phần ĐÁNG CẤY là điểm vào"
    return "CAN_CA_HAI", "chỉ lãi khi tín hiệu và quản lí đi cùng nhau: cấy riêng từng phần có thể mất lãi; giữ nguyên cặp này"


def nguyen_tu(t: dict, thu: dict, ket: dict, r: dict | None = None) -> list[dict]:
    """Tach mot cau hinh thanh nguyen tu kho (chua ghi). `ket` = ket qua `phan_ra`; `r` = do duoc tot nhat (lai_pct_nam...)."""
    ql = XM.chuan_hoa_ql(thu.get("ql"))
    do = {k: r.get(k) for k in ("lai_pct_nam", "sut_giam_pct") if r and r.get(k) is not None}
    do["nhan_ganh"] = ket.get("nhan")
    nhan = ["MÔ PHỎNG"]
    ra = []
    th = t.get("tin_hieu") or {}
    ra.append(KHO.co_che("nguon_lenh", "%s [%s]" % (t.get("ten", t["id"])[:60], XT.mo_ta(th)[:60]), XT.mo_ta(th),
                         tham={"tin_hieu": th, "tham": thu.get("tham") or {}, "ma": thu["ma"], "khung": thu["khung"]},
                         khoang=th.get("khoang") or {}, tu_the=t["id"], kho="xuong", do_duoc=do, nhan=nhan))
    qa = {k: v for k, v in ql.items() if k not in ("hedge_khi_lo_pct", "hedge_ti_le", "mo_khoa_pct", "hedge_max_lan", "go_tien", "lot_tren_1000")}
    ra.append(KHO.co_che("quan_li", "QL %s" % t["id"][:40], _mo_ta_ql(qa), tham=qa, tu_the=t["id"], kho="xuong", do_duoc=do, nhan=nhan))
    if ql.get("hedge_khi_lo_pct"):
        qg = {k: ql[k] for k in ("hedge_khi_lo_pct", "hedge_ti_le", "mo_khoa_pct", "hedge_max_lan", "go_tien") if k in ql}
        ra.append(KHO.co_che("go_lenh", "GO %s" % t["id"][:40], "hedge/khóa rồi gỡ: " + _mo_ta_ql(qg), tham=qg, tu_the=t["id"],
                             kho="xuong", do_duoc=do, nhan=nhan))
    for lc in (th.get("bo_loc") or []):
        ra.append(KHO.co_che("bo_loc", "LOC %s %s" % ((lc.get("tham") or {}).get("kieu", "?"), t["id"][:30]), "", tham=lc.get("tham") or {},
                             tu_the=t["id"], kho="xuong", do_duoc=do, nhan=nhan))
    return ra


def _mo_ta_ql(q: dict) -> str:
    return ", ".join("%s=%s" % (k, v) for k, v in q.items())


# ------------------------------------------------------------------------------------------------- da dang hoa nguyen tu
def vec_ql(q: dict) -> list[float]:
    """Vec to chuan hoa cua mot bo quan li de do khoang cach (log cho tham so ty le)."""
    q = XM.chuan_hoa_ql(q)
    lg = lambda x: math.log(max(float(x or 0) , 1e-4))                   # noqa: E731
    return [lg(q.get("tp_pct", 0.003)) / 3, lg(q.get("dca_buoc_pct", 0.005)) / 3 if q.get("dca_toi_da") else -3.0,
            float(q.get("dca_toi_da", 0)) / 10, float(q.get("dca_he_so_lot", 1.0)) - 1.0,
            (float(q.get("hedge_khi_lo_pct", 0)) / 30), 1.0 if q.get("trail_kich_pct") else 0.0]


def da_dang(ds: list[dict], k: int, khoa=lambda d: d["ql"]) -> list[dict]:
    """Chon k phan tu CACH XA NHAU nhat (farthest-point) theo `vec_ql(khoa(d))`, bat dau tu phan tu dau (thuong la tot nhat)."""
    if len(ds) <= k:
        return list(ds)
    v = [vec_ql(khoa(d)) for d in ds]
    chon = [0]
    dmin = [math.dist(v[0], x) for x in v]
    while len(chon) < k:
        j = max(range(len(ds)), key=lambda i: dmin[i])
        chon.append(j)
        dmin = [min(dmin[i], math.dist(v[j], v[i])) for i in range(len(ds))]
    return [ds[i] for i in chon]
