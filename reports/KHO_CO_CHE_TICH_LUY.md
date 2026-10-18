# Kho cơ chế tích luỹ (tự sinh bởi `python ong_dan.py boc`, đừng sửa tay)

Kho gốc: `data/kho_co_che/kho.sqlite` (git bỏ qua). Số đo trong kho là MÔ PHỎNG Python, phí là PHÍ TẠM cho tới khi máy nhà đo xong `reports/phi_san/`.

| Vai trò | Số cơ chế |
|---|---|
| nguồn lệnh | 27 |
| bộ lọc | 56 |
| mốc/vùng | 1 |
| quản lí | 38 |
| gỡ lệnh | 15 |

Mỗi vai trò liệt kê tối đa 60 cơ chế, cơ chế đã đo đứng trước (lãi cao trước).

| Vai trò | Tên | Từ thẻ | Tham số | Đo được (MÔ PHỎNG) |
|---|---|---|---|---|
| nguồn lệnh | ma_ban_macd_tre1_tren_macd_tre1_va_macd_duoi_macd | nhap_27bd628687ea3867 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_macd_tre1_tren_macd_tre1_va_macd_duoi` | lãi 261.3%/năm, sụt 83.3% |
| nguồn lệnh | ma_mua_macd_tre1_duoi_macd_tre1_va_macd_tren_macd | nhap_27bd628687ea3867 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_macd_tre1_duoi_macd_tre1_va_macd_tren` | lãi 261.3%/năm, sụt 83.3% |
| nguồn lệnh | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_d` | lãi 15.0%/năm, sụt 12.0% |
| nguồn lệnh | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_t` | lãi 15.0%/năm, sụt 12.0% |
| nguồn lệnh | brain_xl_donchian DONCHIAN | brain_xl_donchian | `{"kieu": "brain", "tham": {"kieu": "DONCHIAN", "n": 20}}` | lãi 14.5%/năm, sụt 45.5% |
| nguồn lệnh | ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_tre1_duoi_65 | mql5_14df17f2f4a971bd | `{"kieu": "spec", "specs": [{"ten": "ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_t` | lãi 13.4%/năm, sụt 26.4% |
| nguồn lệnh | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "spec", "specs": [{"ten": "ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200` | lãi 12.3%/năm, sụt 20.0% |
| nguồn lệnh | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "spec", "specs": [{"ten": "ma_mua_ema21_tren_ema50_va_ema50_tren_ema200` | lãi 12.3%/năm, sụt 20.0% |
| nguồn lệnh | ma_ban_ema12_duoi_ema26_va_ema12_tre1_tren_ema26_tre1 | mql5_284d05845ec9daca | `{"kieu": "spec", "specs": [{"ten": "ma_ban_ema12_duoi_ema26_va_ema12_tre1_tren_e` | lãi 11.8%/năm, sụt 15.9% |
| nguồn lệnh | ma_mua_ema12_tren_ema26_va_ema12_tre1_duoi_ema26_tre1 | mql5_284d05845ec9daca | `{"kieu": "spec", "specs": [{"ten": "ma_mua_ema12_tren_ema26_va_ema12_tre1_duoi_e` | lãi 11.8%/năm, sụt 15.9% |
| nguồn lệnh | ma_ban_sma10_tre1_tren_sma30_tre1_va_sma10_duoi_sma30 | mql5_2c753c0fbc531b25 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_sma10_tre1_tren_sma30_tre1_va_sma10_d` | lãi 10.4%/năm, sụt 29.3% |
| nguồn lệnh | ma_mua_sma10_tre1_duoi_sma30_tre1_va_sma10_tren_sma30 | mql5_2c753c0fbc531b25 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_sma10_tre1_duoi_sma30_tre1_va_sma10_t` | lãi 10.4%/năm, sụt 29.3% |
| nguồn lệnh | ma_ban_close_duoi_ema200_close_va_rsi14_duoi_45 | mql5_384f7fb3e2f35a53 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_close_duoi_ema200_close_va_rsi14_duoi` | lãi 10.0%/năm, sụt 12.5% |
| nguồn lệnh | ma_mua_close_tren_ema200_close_va_rsi14_tren_55 | mql5_384f7fb3e2f35a53 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_close_tren_ema200_close_va_rsi14_tren` | lãi 10.0%/năm, sụt 12.5% |
| nguồn lệnh | ma_ban_close_tren_muc_song | mql5_1fb7045d1de0706e | `{"kieu": "spec", "specs": [{"ten": "ma_ban_close_tren_muc_song", "ho": "quay_ve_` | lãi 6.8%/năm, sụt 34.1% |
| nguồn lệnh | ma_mua_close_duoi_muc_song | mql5_1fb7045d1de0706e | `{"kieu": "spec", "specs": [{"ten": "ma_mua_close_duoi_muc_song", "ho": "quay_ve_` | lãi 6.8%/năm, sụt 34.1% |
| nguồn lệnh | ma_mua_rsi2_duoi_25 | mql5_193539a6cfd04436 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_rsi2_duoi_25", "ho": "quay_ve_trung_b` | lãi 5.0%/năm, sụt 56.1% |
| nguồn lệnh | ma_ban_close_tren_muc_song | mql5_36dad1447c8ab5b2 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_close_tren_muc_song", "ho": "quay_ve_` | lãi 4.5%/năm, sụt 58.6% |
| nguồn lệnh | ma_mua_close_duoi_muc_song | mql5_36dad1447c8ab5b2 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_close_duoi_muc_song", "ho": "quay_ve_` | lãi 4.5%/năm, sụt 58.6% |
| nguồn lệnh | ma_ban_close_duoi_low | mql5_1c0bd24216364412 | `{"kieu": "spec", "specs": [{"ten": "ma_ban_close_duoi_low", "ho": "khac", "chieu` | lãi 0.0%/năm, sụt 0.0% |
| nguồn lệnh | ma_mua_close_tren_high | mql5_1c0bd24216364412 | `{"kieu": "spec", "specs": [{"ten": "ma_mua_close_tren_high", "ho": "khac", "chie` | lãi 0.0%/năm, sụt 0.0% |
| nguồn lệnh | ma_mua_rsi14_duoi_30_va_close_tren_muc_song | mql5_134baed46cb08b7f | `{"kieu": "spec", "specs": [{"ten": "ma_mua_rsi14_duoi_30_va_close_tren_muc_song"` | lãi 0.0%/năm, sụt 0.0% |
| nguồn lệnh | lenh_cho (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "lenh_cho"}` | - |
| nguồn lệnh | lenh_cho (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "lenh_cho"}` | - |
| nguồn lệnh | lenh_cho (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "lenh_cho"}` | - |
| nguồn lệnh | lenh_cho (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "lenh_cho"}` | - |
| nguồn lệnh | lenh_cho (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "lenh_cho"}` | - |
| bộ lọc | loc bien dong ATR14 <= 1% | brain_hat_giong | `{"kieu": "bien_dong", "n": 14, "tran_pct": 1.0}` | - |
| bộ lọc | loc gio 07-20 server | brain_hat_giong | `{"kieu": "gio", "tu": 7, "den": 20}` | - |
| bộ lọc | loc xu huong SMA200 | brain_hat_giong | `{"kieu": "xu_huong", "n": 200}` | - |
| bộ lọc | loc_phien (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "loc_phien"}` | - |
| bộ lọc | loc_phien (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "loc_phien"}` | - |
| bộ lọc | loc_phien (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "loc_phien"}` | - |
| bộ lọc | loc_phien (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "loc_phien"}` | - |
| bộ lọc | loc_phien (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "loc_phien"}` | - |
| bộ lọc | loc_spread (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "loc_spread"}` | - |
| bộ lọc | loc_spread (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "loc_spread"}` | - |
| bộ lọc | loc_spread (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "loc_spread"}` | - |
| bộ lọc | loc_spread (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "loc_spread"}` | - |
| bộ lọc | loc_tin (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "loc_tin"}` | - |
| bộ lọc | loc_tin (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "loc_tin"}` | - |
| bộ lọc | loc_tin (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "loc_tin"}` | - |
| bộ lọc | ma_ban_close_duoi_ema200_close_va_rsi14_duoi_45 :: {"trai":  | mql5_384f7fb3e2f35a53 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "gia", "cot": "close"}, ` | - |
| bộ lọc | ma_ban_close_duoi_ema200_close_va_rsi14_duoi_45 :: {"trai":  | mql5_384f7fb3e2f35a53 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_ban_ema12_duoi_ema26_va_ema12_tre1_tren_ema26_tre1 :: {"t | mql5_284d05845ec9daca | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 12}, "phep":` | - |
| bộ lọc | ma_ban_ema12_duoi_ema26_va_ema12_tre1_tren_ema26_tre1 :: {"t | mql5_284d05845ec9daca | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 20}, "phep":` | - |
| bộ lọc | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 200}, "phep"` | - |
| bộ lọc | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ngay_trong_tuan", "luc"` | - |
| bộ lọc | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ngay_trong_tuan", "luc"` | - |
| bộ lọc | ma_ban_ema20_tre1_tren_ema50_tre1_va_ema20_duoi_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 21}, "phep":` | - |
| bộ lọc | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 50}, "phep":` | - |
| bộ lọc | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_ban_ema21_duoi_ema50_va_ema50_duoi_ema200_va_rsi14_tre1_t | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_tre1_duoi_65 :: { | mql5_14df17f2f4a971bd | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "gio"}, "phep": ">=", "p` | - |
| bộ lọc | ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_tre1_duoi_65 :: { | mql5_14df17f2f4a971bd | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "gio"}, "phep": "<", "ph` | - |
| bộ lọc | ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_tre1_duoi_65 :: { | mql5_14df17f2f4a971bd | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi14_tre1_duoi_65 :: { | mql5_14df17f2f4a971bd | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_ban_macd_tre1_tren_macd_tre1_va_macd_duoi_macd :: {"trai" | nhap_27bd628687ea3867 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "macd", "nhanh": 12, "ch` | - |
| bộ lọc | ma_ban_macd_tre1_tren_macd_tre1_va_macd_duoi_macd :: {"trai" | nhap_27bd628687ea3867 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_ban_sma10_tre1_tren_sma30_tre1_va_sma10_duoi_sma30 :: {"t | mql5_2c753c0fbc531b25 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "sma", "n": 10}, "phep":` | - |
| bộ lọc | ma_ban_sma10_tre1_tren_sma30_tre1_va_sma10_duoi_sma30 :: {"t | mql5_2c753c0fbc531b25 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_mua_close_tren_ema200_close_va_rsi14_tren_55 :: {"trai":  | mql5_384f7fb3e2f35a53 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "gia", "cot": "close"}, ` | - |
| bộ lọc | ma_mua_close_tren_ema200_close_va_rsi14_tren_55 :: {"trai":  | mql5_384f7fb3e2f35a53 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_mua_ema12_tren_ema26_va_ema12_tre1_duoi_ema26_tre1 :: {"t | mql5_284d05845ec9daca | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 12}, "phep":` | - |
| bộ lọc | ma_mua_ema12_tren_ema26_va_ema12_tre1_duoi_ema26_tre1 :: {"t | mql5_284d05845ec9daca | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 200}, "phep"` | - |
| bộ lọc | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 20}, "phep":` | - |
| bộ lọc | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ngay_trong_tuan", "luc"` | - |
| bộ lọc | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ngay_trong_tuan", "luc"` | - |
| bộ lọc | ma_mua_ema20_tre1_duoi_ema50_tre1_va_ema20_tren_ema50_va_ema | mql5_344ed0d8ab12c7f0 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 21}, "phep":` | - |
| bộ lọc | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "ema", "n": 50}, "phep":` | - |
| bộ lọc | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_mua_ema21_tren_ema50_va_ema50_tren_ema200_va_rsi14_tre1_d | mql5_115a5e5a55bad5fc | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_mua_macd_tre1_duoi_macd_tre1_va_macd_tren_macd :: {"trai" | nhap_27bd628687ea3867 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "macd", "nhanh": 12, "ch` | - |
| bộ lọc | ma_mua_macd_tre1_duoi_macd_tre1_va_macd_tren_macd :: {"trai" | nhap_27bd628687ea3867 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| bộ lọc | ma_mua_rsi14_duoi_30_va_close_tren_muc_song :: {"trai": {"ch | mql5_134baed46cb08b7f | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "rsi", "n": 14}, "phep":` | - |
| bộ lọc | ma_mua_sma10_tre1_duoi_sma30_tre1_va_sma10_tren_sma30 :: {"t | mql5_2c753c0fbc531b25 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "sma", "n": 10}, "phep":` | - |
| bộ lọc | ma_mua_sma10_tre1_duoi_sma30_tre1_va_sma10_tren_sma30 :: {"t | mql5_2c753c0fbc531b25 | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "tre", "cua": {"chi_bao"` | - |
| mốc/vùng | ma_mua_rsi14_duoi_30_va_close_tren_muc_song :: {"trai": {"ch | mql5_134baed46cb08b7f | `{"kieu": "dieu_kien", "dieu_kien": {"trai": {"chi_bao": "gia", "cot": "close"}, ` | - |
| quản lí | ql tp0.005 dca0.008x8 hs1.3 hedge0.0 | nhap_27bd628687ea3867 | `{"kieu": "ql", "ql": {"tp_pct": 0.005, "dca_buoc_pct": 0.008, "dca_toi_da": 8, "` | lãi 261.3%/năm, sụt 83.3% |
| quản lí | ql tp0.001 dca0.008x5 hs1.0 hedge0.0 | brain_xl_donchian | `{"kieu": "ql", "ql": {"tp_pct": 0.001, "dca_buoc_pct": 0.008, "dca_toi_da": 5, "` | lãi 14.5%/năm, sụt 45.5% |
| quản lí | ql tp0.003 dca0.003x5 hs1.0 hedge0.0 | mql5_14df17f2f4a971bd | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.003, "dca_toi_da": 5, "` | lãi 13.4%/năm, sụt 26.4% |
| quản lí | ql tp0.005 dca0.003x5 hs1.6 hedge0.0 | mql5_115a5e5a55bad5fc | `{"kieu": "ql", "ql": {"tp_pct": 0.005, "dca_buoc_pct": 0.003, "dca_toi_da": 5, "` | lãi 12.3%/năm, sụt 20.0% |
| quản lí | ql tp0.001 dca0.003x5 hs1.3 hedge0.0 | mql5_284d05845ec9daca | `{"kieu": "ql", "ql": {"tp_pct": 0.001, "dca_buoc_pct": 0.003, "dca_toi_da": 5, "` | lãi 11.8%/năm, sụt 15.9% |
| quản lí | ql tp0.003 dca0.005x8 hs1.0 hedge0.0 | mql5_2c753c0fbc531b25 | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 8, "` | lãi 10.4%/năm, sụt 29.3% |
| quản lí | ql tp0.005 dca0.008x5 hs1.0 hedge0.0 | mql5_1fb7045d1de0706e | `{"kieu": "ql", "ql": {"tp_pct": 0.005, "dca_buoc_pct": 0.008, "dca_toi_da": 5, "` | lãi 6.8%/năm, sụt 34.1% |
| quản lí | ql tp0.001 dca0.012x8 hs1.0 hedge0.0 | mql5_1c0bd24216364412 | `{"kieu": "ql", "ql": {"tp_pct": 0.001, "dca_buoc_pct": 0.012, "dca_toi_da": 8, "` | lãi 0.0%/năm, sụt 0.0% |
| quản lí | DCA deu 0,5% x5, TP 0,2% | brain_hat_giong | `{"kieu": "ql", "ql": {"tp_pct": 0.002, "dca_buoc_pct": 0.005, "dca_toi_da": 5, "` | - |
| quản lí | DCA nhan 1,3 0,8% x5, TP 0,3% | brain_hat_giong | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.008, "dca_toi_da": 5, "` | - |
| quản lí | chot_ro (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "chot_ro"}` | - |
| quản lí | chot_ro (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "chot_ro"}` | - |
| quản lí | chot_ro (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "chot_ro"}` | - |
| quản lí | chot_ro (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "chot_ro"}` | - |
| quản lí | chot_ro (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "chot_ro"}` | - |
| quản lí | dca (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "dca"}` | - |
| quản lí | dca (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "dca"}` | - |
| quản lí | dca (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "dca"}` | - |
| quản lí | dca (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "dca"}` | - |
| quản lí | dca (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "dca"}` | - |
| quản lí | dong_mot_phan (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "dong_mot_phan"}` | - |
| quản lí | dong_mot_phan (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "dong_mot_phan"}` | - |
| quản lí | dong_mot_phan (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "dong_mot_phan"}` | - |
| quản lí | dong_mot_phan (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "dong_mot_phan"}` | - |
| quản lí | hoa_von (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "hoa_von"}` | - |
| quản lí | hoa_von (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "hoa_von"}` | - |
| quản lí | hoa_von (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "hoa_von"}` | - |
| quản lí | luoi (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "luoi"}` | - |
| quản lí | luoi (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "luoi"}` | - |
| quản lí | martingale (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "martingale"}` | - |
| quản lí | martingale (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "martingale"}` | - |
| quản lí | martingale (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "martingale"}` | - |
| quản lí | sua_sl_tp (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "sua_sl_tp"}` | - |
| quản lí | trailing (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "trailing"}` | - |
| quản lí | trailing (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "trailing"}` | - |
| quản lí | trailing (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "trailing"}` | - |
| quản lí | trailing (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "trailing"}` | - |
| quản lí | trailing (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "trailing"}` | - |
| gỡ lệnh | ql tp0.003 dca0.005x3 hs1.3 hedge20.0 | mql5_344ed0d8ab12c7f0 | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 3, "` | lãi 15.0%/năm, sụt 12.0% |
| gỡ lệnh | ql tp0.002 dca0.008x8 hs1.0 hedge20.0 | mql5_384f7fb3e2f35a53 | `{"kieu": "ql", "ql": {"tp_pct": 0.002, "dca_buoc_pct": 0.008, "dca_toi_da": 8, "` | lãi 10.0%/năm, sụt 12.5% |
| gỡ lệnh | ql tp0.003 dca0.012x8 hs1.0 hedge10.0 | mql5_193539a6cfd04436 | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.012, "dca_toi_da": 8, "` | lãi 5.0%/năm, sụt 56.1% |
| gỡ lệnh | ql tp0.001 dca0.012x5 hs1.0 hedge10.0 | mql5_36dad1447c8ab5b2 | `{"kieu": "ql", "ql": {"tp_pct": 0.001, "dca_buoc_pct": 0.012, "dca_toi_da": 5, "` | lãi 4.5%/năm, sụt 58.6% |
| gỡ lệnh | ql tp0.003 dca0.005x5 hs1.0 hedge20.0 | mql5_134baed46cb08b7f | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 5, "` | lãi 0.0%/năm, sụt 0.0% |
| gỡ lệnh | go cheo giua hai nguon | brain_hat_giong | `{"kieu": "go_cheo"}` | - |
| gỡ lệnh | go_lenh (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "go_lenh"}` | - |
| gỡ lệnh | go_lenh (freqtrade/freqtrade-strategies) | kho:freqtrade/freqtrade-strategies | `{"kieu": "nhan", "ky_thuat": "go_lenh"}` | - |
| gỡ lệnh | go_lenh (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "go_lenh"}` | - |
| gỡ lệnh | go_lenh (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "go_lenh"}` | - |
| gỡ lệnh | hedge (EA31337) | kho:EA31337 | `{"kieu": "nhan", "ky_thuat": "hedge"}` | - |
| gỡ lệnh | hedge (enarjord/passivbot) | kho:enarjord/passivbot | `{"kieu": "nhan", "ky_thuat": "hedge"}` | - |
| gỡ lệnh | hedge (hummingbot/hummingbot) | kho:hummingbot/hummingbot | `{"kieu": "nhan", "ky_thuat": "hedge"}` | - |
| gỡ lệnh | hedge (iterativv/NostalgiaForInfinity) | kho:iterativv/NostalgiaForInfinity | `{"kieu": "nhan", "ky_thuat": "hedge"}` | - |
| gỡ lệnh | khoa khi lo 10% so du, mo khoa 0,5%, go hoa von | brain_hat_giong | `{"kieu": "ql", "ql": {"tp_pct": 0.003, "dca_buoc_pct": 0.005, "dca_toi_da": 3, "` | - |
