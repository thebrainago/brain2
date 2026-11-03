# Nhánh chỉ số — theo xu hướng trên chỉ số chứng khoán (04/11/2026)

## 1. Lý do
Anh: “nhóm đó là một nhánh đáng nghiên cứu vì chỉ số có xu hướng và động lực tốt hơn”. Chỉ số chứng khoán (US500, US30, US100, GER40) có xu hướng tăng dài hạn, nên hệ **thiên mua, theo xu hướng** có lợi thế cấu trúc mà cặp FX không có.

## 2. Phát hiện trước đây (từ repo)
- **Swap mua XM cao:** `US500Cash` đo 13/09/2026 = −1,21 USD/lot/đêm ≈ 5,77 %/năm, thứ Sáu ×3 (`reports/onh_h1_lan_dau.md`). Giữ lệnh mua lâu ngày bị ăn mòn đáng kể → mọi kết quả phải là **net sau swap**.
- **Mua giữ có đòn bẩy sụt rất sâu năm 2008** (ghi nhận từ trao đổi trước; chưa tìm thấy bảng số cụ thể trong repo ở phiên này) → cần thoát theo chế độ thay vì giữ mãi.
- Tester MT5 trên `US500Cash#`: RSI/MRZ V24 âm (PF 0,45–1,13) (`tai_lieu/HANG_CHO_MAY_NHA.md`) — hồi quy ngắn hạn kiểu đó không phải hướng này.
- Lỗi cũ “0 lệnh trên chỉ số CFD” ở một số engine (`tai_lieu/BAN_GIAO_HE_THONG.md`) — cần kiểm số lệnh > 0 khi có kết quả.

## 3. Thiết kế EA `ea_demo/BRAIN_ChiSo_Trend.mq5`
- **Chế độ:** chỉ mua khi đóng cửa D1 > SMA200 D1 (`InpSmaCheDo`).
- **Kích hoạt** (`InpKichHoat`): 0 = phá đỉnh Donchian N nến, 1 = động lượng ROC N > 0, 2 = cả hai. Lọc ADX tùy chọn (`InpAdxMin`, 0 = tắt).
- **Dừng lỗ/trailing:** SL ban đầu `InpSlATR`×ATR; trailing kiểu chandelier `InpTrailATR`×ATR từ đỉnh cao nhất kể từ lúc vào.
- **Thoát chế độ:** đóng khi close D1 < SMA200 (đệm `InpDemCheDoPct`).
- **Lot:** % rủi ro theo khoảng SL (`InpKieuLot=1`, `InpRuiRoPct`) hoặc lot cố định; trần `InpLotMax`. Thợ nhân k vào `InpRuiRoPct`.
- **Swap:** Tester MT5 trừ swap thật của XM vào net; EA cộng dồn lợi gộp / swap / phí theo magic, ghi `brain2_chiso_log.csv` (thư mục Common) và `OnTester` trả về net ròng.
- Bán khống tắt mặc định (`InpChoBan=false`).

## 4. Việc đã xếp (`hang_doi/can_test/cs_*.json`, 24 việc, ưu tiên 60)
4 mã × 2 khung (D1, H4) × 3 biến thể; 2016.01.01–2026.10.01, model 4 (tick thật), vốn 10.000 USD, 1:500, k = 1, 2, 4 (rủi ro 1 %, 2 %, 4 %/lệnh).

| Biến thể | Kích hoạt | ADX | SL×ATR | Trail×ATR |
|---|---|---|---|---|
| A | Donchian 20 | tắt | 3,0 | 4,0 |
| B | ROC 60 | tắt | 3,0 | 5,0 |
| C | Donchian 55 + ROC 60 | ≥ 20 | 2,5 | 3,5 |

Mã: `US500Cash`, `US30Cash`, `US100Cash`, `GER40Cash`. ID: `cs_<ma>_<tf>_<A|B|C>`.

## 5. Tiêu chí đạt
DD < 80 % và CAGR > 10 %/năm, **net sau swap và phí**; được phép nâng lot (k). Kiểm thêm: số lệnh > 0, swap chiếm bao nhiêu % lợi gộp.

## 6. Cần xác minh trên máy nhà
- **Tên mã:** repo có `US500Cash#` và `GER40Cash#` trong sổ tester (`reports/mt5_lien_tuc/so_cai.jsonl`); `US30Cash`/`US100Cash` chỉ thấy dạng không `#`. Việc dùng tên không `#`; `ky_hieu_slot` trong `may_nha/tho_mt5.py` tự đổi sang `#` nếu slot thiếu. Chưa xác minh trên slot.
- **Biên dịch:** EA chưa biên dịch (box không có MetaEditor); thợ tự biên dịch khi chạy.
- Độ dài lịch sử tick chỉ số trên XM từ 2016 chưa kiểm; H4 dùng SMA200 D1 nhưng ATR theo H4.
- Swap lịch sử: Tester áp swap hiện tại cho cả quá khứ (xem A6 trong `reports/`) — kết quả có sai lệch chi phí.
