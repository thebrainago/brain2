# Sổ cơ chế (tự sinh bởi `python -m nhan.so_co_che xay`, đừng sửa tay)

Một dòng mỗi hệ, chỉ metadata (không có mã nguồn bên thứ ba). Số Python là MÔ PHỎNG; số MT5 là ĐO THẬT real tick lấy từ `reports/UNG_VIEN.md`. Bản đầy đủ: `reports/kho_co_che/so_co_che.jsonl`.

Cập nhật: 20/10/2026 20:41 (giờ máy chạy). Tổng 1114 hệ; trạng thái: CHUA_DO 909, CHUA_DO_MT5 6, DAT_MT5 30, DAT_PY 53, GAN_DAT 25, TRUOT_MT5 9, TRUOT_PY 82.

Phong cách vào lệnh nhiều nhất: trend 835, mean_reversion 729, breakout 406, news 403, session 403, scalping 393, prop_risk 377, basket 301, ml_ai 122, smc_ict 93, loc_spread 17, khac 8, pending 3, donchian 1, mrz 1.

Quản lí: trailing 801, martingale 559, grid 473, hedge 470, dca 425, recovery 351.

## Hệ đạt / gần đạt (tối đa 80)

| id | Trạng thái | Mã | TF | Phong cách | Quản lí | %/năm (MT5 kép hoặc Python) | DD % | Vào lệnh |
|---|---|---|---|---|---|---|---|---|
| sk_st_4a8b8b68d6ee79c0 | GAN_DAT | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 17873.5 | 71.5 | lệnh statement ngoài |
| sk_st_654ee69c11e2fede | DAT_PY | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 6795.0 | 62.8 | lệnh statement ngoài |
| sk_st_207445946266731a | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 4378.5 | 44.6 | lệnh statement ngoài |
| sk_st_a0fc0cfafd5518f2 | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 2673.0 | 64.6 | lệnh statement ngoài |
| sk_st_a4eaaee940da1230 | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 1499.9 | 50.6 | lệnh statement ngoài |
| sk_st_e2f178474ad772a7 | DAT_PY | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 1472.9 | 52.0 | lệnh statement ngoài |
| sk_st_04d4e4af296fa5bc | GAN_DAT | XAGUSD | H1 | ml_ai,trend | dca,martingale | 997.0 | 69.2 | lệnh statement ngoài |
| sk_st_d2e5f244c840adb3 | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 831.3 | 59.2 | lệnh statement ngoài |
| sk_st_37f2cd39c135a137 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 480.5 | 33.8 | lệnh statement ngoài |
| sk_st_9a327f3b65463e5a | DAT_PY | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 463.3 | 30.9 | lệnh statement ngoài |
| sk_st_68c8b1b08e73ff16 | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 459.4 | 46.6 | lệnh statement ngoài |
| sk_st_38aff9afb5c4193b | DAT_PY | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 431.8 | 42.4 | lệnh statement ngoài |
| sk_st_1a8bc11cd2705292 | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 399.1 | 47.1 | lệnh statement ngoài |
| sk_st_064b5f790357c1b7 | GAN_DAT | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 369.9 | 74.9 | lệnh statement ngoài |
| sk_st_2a3a08c1e74856a0 | DAT_PY | GOLD | H1 | prop_risk,session,trend |  | 364.6 | 61.9 | lệnh statement ngoài |
| sk_st_667a43df87f9858b | GAN_DAT | XAGUSD | H1 | ml_ai,trend | dca,martingale | 290.8 | 72.3 | lệnh statement ngoài |
| sk_st_e3a1b4a3a127804b | DAT_PY | EURUSD | H1 | mean_reversion,trend | dca,hedge,martingale,recovery, | 280.3 | 4.5 | lệnh statement ngoài |
| sk_ea_b0d481de86 | GAN_DAT | GBPNZD | H1 | basket,mean_reversion,news,scalping,sess | dca,hedge,martingale,recovery, | 270.3 | 77.9 | ma_mua_close_tre1_tren_close_tre2: Chien luoc THAT rut tu `strategy.entry`: vao lenh khi 1 |
| sk_st_89fcf876a73c3867 | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 265.8 | 18.6 | lệnh statement ngoài |
| sk_ea_aad41ed4c1 | GAN_DAT | GBPCAD | H4 | mean_reversion,ml_ai,news,prop_risk,scal | dca,grid,martingale,trailing | 256.3 | 67.3 | ma_mua_sma14_tren_sma14_tre1_va_close_tren_muc_song: Chien luoc THAT rut tu lenh vao MQL5: |
| sk_st_9b9122b14d9094bb | DAT_PY | XAGUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 249.1 | 20.6 | lệnh statement ngoài |
| sk_st_35ea13097c0c320c | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 211.7 | 32.7 | lệnh statement ngoài |
| sk_st_c434d93a67022f21 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 170.5 | 29.5 | lệnh statement ngoài |
| sk_st_3a215d5d2b11994f | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 161.8 | 21.7 | lệnh statement ngoài |
| sk_ea_44640140cc | DAT_MT5 | GBPCAD | H1 | mean_reversion,ml_ai | dca,hedge,martingale,trailing | 138.6 | 45.8 | ma_mua_close_tren_open: Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi 1 dieu kien cun |
| sk_st_04fd5f2350ee4f35 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 133.1 | 39.6 | lệnh statement ngoài |
| sk_st_493ffbebbd84e04d | DAT_PY | AUDCAD | H1 | basket,breakout,mean_reversion,session,t | dca,grid,hedge,recovery,traili | 122.0 | 18.9 | lệnh statement ngoài |
| sk_st_52341bd17349f964 | DAT_PY | AUDCAD | H1 | basket,breakout,mean_reversion,session,t | dca,grid,hedge,martingale,reco | 117.7 | 27.7 | lệnh statement ngoài |
| sk_st_492900e786ff1674 | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 113.0 | 24.0 | lệnh statement ngoài |
| sk_st_0e17150c25c11088 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 110.2 | 21.4 | lệnh statement ngoài |
| sk_st_d14e3fa73f281037 | DAT_PY | EURUSD | H1 | mean_reversion,trend | trailing | 98.7 | 44.3 | lệnh statement ngoài |
| sk_st_4dd98349beb6b4bc | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 95.9 | 58.2 | lệnh statement ngoài |
| sk_st_3a6d730882bc7d3c | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 93.2 | 31.5 | lệnh statement ngoài |
| sk_st_c7d263204c2af7b1 | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 92.9 | 16.2 | lệnh statement ngoài |
| to_hop_16b0d75bb149f634 | DAT_MT5 | GBPCAD | H1 |  |  | 92.2 | 55.9 | chưa có trong cache box |
| sk_ea_0075f624b3 | DAT_MT5 | GBPNZD | H1 |  |  | 91.2 | 52.8 | chưa có trong cache box |
| sk_ea_0ca971ac32 | DAT_MT5 | GBPNZD | H4 | breakout,mean_reversion,prop_risk,trend | dca,grid | 85.9 | 50.6 | chưa dịch |
| sk_st_803202fb41fbee0c | DAT_PY | GBPUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 80.7 | 16.2 | lệnh statement ngoài |
| mql5_80d6f963a68f258c | DAT_PY | CHFJPY | H1,M15 | mean_reversion | dca,martingale | 71.1 | 61.2 | ma_mua_rsi14_tren_50: Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi 1 dieu kien cung  |
| sk_st_add3a54f8edcbce2 | DAT_MT5 | EURUSD | H1 | mean_reversion,trend | dca,martingale,trailing | 70.3 | 60.8 | lệnh statement ngoài |
| sk_st_0ac948e92eb71e84 | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 67.6 | 45.2 | lệnh statement ngoài |
| mql5_f3313c2c79f00c10 | DAT_MT5 | EURGBP | H4 | mean_reversion | dca | 66.1 | 50.6 | ma_mua_stochastic14_tre1_duoi_stochastic14_tre1_va_stochasti: Chien luoc THAT rut tu lenh  |
| sk_st_bc7a9b9c65d2714c | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 63.0 | 14.1 | lệnh statement ngoài |
| sk_st_e6c601d635d00bb0 | DAT_PY | AUDCAD | H1 | basket,breakout,mean_reversion,session,t | dca,grid,hedge,recovery,traili | 62.3 | 29.6 | lệnh statement ngoài |
| sk_ea_a7cd39087e | DAT_MT5 | GOLD,NZDUSD,SILVER | H1 | mean_reversion,ml_ai,prop_risk,scalping, | grid,trailing | 60.0 | 60.6 | chưa dịch |
| sk_st_dd259d3217e4067d | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,martingale | 55.0 | 17.5 | lệnh statement ngoài |
| sk_st_0c7f464ea3abbd3a | DAT_PY | AUDCAD | H1 | basket,breakout,mean_reversion,session,t | dca,grid,hedge,martingale,reco | 54.8 | 16.3 | lệnh statement ngoài |
| sk_ea_ff87f96be7 | DAT_MT5 | GBPCAD | H1 | breakout,mean_reversion,scalping,trend | grid,martingale,trailing | 53.3 | 31.7 | chưa dịch |
| sk_st_bc2d69511ae778ba | GAN_DAT | GBPJPY,GBPUSD,GOLD | H1,M15 | news | dca,hedge,martingale,trailing | 45.0 | 76.3 | lệnh statement ngoài |
| sk_ea_3279057100 | DAT_MT5 | EURGBP | H1 |  |  | 44.7 | 64.0 | chưa có trong cache box |
| b0be91a35f43f34a | DAT_MT5 | USDCAD | H4 |  |  | 44.0 | 58.6 | chưa có trong cache box |
| sk_st_676f020d892f3c23 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 42.5 | 10.5 | lệnh statement ngoài |
| sk_st_31cc1aa22a6284e0 | DAT_PY | GBPJPY,GBPUSD,GOLD | H1,M15 | news | dca,hedge,martingale,trailing | 41.8 | 49.7 | lệnh statement ngoài |
| sk_ea_02906b7d6a | DAT_MT5 | GOLD | H4 |  |  | 39.2 | 70.3 | chưa có trong cache box |
| sk_st_0cbd0a62301ce139 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 37.8 | 9.4 | lệnh statement ngoài |
| sk_ea_8897567020 | DAT_MT5 | GBPNZD | H1 | mean_reversion,ml_ai,news,prop_risk,scal | dca,grid,hedge,martingale,reco | 37.3 | 45.6 | ma_mua_close_tren_open: Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi 1 dieu kien cun |
| sk_st_ec8b5410865bdcd3 | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 37.1 | 25.7 | lệnh statement ngoài |
| sk_st_c21c2acd239f3c87 | DAT_MT5 | EURUSD | H1 | mean_reversion,trend | dca,martingale,trailing | 37.0 | 49.7 | lệnh statement ngoài |
| sk_ea_5049c79288 | DAT_MT5 | GBPCAD | H4 |  |  | 34.8 | 30.4 | chưa có trong cache box |
| sk_st_770ccee5a9650f52 | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 31.6 | 23.9 | lệnh statement ngoài |
| mql5_fd4bc285e11ab5a1 | DAT_MT5 | EURCHF | H4 | trend | dca | 31.0 | 49.3 | ma_mua_macd_tre1_duoi_macd_tre1_va_macd_tren_macd: Chien luoc THAT rut tu lenh vao MQL5: v |
| sk_st_f1f4dd64ec66dba6 | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,hedge,martingale,recovery | 30.0 | 7.8 | lệnh statement ngoài |
| sk_st_4fe09055d3b8092b | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 29.9 | 17.0 | lệnh statement ngoài |
| mql5_e3c3e4f028dbab72 | DAT_MT5 | EURCAD | H4 | trend | dca,hedge,recovery | 29.0 | 18.4 | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_nga: Chien luoc THAT rut tu lenh  |
| sk_st_14f84d3ab75e249f | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | grid,hedge,martingale,recovery | 28.7 | 27.2 | lệnh statement ngoài |
| mql5_e31426a40a5897fc | DAT_MT5 | GBPUSD | H4 | trend |  | 28.7 | 58.7 | ma_mua_close_tren_muc_song_va_sma60_duoi_sma240: Chien luoc THAT rut tu lenh vao MQL5: vao |
| mql5_ad7d22b5b165a673 | DAT_MT5 | GBPUSD | H4 | mean_reversion | dca,hedge,recovery | 27.2 | 55.0 | ma_mua_rsi14_duoi_30: Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi 1 dieu kien cung  |
| sk_ea_fdbf5bcad6 | DAT_MT5 | EURCAD | H1 | basket,breakout,mean_reversion,trend | dca,hedge,martingale,trailing | 26.4 | 18.2 | ma_mua_close_tren_tuyen_tinh_va_gio_bang_8: Chien luoc THAT rut tu lenh vao MQL5: vao lenh |
| sk_st_bf92700037092f39 | DAT_PY | EURUSD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 24.8 | 11.0 | lệnh statement ngoài |
| mql5_d8f573b8c2314bbf | DAT_MT5 | EURAUD | H1,H4 | trend |  | 24.4 | 41.4 | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_nga: Chien luoc THAT rut tu lenh  |
| sk_ea_0806a3a5e5 | DAT_MT5 | AUDNZD | H1 | breakout,mean_reversion,news,trend | martingale,trailing | 24.4 | 25.9 | chưa dịch |
| sk_st_aca366b679c75482 | DAT_MT5 | EURUSD | H1 | mean_reversion,trend | trailing | 24.4 | 18.2 | lệnh statement ngoài |
| sk_st_781895bc8999398a | DAT_PY | XAGUSD | H1 | ml_ai,trend | dca,hedge,martingale,recovery | 24.3 | 7.6 | lệnh statement ngoài |
| sk_st_2523df1774f6d7c7 | DAT_PY | XAGUSD | H1 | ml_ai,trend | martingale | 24.2 | 12.0 | lệnh statement ngoài |
| sk_st_9c33e515b96d9109 | DAT_PY | XAGUSD | H1 | ml_ai,trend | martingale | 24.2 | 12.0 | lệnh statement ngoài |
| brain_xl_mrz | DAT_PY | AUDCAD | H4 | mrz | dca | 22.9 | 44.8 | BRAIN MRZ {"n": 50, "nguong_z": 2.0} |
| brain_xl_rsi | DAT_PY | AUDCAD | H4 | rsi | dca,martingale | 22.3 | 58.1 | BRAIN RSI {"rsi_thap": 30, "rsi_cao": 70} |
| sk_ea_aba30a4e06 | DAT_MT5 | USDJPY | H4 | breakout,mean_reversion,scalping,trend | grid,martingale,trailing | 21.9 | 49.7 | chưa dịch |
| nhap_cf8073245473d2a1 | DAT_MT5 | EURGBP | H4 | mean_reversion | dca | 20.8 | 67.8 | ma_ban_rsi3_duoi_30: Chien luoc THAT rut tu lenh vao MQL5: vao lenh khi 1 dieu kien cung d |
| sk_st_e516b7a5afa1da96 | DAT_PY | GOLD | D1,H1 | basket,breakout,mean_reversion,news,prop | dca,grid,hedge,martingale,reco | 19.7 | 20.3 | lệnh statement ngoài |
