# Dịch ngược 10 tín hiệu MQL5 (03/11/2026)

> Nguồn: 10 CSV lịch sử giao dịch công khai của tín hiệu MQL5 (sao chép vào `data/cong_khai/csv/`, đã gitignore). Công cụ: `nhan/dich_nguoc` (đã mở rộng bộ đọc: bỏ lệnh chờ Stop/Limit, đọc CSV dạng deal In/Out ghép FIFO, đọc nạp/rút/credit) + `nhan/dich_nguoc/top10.py`. Số liệu thô: `data/dich_nguoc/top10.json`, `data/dich_nguoc/backtest_luoi.json` (gitignore).
> Tiêu chí ĐẠT duy nhất: **DD < 80% VÀ CAGR > 10%/năm**.

## Cách đo
- **Lợi nhuận thật**: số dư ĐÓNG lệnh + dòng tiền nạp/rút/credit → chỉ số TWR theo ngày → CAGR; DD tính trên chỉ số TWR của số dư đóng lệnh. **DD equity nổi: CHƯA ĐO ĐƯỢC** (CSV không có equity) — với lưới/martingale DD thật chắc chắn lớn hơn nhiều.
- **AUC**: lệnh ĐẦU rổ (quyết định vào) so với thời điểm ngẫu nhiên (≥3× số lệnh) trên nến H1 đã đóng; 8 đặc trưng (RSI14, ATR14 pip, khoảng cách MA50/ATR, z-Bollinger20, phá biên phiên Á, giờ, thứ, lợi suất 5 nến/ATR); cây quyết định sâu 3 + logistic, kiểm chéo 5 lớp. Chạy hai lần: có giờ/thứ và **bỏ giờ/thứ** (để tách luật thời gian khỏi luật giá). AUC chiều = logistic BUY vs SELL ở lệnh đầu rổ (không giờ).
- Giá H1: HistData/Dukascopy BID trên box, chủ yếu 2024-01 → 2026-10 (AUDCAD từ 2008). **Giờ server của từng nhà môi giới tín hiệu chưa xác minh** (giả định trùng NY+7) → lệch 1 giờ có thể làm rò rỉ thông tin; AUC chiều 0,97 của 1862128 nghi do lệch giờ/nến tin, không tin được.

## Bảng tổng hợp

| ID | Symbol chính | Phong cách | Giữ trung vị (phút) | Phiên Á/Âu/Mỹ (giờ server) | Lãi đóng lệnh / Nạp | CAGR TWR (số dư đóng) | DD số dư đóng | AUC cây / logistic (có giờ) | AUC cây / logistic (bỏ giờ) | AUC chiều |
|---|---|---|---|---|---|---|---|---|---|---|
| [1862128](https://www.mql5.com/en/signals/1862128) | XAUUSD | breakout lệnh chờ STOP, lệnh đơn lẻ (không lưới đáng kể), có SL | 0.1 | 0.129/0.354/0.517 | 86,953 / 1,000 | 233.4% | 11.7% | 0.618 / 0.476 | 0.435 / 0.468 | 0.966 |
| [1864588](https://www.mql5.com/en/signals/1864588) | GBPUSD | breakout lệnh chờ STOP, lệnh đơn lẻ (không lưới đáng kể), có SL | 0.1 | 0.043/0.101/0.857 | 118,199 / 1,000 | 262.1% | 5.7% | 0.865 / 0.621 | 0.468 / 0.441 | 0.473 |
| [1932739](https://www.mql5.com/en/signals/1932739) | EURUSD | lưới/DCA lot đều, có SL | 24.9 | 0.249/0.505/0.246 | 165,212 / 10,000 | 62.2% | 17.0% | 0.619 / 0.414 | 0.434 / 0.379 | 0.829 |
| [2262642](https://www.mql5.com/en/signals/2262642) | AUDCAD | lưới/DCA lot đều, có hedge, SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal không có cột S/L, T/P) | 442.7 | 0.284/0.246/0.47 | 4,004 / 1,000 | 87.1% | 5.9% | 0.63 / 0.597 | 0.623 / 0.59 | 0.807 |
| [2271402](https://www.mql5.com/en/signals/2271402) | AUDCAD | lưới/DCA lot đều, có hedge, SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal không có cột S/L, T/P) | 739.4 | 0.233/0.248/0.519 | 7,229 / 20,827 | 111.8% | 24.4% | 0.548 / 0.584 | 0.542 / 0.596 | 0.98 |
| [2302081](https://www.mql5.com/en/signals/2302081) | USDJPY | breakout lệnh chờ STOP, lệnh đơn lẻ (không lưới đáng kể), có SL | 0.1 | 0.146/0.133/0.722 | 546,275 / 1,000 | 445.8% | 7.9% | 0.953 / 0.683 | 0.539 / 0.523 | 0.485 |
| [2327790](https://www.mql5.com/en/signals/2327790) | GBPUSD | martingale, có hedge, không SL cứng | 125.1 | 0.227/0.314/0.46 | 11,857 / 34,394 | 83.9% | 16.1% | 0.5 / 0.628 | 0.506 / 0.635 | 0.914 |
| [2330430](https://www.mql5.com/en/signals/2330430) | GBPUSD | lệnh chờ LIMIT (lưới/đảo chiều), lưới/DCA lot đều, có hedge, không SL cứng | 427.6 | 0.164/0.405/0.431 | 22,937 / 5,000 | 23.1% | 2.0% | 0.608 / 0.573 | 0.589 / 0.582 | 0.766 |
| [2378480](https://www.mql5.com/en/signals/2378480) | XAUUSD | martingale, không SL cứng | 530.1 | 0.334/0.209/0.457 | 9,852 / 56,430 | 26.4% | 2.1% | 0.712 / 0.786 | 0.692 / 0.787 | CHƯA ĐO ĐƯỢC |
| [2391346](https://www.mql5.com/en/signals/2391346) | XAUUSD | lệnh đơn lẻ (không lưới đáng kể), có hedge, SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal không có cột S/L, T/P) | 17.7 | 0.092/0.767/0.141 | 602,426 / 54,500 | 183.1% | 23.1% | 0.894 / 0.627 | 0.356 / 0.317 | 0.524 |

## Chi tiết từng tín hiệu

### 1862128 — XAUUSD
- Phong cách: Bẫy tin tức (news straddle) XAUUSD: đặt đồng thời Buy Stop + Sell Stop quanh 15:29:58 giờ server (≈ giờ ra tin Mỹ), SL ~5 pip, TP 100 pip, giữ trung vị 0,1 phút; lệnh không khớp bị hủy sau ~1 phút.
- Tái lập: Luật THỜI GIAN rõ (giờ tin), lặp lại được về logic; nhưng lợi nhuận phụ thuộc trượt giá/khớp lệnh lúc tin → backtest H1 không mô phỏng được. Chung một nhà cung cấp với 1864588 và 2302081 (cùng dấu thời gian).
- Số lệnh (vị thế) 743, 2023-02-14 → 2026-10-29; symbol: XAUUSD 743; tỷ lệ BUY 0.533; lệnh chờ Stop 1222, Limit 0.
- Lô: kiểu co_dinh_don_le, hệ số lô trung vị None, rổ nhiều lệnh 0.0, tối đa 1 lệnh/rổ, bước lưới trung vị None pip (None ATR), lô đầu trung vị 0.64; cặp BUY/SELL chồng thời gian: 0.
- SL/TP: TP có ở 100% lệnh (trung vị 100.0 pip), SL có ở 100% (trung vị 5.0 pip); biên độ đóng trung vị 5.0 pip.
- Vốn: nạp 1,000, rút -0, lãi đóng lệnh 86,953, TWR tổng 86.9534, 3.72 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): atr14_pip: vào 80.02 vs ngẫu nhiên 93.811 (AUC đơn 0.436); thu: vào 2.0 vs ngẫu nhiên 2.0 (AUC đơn 0.474); gio: vào 14.0 vs ngẫu nhiên 12.0 (AUC đơn 0.517)

### 1864588 — GBPUSD
- Phong cách: Bẫy tin tức trên 4 cặp USD (GBPUSD/USDJPY/EURUSD/AUDUSD), Buy Stop + Sell Stop, SL ~4,4 pip, TP 100 pip, 56% lệnh mở lúc 15h server.
- Tái lập: Như 1862128: luật giờ tin, không phải mẫu hình giá. Không mô phỏng được bằng dữ liệu H1 → CHƯA ĐO ĐƯỢC.
- Số lệnh (vị thế) 1688, 2023-02-16 → 2026-10-28; symbol: GBPUSD 495, USDJPY 488, EURUSD 387, AUDUSD 318; tỷ lệ BUY 0.499; lệnh chờ Stop 3657, Limit 0.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.026, tối đa 4 lệnh/rổ, bước lưới trung vị 4.2 pip (0.18 ATR), lô đầu trung vị 0.67; cặp BUY/SELL chồng thời gian: 2.
- SL/TP: TP có ở 100% lệnh (trung vị 100.0 pip), SL có ở 100% (trung vị 4.4 pip); biên độ đóng trung vị 4.4 pip.
- Vốn: nạp 1,000, rút -0, lãi đóng lệnh 118,199, TWR tổng 118.1988, 3.72 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): thu: vào 3.0 vs ngẫu nhiên 2.0 (AUC đơn 0.624); gio: vào 14.0 vs ngẫu nhiên 11.0 (AUC đơn 0.56); atr14_pip: vào 14.201 vs ngẫu nhiên 15.006 (AUC đơn 0.464)

### 1932739 — EURUSD
- Phong cách: Đa cặp (EURUSD/XAUUSD/GBPUSD/USDJPY), lô cố định 0,1, có SL (trung vị 14,8 pip) và TP (83,6 pip), có lệnh Stop chờ, gom tới 49 lệnh cùng chiều; giữ trung vị 25 phút.
- Tái lập: Có cấu trúc giờ (Âu–Mỹ) nhưng bỏ giờ thì AUC < 0,5 → điểm vào không tách được khỏi ngẫu nhiên bằng 8 đặc trưng hiện có.
- Số lệnh (vị thế) 14747, 2019-12-19 → 2026-10-30; symbol: EURUSD 5121, XAUUSD 4279, GBPUSD 1984, USDJPY 1315, AUDUSD 639; tỷ lệ BUY 0.496; lệnh chờ Stop 1984, Limit 2.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.157, tối đa 49 lệnh/rổ, bước lưới trung vị 0.0 pip (0.3 ATR), lô đầu trung vị 0.1; cặp BUY/SELL chồng thời gian: 305.
- SL/TP: TP có ở 98% lệnh (trung vị 83.6 pip), SL có ở 100% (trung vị 14.8 pip); biên độ đóng trung vị 10.0 pip.
- Vốn: nạp 10,000, rút 50,000, lãi đóng lệnh 165,212, TWR tổng 26.7001, 6.87 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): gio: vào 13.0 vs ngẫu nhiên 11.0 (AUC đơn 0.523); atr14_pip: vào 11.866 vs ngẫu nhiên 11.674 (AUC đơn 0.513); thu: vào 2.0 vs ngẫu nhiên 2.0 (AUC đơn 0.487)

### 2262642 — AUDCAD
- Phong cách: Lưới hai chiều AUDCAD (hedge), lô đều 0,01, bước trung vị 15,6 pip (≈1,0 ATR H1), tối đa 140 lệnh/rổ, biên độ đóng trung vị 11,1 pip, giữ trung vị ~7,4 giờ.
- Tái lập: Cơ chế lưới đơn giản → TÁI LẬP ĐƯỢC về cơ chế; điểm vào yếu (AUC ~0,6, đặc trưng chính: ATR thấp hơn ngẫu nhiên).
- Số lệnh (vị thế) 5883, 2021-11-01 → 2026-10-30; symbol: AUDCAD 5883; tỷ lệ BUY 0.505; lệnh chờ Stop 0, Limit 0.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.413, tối đa 140 lệnh/rổ, bước lưới trung vị 15.6 pip (1.02 ATR), lô đầu trung vị 0.01; cặp BUY/SELL chồng thời gian: 847.
- SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal); biên độ đóng trung vị 11.1 pip.
- Vốn: nạp 1,000, rút 3,850, lãi đóng lệnh 4,004, TWR tổng 22.0113, 5.0 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): atr14_pip: vào 13.449 vs ngẫu nhiên 14.597 (AUC đơn 0.418); gio: vào 12.0 vs ngẫu nhiên 12.0 (AUC đơn 0.474); kc_ma50_atr: vào -0.049 vs ngẫu nhiên 0.111 (AUC đơn 0.484)

### 2271402 — AUDCAD
- Phong cách: Lưới/DCA lô đều đa cặp hàng hóa-chéo (AUDCAD/AUDNZD/NZDCAD + US30/XAUUSD/DE40), hedge, bước trung vị 9,6 pip (~1,6 ATR).
- Tái lập: Gần giống 2262642 nhưng trộn nhiều tài sản; nhiều nạp/rút (lãi/nạp chỉ 0,35).
- Số lệnh (vị thế) 1898, 2021-05-12 → 2026-10-30; symbol: AUDCAD 1056, AUDNZD 237, NZDCAD 234, US30 210, XAUUSD 94; tỷ lệ BUY 0.457; lệnh chờ Stop 0, Limit 0.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.42, tối đa 26 lệnh/rổ, bước lưới trung vị 9.6 pip (1.59 ATR), lô đầu trung vị 0.03; cặp BUY/SELL chồng thời gian: 133.
- SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal); biên độ đóng trung vị 18.2 pip.
- Vốn: nạp 20,827, rút 26,531, lãi đóng lệnh 7,229, TWR tổng 60.2193, 5.48 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): atr14_pip: vào 12.697 vs ngẫu nhiên 14.539 (AUC đơn 0.391); bb_z20: vào -0.156 vs ngẫu nhiên 0.012 (AUC đơn 0.473); kc_ma50_atr: vào -0.366 vs ngẫu nhiên -0.052 (AUC đơn 0.478)

### 2302081 — USDJPY
- Phong cách: Bẫy tin tức (cùng nhà cung cấp 1862128/1864588) chủ yếu USDJPY, lô rất lớn (trung vị 7,25), SL ~5,2 pip, TP 100 pip.
- Tái lập: Luật giờ tin; AUC cao chỉ do giờ (bỏ giờ còn ~0,5).
- Số lệnh (vị thế) 762, 2023-03-10 → 2026-10-28; symbol: USDJPY 472, AUDCAD 154, EURGBP 90, NZDCHF 46; tỷ lệ BUY 0.465; lệnh chờ Stop 769, Limit 0.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.023, tối đa 3 lệnh/rổ, bước lưới trung vị 5.7 pip (0.38 ATR), lô đầu trung vị 7.25; cặp BUY/SELL chồng thời gian: 0.
- SL/TP: TP có ở 100% lệnh (trung vị 100.0 pip), SL có ở 100% (trung vị 5.2 pip); biên độ đóng trung vị 5.2 pip.
- Vốn: nạp 1,000, rút -0, lãi đóng lệnh 546,275, TWR tổng 546.2746, 3.72 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): gio: vào 14.0 vs ngẫu nhiên 12.0 (AUC đơn 0.63); thu: vào 3.0 vs ngẫu nhiên 2.0 (AUC đơn 0.613); atr14_pip: vào 24.823 vs ngẫu nhiên 21.727 (AUC đơn 0.576)

### 2327790 — GBPUSD
- Phong cách: Martingale hedge đa cặp (GBPUSD/AUDUSD/GBPAUD/EURUSD), hệ số lô trung vị 1,5, bước ~25 pip (~2 ATR), TP nhỏ ~6 pip, tới 46 lệnh/rổ.
- Tái lập: MARTINGALE thuần → loại khỏi danh sách tái lập theo yêu cầu.
- Số lệnh (vị thế) 8342, 2021-04-22 → 2026-10-29; symbol: GBPUSD 2345, AUDUSD 2216, GBPAUD 1674, EURUSD 850, USDCAD 657; tỷ lệ BUY 0.482; lệnh chờ Stop 0, Limit 1.
- Lô: kiểu martingale, hệ số lô trung vị 1.5, rổ nhiều lệnh 0.209, tối đa 46 lệnh/rổ, bước lưới trung vị 25.2 pip (2.03 ATR), lô đầu trung vị 0.02; cặp BUY/SELL chồng thời gian: 3486.
- SL/TP: TP có ở 79% lệnh (trung vị 6.2 pip), SL có ở 4% (trung vị 26.5 pip); biên độ đóng trung vị 8.2 pip.
- Vốn: nạp 34,394, rút 42,174, lãi đóng lệnh 11,857, TWR tổng 28.0678, 5.53 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): bb_z20: vào -0.558 vs ngẫu nhiên 0.147 (AUC đơn 0.392); rsi14: vào 46.669 vs ngẫu nhiên 52.571 (AUC đơn 0.416); loi_suat_5bar_atr: vào -0.178 vs ngẫu nhiên 0.087 (AUC đơn 0.422)

### 2330430 — GBPUSD
- Phong cách: Lưới hai chiều GBPUSD 10 năm: luôn có BUY+SELL 0,02, mức lưới 35 pip, TP từng lệnh 35 pip, không SL; kèm lệnh Limit xa lô gấp đôi 0,08→1,28 (hầu hết bị hủy); đóng cả rổ khi tổng lãi ≥ 0.
- Tái lập: Cơ chế rất rõ, lô đều → TÁI LẬP ĐƯỢC (ứng viên 1).
- Số lệnh (vị thế) 12591, 2016-10-07 → 2026-10-30; symbol: GBPUSD 12591; tỷ lệ BUY 0.499; lệnh chờ Stop 0, Limit 11858.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.249, tối đa 9 lệnh/rổ, bước lưới trung vị 35.0 pip (2.18 ATR), lô đầu trung vị 0.02; cặp BUY/SELL chồng thời gian: 6283.
- SL/TP: TP có ở 33% lệnh (trung vị 35.0 pip), SL có ở 0% (trung vị None pip); biên độ đóng trung vị 35.0 pip.
- Vốn: nạp 5,000, rút 5,000, lãi đóng lệnh 22,937, TWR tổng 7.0794, 10.06 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): atr14_pip: vào 16.094 vs ngẫu nhiên 14.864 (AUC đơn 0.598); gio: vào 14.0 vs ngẫu nhiên 12.0 (AUC đơn 0.534); thu: vào 2.0 vs ngẫu nhiên 2.0 (AUC đơn 0.522)

### 2378480 — XAUUSD
- Phong cách: Chỉ MUA vàng (99,9% buy), martingale hệ số lô 2,2, bước ~3 ATR, TP ~150 pip; vào sau đà tăng mạnh (RSI14 trung vị 65 vs 52 ngẫu nhiên, bb_z20 1,5 vs 0,2).
- Tái lập: Điểm vào tách được rõ nhất (AUC 0,79 cả khi bỏ giờ) nhưng phần quản lý là MARTINGALE → không chọn làm EA đầu tiên.
- Số lệnh (vị thế) 1226, 2021-11-09 → 2026-10-28; symbol: XAUUSD 1225, AUDUSD 1; tỷ lệ BUY 0.999; lệnh chờ Stop 0, Limit 0.
- Lô: kiểu martingale, hệ số lô trung vị 2.2, rổ nhiều lệnh 0.202, tối đa 21 lệnh/rổ, bước lưới trung vị 502.4 pip (3.03 ATR), lô đầu trung vị 0.24; cặp BUY/SELL chồng thời gian: 0.
- SL/TP: TP có ở 98% lệnh (trung vị 150.0 pip), SL có ở 2% (trung vị 279.2 pip); biên độ đóng trung vị 152.6 pip.
- Vốn: nạp 56,430, rút 49,150, lãi đóng lệnh 9,852, TWR tổng 2.2056, 4.97 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): rsi14: vào 64.982 vs ngẫu nhiên 51.743 (AUC đơn 0.767); bb_z20: vào 1.475 vs ngẫu nhiên 0.235 (AUC đơn 0.762); loi_suat_5bar_atr: vào 1.354 vs ngẫu nhiên 0.14 (AUC đơn 0.75)

### 2391346 — XAUUSD
- Phong cách: XAUUSD, 64% lệnh mở lúc 9h server (mở phiên Âu), lô trung vị 2,0, có hedge, giữ trung vị 18 phút; rút ròng lớn (rút 230.000 vs nạp 54.500).
- Tái lập: Luật GIỜ (AUC cây 0,89 có giờ; bỏ giờ < 0,5); chiều không đoán được (AUC 0,52) → thiếu luật chọn chiều.
- Số lệnh (vị thế) 888, 2021-05-04 → 2026-10-28; symbol: XAUUSD 886, BTCUSD 1, DOW 1; tỷ lệ BUY 0.503; lệnh chờ Stop 0, Limit 0.
- Lô: kiểu co_dinh_dca, hệ số lô trung vị 1.0, rổ nhiều lệnh 0.068, tối đa 67 lệnh/rổ, bước lưới trung vị 33.0 pip (0.22 ATR), lô đầu trung vị 2.0; cặp BUY/SELL chồng thời gian: 70.
- SL/TP: CHƯA ĐO ĐƯỢC (CSV dạng deal); biên độ đóng trung vị 131.0 pip.
- Vốn: nạp 54,500, rút 230,000, lãi đóng lệnh 602,426, TWR tổng 306.932, 5.51 năm.
- Đặc trưng phân biệt hàng đầu (có giờ): gio: vào 8.0 vs ngẫu nhiên 13.0 (AUC đơn 0.329); thu: vào 2.0 vs ngẫu nhiên 2.0 (AUC đơn 0.523); atr14_pip: vào 114.84 vs ngẫu nhiên 94.112 (AUC đơn 0.522)

## Ứng viên tái lập (không chọn martingale thuần)

| Ứng viên | Từ tín hiệu | Luật | EA nháp |
|---|---|---|---|
| UV1 Lưới hedge TP35 | 2330430 | Mỗi mức 35 pip luôn có 1 BUY + 1 SELL, TP từng lệnh 35 pip, không SL; đóng tất cả khi tổng lãi nổi ≥ 0 và ≥ 6 lệnh mở; lô = LotMoi1000 × số dư/1000. (Bỏ lớp Limit lô gấp đôi vì hầu hết bị hủy và là martingale.) | `ea_demo/BRAIN_DN_LuoiHedgeTP.mq5` + `.set` |
| UV2 Rổ DCA hedge | 2262642 | Hai rổ BUY/SELL độc lập; thêm lệnh lô đều khi giá đi ngược 15 pip từ lệnh cuối (≤140 lệnh); đóng rổ khi giá về giá trung bình ± 11 pip, rồi mở lại ngay. | `ea_demo/BRAIN_DN_RoDCAHedge.mq5` + `.set` |
| UV3 Bẫy tin (chỉ thẻ) | 1862128/1864588/2302081 | Buy Stop + Sell Stop đặt lúc 15:29:58 server, SL ~5 pip, TP 100 pip, hủy sau ~1 phút. | KHÔNG viết EA: cần tick thật lúc tin, kết quả CHƯA ĐO ĐƯỢC |

Điểm vào của UV1/UV2 không dùng điều kiện chỉ báo vì AUC bỏ giờ chỉ ~0,6 (yếu). 2378480 có điểm vào rõ nhất (mua vàng sau đà tăng, AUC 0,79) nhưng quản lý martingale 2,2× → để sau.

## MÔ PHỎNG Python (`nhan/dich_nguoc/backtest_luoi.py`) — BỊ THAY THẾ bởi `reports/DICH_NGUOC_VONG2_SWAP_VANG.md` (có swap + margin)

Giả định: H1 BID, đường đi trong nến O→L→H→C (nến tăng) / O→H→L→C (nến giảm), chèn mọi mức lưới; spread cố định AUDCAD 2,5 pip, GBPUSD 1,5 pip; giá trị pip/lot AUDCAD ≈ 7,3 USD (cố định); **KHÔNG tính swap** (với lưới hedge giữ lâu, swap âm hai chiều có thể đáng kể — CHƯA ĐO ĐƯỢC); không mô phỏng margin/stop-out ngoài equity ≤ 0; vốn 1.000 USD, lô lãi kép theo số dư. DD = equity xấu nhất trong nến (H/L) so với đỉnh. Đây chưa phải Strategy Tester real tick.

| Ứng viên | Dữ liệu | Lô/1000 USD | Equity cuối | CAGR | DD max | Cháy | ĐẠT? |
|---|---|---|---|---|---|---|---|
| UV1_luoi_hedge_tp35_(2330430) | AUDCAD_H1_2008_2026 | 0.01 | 0 | -100.0% | 100.0% | 2008-06-02 08:00:00 | không |
| UV1_luoi_hedge_tp35_(2330430) | AUDCAD_H1_2008_2026 | 0.004 | 0 | -100.0% | 100.0% | 2008-10-06 12:00:00 | không |
| UV1_luoi_hedge_tp35_(2330430) | AUDCAD_H1_2008_2026 | 0.002 | 0 | -100.0% | 100.0% | 2008-10-08 11:00:00 | không |
| UV1_luoi_hedge_tp35_(2330430) | AUDCAD_H1_2008_2026 | 0.001 | 11,264 | 13.8% | 60.0% | không | ĐẠT (MÔ PHỎNG) |
| UV1_luoi_hedge_tp35_(2330430) | AUDCAD_H1_2008_2026 | 0.0005 | 3,199 | 6.4% | 27.0% | không | không |
| UV2_ro_dca_hedge_15pip_(2262642) | AUDCAD_H1_2008_2026 | 0.01 | 0 | -100.0% | 100.0% | 2008-08-12 08:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | AUDCAD_H1_2008_2026 | 0.004 | 0 | -100.0% | 100.0% | 2008-08-26 15:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | AUDCAD_H1_2008_2026 | 0.002 | 0 | -100.0% | 100.0% | 2008-09-16 03:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | AUDCAD_H1_2008_2026 | 0.001 | 0 | -100.0% | 100.0% | 2008-10-06 17:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | AUDCAD_H1_2008_2026 | 0.0005 | 3,816 | 7.4% | 83.0% | không | không |
| UV1_luoi_hedge_tp35_(2330430) | GBPUSD_H1_2024_2026 | 0.01 | 0 | -100.0% | 100.0% | 2024-09-25 02:00:00 | không |
| UV1_luoi_hedge_tp35_(2330430) | GBPUSD_H1_2024_2026 | 0.004 | 6,978 | 102.9% | 91.9% | không | không |
| UV1_luoi_hedge_tp35_(2330430) | GBPUSD_H1_2024_2026 | 0.002 | 2,417 | 37.9% | 40.1% | không | ĐẠT (MÔ PHỎNG) |
| UV1_luoi_hedge_tp35_(2330430) | GBPUSD_H1_2024_2026 | 0.001 | 1,505 | 16.1% | 18.8% | không | ĐẠT (MÔ PHỎNG) |
| UV1_luoi_hedge_tp35_(2330430) | GBPUSD_H1_2024_2026 | 0.0005 | 1,210 | 7.2% | 9.7% | không | không |
| UV2_ro_dca_hedge_15pip_(2262642) | GBPUSD_H1_2024_2026 | 0.01 | 0 | -100.0% | 100.0% | 2024-09-20 09:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | GBPUSD_H1_2024_2026 | 0.004 | 0 | -100.0% | 100.0% | 2025-01-08 13:00:00 | không |
| UV2_ro_dca_hedge_15pip_(2262642) | GBPUSD_H1_2024_2026 | 0.002 | 3,486 | 57.6% | 79.3% | không | ĐẠT (MÔ PHỎNG) |
| UV2_ro_dca_hedge_15pip_(2262642) | GBPUSD_H1_2024_2026 | 0.001 | 1,873 | 25.7% | 38.1% | không | ĐẠT (MÔ PHỎNG) |
| UV2_ro_dca_hedge_15pip_(2262642) | GBPUSD_H1_2024_2026 | 0.0005 | 1,370 | 12.2% | 18.0% | không | ĐẠT (MÔ PHỎNG) |

**Đọc kết quả trung thực**:
- Trên chuỗi dài AUDCAD 2008–2026 (18,8 năm), chỉ **UV1 lô 0,001/1000 USD** qua tiêu chí: CAGR 13,8%, DD 60,0% (MÔ PHỎNG, chưa trừ swap). Lô ≥ 0,002 đều CHÁY năm 2008. UV2 cháy ở mọi lô ≥ 0,001 (năm 2008); lô 0,0005 sống nhưng DD 83% và CAGR 7,4% → KHÔNG ĐẠT.
- GBPUSD chỉ có 2,75 năm (2024–2026) → các dòng “ĐẠT” trên GBPUSD là **chuỗi ngắn, không đủ** theo luật dữ liệu dài nhiều năm; không dùng làm bằng chứng.
- UV1 trên GBPUSD chưa kiểm được trên chuỗi dài (thiếu dữ liệu GBPUSD trước 2024 trên box).
- Việc tiếp: chạy hai EA nháp trên MT5 Strategy Tester real tick (máy nhà), có swap thật XM, trên AUDCAD/GBPUSD dài nhất có thể; thêm swap vào mô phỏng.
