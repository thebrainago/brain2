# -*- coding: utf-8 -*-
"""Do DAC TINH van hanh cua cong kiem dinh tren du lieu TONG HOP (khong dung gia that).

Chay: python de_xuat/ma_mau/mo_phong_dac_tinh.py            (~30 giay, 1 nhan)

Hai cau hoi, moi cau do bang mo phong de khong phai tranh luan:
  A. t-test tung lenh co "thoi phong" khi cac lenh cung cum (cung tuan) tuong quan khong?
     -> ti le duong tinh gia (khong co canh nao) o muc alpha danh nghia.
  B. Mot duong ong "sang o GD1 -> kiem top-k tren GD2" bat duoc bao nhieu o THAT, voi cac cach
     da kiem dinh khac nhau? Va n (so lenh moi o) hay cach hieu chinh la don bay manh hon?

GIA DINH (ghi ro, doi duoc o hang so dau file; KHONG phai so do tu du lieu that):
  sd moi lenh 100 bps · loi nhuan chuan o muc trung binh tung o (CLT) · GD1 va GD2 doc lap
  · 2.000 o nhieu + 10 o co canh that · k = 20 o duoc chuyen sang GD2.
Muon biet gia tri that cua rho (ICC) va sd: chay hieu_ung_thiet_ke() tren loi tung lenh that cua v31/v32.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_hai_tang_mau as K  # noqa: E402

SD = 100.0          # bps moi lenh
SEED = 20261016
HO_CONG_DON = 20503  # ho Holm cong don sau v32


def phan_a(so_lan: int = 20000, n: int = 150, kich_cum: int = 5) -> list[dict]:
    rng = np.random.default_rng(SEED)
    G = n // kich_cum
    cum = np.repeat(np.arange(G), kich_cum)
    kq = []
    for rho in (0.0, 0.1, 0.3):
        chung = rng.normal(0, 1, (so_lan, G)).repeat(kich_cum, axis=1)
        rieng = rng.normal(0, 1, (so_lan, n))
        r = SD * (np.sqrt(rho) * chung + np.sqrt(1 - rho) * rieng)
        t_iid = r.mean(1) / (r.std(1, ddof=1) / np.sqrt(n))
        p_iid = stats.t.sf(t_iid, n - 1)
        p_cum = np.array([K.p_gom_cum(r[i], cum)[0] for i in range(so_lan)])
        kq.append(dict(
            rho=rho, deff=round(float(np.mean([K.hieu_ung_thiet_ke(r[i], cum) for i in range(500)])), 2),
            iid_05=float(np.mean(p_iid < 0.05)), cum_05=float(np.mean(p_cum < 0.05)),
            iid_0025=float(np.mean(p_iid < 0.0025)), cum_0025=float(np.mean(p_cum < 0.0025)),
        ))
    return kq


def phan_b(so_lan: int = 2000, n_null: int = 2000, n_that: int = 10, k: int = 20) -> list[dict]:
    rng = np.random.default_rng(SEED + 1)
    kq = []
    for n in (150, 1500):
        for e in (5, 10, 20, 40):
            delta = e / SD * np.sqrt(n)
            mu = np.r_[np.zeros(n_null), np.full(n_that, delta)]
            la_that = np.r_[np.zeros(n_null, bool), np.ones(n_that, bool)]
            acc = {c: np.zeros(2) for c in ("raw", "holm_ho", "holm_k", "bh")}   # [that_duoc_nhan, gia_duoc_nhan]
            mang_that, co_it_nhat_1 = 0.0, {c: 0 for c in acc}
            for _ in range(so_lan):
                z1 = mu + rng.normal(size=mu.size)
                top = np.argpartition(-z1, k)[:k]
                z2 = mu[top] + rng.normal(size=k)
                p2 = stats.norm.sf(z2)
                that = la_that[top]
                mang_that += that.sum()
                nhan = {
                    "raw": p2 < 0.05,
                    "holm_ho": K.holm(p2, m=HO_CONG_DON) < 0.05,
                    "holm_k": K.holm_hai_tang(p2) < 0.05,
                    "bh": K.bh(p2, 0.10),
                }
                for c, mask in nhan.items():
                    acc[c] += (np.sum(mask & that), np.sum(mask & ~that))
                    co_it_nhat_1[c] += int(np.any(mask & that))
            row = dict(n=n, e=e, t_that=round(delta, 2), that_duoc_chuyen=round(mang_that / so_lan, 2))
            for c in acc:
                row[c] = dict(that=round(acc[c][0] / so_lan, 3), gia=round(acc[c][1] / so_lan, 3),
                              it_nhat_1=round(co_it_nhat_1[c] / so_lan, 3))
            kq.append(row)
    return kq


def in_bang(a: list[dict], b: list[dict]) -> str:
    L = ["### A. Duong tinh gia khi lenh cung cum (n=150, 30 tuan x 5 lenh, KHONG co canh nao)", "",
         "| ICC (rho) | deff do duoc | t-test tung lenh @0,05 | gom cum @0,05 | t-test tung lenh @0,0025 | gom cum @0,0025 |",
         "|---|---|---|---|---|---|"]
    for x in a:
        L.append(f"| {x['rho']} | {x['deff']} | {x['iid_05']:.3f} | {x['cum_05']:.3f} | {x['iid_0025']:.4f} | {x['cum_0025']:.4f} |")
    L += ["", "### B. Duong ong sang GD1 -> kiem top-20 tren GD2 (2.000 o nhieu + 10 o canh that, 2.000 lan lap)", "",
          "`that_chuyen` = so o that (trong 10) lot vao top-20 cua GD1. Moi cot cach hieu chinh: so o THAT / so o GIA duoc nhan "
          "trung binh moi lan, va xac suat bat duoc IT NHAT 1 o that.", "",
          "| n/o | canh (bps) | t ky vong | that_chuyen | khong hieu chinh (that/gia · >=1) | Holm ho 20.503 | Holm k=20 | BH 10% |",
          "|---|---|---|---|---|---|---|---|"]
    for x in b:
        def f(c):
            d = x[c]
            return f"{d['that']}/{d['gia']} · {d['it_nhat_1']}"
        L.append(f"| {x['n']} | {x['e']} | {x['t_that']} | {x['that_duoc_chuyen']} | {f('raw')} | {f('holm_ho')} | {f('holm_k')} | {f('bh')} |")
    return "\n".join(L)


if __name__ == "__main__":
    A = phan_a()
    B = phan_b()
    print(in_bang(A, B))
