# bt_3m v2 — Improvement pass (28/11/2026 ~02:40 UTC+7) — PYTHON CONSERVATIVE SIMULATION, NOT MT5
Engine unchanged from XSD-10 (adverse-first, no DCA+close in same bar, gap-through open fills, XM M1 spread + 0.5x slip, XM swap, stop-out 50% margin).
Window 2026-08-20 -> 2026-11-26 UTC. US500 cap 10k; Gold cap 30k (10k + 20k top-up; no top-up used by any finalist).
Mirror = same data reflected (US500 +6%, Gold +21% rally), aggressor sides swapped. Gap shock = ±20% at max exposure, DD vs cap.
Broker costs Exness = ESTIMATES (US500 std 0.90 / raw 0.50 pts all-in; Gold std 0.30 / raw 0.12 USD all-in), XM = real spread column.
Note: basket TP is a fixed USD target per lot, so spread changes timing/number of baskets and floating DD more than per-basket profit.

## US500 (62,400 configs around c1; 7,364 pass grid filters)
Filters: net>0, all 3 months >0, spread×3+slip1 >0, mirror net>0 & DD<25%, ±20% gap DD<70%, no stop-out, placebo ≥95th pct.
| | entry | mgmt | net | DD | F1/F2/F3 | spr×3 | mirror | gap+20/−20 | placebo | ExStd / ExRaw (×2) | no-prune | DSR(v2/all) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v2_c1 | sw_fade z>1.8, ADX>20, both, LD/NY | 2.0 lot ×1, gap 60 ×1.4, max 3, TP 6, prune 1.5, hedge 0.5× @90, no compounding | +1,677.6 | 3.86% | 456/632/590 | +557 | +1,594 / 3.96% | 66% / 63% | 100th (med +706) | +1,619 / +1,677 (+370 / +1,469) | identical (prune never fires) | 0.06 / 0.03 |
| v2_c2 | same signal | 1.0 ×1, gap 45 ×1.4, max 3, TP 6, prune 1.5, hedge 0.75× @180, compounding | +936.1 | 1.88% | 254/328/354 | +157 | +910 / 1.88% | 50% / 33% | 100th | +929 / +936 (+88 / +836) | identical | 0.15 / 0.09 |
| v2_c3 | same signal | 1.0 ×1, gap 45 ×1.4, max 3, TP 6, prune 1.2, hedge 0.5× @180 | +899.9 | 1.79% | 252/316/331 | +170 | +876 / 1.83% | 48% / 32% | 100th | +894 / +900 (+102 / +808) | identical | 0.15 / 0.08 |
Original c1: XM +874.3 / ExStd +874.3 / ExRaw +874.0; no-prune +874.3 (prune never triggered) ⇒ BRAIN_XuLiLenh without prune should be comparable.
Walk-forward inside the robust set: pick on F1 → F2 +311, F3 +7; pick on F1+F2 → F3 +195. Unrestricted pick on F1 → F3 −458 (why filters matter).
Lessons: z 1.8 > 2.0; ADX>20 best; TP 6 best inside filters; bigger lot (2.5) breaks the ±20% gap limit; prune/hedge rarely trigger with max 3 layers.

## Gold (414,720 two-sided configs; 124,734 pass grid filters)
Filters: net>0 & DD<60% on BOTH original (−21%) and mirror (+21%), spread×2 >0, worst month > −2% of 30k, no stop-out, placebo ≥95th pct.
| | entry | mgmt | net | DD | F1/F2/F3 | spr×2 | mirror | gap+20/−20 | placebo | ExStd / ExRaw (×2) | no-prune | delay 2 bars | DSR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v2_c1 | vwap_rev k2 (|dev|>3 ATR), ADX>20, both, all hours | 0.03 ×1, gap 6 ×1.4, max 4, TP 3, no trim/prune/hedge | +4,900 | 6.9% | 2132/881/1887 | +4,934 | +4,556 / 7.1% | 43% / 37% | 95th (med −8,235) | +4,882 / +5,289 (+2,525 / +4,980) | same | +2,446 | ~0 |
| v2_c2 | vwap_rev k1, no ADX, LD/NY | 0.03 ×1.3, gap 12, max 4, TP 3, prune 1.5, hedge 1.0× @36 | +4,607 | 7.3% | 2027/821/1759 | +3,781 | +4,366 / 13.6% | 54% / 65% | 95th | +4,611 / +4,829 (−11,772 / +4,513) | −2,373 (prune essential) | +4,125 | ~0 |
| v2_c3 | sw_fade z>1.8, ADX>20, LD/NY | 0.03 ×1.3, gap 6, max 4, TP 3, prune 1.5, hedge 0.5× @18 | +3,160 | 2.2% | 1682/532/946 | +2,690 | +3,211 / 2.2% | 53% / 45% | 95th (mirror 90th) | +2,521 / +3,141 (+2,055 / +2,539) | +2,804 | +2,371 | ~0 |
Walk-forward inside the robust set: pick on F1 → F2 +66, F3 −47; pick on F1+F2 → F3 −335 (−1.1% of 30k). Unrestricted pick on F1 → F3 −3,099, mirror −2,039.
Caveats: 30% of all gold configs pass the grid filters (no-SL baskets look good on 3 months); placebo only 19/20 beaten; DSR ≈ 0;
c2 depends on prune and blows up on Exness Std ×2 costs. c3 is the most robust gold candidate (lowest DD, survives costs, mirror and no-prune).
Files: mt5_ready_v2/{US500,XAU}_v2_top3.json, *_v2_c1..c3_entries.csv (XM server time = NY+7), v2_{US500,XAU}_finalists.csv, code/v2.py, code/v2_final.py.
