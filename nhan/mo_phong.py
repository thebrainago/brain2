# -*- coding: utf-8 -*-
"""mo_phong.py - ENGINE BACKTEST. Mot cua duy nhat de bien tin hieu thanh tien.

Quy uoc THOI GIAN (quan trong nhat file nay):
  - Template chi duoc tra ve `tin_hieu[i]` = phoi nhiem MONG MUON, tinh tu
    thong tin BIET TAI CLOSE cua bar i.
  - Engine TU dich mot bar: vi_the[i+1] = tin_hieu[i]. Template khong tu dich,
    khong tu chon diem vao -> khong the gian lan do tre.
  - Loi suat mot bar la open[i] -> open[i+1] (vao lenh tai OPEN bar ke tiep,
    CLAUDE.md luat 1). KHONG dung close->close.

Chi phi (bao cao 15/08 - loi nang nhat cua ban cu):
  - spread THAT theo gio, tu cot spread cua bar MT5.
  - truot gia.
  - phi qua dem BAT DOI XUNG mua/ban, tinh theo so ngay THAT giua cac bar.
    Loi that #1 ngay 09/08 la phi chi tinh cho chieu mua -> tang 2 %/nam
    alpha gia cho moi chien luoc co chieu ban. Canary `luon ban` gac cho nay.

TP/SL cung bar: dung OPEN cua chinh bar do de doan cai nao cham truoc
(gan TP hon -> TP truoc). KHONG mac dinh SL - "than trong co he thong" van la
so SAI, va no giet dung loai edge mong dang tim (THIET_KE muc 13).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import chi_phi as CP


@dataclass
class KetQua:
    ma: str = ""
    khung: str = ""
    index: pd.DatetimeIndex | None = None
    vi_the: np.ndarray | None = None
    loi: np.ndarray | None = None          # loi suat log RONG tung bar
    loi_tho: np.ndarray | None = None      # chua tru chi phi
    r: np.ndarray | None = None            # loi suat tai san (open->open)
    chi_phi_spread: float = 0.0
    chi_phi_truot: float = 0.0
    chi_phi_giu: float = 0.0
    so_lan_doi: int = 0
    so_lenh: int = 0
    phoi_nhiem: float = 0.0
    canh_bao: list = field(default_factory=list)
    che_do_gop: str = "log"                # log | so_hoc
    don_bay: float = 1.0
    chay_tai_khoan: bool = False           # co bar nao lam von <= nguong khong
    bar_chay: int | None = None
    ngay_chay: object = None
    von_mang: np.ndarray | None = None     # von SO HOC (co the ve 0)
    chi_tiet: dict | None = None           # `chay_he`: tung chan (mua/ban) rieng

    @property
    def von(self) -> np.ndarray:
        if self.von_mang is not None:
            return self.von_mang
        return np.exp(np.cumsum(np.nan_to_num(self.loi)))

    def chuoi(self) -> pd.Series:
        return pd.Series(self.von, index=self.index, name="von")


def _loi_suat_tien(df: pd.DataFrame) -> np.ndarray:
    """Loi suat log open[i] -> open[i+1]. Bar cuoi = 0 (khong con bar de an)."""
    o = df["open"].to_numpy(dtype=float)
    r = np.zeros(len(o))
    with np.errstate(divide="ignore", invalid="ignore"):
        r[:-1] = np.log(o[1:] / o[:-1])
    return np.nan_to_num(r, nan=0.0, posinf=0.0, neginf=0.0)


def chay(df: pd.DataFrame, tin_hieu, cp: CP.MoHinhChiPhi,
         lai_suat_nam: np.ndarray | None = None, ma: str = "", khung: str = "",
         da_dich: bool = False, don_bay: float = 1.0,
         gop: str = "tu_dong", nguong_chay: float = 0.0,
         phi_them: np.ndarray | None = None) -> KetQua:
    """Chay mot chien luoc. `tin_hieu[i]` la phoi nhiem biet tai close[i].

    da_dich=True chi dung cho CANARY (khi can dat vi the dung bien mot bar).

    `don_bay`: he so nhan phoi nhiem, ap **SAU** khi da cat ve [-1, 1]. Tach
    lam mot tham so rieng la co y: tran +-1 la tam chan chong template tra ve
    so bay (mot template tra 50 se che ra loi suat 50 lan), nen don bay phai
    la thu NGUOI GOI khai ro, khong phai thu template tu gianh duoc.

    Vi sao can: cong 1 so TONG LAI cua he voi mua-giu, nhung he chon loc chi o
    trong thi truong 16-18% thoi gian con moc o 100%. Do khong phai so cung
    don vi. Muon hoi "cung mot muc rui ro thi ben nao lai hon" thi phai dua
    duoc he len dung do bien dong cua moc - va truoc 30/08/2026 dieu do KHONG
    lam duoc: nhan tin hieu len 1,55 lan roi cat ngay ve 1,0, hai lan chay ra
    ket qua GIONG HET NHAU ma khong bao gi.

    Phi cua phan don bay them duoc thu day du: spread theo khoi luong doi va
    phi qua dem theo phoi nhiem, deu tinh tren `v` sau khi nhan.

    `gop`: CACH GOP LOI SUAT QUA THOI GIAN. Day la loi nang duoc phat hien
    03/09/2026, ngay khi du an quay sang cau hoi don bay.
      - "log"    : loi_von = v*r voi r la loi suat LOG. Cong don tuyen tinh.
      - "so_hoc" : loi_von = log(1 + v*(e^r - 1) - phi). Dung.
      - "tu_dong": "so_hoc" khi don_bay != 1, nguoc lai "log" (giu nguyen moi
                   con so cu).

    VI SAO PHAI SUA. Cach "log" cho exp(sum(L*r)) = (S_T/S_0)^L. Do khong phai
    mot vi the don bay L tai can bang hang ngay — do la mua LUY THUA cua chi
    so. Hai thu bi lam bien mat sach:
      1. LUC CAN BIEN DONG ~ 0,5*L*(L-1)*sigma^2/nam. Voi SP500 (sigma 16%)
         va L=3 do la 7,7 diem %/nam bi bo qua.
      2. CHAY TAI KHOAN. Trong log, von khong bao gio am duoc. Ngoai doi L=3
         chet sach o bat ky ngay nao -33,4%.
    Do that tren 98 nam SP500: don_bay=3 kieu log cho von cuoi x76.289.488,
    dung bang (giá cuoi/giá dau)^3, trong khi thuc te chay tai khoan thang
    10/1929. Moi ket luan CAGR o L>1 truoc 03/09/2026 deu phai xem lai.
    (Sharpe thi khong sao: no bat bien theo ti le.)

    `phi_them`: chi phi PHAN TRAM VON cong them o tung bar, do NGUOI GOI tinh.

    Vi sao can (do 12/09/2026): phi o day tinh tren `doi = |diff(v)|`, tuc tren
    phoi nhiem RONG. Mot cau truc HEDGE mo dong thoi mot chan mua va mot chan
    ban thi `v` khong doi -> he THU 0 DONG SPREAD cho hai lenh that. Tuong tu
    phi qua dem tinh tren `v` = 0 trong khi ngoai doi phai tra ca hai chan.
    Ket qua la moi cau truc hedge trong deu hon that, va cang hedge nhieu cang
    "lai". `nhan/vao_lenh.py` tinh phan chenh do roi day vao day.

    `nguong_chay`: von con lai (ti le so voi von truoc bar do) ma duoi no thi
    coi la chay tai khoan. 0,0 = chay sach. San that cat lenh som hon (XM cat
    o muc ky quy 20%), nen 0,0 la CHAN DUOI lac quan.
    """
    n = len(df)
    th = np.asarray(tin_hieu, dtype=float).reshape(-1)
    if len(th) != n:
        raise ValueError(f"tin hieu dai {len(th)} nhung du lieu {n} bar")
    if not np.isfinite(don_bay) or don_bay <= 0:
        raise ValueError(f"don_bay phai la so duong huu han, nhan {don_bay!r}")
    th = np.nan_to_num(th, nan=0.0)
    th = np.clip(th, -1.0, 1.0) * float(don_bay)

    if da_dich:
        v = th
    else:
        v = np.zeros(n)
        v[1:] = th[:-1]          # ENGINE dich, template khong duoc tu dich

    r = _loi_suat_tien(df)
    idx = df.index

    doi = np.abs(np.diff(np.concatenate(([0.0], v))))
    sp = cp.spread_mang(idx)
    phi_sp = doi * sp
    phi_tr = doi * cp.truot_gia_frac
    phi_gi = cp.phi_giu_mang(idx, v, lai_suat_nam)

    if gop == "tu_dong":
        che_do = "so_hoc" if abs(float(don_bay) - 1.0) > 1e-12 else "log"
    elif gop in ("log", "so_hoc"):
        che_do = gop
    else:
        raise ValueError(f"gop phai la log|so_hoc|tu_dong, nhan {gop!r}")

    if phi_them is not None:
        pt = np.nan_to_num(np.asarray(phi_them, float).reshape(-1), nan=0.0)
        if len(pt) != n:
            raise ValueError(f"phi_them dai {len(pt)} nhung du lieu {n} bar")
        if np.any(pt < 0):
            raise ValueError("phi_them am - phi khong duoc la khoan thu")
    else:
        pt = np.zeros(n)
    phi_tong = phi_sp + phi_tr + phi_gi + pt
    canh = list(cp.canh_bao)
    von_mang = None
    chay_tk, bar_chay, ngay_chay = False, None, None

    if che_do == "log":
        loi_tho = v * r
        loi = loi_tho - phi_tong
    else:
        # loi suat SO HOC cua tai san; moi thanh phan duoi day deu la ti le
        # cua VON (notional = v * von), nen cong tru truc tiep duoc.
        ra = np.expm1(r)
        loi_tho_sh = v * ra
        song = 1.0 + loi_tho_sh - phi_tong
        xau = np.nonzero(song <= nguong_chay)[0]
        if len(xau):
            bar_chay = int(xau[0])
            chay_tk = True
            ngay_chay = idx[bar_chay]
            song = song.copy()
            song[bar_chay:] = 1.0        # dong bang: khong con von de lai/lo
            canh.append(f"CHAY TAI KHOAN tai bar {bar_chay} ({ngay_chay}) "
                        f"voi don bay {don_bay:g}x")
        von_mang = np.cumprod(song)
        if bar_chay is not None:
            von_mang[bar_chay:] = 0.0
        loi = np.log(song)
        loi_tho = np.log1p(np.maximum(loi_tho_sh, -1.0 + 1e-12))

    return KetQua(
        ma=ma, khung=khung, index=idx, vi_the=v, loi=loi, loi_tho=loi_tho, r=r,
        chi_phi_spread=float(np.nansum(phi_sp)),
        chi_phi_truot=float(np.nansum(phi_tr)),
        chi_phi_giu=float(np.nansum(phi_gi) + np.nansum(pt)),
        so_lan_doi=int(np.sum(doi > 1e-12)),
        so_lenh=dem_lenh(v),
        phoi_nhiem=float(np.mean(np.abs(v))),
        canh_bao=canh,
        che_do_gop=che_do, don_bay=float(don_bay),
        chay_tai_khoan=chay_tk, bar_chay=bar_chay, ngay_chay=ngay_chay,
        von_mang=von_mang)


def dem_lenh(v: np.ndarray) -> int:
    """So LENH = so lan mo mot vi the moi: vao tu trang thai rong HOAC LAT CHIEU.

    Dem theo kieu "chi tinh khi di tu 0 len" la SAI voi chien luoc luon o trong
    thi truong (+1 -> -1 khong bao gio ve 0): no ra dung 1 lenh cho ca chuoi,
    roi bi bo loc "du lenh" danh truot oan. Da sap that ngay 15/08 khi thu luc cong.
    """
    v = np.asarray(v, dtype=float)
    truoc = np.concatenate(([0.0], v[:-1]))
    khac0 = np.abs(v) > 1e-12
    return int(np.sum(khac0 & (np.sign(v) != np.sign(truoc))))


def mua_giu(df: pd.DataFrame, cp: CP.MoHinhChiPhi, ma: str = "", khung: str = "",
            lai_suat_nam: np.ndarray | None = None) -> KetQua:
    """MUA-GIU CFD SAU PHI THAT - moc chinh de so sanh (THIET_KE muc 2).

    Day moi la thu ta mua duoc. `mua_giu_tho` (chi so khong phi) chi de DOC,
    khong duoc lam dieu kien PASS.
    """
    return chay(df, np.ones(len(df)), cp, lai_suat_nam, ma, khung, da_dich=True)


def mua_giu_tho(df: pd.DataFrame, ma: str = "", khung: str = "") -> KetQua:
    """Chi so khong phi. Doc de biet phi an mat bao nhieu, KHONG lam cong."""
    rong = CP.MoHinhChiPhi(ma=ma, spread_frac_chung=0.0, truot_gia_frac=0.0,
                           phi_nam_mua=0.0, phi_nam_ban=0.0, do_tin="KHAI")
    return chay(df, np.ones(len(df)), rong, None, ma, khung, da_dich=True)


# ----------------------------------------------------------------- TP / SL
def chay_tpsl(df: pd.DataFrame, tin_hieu_vao, tp_frac: float, sl_frac: float,
              cp: CP.MoHinhChiPhi, gio_toi_da: int = 0, ma: str = "",
              khung: str = "") -> KetQua:
    """Chien luoc co TP/SL. `tin_hieu_vao[i]` = +1/-1/0 biet tai close[i],
    vao lenh tai OPEN bar i+1.

    Cham ca TP lan SL trong cung mot bar -> dung OPEN cua bar do de doan:
    gan TP hon thi TP truoc. Day la quy tac cua du an, khong phai mac dinh SL.
    """
    n = len(df)
    th = np.nan_to_num(np.asarray(tin_hieu_vao, dtype=float).reshape(-1), nan=0.0)
    o = df["open"].to_numpy(dtype=float)
    hi = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    idx = df.index

    v = np.zeros(n)          # phoi nhiem giu trong bar i (de tinh phi qua dem)
    kl = np.zeros(n)         # khoi luong giao dich trong bar i (de tinh spread)
    loi_tho = np.zeros(n)
    so_lenh = 0
    dang, gia_vao, bar_vao = 0.0, 0.0, -1

    for i in range(1, n):
        # 1) VAO LENH tai OPEN bar i, theo tin hieu biet tai close bar i-1
        if dang == 0.0 and th[i - 1] != 0.0:
            dang = float(np.sign(th[i - 1]))
            gia_vao, bar_vao = o[i], i
            kl[i] += 1.0
            so_lenh += 1

        if dang == 0.0:
            continue
        v[i] = dang

        # 2) KIEM THOAT trong chinh bar i
        muc_tp = gia_vao * (1.0 + tp_frac * dang)
        muc_sl = gia_vao * (1.0 - sl_frac * dang)
        if dang > 0:
            cham_tp, cham_sl = hi[i] >= muc_tp, lo[i] <= muc_sl
        else:
            cham_tp, cham_sl = lo[i] <= muc_tp, hi[i] >= muc_sl

        gia_ra = None
        if cham_tp and cham_sl:
            # cung bar: doan bang OPEN cua chinh bar do - gan TP hon thi TP truoc.
            # KHONG mac dinh SL (THIET_KE muc 13).
            gia_ra = muc_tp if abs(o[i] - muc_tp) <= abs(o[i] - muc_sl) else muc_sl
        elif cham_tp:
            gia_ra = muc_tp
        elif cham_sl:
            gia_ra = muc_sl
        elif gio_toi_da and (i - bar_vao) >= gio_toi_da and i + 1 < n:
            gia_ra = o[i + 1]      # het gio giu -> dong o OPEN bar ke tiep

        if gia_ra is not None:
            loi_tho[i] = dang * np.log(gia_ra / o[i])
            kl[i] += 1.0
            dang, gia_vao, bar_vao = 0.0, 0.0, -1
        elif i + 1 < n:
            loi_tho[i] = dang * np.log(o[i + 1] / o[i])

    loi_tho = np.nan_to_num(loi_tho, nan=0.0, posinf=0.0, neginf=0.0)
    phi_sp = kl * cp.spread_mang(idx)
    phi_tr = kl * cp.truot_gia_frac
    phi_gi = cp.phi_giu_mang(idx, v, None)
    loi = loi_tho - phi_sp - phi_tr - phi_gi

    return KetQua(
        ma=ma, khung=khung, index=idx, vi_the=v, loi=loi, loi_tho=loi_tho,
        r=_loi_suat_tien(df),
        chi_phi_spread=float(np.nansum(phi_sp)), chi_phi_truot=float(np.nansum(phi_tr)),
        chi_phi_giu=float(np.nansum(phi_gi)), so_lan_doi=int(np.sum(kl > 0)),
        so_lenh=so_lenh,      # dem truc tiep trong vong lap, da dung cho ca lat chieu
        phoi_nhiem=float(np.mean(np.abs(v))), canh_bao=list(cp.canh_bao))


# ------------------------------------------------------- LENH DUNG TRONG BAR
def chay_dung_trong_bar(df: pd.DataFrame, cho_phep, muc, huong: str, chieu: int,
                        giu: int, cp: CP.MoHinhChiPhi, ma: str = "",
                        khung: str = "") -> KetQua:
    """Lenh CHO tai muc gia, khop TRONG bar (them 10/10/2026).

    Mo hinh cho EA kiem lai o MOI tick (khong co cong bar moi): dieu kien dang
    `gia_hien_tai > muc` kich hoat ngay khi gia cham muc, giua bar - khong phai
    o tick dau bar.

    `cho_phep[i]`, `muc[i]` BIET TAI CLOSE bar i (giong `tin_hieu` cua `chay`).
    Trong bar j = i+1:
      - huong ">" : gia di LEN qua muc. open[j] > muc -> khop o open[j] (gap
        qua muc); high[j] > muc -> khop o muc. Khong thi khong co lenh.
      - huong "<" : doi xung voi low.
    Khop o gia P, giu den OPEN bar j+giu (giu=1: chi phan con lai cua bar j).
    Tin hieu moi khi dang giu thi KEO DAI moc ra (giong `rolling(giu).max()`
    cua `ngu_phap.sinh_tu_spec`).

    KHONG nhin truoc: quyet dinh khop trong bar j chi dung open/high/low cua
    CHINH bar j (lenh cho nam san tren san tu dau bar - dung nhu ngoai doi) va
    `cho_phep`/`muc` tu bar <= j-1. Lai/lo bar j = log(open[j+1]/P).
    """
    n = len(df)
    ok = np.nan_to_num(np.asarray(cho_phep, dtype=float).reshape(-1), nan=0.0) != 0
    m = np.asarray(muc, dtype=float).reshape(-1)
    if len(ok) != n or len(m) != n:
        raise ValueError("cho_phep/muc phai dai bang du lieu")
    if huong not in (">", "<"):
        raise ValueError(f"huong phai la '>' hoac '<', nhan {huong!r}")
    chieu = 1.0 if chieu >= 0 else -1.0
    giu = max(1, int(giu))
    o = df["open"].to_numpy(dtype=float)
    hi = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    idx = df.index

    v = np.zeros(n)
    kl = np.zeros(n)
    loi_tho = np.zeros(n)
    so_lenh = 0
    het = -1                      # vi the DONG o OPEN bar `het` (-1 = dang rong)
    for j in range(1, n):
        gia_vao = None
        if ok[j - 1] and np.isfinite(m[j - 1]):
            L = m[j - 1]
            if huong == ">":
                if o[j] > L:
                    gia_vao = o[j]
                elif hi[j] > L:
                    gia_vao = L
            else:
                if o[j] < L:
                    gia_vao = o[j]
                elif lo[j] < L:
                    gia_vao = L
        if het == j:
            if gia_vao is not None and gia_vao == o[j]:
                het = j + giu             # vao lai NGAY open luc dang dong = giu tiep
            else:
                kl[j] += 1.0              # dong o OPEN bar j
                het = -1
        if het > j:                       # dang giu suot bar j
            if gia_vao is not None:
                het = max(het, j + giu)   # tin hieu moi: keo dai, khong mo lenh moi
            v[j] = chieu
            if j + 1 < n:
                loi_tho[j] = chieu * np.log(o[j + 1] / o[j])
            continue
        if gia_vao is None:
            continue
        so_lenh += 1
        kl[j] += 1.0
        het = j + giu
        v[j] = chieu
        if j + 1 < n:
            loi_tho[j] = chieu * np.log(o[j + 1] / gia_vao)
    loi_tho = np.nan_to_num(loi_tho, nan=0.0, posinf=0.0, neginf=0.0)
    phi_sp = kl * cp.spread_mang(idx)
    phi_tr = kl * cp.truot_gia_frac
    phi_gi = cp.phi_giu_mang(idx, v, None)
    loi = loi_tho - phi_sp - phi_tr - phi_gi
    return KetQua(
        ma=ma, khung=khung, index=idx, vi_the=v, loi=loi, loi_tho=loi_tho,
        r=_loi_suat_tien(df),
        chi_phi_spread=float(np.nansum(phi_sp)), chi_phi_truot=float(np.nansum(phi_tr)),
        chi_phi_giu=float(np.nansum(phi_gi)), so_lan_doi=int(np.sum(kl > 0)),
        so_lenh=so_lenh, phoi_nhiem=float(np.mean(np.abs(v))),
        canh_bao=list(cp.canh_bao))


# ------------------------------------------------------- HE NHIEU CHAN + SL/TP
def _duong_bar(o: float, h: float, l: float, c: float) -> tuple:
    """Duong gia gia dinh TRONG bar: O -> cuc tri GAN open hon -> cuc tri kia -> C.

    Cung quy tac du an da dung o `chay_tpsl` ("gan open hon thi cham truoc",
    KHONG mac dinh SL - THIET_KE muc 13). Bang nhau: nen tang O-L-H-C, nen
    giam O-H-L-C (quy uoc OHLC cua MT5)."""
    if abs(h - o) < abs(o - l):
        return (o, h, l, c)
    if abs(h - o) > abs(o - l):
        return (o, l, h, c)
    return (o, l, h, c) if c >= o else (o, h, l, c)


def _diem_tu_gia(gia: float) -> float:
    """`_Point` uoc tu muc gia (FX 5 so ~1e-5, JPY ~1e-3, vang/chi so 1e-2).
    Chi dung khi nguoi goi khong truyen `diem` - la GIA DINH, ghi vao canh_bao."""
    if not np.isfinite(gia) or gia <= 0:
        return 1e-5
    if gia < 20:
        return 1e-5
    if gia < 1000:
        return 1e-3
    return 1e-2


def chay_he(df: pd.DataFrame, chan: list[dict], cp: CP.MoHinhChiPhi, ma: str = "",
            khung: str = "", nhat_ky: list | None = None,
            diem: float | None = None, tai_khoan: dict | None = None) -> KetQua:
    """Mo phong MOT EA co nhieu chan (mua + ban) chung mot tai khoan (10/10/2026 dem).

    Vi sao: EA Breakout1 khong phai hai co che doc lap. No (1) chi mo lenh khi
    KHONG co vi the (`if(PositionSelect) checkForClose(); else checkForOpen();`),
    (2) chan moi lenh sau lenh dau trong ngay (`lastupday/lastdownday`) - ban
    khop truoc thi mua bi chan ca ngay va nguoc lai, (3) dong bang SL/TP dat
    luc vao (SL = bien doi dien khung phien, TP = R x TPFactor) va keo SL moi bar
    - khong phai giu N bar. Mo phong tung chan rieng voi `giu` la mo phong mot he
    KHAC.

    `chan` = danh sach dict tu `ngu_phap.sinh_chan` (thu tu = uu tien khi hai
    chan cung kich hoat o cung mot gia - hiem). Moi mang biet tai CLOSE bar i;
    bar j = i+1:
      1. Tick dau (open j): dang co lenh -> het gio (`giu`) dong o open; gap qua
         SL/TP -> dong o open; roi keo SL bang keo[i] (chi siet, va chi khi muc
         moi con o phia dung cua gia hien tai - khong thi MT5 tu choi).
         Khong co lenh -> chan nao du dieu kien ma gia open da qua muc (hoac
         chan vao o tick dau) thi vao o open.
      2. Di duong gia trong bar (`_duong_bar`), tung doan don dieu: dang co lenh
         thi tim SL/TP bi cat truoc; khong co lenh thi tim muc kich hoat bi cat
         truoc. Vao lenh xong (tick ke tiep) ap keo SL ngay, roi tiep tuc doan.
         Dong lenh giua bar xong van co the vao lai trong bar (neu luat ngay
         cho phep) - dung nhu EA chay moi tick.
      3. Cuoi bar con lenh: tinh lai/lo toi open j+1.
    `nhat_ky` (list) neu co: moi lenh mot dict (chan, vao/ra: bar, gia, ly do) - de soat tay.
    CHAN CHEO (co + loc): chan co `co` = (huong, muc[]) va `loc` = [(phep, muc[])]
    (EA: `bool up = current[0].high > H; if(up && gia < MA) return;`). Co bat
    khi CUC TRI bar dang chay vuot muc va giu suot bar. Khi co cua chan KHAC
    dang bat ma loc cua no khong thoa o gia hien tai, EA `return` truoc lenh vao
    -> chan nay cung KHONG vao duoc (Breakout1: gia da xuyen ca hai bien phien
    trong mot bar -> hai loc MA trai nhau, khong vao lenh nao het bar do).
    Luat ngay: chan bi chan khi ngay-trong-thang cua bar j bang gia tri cua BAT
    KY bien nao trong `chan_boi`; vao lenh xong gan `dat` = ngay do (y het EA,
    ke ca viec so NGAY TRONG THANG chu khong phai ngay day du).

    RO LENH (them 10/10/2026, chan co `ro` - `nhan/ro_mql.py`): EA Breakout2/2-2/3
    khong co SL/TP; ham dong chay MOI tick tren TONG loi lo (tien) cua moi lenh:
    chot dinh (`peakwin>=moc && loi<peakwin*ti_le`), cat lo (`loi<=cat_lo`),
    hedge NGUOC chieu khi so lenh == n va gia cham muc (gia_vao -+ khoang*_Point)
    hoac loi <= nguong. Loi lo tien = sum lot*hop_dong*(chieu*(gia-gia_vao)) - mot
    spread moi lenh (gia la BID nhu bieu do MT5: mua vao ASK, ban dong ASK).
    Trong bar: loi lo tuyen tinh theo gia tren moi doan don dieu, nen su kien
    (cham nguong) tim duoc chinh xac; dinh chi tang khi loi tang (cuoi doan).
    Thu tu trong mot tick y het ma EA: cap nhat dinh -> chot dinh -> cat lo ->
    hedge (voi `postotal` doc TRUOC khi dong - EA dung bien cu). Neu EA se mo
    hedge ngay sau khi vua dong het (chi xay ra khi gap gia) -> dem vao
    `chi_tiet["ro_bat_thuong"]`, khong mo (lenh mo coi khong mo phong).
    Loi suat cua ro tinh theo von danh nghia LENH DAU (lenh hedge 0.4 lot = 4x).
    `diem` = _Point; None -> uoc tu gia (canh_bao).

    TAI KHOAN KHAI BAO (`tai_khoan`, them 10/10/2026 - cong giu luoi/martingale):
    {"von": USD, "don_bay": x, "stop_out": muc ky quy (vd 0.5 = 50%)}. Chi ap cho
    chan co `ro` (ro hedge / luoi) - lenh don (SL/TP, giu N bar) KHONG doi.
      - Von (balance) cong loi lo TIEN cua ro khi dong (`_loi_ro`: da tru spread).
        TRUOT GIA (moi lenh, luc mo VA luc dong: lot*hop_dong*gia*truot_gia_frac) va
        QUA DEM (cuoi moi bar, theo chieu tung lenh: lot*hop_dong*gia*phi_giu_mang)
        tru THANG vao von ngay khi phat sinh (them 10/10/2026 toi) -> von rong / stop-out
        / ky quy tu do tinh co ca hai. Chung KHONG vao `_loi_ro` (EA chi doc
        POSITION_PROFIT de chot dinh/hedge) - so tien y het phan trong chuoi `loi`.
      - Ky quy = hop_dong * gia / don_bay * max(tong lot mua, tong lot ban)
        (tai khoan hedging, kieu "chan lon hon"; tien ky quy = tien yet gia * gia,
        dung cho xxxUSD tai khoan USD).
      - STOP-OUT kieu MT5 (10/10/2026 toi): von_rong (von + loi tha noi) <=
        stop_out * ky_quy -> san dong LENH LO NHAT truoc (loi tien thap nhat tai gia
        do, hoa -> lenh cu hon), TUNG LENH MOT, tinh lai muc ky quy sau moi lenh; dung
        khi muc ky quy > stop_out. Lenh con lai tiep tuc (EA van quan ly: chot dinh,
        hedge theo `postotal` moi, luoi giu chuoi lot). Het lenh -> ro dong
        (`ly_do="stop_out"`). Tren moi doan don dieu von_rong - stop_out*ky_quy
        tuyen tinh theo gia nen muc stop-out tim CHINH XAC (nhu chot dinh).
        `so_stop_out` = so LAN cham nguong; `so_lenh_stop_out` = so lenh bi san dong.
      - Lenh moi (lenh dau / hedge / lenh luoi) bi TU CHOI khi von_rong sau khi
        them < ky quy moi (thieu ky quy tu do) -> dem `tu_choi_ky_quy`; lenh luoi
        bi tu choi duoc thu lai o bar sau (chuoi lot khong tien).
      - Von <= 0 -> CHAY: khong vao lenh nua.
    Ket qua o `chi_tiet["tai_khoan"]`. `tai_khoan=None` -> hanh vi cu y het.

    SL/TP THEO KHOANG CACH (`sl_kc`/`tp_kc`, EA Template: SL = gia_vao -+
    max(ATR*k, 3*spread), TP = gia_vao +- ATR*m) va `rui_ro` (khoi luong theo
    rui ro: lenh lo dung SL mat `rui_ro` von -> trong so = rui_ro*gia/khoang_SL);
    `spread_max_diem`: bo lenh khi spread (diem) cua gio do > nguong (SpreadOK).

    KHONG nhin truoc: quyet dinh o bar j chi dung mang tai i = j-1 va gia cua
    chinh bar j (lenh cho/SL/TP nam san tren san). Test cat: `test_sltp_he.py`,
    `test_ro_hedge.py`.
    """
    n = len(df)
    K = len(chan)
    o = df["open"].to_numpy(dtype=float)
    hi = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    cl = df["close"].to_numpy(dtype=float)
    idx = df.index
    sp = cp.spread_mang(idx)
    canh_bao = list(cp.canh_bao)
    if any(c_.get("ro") for c_ in chan) or any(c_.get("spread_max_diem") for c_ in chan):
        if diem is None:
            diem = _diem_tu_gia(float(np.nanmedian(cl)) if n else 1.0)
            canh_bao.append(f"_Point uoc tu gia = {diem:g} (gia dinh)")
        if any(c_.get("ro") for c_ in chan) and ma and not ma.upper().endswith("USD"):
            canh_bao.append("ro lenh: nguong tien gia dinh tien yet gia = tien tai khoan "
                            f"(USD) - {ma} khong yet gia USD")
    try:
        ngay_thang = np.asarray(idx.day)
    except AttributeError:
        ngay_thang = np.zeros(n, dtype=int)
    for c_ in chan:
        for f in ("cho", "muc", "sl", "keo", "sl_kc", "tp_kc"):
            if c_.get(f) is not None and len(c_[f]) != n:
                raise ValueError(f"chan.{f} phai dai bang du lieu")
        if c_.get("muc") is not None and c_.get("huong") not in (">", "<"):
            raise ValueError("chan co `muc` phai co huong '>' hoac '<'")

    loi_tho = np.zeros((K, n))
    kl = np.zeros((K, n))
    vm = np.zeros((K, n))                       # phoi nhiem MUA cuoi bar (trong so)
    vb = np.zeros((K, n))                       # phoi nhiem BAN cuoi bar
    co_lenh = np.zeros(n)
    so_lenh = [0] * K
    so_hedge = [0] * K
    bat_thuong = [0]
    bien: dict = {}
    pos: dict | None = None
    dinh_g = [0.0]                              # `peakwin` (bien TOAN CUC cua EA)
    cong_dong = [-1]                            # bar ham dong da qua cong `prevTime` (luoi)
    mo_bar = [-1]                               # bar mo lenh dau gan nhat (cong ham mo)
    luoi_tk = {"max_lenh": 0, "max_lot": 0.0, "lo_tha_noi_max": 0.0, "vuot_chuoi": 0}
    cuc = [0.0, 0.0]                           # cao / thap cua bar dang chay
    EPS = 1e-7
    tk = None
    if tai_khoan is not None:
        tk = {"von_dau": float(tai_khoan["von"]), "von": float(tai_khoan["von"]),
              "don_bay": float(tai_khoan["don_bay"]),
              "stop_out": float(tai_khoan["stop_out"]),
              "so_stop_out": 0, "tu_choi_ky_quy": 0, "chay": False,
              "muc_ky_quy_min": float("inf"), "von_rong_min": float(tai_khoan["von"]),
              "bar_stop_out": [], "so_lenh_stop_out": 0,
              "phi_truot_usd": 0.0, "phi_qua_dem_usd": 0.0}
        # qua dem (frac / don vi danh nghia) cuoi moi bar, theo chieu - giong `loi_k`
        swap_mua = cp.phi_giu_mang(idx, np.ones(n), None) if n else np.zeros(0)
        swap_ban = cp.phi_giu_mang(idx, -np.ones(n), None) if n else np.zeros(0)
        if ma and not ma.upper().endswith("USD"):
            canh_bao.append(f"tai khoan: ky quy/loi lo gia dinh tien yet gia = USD - {ma}")

    def _so(a: float, phep: str, b: float) -> bool:
        return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}.get(phep, False)

    def _bi_chan_cheo(k: int, i: int, gia: float) -> bool:
        hi_, lo_ = max(cuc[0], gia), min(cuc[1], gia)
        for m_, c_ in enumerate(chan):
            if m_ == k or c_.get("co") is None or not bool(c_["cho"][i]):
                continue
            h_, lv = c_["co"]
            if not np.isfinite(lv[i]):
                continue
            bat = hi_ > lv[i] if h_ == ">" else lo_ < lv[i]
            if bat and not all(np.isfinite(x[i]) and _so(gia, ph, x[i])
                               for ph, x in c_.get("loc") or []):
                return True
        return False

    def _duoc(k: int, i: int, ngay, bo_cho: bool = False) -> bool:
        c_ = chan[k]
        if not bo_cho and not bool(c_["cho"][i]):
            return False
        if (c_.get("ro") or {}).get("cong_mo_bar") and mo_bar[0] == i + 1:
            return False                      # ham mo: `if(curTime==prevTime) return;`
        if any(bien.get(b) == ngay for b in c_.get("chan_boi") or []):
            return False
        if c_.get("muc") is not None and not np.isfinite(c_["muc"][i]):
            return False
        if c_.get("sl") is not None and not np.isfinite(c_["sl"][i]):
            return False
        sm = c_.get("spread_max_diem")
        if sm is not None and i + 1 < n and sp[i + 1] * o[i + 1] / diem > float(sm) + 1e-9:
            return False                      # SpreadOK(): spread (point) > nguong
        return True

    def _keo(i: int, gia: float) -> None:
        if pos.get("ro") is not None:
            return
        kk = chan[pos["k"]].get("keo")
        if kk is None or pos["sl"] is None:
            return
        x = kk[i]
        if not np.isfinite(x):
            return
        if pos["chieu"] > 0 and pos["sl"] < x < gia:
            pos["sl"] = x
        elif pos["chieu"] < 0 and gia < x < pos["sl"]:
            pos["sl"] = x

    # ------------------------------------------------------------ RO LENH
    def _he_so_kq(legs: list) -> float:
        """ky_quy(p) = he_so * p (USD)."""
        if tk is None or not legs:
            return 0.0
        C = pos["ro"]["hop_dong"] if pos is not None else 0.0
        mua = sum(L["lot"] for L in legs if L["ch"] > 0)
        ban = sum(L["lot"] for L in legs if L["ch"] < 0)
        return C / tk["don_bay"] * max(mua, ban)

    def _du_ky_quy(ch: int, lot: float, gia: float, C: float) -> bool:
        """Lenh moi co du ky quy tu do khong (sau khi them: von_rong >= ky quy)."""
        if tk is None:
            return True
        legs = list(pos["legs"]) if pos is not None and pos.get("legs") else []
        loi = _loi_ro(gia) if legs else 0.0
        mua = sum(L["lot"] for L in legs if L["ch"] > 0) + (lot if ch > 0 else 0.0)
        ban = sum(L["lot"] for L in legs if L["ch"] < 0) + (lot if ch < 0 else 0.0)
        kq_moi = C * gia / tk["don_bay"] * max(mua, ban)
        # lenh moi chiu ngay mot spread (mua o ASK) - tinh vao von rong
        return tk["von"] + loi > kq_moi + EPS

    def _kiem_stop_out(j: int, p: float) -> bool:
        """Theo doi muc ky quy; True neu san vua dong ro vi stop-out."""
        if tk is None or pos is None or not pos.get("legs"):
            return False
        m = _he_so_kq(pos["legs"]) * p
        if m <= 0:
            return False
        eq = tk["von"] + _loi_ro(p)
        tk["von_rong_min"] = min(tk["von_rong_min"], eq)
        tk["muc_ky_quy_min"] = min(tk["muc_ky_quy_min"], eq / m)
        if eq > tk["stop_out"] * m + 1e-4:
            return False
        tk["so_stop_out"] += 1
        tk["bar_stop_out"].append(int(j))
        # MT5: dong lenh LO NHAT truoc, tung lenh, den khi muc ky quy > stop_out
        while pos is not None and pos["legs"]:
            if len(pos["legs"]) == 1:
                tk["so_lenh_stop_out"] += 1
                _dong_ro(j, p, "stop_out")
                return True
            C = pos["ro"]["hop_dong"]
            loi_l = [L["lot"] * C * (L["ch"] * (p - L["e"]) - L["s"]) for L in pos["legs"]]
            x = int(np.argmin(loi_l))           # argmin: hoa -> lenh cu hon (dau danh sach)
            _dong_chan_le(j, p, x)
            m = _he_so_kq(pos["legs"]) * p
            eq = tk["von"] + _loi_ro(p)
            if m <= 0 or eq > tk["stop_out"] * m + 1e-4:
                if m > 0:
                    tk["muc_ky_quy_min"] = min(tk["muc_ky_quy_min"], eq / m)
                return False
        return False

    def _tru_von(x: float, loai: str) -> None:
        """Truot / qua dem (USD) tru thang vao von - chi khi co tai khoan."""
        if tk is None or x == 0.0:
            return
        tk["von"] -= x
        tk[loai] += x
        if pos is None and tk["von"] <= 0:
            tk["chay"] = True

    def _dong_chan_le(j: int, gia: float, x: int) -> None:
        """San dong MOT lenh (stop-out tung lenh); ro van mo."""
        k = pos["k"]
        C = pos["ro"]["hop_dong"]
        L = pos["legs"].pop(x)
        loi_t = L["lot"] * C * (L["ch"] * (gia - L["e"]) - L["s"])
        loi_tho[k, j] += L["w"] * L["ch"] * np.log(gia / L["ref"])
        kl[k, j] += L["w"]
        tk["von"] += loi_t
        _tru_von(L["lot"] * C * gia * cp.truot_gia_frac, "phi_truot_usd")
        tk["so_lenh_stop_out"] += 1
        if nhat_ky is not None and nhat_ky:
            nhat_ky[-1].setdefault("stop_out_le", []).append(
                {"bar": j, "gia": gia, "chieu": L["ch"], "lot": L["lot"],
                 "loi_tien": round(loi_t, 4)})

    def _loi_ro(p: float) -> float:
        C = pos["ro"]["hop_dong"]
        return sum(L["lot"] * C * (L["ch"] * (p - L["e"]) - L["s"]) for L in pos["legs"])

    def _doc_ro() -> tuple[float, float]:
        """loi(p) = N*p + K0 (tuyen tinh tren doan)."""
        C = pos["ro"]["hop_dong"]
        N = sum(L["lot"] * C * L["ch"] for L in pos["legs"])
        K0 = sum(L["lot"] * C * (-L["ch"] * L["e"] - L["s"]) for L in pos["legs"])
        return N, K0

    def _them_chan_ro(j: int, ch: int, lot: float, gia: float) -> None:
        w = lot / pos["ro"]["lot_dau"]
        pos["legs"].append({"ch": ch, "lot": lot, "e": gia, "s": sp[j] * gia,
                            "w": w, "ref": gia})
        kl[pos["k"], j] += w
        if tk is not None:
            _tru_von(lot * pos["ro"]["hop_dong"] * gia * cp.truot_gia_frac, "phi_truot_usd")

    def _dong_ro(j: int, gia: float, ly_do: str) -> None:
        nonlocal pos
        k = pos["k"]
        loi_t = _loi_ro(gia)
        for L in pos["legs"]:
            loi_tho[k, j] += L["w"] * L["ch"] * np.log(gia / L["ref"])
            kl[k, j] += L["w"]
        if nhat_ky is not None and nhat_ky:
            nhat_ky[-1].update(bar_ra=j, gia_ra=gia, ly_do=ly_do, loi_tien=round(loi_t, 4),
                               so_chan=len(pos["legs"]))
        if tk is not None:
            tk["von"] += loi_t
            _tru_von(sum(L["lot"] for L in pos["legs"]) * pos["ro"]["hop_dong"] * gia
                     * cp.truot_gia_frac, "phi_truot_usd")
            if tk["von"] <= 0:
                tk["chay"] = True
        pos = None

    def _kich_hedge(h: dict, p: float, loi: float) -> bool:
        if h["kich"] == "loi":
            return loi <= h["nguong"] + EPS
        L, ph = h["_muc"], h["_phep"]
        return p <= L + 1e-12 if ph == "<=" else p >= L - 1e-12

    def _tick_ro(j: int, p: float) -> bool:
        """Mot lan goi ham dong cua EA tai gia p. Tra True neu vua them hedge."""
        if _kiem_stop_out(j, p):
            return False
        ro = pos["ro"]
        lu_st = pos.get("luoi")
        loi = _loi_ro(p)
        if lu_st is not None:
            luoi_tk["lo_tha_noi_max"] = max(luoi_tk["lo_tha_noi_max"], -loi)
        d = ro.get("dinh")
        if d:
            if d.get("reset_am") and loi <= 0:
                dinh_g[0] = 0.0
            else:
                dinh_g[0] = max(dinh_g[0], loi)
        so_cu = len(pos["legs"])                # `postotal` doc dau ham
        dong = False
        if d and dinh_g[0] >= d["moc"] and loi < d["ti_le"] * dinh_g[0] + EPS:
            _dong_ro(j, p, "chot_dinh")
            dong = True
        if not dong and ro.get("cat_lo") is not None and loi <= ro["cat_lo"] + EPS:
            _dong_ro(j, p, "cat_lo")
            dong = True
        them = False
        for h in pos["hedge"] if pos is not None else ro.get("hedge") or []:
            if so_cu != h["khi_so_lenh"]:
                continue
            if dong:
                # EA dung `postotal` cu: neu dieu kien hedge van dung se mo lenh
                # MO COI ngay sau CloseAll. Khong mo phong - chi dem.
                if h["kich"] == "loi" and loi <= h["nguong"] + EPS:
                    bat_thuong[0] += 1
                continue
            if _kich_hedge(h, p, loi):
                if not _du_ky_quy(-pos["chieu"], float(h["lot"]), p, ro["hop_dong"]):
                    tk["tu_choi_ky_quy"] += 1
                    continue
                _them_chan_ro(j, -pos["chieu"], float(h["lot"]), p)
                so_hedge[pos["k"]] += 1
                if h.get("reset_dinh"):
                    dinh_g[0] = 0.0
                if nhat_ky is not None and nhat_ky:
                    nhat_ky[-1].setdefault("hedge", []).append(
                        {"bar": j, "gia": p, "lot": float(h["lot"])})
                them = True
        lu = ro.get("luoi")
        if lu and lu_st is not None and cong_dong[0] != j:
            # sau `if(curTime==prevTime) return;`: chi lan goi DAU TIEN cua bar
            cong_dong[0] = j
            kich = p <= lu_st["muc"] + 1e-12 if lu_st["phep"] == "<=" else \
                p >= lu_st["muc"] - 1e-12
            if dong:
                if kich:
                    bat_thuong[0] += 1        # EA dung `postotal` cu -> lenh mo coi
            elif kich:
                n_ = lu_st["n"]
                if n_ >= len(lu["lot"]):
                    luoi_tk["vuot_chuoi"] += 1
                elif not _du_ky_quy(pos["chieu"] * (1 if lu.get("cung_chieu", True) else -1),
                                    float(lu["lot"][n_]), p, ro["hop_dong"]):
                    tk["tu_choi_ky_quy"] += 1     # thu lai o bar sau
                else:
                    lot = float(lu["lot"][n_])
                    lu_st["n"] = n_ + 1
                    ch_t = pos["chieu"] * (1 if lu.get("cung_chieu", True) else -1)
                    _them_chan_ro(j, ch_t, lot, p)
                    so_hedge[pos["k"]] += 1
                    goc, d_ = lu["buoc"]["mua" if pos["chieu"] > 0 else "ban"]
                    lu_st["muc"] = p + (sp[j] * p if goc == "ASK" else 0.0) + float(d_) * diem
                    if lu.get("reset_dinh"):
                        dinh_g[0] = 0.0
                    luoi_tk["max_lenh"] = max(luoi_tk["max_lenh"], len(pos["legs"]))
                    luoi_tk["max_lot"] = max(luoi_tk["max_lot"], lot)
                    if nhat_ky is not None and nhat_ky:
                        nhat_ky[-1].setdefault("them", []).append(
                            {"bar": j, "gia": p, "lot": lot})
                    them = True
        return them

    def _su_kien_ro(cur: float, b: float) -> float | None:
        """Gia GAN nhat trong (cur, b] tai do EA se lam gi do (dong / hedge)."""
        ro = pos["ro"]
        up = b > cur
        N, K0 = _doc_ro()
        ung = []

        def _them(x):
            if (up and cur < x <= b) or (not up and b <= x < cur):
                ung.append(x)
        giam = (up and N < 0) or (not up and N > 0)        # loi giam tren doan nay
        if giam and N != 0:
            d = ro.get("dinh")
            if d and dinh_g[0] >= d["moc"]:
                _them((d["ti_le"] * dinh_g[0] - K0) / N)
            if ro.get("cat_lo") is not None:
                _them((ro["cat_lo"] - K0) / N)
            for h in pos["hedge"]:
                if h["kich"] == "loi" and len(pos["legs"]) == h["khi_so_lenh"]:
                    _them((h["nguong"] - K0) / N)
        for h in pos["hedge"]:
            if h["kich"] == "diem" and len(pos["legs"]) == h["khi_so_lenh"]:
                if (h["_phep"] == "<=" and not up) or (h["_phep"] == ">=" and up):
                    _them(h["_muc"])
        if tk is not None and pos["legs"]:
            # von + N p + K0 = stop_out * a * p  (tuyen tinh tren doan)
            a = _he_so_kq(pos["legs"])
            mau = N - tk["stop_out"] * a
            if a > 0 and mau != 0:
                _them(-(tk["von"] + K0) / mau)
        if not ung:
            return None
        return min(ung) if up else max(ung)

    def _mo_ro(k: int, i: int, j: int, gia: float, ngay) -> None:
        nonlocal pos
        c_ = chan[k]
        ro = c_["ro"]
        ch = c_["chieu"]
        pos = {"k": k, "chieu": ch, "ro": ro, "legs": [], "sl": None, "tp": None,
               "het": None, "w": 1.0}
        _them_chan_ro(j, ch, float(ro["lot_dau"]), gia)
        hs = []
        for h in ro.get("hedge") or []:
            h = dict(h)
            if h["kich"] == "diem":
                D = float(h["khoang_diem"]) * diem
                if ch > 0:      # hedgeprice = ASK luc vao - D; kich khi BID <= hedgeprice
                    h["_muc"], h["_phep"] = gia + sp[j] * gia - D, "<="
                else:           # hedgeprice = BID luc vao + D; kich khi BID >= hedgeprice
                    h["_muc"], h["_phep"] = gia + D, ">="
            hs.append(h)
        pos["hedge"] = hs
        lu = ro.get("luoi")
        if lu:
            goc, d_ = lu["muc_dau"]["mua" if ch > 0 else "ban"]
            pos["luoi"] = {"muc": gia + (sp[j] * gia if goc == "ASK" else 0.0) + float(d_) * diem,
                           "phep": lu["phep"]["mua" if ch > 0 else "ban"], "n": 0}
            luoi_tk["max_lenh"] = max(luoi_tk["max_lenh"], 1)
        mo_bar[0] = j
        if (ro.get("dinh") or {}).get("reset_vao"):
            dinh_g[0] = 0.0

    def _vao(k: int, i: int, j: int, gia: float, ngay) -> bool:
        nonlocal pos
        c_ = chan[k]
        ch = c_["chieu"]
        if c_.get("ro") is not None:
            if tk is not None and (tk["chay"] or not _du_ky_quy(
                    ch, float(c_["ro"]["lot_dau"]), gia, c_["ro"]["hop_dong"])):
                if not tk["chay"]:
                    tk["tu_choi_ky_quy"] += 1
                return False
            if nhat_ky is not None:
                nhat_ky.append({"chan": k, "chieu": ch, "bar_vao": j, "gia_vao": gia,
                                "ro": True})
            _mo_ro(k, i, j, gia, ngay)
            for b_ in c_.get("dat") or []:
                bien[b_] = ngay
            so_lenh[k] += 1
            co_lenh[j] = 1.0
            if _tick_ro(j, gia) and pos is not None:   # tick ke tiep: ham dong
                _tick_ro(j, gia)
            return True
        w = 1.0
        sl = float(c_["sl"][i]) if c_.get("sl") is not None else None
        tp = None
        if c_.get("sl_kc") is not None:
            d = float(c_["sl_kc"][i])
            if not np.isfinite(d) or d <= 0:
                return False                  # `if(atr <= 0) return;`
            d = max(d, float(c_.get("sl_kc_min_spread") or 0.0) * sp[j] * gia)
            sl = gia - ch * d
            if c_.get("tp_kc") is not None and np.isfinite(c_["tp_kc"][i]) and c_["tp_kc"][i] > 0:
                tp = gia + ch * float(c_["tp_kc"][i])
            if c_.get("rui_ro"):
                w = float(c_["rui_ro"]) * gia / d
        if sl is not None and (sl - gia) * ch >= 0:
            return False                      # SL sai phia: MT5 tu choi lenh
        if sl is not None and c_.get("tp") and c_.get("sl_kc") is None:
            tp = gia + ch * abs(gia - sl) * float(c_["tp"])
        het = None if (sl is not None or tp is not None) else j + max(1, int(c_["giu"]))
        pos = {"k": k, "chieu": ch, "sl": sl, "tp": tp, "het": het, "ref": gia, "w": w}
        if nhat_ky is not None:
            nhat_ky.append({"chan": k, "chieu": ch, "bar_vao": j, "gia_vao": gia,
                            "sl": sl, "tp": tp, "trong_so": w})
        for b in c_.get("dat") or []:
            bien[b] = ngay
        so_lenh[k] += 1
        kl[k, j] += w
        co_lenh[j] = 1.0
        _keo(i, gia)                          # checkForClose o tick ke tiep
        return True

    def _ra(j: int, gia: float, ly_do: str = "") -> None:
        nonlocal pos
        k = pos["k"]
        if nhat_ky is not None and nhat_ky:
            nhat_ky[-1].update(bar_ra=j, gia_ra=gia, ly_do=ly_do, sl_cuoi=pos["sl"])
        loi_tho[k, j] += pos["w"] * pos["chieu"] * np.log(gia / pos["ref"])
        kl[k, j] += pos["w"]
        pos = None

    def _vao_tai(i: int, j: int, gia: float, ngay, tick_dau: bool) -> bool:
        """Vao NGAY tai gia hien tai neu co chan da qua muc (hoac vao o tick dau)."""
        for k in range(K):
            c_ = chan[k]
            lai = (not tick_dau and c_.get("muc") is None and c_.get("muc_lai") is not None)
            if not _duoc(k, i, ngay, bo_cho=lai):
                continue
            m = c_.get("muc")
            if lai:
                # cap mua/ban bu nhau quanh MOT muc, EA kiem moi tick: vao lai GIUA bar
                # (sau khi ro dong) theo gia hien tai so voi muc (vd pivot gio)
                lv = c_["muc_lai"][i]
                ok = bool(np.isfinite(lv)) and _so(gia, c_["phep_lai"], lv)
            elif m is None:
                ok = tick_dau                 # tin hieu tick dau: chi o open
            elif c_["huong"] == ">":
                ok = gia > m[i]
            else:
                ok = gia < m[i]
            if ok and not _bi_chan_cheo(k, i, gia) and _vao(k, i, j, gia, ngay):
                return True
        return False

    for j in range(1, n):
        i = j - 1
        ngay = ngay_thang[j]
        if pos is not None:
            co_lenh[j] = 1.0
            if pos.get("ro") is not None:
                if _tick_ro(j, o[j]) and pos is not None:
                    _tick_ro(j, o[j])
            else:
                ch, sl, tp = pos["chieu"], pos["sl"], pos["tp"]
                if pos["het"] is not None and pos["het"] <= j:
                    _ra(j, o[j], "het_gio")
                elif sl is not None and (o[j] - sl) * ch <= 0:
                    _ra(j, o[j], "gap_sl")        # gap qua SL
                elif tp is not None and (o[j] - tp) * ch >= 0:
                    _ra(j, o[j], "gap_tp")        # gap qua TP
                else:
                    _keo(i, o[j])
        cuc[0] = cuc[1] = o[j]
        if pos is None:
            _vao_tai(i, j, o[j], ngay, True)
        duong = _duong_bar(o[j], hi[j], lo[j], cl[j])
        for s_ in range(3):
            cur, b = duong[s_], duong[s_ + 1]
            if b == cur:
                continue
            len_ = b > cur
            bo_qua: set = set()
            for _ in range(16 + K):           # moi vong: mot su kien
                if pos is not None and pos.get("ro") is not None:
                    x = _su_kien_ro(cur, b)
                    if x is None:
                        break
                    cur = x
                    cuc[0], cuc[1] = max(cuc[0], x), min(cuc[1], x)
                    if _tick_ro(j, x) and pos is not None:
                        _tick_ro(j, x)        # tick ke tiep (cung gia) sau khi hedge
                    if pos is None:
                        _vao_tai(i, j, cur, ngay, False)
                    continue
                if pos is not None:
                    ch, sl, tp = pos["chieu"], pos["sl"], pos["tp"]
                    x = ld = None
                    if len_:
                        if ch > 0 and tp is not None and cur < tp <= b:
                            x, ld = tp, "tp"
                        elif ch < 0 and sl is not None and cur < sl <= b:
                            x, ld = sl, "sl"
                    else:
                        if ch > 0 and sl is not None and b <= sl < cur:
                            x, ld = sl, "sl"
                        elif ch < 0 and tp is not None and b <= tp < cur:
                            x, ld = tp, "tp"
                    if x is None:
                        break
                    _ra(j, x, ld)
                    cur = x
                    cuc[0], cuc[1] = max(cuc[0], x), min(cuc[1], x)
                    _vao_tai(i, j, cur, ngay, False)   # EA kiem lai ngay tick sau
                    continue
                best = None
                for k in range(K):
                    c_ = chan[k]
                    if c_.get("muc") is None or not _duoc(k, i, ngay) or k in bo_qua:
                        continue
                    L = c_["muc"][i]
                    if len_ and c_["huong"] == ">" and cur <= L < b:
                        d = L - cur
                    elif not len_ and c_["huong"] == "<" and b < L <= cur:
                        d = cur - L
                    else:
                        continue
                    if best is None or d < best[0]:
                        best = (d, k, L)
                if best is None:
                    break
                if _bi_chan_cheo(best[1], i, best[2]):
                    # Breakout1: chan cheo giu nguyen het bar (cuc tri chi lon
                    # dan, hai loc MA trai nhau) -> bo chan nay o phan con lai
                    # cua doan; doan sau xet lai.
                    bo_qua.add(best[1])
                    continue
                if not _vao(best[1], i, j, best[2], ngay):
                    break
                cur = best[2]
                cuc[0], cuc[1] = max(cuc[0], cur), min(cuc[1], cur)
            if pos is not None and pos.get("ro") is not None and cur != b:
                _tick_ro(j, b)                # cap nhat dinh o cuoi doan (khong co su kien)
            cuc[0], cuc[1] = max(cuc[0], b), min(cuc[1], b)
        if pos is not None:
            co_lenh[j] = 1.0
            k = pos["k"]
            if pos.get("ro") is not None:
                if tk is not None and j + 1 < n:
                    C_ = pos["ro"]["hop_dong"]
                    _tru_von(sum(L["lot"] * C_ * o[j + 1] *
                                 (swap_mua[j] if L["ch"] > 0 else swap_ban[j])
                                 for L in pos["legs"]), "phi_qua_dem_usd")
                for L in pos["legs"]:
                    if j + 1 < n:
                        loi_tho[k, j] += L["w"] * L["ch"] * np.log(o[j + 1] / L["ref"])
                        L["ref"] = o[j + 1]
                    if L["ch"] > 0:
                        vm[k, j] += L["w"]
                    else:
                        vb[k, j] += L["w"]
            elif j + 1 < n:
                loi_tho[k, j] += pos["w"] * pos["chieu"] * np.log(o[j + 1] / pos["ref"])
                pos["ref"] = o[j + 1]
                if pos["chieu"] > 0:
                    vm[k, j] = pos["w"]
                else:
                    vb[k, j] = pos["w"]

    loi_tho = np.nan_to_num(loi_tho, nan=0.0, posinf=0.0, neginf=0.0)
    loi_k = np.zeros((K, n))
    phi_sp = phi_tr = phi_gi = 0.0
    for k in range(K):
        a = kl[k] * sp
        t = kl[k] * cp.truot_gia_frac
        # tai khoan hedging: lenh mua tra phi mua, lenh ban tra phi ban - rieng tung lenh
        g = cp.phi_giu_mang(idx, vm[k], None) + cp.phi_giu_mang(idx, -vb[k], None)
        loi_k[k] = loi_tho[k] - a - t - g
        phi_sp += float(np.nansum(a))
        phi_tr += float(np.nansum(t))
        phi_gi += float(np.nansum(g))
    v = (vm - vb).sum(axis=0)
    ct = {"chan": [{"chieu": chan[k]["chieu"], "so_lenh": so_lenh[k], "loi": loi_k[k],
                    "so_hedge": so_hedge[k]} for k in range(K)],
          "ro_bat_thuong": bat_thuong[0]}
    if any((c_.get("ro") or {}).get("luoi") for c_ in chan):
        ct["luoi"] = dict(luoi_tk)
    if tk is not None:
        ct["tai_khoan"] = {k_: v_ for k_, v_ in tk.items()}
    return KetQua(
        ma=ma, khung=khung, index=idx, vi_the=v, loi=loi_k.sum(axis=0),
        loi_tho=loi_tho.sum(axis=0), r=_loi_suat_tien(df),
        chi_phi_spread=phi_sp, chi_phi_truot=phi_tr, chi_phi_giu=phi_gi,
        so_lan_doi=int(np.sum(kl.sum(axis=0) > 0)), so_lenh=int(sum(so_lenh)),
        phoi_nhiem=float(np.mean(co_lenh)), canh_bao=canh_bao, chi_tiet=ct)


# ------------------------------------------------------------------ TIEN ICH
def dich_khong_nhin_truoc(s: pd.Series | np.ndarray) -> np.ndarray:
    """Tien ich cho template: chuyen chuoi chi bao thanh tin hieu hop le.
    Chi de tuong minh - engine van tu dich them mot bar nua."""
    a = np.asarray(s, dtype=float)
    return np.nan_to_num(a, nan=0.0)
