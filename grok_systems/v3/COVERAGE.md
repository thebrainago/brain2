## COVERAGE — họ tín hiệu × {fade, momentum} × {basket, scalp SL/TP}
(số cấu hình đã chạy / số cấu hình dương cả A và B; "CHƯA" = chưa thử; cập nhật tự động bởi `code/cov.py`)

| Họ (family) | Fade·basket | Mom·basket | Fade·scalp | Mom·scalp |
|---|---|---|---|---|
| Sweep (sw z) | 1096 cfg / 854 A&B+ | 1096 cfg / 507 A&B+ | 12114 cfg / 1157 A&B+ | 6057 cfg / 79 A&B+ |
| Delta z (dz) | 2560 cfg / 1617 A&B+ | 2048 cfg / 1391 A&B+ | 16614 cfg / 1060 A&B+ | 14146 cfg / 675 A&B+ |
| Big prints / whale (g1–g3) | 2916 cfg / 1509 A&B+ | 2916 cfg / 1791 A&B+ | 27375 cfg / 1321 A&B+ | 26835 cfg / 3443 A&B+ |
| CVD divergence / CVD lead | 1224 cfg / 628 A&B+ | 72 cfg / 35 A&B+ | 9869 cfg / 259 A&B+ | 960 cfg / 90 A&B+ |
| Absorption | 2504 cfg / 1376 A&B+ | 2504 cfg / 1390 A&B+ | 16776 cfg / 565 A&B+ | 16391 cfg / 1042 A&B+ |
| Imbalance / stacked | 2904 cfg / 1653 A&B+ | 2904 cfg / 1136 A&B+ | 23532 cfg / 848 A&B+ | 19182 cfg / 545 A&B+ |
| VWAP (z, ATR, cross, flow) | 1096 cfg / 533 A&B+ | 244 cfg / 183 A&B+ | 15406 cfg / 383 A&B+ | 1412 cfg / 44 A&B+ |
| Volume profile POC/VAH/VAL/naked POC/80% rule | 590 cfg / 325 A&B+ | 134 cfg / 71 A&B+ | 8861 cfg / 229 A&B+ | 640 cfg / 31 A&B+ |
| Opening/session range (NY OR, IB, London OR, COMEX OR, Asia) | 425 cfg / 241 A&B+ | 1253 cfg / 824 A&B+ | 5018 cfg / 282 A&B+ | 10120 cfg / 735 A&B+ |
| Prior day/week levels, NR day | 748 cfg / 402 A&B+ | 200 cfg / 162 A&B+ | 10540 cfg / 452 A&B+ | 1638 cfg / 136 A&B+ |
| Round numbers | 72 cfg / 41 A&B+ | 72 cfg / 40 A&B+ | 960 cfg / 0 A&B+ | 960 cfg / 1 A&B+ |
| Cross-asset lead-lag ES↔GC | 2368 cfg / 442 A&B+ | 2424 cfg / 402 A&B+ | 14787 cfg / 843 A&B+ | 14653 cfg / 483 A&B+ |
| Futures return / basis | 252 cfg / 118 A&B+ | 252 cfg / 87 A&B+ | 3360 cfg / 197 A&B+ | 3360 cfg / 41 A&B+ |
| Time-of-day anchors / news | 141 cfg / 51 A&B+ | 141 cfg / 113 A&B+ | 1640 cfg / 114 A&B+ | 1640 cfg / 251 A&B+ |
| Volatility regime: squeeze/expansion/climax | 177 cfg / 84 A&B+ | 177 cfg / 83 A&B+ | 2360 cfg / 184 A&B+ | 2360 cfg / 17 A&B+ |
| Trend pullback (EMA/VWAP) | CHƯA | 167 cfg / 95 A&B+ | CHƯA | 4815 cfg / 712 A&B+ |
| Gaps (overnight / weekend) | CHƯA | CHƯA | CHƯA | CHƯA |
| IBS (prior-day close position) | 120 cfg / 109 A&B+ | CHƯA | 944 cfg / 42 A&B+ | CHƯA |
| 60-bar high/low break/sweep | 36 cfg / 12 A&B+ | 36 cfg / 15 A&B+ | 480 cfg / 0 A&B+ | 480 cfg / 0 A&B+ |
| Placebo (control) | 512 cfg / 272 A&B+ | CHƯA | 2560 cfg / 50 A&B+ | CHƯA |
| Other | CHƯA | CHƯA | CHƯA | CHƯA |

Không thể thử (thiếu dữ liệu): lead-lag NQ/SI/CL (KHÔNG CÓ dữ liệu), GEX / gamma flip / call-put walls (KHÔNG CÓ lịch sử), MBO/queue position (KHÔNG CÓ).
Tổng cấu hình đã chạy: basket 36,381, scalp 298,845 (gồm cả 2 tài sản).