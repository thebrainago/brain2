# Danh mục chiến lược đã qua lọc (brain2)

Tạo ngày 21/10/2026 (giờ Sài Gòn, UTC+7) cho anh Anh. Mọi số liệu lấy từ tệp trong repo; ô nào không có trong mã/dữ liệu ghi **CHƯA RÕ trong mã**. Tài liệu chỉ để đọc nghiên cứu — BACKTEST/DEMO, không phải lời khuyên đầu tư.

**Nguồn dữ liệu:** `reports/vong2/KET_QUA_VONG2.md` + `ket_qua_vong2_sau.json` (78 hệ ĐẠT, 43 hệ “bền”), `reports/UNG_VIEN.md` (kỳ đo, PF), sổ cái MT5 `reports/mt5_lien_tuc/so_cai.jsonl` và hàng chờ `reports/ong_dan/hang_cho_mt5.jsonl`, `reports/phan_viec/hang_cho_mt5_box.jsonl` (tham số EA `BRAIN_XuLiLenh`), thẻ & bản dịch trong `data/ong_dan/tho_box.sqlite` / `trang_thai.sqlite`, `reports/kho_co_che/so_co_che.jsonl`, `data/tho_box/dich_tay*`, báo cáo `reports/phan_viec/DICH_TAY_DOT3/4/5_2026-10-21.md`.

**Cách đọc chung:** Mọi hệ ở phần A được đo trên MT5 (real tick, XM micro, vốn 1.000 USD, đòn bẩy 1:500) bằng EA quản lý lệnh chung `BRAIN_XuLiLenh` ở chế độ `VAO_CSV`: điểm vào lệnh do bản dịch Python của chiến lược sinh ra (tệp CSV), còn DCA/TP/hedge do EA thực hiện theo tham số ghi bên dưới. “%/năm” = lãi kép/năm; “DD” = sụt giảm vốn (equity) tái dựng. Stress phí, Monte Carlo, ghép = MÔ PHỎNG.

## Tóm tắt

| Nhóm | Số hệ/thẻ | Nguồn kết quả | Ghi chú |
|---|---|---|---|
| A. Hệ ĐẠT MT5 (vòng 2) | 78 hệ (78 thẻ, 71 nhóm EA/chiến lược gốc) | MT5 real tick (ĐO THẬT) | 43 hệ “bền” ✔ |
| B. Thẻ mới qua lọc Python hôm nay | 13 thẻ (đợt 3: 6, đợt 4: 2, đợt 5: 5) | Python MÔ PHỎNG | CHƯA đo MT5 |

“Bền” = qua stress phí ×1,5 + hoa hồng 7 USD, ≥ 2 năm, ≥ 30 lệnh, không đoạn walk-forward âm, Monte Carlo DD p95 ≤ 80%.

### Bảng nhanh 78 hệ ĐẠT MT5 (xếp theo %/năm)

| # | Mã hệ | Thẻ | Cặp | TF | %/năm | DD % | Lệnh | Năm | Bền |
|---|---|---|---|---|---|---|---|---|---|
| 1 | skst4ac0c7fd10781af4 | sk_st_4ac0c7fd10781af4 | EURUSD | H1 | 331.4 | 45.5 | 73 | 1.34 |  |
| 2 | ghep9c03cef0b89f948f | ghep_9c03cef0b89f948f | GBPCAD | H1 | 173.5 | 59.1 | 129 | 2.76 | ✔ |
| 3 | ghepea3b5db61a7c4792 | ghep_ea3b5db61a7c4792 | GBPCAD | H4 | 147.3 | 44.4 | 279 | 2.76 |  |
| 4 | skea44640140cc | sk_ea_44640140cc | GBPCAD | H1 | 138.8 | 43.6 | 616 | 2.76 | ✔ |
| 5 | ghepe9b41c33d4deee54 | ghep_e9b41c33d4deee54 | GBPNZD | H4 | 122.9 | 41.5 | 135 | 2.76 | ✔ |
| 6 | tohop16b0d75bb149f634 | to_hop_16b0d75bb149f634 | GBPCAD | H1 | 92.3 | 55.2 | 127 | 2.76 | ✔ |
| 7 | skea0075f624b3 | sk_ea_0075f624b3 | GBPNZD | H1 | 91.4 | 50.1 | 139 | 2.74 |  |
| 8 | ghepc9f8a1b857b9a416 | ghep_c9f8a1b857b9a416 | GBPCAD | H4 | 89.6 | 50.8 | 122 | 2.76 |  |
| 9 | ghep6f5c193256881f31 | ghep_6f5c193256881f31 | GBPCAD | H1 | 86.3 | 50.2 | 324 | 2.76 |  |
| 10 | skea0ca971ac32 | sk_ea_0ca971ac32 | GBPNZD | H4 | 86.0 | 45.7 | 27 | 2.76 |  |
| 11 | skstadd3a54f8edcbce2 | sk_st_add3a54f8edcbce2 | EURUSD | H1 | 70.5 | 62.8 | 15 | 1.34 |  |
| 12 | skea0b8298aa53 | sk_ea_0b8298aa53 | GOLD | H1 | 68.1 | 43.3 | 16 | 2.76 |  |
| 13 | skea8771fe6061 | sk_ea_8771fe6061 | EURCHF | H4 | 67.2 | 37.8 | 30 | 2.72 | ✔ |
| 14 | ghep60ff9350c26c63ee | ghep_60ff9350c26c63ee | GBPCAD | H1 | 67.0 | 22.8 | 322 | 2.76 | ✔ |
| 15 | mql5f3313c2c79f00c10 | mql5_f3313c2c79f00c10 | EURGBP | H4 | 66.2 | 52.5 | 178 | 2.74 |  |
| 16 | skeab536f57733 | sk_ea_b536f57733 | EURUSD | H4 | 64.5 | 39.4 | 249 | 2.76 | ✔ |
| 17 | ghep0bf2c31fbfc9dea0 | ghep_0bf2c31fbfc9dea0 | GBPCAD | H4 | 62.2 | 52.2 | 78 | 2.76 |  |
| 18 | skeaa7cd39087e | sk_ea_a7cd39087e | GOLD | H1 | 60.0 | 55.6 | 351 | 2.76 |  |
| 19 | skeadd170ac7bf | sk_ea_dd170ac7bf | USDCAD | H1 | 54.1 | 53.8 | 109 | 2.76 |  |
| 20 | skeaff87f96be7 | sk_ea_ff87f96be7 | GBPCAD | H1 | 53.4 | 40.9 | 211 | 2.75 | ✔ |
| 21 | skea5fdf89aa94 | sk_ea_5fdf89aa94 | USDJPY | H4 | 47.8 | 47.8 | 6 | 1.85 |  |
| 22 | skea3279057100 | sk_ea_3279057100 | EURGBP | H1 | 44.8 | 63.4 | 203 | 2.76 |  |
| 23 | b0be91a35f43f34a | b0be91a35f43f34a | USDCAD | H4 | 44.0 | 57.2 | 46 | 2.71 |  |
| 24 | skead5df5bc834 | sk_ea_d5df5bc834 | GOLD | H1 | 41.0 | 47.2 | 268 | 2.76 | ✔ |
| 25 | skea31214192bc | sk_ea_31214192bc | GBPNZD | H4 | 39.6 | 29.6 | 36 | 2.64 | ✔ |
| 26 | skeadc40280363 | sk_ea_dc40280363 | CADJPY | H1 | 39.6 | 37.2 | 160 | 2.76 | ✔ |
| 27 | skea02906b7d6a | sk_ea_02906b7d6a | GOLD | H4 | 39.3 | 65.0 | 180 | 2.76 |  |
| 28 | skea154c9fdee7 | sk_ea_154c9fdee7 | GBPCAD | H4 | 38.3 | 57.0 | 182 | 2.72 | ✔ |
| 29 | skea8897567020 | sk_ea_8897567020 | GBPNZD | H1 | 37.3 | 43.6 | 154 | 2.76 |  |
| 30 | skea89d6f8661b | sk_ea_89d6f8661b | AUDUSD | H1 | 37.1 | 32.6 | 75 | 2.68 | ✔ |
| 31 | skstc21c2acd239f3c87 | sk_st_c21c2acd239f3c87 | EURUSD | H1 | 37.1 | 46.3 | 20 | 1.34 |  |
| 32 | skea45b39eb1d5 | sk_ea_45b39eb1d5 | AUDJPY | H4 | 36.1 | 46.0 | 202 | 2.76 | ✔ |
| 33 | skea5049c79288 | sk_ea_5049c79288 | GBPCAD | H4 | 34.8 | 30.0 | 83 | 2.71 | ✔ |
| 34 | skeaa3d6925a71 | sk_ea_a3d6925a71 | AUDUSD | H4 | 32.6 | 52.7 | 533 | 2.74 |  |
| 35 | ghep89811dee41bce6b9 | ghep_89811dee41bce6b9 | GOLD | H4 | 32.4 | 39.0 | 92 | 2.76 | ✔ |
| 36 | mql5fd4bc285e11ab5a1 | mql5_fd4bc285e11ab5a1 | EURCHF | H4 | 31.0 | 46.5 | 138 | 2.76 |  |
| 37 | skea61c21a2049 | sk_ea_61c21a2049 | CADJPY | H4 | 29.2 | 27.1 | 219 | 2.74 | ✔ |
| 38 | mql5e3c3e4f028dbab72 | mql5_e3c3e4f028dbab72 | EURCAD | H4 | 29.1 | 18.0 | 120 | 2.76 | ✔ |
| 39 | mql5e31426a40a5897fc | mql5_e31426a40a5897fc | GBPUSD | H4 | 28.7 | 55.9 | 15 | 2.59 |  |
| 40 | skea2f7862a741 | sk_ea_2f7862a741 | AUDUSD | H4 | 28.6 | 16.2 | 71 | 2.61 | ✔ |
| 41 | 2600ea39abbd7b0f | 2600ea39abbd7b0f | GBPNZD | H1 | 27.8 | 25.3 | 131 | 2.76 | ✔ |
| 42 | ghepeab4082becc0e276 | ghep_eab4082becc0e276 | EURGBP | H4 | 27.7 | 56.3 | 124 | 2.74 |  |
| 43 | skea0c762cdb38 | sk_ea_0c762cdb38 | CHFJPY | H4 | 27.6 | 20.2 | 39 | 2.55 | ✔ |
| 44 | skeaf7a71f885d | sk_ea_f7a71f885d | GBPNZD | H1 | 27.5 | 32.0 | 479 | 2.76 | ✔ |
| 45 | mql5ad7d22b5b165a673 | mql5_ad7d22b5b165a673 | GBPUSD | H4 | 27.2 | 53.6 | 134 | 2.76 | ✔ |
| 46 | skeafdbf5bcad6 | sk_ea_fdbf5bcad6 | EURCAD | H1 | 26.5 | 18.9 | 190 | 2.76 |  |
| 47 | skeabc8157a270 | sk_ea_bc8157a270 | NZDJPY | H4 | 25.2 | 59.5 | 292 | 2.74 | ✔ |
| 48 | mql5d8f573b8c2314bbf | mql5_d8f573b8c2314bbf | EURAUD | H1 | 24.5 | 47.1 | 106 | 2.76 |  |
| 49 | skstaca366b679c75482 | sk_st_aca366b679c75482 | EURUSD | H1 | 24.4 | 18.3 | 15 | 1.34 |  |
| 50 | skea0806a3a5e5 | sk_ea_0806a3a5e5 | AUDNZD | H1 | 24.4 | 24.6 | 29 | 2.76 |  |
| 51 | skea0cc19095a9 | sk_ea_0cc19095a9 | GBPNZD | H1 | 24.3 | 27.5 | 429 | 2.76 | ✔ |
| 52 | skea0ab6e87da9 | sk_ea_0ab6e87da9 | EURGBP | H4 | 22.8 | 74.4 | 245 | 2.74 |  |
| 53 | skea363d6c8238 | sk_ea_363d6c8238 | NZDJPY | H4 | 22.6 | 30.5 | 63 | 2.68 | ✔ |
| 54 | skea66a65a142a | sk_ea_66a65a142a | GBPNZD | H1 | 22.5 | 50.2 | 263 | 2.76 |  |
| 55 | 0557d803384c6211 | 0557d803384c6211 | GBPUSD | H4 | 22.2 | 46.1 | 182 | 2.76 | ✔ |
| 56 | skeaaba30a4e06 | sk_ea_aba30a4e06 | USDJPY | H4 | 21.9 | 48.1 | 164 | 2.76 | ✔ |
| 57 | nhapcf8073245473d2a1 | nhap_cf8073245473d2a1 | EURGBP | H4 | 20.8 | 78.2 | 188 | 2.76 |  |
| 58 | skeae2482b06a4 | sk_ea_e2482b06a4 | GBPUSD | H1 | 20.6 | 41.2 | 1338 | 2.76 | ✔ |
| 59 | skea09c76b6df5 | sk_ea_09c76b6df5 | GBPAUD | H4 | 20.2 | 34.4 | 224 | 2.70 | ✔ |
| 60 | mql5b39a9f3ba216fb47 | mql5_b39a9f3ba216fb47 | CHFJPY | H1 | 19.6 | 28.6 | 392 | 2.76 | ✔ |
| 61 | mql525573694a7f03d3a | mql5_25573694a7f03d3a | EURGBP | H1 | 19.5 | 33.4 | 282 | 2.76 |  |
| 62 | skea5539346824 | sk_ea_5539346824 | EURGBP | H1 | 19.3 | 48.9 | 233 | 2.72 |  |
| 63 | skeaf88d932deb | sk_ea_f88d932deb | GOLD | H1 | 18.9 | 53.2 | 605 | 2.76 | ✔ |
| 64 | mql5b5a04d7c15935f8b | mql5_b5a04d7c15935f8b | GBPNZD | H1 | 18.3 | 29.3 | 208 | 2.76 | ✔ |
| 65 | skead0a7af9f8b | sk_ea_d0a7af9f8b | AUDJPY | H4 | 17.9 | 7.2 | 158 | 2.74 | ✔ |
| 66 | mql5a790e25e547f0b57 | mql5_a790e25e547f0b57 | AUDNZD | H4 | 17.5 | 19.6 | 31 | 2.74 | ✔ |
| 67 | skea0ab4d307d3 | sk_ea_0ab4d307d3 | EURNZD | H1 | 17.5 | 38.8 | 286 | 2.76 | ✔ |
| 68 | tohop564be9bb91406c57 | to_hop_564be9bb91406c57 | GBPUSD | H1 | 17.4 | 26.9 | 62 | 2.72 | ✔ |
| 69 | skea135e93ee32 | sk_ea_135e93ee32 | EURUSD | H1 | 17.4 | 18.3 | 57 | 2.76 | ✔ |
| 70 | skeaf3d30ea9da | sk_ea_f3d30ea9da | GBPAUD | H1 | 16.9 | 44.4 | 956 | 2.76 | ✔ |
| 71 | tohop09a3b2ddc3e78dc8 | to_hop_09a3b2ddc3e78dc8 | EURUSD | H4 | 15.6 | 31.6 | 69 | 2.76 | ✔ |
| 72 | tohopc2d52300cc825dff | to_hop_c2d52300cc825dff | AUDNZD | H1 | 14.4 | 26.1 | 144 | 2.74 |  |
| 73 | 3304d2fad28adef6 | 3304d2fad28adef6 | USDCAD | H4 | 14.2 | 47.3 | 64 | 2.59 |  |
| 74 | mql5e52afb999eca4bd1 | mql5_e52afb999eca4bd1 | EURGBP | H1 | 13.7 | 30.0 | 110 | 2.76 | ✔ |
| 75 | skea7eec0ab393 | sk_ea_7eec0ab393 | GBPAUD | H4 | 13.1 | 59.5 | 294 | 2.70 |  |
| 76 | tohop9acc6e0d2f784cb9 | to_hop_9acc6e0d2f784cb9 | GBPCAD | H1 | 12.9 | 10.4 | 59 | 2.72 | ✔ |
| 77 | 018dcb1347276c97 | 018dcb1347276c97 | EURNZD | H4 | 12.1 | 14.8 | 76 | 2.72 | ✔ |
| 78 | skea0757c93eb3 | sk_ea_0757c93eb3 | EURNZD | H4 | 10.6 | 17.4 | 2 | 2.76 |  |

### Bảng nhanh 13 thẻ mới (Python MÔ PHỎNG)

| Thẻ | EA | Cặp | TF | %/năm | DD % | Đợt |
|---|---|---|---|---|---|---|
| sk_ea_2f4540d68a | GridScalperEA (lưới hồi quy theo Bollinger) | AUDUSD | H1 | 86.9 | 45.1 | 3 |
| sk_ea_3d5da5b65e | Sniper Gold Hybrid Recovery | XAUUSD | H4 | 33.6 | 63.7 | 3 |
| sk_ea_9345f47763 | MakeGrid193 (lưới lọc EMA34 + MACD) | EURUSD | H1 | 24.8 | 50.5 | 3 |
| sk_ea_b18d784179 | Zerith XAU SwingGrid Recovery | GBPUSD | H1 | 19.0 | 20.0 | 3 |
| sk_ea_31b7c0180f | Zerith MACD Martingale Grid | GBPUSD | H4 | 18.1 | 55.7 | 3 |
| sk_ea_8760277bca | MintyGrid 7.2 (RSI 30/70) | GBPJPY | H4 | 15.4 | 43.5 | 3 |
| sk_ea_b7faac890a | Zerith Oneshot (DeMarker, 1 lệnh/ngày) | GBPUSD | H1 | 75.0 | 62.2 | 4 |
| sk_ea_a0d40c82ed | Hon-Matrix (kênh + RSI) | EURUSD | H1 | 19.0 | 16.5 | 4 |
| sk_ea_37d18e3ece | ZONE_RECOVERY_AREA_II | EURCAD | H1 | 62.6 | 55.9 | 5 |
| sk_ea_c67d5d31e9 | Ichimoku EA v1.3 | GBPCAD | H4 | 33.0 | 27.1 | 5 |
| sk_ea_42415c4f24 | Trickerless_RHMP | EURGBP | H1 | 24.5 | 50.4 | 5 |
| sk_ea_94672bd399 | GBPJPY_EA_scalper_n6 (BB 2,5σ) | GBPJPY | H4 | 24.1 | 43.4 | 5 |
| sk_ea_5056669865 | Zone_Recovery_Formula | GBPCHF | H1 | 23.0 | 36.8 | 5 |

## A. Các hệ ĐẠT MT5 (78 hệ vòng 2), nhóm theo EA / chiến lược gốc

### A1. huanghq2000/fx_trading :: StrategyTester-From2502.htm

Nguồn: https://github.com/huanghq2000/fx_trading

#### od_skst4ac0c7fd10781af4_XM_CSV 

- **Thẻ:** `sk_st_4ac0c7fd10781af4` · **Cặp:** EURUSDmicro · **TF:** H1 · **Kiểu dịch:** lenh_ngoai
- **Điều kiện vào lệnh:**
- Không có công thức chỉ báo: điểm vào lấy **nguyên lệnh thật từ báo cáo/statement** của tác giả (194 lệnh vào, 2025-02-04 00:07 → 2026-05-28 03:45, mã EURUSD). Quy tắc vào lệnh gốc: CHƯA RÕ trong mã.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 331.4%/năm kép · DD equity 45.5% (DD báo cáo 49.5%) · 73 lệnh · PF 5.98 · giai đoạn 2025.01.30–2026.06.03 (1.34 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 310.9%/năm, DD 47.7%. Walk-forward 3 đoạn: 1171 / 365 / 62 %/năm. MC DD p95: 51.8%.
- **Python trước MT5 (MÔ PHỎNG):** 376.6%/năm, DD 52.9%.
- **Ghi chú:** lịch sử ngắn 1.3 năm; 1 đoạn WF gánh 73% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A2. Ghép vao_x_quan_li: borgesbsb/forexneural :: v1.7_BETA.mq5 × schundi365/Wise-Expert :: report_S3_no_r

#### od_ghep9c03cef0b89f948f_XM_CSV ✔ BỀN

- **Thẻ:** `ghep_9c03cef0b89f948f` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > giá mở cửa.
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_44640140cc`, phong cách quản lý của thẻ `sk_st_207445946266731a`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 173.5%/năm kép · DD equity 59.1% (DD báo cáo 60.0%) · 129 lệnh · PF 4.03 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 167.2%/năm, DD 61.6%. Walk-forward 3 đoạn: 487 / 166 / 41 %/năm. MC DD p95: 75.7%.
- **Python trước MT5 (MÔ PHỎNG):** 174.0%/năm, DD 59.8%.
- **Ghi chú:** 1 đoạn WF gánh 70% lãi; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A3. Ghép vao_x_quan_li: santiago-cruzlopez/MQL5 :: 09_OnTester.m × schundi365/Wise-Expert :: report_S3_no_r

#### od_ghepea3b5db61a7c4792_XM_CSV 

- **Thẻ:** `ghep_ea3b5db61a7c4792` · **Cặp:** GBPCADmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(14) > SMA(14) của 1 nến trước; giá đóng cửa > mức sóng của SMA(14) (ngưỡng SMA(14)).
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_aad41ed4c1`, phong cách quản lý của thẻ `sk_st_207445946266731a`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 147.3%/năm kép · DD equity 44.4% (DD báo cáo 45.6%) · 279 lệnh · PF 7.98 · giai đoạn 2023.12.28–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 141.9%/năm, DD 46.8%. Walk-forward 3 đoạn: 441 / 80 / 59 %/năm. MC DD p95: 82.6%.
- **Python trước MT5 (MÔ PHỎNG):** 143.9%/năm, DD 48.0%.
- **Ghi chú:** 1 đoạn WF gánh 76% lãi; MC DD p95 83% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A4. borgesbsb/forexneural :: v1.7_BETA.mq5

Nguồn: https://github.com/borgesbsb/forexneural

#### od_skea44640140cc_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_44640140cc` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > giá mở cửa.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 138.8%/năm kép · DD equity 43.6% (DD báo cáo 45.8%) · 616 lệnh · PF 4.32 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 130.9%/năm, DD 45.9%. Walk-forward 3 đoạn: 396 / 86 / 51 %/năm. MC DD p95: 66.4%.
- **Python trước MT5 (MÔ PHỎNG):** 150.0%/năm, DD 46.4%.
- **Ghi chú:** 1 đoạn WF gánh 74% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A5. Ghép vao_x_quan_li: luxiaoqi/mql4 :: 5M剥头皮.mq4 × schundi365/Wise-Expert :: report_G0_base

#### od_ghepe9b41c33d4deee54_XM_CSV ✔ BỀN

- **Thẻ:** `ghep_e9b41c33d4deee54` · **Cặp:** GBPNZDmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa của 1 nến trước > giá đóng cửa của 2 nến trước.
- **MUA** khi đồng thời: giá đóng cửa của 1 nến trước < giá đóng cửa của 2 nến trước.
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_b0d481de86`, phong cách quản lý của thẻ `sk_st_654ee69c11e2fede`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 122.9%/năm kép · DD equity 41.5% (DD báo cáo 43.6%) · 135 lệnh · PF 5.35 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 119.5%/năm, DD 42.5%. Walk-forward 3 đoạn: 343 / 68 / 50 %/năm. MC DD p95: 71.8%.
- **Python trước MT5 (MÔ PHỎNG):** 121.1%/năm, DD 38.4%.
- **Ghi chú:** 1 đoạn WF gánh 74% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A6. (tên EA gốc CHƯA RÕ trong mã) — thẻ to_hop_16b0d75bb149f634

#### od_tohop16b0d75bb149f634_XM_CSV ✔ BỀN

- **Thẻ:** `to_hop_16b0d75bb149f634` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** CHƯA RÕ trong mã
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ không có trong CSDL box; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 92.3%/năm kép · DD equity 55.2% (DD báo cáo 55.9%) · 127 lệnh · PF 4.71 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 88.4%/năm, DD 57.7%. Walk-forward 3 đoạn: 120 / 79 / 78 %/năm. MC DD p95: 77.7%.
- **Python trước MT5 (MÔ PHỎNG):** 112.6%/năm, DD 62.1%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A7. GDS Renko Dual MA Demo EA :: GDS_Renko_Dual_MA_Demo.mq5

Nguồn: https://www.mql5.com/en/code/77232

#### od_skea0075f624b3_XM_CSV 

- **Thẻ:** `sk_ea_0075f624b3` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 91.4%/năm kép · DD equity 50.1% (DD báo cáo 52.8%) · 139 lệnh · PF 3.15 · giai đoạn 2024.01.03–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 86.6%/năm, DD 52.6%. Walk-forward 3 đoạn: 175 / 74 / 48 %/năm. MC DD p95: 84.4%.
- **Python trước MT5 (MÔ PHỎNG):** 153.1%/năm, DD 40.2%.
- **Ghi chú:** MC DD p95 84% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A8. Ghép vao_x_quan_li: santiago-cruzlopez/MQL5 :: 09_OnTester.m × schundi365/Wise-Expert :: report_S4_no_f

#### od_ghepc9f8a1b857b9a416_XM_CSV 

- **Thẻ:** `ghep_c9f8a1b857b9a416` · **Cặp:** GBPCADmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(14) > SMA(14) của 1 nến trước; giá đóng cửa > mức sóng của SMA(14) (ngưỡng SMA(14)).
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_aad41ed4c1`, phong cách quản lý của thẻ `sk_st_4a8b8b68d6ee79c0`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 89.6%/năm kép · DD equity 50.8% (DD báo cáo 51.4%) · 122 lệnh · PF 4.54 · giai đoạn 2023.12.28–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 85.9%/năm, DD 53.1%. Walk-forward 3 đoạn: 152 / 86 / 51 %/năm. MC DD p95: 84.5%.
- **Python trước MT5 (MÔ PHỎNG):** 91.1%/năm, DD 52.2%.
- **Ghi chú:** MC DD p95 85% > 80%; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A9. Ghép vao_x_quan_li: santiago-cruzlopez/MQL5 :: 09_OnTester.m × schundi365/Wise-Expert :: report_G0_base

#### od_ghep6f5c193256881f31_XM_CSV 

- **Thẻ:** `ghep_6f5c193256881f31` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(14) > SMA(14) của 1 nến trước; giá đóng cửa > mức sóng của SMA(14) (ngưỡng SMA(14)).
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_aad41ed4c1`, phong cách quản lý của thẻ `sk_st_654ee69c11e2fede`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 86.3%/năm kép · DD equity 50.2% (DD báo cáo 49.3%) · 324 lệnh · PF 2.39 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 75.1%/năm, DD 58.3%. Walk-forward 3 đoạn: 108 / 107 / 49 %/năm. MC DD p95: 84.8%.
- **Python trước MT5 (MÔ PHỎNG):** 84.9%/năm, DD 50.5%.
- **Ghi chú:** MC DD p95 85% > 80%; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A10. galileoChr/Projects_galileo :: MovingAverage_Test.mq5

Nguồn: https://github.com/galileoChr/Projects_galileo

#### od_skea0ca971ac32_XM_CSV 

- **Thẻ:** `sk_ea_0ca971ac32` · **Cặp:** GBPNZDmicro · **TF:** H4 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa dịch”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 86.0%/năm kép · DD equity 45.7% (DD báo cáo 50.6%) · 27 lệnh · PF 80.19 · giai đoạn 2023.12.28–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 83.3%/năm, DD 46.6%. Walk-forward 3 đoạn: 210 / 70 / 22 %/năm. MC DD p95: 81.8%.
- **Python trước MT5 (MÔ PHỎNG):** 150.9%/năm, DD 49.3%.
- **Ghi chú:** ít lệnh 27; 1 đoạn WF gánh 70% lãi; MC DD p95 82% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A11. huanghq2000/fx_trading :: StrategyTester-From2502-v4.0.htm

Nguồn: https://github.com/huanghq2000/fx_trading

#### od_skstadd3a54f8edcbce2_XM_CSV 

- **Thẻ:** `sk_st_add3a54f8edcbce2` · **Cặp:** EURUSDmicro · **TF:** H1 · **Kiểu dịch:** lenh_ngoai
- **Điều kiện vào lệnh:**
- Không có công thức chỉ báo: điểm vào lấy **nguyên lệnh thật từ báo cáo/statement** của tác giả (17 lệnh vào, 2025-02-06 12:00 → 2026-05-29 16:55, mã EURUSD). Quy tắc vào lệnh gốc: CHƯA RÕ trong mã.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 70.5%/năm kép · DD equity 62.8% (DD báo cáo 60.8%) · 15 lệnh · PF 7.31 · giai đoạn 2025.01.30–2026.06.04 (1.34 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 65.6%/năm, DD 64.2%. Walk-forward 3 đoạn: 50 / 119 / 47 %/năm. MC DD p95: 65.5%.
- **Python trước MT5 (MÔ PHỎNG):** 73.8%/năm, DD 63.6%.
- **Ghi chú:** lịch sử ngắn 1.3 năm; ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A12. zhutoutoutousan/profitable-expert-advisor :: main.mq5

Nguồn: https://github.com/zhutoutoutousan/profitable-expert-advisor

#### od_skea0b8298aa53_XM_CSV 

- **Thẻ:** `sk_ea_0b8298aa53` · **Cặp:** GOLDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- Bộ tham số gốc (.set) của tác giả trong thẻ: MagicNumber=7, rsiPeriod=19, overboughtLevel=93, oversoldLevel=22, entryRSIBuySpread=0.0, entryRSISellSpread=0.0, lotSize=0.1, slippage=3, cooldownSeconds=209, TimeFrame1=1, TimeFrame2=1, BarTimeFrame=12, emaPeriod=140, emaSlopeThreshold=105.0, exitBuyRSI=86.0, exitSellRSI=10.0, TrailingStop=295.0, emaDistanceThreshold=165.0, tradingHourOneBegin=24, tradingHourOneEnd=22, tradingHourTwoBegin=6, tradingHourTwoEnd=19, Sunday=false, Monday=false, Tuesday=true, Wednesday=true, Thursday=true, Friday=false, Saturday=false
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 68.1%/năm kép · DD equity 43.3% (DD báo cáo 43.2%) · 16 lệnh · PF 41.38 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 67.0%/năm, DD 43.6%. Walk-forward 3 đoạn: 97 / 8 / 125 %/năm. MC DD p95: 42.5%.
- **Python trước MT5 (MÔ PHỎNG):** 76.6%/năm, DD 58.7%.
- **Ghi chú:** ít lệnh 16; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skead5df5bc834_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_d5df5bc834` · **Cặp:** GOLDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) của 2 nến trước ≤ 73; RSI(14) của 1 nến trước > 73.
- **BÁN** khi đồng thời: RSI(14) của 2 nến trước ≥ 90; RSI(14) của 1 nến trước < 90.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 41.0%/năm kép · DD equity 47.2% (DD báo cáo 47.7%) · 268 lệnh · PF 2.32 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 38.9%/năm, DD 49.1%. Walk-forward 3 đoạn: 37 / 55 / 32 %/năm. MC DD p95: 62.3%.
- **Python trước MT5 (MÔ PHỎNG):** 39.4%/năm, DD 49.8%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skea0c762cdb38_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_0c762cdb38` · **Cặp:** CHFJPYmicro · **TF:** H4 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 27.6%/năm kép · DD equity 20.2% (DD báo cáo 19.9%) · 39 lệnh · PF 5.74 · giai đoạn 2024.03.13–2026.10.01 (2.55 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 25.8%/năm, DD 20.4%. Walk-forward 3 đoạn: 29 / 37 / 17 %/năm. MC DD p95: 27.9%.
- **Python trước MT5 (MÔ PHỎNG):** 25.2%/năm, DD 29.9%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skeaf88d932deb_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_f88d932deb` · **Cặp:** GOLDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) của 2 nến trước ≤ 66; RSI(14) của 1 nến trước > 66.
- **BÁN** khi đồng thời: RSI(14) của 2 nến trước ≥ 6; RSI(14) của 1 nến trước < 6.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **0.3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 18.9%/năm kép · DD equity 53.2% (DD báo cáo 53.0%) · 605 lệnh · PF 2.12 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.5%/năm, DD 53.7%. Walk-forward 3 đoạn: 12 / 20 / 25 %/năm. MC DD p95: 62.2%.
- **Python trước MT5 (MÔ PHỎNG):** 23.0%/năm, DD 55.1%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skea135e93ee32_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_135e93ee32` · **Cặp:** EURUSDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(28) cắt xuống dưới 8; giờ (server) ≥ 0; giờ (server) < 8.
- **BÁN** khi đồng thời: RSI(28) cắt lên trên 60; giờ (server) ≥ 0; giờ (server) < 8.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 17.4%/năm kép · DD equity 18.3% (DD báo cáo 20.1%) · 57 lệnh · PF 4.52 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.6%/năm, DD 18.6%. Walk-forward 3 đoạn: 11 / 26 / 15 %/năm. MC DD p95: 27.9%.
- **Python trước MT5 (MÔ PHỎNG):** 17.2%/năm, DD 20.0%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A13. thong9-dev/MQL4 :: BollingerMomen.mq4

Nguồn: https://github.com/thong9-dev/MQL4

#### od_skea8771fe6061_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_8771fe6061` · **Cặp:** EURCHFmicro · **TF:** H4 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Close vuot BB(15,4) tren nen truoc va tren duong giua -> mua (chi mua)”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    c = df['close']
    n = 15
    mid = c.rolling(n, min_periods=n).mean()
    sd = c.rolling(n, min_periods=n).std(ddof=0)
    up4 = mid + 4 * sd
    mua = (c > mid.shift(1)) & (c > mid) & (c > up4.shift(1))
    return np.where(mua, 1, 0).astype(int)
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 67.2%/năm kép · DD equity 37.8% (DD báo cáo 37.7%) · 30 lệnh · PF 16.73 · giai đoạn 2024.01.10–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 64.0%/năm, DD 39.2%. Walk-forward 3 đoạn: 114 / 74 / 26 %/năm. MC DD p95: 42.8%.
- **Python trước MT5 (MÔ PHỎNG):** 67.7%/năm, DD 42.5%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A14. Ghép vao_x_quan_li: borgesbsb/forexneural :: v1.7_BETA.mq5 × schundi365/Wise-Expert :: report_G0_base

#### od_ghep60ff9350c26c63ee_XM_CSV ✔ BỀN

- **Thẻ:** `ghep_60ff9350c26c63ee` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > giá mở cửa.
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_44640140cc`, phong cách quản lý của thẻ `sk_st_654ee69c11e2fede`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 67.0%/năm kép · DD equity 22.8% (DD báo cáo 23.1%) · 322 lệnh · PF 3.90 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 62.4%/năm, DD 24.1%. Walk-forward 3 đoạn: 104 / 71 / 39 %/năm. MC DD p95: 47.4%.
- **Python trước MT5 (MÔ PHỎNG):** 69.8%/năm, DD 22.9%.
- **Ghi chú:** 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A15. juanmql__expert-advisors__B03_Stoch_Lento_H4/B03_Stoch_Lento_H4.mq5

Nguồn: https://github.com/juanmql/expert-advisors/blob/main/B03_Stoch_Lento_H4.mq5

#### od_mql5f3313c2c79f00c10_XM_CSV 

- **Thẻ:** `mql5_f3313c2c79f00c10` · **Cặp:** EURGBPmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: Stochastic(14,3) %K của 1 nến trước ≤ Stochastic(14,3,3) đường tín hiệu %D của 1 nến trước; Stochastic(14,3) %K > Stochastic(14,3,3) đường tín hiệu %D; Stochastic(14,3) %K < 25; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 600.0 điểm / TP 900.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **BÁN** khi đồng thời: Stochastic(14,3) %K của 1 nến trước ≥ Stochastic(14,3,3) đường tín hiệu %D của 1 nến trước; Stochastic(14,3) %K < Stochastic(14,3,3) đường tín hiệu %D; Stochastic(14,3) %K > 75; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 600.0 điểm / TP 900.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 66.2%/năm kép · DD equity 52.5% (DD báo cáo 50.6%) · 178 lệnh · PF 4.32 · giai đoạn 2024.01.02–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 60.5%/năm, DD 57.8%. Walk-forward 3 đoạn: 170 / -28 / 120 %/năm. MC DD p95: 78.5%.
- **Python trước MT5 (MÔ PHỎNG):** 57.3%/năm, DD 55.3%.
- **Ghi chú:** có đoạn WF âm (-28%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A16. Aeron JJN Scalper EA :: jjn_ind.mq4

Nguồn: https://www.mql5.com/en/code/12975

#### od_skeab536f57733_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_b536f57733` · **Cặp:** EURUSDmicro · **TF:** H4 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
import numpy as np

def tin_hieu(df):
    n = len(df)
    signals = np.zeros(n)
    o = df['open'].values
    c = df['close'].values
    
    DojiDiff1 = 0.001
    DojiDiff2 = 0.0004
    
    is_bearish_strong = (c < o) & ((o - c) > DojiDiff2)
    is_bullish_strong = (c > o) & ((c - o) > DojiDiff2)
    
    curr_bearish_open = np.nan
    curr_bullish_open = np.nan
    
    for i in range(1, n):
        if is_bearish_strong[i-1]:
            curr_bearish_open = o[i-1]
        if is_bullish_strong[i-1]:
            curr_bullish_open = o[i-1]
            
        if c[i] > o[i] and (o[i-1] - c[i-1]) > DojiDiff1:
            if not np.isnan(curr_bearish_open) and c[i] < curr_bearish_open:
                signals[i] = 1
        elif c[i] < o[i] and (c[i-1] - o[i-1]) > DojiDiff1:
            if not np.isnan(curr_bullish_open) and c[i] > curr_bullish_open:
                signals[i] = -1
                
    return signals
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 64.5%/năm kép · DD equity 39.4% (DD báo cáo 39.8%) · 249 lệnh · PF 2.08 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 61.8%/năm, DD 40.8%. Walk-forward 3 đoạn: 84 / 97 / 16 %/năm. MC DD p95: 57.1%.
- **Python trước MT5 (MÔ PHỎNG):** 60.1%/năm, DD 39.5%.
- **Ghi chú:** 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A17. Ghép vao_x_quan_li: borgesbsb/forexneural :: v1.7_BETA.mq5 × schundi365/Wise-Expert :: report_S4_no_f

#### od_ghep0bf2c31fbfc9dea0_XM_CSV 

- **Thẻ:** `ghep_0bf2c31fbfc9dea0` · **Cặp:** GBPCADmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > giá mở cửa.
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_44640140cc`, phong cách quản lý của thẻ `sk_st_4a8b8b68d6ee79c0`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 62.2%/năm kép · DD equity 52.2% (DD báo cáo 52.5%) · 78 lệnh · PF 9.06 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 52.4%/năm, DD 57.7%. Walk-forward 3 đoạn: 122 / 49 / 31 %/năm. MC DD p95: 92.3%.
- **Python trước MT5 (MÔ PHỎNG):** 71.6%/năm, DD 55.5%.
- **Ghi chú:** 1 đoạn WF gánh 61% lãi; MC DD p95 92% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A18. zhutoutoutousan/profitable-expert-advisor :: XAUUSD_M15_ActionEA.mq5

Nguồn: https://github.com/zhutoutoutousan/profitable-expert-advisor

#### od_skeaa7cd39087e_XM_CSV 

- **Thẻ:** `sk_ea_a7cd39087e` · **Cặp:** GOLDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa dịch”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- Mô tả cơ chế ghi trong thẻ (bản dịch bị đánh `HONG`, nên không chắc đây là công thức đã sinh CSV; nguyên văn): “Su dung mo hinh ONNX du doan 5 lop (HOLD, BUY, SELL, CLOSE_LONG, CLOSE_SHORT) tu 24 dac trung (gia, volume, RSI, EMA, ATR, session).”.
- Bộ tham số gốc (.set) của tác giả trong thẻ: InpLookback=64, InpEntryMode=1, InpProbBuy=0.18, InpProbSell=0.18, InpMinBeatHold=0.0, InpExitMode=2, InpProbCloseL=0.18, InpProbCloseS=0.18, InpMinCloseBeatHold=0.0, InpSessionHourOffset=0, InpFeatMinStr=, InpFeatMaxStr=, InpLotSize=0.01, InpMagic=902015, InpSlippage=30, InpMaxAdverseATR=2.0, InpTakeProfitATR=0.0
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 60.0%/năm kép · DD equity 55.6% (DD báo cáo 60.6%) · 351 lệnh · PF 1.39 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 53.5%/năm, DD 58.5%. Walk-forward 3 đoạn: 71 / 232 / -29 %/năm. MC DD p95: 85.4%.
- **Python trước MT5 (MÔ PHỎNG):** 106.7%/năm, DD 40.3%.
- **Ghi chú:** có đoạn WF âm (-29%/năm); 1 đoạn WF gánh 77% lãi; MC DD p95 85% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skea02906b7d6a_XM_CSV 

- **Thẻ:** `sk_ea_02906b7d6a` · **Cặp:** GOLDmicro · **TF:** H4 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- Bộ tham số gốc (.set) của tác giả trong thẻ: InpLookback=64, InpEntryMode=1, InpProbBuy=0.18, InpProbSell=0.18, InpMinBeatHold=0.0, InpExitMode=2, InpProbCloseL=0.18, InpProbCloseS=0.18, InpMinCloseBeatHold=0.0, InpSessionHourOffset=0, InpFeatMinStr=, InpFeatMaxStr=, InpLotSize=0.01, InpMagic=902015, InpSlippage=30, InpMaxAdverseATR=2.0, InpTakeProfitATR=0.0
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 39.3%/năm kép · DD equity 65.0% (DD báo cáo 70.3%) · 180 lệnh · PF 1.26 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 35.1%/năm, DD 66.9%. Walk-forward 3 đoạn: 92 / 115 / -39 %/năm. MC DD p95: 89.2%.
- **Python trước MT5 (MÔ PHỎNG):** 74.4%/năm, DD 59.1%.
- **Ghi chú:** có đoạn WF âm (-39%/năm); MC DD p95 89% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A19. GeneralTradingSarl/expert-mt5 :: ama_trader_2.mq5

Nguồn: https://github.com/GeneralTradingSarl/expert-mt5

#### od_skeadd170ac7bf_XM_CSV 

- **Thẻ:** `sk_ea_dd170ac7bf` · **Cặp:** USDCADmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > EMA(15); giá trị thấp nhất 3 nến của RSI(14) < 30.
- **BÁN** khi đồng thời: giá đóng cửa < EMA(15); giá trị cao nhất 3 nến của RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 54.1%/năm kép · DD equity 53.8% (DD báo cáo 54.6%) · 109 lệnh · PF 4.42 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 52.4%/năm, DD 55.4%. Walk-forward 3 đoạn: 54 / 25 / 90 %/năm. MC DD p95: 81.0%.
- **Python trước MT5 (MÔ PHỎNG):** 52.3%/năm, DD 54.4%.
- **Ghi chú:** MC DD p95 81% > 80%; 7 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A20. GeneralTradingSarl/mql4_experts :: adx_ea.mq4

Nguồn: https://github.com/GeneralTradingSarl/mql4_experts

#### od_skeaff87f96be7_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_ff87f96be7` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Ket hop ADX, +DI/-DI, LWMA va Momentum de tao tin hieu vao lenh”
- Mô tả trong thẻ (nguyên văn, không dấu): “Loc tin hieu khi volume tang (khong the hien trong python do thieu cot volume chuan)”
- Mô tả trong thẻ (nguyên văn, không dấu): “Dong toan bo lenh khi lo qua % TotalEquityRisk”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    n = 14
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr)
    
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9))
    adx = dx.ewm(alpha=1/n, adjust=False).mean()
    
    tp = (high + low + close) / 3
    def lwma(series, period):
        weights = np.arange(1, period + 1)
        return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    ma1 = lwma(tp, 6)
    ma2 = lwma(tp, 85)
    
    mom = close / close.shift(14) * 100
    
    sig = np.zeros(len(df))
    
    buy_cond = (
        (plus_di > minus_di) &
        (adx > 10) &
        (ma1 > ma2) &
        (mom > mom.shift(1)) &
        ((plus_di - minus_di) > 10)
    )
    
    sell_cond = (
        (plus_di < minus_di) &
        (adx > 10) &
        (ma1 < ma2) &
        (mom < mom.shift(1)) &
        ((minus_di - plus_di) > 10)
    )
    
    sig[buy_cond] = 1
    sig[sell_cond] = -1
    
    return sig.tolist()
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 53.4%/năm kép · DD equity 40.9% (DD báo cáo 31.7%) · 211 lệnh · PF 3.10 · giai đoạn 2023.12.29–2026.10.01 (2.75 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 50.5%/năm, DD 42.5%. Walk-forward 3 đoạn: 62 / 52 / 46 %/năm. MC DD p95: 58.3%.
- **Python trước MT5 (MÔ PHỎNG):** 51.8%/năm, DD 54.3%.
- **Ghi chú:** 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5); Bản dịch gần đúng/chưa dịch (nguyên văn): Logic MACD khung MN1 (PERIOD_MN1) dung de loc lenh va thoat lenh khong the trien khai chuan xac tren DataFrame 1 khung thoi gian ma khong dung resample, da bo qua trong python.; Logic Volume filter (iVolume) khong duoc ho tro trong danh sach chi bao chuan, da bo qua.; Cac ham quan li von (Money Trailing, TP In Money/Percent) phu thuoc vao AccountEquity/Balance, khong the mo phong hoan toan trong backtest tin hieu thong thuong..

#### od_skea5049c79288_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_5049c79288` · **Cặp:** GBPCADmicro · **TF:** H4 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 34.8%/năm kép · DD equity 30.0% (DD báo cáo 30.4%) · 83 lệnh · PF 3.07 · giai đoạn 2024.01.15–2026.10.01 (2.71 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 33.2%/năm, DD 31.0%. Walk-forward 3 đoạn: 63 / 11 / 35 %/năm. MC DD p95: 53.3%.
- **Python trước MT5 (MÔ PHỎNG):** 57.0%/năm, DD 31.8%.
- **Ghi chú:** 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A21. Simple Martingale Template :: Simple_Martingale_Template.mq4

Nguồn: https://www.mql5.com/en/code/32299

#### od_skea5fdf89aa94_XM_CSV 

- **Thẻ:** `sk_ea_5fdf89aa94` · **Cặp:** USDJPYmicro · **TF:** H4 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Close>SMA50>SMA200, SMA50 vua cat SMA200 (nen truoc duoi), close > high nen truoc -> mua; nguoc lai ban”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    c = df['close']; h = df['high']; l = df['low']
    f = c.rolling(50, min_periods=50).mean()
    s = c.rolling(200, min_periods=200).mean()
    mua = (c > f) & (f > s) & (f.shift(1) < s.shift(1)) & (c > h.shift(1))
    ban = (c < f) & (f < s) & (f.shift(1) > s.shift(1)) & (c < l.shift(1))
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 47.8%/năm kép · DD equity 47.8% (DD báo cáo 49.2%) · 6 lệnh · PF 38.09 · giai đoạn 2024.11.25–2026.10.01 (1.85 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 46.8%/năm, DD 48.2%. Walk-forward 3 đoạn: 52 / 113 / -0 %/năm. MC DD p95: 54.1%.
- **Python trước MT5 (MÔ PHỎNG):** 26.1%/năm, DD 49.1%.
- **Ghi chú:** lịch sử ngắn 1.9 năm; ít lệnh 6; 1 đoạn WF gánh 68% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A22. GeneralTradingSarl/mql4_experts :: autopendingbyrsi.mq4

Nguồn: https://github.com/GeneralTradingSarl/mql4_experts

#### od_skea3279057100_XM_CSV 

- **Thẻ:** `sk_ea_3279057100` · **Cặp:** EURGBPmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 44.8%/năm kép · DD equity 63.4% (DD báo cáo 64.0%) · 203 lệnh · PF 1.24 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 31.0%/năm, DD 76.3%. Walk-forward 3 đoạn: 147 / -11 / 44 %/năm. MC DD p95: 93.7%.
- **Python trước MT5 (MÔ PHỎNG):** 39.2%/năm, DD 59.9%.
- **Ghi chú:** có đoạn WF âm (-11%/năm); 1 đoạn WF gánh 77% lãi; MC DD p95 94% > 80%; 10 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

#### od_skeaaba30a4e06_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_aba30a4e06` · **Cặp:** USDJPYmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) < 30.
- **BÁN** khi đồng thời: RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 21.9%/năm kép · DD equity 48.1% (DD báo cáo 49.7%) · 164 lệnh · PF 2.07 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 20.2%/năm, DD 48.4%. Walk-forward 3 đoạn: 39 / 17 / 12 %/năm. MC DD p95: 57.4%.
- **Python trước MT5 (MÔ PHỎNG):** 24.3%/năm, DD 51.4%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A23. freqtrade/freqtrade-strategies :: user_data/strategies/berlinguyinca/Low_BB.py

Nguồn: https://github.com/freqtrade/freqtrade-strategies/blob/HEAD/user_data/strategies/berlinguyinca/Low_BB.py

#### od_b0be91a35f43f34a_XM_CSV 

- **Thẻ:** `b0be91a35f43f34a` · **Cặp:** USDCADmicro · **TF:** H4 · **Kiểu dịch:** llm
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `llm`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 44.0%/năm kép · DD equity 57.2% (DD báo cáo 58.6%) · 46 lệnh · PF 0.00 · giai đoạn 2024.01.15–2026.10.01 (2.71 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 39.6%/năm, DD 61.8%. Walk-forward 3 đoạn: 82 / 25 / 31 %/năm. MC DD p95: 88.7%.
- **Python trước MT5 (MÔ PHỎNG):** 41.3%/năm, DD 55.2%.
- **Ghi chú:** MC DD p95 89% > 80%; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A24. alfredomaussa/MQL5 :: iMA_crossover.mq5

Nguồn: https://github.com/alfredomaussa/MQL5

#### od_skea31214192bc_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_31214192bc` · **Cặp:** GBPNZDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(20) cắt lên trên SMA(50).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 39.6%/năm kép · DD equity 29.6% (DD báo cáo 29.8%) · 36 lệnh · PF 0.00 · giai đoạn 2024.02.08–2026.10.01 (2.64 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 32.7%/năm, DD 32.0%. Walk-forward 3 đoạn: 54 / 40 / 26 %/năm. MC DD p95: 44.7%.
- **Python trước MT5 (MÔ PHỎNG):** 34.6%/năm, DD 43.2%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A25. AmonCheruiyotHQ/MQL4-Projects :: Binary Comodo.mq4

Nguồn: https://github.com/AmonCheruiyotHQ/MQL4-Projects

#### od_skeadc40280363_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_dc40280363` · **Cặp:** CADJPYmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Tin hieu mua khi EMA5 cat len EMA200 va RSI12 cat len 50 (state machine). Tin hieu ban nguoc lai.”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    close = df['close']
    ema5 = close.ewm(span=5, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/12, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/12, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    ema_cu = (ema5 > ema200) & (ema5.shift(1) <= ema200.shift(1))
    ema_cd = (ema5 < ema200) & (ema5.shift(1) >= ema200.shift(1))
    rsi_cu = (rsi > 50) & (rsi.shift(1) <= 50)
    rsi_cd = (rsi < 50) & (rsi.shift(1) >= 50)
    signals = np.zeros(len(df))
    st_ema = 0
    st_rsi = 0
    last_sig = 0
    for i in range(1, len(df)):
        if ema_cu.iloc[i]: st_ema = 1
        elif ema_cd.iloc[i]: st_ema = -1
        if rsi_cu.iloc[i]: st_rsi = 1
        elif rsi_cd.iloc[i]: st_rsi = -1
        if st_ema == 1 and st_rsi == 1 and last_sig != 1:
            signals[i] = 1
            last_sig = 1
        elif st_ema == -1 and st_rsi == -1 and last_sig != -1:
            signals[i] = -1
            last_sig = -1
    return signals
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 39.6%/năm kép · DD equity 37.2% (DD báo cáo 38.8%) · 160 lệnh · PF 2.74 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 37.7%/năm, DD 37.4%. Walk-forward 3 đoạn: 66 / 57 / 4 %/năm. MC DD p95: 47.6%.
- **Python trước MT5 (MÔ PHỎNG):** 37.4%/năm, DD 41.4%.
- **Ghi chú:** 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5); Bản dịch gần đúng/chưa dịch (nguyên văn): Code MQL4 goc co loi dung chi so -1 (du lieu tuong lai) cho iMA va iRSI (vi du Li_4 - 1). Da bo qua dieu kien nay va chi dung du lieu qua khu (shift 1) de tranh look-ahead bias..

### A26. Moving Average (MA) Crossover EA :: _HPCS_FastSlowMACrosssover_MT4_EA_V01_WE.mq4

Nguồn: https://www.mql5.com/en/code/37600

#### od_skea154c9fdee7_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_154c9fdee7` · **Cặp:** GBPCADmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(14) cắt lên trên SMA(21).
- **BÁN** khi đồng thời: SMA(14) cắt xuống dưới SMA(21).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 38.3%/năm kép · DD equity 57.0% (DD báo cáo 56.5%) · 182 lệnh · PF 2.60 · giai đoạn 2024.01.10–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 34.6%/năm, DD 59.8%. Walk-forward 3 đoạn: 55 / 38 / 24 %/năm. MC DD p95: 77.7%.
- **Python trước MT5 (MÔ PHỎNG):** 37.8%/năm, DD 58.2%.
- **Ghi chú:** 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A27. santiago-cruzlopez/MQL5 :: 02_Check_Open_Positions.mq5

Nguồn: https://github.com/santiago-cruzlopez/MQL5

#### od_skea8897567020_XM_CSV 

- **Thẻ:** `sk_ea_8897567020` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > giá mở cửa.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 37.3%/năm kép · DD equity 43.6% (DD báo cáo 45.6%) · 154 lệnh · PF 1.90 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 33.0%/năm, DD 45.8%. Walk-forward 3 đoạn: 49 / 51 / 17 %/năm. MC DD p95: 80.7%.
- **Python trước MT5 (MÔ PHỎNG):** 53.7%/năm, DD 35.5%.
- **Ghi chú:** MC DD p95 81% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A28. Periodic Range Breakout (Martingale) :: RangeBreakout.mq5

Nguồn: https://www.mql5.com/en/code/30560

#### od_skea89d6f8661b_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_89d6f8661b` · **Cặp:** AUDUSDmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Thu Hai 00:00 lay gia tam; dat stop tren/duoi tam +/- 100% ATR(20, D1); lenh dau cham thi vao (1 lenh/tuan)”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    idx = pd.DatetimeIndex(df.index)
    h = df['high']; l = df['low']; c = df['close']; o = df['open']
    ngay = idx.normalize()
    dh = h.groupby(ngay).max(); dl = l.groupby(ngay).min(); dc = c.groupby(ngay).last()
    tr = pd.concat([dh - dl, (dh - dc.shift(1)).abs(), (dl - dc.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(20, min_periods=20).mean().shift(1)
    a = pd.Series(atr.reindex(ngay).to_numpy(), index=df.index)
    tuan = np.asarray(ngay.asi8 // 86400000000000) - np.asarray(idx.dayofweek)
    dau = np.r_[True, tuan[1:] != tuan[:-1]]
    tam = pd.Series(np.where(dau, o.to_numpy(), np.nan), index=df.index).groupby(tuan).ffill()
    rg = pd.Series(np.where(dau, a.to_numpy(), np.nan), index=df.index).groupby(tuan).ffill()
    tren = tam + rg; duoi = tam - rg
    n = len(c); s = np.zeros(n, dtype=int)
    cv = c.to_numpy(); tv = tren.to_numpy(); dv = duoi.to_numpy(); tk = np.asarray(tuan)
    da = None
    for i in range(1, n):
        if np.isnan(tv[i]) or tk[i] == da:
            continue
        if cv[i] > tv[i]:
            s[i] = 1; da = tk[i]
        elif cv[i] < dv[i]:
            s[i] = -1; da = tk[i]
    return s
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 37.1%/năm kép · DD equity 32.6% (DD báo cáo 31.3%) · 75 lệnh · PF 28.73 · giai đoạn 2024.01.26–2026.10.01 (2.68 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 34.4%/năm, DD 33.5%. Walk-forward 3 đoạn: 61 / 4 / 54 %/năm. MC DD p95: 48.3%.
- **Python trước MT5 (MÔ PHỎNG):** 30.4%/năm, DD 36.7%.
- **Ghi chú:** 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5); Bản dịch gần đúng/chưa dịch (nguyên văn): ATR D1 tinh tu nen H1 gop theo ngay, chi ngay da dong; moc Thu Hai 00:00 = nen dau tien cua tuan (gio san).

### A29. huanghq2000/fx_trading :: StrategyTester-From2502-v3.0.htm

Nguồn: https://github.com/huanghq2000/fx_trading

#### od_skstc21c2acd239f3c87_XM_CSV 

- **Thẻ:** `sk_st_c21c2acd239f3c87` · **Cặp:** EURUSDmicro · **TF:** H1 · **Kiểu dịch:** lenh_ngoai
- **Điều kiện vào lệnh:**
- Không có công thức chỉ báo: điểm vào lấy **nguyên lệnh thật từ báo cáo/statement** của tác giả (17 lệnh vào, 2025-02-06 12:00 → 2026-05-29 22:54, mã EURUSD). Quy tắc vào lệnh gốc: CHƯA RÕ trong mã.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 37.1%/năm kép · DD equity 46.3% (DD báo cáo 49.7%) · 20 lệnh · PF 4.50 · giai đoạn 2025.01.30–2026.06.04 (1.34 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 34.4%/năm, DD 46.9%. Walk-forward 3 đoạn: 22 / 70 / 23 %/năm. MC DD p95: 47.7%.
- **Python trước MT5 (MÔ PHỎNG):** 41.2%/năm, DD 52.8%.
- **Ghi chú:** lịch sử ngắn 1.3 năm; ít lệnh 20; 1 đoạn WF gánh 61% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A30. GeneralTradingSarl/expert-mt5 :: alexav_d1_profit_gbpusd.mq5

Nguồn: https://github.com/GeneralTradingSarl/expert-mt5

#### od_skea45b39eb1d5_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_45b39eb1d5` · **Cặp:** AUDJPYmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá mở cửa của 1 nến trước < EMA(6) của giá cao của 1 nến trước; giá đóng cửa của 1 nến trước > EMA(6) của giá cao của 1 nến trước; RSI(10) của 1 nến trước > 60; RSI(10) của 1 nến trước < 80.
- **BÁN** khi đồng thời: giá mở cửa của 1 nến trước > EMA(6) của giá cao của 1 nến trước; giá đóng cửa của 1 nến trước < EMA(6) của giá cao của 1 nến trước; RSI(10) của 1 nến trước < 39; RSI(10) của 1 nến trước > 25.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 36.1%/năm kép · DD equity 46.0% (DD báo cáo 46.0%) · 202 lệnh · PF 8.07 · giai đoạn 2023.12.28–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 29.5%/năm, DD 50.8%. Walk-forward 3 đoạn: 80 / 16 / 21 %/năm. MC DD p95: 63.4%.
- **Python trước MT5 (MÔ PHỎNG):** 28.9%/năm, DD 45.7%.
- **Ghi chú:** 1 đoạn WF gánh 69% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A31. joaotorresmarques/mql4 :: Moving Average.mq4

Nguồn: https://github.com/joaotorresmarques/mql4

#### od_skeaa3d6925a71_XM_CSV 

- **Thẻ:** `sk_ea_a3d6925a71` · **Cặp:** AUDUSDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá mở cửa < SMA(12) của 5 nến trước; giá đóng cửa > SMA(12) của 5 nến trước.
- **BÁN** khi đồng thời: giá mở cửa > SMA(12) của 5 nến trước; giá đóng cửa < SMA(12) của 5 nến trước.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 32.6%/năm kép · DD equity 52.7% (DD báo cáo 56.0%) · 533 lệnh · PF 1.48 · giai đoạn 2024.01.01–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 26.7%/năm, DD 54.9%. Walk-forward 3 đoạn: 121 / 72 / -39 %/năm. MC DD p95: 81.5%.
- **Python trước MT5 (MÔ PHỎNG):** 34.6%/năm, DD 51.8%.
- **Ghi chú:** có đoạn WF âm (-39%/năm); 1 đoạn WF gánh 63% lãi; MC DD p95 82% > 80%; 18 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A32. Ghép vao_x_quan_li: zhutoutoutousan/profitable-expert-adviso × Marco210210/AI-Enhanced-HFT :: ReportTes

#### od_ghep89811dee41bce6b9_XM_CSV ✔ BỀN

- **Thẻ:** `ghep_89811dee41bce6b9` · **Cặp:** GOLDmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) của 2 nến trước ≤ 73; RSI(14) của 1 nến trước > 73.
- **BÁN** khi đồng thời: RSI(14) của 2 nến trước ≥ 90; RSI(14) của 1 nến trước < 90.
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `sk_ea_d5df5bc834`, phong cách quản lý của thẻ `sk_st_04d4e4af296fa5bc`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 32.4%/năm kép · DD equity 39.0% (DD báo cáo 39.5%) · 92 lệnh · PF 3.11 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 31.4%/năm, DD 40.0%. Walk-forward 3 đoạn: 31 / 38 / 29 %/năm. MC DD p95: 54.8%.
- **Python trước MT5 (MÔ PHỎNG):** 28.7%/năm, DD 58.4%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A33. diayuunr__ea-optimization-project__EA05_MACD_Momentum_EA05_MACD_Momentum/EA05_MACD_Momentum.mq5

Nguồn: https://github.com/diayuunr/ea-optimization-project/blob/main/EA05_MACD%20Momentum/EA05_MACD_Momentum.mq5

#### od_mql5fd4bc285e11ab5a1_XM_CSV 

- **Thẻ:** `mql5_fd4bc285e11ab5a1` · **Cặp:** EURCHFmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: MACD(12,26,9) đường chính của 1 nến trước ≤ MACD(12,26,9) đường tín hiệu của 1 nến trước; MACD(12,26,9) đường chính > MACD(12,26,9) đường tín hiệu. (EA gốc có SL 500.0 điểm / TP 1000.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **BÁN** khi đồng thời: MACD(12,26,9) đường chính của 1 nến trước ≥ MACD(12,26,9) đường tín hiệu của 1 nến trước; MACD(12,26,9) đường chính < MACD(12,26,9) đường tín hiệu. (EA gốc có SL 500.0 điểm / TP 1000.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 31.0%/năm kép · DD equity 46.5% (DD báo cáo 49.3%) · 138 lệnh · PF 1.83 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 28.8%/năm, DD 47.5%. Walk-forward 3 đoạn: 57 / 42 / -0 %/năm. MC DD p95: 64.0%.
- **Python trước MT5 (MÔ PHỎNG):** 25.5%/năm, DD 45.9%.
- **Ghi chú:** có đoạn WF âm (-0%/năm); 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A34. nkanven/MT4-MT5-Trading-EA-Collections :: MA Crossover.mq5

Nguồn: https://github.com/nkanven/MT4-MT5-Trading-EA-Collections

#### od_skea61c21a2049_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_61c21a2049` · **Cặp:** CADJPYmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(10) cắt lên trên SMA(20).
- **BÁN** khi đồng thời: SMA(10) cắt xuống dưới SMA(20).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 29.2%/năm kép · DD equity 27.1% (DD báo cáo 28.3%) · 219 lệnh · PF 2.15 · giai đoạn 2024.01.03–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 25.8%/năm, DD 28.7%. Walk-forward 3 đoạn: 35 / 37 / 17 %/năm. MC DD p95: 36.6%.
- **Python trước MT5 (MÔ PHỎNG):** 30.9%/năm, DD 30.2%.
- **Ghi chú:** 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A35. juanmql__expert-advisors__F01_Conservador_H4/F01_Conservador_H4.mq5

Nguồn: https://github.com/juanmql/expert-advisors/blob/main/F01_Conservador_H4.mq5

#### od_mql5e3c3e4f028dbab72_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_e3c3e4f028dbab72` · **Cặp:** EURCADmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: EMA(20) của 1 nến trước ≤ EMA(50) của 1 nến trước; EMA(20) > EMA(50); thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 900.0 điểm / TP 2700.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **BÁN** khi đồng thời: EMA(20) của 1 nến trước ≥ EMA(50) của 1 nến trước; EMA(20) < EMA(50); thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 900.0 điểm / TP 2700.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 29.1%/năm kép · DD equity 18.0% (DD báo cáo 18.4%) · 120 lệnh · PF 6.21 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 27.6%/năm, DD 18.3%. Walk-forward 3 đoạn: 47 / 19 / 23 %/năm. MC DD p95: 25.2%.
- **Python trước MT5 (MÔ PHỎNG):** 33.0%/năm, DD 18.7%.
- **Ghi chú:** 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A36. navamirhossein__MQL5__Experts_CrossMovingAverageEA/CrossMovingAverageEA.mq5

Nguồn: https://github.com/navamirhossein/MQL5/blob/main/Experts/CrossMovingAverageEA.mq5

#### od_mql5e31426a40a5897fc_XM_CSV 

- **Thẻ:** `mql5_e31426a40a5897fc` · **Cặp:** GBPUSDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > mức sóng của SMA(60) (ngưỡng SMA(240)); SMA(60) < SMA(240).
- **BÁN** khi đồng thời: giá đóng cửa < mức sóng của SMA(60) (ngưỡng SMA(240)); SMA(60) > SMA(240).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 28.7%/năm kép · DD equity 55.9% (DD báo cáo 58.7%) · 15 lệnh · PF 0.00 · giai đoạn 2024.02.28–2026.10.01 (2.59 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 28.0%/năm, DD 56.4%. Walk-forward 3 đoạn: 40 / 17 / 30 %/năm. MC DD p95: 63.6%.
- **Python trước MT5 (MÔ PHỎNG):** 26.1%/năm, DD 59.6%.
- **Ghi chú:** ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A37. Trend_Catcher :: trend_catcher.mq4

Nguồn: https://www.mql5.com/en/code/13661

#### od_skea2f7862a741_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_2f7862a741` · **Cặp:** AUDUSDmicro · **TF:** H4 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Close cat len PSAR(0.004,0.2), SMA50>SMA200, gia > SMA25 -> mua; nguoc lai ban”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    h = df['high'].to_numpy(float); l = df['low'].to_numpy(float); c = df['close'].to_numpy(float)
    n = len(c)
    st = 0.004; mx = 0.2
    sar = np.full(n, np.nan)
    if n < 3:
        return np.zeros(n, dtype=int)
    up = True; af = st; ep = h[0]; sar[0] = l[0]
    for i in range(1, n):
        p = sar[i - 1] + af * (ep - sar[i - 1])
        if up:
            p = min(p, l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < p:
                up = False; p = ep; ep = l[i]; af = st
            elif h[i] > ep:
                ep = h[i]; af = min(af + st, mx)
        else:
            p = max(p, h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > p:
                up = True; p = ep; ep = h[i]; af = st
            elif l[i] < ep:
                ep = l[i]; af = min(af + st, mx)
        sar[i] = p
    cs = pd.Series(c)
    m200 = cs.rolling(200, min_periods=200).mean().to_numpy()
    m50 = cs.rolling(50, min_periods=50).mean().to_numpy()
    m25 = cs.rolling(25, min_periods=25).mean().to_numpy()
    s = np.zeros(n, dtype=int)
    for i in range(1, n):
        if np.isnan(m200[i]):
            continue
        if c[i] > sar[i] and c[i - 1] < sar[i - 1] and m50[i] > m200[i] and c[i] > m25[i]:
            s[i] = 1
        elif c[i] < sar[i] and c[i - 1] > sar[i - 1] and m50[i] < m200[i] and c[i] < m25[i]:
            s[i] = -1
    return s
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 28.6%/năm kép · DD equity 16.2% (DD báo cáo 17.9%) · 71 lệnh · PF 5.81 · giai đoạn 2024.02.19–2026.10.01 (2.61 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 25.6%/năm, DD 17.1%. Walk-forward 3 đoạn: 33 / 28 / 23 %/năm. MC DD p95: 18.9%.
- **Python trước MT5 (MÔ PHỎNG):** 27.3%/năm, DD 21.3%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A38. freqtrade/freqtrade-strategies :: user_data/strategies/berlinguyinca/SmoothOperator.py

Nguồn: https://github.com/freqtrade/freqtrade-strategies/blob/HEAD/user_data/strategies/berlinguyinca/SmoothOperator.py

#### od_2600ea39abbd7b0f_XM_CSV ✔ BỀN

- **Thẻ:** `2600ea39abbd7b0f` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: CCI(20) < -200; RSI(14) < 30; giá đóng cửa > giá đóng cửa của 1 nến trước; giá thấp < SMA(20).
- **MUA** khi đồng thời: CCI(20) < -150; RSI(14) < 30; giá đóng cửa > giá đóng cửa của 1 nến trước.
- **MUA** khi đồng thời: CCI(20) của 1 nến trước < -100; RSI(14) của 1 nến trước < 30; giá đóng cửa > giá đóng cửa của 1 nến trước; giá thấp của 1 nến trước < SMA(20).
- **BÁN** khi đồng thời: CCI(20) > 200; RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 27.8%/năm kép · DD equity 25.3% (DD báo cáo 27.1%) · 131 lệnh · PF 2.09 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 25.1%/năm, DD 25.3%. Walk-forward 3 đoạn: 26 / 40 / 18 %/năm. MC DD p95: 53.0%.
- **Python trước MT5 (MÔ PHỎNG):** 26.4%/năm, DD 26.2%.
- **Ghi chú:** 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A39. Ghép vao_x_quan_li: juanmql__expert-advisors__B03_Stoch_Lent × schundi365/Wise-Expert :: report_G5_sess

#### od_ghepeab4082becc0e276_XM_CSV 

- **Thẻ:** `ghep_eab4082becc0e276` · **Cặp:** EURGBPmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: Stochastic(14,3) %K của 1 nến trước ≤ Stochastic(14,3,3) đường tín hiệu %D của 1 nến trước; Stochastic(14,3) %K > Stochastic(14,3,3) đường tín hiệu %D; Stochastic(14,3) %K < 25; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 600.0 điểm / TP 900.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **BÁN** khi đồng thời: Stochastic(14,3) %K của 1 nến trước ≥ Stochastic(14,3,3) đường tín hiệu %D của 1 nến trước; Stochastic(14,3) %K < Stochastic(14,3,3) đường tín hiệu %D; Stochastic(14,3) %K > 75; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 600.0 điểm / TP 900.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- Thẻ ghép chéo kiểu `vao_x_quan_li`: lấy điểm vào của thẻ `mql5_f3313c2c79f00c10`, phong cách quản lý của thẻ `sk_st_e2f178474ad772a7`.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 27.7%/năm kép · DD equity 56.3% (DD báo cáo 54.0%) · 124 lệnh · PF 3.38 · giai đoạn 2024.01.02–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 26.6%/năm, DD 57.3%. Walk-forward 3 đoạn: 29 / -22 / 87 %/năm. MC DD p95: 70.1%.
- **Python trước MT5 (MÔ PHỎNG):** 26.6%/năm, DD 55.1%.
- **Ghi chú:** có đoạn WF âm (-22%/năm); 1 đoạn WF gánh 75% lãi; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A40. Yahao277/NNFX-EA-mql4 :: Sinergia_HiLo.mq4

Nguồn: https://github.com/Yahao277/NNFX-EA-mql4

#### od_skeaf7a71f885d_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_f7a71f885d` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Mua khi gia cat len tren duong SSL (SMA High) va chuyen trang thai sang tang, ban khi gia cat xuong duoi duong SSL (SMA Low) va chuyen trang thai sang giam.”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    Lb = 10
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    sma_high = pd.Series(high).rolling(Lb).mean().shift(1).values
    sma_low = pd.Series(low).rolling(Lb).mean().shift(1).values
    n = len(df)
    signals = np.zeros(n)
    hlv = np.zeros(n)
    for i in range(1, n):
        if pd.isna(sma_high[i]) or pd.isna(sma_low[i]):
            hlv[i] = hlv[i-1]
            continue
        if close[i] > sma_high[i]:
            hld = 1
        elif close[i] < sma_low[i]:
            hld = -1
        else:
            hld = 0
        if hld != 0:
            hlv[i] = hld
        else:
            hlv[i] = hlv[i-1]
        if hlv[i] == 1 and hlv[i-1] == -1:
            signals[i] = 1
        elif hlv[i] == -1 and hlv[i-1] == 1:
            signals[i] = -1
    return signals
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 27.5%/năm kép · DD equity 32.0% (DD báo cáo 35.4%) · 479 lệnh · PF 1.63 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 23.4%/năm, DD 35.1%. Walk-forward 3 đoạn: 14 / 41 / 30 %/năm. MC DD p95: 65.4%.
- **Python trước MT5 (MÔ PHỎNG):** 25.5%/năm, DD 48.0%.
- **Ghi chú:** 6 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A41. smizxe__mt5-agent-toolkit__src_Experts_RsiLevel/RsiLevel.mq5

Nguồn: https://github.com/smizxe/mt5-agent-toolkit/blob/main/src/Experts/RsiLevel.mq5

#### od_mql5ad7d22b5b165a673_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_ad7d22b5b165a673` · **Cặp:** GBPUSDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) < 30.
- **BÁN** khi đồng thời: RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 27.2%/năm kép · DD equity 53.6% (DD báo cáo 55.0%) · 134 lệnh · PF 2.36 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 25.1%/năm, DD 55.0%. Walk-forward 3 đoạn: 28 / 37 / 17 %/năm. MC DD p95: 74.4%.
- **Python trước MT5 (MÔ PHỎNG):** 20.3%/năm, DD 60.9%.
- **Ghi chú:** 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A42. 97joseph/MultiCurrencyStrength :: Breakout2.mq5

Nguồn: https://github.com/97joseph/MultiCurrencyStrength

#### od_skeafdbf5bcad6_XM_CSV 

- **Thẻ:** `sk_ea_fdbf5bcad6` · **Cặp:** EURCADmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > 1×[đỉnh trong khung giờ 0–7h] + -0.5×[đỉnh trong khung giờ 0–7h] + 0.5×[đáy trong khung giờ 0–7h]; giờ (server) = 8.
- **BÁN** khi đồng thời: giá đóng cửa < 1×[đáy trong khung giờ 0–7h] + 0.5×[đỉnh trong khung giờ 0–7h] + -0.5×[đáy trong khung giờ 0–7h]; giờ (server) = 8.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 26.5%/năm kép · DD equity 18.9% (DD báo cáo 18.2%) · 190 lệnh · PF 1.94 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 17.8%/năm, DD 20.9%. Walk-forward 3 đoạn: 45 / 64 / -12 %/năm. MC DD p95: 50.5%.
- **Python trước MT5 (MÔ PHỎNG):** 24.4%/năm, DD 18.7%.
- **Ghi chú:** có đoạn WF âm (-12%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A43. Gold Breakout EA for XAUUSD H4 +90 Percent in a 2020 to 2026 Backtest :: GoldBreakoutEA.mq5

Nguồn: https://www.mql5.com/en/code/77691

#### od_skeabc8157a270_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_bc8157a270` · **Cặp:** NZDJPYmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa của 1 nến trước > giá trị cao nhất 20 nến của giá cao của 2 nến trước; giá đóng cửa của 2 nến trước ≤ giá trị cao nhất 20 nến của giá cao của 3 nến trước; giá đóng cửa của 1 nến trước > EMA(200) của 1 nến trước.
- **BÁN** khi đồng thời: giá đóng cửa của 1 nến trước < giá trị thấp nhất 20 nến của giá thấp của 2 nến trước; giá đóng cửa của 2 nến trước ≥ giá trị thấp nhất 20 nến của giá thấp của 3 nến trước; giá đóng cửa của 1 nến trước < EMA(200) của 1 nến trước.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 25.2%/năm kép · DD equity 59.5% (DD báo cáo 60.2%) · 292 lệnh · PF 1.69 · giai đoạn 2024.01.03–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 20.8%/năm, DD 62.0%. Walk-forward 3 đoạn: 36 / 10 / 30 %/năm. MC DD p95: 66.4%.
- **Python trước MT5 (MÔ PHỎNG):** 19.5%/năm, DD 23.6%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A44. juanmql__expert-advisors__F03_TrailingPuro_H4/F03_TrailingPuro_H4.mq5

Nguồn: https://github.com/juanmql/expert-advisors/blob/main/F03_TrailingPuro_H4.mq5

#### od_mql5d8f573b8c2314bbf_XM_CSV 

- **Thẻ:** `mql5_d8f573b8c2314bbf` · **Cặp:** EURAUDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: EMA(20) của 1 nến trước ≤ EMA(50) của 1 nến trước; EMA(20) > EMA(50); thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6.
- **BÁN** khi đồng thời: EMA(20) của 1 nến trước ≥ EMA(50) của 1 nến trước; EMA(20) < EMA(50); thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 24.5%/năm kép · DD equity 47.1% (DD báo cáo 41.4%) · 106 lệnh · PF 1.60 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 19.5%/năm, DD 49.2%. Walk-forward 3 đoạn: 82 / 43 / -26 %/năm. MC DD p95: 58.6%.
- **Python trước MT5 (MÔ PHỎNG):** 25.2%/năm, DD 34.4%.
- **Ghi chú:** có đoạn WF âm (-26%/năm); 1 đoạn WF gánh 65% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A45. huanghq2000/fx_trading :: StrategyTester-h4v2.0.htm

Nguồn: https://github.com/huanghq2000/fx_trading

#### od_skstaca366b679c75482_XM_CSV 

- **Thẻ:** `sk_st_aca366b679c75482` · **Cặp:** EURUSDmicro · **TF:** H1 · **Kiểu dịch:** lenh_ngoai
- **Điều kiện vào lệnh:**
- Không có công thức chỉ báo: điểm vào lấy **nguyên lệnh thật từ báo cáo/statement** của tác giả (19 lệnh vào, 2025-02-06 12:00 → 2026-05-28 01:30, mã EURUSD). Quy tắc vào lệnh gốc: CHƯA RÕ trong mã.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 24.4%/năm kép · DD equity 18.3% (DD báo cáo 18.2%) · 15 lệnh · PF 0.00 · giai đoạn 2025.01.30–2026.06.03 (1.34 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 22.6%/năm, DD 18.4%. Walk-forward 3 đoạn: 15 / 27 / 33 %/năm. MC DD p95: 21.0%.
- **Python trước MT5 (MÔ PHỎNG):** 23.9%/năm, DD 18.4%.
- **Ghi chú:** lịch sử ngắn 1.3 năm; ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A46. victor-algo/channel :: morning-buy-us.mq5

Nguồn: https://github.com/victor-algo/channel

#### od_skea0806a3a5e5_XM_CSV 

- **Thẻ:** `sk_ea_0806a3a5e5` · **Cặp:** AUDNZDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa dịch”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 24.4%/năm kép · DD equity 24.6% (DD báo cáo 25.9%) · 29 lệnh · PF 10.57 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 23.3%/năm, DD 25.0%. Walk-forward 3 đoạn: 19 / 14 / 41 %/năm. MC DD p95: 44.0%.
- **Python trước MT5 (MÔ PHỎNG):** 44.3%/năm, DD 38.6%.
- **Ghi chú:** ít lệnh 29; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A47. New Martin :: New_Martin.mq5

Nguồn: https://www.mql5.com/en/code/17438

#### od_skea0cc19095a9_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_0cc19095a9` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 24.3%/năm kép · DD equity 27.5% (DD báo cáo 28.9%) · 429 lệnh · PF 1.66 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 20.8%/năm, DD 28.7%. Walk-forward 3 đoạn: 23 / 33 / 18 %/năm. MC DD p95: 39.6%.
- **Python trước MT5 (MÔ PHỎNG):** 44.5%/năm, DD 50.7%.
- **Ghi chú:** 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A48. Monkeyattack/monkeyattack-gold-pivot-ea :: Moving Average.mq4

Nguồn: https://github.com/Monkeyattack/monkeyattack-gold-pivot-ea

#### od_skea0ab6e87da9_XM_CSV 

- **Thẻ:** `sk_ea_0ab6e87da9` · **Cặp:** EURGBPmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá mở cửa < SMA(12) của 5 nến trước; giá đóng cửa > SMA(12) của 5 nến trước.
- **BÁN** khi đồng thời: giá mở cửa > SMA(12) của 5 nến trước; giá đóng cửa < SMA(12) của 5 nến trước.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 22.8%/năm kép · DD equity 74.4% (DD báo cáo 75.7%) · 245 lệnh · PF 1.57 · giai đoạn 2024.01.03–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 18.1%/năm, DD 79.1%. Walk-forward 3 đoạn: 18 / 34 / 18 %/năm. MC DD p95: 86.5%.
- **Python trước MT5 (MÔ PHỎNG):** 22.1%/năm, DD 47.6%.
- **Ghi chú:** MC DD p95 86% > 80%; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A49. MA2CCI :: MA2CCI.mq4

Nguồn: https://www.mql5.com/en/code/10363

#### od_skea363d6c8238_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_363d6c8238` · **Cặp:** NZDJPYmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(4) cắt lên trên SMA(8); CCI(4) cắt lên trên 0.
- **BÁN** khi đồng thời: SMA(4) cắt xuống dưới SMA(8); CCI(4) cắt xuống dưới 0.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 22.6%/năm kép · DD equity 30.5% (DD báo cáo 33.0%) · 63 lệnh · PF 3.77 · giai đoạn 2024.01.24–2026.10.01 (2.68 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 21.6%/năm, DD 30.8%. Walk-forward 3 đoạn: 22 / 31 / 16 %/năm. MC DD p95: 39.0%.
- **Python trước MT5 (MÔ PHỎNG):** 20.9%/năm, DD 30.9%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A50. GridPro Panel — open-source grid trading EA with on-chart control panel :: GridPro_Panel_v1.mq5

Nguồn: https://www.mql5.com/en/code/78206

#### od_skea66a65a142a_XM_CSV 

- **Thẻ:** `sk_ea_66a65a142a` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: EMA(10) cắt lên trên EMA(30).
- **BÁN** khi đồng thời: EMA(10) cắt xuống dưới EMA(30).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 22.5%/năm kép · DD equity 50.2% (DD báo cáo 53.0%) · 263 lệnh · PF 1.17 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 12.2%/năm, DD 55.1%. Walk-forward 3 đoạn: 47 / 52 / -20 %/năm. MC DD p95: 90.6%.
- **Python trước MT5 (MÔ PHỎNG):** 20.2%/năm, DD 62.1%.
- **Ghi chú:** có đoạn WF âm (-20%/năm); MC DD p95 91% > 80%; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A51. freqtrade/freqtrade-strategies :: user_data/strategies/multi_tf.py

Nguồn: https://github.com/freqtrade/freqtrade-strategies/blob/HEAD/user_data/strategies/multi_tf.py

#### od_0557d803384c6211_XM_CSV ✔ BỀN

- **Thẻ:** `0557d803384c6211` · **Cặp:** GBPUSDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) < 30.
- **BÁN** khi đồng thời: RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 22.2%/năm kép · DD equity 46.1% (DD báo cáo 47.1%) · 182 lệnh · PF 2.30 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 19.2%/năm, DD 46.9%. Walk-forward 3 đoạn: 30 / 23 / 14 %/năm. MC DD p95: 55.5%.
- **Python trước MT5 (MÔ PHỎNG):** 19.5%/năm, DD 59.0%.
- **Ghi chú:** 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A52. Nhập tay: trang_luu_tay.html

#### od_nhapcf8073245473d2a1_XM_CSV 

- **Thẻ:** `nhap_cf8073245473d2a1` · **Cặp:** EURGBPmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **BÁN** khi đồng thời: RSI(3) ≤ 30.
- **MUA** khi đồng thời: RSI(3) ≥ 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 20.8%/năm kép · DD equity 78.2% (DD báo cáo 67.8%) · 188 lệnh · PF 1.42 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 17.8%/năm, DD 81.9%. Walk-forward 3 đoạn: 16 / -22 / 114 %/năm. MC DD p95: 92.1%.
- **Python trước MT5 (MÔ PHỎNG):** 22.0%/năm, DD 59.7%.
- **Ghi chú:** có đoạn WF âm (-22%/năm); 1 đoạn WF gánh 88% lãi; MC DD p95 92% > 80%; 10 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A53. FX-CHAOS_SCALP :: FX-AO.mq4

Nguồn: https://www.mql5.com/en/code/8053

#### od_skeae2482b06a4_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_e2482b06a4` · **Cặp:** GBPUSDmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Mua khi AO chuyen sang mau xanh (tang), Ban khi AO chuyen sang mau do (giam)”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    high = df['high'].values
    low = df['low'].values
    n = len(df)
    median = [(high[i] + low[i]) / 2.0 for i in range(n)]
    ao = [0.0] * n
    for i in range(4, n):
        ao[i] += sum(median[i-4:i+1]) / 5.0
    for i in range(33, n):
        ao[i] -= sum(median[i-33:i+1]) / 34.0
    signals = [0] * n
    for i in range(35, n):
        curr = ao[i]
        prev1 = ao[i-1]
        prev2 = ao[i-2]
        if curr > prev1 and prev1 <= prev2:
            signals[i] = 1
        elif curr < prev1 and prev1 >= prev2:
            signals[i] = -1
    return signals
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **0.3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 20.6%/năm kép · DD equity 41.2% (DD báo cáo 41.9%) · 1338 lệnh · PF 1.54 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 17.3%/năm, DD 42.3%. Walk-forward 3 đoạn: 28 / 25 / 9 %/năm. MC DD p95: 50.0%.
- **Python trước MT5 (MÔ PHỎNG):** 18.6%/năm, DD 43.2%.
- **Ghi chú:** 8 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5); Bản dịch gần đúng/chưa dịch (nguyên văn): Code MQL4 ghi iMA period 2, shift 1 va period 13, shift 8. Day la loi OCR tu anh goc, vi SetIndexDrawBegin la 34 va Awesome Oscillator chuan la SMA(Median, 5) va SMA(Median, 34). Da dung 5 va 34 de tinh toan..

### A54. pipbolt/experts :: Moving-Average-Cross-EA.mq5

Nguồn: https://github.com/pipbolt/experts

#### od_skea09c76b6df5_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_09c76b6df5` · **Cặp:** GBPAUDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: SMA(12) cắt lên trên SMA(30).
- **BÁN** khi đồng thời: SMA(12) cắt xuống dưới SMA(30).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 20.2%/năm kép · DD equity 34.4% (DD báo cáo 34.5%) · 224 lệnh · PF 1.98 · giai đoạn 2024.01.16–2026.10.01 (2.70 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.3%/năm, DD 35.8%. Walk-forward 3 đoạn: 30 / 19 / 12 %/năm. MC DD p95: 72.8%.
- **Python trước MT5 (MÔ PHỎNG):** 20.5%/năm, DD 38.7%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A55. juanmql__expert-advisors__D01_Bollinger_Ruptura_H1/D01_Bollinger_Ruptura_H1.mq5

Nguồn: https://github.com/juanmql/expert-advisors/blob/main/D01_Bollinger_Ruptura_H1.mq5

#### od_mql5b39a9f3ba216fb47_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_b39a9f3ba216fb47` · **Cặp:** CHFJPYmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: Bollinger(20, 2.0) dải trên < giá đóng cửa; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 400.0 điểm / TP 1000.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **0.3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 19.6%/năm kép · DD equity 28.6% (DD báo cáo 27.1%) · 392 lệnh · PF 1.81 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 18.2%/năm, DD 29.7%. Walk-forward 3 đoạn: 27 / 22 / 11 %/năm. MC DD p95: 40.1%.
- **Python trước MT5 (MÔ PHỎNG):** 22.3%/năm, DD 44.8%.
- **Ghi chú:** 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A56. Spoofiecus__MetaTrader5-ExpertAdvisors__BollingerBands_EA/BollingerBands_EA.mq5

Nguồn: https://github.com/Spoofiecus/MetaTrader5-ExpertAdvisors/blob/ma-crossover-ea/BollingerBands_EA.mq5

#### od_mql525573694a7f03d3a_XM_CSV 

- **Thẻ:** `mql5_25573694a7f03d3a` · **Cặp:** EURGBPmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá thấp của 1 nến trước < Bollinger(20, 2.0) dải dưới của 1 nến trước; giá thấp ≥ Bollinger(20, 2.0) dải dưới. (EA gốc có SL 50.0 điểm / TP 100.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **BÁN** khi đồng thời: giá cao của 1 nến trước > Bollinger(20, 2.0) dải trên của 1 nến trước; giá cao ≤ Bollinger(20, 2.0) dải trên. (EA gốc có SL 50.0 điểm / TP 100.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 19.5%/năm kép · DD equity 33.4% (DD báo cáo 31.5%) · 282 lệnh · PF 2.22 · giai đoạn 2023.12.27–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 17.4%/năm, DD 35.2%. Walk-forward 3 đoạn: 20 / -13 / 61 %/năm. MC DD p95: 49.0%.
- **Python trước MT5 (MÔ PHỎNG):** 18.7%/năm, DD 30.0%.
- **Ghi chú:** có đoạn WF âm (-13%/năm); 1 đoạn WF gánh 75% lãi; 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A57. DAAC11/Test :: T14RegMA.mq4

Nguồn: https://github.com/DAAC11/Test

#### od_skea5539346824_XM_CSV 

- **Thẻ:** `sk_ea_5539346824` · **Cặp:** EURGBPmicro · **TF:** H1 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “SMA50(median) > open va |SMA-close| > trung binh do lech 199 nen -> mua; SMA < close va lech lon -> ban”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    c = df['close']; o = df['open']
    m = ((df['high'] + df['low']) / 2.0).rolling(50, min_periods=50).mean()
    lech = (m - c).abs()
    avg = lech.shift(1).rolling(199, min_periods=199).sum() / 199.0
    xa = (m - c).abs() > avg
    mua = (m > o) & xa
    ban = (m < c) & xa & ~mua
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 19.3%/năm kép · DD equity 48.9% (DD báo cáo 46.5%) · 233 lệnh · PF 1.77 · giai đoạn 2024.01.09–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 14.9%/năm, DD 53.4%. Walk-forward 3 đoạn: 20 / -15 / 67 %/năm. MC DD p95: 65.5%.
- **Python trước MT5 (MÔ PHỎNG):** 18.8%/năm, DD 46.2%.
- **Ghi chú:** có đoạn WF âm (-15%/năm); 1 đoạn WF gánh 77% lãi; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5); Bản dịch gần đúng/chưa dịch (nguyên văn): EA doc nen 0 (dang chay); dung nen da dong.

### A58. zhihua045-ui__free-mt5-ea-source-code__RSI_SinglePosition/RSI_SinglePosition.mq5

Nguồn: https://github.com/zhihua045-ui/free-mt5-ea-source-code/blob/main/RSI_SinglePosition.mq5

#### od_mql5b5a04d7c15935f8b_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_b5a04d7c15935f8b` · **Cặp:** GBPNZDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) < 30.
- **BÁN** khi đồng thời: RSI(14) > 70.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 18.3%/năm kép · DD equity 29.3% (DD báo cáo 33.3%) · 208 lệnh · PF 1.45 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 14.7%/năm, DD 31.8%. Walk-forward 3 đoạn: 6 / 26 / 24 %/năm. MC DD p95: 55.4%.
- **Python trước MT5 (MÔ PHỎNG):** 17.7%/năm, DD 36.0%.
- **Ghi chú:** 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A59. need an EA made from an indicator :: BBands_Stop_v1.mq4

Nguồn: https://www.forexfactory.com/thread/1356727-need-an-ea-made-from-an-indicator

#### od_skead0a7af9f8b_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_d0a7af9f8b` · **Cặp:** AUDJPYmicro · **TF:** H4 · **Kiểu dịch:** python_llm
- **Điều kiện vào lệnh:**
- Mô tả trong thẻ (nguyên văn, không dấu): “Mua khi gia cat len tren dai tren Bollinger Bands (trend flip len 1), Ban khi gia cat xuong duoi dai duoi (trend flip xuong -1).”
- Bản dịch Python (`tin_hieu`, 1 = mua, −1 = bán):

```python
def tin_hieu(df):
    c = df['close'].values
    n = len(c)
    out = np.zeros(n)
    if n < 21: return out
    s = pd.Series(c)
    sma = s.rolling(20).mean().values
    std = s.rolling(20).std(ddof=0).values
    up = sma + 2.0 * std
    dn = sma - 2.0 * std
    trend = 0
    for i in range(20, n):
        prev_trend = trend
        if c[i] > up[i-1]:
            trend = 1
        elif c[i] < dn[i-1]:
            trend = -1
        if trend == 1 and prev_trend <= 0:
            out[i] = 1
        elif trend == -1 and prev_trend >= 0:
            out[i] = -1
    return out
```
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 17.9%/năm kép · DD equity 7.2% (DD báo cáo 8.4%) · 158 lệnh · PF 7.97 · giai đoạn 2024.01.02–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.7%/năm, DD 7.2%. Walk-forward 3 đoạn: 22 / 21 / 11 %/năm. MC DD p95: 7.9%.
- **Python trước MT5 (MÔ PHỎNG):** 18.6%/năm, DD 11.9%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A60. juanmql__expert-advisors__B04_Bollinger_Reversion_M15/B04_Bollinger_Reversion_M15.mq5

Nguồn: https://github.com/juanmql/expert-advisors/blob/main/B04_Bollinger_Reversion_M15.mq5

#### od_mql5a790e25e547f0b57_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_a790e25e547f0b57` · **Cặp:** AUDNZDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: Bollinger(20, 2.0) dải dưới > giá đóng cửa; thứ trong tuần (0=thứ Hai) ≠ 0; thứ trong tuần (0=thứ Hai) ≠ 6. (EA gốc có SL 250.0 điểm / TP 250.0 điểm — bộ quản lý lệnh trong lần đo MT5 dùng tham số riêng bên dưới.)
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 17.5%/năm kép · DD equity 19.6% (DD báo cáo 20.9%) · 31 lệnh · PF 24.36 · giai đoạn 2024.01.02–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.2%/năm, DD 19.9%. Walk-forward 3 đoạn: 12 / 17 / 22 %/năm. MC DD p95: 40.7%.
- **Python trước MT5 (MÔ PHỎNG):** 20.3%/năm, DD 20.2%.
- **Ghi chú:** 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A61. Hybrid Scalper :: hybrid_Scalper.mq4

Nguồn: https://www.mql5.com/en/code/12298

#### od_skea0ab4d307d3_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_0ab4d307d3` · **Cặp:** EURNZDmicro · **TF:** H1 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 17.5%/năm kép · DD equity 38.8% (DD báo cáo 48.6%) · 286 lệnh · PF 1.39 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 14.0%/năm, DD 40.3%. Walk-forward 3 đoạn: 23 / 23 / 7 %/năm. MC DD p95: 62.7%.
- **Python trước MT5 (MÔ PHỎNG):** 20.9%/năm, DD 42.4%.
- **Ghi chú:** 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A62. (tên EA gốc CHƯA RÕ trong mã) — thẻ to_hop_564be9bb91406c57

#### od_tohop564be9bb91406c57_XM_CSV ✔ BỀN

- **Thẻ:** `to_hop_564be9bb91406c57` · **Cặp:** GBPUSDmicro · **TF:** H1 · **Kiểu dịch:** CHƯA RÕ trong mã
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ không có trong CSDL box; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 17.4%/năm kép · DD equity 26.9% (DD báo cáo 26.2%) · 62 lệnh · PF 2.54 · giai đoạn 2024.01.12–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 16.3%/năm, DD 27.5%. Walk-forward 3 đoạn: 19 / 17 / 17 %/năm. MC DD p95: 38.5%.
- **Python trước MT5 (MÔ PHỎNG):** 16.8%/năm, DD 27.4%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A63. RSI 50 X Scalping System :: Advanced MTF RSI.mq4

Nguồn: https://www.forexfactory.com/thread/1209024-rsi-50-x-scalping-system

#### od_skeaf3d30ea9da_XM_CSV ✔ BỀN

- **Thẻ:** `sk_ea_f3d30ea9da` · **Cặp:** GBPAUDmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: RSI(14) > 50; RSI(14) của 1 nến trước ≤ 50.
- **BÁN** khi đồng thời: RSI(14) < 50; RSI(14) của 1 nến trước ≥ 50.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.50% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **0.3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 16.9%/năm kép · DD equity 44.4% (DD báo cáo 47.2%) · 956 lệnh · PF 1.56 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 13.9%/năm, DD 45.0%. Walk-forward 3 đoạn: 18 / 16 / 19 %/năm. MC DD p95: 49.6%.
- **Python trước MT5 (MÔ PHỎNG):** 18.8%/năm, DD 37.2%.
- **Ghi chú:** 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A64. Tổ hợp: ma_ban_ema12_duoi_ema26_va_ema12_tre1_tr + DCA deu 0,5% x5, TP 0,2%

#### od_tohop09a3b2ddc3e78dc8_XM_CSV ✔ BỀN

- **Thẻ:** `to_hop_09a3b2ddc3e78dc8` · **Cặp:** EURUSDmicro · **TF:** H4 · **Kiểu dịch:** to_hop
- **Điều kiện vào lệnh:**
- **BÁN** khi đồng thời: EMA(12) < EMA(26); EMA(12) của 1 nến trước ≥ EMA(26) của 1 nến trước.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 15.6%/năm kép · DD equity 31.6% (DD báo cáo 32.0%) · 69 lệnh · PF 2.41 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 14.5%/năm, DD 32.4%. Walk-forward 3 đoạn: 22 / 8 / 18 %/năm. MC DD p95: 44.5%.
- **Python trước MT5 (MÔ PHỎNG):** 20.6%/năm, DD 21.4%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A65. (tên EA gốc CHƯA RÕ trong mã) — thẻ to_hop_c2d52300cc825dff

#### od_tohopc2d52300cc825dff_XM_CSV 

- **Thẻ:** `to_hop_c2d52300cc825dff` · **Cặp:** AUDNZDmicro · **TF:** H1 · **Kiểu dịch:** CHƯA RÕ trong mã
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ không có trong CSDL box; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot nhân hệ số × 1.3 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 14.4%/năm kép · DD equity 26.1% (DD báo cáo 25.6%) · 144 lệnh · PF 1.66 · giai đoạn 2024.01.03–2026.10.01 (2.74 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 11.6%/năm, DD 29.1%. Walk-forward 3 đoạn: -15 / 32 / 34 %/năm. MC DD p95: 45.4%.
- **Python trước MT5 (MÔ PHỎNG):** 17.1%/năm, DD 42.5%.
- **Ghi chú:** có đoạn WF âm (-15%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A66. freqtrade/freqtrade-strategies :: user_data/strategies/Strategy002.py

Nguồn: https://github.com/freqtrade/freqtrade-strategies/blob/HEAD/user_data/strategies/Strategy002.py

#### od_3304d2fad28adef6_XM_CSV 

- **Thẻ:** `3304d2fad28adef6` · **Cặp:** USDCADmicro · **TF:** H4 · **Kiểu dịch:** llm
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `llm`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- Mô tả cơ chế ghi trong thẻ (bản dịch bị đánh `HONG`, nên không chắc đây là công thức đã sinh CSV; nguyên văn): “RSI < 30, Stoch SlowK < 20, Close < BB Lower, CDLHAMMER”.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.10%** (InpTPPct=0.001).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **6 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 20% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **10 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 14.2%/năm kép · DD equity 47.3% (DD báo cáo 40.2%) · 64 lệnh · PF 1.66 · giai đoạn 2024.02.28–2026.10.01 (2.59 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 9.1%/năm, DD 51.5%. Walk-forward 3 đoạn: 19 / 26 / -1 %/năm. MC DD p95: 60.4%.
- **Python trước MT5 (MÔ PHỎNG):** 23.2%/năm, DD 17.4%.
- **Ghi chú:** có đoạn WF âm (-1%/năm); chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A67. Yumerain__EA-MQL4__Experts_OKMA_mq4/OKMA.mq4

Nguồn: https://github.com/Yumerain/EA-MQL4/blob/master/Experts/OKMA.mq4

#### od_mql5e52afb999eca4bd1_XM_CSV ✔ BỀN

- **Thẻ:** `mql5_e52afb999eca4bd1` · **Cặp:** EURGBPmicro · **TF:** H1 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: giá đóng cửa > mức sóng của EMA(15) (ngưỡng SMA(50)); giá đóng cửa > mức sóng của EMA(144) (ngưỡng EMA(169)).
- **BÁN** khi đồng thời: giá đóng cửa < mức sóng của EMA(15) (ngưỡng SMA(50)); giá đóng cửa < mức sóng của EMA(144) (ngưỡng EMA(169)).
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 1.20% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 13.7%/năm kép · DD equity 30.0% (DD báo cáo 24.9%) · 110 lệnh · PF 1.39 · giai đoạn 2023.12.28–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 11.7%/năm, DD 31.7%. Walk-forward 3 đoạn: 10 / 2 / 33 %/năm. MC DD p95: 58.9%.
- **Python trước MT5 (MÔ PHỎNG):** 17.7%/năm, DD 20.3%.
- **Ghi chú:** 1 đoạn WF gánh 74% lãi; 6 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A68. GeneralTradingSarl/expert-mt5 :: badx.mq5

Nguồn: https://github.com/GeneralTradingSarl/expert-mt5

#### od_skea7eec0ab393_XM_CSV 

- **Thẻ:** `sk_ea_7eec0ab393` · **Cặp:** GBPAUDmicro · **TF:** H4 · **Kiểu dịch:** spec
- **Điều kiện vào lệnh:**
- **MUA** khi đồng thời: ADX(30) < 20; giá đóng cửa < Bollinger(10, 1.5) dải dưới.
- **BÁN** khi đồng thời: ADX(30) < 20; giá đóng cửa > Bollinger(10, 1.5) dải trên.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.30%** (InpTPPct=0.003).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot nhân hệ số × 1.6 mỗi tầng; tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: khóa bằng lệnh ngược khi rổ lỗ thả nổi ≥ 10% số dư (khối lượng ×1, tối đa 3 lần/rổ, mở khóa khi giá hồi 0.50%).
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 13.1%/năm kép · DD equity 59.5% (DD báo cáo 53.0%) · 294 lệnh · PF 1.20 · giai đoạn 2024.01.17–2026.10.01 (2.70 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 8.6%/năm, DD 62.5%. Walk-forward 3 đoạn: 56 / 18 / -21 %/năm. MC DD p95: 81.8%.
- **Python trước MT5 (MÔ PHỎNG):** 21.4%/năm, DD 55.2%.
- **Ghi chú:** có đoạn WF âm (-21%/năm); 1 đoạn WF gánh 76% lãi; MC DD p95 82% > 80%; 8 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A69. (tên EA gốc CHƯA RÕ trong mã) — thẻ to_hop_9acc6e0d2f784cb9

#### od_tohop9acc6e0d2f784cb9_XM_CSV ✔ BỀN

- **Thẻ:** `to_hop_9acc6e0d2f784cb9` · **Cặp:** GBPCADmicro · **TF:** H1 · **Kiểu dịch:** CHƯA RÕ trong mã
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ không có trong CSDL box; ghi chú kho cơ chế: “—”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.80% giá lệnh đầu; lot đều (không nhân); tối đa **4 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **1 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 12.9%/năm kép · DD equity 10.4% (DD báo cáo 10.6%) · 59 lệnh · PF 7.80 · giai đoạn 2024.01.10–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 12.4%/năm, DD 10.4%. Walk-forward 3 đoạn: 17 / 8 / 15 %/năm. MC DD p95: 19.1%.
- **Python trước MT5 (MÔ PHỎNG):** 16.6%/năm, DD 14.2%.
- **Ghi chú:** chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A70. freqtrade/freqtrade-strategies :: user_data/strategies/berlinguyinca/BbandRsi.py

Nguồn: https://github.com/freqtrade/freqtrade-strategies/blob/HEAD/user_data/strategies/berlinguyinca/BbandRsi.py

#### od_018dcb1347276c97_XM_CSV ✔ BỀN

- **Thẻ:** `018dcb1347276c97` · **Cặp:** EURNZDmicro · **TF:** H4 · **Kiểu dịch:** llm
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `llm`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- Mô tả cơ chế ghi trong thẻ (bản dịch bị đánh `HONG`, nên không chắc đây là công thức đã sinh CSV; nguyên văn): “RSI < 30 va Gia dong cua < Band duoi Bollinger”.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.20%** (InpTPPct=0.002).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: không (1 lệnh/rổ).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **3 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 12.1%/năm kép · DD equity 14.8% (DD báo cáo 18.4%) · 76 lệnh · PF 5.55 · giai đoạn 2024.01.10–2026.10.01 (2.72 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 10.8%/năm, DD 15.0%. Walk-forward 3 đoạn: 8 / 22 / 7 %/năm. MC DD p95: 28.8%.
- **Python trước MT5 (MÔ PHỎNG):** 22.9%/năm, DD 26.0%.
- **Ghi chú:** 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

### A71. RSI Bot MT5 :: RSI_Alert.mq5

Nguồn: https://www.mql5.com/en/code/41739

#### od_skea0757c93eb3_XM_CSV 

- **Thẻ:** `sk_ea_0757c93eb3` · **Cặp:** EURNZDmicro · **TF:** H4 · **Kiểu dịch:** mt5_truc_tiep
- **Điều kiện vào lệnh:**
- CHƯA RÕ trong mã (thẻ chạy kiểu `mt5_truc_tiep`; ghi chú kho cơ chế: “chưa có trong cache box”). Lệnh vào MT5 được đọc từ tệp CSV do Python sinh, nhưng công thức sinh không còn lưu trong thẻ/CSDL trong repo.
- **Quản lý lệnh (tham số MT5 thực chạy):**
  - TP: chốt cả rổ khi giá vượt giá vốn bình quân **0.50%** (InpTPPct=0.005).
  - SL: **không SL cứng** (InpCatLoPct=0).
  - DCA/lưới: nhồi ngược chiều, bước 0.30% giá lệnh đầu; lot đều (không nhân); tối đa **9 lệnh/rổ** (kể cả lệnh đầu).
  - Hedge: không.
  - Recovery/gỡ: không có tham số gỡ riêng (InpGoTien=0).
  - Trailing: không.
  - Khác: không mở lệnh mới từ 23h đến 2h (giờ server); chờ 0 nến sau khi đóng rổ.
  - Lot: lệnh đầu **30 lot** (lot micro XM, vốn 1.000 USD, đòn bẩy 1:500).
- **Kết quả đo (MT5 real tick, ĐO THẬT):** 10.6%/năm kép · DD equity 17.4% (DD báo cáo 29.2%) · 2 lệnh · PF 0.00 · giai đoạn 2023.12.26–2026.10.01 (2.76 năm). Stress ×1,5 + 7 USD (MÔ PHỎNG): 10.2%/năm, DD 17.4%. Walk-forward 3 đoạn: 35 / 0 / -0 %/năm. MC DD p95: 18.3%.
- **Python trước MT5 (MÔ PHỎNG):** 22.8%/năm, DD 50.3%.
- **Ghi chú:** ít lệnh 2; 1 đoạn WF gánh 100% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5).

## B. 13 thẻ mới qua lọc Python hôm nay (CHƯA đo MT5)

Lọc Python “65/15” sau phí, lot thật, tài khoản XM micro 1.000 USD 1:500, giai đoạn 2,77 năm (dữ liệu box). Mọi số ở phần này là **MÔ PHỎNG**; việc MT5 đã xếp hàng nhưng chưa có kết quả.

### sk_ea_2f4540d68a — GridScalperEA (lưới hồi quy theo Bollinger)

- **Nguồn EA:** crissofiasi/scalping :: GridScalperEA.mq5 (https://github.com/crissofiasi/scalping) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** AUDUSD / H1
- **Điều kiện vào lệnh:** MUA khi giá đóng cửa vừa cắt xuống ≤ dải dưới Bollinger(20, 2); BÁN khi vừa cắt lên ≥ dải trên Bollinger(20, 2) (so với nến trước).
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.50%** quanh giá vốn bình quân (tp_pct=0.005).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.30%, hệ số lot ×1, tối đa 3 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 10 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: TP 10 pip mỗi lệnh; lưới 5 bậc mỗi phía, bước 5 pip, tối đa 10 lệnh; dừng theo DD tuần 8% / tháng 15%.
- **Kết quả đo (Python MÔ PHỎNG):** 86.9%/năm · DD 45.1% · 283 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): -11.69%/năm, DD 16.11%.
- **Ghi chú bản dịch:** Nhánh “breakthrough” (vượt BB + 5 pip, vào theo xu hướng, lot ×1,5) CHƯA dịch.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']
    m = c.rolling(20, min_periods=20).mean(); s = c.rolling(20, min_periods=20).std(ddof=0)
    mua = (c <= m - 2*s) & (c.shift(1) > m.shift(1) - 2*s.shift(1))
    ban = (c >= m + 2*s) & (c.shift(1) < m.shift(1) + 2*s.shift(1))
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```

### sk_ea_3d5da5b65e — Sniper Gold Hybrid Recovery

- **Nguồn EA:** Sniper Gold Hybrid Recovery EA :: Sniper_Gold_Hybrid_Recovery_EA.mq5 (https://www.mql5.com/en/code/76605) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** XAUUSD / H4
- **Điều kiện vào lệnh:** Chỉ MUA: RSI(14) nến trước ≤ mức động (40; giảm còn 35 khi ATR14 ≥ 1,4 × TB50 của ATR; còn 30 khi ≥ 2,0 ×) VÀ (nến có râu dưới > 50% thân nến – nến từ chối, HOẶC RSI đang tăng).
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: không (dca_toi_da=0).
  - Hedge: khóa khi lỗ ≥ 10% số dư.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: recovery mua thêm cách ATR×1,55 (tăng dần +0,45), tối thiểu 1800/3000/4500 điểm; chốt rổ khi lãi 15 USD, trailing 5 USD; dừng khi equity mất 50%.
- **Kết quả đo (Python MÔ PHỎNG):** 33.6%/năm · DD 63.7% · 137 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 43.66%/năm, DD 63.69%.
- **Ghi chú bản dịch:** Điểm cấu trúc LL/LH (score) được đơn giản hoá thành “nến từ chối / RSI tăng” — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    o = df['open']; h = df['high']; l = df['low']; c = df['close']
    d = c.diff(); g = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rsi = 100 - 100/(1 + g/ls)
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14, min_periods=14).mean(); tb = atr.rolling(50, min_periods=20).mean()
    muc = 40 - 5*(atr >= 1.4*tb).astype(int) - 5*(atr >= 2.0*tb).astype(int)
    tu_choi = (np.minimum(o, c) - l) > (h - l)*0.5
    len_ = rsi > rsi.shift(1)
    mua = (rsi.shift(1) <= muc) & (tu_choi | len_)
    return np.where(mua, 1, 0).astype(int)
```

### sk_ea_9345f47763 — MakeGrid193 (lưới lọc EMA34 + MACD)

- **Nguồn EA:** Grid Ea :: MakeGrid193.mq4 (https://www.forexfactory.com/thread/59951-grid-ea) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** EURUSD / H1
- **Điều kiện vào lệnh:** Trạng thái +1 khi giá > EMA(34) và MACD(12,26) > 0; −1 khi giá < EMA(34) và MACD < 0. Vào lệnh (MUA/BÁN) tại nến trạng thái vừa đổi sang +1/−1.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.50%, hệ số lot ×1, tối đa 8 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 1 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: lưới 10 bậc lệnh chờ, mỗi lệnh TP 10 tick, làm mới lưới định kỳ; huỷ lệnh chờ trái chiều khi bộ lọc đổi.
- **Kết quả đo (Python MÔ PHỎNG):** 24.8%/năm · DD 50.5% · 404 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 3.25%/năm, DD 12.24%.
- **Ghi chú bản dịch:** Lưới lệnh chờ quy về tín hiệu đổi trạng thái — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']
    ema = c.ewm(span=34, adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    st = np.where((c > ema) & (macd > 0), 1, np.where((c < ema) & (macd < 0), -1, 0))
    st = pd.Series(st, index=df.index)
    doi = (st != st.shift(1)) & (st != 0)
    return np.where(doi, st, 0).astype(int)
```

### sk_ea_b18d784179 — Zerith XAU SwingGrid Recovery

- **Nguồn EA:** BlamzKunG/My-Expert-Advisor :: Zerith_XAU_SwingGrid_Recovery_EA.mq5 (https://github.com/BlamzKunG/My-Expert-Advisor) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** GBPUSD / H1
- **Điều kiện vào lệnh:** Chia chế độ theo ADX(14): xu hướng mạnh (ADX > 25, EMA20/EMA50 cùng chiều giá) → MUA khi RSI(14) < 40 và histogram MACD tăng; đi ngang (ADX < 20) → MUA khi RSI(14) ≤ 28 và RSI(56) ≤ 40; bình thường → MUA khi RSI ≤ 35, RSI(56) ≤ 45 và histogram tăng. BÁN đối xứng (RSI > 60 / ≥ 72 / ≥ 65…).
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 1.20%, hệ số lot ×1.3, tối đa 3 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: lưới swing + recovery theo điểm swing; TP = InpTpPointsBase × hệ số chế độ; dừng khi DD equity vượt ngưỡng.
- **Kết quả đo (Python MÔ PHỎNG):** 19.0%/năm · DD 20.0% · 52 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 13.96%/năm, DD 9.92%.
- **Ghi chú bản dịch:** Gốc dùng M1/M5/H1, gộp về 1 khung (RSI56 ≈ khung ×4); chế độ VOLATILE/CHOPPY bỏ qua — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']; c = df['close']

    def tinh_rsi(x, n):
        d = x.diff(); g = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
        return 100 - 100/(1 + g/ls)

    rsi = tinh_rsi(c, 14); rsi4 = tinh_rsi(c, 56)
    ef = c.ewm(span=20, adjust=False).mean(); es = c.ewm(span=50, adjust=False).mean()
    xu = np.where((ef > es) & (c > ef), 1, np.where((ef < es) & (c < ef), -1, 0))
    hist = (c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean())
    hist = hist - hist.ewm(span=9, adjust=False).mean()
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/14, adjust=False).mean()
    up = h.diff(); dn = -l.diff()
    pdi = 100*pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index).ewm(alpha=1/14, adjust=False).mean()/atr
    ndi = 100*pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index).ewm(alpha=1/14, adjust=False).mean()/atr
    adx = (100*(pdi - ndi).abs()/(pdi + ndi)).ewm(alpha=1/14, adjust=False).mean()
    hl = hist > hist.shift(1); hx = hist < hist.shift(1)
    manh = (adx > 25) & (xu != 0); yen = (adx < 20) & ~manh; tb = ~manh & ~yen
    mua = (manh & (xu > 0) & (rsi < 40) & hl) | (yen & (rsi <= 28) & (rsi4 <= 40)) | (tb & (rsi <= 35) & (rsi4 <= 45) & hl)
    ban = (manh & (xu < 0) & (rsi > 60) & hx) | (yen & (rsi >= 72) & (rsi4 >= 60)) | (tb & (rsi >= 65) & (rsi4 >= 55) & hx)
    return np.where(mua, 1, np.where(ban & ~mua, -1, 0)).astype(int)
```

### sk_ea_31b7c0180f — Zerith MACD Martingale Grid

- **Nguồn EA:** BlamzKunG/My-Expert-Advisor :: Zerith_MACD_Martingale_Grid_EA.mq5 (https://github.com/BlamzKunG/My-Expert-Advisor) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** GBPUSD / H4
- **Điều kiện vào lệnh:** MUA khi MACD(12,26) cắt lên đường tín hiệu SMA(9) (xác nhận trên nến đã đóng) và giá ≥ EMA(800) (≈ EMA200 H4); BÁN đối xứng khi cắt xuống và giá ≤ EMA(800).
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.10%** quanh giá vốn bình quân (tp_pct=0.001).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.80%, hệ số lot ×1.3, tối đa 5 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: lưới ATR14×2 (tối thiểu 50 pip), lot +0,01 mỗi 5 bậc, tối đa 10 bậc; từ bậc 5 mở hedge 50% khối lượng; chốt rổ 10 USD (net 5 USD khi có hedge), trailing rổ từ 10 USD bước 3 USD; equity stop 20%.
- **Kết quả đo (Python MÔ PHỎNG):** 18.1%/năm · DD 55.7% · 156 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 12.55%/năm, DD 12.26%.
- **Ghi chú bản dịch:** Bộ lọc EMA200 H4 xấp xỉ bằng EMA800 H1 — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.rolling(9, min_periods=9).mean()
    xu = c.ewm(span=800, adjust=False).mean()   # EMA200 H4 ~ EMA800 H1
    m1 = macd.shift(1); s1 = sig.shift(1); m2 = macd.shift(2); s2 = sig.shift(2)
    mua = (m1 > s1) & (m2 <= s2) & (c >= xu)
    ban = (m1 < s1) & (m2 >= s2) & (c <= xu)
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```

### sk_ea_8760277bca — MintyGrid 7.2 (RSI 30/70)

- **Nguồn EA:** alboogycOdR/dev-projects :: MintyGrid_7_2.mq5 (https://github.com/alboogycOdR/dev-projects) · dịch tay đợt 3 (grokbot-tay)
- **Cặp / TF:** GBPJPY / H4
- **Điều kiện vào lệnh:** RSI(14) tính trên giá typical (H+L+C)/3: MUA khi vừa cắt xuống ≤ 30; BÁN khi vừa cắt lên ≥ 70.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.50%, hệ số lot ×1.6, tối đa 5 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 1 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: martingale lot ×2, bước 1% giá ×10 tăng dần, tối đa 10 bậc, hoà vốn ở bậc 5; chốt lãi theo % vốn.
- **Kết quả đo (Python MÔ PHỎNG):** 15.4%/năm · DD 43.5% · 177 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): -16.75%/năm, DD 43.48%.
- **Ghi chú bản dịch:** —
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']; c = df['close']

    def tinh_rsi(x, n):
        d = x.diff(); g = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
        return 100 - 100/(1 + g/ls)

    r = tinh_rsi((h + l + c)/3, 14)
    mua = (r <= 30) & (r.shift(1) > 30)
    ban = (r >= 70) & (r.shift(1) < 70)
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```

### sk_ea_b7faac890a — Zerith Oneshot (DeMarker, 1 lệnh/ngày)

- **Nguồn EA:** BlamzKunG/My-Expert-Advisor :: Zerith_Oneshot.mq5 (https://github.com/BlamzKunG/My-Expert-Advisor) · dịch tay đợt 4 (grokbot-tay)
- **Cặp / TF:** GBPUSD / H1
- **Điều kiện vào lệnh:** DeMarker(18) và DeMarker(16) cùng > 0,7 → MUA; cùng < 0,3 → BÁN; chỉ lấy tín hiệu đầu tiên trong ngày.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.50%, hệ số lot ×1.6, tối đa 5 lệnh nhồi thêm.
  - Hedge: khóa khi lỗ ≥ 10% số dư.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, nguyên văn):** sl: cat lo o buoc MaxOrders+1; dca: recovery toi da 5 lenh, buoc 200 diem x1.5 gian, lot x1.2
- **Kết quả đo (Python MÔ PHỎNG):** 75.0%/năm · DD 62.2% · 457 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 1.23%/năm, DD 37.44%.
- **Ghi chú bản dịch:** Strategy01 M6/M15 gộp về 1 khung; các strategy khác chưa dịch — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']
    def dem(n):
        dmx = (h - h.shift(1)).clip(lower=0); dmn = (l.shift(1) - l).clip(lower=0)
        a = dmx.rolling(n, min_periods=n).mean(); b = dmn.rolling(n, min_periods=n).mean()
        return a/(a + b)
    da = dem(18); db = dem(16)
    s = np.where((da > 0.7) & (db > 0.7), 1, np.where((da < 0.3) & (db < 0.3), -1, 0))
    ngay = pd.Series(pd.DatetimeIndex(df.index).date, index=df.index)
    s = pd.Series(s, index=df.index)
    dau = (s != 0) & (s.ne(0).groupby(ngay).cumsum() == 1)
    return np.where(dau, s, 0).astype(int)
```

### sk_ea_a0d40c82ed — Hon-Matrix (kênh + RSI)

- **Nguồn EA:** Hon Matrix :: Hon-Matrix.mq5 (https://www.mql5.com/en/code/71645) · dịch tay đợt 4 (grokbot-tay)
- **Cặp / TF:** EURUSD / H1
- **Điều kiện vào lệnh:** Khi thị trường đi ngang (biên độ kênh 50 nến < 8 × ATR14): MUA khi giá ≤ đáy kênh + 15% biên độ và RSI(14) < 35; BÁN khi giá ≥ đỉnh kênh − 15% và RSI > 65; hai tín hiệu cách nhau tối thiểu 4 nến.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.10%** quanh giá vốn bình quân (tp_pct=0.001).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 1.20%, hệ số lot ×1, tối đa 8 lệnh nhồi thêm.
  - Hedge: khóa khi lỗ ≥ 10% số dư.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: TP 50 pip, trailing 15 pip, lưới Fibonacci 5 lệnh ×1,1; đóng hết khi lãi 40% / lỗ 30% vốn.
- **Kết quả đo (Python MÔ PHỎNG):** 19.0%/năm · DD 16.5% · 295 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): -1.85%/năm, DD 16.48%.
- **Ghi chú bản dịch:** Bộ dò S/R, AMA, pha thị trường gốc thay bằng kênh 50 nến + ATR; nhánh breakout/bounce chưa dịch — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']; c = df['close']

    def tinh_rsi(x, n):
        d = x.diff(); g = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
        return 100 - 100/(1 + g/ls)

    rsi = tinh_rsi(c, 14)
    hh = h.rolling(50, min_periods=50).max(); ll = l.rolling(50, min_periods=50).min()
    w = hh - ll
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14, min_periods=14).mean()
    yen = w < 8*atr
    mua = yen & (c <= ll + 0.15*w) & (rsi < 35)
    ban = yen & (c >= hh - 0.15*w) & (rsi > 65)
    s = np.where(mua, 1, np.where(ban, -1, 0))
    out = np.zeros(len(s), dtype=int); cuoi = -10
    for i in range(len(s)):
        if s[i] != 0 and i - cuoi >= 4: out[i] = s[i]; cuoi = i
    return out
```

### sk_ea_37d18e3ece — ZONE_RECOVERY_AREA_II

- **Nguồn EA:** Hedging_Zone_Recovery_Area :: ZONE_RECOVERY_AREA_VERSION_II1.mq4 (https://www.mql5.com/en/code/20266) · dịch tay đợt 5 (grokbot-tay)
- **Cặp / TF:** EURCAD / H1
- **Điều kiện vào lệnh:** Chỉ MUA: tại nến điều kiện vừa bật: SMA(20) < SMA(200) (nến trước) VÀ MACD(12,26,9) đường chính > đường tín hiệu.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.80%, hệ số lot ×1.3, tối đa 3 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 10 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: TP 200 pip; zone recovery 10 pip mở lệnh ngược lot ×2; TP/SL theo tiền tuỳ chọn.
- **Kết quả đo (Python MÔ PHỎNG):** 62.6%/năm · DD 55.9% · 91 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 19.84%/năm, DD 44.58%.
- **Ghi chú bản dịch:** MACD gốc tính trên MN1, bản dịch dùng khung hiện tại — GẦN ĐÚNG; nhánh BÁN của gốc không bao giờ chạy (lỗi gắn else) nên bản dịch chỉ MUA.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']

    def canh(m):
        return m & ~m.shift(1, fill_value=False)

    f = c.rolling(20, min_periods=20).mean(); s = c.rolling(200, min_periods=200).mean()
    m = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean(); sg = m.ewm(span=9, adjust=False).mean()
    mua = (f.shift(1) < s.shift(1)) & (m > sg)
    return np.where(canh(mua), 1, 0).astype(int)
```

### sk_ea_c67d5d31e9 — Ichimoku EA v1.3

- **Nguồn EA:** shidatonglin/GitGpa :: 2011-06_Ichimoku EA v1.3.mq4 (https://github.com/shidatonglin/GitGpa) · dịch tay đợt 5 (grokbot-tay)
- **Cặp / TF:** GBPCAD / H4
- **Điều kiện vào lệnh:** MUA khi Tenkan(9) cắt lên Kijun(26) và giá > Kijun; BÁN khi Tenkan cắt xuống Kijun và giá < Kijun.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.80%, hệ số lot ×1, tối đa 8 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: tối đa 5 lệnh cùng chiều; TP/SL gốc: CHƯA RÕ trong mã.
- **Kết quả đo (Python MÔ PHỎNG):** 33.0%/năm · DD 27.1% · 127 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 20.47%/năm, DD 12.5%.
- **Ghi chú bản dịch:** Lọc Senkou/Chikou và giờ GMT/thứ Sáu chưa dịch — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']; c = df['close']
    tk = (h.rolling(9).max() + l.rolling(9).min())/2; kj = (h.rolling(26).max() + l.rolling(26).min())/2
    mua = (tk > kj) & (tk.shift(1) <= kj.shift(1)) & (c > kj)
    ban = (tk < kj) & (tk.shift(1) >= kj.shift(1)) & (c < kj)
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```

### sk_ea_42415c4f24 — Trickerless_RHMP

- **Nguồn EA:** Trickerless :: Trickerless_RHMP.mq4 (https://www.mql5.com/en/code/39833) · dịch tay đợt 5 (grokbot-tay)
- **Cặp / TF:** EURGBP / H1
- **Điều kiện vào lệnh:** Khi ADX(14) > 20: MUA khi SMMA(120) < SMMA(60), SMMA(60) đang lên và giá < SMMA(60) (mua nhịp hồi); BÁN đối xứng. SMMA tính trên giá trung vị (H+L)/2.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: không (dca_toi_da=0).
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 30 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: rổ theo nhóm, MaxTrades; chốt rổ BasketProfit 1,06; lệnh dự phòng khi nến spike ×7.
- **Kết quả đo (Python MÔ PHỎNG):** 24.5%/năm · DD 50.4% · 40 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): -28.89%/năm, DD 28.17%.
- **Ghi chú bản dịch:** Ngưỡng ADX/MinTrend/TrendSpace đặt tạm; SignalB/C và lệnh spike chưa dịch — GẦN ĐÚNG.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    h = df['high']; l = df['low']; c = df['close']; p = (h + l)/2
    m1 = p.ewm(alpha=1/120, adjust=False).mean(); m2 = p.ewm(alpha=1/60, adjust=False).mean()
    up = h.diff(); dn = -l.diff()
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/14, adjust=False).mean()
    pdi = 100*pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).ewm(alpha=1/14, adjust=False).mean()/atr
    ndi = 100*pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).ewm(alpha=1/14, adjust=False).mean()/atr
    adx = (100*(pdi - ndi).abs()/(pdi + ndi)).ewm(alpha=1/14, adjust=False).mean()
    xh = adx > 20
    mua = xh & (m1 < m2) & (m2 > m2.shift(1)) & (c < m2)
    ban = xh & (m1 > m2) & (m2 < m2.shift(1)) & (c > m2)
    return np.where(mua, 1, np.where(ban, -1, 0)).astype(int)
```

### sk_ea_94672bd399 — GBPJPY_EA_scalper_n6 (BB 2,5σ)

- **Nguồn EA:** joaotorresmarques/mql4 :: GBPJPY_EA_scalper_n6-.mq4 (https://github.com/joaotorresmarques/mql4) · dịch tay đợt 5 (grokbot-tay)
- **Cặp / TF:** GBPJPY / H4
- **Điều kiện vào lệnh:** MUA khi giá đóng cửa ≤ SMA(50) − 2,5σ (trung bình dải dưới BB(50,2) và BB(50,3)); BÁN khi ≥ SMA(50) + 2,5σ.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.30%** quanh giá vốn bình quân (tp_pct=0.003).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.50%, hệ số lot ×1.3, tối đa 3 lệnh nhồi thêm.
  - Hedge: không.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: martingale tuỳ chọn; TP/SL gốc: CHƯA RÕ trong mã.
- **Kết quả đo (Python MÔ PHỎNG):** 24.1%/năm · DD 43.4% · 116 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): -6.94%/năm, DD 34.7%.
- **Ghi chú bản dịch:** —
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']
    m = c.rolling(50, min_periods=50).mean(); s = c.rolling(50, min_periods=50).std(ddof=0)
    return np.where(c <= m - 2.5*s, 1, np.where(c >= m + 2.5*s, -1, 0)).astype(int)
```

### sk_ea_5056669865 — Zone_Recovery_Formula

- **Nguồn EA:** Zone_Recovery_Area Formula1 :: Zone_Recovery_Formula.mq4 (https://www.mql5.com/en/code/25337) · dịch tay đợt 5 (grokbot-tay)
- **Cặp / TF:** GBPCHF / H1
- **Điều kiện vào lệnh:** Chỉ MUA: tại nến điều kiện vừa bật: SMA(20) < SMA(200) (nến trước) VÀ MACD(12,26,9) đường chính > đường tín hiệu.
- **Quản lý lệnh dùng khi lọc (Python):**
  - TP: chốt cả rổ ở **0.10%** quanh giá vốn bình quân (tp_pct=0.001).
  - SL: **không SL cứng**.
  - DCA: nhồi ngược chiều bước 0.50%, hệ số lot ×1, tối đa 3 lệnh nhồi thêm.
  - Hedge: khóa khi lỗ ≥ 10% số dư.
  - Trailing / basket TP riêng / số lệnh tối đa khác: không có trong cấu hình đo Python.
  - Lot: 3 lot / 1.000 USD vốn (lot0).
- **Quản lý lệnh trong EA gốc (theo thẻ, chưa áp dụng khi đo):** EA gốc: TP 150 pip; zone recovery 50 pip mở lệnh ngược lot ×2; TP/SL theo tiền tuỳ chọn.
- **Kết quả đo (Python MÔ PHỎNG):** 23.0%/năm · DD 36.8% · 214 lệnh · 2.77 năm · stop-out 0. Đoạn ngoài mẫu (nhãn, không phải cổng): 16.93%/năm, DD 4.84%.
- **Ghi chú bản dịch:** MACD gốc trên MN1 → dùng khung hiện tại — GẦN ĐÚNG; chỉ MUA như hành vi gốc.
- **Bản dịch Python:**

```python
def tin_hieu(df):
    c = df['close']

    def canh(m):
        return m & ~m.shift(1, fill_value=False)

    f = c.rolling(20, min_periods=20).mean(); s = c.rolling(200, min_periods=200).mean()
    m = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean(); sg = m.ewm(span=9, adjust=False).mean()
    mua = (f.shift(1) < s.shift(1)) & (m > sg)
    return np.where(canh(mua), 1, 0).astype(int)
```

## Khoảng trống dữ liệu

- 19 hệ ở phần A không còn công thức tín hiệu trong thẻ/CSDL repo (thẻ chạy `mt5_truc_tiep` mà bản dịch hỏng, hoặc thẻ tổ hợp không còn trong bảng `to_hop`): `sk_ea_0ca971ac32`, `sk_ea_0075f624b3`, `to_hop_16b0d75bb149f634`, `sk_ea_0b8298aa53`, `sk_ea_0c762cdb38`, `to_hop_9acc6e0d2f784cb9`, `sk_ea_5049c79288`, `sk_ea_a7cd39087e`, `sk_ea_0806a3a5e5`, `sk_ea_0cc19095a9`, `018dcb1347276c97`, `b0be91a35f43f34a`, `to_hop_564be9bb91406c57`, `sk_ea_0757c93eb3`, `sk_ea_02906b7d6a`, `sk_ea_3279057100`, `to_hop_c2d52300cc825dff`, `sk_ea_0ab4d307d3`, `3304d2fad28adef6`. Lệnh vào MT5 của chúng nằm trong tệp CSV `reports/*/viec_mt5/<thẻ>/*_vao.csv`.
- Các hệ “lệnh statement” (`sk_st_*`) dùng nguyên lệnh của tác giả; quy tắc vào gốc CHƯA RÕ trong mã.
- Hoa hồng thật XM micro: CHƯA ĐO ĐƯỢC (báo cáo = 0), chỉ thử bằng stress MÔ PHỎNG.
- Phần B: chưa có kết quả MT5.
