# -*- coding: utf-8 -*-
"""Phân tích Fibo xoắn ốc: φ so với xoắn ốc ngẫu nhiên (permutation qua N_RAND lần rút)."""
import glob, numpy as np, pandas as pd
from common2 import bh_fdr
FAMS = ["phi", "rand_g", "rand_rot", "rand_both"]; SC = ["1nen=1ATR", "theo_chan_song"]; DR = ["CW", "CCW"]
rows = []
for f in sorted(glob.glob("results6/spiral_acc_*.npy")):
    tag = f.split("spiral_acc_")[1][:-4]; A = np.load(f)
    # các lát cắt: (scaling, dir, period) cụ thể + gộp
    slices = []
    for sc in (0, 1):
        for dr in (0, 1):
            for pi, pn in ((0, "IS"), (2, "OOS")):
                slices.append((f"{SC[sc]}|{DR[dr]}|{pn}", (slice(sc, sc + 1), slice(dr, dr + 1), slice(pi, pi + 1))))
    slices.append(("GOP_TAT_CA", (slice(None), slice(None), slice(None))))
    for name, (s1, s2, s3) in slices:
        real = A[0, 0, s1, s2, s3].sum((0, 1, 2))
        for metric, num, den in (("giu5", 1, 0), ("hoi1ATR", 2, 0), ("moc_tg_trung_dao_chieu", 4, 3)):
            if real[den] < 5: continue
            obs = real[num] / real[den]
            for fi in (1, 2, 3):
                nl = A[fi, :, s1, s2, s3].sum((1, 2, 3)); null = nl[:, num] / np.maximum(nl[:, den], 1)
                z = (obs - null.mean()) / (null.std() + 1e-12)
                p = (1 + (np.abs(null - null.mean()) >= abs(obs - null.mean())).sum()) / (len(null) + 1)
                rows.append(dict(data=tag, lat_cat=name, chi_tieu=metric, n_phi=int(real[den]), P_phi=100 * obs,
                                 doi_chung=FAMS[fi], P_null=100 * null.mean(), n_null_moi_lan=nl[:, den].mean(), z=z, p=p))
R = pd.DataFrame(rows)
sub = R[R.lat_cat != "GOP_TAT_CA"].copy(); sub["q"] = bh_fdr(sub.p.values)
g = R[R.lat_cat == "GOP_TAT_CA"].copy(); g["q"] = bh_fdr(g.p.values)
R = pd.concat([sub, g]); R.round(4).to_csv("results6/spiral_tests.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(g.round(3).to_string(index=False))
print("lát cắt:", len(sub), "p<0.05:", (sub.p < .05).sum(), "q<0.05:", (sub.q < .05).sum())
print(sub[sub.p < .05].round(3).to_string(index=False))
