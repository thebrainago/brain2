# -*- coding: utf-8 -*-
"""Tổng hợp Phần 2: chọn tốt nhất IS -> OOS, so đối chứng, bootstrap, FDR, và độ 'ảo' khi khớp giá HA/brick."""
import numpy as np, pandas as pd
from common2 import bh_fdr
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
R = pd.read_csv("results6/charts_all.csv"); B = pd.read_csv("results6/charts_boot.csv")
B["q"] = bh_fdr(B.p_boot.values)
k = ["ticker", "tf", "method", "param", "mode"]
real = R[R.fill == "that"]
oos = real[real.period == "OOS"].set_index(k); isr = real[real.period == "IS"].set_index(k)
fake = R[R.fill == "ao"].set_index(k + ["period"])
B = B.set_index(k)
B["IS_sharpe"] = isr.sharpe.reindex(B.index)
for c in ["PF", "expR", "win", "trades", "maxdd_pct", "tot_ret_pct", "exposure"]: B["OOS_" + c] = oos[c].reindex(B.index)
B["ao_IS_sharpe"] = [fake.sharpe.get(i + ("IS",), np.nan) for i in B.index]
B["ao_OOS_sharpe"] = [fake.sharpe.get(i + ("OOS",), np.nan) for i in B.index]
B = B.reset_index()
bh = oos.reset_index(); bh = bh[bh.method == "BL_BuyHold"][["ticker", "tf", "sharpe", "tot_ret_pct", "maxdd_pct"]].rename(
    columns=dict(sharpe="BH_OOS_sharpe", tot_ret_pct="BH_OOS_ret", maxdd_pct="BH_OOS_dd"))
bl = B[B.method.isin(["BL_Donchian", "BL_EMA"])]
blbest = bl.loc[bl.groupby(["ticker", "tf"]).IS_sharpe.idxmax()][["ticker", "tf", "method", "OOS_sharpe"]].rename(
    columns=dict(method="BL_tot_nhat_IS", OOS_sharpe="BL_OOS_sharpe"))
B = B.merge(bh, on=["ticker", "tf"]).merge(blbest, on=["ticker", "tf"])
B["hon_BL"] = B.OOS_sharpe > B.BL_OOS_sharpe; B["hon_BH"] = B.OOS_sharpe > B.BH_OOS_sharpe
B.round(3).to_csv("results6/charts_best_IS_to_OOS.csv", index=False)
# độ ảo trên toàn lưới
f = R[~R.method.str.startswith("BL_")].pivot_table(index=k + ["period"], columns="fill", values=["sharpe", "PF"])
f.columns = [f"{a}_{b}" for a, b in f.columns]; f = f.reset_index()
f["ao_tru_that_sharpe"] = f.sharpe_ao - f.sharpe_that
inf = f.groupby(["method", "tf"]).agg(sharpe_ao_tb=("sharpe_ao", "median"), sharpe_that_tb=("sharpe_that", "median"),
                                      chenh_tb=("ao_tru_that_sharpe", "median"), PF_ao_tb=("PF_ao", "median"), PF_that_tb=("PF_that", "median")).round(2)
inf.to_csv("results6/charts_fake_vs_real.csv")
print(inf.to_string())
nm = B[~B.method.str.startswith("BL_")]
print("\nSố phép thử (PP phi chuẩn):", len(nm), " p<0.05:", (nm.p_boot < .05).sum(), " q<0.05:", (nm.q < .05).sum(),
      " OOS>BL:", nm.hon_BL.sum(), " OOS>B&H:", nm.hon_BH.sum(), " OOS>cả hai:", (nm.hon_BL & nm.hon_BH).sum())
cols = ["ticker", "tf", "method", "param", "mode", "IS_sharpe", "OOS_sharpe", "OOS_PF", "OOS_expR", "OOS_win", "OOS_trades", "OOS_maxdd_pct",
        "p_boot", "q", "BL_OOS_sharpe", "BH_OOS_sharpe", "ao_OOS_sharpe"]
print(B[cols].round(2).to_string(index=False))
