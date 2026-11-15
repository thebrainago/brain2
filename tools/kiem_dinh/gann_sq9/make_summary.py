# Tạo bảng tổng hợp gộp: Sq9 vs đối chứng ngẫu nhiên cùng khoảng cách (rand trong ±22.5° quanh mỗi góc)
import pandas as pd, numpy as np
L = pd.read_csv("results/levels.csv.gz")
rows = []
for (tk, tf, an), d in L.groupby(["ticker", "tf", "anchor_type"], sort=False):
    sq = d[d.group == "sq9"]; rd = d[d.group == "rand"]
    eT = eH = eV = 0.0; nT = nHB = nTch = 0
    for A in range(45, 361, 45):
        a = sq[sq.angle == A]; r = rd[(rd.angle - A).abs() <= 22.5]
        rhb = r.hold.sum() + r.brk.sum()
        eT += a.shape[0] * r.touched.mean()
        hb = a.hold.sum() + a.brk.sum()
        if rhb: eH += hb * r.hold.sum() / rhb
        if r.touched.sum(): eV += a.touched.sum() * r.rev.sum() / r.touched.sum()
        nT += a.shape[0]; nHB += hb; nTch += a.touched.sum()
    hold = sq.hold.sum()
    p, p0 = hold / nHB, eH / nHB
    z = (p - p0) / np.sqrt(p0 * (1 - p0) / nHB)
    rows.append(dict(ticker=tk, tf=tf, anchor=an, levels=nT, touch=100 * sq.touched.sum() / nT, touch_rand=100 * eT / nT,
                     hold=100 * p, hold_rand=100 * p0, z_hold=z,
                     rev=100 * sq.rev.sum() / nTch, rev_rand=100 * eV / nTch,
                     sup=int(sq.sup.sum()), res=int(sq.res.sum()), brk=int(sq.brk.sum())))
P = pd.DataFrame(rows).round(1)
P.to_csv("results/pooled_vs_random.csv", index=False)
print(P.to_string(index=False))
# Theo góc, gộp mọi mã/khung/neo
C = pd.read_csv("results/per_angle.csv")
g = []
for A in range(45, 361, 45):
    a = L[(L.group == "sq9") & (L.angle == A)]; r = L[(L.group == "rand") & ((L.angle - A).abs() <= 22.5)]
    f = lambda x: (100 * x.touched.mean(), 100 * x.hold.sum() / max(x.hold.sum() + x.brk.sum(), 1), 100 * x.rev.sum() / max(x.touched.sum(), 1))
    t1, h1, v1 = f(a); t2, h2, v2 = f(r)
    g.append(dict(angle=A, touch=t1, touch_rand=t2, hold=h1, hold_rand=h2, rev=v1, rev_rand=v2, touches=int(a.touched.sum())))
G = pd.DataFrame(g).round(1); G.to_csv("results/by_angle_all.csv", index=False); print(G.to_string(index=False))
print("z>1.96:", (C.z_hold > 1.96).sum(), " z<-1.96:", (C.z_hold < -1.96).sum(), " / ", len(C))
