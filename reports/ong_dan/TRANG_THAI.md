# Ống dẫn: trạng thái (tự sinh bởi `python ong_dan.py bao_cao`)

Mọi số là **MÔ PHỎNG** Python ở **lot thật** (ký quỹ, stop-out, `nhan/tai_khoan.chay_tk`). Phí: **PHÍ TẠM** (hồ sơ XM đã đo trong `config/chi_phi_do.json`) cho tới khi máy nhà đo `reports/phi_san/`. Ngưỡng lọc Python: sụt giảm < 65 %% và lãi > 15 %%/năm; chuẩn cuối 80/10 (đo ở MT5). OOS chỉ là nhãn.

## Đếm theo bước

```json
{
 "doc_mt5": {
  "CHUA_DO_DUOC": 3,
  "DAT_CUOI": 33,
  "TRUOT_CUOI": 12
 },
 "loc": {
  "CHUA_DO_DUOC": 208,
  "TRUOT_LOC": 127
 },
 "quyet_dinh": {
  "BO_QUA": 1854,
  "LLM": 252,
  "MT5_TRUC_TIEP": 3275,
  "PYTHON_LLM": 3,
  "SPEC_DSL": 7
 },
 "sinh_mt5": {
  "CHO_EA_GHEP": 14,
  "CHO_MT5": 2,
  "CHO_MT5_NGOAI": 2718
 },
 "_so_phep_thu": 5084,
 "_so_to_hop": 268,
 "_kho_co_che": {
  "nguon_lenh": 384,
  "bo_loc": 274,
  "moc_vung": 41,
  "quan_li": 351,
  "go_lenh": 80
 }
}
```

## Ứng viên đã tối ưu (tốt nhất mỗi thẻ)

| Thẻ | Mã · khung | Lot | Lãi %/năm | Sụt % | Stop-out | Kẹt lâu nhất (ngày) | OOS (nhãn) | Lọc 65/15 |
|---|---|---|---|---|---|---|---|---|
| BRAIN_XuLiLenh · Donchian phá đỉnh/đáy | EURGBP H4 | 3.0 | 14.473 | 45.478 | 0 | 115.3 | 12.47 / 15.39 | TRUOT_LOC |
| BRAIN_XuLiLenh · MRZ (hồi quy z-score) | AUDCAD H4 | 10.0 | 22.882 | 44.836 | 0 | 198.8 | -8.68 / 40.91 | ĐẠT |
| BRAIN_XuLiLenh · RSI quá mua / quá bán | AUDCAD H4 | 3.0 | 22.318 | 58.15 | 0 | 30.2 | 5.87 / 18.36 | ĐẠT |
| Nhập tay: U3e41d7_mau_nhap_tay.mq5 | NZDUSD H4 | 30.0 | 261.331 | 83.284 | 0 | 56.7 | 44.52 / 39.15 | TRUOT_LOC |
| Nhập tay: trang_luu_tay.html | EURGBP H4 | 3.0 | 21.952 | 59.698 | 0 | 292.3 | 46.84 / 19.22 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: XAUUSD_M15_Acti | XAUUSD H4 | 3.0 | 74.354 | 59.096 | 0 | 179.3 | -31.22 / 59.1 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURGBP H1 | 1.0 | 6.633 | 14.158 | 0 | 57.2 | 2.61 / 3.98 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: macross.mq4 | EURJPY H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| XANDER Grid XAUUSD :: XANDER_Grid_XAUUSD.mq5 | NZDUSD H1 | 3.0 | -3.384 | 31.533 | 0 | 2207.5 | -5.12 / 14.37 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURGBP H1 | 3.0 | 15.058 | 31.666 | 0 | 293.0 | 22.17 / 13.28 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURCHF H1 | 1.0 | -1.519 | 6.756 | 0 | 613.5 | -3.87 / 3.96 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: adjustable_ma.mq4 | CADJPY H1 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: autopendingbyrsi.mq4 | EURGBP H1 | 10.0 | 39.217 | 59.93 | 0 | 282.4 | 1.41 / 30.47 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURUSD H4 | 1.0 | 8.306 | 10.275 | 0 | 18.5 | 0.07 / 10.27 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | GBPCAD H1 | 0.3 | 7.763 | 9.287 | 0 | 28.1 | 8.25 / 1.3 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: 3sma_www_forex-instrument | CHFJPY H4 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: Avalanche_v1_2.mq4 | EURGBP H1 | 1.0 | 7.119 | 12.528 | 0 | 284.3 | 5.2 / 8.41 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: alexav_d1_profit_gbpusd.mq5 | GBPUSD H4 | 1.0 | 10.704 | 63.952 | 0 | 390.3 | 2.02 / 36.36 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: macross.mq4 | XAUUSD H1 | 3.0 | 14.039 | 64.665 | 0 | 653.2 | -50.2 / 64.66 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | XAUUSD H1 | 1.0 | 19.424 | 28.024 | 0 | 653.2 | -6.74 / 28.02 | ĐẠT |
| GeneralTradingSarl/mql4_experts :: adx_ea.mq4 | GBPCAD H4 | 3.0 | 56.956 | 31.776 | 0 | 68.5 | 28.12 / 17.26 | ĐẠT |
| GeneralTradingSarl/expert-mt5 :: badx.mq5 | EURGBP H4 | 3.0 | 15.243 | 32.217 | 0 | 292.3 | 45.37 / 15.08 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | XAUUSD H1 | 1.0 | 4.866 | 37.841 | 0 | 653.5 | -31.32 / 37.56 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: bss_1_0.mq5 | CHFJPY H1 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | XAUUSD H1 | 10.0 | 54.556 | 86.387 | 0 | 653.5 | -55.25 / 86.25 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | CHFJPY H4 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: Avalanche_v1_2.mq4 | EURCHF H4 | 0.3 | 5.517 | 9.759 | 0 | 154.5 | -2.39 / 9.76 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: badx.mq5 | CHFJPY H1 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| ExMachina SafeScalping :: ExMachina_SafeScalping_CB_l1j.mq5 | GBPUSD H1 | 0.3 | 5.226 | 18.454 | 0 | 389.3 | 2.52 / 11.41 | TRUOT_LOC |
| BlueMoon :: BlueMoon_EA_v3_4_Netting_Volume_Fix.mq5 | EURCHF H1 | 3.0 | 12.254 | 55.218 | 0 | 98.8 | -7.62 / 32.09 | TRUOT_LOC |
| XANDER Grid XAUUSD :: XANDER_Grid_XAUUSD.mq5 | GBPJPY H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: bss_1_0.mq5 | EURCAD H4 | 3.0 | 31.154 | 63.57 | 0 | 35.7 | 1.22 / 35.93 | ĐẠT |
| GeneralTradingSarl/mql4_experts :: FT_BillWillams_AO.mq4 | AUDUSD H4 | 0.3 | -0.627 | 2.054 | 0 | 391.2 | -0.81 / 0.83 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main_portfolio. | NZDUSD H1 | 0.3 | 2.12 | 22.946 | 0 | 552.4 | 6.62 / 8.83 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: 3sma.mq5 | EURGBP H1 | 1.0 | 8.884 | 12.752 | 0 | 277.7 | 11.18 / 8.24 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: alexav_d1_profit_gbpusd.mq5 | GBPUSD H1 | 0.3 | 1.027 | 19.583 | 0 | 429.3 | 0.91 / 13.38 | TRUOT_LOC |
| 370 Percent from 2022 to 2026 at 10 Percent MaxDD. The GER40 | GBPCAD H1 | 10.0 | 163.33 | 48.489 | 0 | 30.6 | 42.97 / 32.18 | ĐẠT |
| 370 Percent from 2022 to 2026 at 10 Percent MaxDD. The GER40 | GBPCHF H4 | 1.0 | 5.691 | 32.818 | 0 | 582.5 | 20.85 / 19.16 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: XAUUSD_M15_Acti | XAUUSD H1 | 3.0 | 106.68 | 40.309 | 0 | 150.5 | -6.07 / 40.31 | ĐẠT |
| GeneralTradingSarl/mql4_experts :: 3sma_www_forex-instrument | GBPCAD H1 | 3.0 | 88.896 | 48.701 | 0 | 52.8 | 25.87 / 12.41 | ĐẠT |
| GeneralTradingSarl/mql4_experts :: autopendingbyrsi.mq4 | USDJPY H4 | 3.0 | 24.341 | 51.43 | 0 | 54.8 | 13.72 / 22.68 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | GBPCHF H1 | 0.3 | -3.102 | 9.338 | 0 | 392.9 | -3.61 / 4.41 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: USDCHF.mq5 | CADJPY H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/expert-mt5 :: 3sma.mq5 | EURGBP H4 | 1.0 | 0.432 | 13.681 | 0 | 293.5 | 5.04 / 3.95 | TRUOT_LOC |
| BlueMoon :: BlueMoon_EA_v3_4_Netting_Volume_Fix.mq5 | AUDCAD H1 | 0.3 | -1.503 | 33.969 | 0 | 722.4 | -8.26 / 33.97 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURCAD H4 | 0.3 | 0.923 | 2.778 | 0 | 422.7 | 0.89 / 0.71 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: main.mq5 | EURUSD H4 | 0.3 | 0.354 | 13.877 | 0 | 438.7 | -5.27 / 9.58 | TRUOT_LOC |
| Most Famous Blessing 3.9.6 EA and Setfiles :: Blessing 3 v3. | EURUSD H4 | 0.3 | 8.575 | 14.661 | 0 | 54.7 | -4.23 / 14.66 | TRUOT_LOC |
| ExMachina SafeScalping :: ExMachina_SafeScalping_CB_l1j.mq5 | AUDJPY H4 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| zhutoutoutousan/profitable-expert-advisor :: USDCHF.mq5 | USDCHF H4 | 0.3 | 1.418 | 19.715 | 0 | 133.0 | 0.65 / 7.65 | TRUOT_LOC |
| Most Famous Blessing 3.9.6 EA and Setfiles :: Blessing 3 v3. | GBPCAD H4 | 1.0 | 15.217 | 35.246 | 0 | 29.5 | 12.37 / 4.64 | ĐẠT |
| zhutoutoutousan/profitable-expert-advisor :: main_portfolio. | NZDUSD H1 | 1.0 | 5.753 | 63.691 | 0 | 510.1 | 5.89 / 6.64 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: FT_BillWillams_AO.mq4 | EURCHF H1 | 0.3 | 7.81 | 20.389 | 0 | 94.0 | 3.15 / 7.4 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: adjustable_ma.mq4 | CHFJPY H4 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| GeneralTradingSarl/mql4_experts :: adx_ea.mq4 | GBPCAD H1 | 1.0 | 51.807 | 54.287 | 0 | 41.8 | 27.29 / 35.23 | ĐẠT |
| schundi365/Wise-Expert :: report_C1_retest_limit.htm | XAUUSD H1 | 0.3 | -100.0 | 100.331 | 2 | 2.6 | - | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 3.0 | 997.045 | 69.16 | 0 | 6.4 | 422.16 / 30.62 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E9_eur_tuned_EURUSD_2025070 | EURUSD H1 | 10.0 | 133.067 | 39.636 | 0 | 60.1 | 1055.98 / 19.16 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G0_raw_bin_GBPUSD_20260101- | GBPUSD H1 | 30.0 | 369.892 | 74.86 | 0 | 8.8 | 305.31 / 19.34 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 67.64 | 45.24 | 0 | 5.2 | -40.22 / 45.24 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: StrategyTester-Default.htm | AUDCAD H1 | 3.0 | 54.798 | 16.27 | 0 | 11.5 | 34.65 / 14.54 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E9_eur_tuned_EURUSD_2026010 | EURUSD H1 | 1.0 | 37.803 | 9.44 | 0 | 10.5 | 15.82 / 3.32 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G7_gbp_tuned_GBPUSD_2026010 | GBPUSD H1 | 30.0 | 6656.443 | 83.818 | 0 | 11.3 | 47.03 / 28.2 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E8_session_ny_EURUSD_202507 | EURUSD H1 | 3.0 | 110.172 | 21.43 | 0 | 28.8 | 43.09 / 13.06 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E1_silver_D1.htm | XAUUSD H1 | 1.0 | 1.292 | 54.95 | 0 | 5.8 | 1.44 / 21.25 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester01.htm | EURUSD H1 | 30.0 | 8784.204 | 95.965 | 0 | 15.2 | 21864.77 / 95.44 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A1_full_v20.htm | XAUUSD H1 | 0.3 | 28.715 | 27.164 | 0 | 9.0 | 22.79 / 5.63 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 10.0 | 3334.331 | 98.546 | 0 | 6.3 | 243.11 / 48.99 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 10.0 | 315.224 | 91.915 | 0 | 46.2 | -97.83 / 57.36 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A2_tuned_XAGUSD_20260101-20 | XAGUSD H1 | 1.0 | 399.138 | 47.121 | 0 | 1.2 | 345.86 / 47.12 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S3_no_retest_limit_XAGUSD_2 | XAGUSD H1 | 3.0 | 4378.547 | 44.575 | 0 | 0.5 | 1019.2 / 11.71 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 24.184 | 11.986 | 0 | 13.6 | 18.85 / 5.8 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-From2502-v2.0.htm | EURUSD H1 | 30.0 | 187.656 | 54.454 | 0 | 15.2 | 616.83 / 39.76 | ĐẠT |
| cofsonJame/GOLD_EA :: ReportTester-419092552.html | XAUUSD H1 | 1.0 | 364.589 | 61.925 | 0 | 119.3 | 153.74 / 5.5 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_C3_stop_orders.htm | XAUUSD H1 | 10.0 | -100.0 | 100.603 | 1 | 3.1 | - | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 0.3 | -25.21 | 42.696 | 0 | 159.0 | -26.43 / 25.13 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_V1_cycleweight_030_XAUUSD_2 | XAUUSD H1 | 0.3 | -51.644 | 36.663 | 0 | 81.4 | -80.81 / 25.28 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 0.3 | 41.773 | 49.745 | 0 | 6.0 | 38.58 / 6.1 | ĐẠT |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 211.736 | 32.71 | 0 | 5.5 | 161.34 / 17.6 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E5_no_retest_limit_EURUSD_2 | EURUSD H1 | 10.0 | 480.492 | 33.812 | 0 | 12.6 | 714.78 / 12.89 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G2_vol_scaling_on_GBPUSD_20 | GBPUSD H1 | 30.0 | 431.79 | 42.351 | 0 | 11.9 | -34.68 / 23.01 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 161.79 | 21.669 | 0 | 6.4 | 131.41 / 13.51 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 3.0 | 93.17 | 31.455 | 0 | 0.5 | 64.7 / 18.61 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_W1_volregime_on_XAUUSD_2026 | XAUUSD H1 | 1.0 | -85.64 | 98.811 | 0 | 102.4 | -98.16 / 60.04 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-From2502-v2.0-fixbu | EURUSD H1 | 10.0 | 78.364 | 62.584 | 0 | 61.0 | 44.18 / 45.79 | ĐẠT |
| schundi365/Wise-Expert :: report_C2_m1_close.htm | XAUUSD H1 | 1.0 | 112.977 | 23.954 | 0 | 1.2 | 115.14 / 23.95 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: StrategyTester.htm | AUDCAD H1 | 10.0 | 122.013 | 18.875 | 0 | 8.0 | 330.34 / 10.33 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S4_no_friday_flatten_XAGUSD | XAGUSD H1 | 10.0 | 17873.485 | 71.46 | 0 | 2.4 | 1850.07 / 28.05 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-From2502.htm | EURUSD H1 | 30.0 | 376.574 | 52.897 | 0 | 12.1 | 138.78 / 32.23 | ĐẠT |
| schundi365/Wise-Expert :: report_E3_adx_gate_on_EURUSD_20250 | EURUSD H1 | 10.0 | 95.854 | 58.203 | 0 | 60.1 | 2000.88 / 35.26 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_X1_persistence_on_XAUUSD_20 | XAUUSD H1 | 0.3 | 29.927 | 17.044 | 0 | 2.1 | 19.96 / 13.8 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: H1 AUDCAD – Natural+Recover | AUDCAD H1 | 10.0 | 117.695 | 27.703 | 0 | 12.2 | 1803.03 / 11.06 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: _v1.html | XAUUSD H1 | 0.3 | -17.866 | 38.707 | 0 | 160.7 | -20.69 / 23.16 | TRUOT_LOC |
| schundi365/Wise-Expert :: report_B2_no_adaptive_sizing.htm | XAUUSD H1 | 30.0 | -99.925 | 97.78 | 1 | 0.2 | 0.0 / 0.0 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_T1_momentum_m30_XAUUSD_2026 | XAUUSD H1 | 1.0 | -100.0 | 101.471 | 2 | 3.2 | - | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 0.3 | 13.966 | 50.302 | 0 | 54.5 | 133.29 / 10.33 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G0_baseline_GBPUSD_20260101 | GBPUSD H1 | 30.0 | 6794.986 | 62.779 | 0 | 44.8 | 86.79 / 47.55 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 3.0 | 290.767 | 72.266 | 0 | 3.8 | 482.02 / 72.27 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 0.3 | -23.434 | 39.988 | 0 | 111.0 | -33.28 / 25.25 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A2_tuned_XAUUSD_20260101-20 | XAUUSD H1 | 0.3 | -55.086 | 37.014 | 0 | 102.4 | -68.78 / 21.08 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E2_eurusd_EURUSD_20250701-2 | EURUSD H1 | 1.0 | 42.482 | 10.491 | 0 | 15.2 | 79.64 / 4.07 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 3.0 | 459.433 | 46.591 | 0 | 3.9 | 577.87 / 46.59 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B3_no_retest.htm | XAUUSD H1 | 3.0 | -99.998 | 99.564 | 1 | 0.6 | 0.0 / 0.0 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B7_wide_session.htm | XAUUSD H1 | 0.3 | -52.538 | 36.967 | 0 | 106.8 | -78.46 / 24.94 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: H1 AUDCAD – Natural+Recover | AUDCAD H1 | 0.3 | 9.603 | 2.852 | 0 | 13.3 | 10.76 / 0.81 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_T1_momentum_m15_XAUUSD_2026 | XAUUSD H1 | 30.0 | 4570.92 | 91.418 | 2 | 2.9 | 578334186209.72 / 91.19 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_U1_regression_on_XAUUSD_202 | XAUUSD H1 | 0.3 | 31.625 | 23.943 | 0 | 2.1 | 25.57 / 19.11 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 0.3 | 24.286 | 7.596 | 0 | 6.4 | 23.68 / 2.28 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S5_silver_tuned_XAGUSD_2025 | XAGUSD H1 | 1.0 | -100.0 | 99.983 | 1 | 73.2 | -100.0 / 99.98 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A2_tuned.htm | EURUSD H1 | 30.0 | 1772.691 | 84.603 | 0 | 11.9 | 14137.11 / 25.07 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_T0_baseline_m30_XAUUSD_2026 | XAUUSD H1 | 0.3 | -100.0 | 100.102 | 2 | 2.1 | - | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G4_no_friday_flatten_GBPUSD | GBPUSD H1 | 3.0 | 80.711 | 16.243 | 0 | 45.1 | -19.09 / 11.72 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S2_vol_scaling_on_XAGUSD_20 | XAGUSD H1 | 1.0 | 265.776 | 18.583 | 0 | 2.4 | 245.39 / 11.76 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_D4_flatten.htm | XAUUSD H1 | 1.0 | -100.0 | 102.057 | 1 | 1.5 | - | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A3_tuned_nogap.htm | XAUUSD H1 | 1.0 | -89.72 | 99.163 | 0 | 102.4 | -99.14 / 65.19 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: _v2.html | XAUUSD H1 | 1.0 | -54.97 | 84.39 | 0 | 220.2 | -71.23 / 75.77 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B6_no_outlier_mask.htm | XAUUSD H1 | 30.0 | -99.804 | 96.71 | 2 | 0.0 | 0.0 / 0.0 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G6_session_ny_GBPUSD_202601 | GBPUSD H1 | 30.0 | 463.282 | 30.944 | 0 | 7.4 | -37.43 / 27.95 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S5_silver_tuned_XAGUSD_2026 | XAGUSD H1 | 1.0 | 249.078 | 20.61 | 0 | 1.5 | 167.52 / 13.11 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 24.184 | 11.986 | 0 | 13.6 | 18.85 / 5.8 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_V2_cycleweight_040_XAUUSD_2 | XAUUSD H1 | 0.3 | -38.939 | 34.153 | 0 | 102.4 | -55.73 / 16.18 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S0_baseline_XAGUSD_20260101 | XAGUSD H1 | 3.0 | 2672.975 | 64.582 | 0 | 2.4 | 1029.73 / 60.32 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_S1_adx_gate_on_XAGUSD_20260 | XAGUSD H1 | 1.0 | 1499.939 | 50.567 | 0 | 0.5 | 263.85 / 10.57 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: H1 AUDCAD – Natural+Recover | AUDCAD H1 | 0.3 | 0.115 | 1.141 | 0 | 12.2 | 3.21 / 0.44 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-h4v2.0.htm | EURUSD H1 | 10.0 | 23.885 | 18.363 | 0 | 15.6 | 52.89 / 10.69 | ĐẠT |
| huanghq2000/fx_trading :: StrategyTester-From2502-v4.0.htm | EURUSD H1 | 30.0 | 73.756 | 63.558 | 0 | 12.2 | 185.39 / 47.56 | ĐẠT |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 1.0 | 44.982 | 76.324 | 0 | 6.8 | 64.26 / 43.51 | TRUOT_LOC |
| schundi365/Wise-Expert :: report_E6_no_friday_flatten_EURUSD | EURUSD H1 | 3.0 | 62.96 | 14.055 | 0 | 7.0 | 59.93 / 8.77 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G3_no_retest_limit_GBPUSD_2 | GBPUSD H1 | 30.0 | 5206.418 | 97.211 | 1 | 12.0 | 629.23 / 78.89 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_E7_session_london_EURUSD_20 | EURUSD H1 | 0.3 | 24.789 | 10.995 | 0 | 15.3 | 19.98 / 3.68 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-From2502-v3.0.htm | EURUSD H1 | 10.0 | 41.189 | 52.822 | 0 | 12.2 | 90.95 / 35.83 | ĐẠT |
| schundi365/Wise-Expert :: report_E4_vol_scaling_on_EURUSD_20 | EURUSD H1 | 3.0 | 170.478 | 29.488 | 0 | 28.9 | 57.29 / 14.92 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 92.876 | 16.209 | 0 | 4.1 | 119.99 / 16.21 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 0.3 | -13.202 | 24.644 | 0 | 113.0 | -28.49 / 18.34 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B5_no_relvol.htm | XAUUSD H1 | 1.0 | -100.0 | 101.628 | 1 | 7.7 | - | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-daily.htm | EURUSD H1 | 30.0 | 98.736 | 44.279 | 0 | 12.1 | 175.43 / 5.74 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 10.0 | 831.302 | 59.205 | 0 | 0.7 | 361.64 / 24.85 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_D3_be_only.htm | XAUUSD H1 | 1.0 | 1.282 | 54.95 | 0 | 5.8 | 1.44 / 21.26 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_D2_soft_lock.htm | XAUUSD H1 | 1.0 | 1.282 | 54.95 | 0 | 5.8 | 1.44 / 21.26 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B4_no_adx_gate.htm | XAUUSD H1 | 1.0 | -86.029 | 97.848 | 0 | 102.4 | -98.44 / 60.41 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 1.0 | 54.992 | 17.498 | 0 | 3.9 | 73.38 / 17.5 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_B1_no_exit_mgmt.htm | XAUUSD H1 | 10.0 | -100.0 | 103.102 | 1 | 2.9 | - | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G5_session_london_GBPUSD_20 | GBPUSD H1 | 30.0 | 1472.88 | 51.973 | 0 | 10.5 | 210357.41 / 19.43 | CHUA_DO_DUOC |
| huanghq2000/fx_trading :: StrategyTester-h4.htm | EURUSD H1 | 10.0 | 280.286 | 4.498 | 0 | 2.0 | 301.85 / 3.86 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_Y1_mtf_h1_on_XAUUSD_2026010 | XAUUSD H1 | 0.3 | 19.66 | 20.267 | 0 | 5.8 | -18.79 / 20.27 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_G1_adx_gate_on_GBPUSD_20260 | GBPUSD H1 | 10.0 | 943.012 | 98.219 | 0 | 108.7 | -82.63 / 54.48 | CHUA_DO_DUOC |
| philiplau114/Grid-Trading-Bot :: H1 AUDCAD – Natural+Recover | AUDCAD H1 | 10.0 | 62.295 | 29.573 | 0 | 12.5 | 111.55 / 5.94 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 30.0 | -86.346 | 99.596 | 1 | 0.8 | 0.0 / 0.0 | TRUOT_LOC |
| schundi365/Wise-Expert :: report_D1_early_lock.htm | XAUUSD H1 | 0.3 | 37.13 | 25.677 | 0 | 9.0 | 24.5 / 5.48 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_W1_volregime_on_XAUUSD_2025 | XAUUSD H1 | 1.0 | -1.341 | 40.779 | 0 | 79.4 | -60.62 / 31.37 | CHUA_DO_DUOC |
| Marco210210/AI-Enhanced-HFT :: ReportTester-7101049.html | XAGUSD H1 | 0.3 | 30.029 | 7.82 | 0 | 6.3 | 18.11 / 7.73 | CHUA_DO_DUOC |
| schundi365/Wise-Expert :: report_A0_baseline_v16_like.htm | XAUUSD H1 | 3.0 | -100.0 | 99.198 | 4 | 1.5 | 0.0 / 0.0 | CHUA_DO_DUOC |
| jiangchengban-art/T-EA :: ReportTester-370081543.html | XAUUSD H1 | 1.0 | -36.419 | 25.418 | 0 | 49.3 | -49.93 / 11.47 | CHUA_DO_DUOC |
| shahadatnovel__3SMA-EA-in-mql4__3sma_mq4/3sma.mq4 | AUDCAD H1 | 1.0 | 19.058 | 51.646 | 0 | 95.4 | 6.95 / 28.1 | ĐẠT |
| juanmql__expert-advisors__A01_EMA_Rapida_M15/A01_EMA_Rapida_ | NZDUSD H4 | 3.0 | 23.93 | 50.291 | 0 | 103.5 | 23.83 / 21.59 | ĐẠT |
| alexanderbang01__mt5-expert-advisors__TrendFollower_EA/Trend | NZDUSD H1 | 0.3 | 12.285 | 20.002 | 0 | 161.5 | 15.67 / 14.8 | TRUOT_LOC |
| clintonbruce__-RSI-mt4-EA__BuruzRSI_mq4/BuruzRSI.mq4 | EURGBP H1 | 3.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| Muzi12345632__Relative-Strength-Index-trading-expert-advisor | NZDUSD H1 | 10.0 | 33.543 | 37.392 | 0 | 154.4 | 4.41 / 17.19 | ĐẠT |
| 77738/RSI_Exhaustion_Reversal.mq5 | EURGBP H4 | 3.0 | 13.359 | 26.436 | 0 | 22.0 | 13.81 / 4.11 | TRUOT_LOC |
| alexanderbang01__mt5-expert-advisors__EMA_RSI_EA/EMA_RSI_EA. | NZDUSD H1 | 1.0 | 38.483 | 23.07 | 0 | 151.7 | 5.55 / 16.98 | ĐẠT |
| fpinheiro921__trading-ea-mql5__IFR2_Visual/IFR2_Visual.mq5 | AUDCAD H1 | 1.0 | 4.969 | 56.107 | 0 | 289.2 | 10.23 / 19.57 | TRUOT_LOC |
| Ayooluwa-trading-dev__Automatic-Breakout-Strategy-EA__Breako | AUDCAD H1 | 1.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| syarief02__KelasEA13__template3_mq4/template3.mq4 | AUDCAD H4 | 3.0 | 6.825 | 34.101 | 0 | 221.8 | -7.76 / 34.1 | TRUOT_LOC |
| aobathree__mt5-trading-bots__SimpleMA_EA/SimpleMA_EA.mq5 | NZDUSD H1 | 3.0 | 22.536 | 41.283 | 0 | 50.8 | -7.88 / 41.28 | ĐẠT |
| Spoofiecus__MetaTrader5-ExpertAdvisors__BollingerBands_EA/Bo | EURGBP H1 | 1.0 | 18.677 | 29.966 | 0 | 283.5 | 41.15 / 16.72 | ĐẠT |
| 77653/EMA_Cross_Demo_EA.mq5 | NZDUSD H1 | 1.0 | 11.823 | 15.867 | 0 | 19.4 | -6.44 / 15.87 | TRUOT_LOC |
| smizxe__mt5-agent-toolkit__templates_EA_Template/EA_Template | GBPCAD H4 | 3.0 | 12.217 | 12.768 | 0 | 88.5 | 7.06 / 7.02 | TRUOT_LOC |
| juanmql__expert-advisors__A03_EMA_ConTendenciaMayor_H1/A03_E | NZDUSD H1 | 3.0 | 16.671 | 52.179 | 0 | 539.7 | 13.7 / 28.15 | ĐẠT |
| traderr87__RSI_SLTP_EA__Experts_RSI_SLTP_EA/RSI_SLTP_EA.mq5 | EURGBP H1 | 10.0 | 4.482 | 58.562 | 0 | 103.3 | -25.92 / 35.07 | TRUOT_LOC |
| VeyselSafetoglu__Mt5-Scalper__experts_classic_Yerlesik-Bot/Y | GBPCAD H4 | 1.0 | 11.444 | 27.766 | 0 | 154.0 | 10.72 / 6.22 | TRUOT_LOC |
| 74135/EMA_Cross_EA5.mq5 | EURGBP H1 | 0.3 | 9.124 | 26.095 | 0 | 283.3 | 29.5 / 14.6 | TRUOT_LOC |
| TaqiAmrlh__SainsManajemenEA__EA_MovingAverage/MovingAverage. | EURCAD H1 | 1.0 | 6.979 | 17.005 | 0 | 205.0 | 15.11 / 9.1 | TRUOT_LOC |
| Gogeta999__metatrader_EA_codes__Open_Order_Based_On_RSI_mq4/ | USDJPY H4 | 1.0 | 13.583 | 63.227 | 0 | 89.3 | 15.48 / 8.98 | TRUOT_LOC |
| shogona__BollingerBand__BollingerBand1_mq4/BollingerBand1.mq | AUDUSD H4 | 0.3 | 7.795 | 23.508 | 0 | 48.5 | 5.51 / 23.51 | TRUOT_LOC |
| juanmql__expert-advisors__B01_RSI_Extremos_H1/B01_RSI_Extrem | USDJPY H4 | 1.0 | 6.993 | 37.153 | 0 | 52.7 | 4.09 / 14.9 | TRUOT_LOC |
| Spoofiecus__MetaTrader5-ExpertAdvisors__CCI_EA/CCI_EA.mq5 | USDJPY H1 | 0.3 | 6.388 | 33.953 | 0 | 168.8 | 4.22 / 17.72 | TRUOT_LOC |
| fauzaanu__average_scalper__avg_scalper_mq4/avg_scalper.mq4 | USDCHF H4 | 1.0 | -2.503 | 10.292 | 0 | 635.5 | -4.05 / 4.57 | TRUOT_LOC |
| syarief02__kelasEA17__Kelas17eadua_mq4/Kelas17eadua.mq4 | EURCHF H1 | 0.3 | 5.24 | 11.515 | 0 | 93.6 | 1.37 / 5.06 | TRUOT_LOC |
| marcoyap41__sains-manajemen-ea__EAs_EA01_MA_Crossover_EA/EA0 | GBPNZD H4 | 10.0 | 13.692 | 30.634 | 0 | 14.3 | 9.81 / 28.97 | TRUOT_LOC |
| arian01Xx__ExpertAdvisorMQL5Three__SeconProjectIDK/SeconProj | CHFJPY H1 | 0.3 | 71.084 | 61.199 | 0 | 264.6 | 1.58 / 48.86 | ĐẠT |
| zhihua045-ui__free-mt5-ea-source-code__SimpleEMA_SinglePosit | EURUSD H1 | 10.0 | 9.596 | 23.771 | 0 | 451.6 | -11.75 / 18.16 | TRUOT_LOC |
| 77470/RiskGuardLite.mq5 | GBPCAD H1 | 1.0 | 8.78 | 15.383 | 0 | 150.9 | -4.6 / 13.05 | TRUOT_LOC |
| diayuunr__ea-optimization-project__EA04_Bollinger_Bands_Reve | EURAUD H1 | 1.0 | 8.55 | 48.028 | 0 | 327.3 | -9.96 / 13.98 | TRUOT_LOC |
| githubgit__mt4-ea__AmazingEA_ExpertForNews_mq4/ExpertForNews | EURGBP H4 | 0.3 | -0.589 | 1.737 | 0 | 474.5 | -0.72 / 0.72 | TRUOT_LOC |
| juanmql__expert-advisors__B04_Bollinger_Reversion_M15/B04_Bo | AUDNZD H4 | 10.0 | 20.349 | 20.177 | 0 | 125.3 | 26.79 / 7.8 | ĐẠT |
| smizxe__mt5-agent-toolkit__src_Experts_RsiLevel/RsiLevel.mq5 | GBPUSD H4 | 3.0 | 20.252 | 60.899 | 0 | 47.0 | 9.28 / 16.63 | ĐẠT |
| smizxe__mt5-agent-toolkit__src_Experts_RsiReversal/RsiRevers | EURJPY H1 | 1.0 | 4.792 | 11.553 | 0 | 27.7 | -5.17 / 11.55 | TRUOT_LOC |
| juanmql__expert-advisors__D01_Bollinger_Ruptura_H1/D01_Bolli | CHFJPY H1 | 0.3 | 22.256 | 44.79 | 0 | 22.2 | 19.4 / 44.79 | ĐẠT |
| zhihua045-ui__free-mt5-ea-source-code__RSI_SinglePosition/RS | GBPNZD H1 | 1.0 | 17.654 | 36.0 | 0 | 66.8 | 16.16 / 20.08 | ĐẠT |
| shahadatnovel__Fibonacci-EA__fibonacci_mq4/fibonacci.mq4 | CADJPY H1 | 3.0 | 9.906 | 12.089 | 0 | 23.6 | 7.09 / 5.99 | TRUOT_LOC |
| Monkeyattack__monkeyattack-gold-pivot-ea__Moving_Average_mq4 | EURCAD H1 | 1.0 | 8.204 | 13.893 | 0 | 95.7 | 7.16 / 7.3 | TRUOT_LOC |
| Spoofiecus__MetaTrader5-ExpertAdvisors__EngulfingPattern_EA/ | USDCHF H4 | 0.3 | -2.25 | 32.735 | 0 | 430.3 | 13.93 / 18.81 | TRUOT_LOC |
| 160037lk__mt4-ai-trading__experts_Moving_Average_mq4/Moving_ | EURUSD H1 | 1.0 | 9.919 | 34.492 | 0 | 416.6 | 8.22 / 19.28 | TRUOT_LOC |
| themusafirr__antilatency-sniper-ea__AntiLatency_Sniper_EA_mq | AUDCAD H4 | 0.3 | 3.523 | 15.981 | 0 | 10.8 | 2.92 / 15.09 | TRUOT_LOC |
| syarief02__kelasEA17__Kelas17eatiga_mq4/Kelas17eatiga.mq4 | GBPAUD H1 | 1.0 | 4.524 | 30.919 | 0 | 205.8 | -15.82 / 22.41 | TRUOT_LOC |
| juanmql__expert-advisors__F03_TrailingPuro_H4/F03_TrailingPu | EURAUD H1 | 10.0 | 25.178 | 34.431 | 0 | 208.0 | -38.6 / 34.36 | ĐẠT |
| tmpmosisili__forexeas__RsiEA/RsiEA.mq5 | USDCHF H4 | 3.0 | 11.872 | 50.513 | 0 | 3.3 | 0.0 / 0.0 | TRUOT_LOC |
| navamirhossein__MQL5__Experts_CrossMovingAverageEA/CrossMovi | GBPUSD H4 | 10.0 | 26.109 | 59.643 | 0 | 105.0 | 35.88 / 8.36 | ĐẠT |
| juanmql__expert-advisors__F01_Conservador_H4/F01_Conservador | EURCAD H4 | 3.0 | 32.983 | 18.696 | 0 | 26.0 | 29.56 / 9.65 | ĐẠT |
| Yumerain__EA-MQL4__Experts_OKMA_mq4/OKMA.mq4 | EURGBP H1 | 3.0 | 17.675 | 20.324 | 0 | 285.3 | 11.75 / 11.24 | ĐẠT |
| AnketKohak__AlgoTrading__EA_Using_Mql4_Moving_Average_mq4/Mo | EURUSD H4 | 1.0 | 0.91 | 31.777 | 0 | 390.2 | 10.0 / 18.17 | TRUOT_LOC |
| juanmql__expert-advisors__B03_Stoch_Lento_H4/B03_Stoch_Lento | EURGBP H4 | 10.0 | 57.325 | 55.263 | 0 | 284.0 | 67.39 / 24.6 | ĐẠT |
| keyneelvrt__mt5-expert-advisors__EA05_DualMovingAverage_Dual | EURCAD H1 | 1.0 | 7.931 | 17.35 | 0 | 46.3 | -5.14 / 16.97 | TRUOT_LOC |
| syarief02__kelasEA17__kelas17ea2_mq4/kelas17ea2.mq4 | GBPCAD H1 | 3.0 | 71.878 | 43.329 | 0 | 64.2 | 20.44 / 11.47 | ĐẠT |
| diayuunr__ea-optimization-project__EA05_MACD_Momentum_EA05_M | EURCHF H4 | 3.0 | 25.466 | 45.869 | 0 | 350.0 | 12.38 / 42.19 | ĐẠT |
| GDS Renko Dual MA Demo EA :: GDS_Renko_Dual_MA_Demo.mq5 | GBPNZD H1 | 10.0 | 153.102 | 40.199 | 0 | 91.3 | 35.98 / 22.04 | ĐẠT |
| EarnForex/Binario :: Binario.mq5 | XAUUSD H1 | 0.3 | 7.242 | 12.57 | 0 | 653.2 | -2.15 / 12.57 | TRUOT_LOC |
| Bollinger Bands N positions v2 :: Bollinger_Bands_N_position | EURUSD H4 | 0.3 | 15.583 | 60.347 | 0 | 41.0 | 5.98 / 6.34 | ĐẠT |
| akshayboora342-cell/moneymaker :: Mean_Reversion.mq5 | GBPAUD H4 | 0.3 | 2.649 | 28.555 | 0 | 175.7 | 5.01 / 2.74 | TRUOT_LOC |
| Yogurt-Peng/TrendEA :: Test.mq5 | GBPJPY H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: Breakout5-2-2.mq5 | CHFJPY H4 | 0.3 | -2.27 | 28.501 | 0 | 357.2 | 2.05 / 11.31 | TRUOT_LOC |
| The Expert Advisor on Traffic Light trend strategy :: traffi | EURUSD H4 | 1.0 | 12.394 | 15.443 | 0 | 40.7 | -2.28 / 12.84 | TRUOT_LOC |
| jensengelke/MT4 :: rsi_grid.mq4 | EURGBP H4 | 0.3 | 1.614 | 4.724 | 0 | 174.2 | 0.04 / 2.15 | TRUOT_LOC |
| BreakOut15 :: Breakout15.mq4 | EURUSD H1 | 10.0 | 11.232 | 24.267 | 0 | 451.6 | -7.33 / 16.15 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: Breakout5.mq5 | USDCHF H1 | 0.3 | -1.757 | 5.008 | 0 | 633.0 | -1.95 / 1.86 | TRUOT_LOC |
| peterthomet/MetaTrader-5-and-4-Tools :: Breakout5-2.mq5 | EURCAD H1 | 1.0 | 20.383 | 30.713 | 0 | 149.3 | -3.11 / 15.59 | ĐẠT |
| santiago-cruzlopez/MQL5 :: 011_RSI_V2_EA.mq5 | GBPCHF H1 | 3.0 | 0.67 | 5.752 | 0 | 0.5 | 0.0 / 0.0 | TRUOT_LOC |
| zobad16/Zobad_EA :: AMG.mq5 | EURCAD H4 | 10.0 | 4.881 | 12.842 | 0 | 16.8 | 3.46 / 4.21 | TRUOT_LOC |
| ScalpWiz 9001 :: ScalpWiz_9001.mq5 | USDJPY H1 | 0.3 | 9.316 | 31.344 | 0 | 130.9 | 8.69 / 10.1 | TRUOT_LOC |
| peterthomet/MetaTrader-5-and-4-Tools :: 2BarReversal.mq5 | AUDUSD H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| RSI MA EA :: MA-RSI-EA.mq4 | EURGBP H1 | 1.0 | 9.993 | 21.53 | 0 | 35.3 | 4.99 / 3.21 | TRUOT_LOC |
| RSI Bot MT5 :: RSI_Alert.mq5 | EURNZD H4 | 30.0 | 22.797 | 50.285 | 0 | 2.2 | 0.0 / 0.0 | ĐẠT |
| victor-algo/channel :: morning-buy-us.mq5 | AUDNZD H1 | 10.0 | 44.316 | 38.628 | 0 | 212.2 | 73.43 / 14.65 | ĐẠT |
| Quantum XAUUSD Silver Trader :: Quantum_XAUUSD_Silver_Trader | EURGBP H4 | 1.0 | 4.246 | 16.008 | 0 | 287.0 | 17.81 / 7.53 | TRUOT_LOC |
| tHeStRyNg/mt5_mql5_eas :: SMA_Fractals_RSI.mq5 | GBPCAD H4 | 0.3 | 14.473 | 48.474 | 0 | 32.0 | 7.49 / 3.68 | TRUOT_LOC |
| Market Miner :: Market_Miner.mq5 | CHFJPY H1 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| Smoothing Average :: Smoothing_Average.mq5 | EURCHF H1 | 1.0 | 16.305 | 21.496 | 0 | 153.5 | 0.63 / 19.9 | ĐẠT |
| peterthomet/MetaTrader-5-and-4-Tools :: Breakout2.mq5 | NZDJPY H1 | 1.0 | 3.16 | 33.711 | 0 | 582.1 | 3.73 / 11.09 | TRUOT_LOC |
| Hybrid Scalper :: hybrid_Scalper.mq4 | EURNZD H1 | 1.0 | 20.865 | 42.356 | 0 | 46.0 | 15.96 / 42.36 | ĐẠT |
| Xzmjj/Trading_Bots :: Pirañas.mq5 | GBPCHF H4 | 0.3 | 0.134 | 12.461 | 0 | 394.2 | 0.07 / 7.07 | TRUOT_LOC |
| VR Smart Grid Lite :: VR_Smart_Grid_Lite.mq4 | XAUUSD H1 | 1.0 | 2.097 | 41.15 | 0 | 653.2 | -24.31 / 41.15 | TRUOT_LOC |
| RSI Eraser :: RSI_Eraser.mq5 | EURCHF H4 | 1.0 | 2.526 | 15.655 | 0 | 154.5 | -6.08 / 12.74 | TRUOT_LOC |
| galileoChr/Projects_galileo :: MovingAverage_Test.mq5 | GBPNZD H4 | 30.0 | 150.914 | 49.33 | 0 | 219.2 | 13.52 / 24.79 | ĐẠT |
| New Martin :: New_Martin.mq5 | GBPNZD H1 | 1.0 | 44.486 | 50.721 | 0 | 62.3 | 21.74 / 10.91 | ĐẠT |
| Desmath3/MT5-EA-Project :: Belema SFP V12.mq5 | XAUUSD H1 | 0.3 | -11.257 | 36.074 | 0 | 653.5 | -26.5 / 30.38 | TRUOT_LOC |
| GDS Renko ADX Demo EA :: GDS_Renko_ADX_Demo.mq5 | EURJPY H1 | 10.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| zhihua045-ui/free-mt5-ea-source-code :: SimpleEMA_SinglePosi | XAUUSD H1 | 0.3 | 3.063 | 15.335 | 0 | 653.5 | -10.06 / 15.14 | TRUOT_LOC |
| APB Channel EA — Heikin-Ashi reversal with channel confirmat | GBPCHF H4 | 1.0 | -6.636 | 18.39 | 0 | 578.7 | -6.19 / 6.27 | TRUOT_LOC |
| Kyosuke-Fukui/AutoTrade_test :: ma_regression.mq4 | GBPUSD H4 | 3.0 | 8.176 | 20.49 | 0 | 430.7 | 6.0 / 11.31 | TRUOT_LOC |
| 17636208107zxc/XAUUSD-C3.3-TF1 :: XAUUSD_M15_M5_V3_10_9_C33_ | GBPAUD H4 | 0.3 | -2.026 | 6.092 | 0 | 560.7 | -1.0 / 1.27 | TRUOT_LOC |
| tthanhvu002sgu/ea :: The Volatility Rider session filter cop | GBPCAD H4 | 1.0 | 50.502 | 51.84 | 0 | 79.0 | 17.31 / 8.59 | ĐẠT |
| Young666YHF/xauusd_backtest :: XAUUSD_DollarTrader.mq4 | XAUUSD H1 | 0.3 | -8.245 | 24.979 | 0 | 653.2 | -20.93 / 22.45 | TRUOT_LOC |
| bailzx5522/mql_divergence :: bai_FTD.mq4 | AUDJPY H4 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: Breakout5-2.mq5 | CADJPY H1 | 0.3 | 3.297 | 13.705 | 0 | 433.9 | 3.28 / 2.74 | TRUOT_LOC |
| santiago-cruzlopez/MQL5 :: 013_Bollinger_Bands_EA.mq5 | CADJPY H4 | 0.3 | 2.416 | 4.48 | 0 | 26.5 | -0.32 / 4.48 | TRUOT_LOC |
| Simple EMA Cross EA with SL/TP and Magic Number :: EMA_Cross | XAUUSD H4 | 1.0 | 34.075 | 93.742 | 0 | 18.8 | 42.74 / 69.04 | TRUOT_LOC |
| Digital-101/AlgoTrading :: MA_Crossover.mq5 | EURGBP H1 | 10.0 | 66.031 | 62.206 | 0 | 354.3 | 18.4 / 20.25 | ĐẠT |
| peterthomet/MetaTrader-5-and-4-Tools :: Breakout5-2-2.mq5 | EURGBP H1 | 0.3 | 3.634 | 5.848 | 0 | 282.6 | 5.93 / 3.67 | TRUOT_LOC |
| borgesbsb/forexneural :: v1.7_BETA.mq5 | GBPCAD H1 | 3.0 | 150.0 | 46.371 | 0 | 60.4 | 54.66 / 28.14 | ĐẠT |
| RiskGuard Lite - Percent-Risk EMA/ATR EA :: RiskGuardLite.mq | EURUSD H1 | 1.0 | 3.755 | 19.483 | 0 | 31.6 | -12.9 / 19.48 | TRUOT_LOC |
| EMA Cross Demo EA with ATR Stops :: EMA_Cross_Demo_EA.mq5 | EURUSD H4 | 1.0 | 13.234 | 14.617 | 0 | 75.0 | 7.08 / 14.62 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: Breakout3.mq5 | EURCAD H4 | 1.0 | 8.591 | 21.947 | 0 | 36.0 | -5.41 / 21.95 | TRUOT_LOC |
| victor-algo/channel :: rwr-1.0.mq5 | AUDNZD H1 | 3.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| santiago-cruzlopez/MQL5 :: 02_Check_Open_Positions.mq5 | GBPNZD H1 | 3.0 | 53.658 | 35.46 | 0 | 53.7 | 18.55 / 24.15 | ĐẠT |
| zhihua045-ui/free-mt5-ea-source-code :: RSI_SinglePosition.m | CADJPY H4 | 0.3 | 1.506 | 6.695 | 0 | 14.8 | 2.17 / 2.47 | TRUOT_LOC |
| peterthomet/MetaTrader-5-and-4-Tools :: Breakout5.mq5 | AUDUSD H1 | 0.3 | -1.337 | 10.124 | 0 | 389.3 | 2.39 / 4.82 | TRUOT_LOC |
| santiago-cruzlopez/MQL5 :: 09_OnTester.mq5 | GBPCAD H4 | 30.0 | 256.261 | 67.325 | 0 | 59.8 | 64.62 / 24.16 | TRUOT_LOC |
| luxiaoqi/mql4 :: 5M剥头皮.mq4 | GBPNZD H1 | 30.0 | 270.275 | 77.897 | 0 | 116.9 | 28.8 / 26.07 | TRUOT_LOC |
| Moving Average x Relative Strength Indicator EA :: marsi_ea. | XAUUSD H1 | 30.0 | 9.128 | 27.244 | 0 | 1.2 | 0.0 / 0.0 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: 2BarReversal.mq5 | CHFJPY H1 | 30.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| santiago-cruzlopez/MQL5 :: 012_MA_V1_EA.mq5 | EURGBP H4 | 3.0 | 13.634 | 48.71 | 0 | 273.5 | 64.25 / 23.55 | TRUOT_LOC |
| peterthomet/MetaTrader-5-and-4-Tools :: Breakout3.mq5 | GBPCAD H4 | 0.3 | -1.112 | 3.289 | 0 | 719.5 | -1.5 / 1.46 | TRUOT_LOC |
| 97joseph/MultiCurrencyStrength :: Breakout2.mq5 | EURCAD H1 | 10.0 | 24.434 | 18.736 | 0 | 353.9 | -8.72 / 15.94 | ĐẠT |
| kecoma1/Trading_BOT :: CloseOnCross.mq5 | GBPUSD H1 | 0.3 | 7.982 | 12.214 | 0 | 99.3 | 5.5 / 5.65 | TRUOT_LOC |
| freqtrade/freqtrade-strategies :: user_data/strategies/berli | EURNZD H4 | 3.0 | 22.945 | 25.959 | 0 | 146.8 | 6.97 / 11.0 | ĐẠT |
| freqtrade/freqtrade-strategies :: user_data/strategies/Strat | USDCAD H4 | 10.0 | 23.186 | 17.418 | 0 | 7.2 | 24.75 / 11.67 | ĐẠT |
| freqtrade/freqtrade-strategies :: user_data/strategies/berli | EURNZD H1 | 1.0 | 13.026 | 63.666 | 0 | 51.8 | 12.18 / 5.75 | TRUOT_LOC |
| freqtrade/freqtrade-strategies :: user_data/strategies/berli | GBPUSD H1 | 0.3 | 3.585 | 16.617 | 0 | 430.8 | -3.7 / 11.8 | TRUOT_LOC |
| freqtrade/freqtrade-strategies :: user_data/strategies/berli | EURGBP H4 | 1.0 | 4.553 | 12.635 | 0 | 283.0 | 10.15 / 5.87 | TRUOT_LOC |
| freqtrade/freqtrade-strategies :: user_data/strategies/Infor | EURUSD H4 | 0.3 | 0.208 | 10.247 | 0 | 433.7 | 1.95 / 4.44 | TRUOT_LOC |
| freqtrade/freqtrade-strategies :: user_data/strategies/berli | USDCAD H4 | 30.0 | 41.343 | 55.159 | 0 | 148.5 | 48.5 / 48.36 | ĐẠT |
| Tổ hợp: ma_ban_ema12_duoi_ema26_va_ema12_tre1_tr + DCA deu 0 | EURUSD H4 | 3.0 | 20.635 | 21.389 | 0 | 32.3 | 15.47 / 14.74 | ĐẠT |
| Tổ hợp: ma_mua_ema20_tren_ema50_va_ema20_tre1_du + loc bien  | GBPCAD H1 | 10.0 | 112.636 | 62.064 | 0 | 33.0 | 36.29 / 28.79 | ĐẠT |
| Tổ hợp: ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi + loc gio 0 | EURGBP H4 | 1.0 | 4.903 | 9.952 | 0 | 22.0 | 5.31 / 1.62 | TRUOT_LOC |
| Tổ hợp: ma_mua_close_tren_tuyen_tinh_va_gio_bang + loc bien  | EURCAD H4 | 1.0 | 16.517 | 18.898 | 0 | 71.2 | 6.11 / 14.9 | ĐẠT |
| Tổ hợp: ma_mua_ema20_tren_ema50_va_ema20_tre1_du + loc xu hu | GBPCAD H1 | 1.0 | 16.603 | 14.23 | 0 | 67.9 | 19.79 / 12.61 | ĐẠT |
| Tổ hợp: ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi + loc bien  | AUDUSD H4 | 3.0 | 3.038 | 43.608 | 0 | 44.2 | 1.04 / 43.61 | TRUOT_LOC |
| Tổ hợp: ma_ban_sma10_tre1_tren_sma30_tre1_va_sma + loc bien  | EURGBP H1 | 10.0 | 66.74 | 64.186 | 0 | 101.2 | 78.25 / 18.77 | ĐẠT |
| Tổ hợp: ma_ban_ema21_duoi_ema50_va_ema50_duoi_em + ql tp0.00 | EURGBP H1 | 1.0 | 4.974 | 24.347 | 0 | 418.0 | 18.71 / 8.33 | TRUOT_LOC |
