#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mô phỏng Python logic thống kê của indicator Gann Square of 9 (gann_sq9_indicator_fixed.pine).

Mức Sq9:  L = (sqrt(neo*k) ± góc/180)^2 / k   (k = 1 cho vàng và S&P 500)
Quy trình cho từng mức (mỗi mức sống độc lập, không bị bộ neo sau xoá):
  - Tạo tại nến đóng t (nến xác nhận neo). Theo dõi touch ở các nến t+1 .. t+X.
  - Touch: low <= L+tol và high >= L-tol. tol = tolATR*ATR(14) (hoặc %*L).
  - Hướng tiếp cận: close[nến trước] >= L -> từ trên (test hỗ trợ), ngược lại test kháng cự.
  - Sau touch (tính cả nến chạm): nếu close vượt qua L∓tol -> PHÁ.
    Nếu giữ đủ M nến -> HỖ TRỢ / KHÁNG CỰ ("giữ"); và nếu biên độ bật ngược lớn nhất
    (close nến chạm, high/low các nến sau) >= rev*ATR(lúc chạm) -> thêm 1 ĐIỂM HỒI.
  - Mức chưa xong cửa sổ khi hết dữ liệu bị loại khỏi thống kê.

Nhóm đối chứng (baseline):
  - "mid": các góc lệch nửa bước 22.5°, 67.5°, ..., 337.5° (cùng công thức).
  - "rand": góc ngẫu nhiên đều trong (0°, 382.5°), R mức trên + R mức dưới mỗi bộ neo.
    Kỳ vọng "ngẫu nhiên" cho góc A = trung bình các mức rand có góc trong A ± 22.5°
    (cùng khoảng cách, chỉ khác pha) -> so sánh công bằng theo khoảng cách.
Chế độ --legacy mô phỏng bản gốc: mọi mức đang theo dõi bị huỷ khi có bộ neo mới.
"""
import argparse, os
import numpy as np, pandas as pd

ANGLES = np.arange(45.0, 361.0, 45.0)
MID = ANGLES - 22.5


def atr_rma(h, l, c, n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    out = np.full(len(c), np.nan)
    if len(c) < n: return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def sq9(anchor, ang, side, k=1.0):
    r = np.sqrt(anchor * k) + side * ang / 180.0
    return np.where(r > 0, r * r / k, np.nan)


def anchor_events(df, kind, intraday, left=10, right=5, fut=False):
    """Trả về list (bar_tạo, giá_neo) – chỉ dùng thông tin đã biết tại nến tạo."""
    o, h, l, c = (df[x].values for x in ("Open", "High", "Low", "Close"))
    n = len(df); ev = []
    if kind in ("pdc", "dopen"):
        if intraday:
            idx = df.index.tz_convert("America/New_York")
            day = (idx + pd.Timedelta(hours=6)).date if fut else idx.date   # CME: phiên bắt đầu 18:00 ET
            day = np.array(day)
            newday = np.r_[True, day[1:] != day[:-1]]
            starts = np.flatnonzero(newday)
            for j, s in enumerate(starts):
                if kind == "pdc":
                    if j == 0: continue
                    ev.append((s, c[s - 1]))           # close nến cuối ngày trước
                else:
                    ev.append((s, o[s]))               # open nến đầu ngày
        else:
            for t in range(1, n):
                ev.append((t, c[t - 1] if kind == "pdc" else o[t]))
    else:
        src = h if kind == "swh" else l
        for t in range(left + right, n):
            p = t - right
            w = src[p - left:t + 1]; v = src[p]
            if kind == "swh":
                ok = v >= w.max() and v > src[p - left:p].max()
            else:
                ok = v <= w.min() and v < src[p - left:p].min()
            if ok: ev.append((t, v))
    # chỉ tạo bộ mới khi giá neo thay đổi (giống Pine: anchor != curAnchor)
    out, last = [], None
    for t, a in ev:
        if np.isfinite(a) and a != last:
            out.append((t, a)); last = a
    return out


def evaluate(df, events, X=20, M=5, tol_atr=0.2, tol_pct=None, rev=1.0, R=6, seed=1, legacy=False):
    o, h, l, c = (df[x].values.astype(float) for x in ("Open", "High", "Low", "Close"))
    atr = atr_rma(h, l, c, 14)
    n = len(c); rng = np.random.default_rng(seed)
    rows = []
    for e, (t, a) in enumerate(events):
        if not np.isfinite(atr[t]): continue
        end = t + X                                      # nến cuối cửa sổ touch
        cut = 10**12
        if legacy and e + 1 < len(events):
            cut = events[e + 1][0]                       # bản gốc: bộ mới huỷ bộ cũ (sau khi xử lý nến đó)
            end = min(end, cut)
        if t + X + M >= n: break                         # thiếu dữ liệu -> bỏ
        grp, angs = [], []
        for name, arr in (("sq9", ANGLES), ("mid", MID)):
            for s in (1, -1):
                grp += [name] * len(arr); angs += list(arr * s)
        ra = rng.uniform(0.0, 382.5, 2 * R)
        grp += ["rand"] * (2 * R); angs += list(ra * np.r_[np.ones(R), -np.ones(R)])
        angs = np.array(angs)
        lv = sq9(a, np.abs(angs), np.sign(angs))
        for g, ang, L in zip(grp, angs, lv):
            if not np.isfinite(L): continue
            rec = dict(bar=t, anchor=a, group=g, angle=abs(ang), side=int(np.sign(ang)),
                       dist_atr=abs(L - a) / atr[t], touched=0, hold=0, brk=0, sup=0, res=0, rev=0, unresolved=0)
            tb = None
            for i in range(t + 1, end + 1):
                tol = L * tol_pct / 100 if tol_pct else tol_atr * atr[i]
                if l[i] <= L + tol and h[i] >= L - tol:
                    tb = i; break
            if tb is not None:
                rec["touched"] = 1
                d = 1 if c[tb - 1] >= L else -1
                ext, at = 0.0, atr[tb]; done = False
                hold_end = min(tb + M, n - 1, cut)
                for i in range(tb, hold_end + 1):
                    tol = L * tol_pct / 100 if tol_pct else tol_atr * atr[i]
                    if i == tb: x = (c[i] - L) * d
                    else: x = (h[i] - L) if d == 1 else (L - l[i])
                    ext = max(ext, x)
                    if (d == 1 and c[i] < L - tol) or (d == -1 and c[i] > L + tol):
                        rec["brk"] = 1; done = True; break
                    if i - tb >= M:
                        rec["hold"] = 1; rec["sup" if d == 1 else "res"] = 1
                        rec["rev"] = int(ext >= rev * at); done = True; break
                if not done: rec["unresolved"] = 1
            rows.append(rec)
    return pd.DataFrame(rows)


def summarize(d):
    g = d.groupby(["group", "angle"]) if "angle" in d else d
    s = g.agg(created=("touched", "size"), touched=("touched", "sum"), sup=("sup", "sum"),
              res=("res", "sum"), rev=("rev", "sum"), brk=("brk", "sum"), dist_atr=("dist_atr", "median"))
    return s


def rates(s):
    s = s.copy()
    s["touch%"] = 100 * s.touched / s.created
    s["hold%"] = 100 * (s.sup + s.res) / (s.sup + s.res + s.brk).replace(0, np.nan)
    s["rev%touch"] = 100 * s.rev / s.touched.replace(0, np.nan)
    return s


def compare(df_lv):
    """Bảng theo góc: Sq9 vs kỳ vọng ngẫu nhiên cùng khoảng cách (rand trong ±22.5°)."""
    out = []
    sq = df_lv[df_lv.group == "sq9"]; rd = df_lv[df_lv.group == "rand"]; md = df_lv[df_lv.group == "mid"]
    for A in ANGLES:
        a = sq[sq.angle == A]; r = rd[(rd.angle - A).abs() <= 22.5]
        def st(x):
            t = x.touched.sum(); hb = x.hold.sum() + x.brk.sum()
            return (len(x), 100 * x.touched.mean() if len(x) else np.nan,
                    100 * x.hold.sum() / hb if hb else np.nan,
                    100 * x.rev.sum() / t if t else np.nan, t)
        n1, t1, h1, v1, tt = st(a); n2, t2, h2, v2, _ = st(r)
        # z-test cho tỷ lệ giữ (hold) Sq9 vs rand
        hb1 = a.hold.sum() + a.brk.sum(); hb2 = r.hold.sum() + r.brk.sum()
        z = np.nan
        if hb1 and hb2:
            p1, p2 = a.hold.sum() / hb1, r.hold.sum() / hb2; p = (a.hold.sum() + r.hold.sum()) / (hb1 + hb2)
            se = np.sqrt(p * (1 - p) * (1 / hb1 + 1 / hb2)); z = (p1 - p2) / se if se > 0 else np.nan
        out.append(dict(angle=int(A), n=n1, touch=t1, touch_rand=t2, hold=h1, hold_rand=h2, z_hold=z,
                        rev=v1, rev_rand=v2, sup=int(a.sup.sum()), res=int(a.res.sum()), revN=int(a.rev.sum())))
    tot = {}
    for name, x in (("sq9", sq), ("mid", md), ("rand", rd[rd.angle <= 382.5])):
        hb = x.hold.sum() + x.brk.sum()
        tot[name] = dict(n=len(x), touch=100 * x.touched.mean(), hold=100 * x.hold.sum() / hb,
                         rev=100 * x.rev.sum() / max(x.touched.sum(), 1))
    return pd.DataFrame(out), tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--X", type=int, default=20); ap.add_argument("--M", type=int, default=5)
    ap.add_argument("--tol", type=float, default=0.2); ap.add_argument("--rev", type=float, default=1.0)
    ap.add_argument("--legacy", action="store_true"); ap.add_argument("--out", default="results")
    ap.add_argument("--daily_from", default="2000-01-01")
    args = ap.parse_args()
    base = os.path.dirname(os.path.abspath(__file__)); od = os.path.join(base, args.out); os.makedirs(od, exist_ok=True)
    sets = [("GC=F", "1h", True, True), ("ES=F", "1h", True, True), ("^GSPC", "1h", True, False),
            ("GC=F", "1d", False, True), ("ES=F", "1d", False, True), ("^GSPC", "1d", False, False)]
    allc, tots, levels = [], [], []
    for tk, iv, intra, fut in sets:
        f = os.path.join(base, f"data_{tk.replace('=','').replace('^','')}_{iv}.pkl")
        df = pd.read_pickle(f).dropna(subset=["Open", "High", "Low", "Close"])
        if not intra: df = df[df.index >= args.daily_from]
        for kind in ("pdc", "dopen", "swh", "swl"):
            ev = anchor_events(df, kind, intra, fut=fut)
            lv = evaluate(df, ev, X=args.X, M=args.M, tol_atr=args.tol, rev=args.rev, legacy=args.legacy)
            lv["ticker"], lv["tf"], lv["anchor_type"] = tk, iv, kind
            levels.append(lv)
            cmp, tot = compare(lv)
            cmp.insert(0, "anchor_type", kind); cmp.insert(0, "tf", iv); cmp.insert(0, "ticker", tk)
            allc.append(cmp)
            for g, v in tot.items():
                tots.append(dict(ticker=tk, tf=iv, anchor_type=kind, group=g, sets=len(ev), **v))
            print(tk, iv, kind, "sets", len(ev), {g: {k: round(x, 1) for k, x in v.items()} for g, v in tot.items()}, flush=True)
    C = pd.concat(allc); T = pd.DataFrame(tots); Lv = pd.concat(levels)
    C.round(2).to_csv(os.path.join(od, "per_angle.csv"), index=False)
    T.round(2).to_csv(os.path.join(od, "totals.csv"), index=False)
    Lv.to_csv(os.path.join(od, "levels.csv.gz"), index=False)


if __name__ == "__main__":
    main()
