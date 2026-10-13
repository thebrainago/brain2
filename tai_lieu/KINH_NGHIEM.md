# KINH NGHIỆM GIAO DỊCH (rút từ vòng 1–26, cập nhật vòng 27). Tất cả là MÔ PHỎNG trừ khi ghi MT5.
1. **Kết quả quá đẹp = lỗi trước.** Vòng 25 lần đầu ra 27 "hệ sống" do lookahead (mảng thoát dùng s[i+1]); sửa xong còn 0. Mọi hàm tín hiệu phải có test cắt dữ liệu.
2. **Phí ăn hết cạnh khung nhỏ.** RSI_Exhaustion M5 EURUSD có lãi GỘP cả hai nửa nhưng spread XM ≈ 68 % biên độ nến M5 trung vị → ròng âm (kiểm −4,1 %). Khung M5/M15 chỉ đáng thử khi cạnh thô > ~3× spread.
3. **Giờ vào lệnh quan trọng ngang tín hiệu.** Spread 00h server (mở nến D1) đắt gấp 3–5 lần 02h (GBPUSD 3,9 vs 0,74 bps; AUDUSD 5,3 vs 1,65). Hệ D1 nên vào lệch giờ (EA MRZ `InpGioVao=2`).
4. **Near-miss tốt nhất tới nay:** MRZ (z50 ±2, TR2) D1 AUDUSD vào 02h: sau phí 29,5 / 67,8 bps/lệnh, p 0,008, DD 15 % — nhưng Holm cộng dồn 1,0 → KHÔNG qua. Không được nới cổng.
5. **Ghép danh mục với hệ phá vỡ (DINH20) làm xấu đi** mọi nhóm vòng 26; lọc EMA200 làm còn < 30 lệnh/nửa → CHƯA ĐO ĐƯỢC.
6. **Lưới/martingale**: Sharpe/t không đủ để giữ; đuôi stop-out kiểu MT5 phải mô phỏng, nếu không lãi giả.
7. **Dữ liệu MT5 cũ của XM yếu** (AUDUSD 2004–2015 chất lượng mô hình ~4 %) → giai đoạn cũ chưa kiểm chứng MT5.
8. **Bộ đọc EA**: phần lớn EA tải về là công cụ (guard/panel/calculator, không có điều kiện vào) — tỷ lệ dịch thấp (3/78) không chủ yếu do bộ đọc. Lý do thật còn lại: hàm trả hướng int qua biến cục bộ (`dir = CheckBreakout()`), lệnh trong vòng for/while, so sánh chuỗi trạng thái.
9. **Swap**: nhóm '#' tài khoản XM thật swap DISABLED; mô hình cũ trừ 2,5 %/năm — giữ để bảo thủ.
10. **Holm cộng dồn** đã > 12.900 phép thử: một hệ cần p một phía cỡ < 4e-6 mới qua. Ưu tiên ít ô, có chủ đích, đa tài sản (gộp tăng n), thay vì quét lưới rộng.
11. **Spread ×1,5 + trượt 1 bps** là phép thử áp lực bắt buộc; nhiều hệ chết ở đây.
12. Nguồn TradingView/fxblue/quantpedia bị 403/Cloudflare trên box → CHƯA ĐO ĐƯỢC, không vượt; chuyển sang máy nhà.
13. **(Chu kỳ 3, 13/10) Đo bộ đọc trên TOÀN KHO, không chỉ lô mới.** Kho 3.204 tệp duy nhất (md5): 726 công cụ không có lệnh đặt, 100 không phải EA, 2.378 EA có lệnh → dịch được 81 → 85 (3,41 % → 3,57 %). Tỷ lệ dịch thấp là đuôi dài: mỗi EA hỏng thường có 2–3 chỗ chặn nối nhau (sửa chỗ đầu chỉ lộ chỗ sau). Lý do hàng đầu còn lại: điều kiện chưa dịch được (881), gọi hàm phụ (465), không tìm được guard (356).
14. **Ba ngôi `cond ? trade.Buy : trade.Sell` từng sinh luật NGƯỢC CHIỀU.** Sau chuyên biệt hoá, `(true) ? Buy : Sell` không được gập → bộ đọc nhận CẢ HAI chiều cho mỗi chỗ gọi: 3 EA (EA_Template, RsiLevel, RsiReversal) mỗi cái có 2 luật sai chiều (bán khi cắt lên). Đã gập hằng → còn 2 luật đúng. Luật từ bộ đọc phải được đối chiếu chiều với mã gốc trước khi tin.
15. **Bộ đọc chặn nhầm `if(A && B) F();`** (lý do "sau toán tử điều kiện"): kiểm `and/or/?` trên cả câu lệnh thay vì phần còn lại sau `if(...)`. Test đơn vị nhỏ bắt được cả lỗi else treo (`if(a) if(b) x; else …`) trước khi đưa vào kho.
