# MT5 Strategy Tester – lô 289 khẳng định CHO_KIEM (Evo, 15/11/2026)

Công cụ: `tools/kiem_dinh/evo/mt5_runner/` – `sinh_lo.py` (box: chọn 1 giả thuyết đại diện/template theo chuẩn đã sửa, dịch qua `nhan/dich_mq5`, gom theo mã×khung thành 28 EA optimization trên `InpMaCoChe`), `chay_lo.py` (PC: compile 1 lần, `terminal64.exe /portable /config`, `[Tester] Expert=EVO\<ea>.ex5`, Period=M15, Model=2 open prices, 2016-01-01→2026-11-13, lot 0,1, vốn 10k), `chay_don.py` (chạy đơn nhóm qua sơ bộ, đọc bảng deal → PF theo lệnh, Sharpe năm hoá theo lệnh, %/năm, tập trung), `tong_hop.py` (chấm + ghi `nao.db`).
Thời gian thực: ~9 phút optimization 216 cơ chế + ~25 phút 54 lượt đơn, trên `E:\mt5_tester\p3`.

## Phủ
| | Số |
|---|---|
| Khẳng định CHO_KIEM | 289 |
| Chạy MT5 | **216** (trang_thai → `DA_KIEM_MT5`, backup `nao.db.bak_evo_mt5_202611151201`) |
| Không dịch được | 73 – đều **chưa có giả thuyết nào** trong `gia_thuyet`: 46 template không có trong kho DSL, 27 có DSL nhưng chưa chọn tài sản/tham số. Giữ `CHO_KIEM`. |
| Lỗi dịch_mq5 | 0 |

## Kết quả (tiêu chí đã sửa: ≥30 lệnh, PF lệnh ≥1,2, Sharpe năm ≥0,3, TB lệnh >0)
- Qua sơ bộ optimization: 54. Đạt đủ 4 tiêu chí ở chạy đơn: **47**.
- Vướng: PF<1,2: 116 · <30 lệnh: 45 · Sharpe<0,3: 7 · 0 lệnh: 1.
- **Chưa pass thật**: giai đoạn MT5 chồng lên giai đoạn dò tham số của Python; 216 phép thử (~11 đạt do may ở mức 5%); không có placebo trên MT5; 18/47 dồn vào AUDCAD# H4 (dữ liệu XM `#` chỉ ~2017+), cùng họ "mua đáy khối lượng mỏng" – tương quan cao. Mua-giữ AUDCAD H4 PF 0,96 nên không phải ăn drift.
- %/năm trung thực ở 0,1 lot/10k rất nhỏ (0,1–3%/năm); muốn lớn phải nhân lot, DD nhân theo.

| # | kd | Mã/khung | Template | Lệnh | PF lệnh | Sharpe năm | %/năm (0,1 lot/10k) | Top10% lãi | Năm dương | DD% | PF mua-giữ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | AUDCAD# H4 | `mua_qua_dem_aud_sau_phien_giam` | 1100 | 1.28 | 1.079 | 3.04 | 42.9 | 8/9 | 4.67 | 0.956 |
| 2 | 156 | AUDCAD# H4 | `mua_quet_day_20_that_bai_khi_rsi_thap_kl_mong` | 105 | 2.182 | 1.019 | 0.92 | 28.0 | 7/9 | 2.34 | 0.956 |
| 3 | 79 | US500Cash# H4 | `mua_giam_10_bar_trat_tu_bien_dong_thap_tren_sma200` | 136 | 2.346 | 0.996 | 0.12 | 36.8 | 9/11 | 0.35 | 1.108 |
| 4 | 25 | AUDCAD# H4 | `mua_soc_giam_khoi_luong_mong` | 159 | 1.863 | 0.968 | 1.64 | 34.3 | 8/9 | 2.89 | 0.956 |
| 5 | 239 | AUDCAD# H4 | `mua_cham_day10_nen_tang_kl_mong_khi_doi_pct250_phan_vi_cao` | 101 | 2.085 | 0.958 | 0.73 | 37.9 | 8/9 | 1.48 | 0.956 |
| 6 | 96 | AUDCAD# H4 | `mua_ibs_thap_sau_ba_bar_giam_khoi_luong_mong_tren_sma200` | 272 | 1.532 | 0.911 | 0.89 | 38.8 | 6/9 | 1.47 | 0.956 |
| 7 | 155 | AUDNZD# H1 | `mua_hap_thu_soc_giam_khi_ibs_tre_cao_atr_vua` | 67 | 2.069 | 0.871 | 0.14 | 27.9 | 8/9 | 0.3 | 1.244 |
| 8 | 32 | AUDCHF# H4 | `kenh_trong_ban_dinh_khi_khong_xu_huong` | 137 | 1.706 | 0.831 | 2.17 | 27.0 | 7/9 | 6.56 | 0.597 |
| 9 | 165 | GBPCAD# H4 | `mua_kl_dot_bien_dong_nua_tren_khi_zscore_am_sau` | 47 | 2.577 | 0.822 | 1.66 | 34.8 | 8/9 | 4.49 | 1.124 |
| 10 | 110 | AUDCHF# H4 | `ban_pha_dinh_20_that_bai_khi_bien_dong_cao` | 137 | 1.742 | 0.802 | 1.46 | 48.1 | 5/9 | 3.42 | 0.597 |
| 11 | 126 | AUDCAD# H4 | `mua_day_kenh_50_khi_xu_huong_phang_do_doc_sma_thap` | 142 | 1.637 | 0.795 | 1.42 | 29.2 | 6/9 | 4.97 | 0.956 |
| 12 | 69 | AUDCAD# H4 | `ban_ibs_cao_hai_bar_lien_tiep_duoi_sma200` | 188 | 1.727 | 0.782 | 0.98 | 48.1 | 6/9 | 2.24 | 0.956 |
| 13 | 147 | AUDCAD# H4 | `mua_day_kenh_50_khi_khoi_luong_mong_va_atr_vua` | 58 | 2.105 | 0.756 | 0.84 | 25.5 | 9/9 | 3.06 | 0.956 |
| 14 | 235 | EURCAD# H4 | `ban_ibs_cao_kl_mong_khi_atr_phan_vi_giua_duoi_ema100` | 184 | 1.626 | 0.694 | 0.96 | 38.9 | 8/11 | 3.49 | 1.112 |
| 15 | 279 | GBPCAD# H4 | `mua_nen_giam_dai_kl_mong_khi_bien_do_tb10_thap_tren_sma200` | 47 | 2.089 | 0.67 | 0.8 | 34.8 | 7/9 | 2.52 | 1.124 |
| 16 | 125 | EURGBP# H4 | `ban_rsi2_cuc_cao_khi_bien_dong_cao_duoi_sma200` | 55 | 2.292 | 0.66 | 0.8 | 41.7 | 9/10 | 2.19 | 1.367 |
| 17 | 187 | AUDCAD# H4 | `ban_zscore_cao_khi_do_lech_nen_duoi_sma200` | 89 | 1.686 | 0.635 | 0.66 | 24.4 | 6/9 | 3.07 | 0.956 |
| 18 | 256 | EURCAD# H4 | `ban_hai_bar_ibs_cao_lien_tiep_kl_mong_khi_doi_pct120_am` | 110 | 1.706 | 0.621 | 0.63 | 39.6 | 7/11 | 2.53 | 1.112 |
| 19 | 166 | EURUSD# H4 | `mua_bar_hep_sau_bar_giam_bung_khi_tren_sma200` | 95 | 1.767 | 0.621 | 0.77 | 43.9 | 8/11 | 3.25 | 1.061 |
| 20 | 236 | GBPCAD# H1 | `mua_zscore20_am_khi_bien_do_tb10_phan_vi_thap_tren_sma200` | 248 | 1.374 | 0.62 | 1.16 | 40.2 | 6/9 | 4.05 | 1.021 |
| 21 | 240 | AUDCAD# H1 | `mua_zscore50_am_kl_mong_sau_khi_atr_rut_tu_dinh_tren_sma200` | 48 | 2.006 | 0.618 | 0.32 | 26.4 | 8/9 | 1.62 | 0.952 |
| 22 | 133 | AUDCHF# H4 | `ban_zscore_20_cao_khi_xu_huong_50_bar_di_ngang` | 106 | 1.739 | 0.616 | 1.24 | 51.5 | 6/9 | 3.17 | 0.597 |
| 23 | 207 | GBPCAD# H1 | `ban_zscore100_cang_khi_bien_dong_phan_vi_thap` | 264 | 1.36 | 0.616 | 2.15 | 28.2 | 7/9 | 9.25 | 1.021 |
| 24 | 81 | AUDCAD# H4 | `mua_ibs_thap_khoi_luong_mong_bien_dong_thap_tren_sma200` | 193 | 1.44 | 0.607 | 0.62 | 41.0 | 6/9 | 1.75 | 0.956 |
| 25 | 73 | AUDCAD# H4 | `mua_ba_bar_giam_than_nen_thu_hep_khoi_luong_can_tren_sma200` | 115 | 1.513 | 0.591 | 0.43 | 31.8 | 9/9 | 1.83 | 0.956 |
| 26 | 36 | AUDCAD# H1 | `ban_dinh_moi_50_bar_khi_khoi_luong_mong` | 207 | 1.455 | 0.59 | 0.47 | 41.4 | 5/9 | 2.14 | 0.952 |
| 27 | 233 | US500Cash# H1 | `mua_zscore100_am_cang_khi_atr_phan_vi_thap_tren_sma250` | 44 | 2.258 | 0.56 | 0.05 | 32.9 | 8/11 | 0.3 | 1.047 |
| 28 | 43 | AUDNZD# H4 | `mua_pha_dinh_20_sau_nen_bien_do_hep` | 63 | 1.613 | 0.505 | 0.39 | 32.8 | 7/9 | 1.62 | 1.673 |
| 29 | 66 | AUDCHF# H1 | `ban_khoi_luong_cao_bien_do_hep_sau_nhip_tang_duoi_sma200` | 78 | 1.668 | 0.483 | 0.31 | 51.4 | 5/9 | 1.06 | 0.731 |
| 30 | 188 | EURGBP# H4 | `mua_cu_soc_giam_tuyet_doi_kl_mong_khi_dong_luong_60_duong` | 40 | 2.947 | 0.465 | 0.93 | 68.2 | 8/11 | 2.78 | 1.367 |
| 31 | 52 | USDCAD# H4 | `mua_ibs_day_khoi_luong_dot_bien_trong_xu_huong_tang` | 150 | 1.478 | 0.453 | 0.61 | 46.7 | 6/11 | 4.26 | 1.013 |
| 32 | 108 | AUDCAD# H4 | `mua_ibs_thap_khi_bien_do_bar_hep_tren_sma200` | 346 | 1.23 | 0.45 | 0.52 | 42.1 | 8/9 | 1.85 | 0.956 |
| 33 | 5 | AUDCAD# H4 | `mua_sau_chuoi_ba_bar_giam_khi_khoi_luong_can` | 306 | 1.211 | 0.435 | 0.61 | 44.3 | 7/9 | 2.89 | 0.956 |
| 34 | 64 | AUDCAD# H4 | `mua_ba_bar_giam_manh_khoi_luong_can_tren_sma200` | 198 | 1.242 | 0.413 | 0.53 | 39.5 | 7/9 | 3.61 | 0.956 |
| 35 | 87 | GBPCAD# H4 | `mua_zscore_am_sau_khi_bien_dong_thap_tren_sma200` | 93 | 1.406 | 0.406 | 0.86 | 31.7 | 6/9 | 6.95 | 1.124 |
| 36 | 226 | AUDCHF# H4 | `ban_zscore50_cang_duong_kl_phan_vi_thap_khi_doi_pct120_am` | 67 | 1.472 | 0.405 | 0.6 | 35.8 | 7/9 | 2.99 | 0.597 |
| 37 | 1 | AUDCAD# D1 | `vang_ban_qua_da_ngan_han_khi_bien_dong_binh_thuong` | 45 | 1.494 | 0.376 | 0.34 | 34.7 | 7/9 | 1.88 | 0.882 |
| 38 | 37 | EURGBP# D1 | `ban_theo_cu_sap_khi_bien_dong_da_cao` | 47 | 1.618 | 0.371 | 0.69 | 40.0 | 5/7 | 10.26 | 2.291 |
| 39 | 229 | GBPCAD# H4 | `mua_quet_day20_dong_lai_tren_kl_mong_khi_ema200_doc_len` | 112 | 1.316 | 0.365 | 0.49 | 34.6 | 7/9 | 2.86 | 1.124 |
| 40 | 130 | AUDCAD# H4 | `mua_lech_sau_khoi_sma200_khi_atr_dang_nguoi_di` | 137 | 1.259 | 0.356 | 0.66 | 39.8 | 7/9 | 4.87 | 0.956 |
| 41 | 160 | EURCAD# D1 | `mua_zscore_am_cuc_ibs_thap_khi_sma200_doc_duong` | 54 | 1.512 | 0.349 | 0.68 | 39.6 | 5/10 | 5.17 | 1.5 |
| 42 | 103 | AUDCAD# H4 | `mua_hap_thu_ban_thao_sau_cu_soc_bien_do_khi_che_do_yen_tinh` | 114 | 1.276 | 0.332 | 0.3 | 37.3 | 6/9 | 2.43 | 0.956 |
| 43 | 254 | EURUSD# H4 | `ban_cham_dinh10_nen_giam_kl_mong_khi_doi_pct250_phan_vi_thap` | 63 | 1.45 | 0.328 | 0.44 | 46.1 | 6/11 | 3.45 | 1.061 |
| 44 | 151 | AUDCHF# H1 | `mua_roi_3bar_cuc_doan_kl_mong_khi_sma50_phang` | 219 | 1.21 | 0.324 | 0.35 | 30.8 | 6/9 | 2.24 | 0.731 |
| 45 | 148 | AUDCAD# H4 | `mua_ibs_thap_kl_mong_khi_rsi_duoi_phan_vi_thap_atr_vua` | 111 | 1.258 | 0.317 | 0.19 | 43.4 | 5/9 | 1.63 | 0.956 |
| 46 | 84 | AUDCAD# H4 | `ban_rsi2_cuc_cao_bien_dong_thap_duoi_sma200` | 152 | 1.205 | 0.31 | 0.25 | 35.1 | 5/9 | 1.81 | 0.956 |
| 47 | 157 | AUDNZD# H4 | `mua_pullback_ema20_khi_ema50_tren_ema200_atr_thap` | 50 | 1.411 | 0.301 | 0.5 | 56.1 | 6/9 | 4.09 | 1.673 |

## Bài học vận hành
- Các bản tester dùng chung `Bases` (junction → `E:\brain2_grok\shared_bases`) **không chạy song song được**: lỗi khoá file `[32]`, optimization ra xml rỗng. Chạy tuần tự (1 bản) hoặc mỗi bản `Bases` riêng (mỗi cặp M1 ~1,5–2 GB).
- Trên tài khoản XM demo 345930355: `US500Cash` không tồn tại → `US500Cash#`; `NZDCADmicro` → `NZDCAD#`.
- `Expert=` trong `[Tester]` phải là đường dẫn tương đối từ `MQL5\Experts` kèm `.ex5` (vd `EVO\EvoLo_X.ex5`), nếu không tester nạp EA mẫu Moving Average.
- `robocopy` mặc định đi theo junction (`Bases`) – dùng `/XJ`.
