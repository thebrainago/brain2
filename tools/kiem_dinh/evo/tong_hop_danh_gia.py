# Tong hop danh_gia_lai.json: so pass theo tung bo tieu chi.
import json, sys, collections as C
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/workspace/brain2-run/danh_gia_lai.json"))
import sqlite3
_c = sqlite3.connect("file:/workspace/brain2/nao.db?mode=ro", uri=True)
G11 = {m: json.loads(cg).get("11_khong_an_khe_dao_ngay", True) for m, cg in
       _c.execute("SELECT gt_ma, cong FROM ket_qua WHERE superseded_by IS NULL")}
# Cong 11 (an khe dao ngay) la CAN THIET: lai den tu bao gia bia luc dao ngay -> loai truoc.
ok = [r for r in d if "loi" not in r]
print("tong", len(d), "loi", len(d) - len(ok), "truot cong 11 (khe dao ngay):", sum(1 for r in ok if G11.get(r["ma"]) is False))
ok = [r for r in ok if G11.get(r["ma"]) is not False]
def P(r, k="A", pf="pf_lenh", pfmin=1.2, pk="p", nmin=30):
    m = r.get(k) or {}; p = r["p_repo"] if pk == "p_repo" else m.get("p")
    return (m.get("so_lenh", 0) >= nmin and (m.get(pf) or 0) >= pfmin and (m.get("sharpe") or -9) >= 0.3
            and m.get("tb_lenh_pct", 0) > 0 and p is not None and p <= 0.05)
bo = {"CU (pf bar, p max-hat repo)": lambda r: P(r, pf="pf_bar", pk="p_repo"),
      "SUA p gop, pf bar": lambda r: P(r, pf="pf_bar"),
      "SUA pf lenh, p repo": lambda r: P(r, pk="p_repo"),
      "SUA ca hai (A=phi repo)": lambda r: P(r),
      "SUA + PF>=1.1": lambda r: P(r, pfmin=1.1),
      "SUA + phi that R1 (spread tick, swap XM)": lambda r: P(r, "R1") if "R1" in r else P(r),
      "SUA + phi that R2 (swap 0)": lambda r: P(r, "R2") if "R2" in r else P(r)}
for k, f in bo.items():
    s = [r for r in ok if f(r)]; print(f"{k}: {len(s)}")
# truot theo tieu chi (A, da sua)
t = C.Counter()
for r in ok:
    m = r["A"]
    if m["so_lenh"] < 30: t["lenh<30"] += 1
    if (m.get("pf_lenh") or 0) < 1.2: t["pf_lenh<1.2"] += 1
    if (m.get("sharpe") or -9) < 0.3: t["sharpe<0.3"] += 1
    if m["tb_lenh_pct"] <= 0: t["tb<=0"] += 1
    if m.get("p") is None or m["p"] > 0.05: t["p>0.05"] += 1
    if m["tb_lenh_tho_pct"] > 0 >= m["tb_lenh_pct"]: t["phi_an_het_A"] += 1
    for k in ("R1", "R2"):
        if k in r and m["tb_lenh_tho_pct"] > 0 >= m["tb_lenh_pct"] and r[k]["tb_lenh_pct"] > 0: t[f"phi_an_het_A->duong_{k}"] += 1
print(dict(t))
# BH tham khao tren p (A)
ps = sorted([(r["A"]["p"], r["ma"]) for r in ok if r["A"].get("p") is not None]); m = len(ok)
bh = [x for i, x in enumerate(ps) if x[0] <= 0.10 * (i + 1) / m]; print("BH q=0.10 tren", m, ":", len(bh))
print("ky vong pass do may (p<=0.05 tren m):", round(0.05 * m))
# theo khung
for kh in ("H1", "H4", "D1"):
    x = [r["A"] for r in ok if r["khung"] == kh and r["A"]["so_lenh"] >= 10]
    import statistics as st
    tho = [a["tb_lenh_tho_pct"] for a in x]; rong = [a["tb_lenh_pct"] for a in x]
    phi = [a["tb_lenh_tho_pct"] - a["tb_lenh_pct"] for a in x]
    print(kh, "n", len(x), "TB tho/lenh %", round(st.median(tho), 4), "phi/lenh %", round(st.median(phi), 4),
          "rong>0", f"{sum(1 for a in rong if a > 0)}/{len(x)}", "tho>0", f"{sum(1 for a in tho if a > 0)}/{len(x)}",
          "phi/|tho| trung vi", round(st.median([p / abs(t) for p, t in zip(phi, tho) if abs(t) > 1e-9]), 2))
S = [r for r in ok if P(r, pfmin=1.1) or P(r) or (("R2" in r) and P(r, "R2"))]
print("DS:")
for r in sorted(S, key=lambda r: r["A"].get("p") or 1):
    a = r["A"]; b = r.get("R2", {})
    print(f'{r["ma"][:70]} | {r["hold"]} | n{a["so_lenh"]} pfL{a["pf_lenh"]} pfB{a["pf_bar"]} sh{a["sharpe"]} tb{a["tb_lenh_pct"]} cagr{a["cagr_pct"]} dd{a["dd_pct"]} exp{a["phoi_nhiem"]} p{a.get("p")} prepo{r["p_repo"]} top10 {a.get("tap_trung_top10")} nam {a.get("nam_duong")} | R2 p{b.get("p")} pf{b.get("pf_lenh")} sh{b.get("sharpe")} | {r["vd_repo"]} {r["nguon"][:12]}')
