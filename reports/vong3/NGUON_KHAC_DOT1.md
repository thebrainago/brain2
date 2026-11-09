# Nguồn khác đợt 1 — Darwinex / FX Blue / Collective2 (+ Zulu / FF / SignalStart)

Giờ Việt Nam (Asia/Bangkok, UTC+7). **Không commit secrets.** ĐO: 09–10/11/2026.

Cổng 0: `nguon_khac_dot1_loc_phi.py` · Modules: `brain2/seeker_unblock/box/`.

REJECT nếu net_E≤0 hoặc edge/cost<1.5 hoặc CAGR_ff≤10%/DD_ff≥80%.

---

## 0. Nguồn

| Nguồn | Box CSV? | Endpoint | Nghẽn | Module |
|---|---|---|---|---|
| FX Blue | Có | `/users/{u}/csv` | private→login | `box/fxblue/` |
| Collective2 | Có | `/strategy/csv/{id}` | API v4 chết | `box/collective2/` |
| Darwinex | Series | `/invest/{T}` | filters 401 | `box/darwinex/` |
| ZuluTrade | Chưa | gateway OAuth | 401 | `box/zulutrade/` |
| Forex Factory | Một phần | curl_cffi + explorerapi | cần explorer id | `box/forexfactory/` |
| SignalStart | Chưa | search-signals | login | `box/signalstart/` |

---

## 1. Cổng 0 trade-level

| Nguồn | ID | n | năm | hang | cover% | net_E | e/c | CAGR_ff | DD_ff | ≥2y | Cổng 0 |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|:---:|---|
| fxblue | bullbear | 2608 | 2.647 | luoi | 86.6 | 0.155323 | 1.990 | 983.6 | 37.338 | Y | **PASS** |
| collective2 | 143135149 | 724 | 2.616 | don_le | 100.0 | 0.0147615 | 1.618 | 110.2 | 17.705 | Y | **PASS** |
| fxblue | Metaliq-Gold | 771 | 2.146 | luoi | 99.4 | 0.388313 | 1.743 | 236.2 | 9.634 | Y | **PASS** |
| fxblue | metaliq-gold | 771 | 2.146 | luoi | 99.4 | 0.388313 | 1.743 | 236.2 | 9.634 | Y | **PASS** |
| fxblue | free-forex-signal_USDJPY | 110 | 1.911 | don_le | 100.0 | 0.0144584 | 1.531 | 17.888 | 4.939 | n | **PASS** |
| fxblue | algo-trading | 834 | 1.696 | pyramid | 100.0 | 0.608101 | 3.230 | 283.2 | 36.037 | n | **PASS** |
| fxblue | happy-forex | 239 | 1.577 | luoi | 100.0 | 5.505 | 1.912 | 288.1 | 1.990 | n | **PASS** |
| fxblue | metaliq_gold | 651 | 1.473 | luoi | 99.2 | 0.395632 | 1.771 | 366.1 | 7.726 | n | **PASS** |
| fxblue | forex_alpha | 3901 | 1.203 | luoi | 63.0 | 0.00641537 | 2.487 | 2005.6 | 17.795 | n | **PASS** |
| fxblue | ibitebyt3s-10k-50r | 159 | 1.175 | pyramid | 95.6 | 16.955 | 5.142 | 17.797 | 7.790 | n | **PASS** |
| fxblue | algobreed-xauusd-2 | 360 | 0.506 | luoi | 100.0 | 1.906 | 4.298 | 6792.6 | 3.940 | n | **PASS** |
| fxblue | algobreed-xauusd-1 | 347 | 0.441 | luoi | 100.0 | 0.520706 | 1.956 | 69.466 | 19.917 | n | **PASS** |
| collective2 | 14614678 | 41 | 0.284 | don_le | 100.0 | 0.0361685 | 2.969 | 80.501 | 2.970 | n | **PASS** |
| fxblue | pepperstonexau | 376 | 0.22 | luoi | 100.0 | 2.795 | 5.333 | 10.108 | 24.199 | n | **PASS** |
| fxblue | 3propea_xauusd | 59 | 0.074 | don_le | 100.0 | 0.547824 | 1.753 | 630.7 | 4.920 | n | **PASS** |
| fxblue | divisagold | 16 | 0.022 | don_le | 100.0 | 1.237 | 3.153 | 138.1 | 2.010 | n | **PASS** |
| collective2 | 94987184 | 1059 | 10.185 | don_le | 100.0 | -0.20517 | -0.201429 | 87.037 | 4.958 | Y | **REJECT** |
| collective2 | 111340583 | 39 | 8.307 | don_le | 100.0 | -0.00748151 | 0.0979719 | -1.339 | 10.591 | Y | **REJECT** |
| collective2 | 116569489 | 213 | 7.501 | don_le | 100.0 | -0.0016457 | 0.181092 | 7.169 | 16.674 | Y | **REJECT** |
| fxblue | fx-ekspert-ma-demo | 6285 | 6.256 | luoi | 100.0 | -0.022281 | -0.712708 | — | — | Y | **REJECT** |
| fxblue | easyscalper | 2582 | 6.043 | don_le | 100.0 | -0.0055029 | 0.261958 | -25.134 | 84.557 | Y | **REJECT** |
| fxblue | EasyScalper | 2582 | 6.043 | don_le | 100.0 | -0.0055029 | 0.261958 | -25.134 | 84.557 | Y | **REJECT** |
| fxblue | forexlive | 4990 | 5.949 | luoi | 100.0 | -0.0105343 | -2.471 | 326.7 | 52.242 | Y | **REJECT** |
| collective2 | 134962085 | 265 | 5.592 | don_le | 89.8 | -0.00422078 | 0.971342 | 21.480 | 7.726 | Y | **REJECT** |
| collective2 | 128013249 | 56 | 5.442 | don_le | 100.0 | 0.0515021 | 13.007 | 9.165 | 1.990 | Y | **REJECT** |
| collective2 | 128801236 | 66 | 5.309 | don_le | 98.5 | -6.429 | -0.460978 | -5.017 | 23.910 | Y | **REJECT** |
| collective2 | 128454494 | 14 | 5.229 | don_le | 100.0 | 0.117373 | 2.617 | 0.754377 | 2.980 | Y | **REJECT** |
| fxblue | swingfx | 1319 | 5.204 | don_le | 100.0 | -0.000894412 | -0.60917 | 184.7 | 5.871 | Y | **REJECT** |
| fxblue | fx-ea | 78165 | 3.949 | luoi | 100.0 | -0.00392065 | 0.534283 | -100.0 | 100.0 | Y | **REJECT** |
| fxblue | trend-detector | 774 | 3.899 | luoi | 100.0 | -0.00728984 | -0.308399 | -0.987685 | 35.944 | Y | **REJECT** |
| collective2 | 137931431 | 280 | 3.824 | don_le | 100.0 | -0.000260805 | 0.702819 | 89.583 | 4.901 | Y | **REJECT** |
| fxblue | robot-forex | 12445 | 3.76 | luoi | 100.0 | -0.000341025 | -0.238461 | — | — | Y | **REJECT** |
| fxblue | icmarkets-demo | 19381 | 3.747 | luoi | 100.0 | 0.00772509 | 1.013 | -99.994 | 100.000 | Y | **REJECT** |
| collective2 | 140118626 | 36 | 3.252 | don_le | 100.0 | -0.00602721 | 0.404907 | -7.735 | 23.034 | Y | **REJECT** |
| fxblue | fibonacci | 543 | 3.096 | luoi | 100.0 | -0.249841 | -0.263356 | -35.069 | 75.950 | Y | **REJECT** |
| fxblue | night-hawk | 1745 | 2.838 | luoi | 100.0 | -0.00037093 | 0.487046 | 211.3 | 12.388 | Y | **REJECT** |
| fxblue | alphafx | 1165 | 2.756 | luoi | 100.0 | -0.0109458 | 0.0693729 | 402.8 | 14.149 | Y | **REJECT** |
| fxblue | liehtw | 5961 | 2.704 | luoi | 92.8 | 0.830938 | 1.320 | -99.639 | 100.000 | Y | **REJECT** |
| collective2 | 122467834 | 2432 | 2.597 | don_le | 100.0 | -0.00659252 | 0.435154 | 85.060 | 53.535 | Y | **REJECT** |
| fxblue | capitalgrowth | 6942 | 2.39 | luoi | 100.0 | -0.354022 | -0.0840313 | -99.637 | 100.000 | Y | **REJECT** |
| fxblue | forex_trend_detector | 429 | 2.367 | luoi | 100.0 | 0.000290728 | 2.140 | -4.600 | 32.058 | Y | **REJECT** |
| fxblue | smart-grid | 1967 | 2.285 | luoi | 100.0 | -0.00144429 | 0.631069 | 88.777 | 44.455 | Y | **REJECT** |
| fxblue | myforexpath1 | 1471 | 2.247 | luoi | 100.0 | -0.000296043 | 0.476211 | 1064.9 | 22.218 | Y | **REJECT** |
| fxblue | profitlab | 9706 | 2.175 | luoi | 100.0 | -0.233885 | -4.333 | 2895.2 | 90.284 | Y | **REJECT** |
| fxblue | supplydemand | 95 | 2.135 | luoi | 94.7 | -1.042 | 0.217974 | -17.261 | 37.753 | Y | **REJECT** |
| fxblue | trader_2 | 594 | 2.032 | luoi | 52.7 | 0.0110562 | 1.483 | -10.509 | 23.968 | Y | **REJECT** |
| fxblue | free-forex-signal | 1341 | 1.955 | don_le | 100.0 | 0.000814281 | 1.189 | 40.374 | 30.146 | n | **REJECT** |
| fxblue | myforexpath2 | 538 | 1.89 | luoi | 100.0 | -0.000402178 | -0.192175 | 212.5 | 12.257 | n | **REJECT** |
| fxblue | xmglobal | 5697 | 1.79 | luoi | 91.0 | -0.606025 | -0.21094 | -96.988 | 99.994 | n | **REJECT** |
| fxblue | trend_detector | 111 | 1.77 | luoi | 100.0 | -0.00160758 | -4.421 | -21.819 | 39.047 | n | **REJECT** |
| fxblue | free-forex-signal_GBPUSD | 51 | 1.673 | don_le | 100.0 | 0.000356876 | 2.330 | 6.633 | 3.048 | n | **REJECT** |
| fxblue | gold_edge | 991 | 1.61 | luoi | 100.0 | -0.000296342 | 0.0736827 | 1161.5 | 3.940 | n | **REJECT** |
| collective2 | 123920081 | 81 | 1.458 | don_le | 100.0 | -0.0127069 | 0.645697 | -6.248 | 11.645 | n | **REJECT** |
| fxblue | forex-live | 916 | 1.362 | pyramid | 99.6 | -0.0266461 | -0.531004 | 542.7 | 19.861 | n | **REJECT** |
| fxblue | fx-pro | 382 | 1.295 | pyramid | 93.5 | -2.227 | -1.928 | 76.026 | 11.406 | n | **REJECT** |
| collective2 | 117104490 | 1220 | 1.202 | don_le | 100.0 | 0.00060474 | 1.107 | 5058.0 | 7.809 | n | **REJECT** |
| fxblue | eatradingacademy | 62073 | 1.136 | luoi | 100.0 | -0.000324956 | -0.327263 | -100.0 | 100.0 | n | **REJECT** |
| fxblue | Public-stats | 7176 | 1.116 | luoi | 94.5 | 0.00241019 | 2.153 | -93.664 | 99.986 | n | **REJECT** |
| collective2 | 151472571 | 162 | 1.106 | don_le | 63.6 | -0.0475688 | -5.869 | -17.682 | 19.359 | n | **REJECT** |
| fxblue | ForexTrendDetector | 1758 | 1.091 | luoi | 99.9 | 7.6804e-05 | 1.241 | 188941.2 | 55.987 | n | **REJECT** |
| collective2 | 133743692 | 816 | 1.054 | don_le | 99.9 | -0.0040438 | 0.724133 | -91.281 | 93.468 | n | **REJECT** |
| fxblue | liehtw_XAUEUR | 92 | 1.044 | don_le | 100.0 | 2.163 | 21.101 | -2.328 | 11.618 | n | **REJECT** |
| collective2 | 24790189 | 615 | 1.002 | don_le | 100.0 | 0.00210072 | 2.018 | -75.297 | 77.389 | n | **REJECT** |
| fxblue | forex_edge_pro | 417 | 0.955 | pyramid | 100.0 | -0.000117665 | 0.553872 | 385.4 | 6.933 | n | **REJECT** |
| fxblue | dynascalp_demo | 588 | 0.902 | don_le | 100.0 | -0.03132 | -0.242525 | -72.668 | 87.498 | n | **REJECT** |
| collective2 | 151615755 | 698 | 0.813 | don_le | 100.0 | -7.01861e-05 | 0.747223 | -93.110 | 90.440 | n | **REJECT** |
| collective2 | 141924124 | 123 | 0.772 | don_le | 100.0 | -0.0443473 | 0.312302 | 230.9 | 5.908 | n | **REJECT** |
| collective2 | 89703872 | 119 | 0.749 | don_le | 100.0 | -0.0157771 | -3.555 | 118.0 | 9.598 | n | **REJECT** |
| fxblue | gold-pips | 200 | 0.748 | luoi | 100.0 | -15.777 | -2.247 | 59.704 | 12.344 | n | **REJECT** |
| fxblue | forex-gold-investor | 156 | 0.698 | don_le | 100.0 | -1.177 | 0.115276 | -11.817 | 15.950 | n | **REJECT** |
| fxblue | gold-system | 313 | 0.693 | don_le | 100.0 | -0.000233011 | 0.217519 | -45.892 | 36.588 | n | **REJECT** |
| fxblue | nsr_gold | 348 | 0.687 | luoi | 100.0 | -1.388 | -0.353836 | 443.0 | 10.466 | n | **REJECT** |
| collective2 | 154330462 | 20 | 0.674 | don_le | 100.0 | -0.000304878 | -0.294632 | -8.649 | 5.918 | n | **REJECT** |
| fxblue | forextraded4 | 2098 | 0.614 | luoi | 100.0 | -0.564567 | 0.0166708 | 51.561 | 77.753 | n | **REJECT** |
| collective2 | 79862763 | 11 | 0.612 | don_le | 100.0 | -0.00462825 | -1.505 | -1.708 | 3.950 | n | **REJECT** |
| fxblue | gpbootcamp | 83960 | 0.561 | luoi | 97.3 | -0.0115521 | -0.183825 | -100.0 | 100.0 | n | **REJECT** |
| fxblue | myforexpath | 73 | 0.508 | luoi | 100.0 | -0.00580848 | -2.823 | 13.954 | 11.362 | n | **REJECT** |
| collective2 | 125545530 | 403 | 0.408 | don_le | 100.0 | -0.0104386 | -1.396 | -99.116 | 85.632 | n | **REJECT** |
| fxblue | gold-investor | 96 | 0.363 | pyramid | 100.0 | -1.477 | -0.203619 | -20.822 | 10.645 | n | **REJECT** |
| collective2 | 156716997 | 48 | 0.336 | don_le | 100.0 | -0.00420031 | 0.138099 | 41.923 | 2.029 | n | **REJECT** |
| fxblue | pow-50883896 | 13990 | 0.332 | luoi | 100.0 | -0.600505 | -0.0291463 | -100.000 | 99.998 | n | **REJECT** |
| collective2 | 126172384 | 135 | 0.306 | don_le | 100.0 | -0.00748129 | 0.123759 | 82.020 | 6.012 | n | **REJECT** |
| fxblue | MT5GoldEA | 97079 | 0.29 | luoi | 99.0 | -0.849726 | -0.489032 | -100.0 | 100.0 | n | **REJECT** |
| fxblue | mt5goldea | 97079 | 0.29 | luoi | 99.0 | -0.849726 | -0.489032 | -100.0 | 100.0 | n | **REJECT** |
| fxblue | gold_scalping | 6003 | 0.275 | luoi | 100.0 | -0.712728 | -0.186226 | -100.0 | 100.000 | n | **REJECT** |
| collective2 | 139585165 | 266 | 0.271 | don_le | 98.1 | 0.0219345 | 2.566 | -79.016 | 49.869 | n | **REJECT** |
| fxblue | Seagull_EA | 156 | 0.263 | luoi | 100.0 | -0.000502543 | -0.225594 | 1010.1 | 5.852 | n | **REJECT** |
| fxblue | ruby-forex-ea | 43 | 0.182 | don_le | 100.0 | -0.000336648 | -0.450344 | 336.4 | 1.990 | n | **REJECT** |
| fxblue | xauusd11 | 209 | 0.112 | luoi | 100.0 | -2.017 | -2.595 | 1348.8 | 12.362 | n | **REJECT** |
| fxblue | robots-forex-live | 91 | 0.08 | luoi | 100.0 | -0.00100716 | -3.273 | 276.6 | 7.735 | n | **REJECT** |
| fxblue | goldscalping_demo | 29 | 0.008 | luoi | 100.0 | 0.338897 | 1.494 | 252312970475.6 | 2.970 | n | **REJECT** |
| collective2 | 131145247 | 774 | 6.136 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| collective2 | 132148218 | 501 | 5.988 | don_le | 0.2 | — | — | -0.167709 | 1.000 | Y | **CHUA_DO** |
| collective2 | 143110798 | 392 | 3.822 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| collective2 | 114146885 | 7 | 3.773 | don_le | 28.6 | — | — | -0.00265079 | 1.000 | Y | **CHUA_DO** |
| collective2 | 146006468 | 1022 | 3.092 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| collective2 | 147255777 | 5 | 2.751 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| collective2 | 146455121 | 21 | 2.419 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| fxblue | mt5live | 1377 | 2.313 | pyramid | 33.8 | — | — | -6.816 | 25.659 | Y | **CHUA_DO** |
| collective2 | 149476882 | 225 | 2.111 | don_le | 0.0 | — | — | — | — | Y | **CHUA_DO** |
| collective2 | 150377786 | 826 | 1.876 | don_le | 0.1 | — | — | -0.534293 | 1.000 | n | **CHUA_DO** |
| collective2 | 150373429 | 175 | 1.845 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 150759166 | 767 | 1.752 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 150565426 | 84 | 1.588 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 151330723 | 52 | 1.586 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 152305186 | 37 | 1.31 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 152305234 | 37 | 1.31 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 153204518 | 230 | 1.016 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 153432780 | 244 | 0.974 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| fxblue | forex_gold | 1192 | 0.922 | luoi | 7.7 | — | — | 53.577 | 7.818 | n | **CHUA_DO** |
| collective2 | 152169281 | 20 | 0.829 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 149244504 | 5 | 0.513 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 148093242 | 7 | 0.186 | don_le | 100.0 | — | — | -15.072 | 4.901 | n | **CHUA_DO** |
| collective2 | 109650444 | 4 | 0.098 | don_le | 100.0 | — | — | -18.699 | 2.970 | n | **CHUA_DO** |
| collective2 | 152701320 | 34 | 0.093 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 119679215 | 6 | 0.074 | don_le | 100.0 | — | — | 71.558 | 1.000 | n | **CHUA_DO** |
| collective2 | 152221526 | 1 | 0.045 | don_le | 0.0 | — | — | — | — | n | **CHUA_DO** |
| fxblue | DynaScalp | 1155 | 0.031 | luoi | 0.0 | — | — | — | — | n | **CHUA_DO** |
| collective2 | 157135749 | 8 | 0.019 | don_le | 100.0 | — | — | -64.908 | 3.940 | n | **CHUA_DO** |
| fxblue | fundednext | 525 | 0.007 | luoi | 47.8 | — | — | 3317198.8 | 26.792 | n | **CHUA_DO** |
| collective2 | 151319237 | — | — | — | — | — | — | — | — | n | **CHUA_DO** |
| collective2 | 98549641 | — | — | — | — | — | — | — | — | n | **CHUA_DO** |

### Verdict

- **PASS ≥2y toàn TK: 4** — Metaliq-Gold (luoi), bullbear (luoi), 143135149 (don_le), metaliq-gold (luoi)
- **don_le ≥2y toàn TK: 1** — 143135149
- **pyramid ≥2y toàn TK: 0** — —
- PASS <2y: 12
- Gated unique: **122** + Darwinex **24**

**Mã con đáng chú ý:** `122467834/EURUSD` (Tendency) don_le PASS Cổng 0 y=2.57 e/c≈1.68 CAGR≈41% DD≈12% — Cổng S fade≥60% nhưng V1 WF REJECT. Xem `NGUON_KHAC_DOT1_CONG_S.md`.

**RC105:** Cổng S match≥70% (MA200/breakout) nhưng V1 WF REJECT trên 3 majors.

Hunt sau a09a048a: **không** thêm don_le/pyramid PASS ≥2y toàn TK.

---

## 2. Darwinex series

| Ticker | năm | ret_2y% | DD_2y% | CAGR≈ | ret_ann |
|---|---:|---:|---:|---:|---:|
| EUX | 7.1 | 62.041 | -9.510 | 27.3 | 8.43 |
| HLB | 2.6 | 58.574 | -12.014 | 25.93 | 21.3 |
| LSP | 3.17 | 62.161 | -12.624 | 27.34 | 26.14 |
| OSC | 4.97 | 57.586 | -19.631 | 25.53 | 12.79 |
| RMXR | 2.43 | 57.276 | -21.390 | 25.41 | 20.98 |
| VNZX | 2.81 | 60.366 | -11.092 | 26.64 | 14.5 |
| WMH | 2.88 | 73.148 | -10.887 | 31.59 | 21.23 |
| XKA | 2.01 | 63.230 | -6.085 | 27.76 | 28.2 |
| XQK | 2.01 | 59.390 | -10.778 | 26.25 | 21.96 |
| XUV | 6.49 | 67.875 | -6.849 | 29.57 | 7.95 |
| YHD | 2.2 | 58.820 | -13.673 | 26.02 | 25.25 |
| YPIU | 2.46 | 60.153 | -14.472 | 26.55 | 17.6 |
| EITZ | 2.24 | 45.860 | -5.281 | 20.77 | 22.05 |
| SEQV | 2.15 | 33.960 | -4.434 | 15.74 | 17.28 |
| MLTY | 2.18 | 57.100 | -7.711 | 25.34 | 26.87 |
| PHI | 11.76 | 49.089 | -6.683 | 22.1 | 7.22 |
| QBG | 2.63 | 54.922 | -7.891 | 24.47 | 27.03 |
| KEPU | 2.07 | 47.300 | -6.992 | 21.37 | 18.25 |
| SPBB | 2.14 | 40.970 | -6.431 | 18.73 | 21.52 |
| WDIH | 2.14 | 49.250 | -8.214 | 22.17 | 22.43 |
| SVRX | 3.18 | 37.786 | -6.388 | 17.38 | 12.54 |
| UYF | 2.99 | 25.403 | -4.357 | 11.98 | 12.6 |
| BDE | 6.78 | 43.205 | -7.575 | 19.67 | 9.41 |
| MRST | 4.16 | 32.464 | -5.723 | 15.09 | 17.15 |

---

## 3. Artifact

`nguon_khac/` · `NGUON_KHAC_DOT1*.md` · `NGUON_KHAC_RC105_*.json` · `NGUON_KHAC_TENDENCY_EURUSD_CONG_S_V1.json` · `NGUON_KHAC_DONLE_SUBSETS.json` · `seeker_unblock/box/` · `reports/vong3/`

As-of: 2026-11-09 23:59:20 Asia/Bangkok.