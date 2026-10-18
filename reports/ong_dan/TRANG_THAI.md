# Ống dẫn: trạng thái (tự sinh bởi `python ong_dan.py bao_cao`)

Mọi số là **MÔ PHỎNG** Python ở **lot thật** (ký quỹ, stop-out, `nhan/tai_khoan.chay_tk`). Phí: **PHÍ TẠM** (hồ sơ XM đã đo trong `config/chi_phi_do.json`) cho tới khi máy nhà đo `reports/phi_san/`. Ngưỡng lọc Python: sụt giảm < 65 %% và lãi > 15 %%/năm; chuẩn cuối 80/10 (đo ở MT5). OOS chỉ là nhãn.

## Đếm theo bước

```json
{
 "loc": {
  "TRUOT_LOC": 13
 },
 "quyet_dinh": {
  "BO_QUA": 1140,
  "LLM": 138,
  "MT5_TRUC_TIEP": 199,
  "SPEC_DSL": 35
 },
 "sinh_mt5": {
  "CHO_EA_GHEP": 12,
  "CHO_MT5": 2,
  "CHO_MT5_NGOAI": 30
 },
 "_so_phep_thu": 592,
 "_so_to_hop": 148,
 "_kho_co_che": {
  "nguon_lenh": 27,
  "bo_loc": 56,
  "moc_vung": 1,
  "quan_li": 38,
  "go_lenh": 15
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
| shahadatnovel__3SMA-EA-in-mql4__3sma_mq4/3sma.mq4 | AUDCAD H1 | 1.0 | 19.058 | 51.646 | 0 | 95.4 | 6.95 / 28.1 | ĐẠT |
| juanmql__expert-advisors__A01_EMA_Rapida_M15/A01_EMA_Rapida_ | NZDUSD H4 | 3.0 | 23.93 | 50.291 | 0 | 103.5 | 23.83 / 21.59 | ĐẠT |
| alexanderbang01__mt5-expert-advisors__TrendFollower_EA/Trend | NZDUSD H1 | 0.3 | 12.285 | 20.002 | 0 | 161.5 | 15.67 / 14.8 | TRUOT_LOC |
| clintonbruce__-RSI-mt4-EA__BuruzRSI_mq4/BuruzRSI.mq4 | EURGBP H1 | 3.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| Muzi12345632__Relative-Strength-Index-trading-expert-advisor | NZDUSD H1 | 10.0 | 33.543 | 37.392 | 0 | 154.4 | 4.41 / 17.19 | ĐẠT |
| 77738/RSI_Exhaustion_Reversal.mq5 | EURGBP H4 | 3.0 | 13.359 | 26.436 | 0 | 22.0 | 13.81 / 4.11 | TRUOT_LOC |
| alexanderbang01__mt5-expert-advisors__EMA_RSI_EA/EMA_RSI_EA. | NZDUSD H1 | 1.0 | 38.483 | 23.07 | 0 | 151.7 | 5.55 / 16.98 | ĐẠT |
| fpinheiro921__trading-ea-mql5__IFR2_Visual/IFR2_Visual.mq5 | AUDCAD H1 | 1.0 | 4.969 | 56.107 | 0 | 289.2 | 10.23 / 19.57 | TRUOT_LOC |
| Ayooluwa-trading-dev__Automatic-Breakout-Strategy-EA__Breako | AUDCAD H4 | 0.3 | 0.0 | 0.0 | 0 | 0.0 | 0.0 / 0.0 | TRUOT_LOC |
| syarief02__KelasEA13__template3_mq4/template3.mq4 | AUDCAD H4 | 3.0 | 6.825 | 34.101 | 0 | 221.8 | -7.76 / 34.1 | TRUOT_LOC |
| aobathree__mt5-trading-bots__SimpleMA_EA/SimpleMA_EA.mq5 | NZDUSD H1 | 3.0 | 22.536 | 41.283 | 0 | 50.8 | -7.88 / 41.28 | ĐẠT |
| Spoofiecus__MetaTrader5-ExpertAdvisors__BollingerBands_EA/Bo | EURGBP H1 | 1.0 | 18.677 | 29.966 | 0 | 283.5 | 41.15 / 16.72 | ĐẠT |
| 77653/EMA_Cross_Demo_EA.mq5 | NZDUSD H1 | 1.0 | 11.823 | 15.867 | 0 | 19.4 | -6.44 / 15.87 | TRUOT_LOC |
| smizxe__mt5-agent-toolkit__templates_EA_Template/EA_Template | EURGBP H1 | 1.0 | 10.439 | 29.334 | 0 | 282.0 | 27.2 / 9.87 | TRUOT_LOC |
| juanmql__expert-advisors__A03_EMA_ConTendenciaMayor_H1/A03_E | EURGBP H4 | 3.0 | 14.965 | 11.99 | 0 | 26.2 | 12.37 / 11.99 | TRUOT_LOC |
| traderr87__RSI_SLTP_EA__Experts_RSI_SLTP_EA/RSI_SLTP_EA.mq5 | EURGBP H1 | 10.0 | 4.482 | 58.562 | 0 | 103.3 | -25.92 / 35.07 | TRUOT_LOC |
| VeyselSafetoglu__Mt5-Scalper__experts_classic_Yerlesik-Bot/Y | EURGBP H4 | 1.0 | 9.978 | 12.53 | 0 | 283.7 | 10.31 / 7.88 | TRUOT_LOC |
| Tổ hợp: ma_ban_ema12_duoi_ema26_va_ema12_tre1_tr + DCA deu 0 | NZDUSD H1 | 3.0 | 21.067 | 46.83 | 0 | 149.2 | 20.56 / 42.83 | ĐẠT |
| Tổ hợp: ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi + loc gio 0 | EURGBP H4 | 10.0 | 18.78 | 9.036 | 0 | 17.8 | 20.41 / 9.04 | ĐẠT |
| Tổ hợp: ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi + loc bien  | EURGBP H4 | 10.0 | 18.78 | 9.036 | 0 | 17.8 | 20.41 / 9.04 | ĐẠT |
| Tổ hợp: ma_ban_sma10_tre1_tren_sma30_tre1_va_sma + loc bien  | EURGBP H1 | 3.0 | 16.229 | 33.141 | 0 | 174.5 | 37.18 / 13.01 | ĐẠT |
| Tổ hợp: ma_ban_ema21_duoi_ema50_va_ema50_duoi_em + ql tp0.00 | NZDUSD H1 | 3.0 | 22.858 | 50.514 | 0 | 389.6 | 19.76 / 41.03 | ĐẠT |
