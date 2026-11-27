# Quy tắc máy phong cách tay (cent)

Nguồn: transcript XAUUSD Scalp Bot (agent `526b1021-99a6-43d7-9b5c-9cd1b79f4029`) + xuất deal/order chỉ-đọc từ terminal XM Global MT5 đang đăng nhập (C:\Program Files\XM Global MT5, demo 345930355, trade_mode=0). Exness cent `E:\exness_cent` **không có** trên máy — không khởi động terminal.

Thời điểm deal: 29/07/2026 16:27 → 27/11/2026 22:04 (giờ Việt Nam, UTC+7). 2870 deal, 2817 lệnh, 46 vị thế đang mở.

## Những gì Anh làm (số đo)

- **Không SL cứng:** 8/2817 lệnh có SL (0,28%), tất cả comment `grokmgr` (bot). 0/46 vị thế mở có SL/TP. Deal đóng: 2786 mobile, 23 expert, 3 SL, 2 TP, 1 client. Lệnh tay (magic=0) chiếm ~99%.
- **Vào cụm lot nhỏ:** lot trung vị 0,10. 72,7% cụm vào có ≥3 lệnh trong ≤2 giây. Vàng: cụm trung vị 4 lệnh (tối đa 34). US500: trung vị 5,5 (tối đa 26). Cùng giây, cùng giá, cùng chiều.
- **DCA theo khoảng, lot thường bằng nhau:** 124 lần thêm cùng chiều sau >2s. Vàng: khe giá trung vị 5,47, thời gian 14,5 phút, hệ số lot trung vị 1,0 (trung bình 1,82, tối đa 10). Tầng trước khi thêm: tối đa 77 (vàng), 57 (US500). Tầng đồng thời tối đa: vàng 86 mua / 58 bán / 110 cả hai.
- **Hedge nhiều lệnh nhỏ:** 890 lần vào ngược khi phía kia còn mở. Vàng: khe giá trung vị 21,37, tuổi rổ 49 phút (p75 ~5,8 giờ). US500: khe 80 điểm, tuổi trung vị ~17 giờ (hedge chậm hơn, kiểu AG). Lot hedge trung vị 0,10. Số lệnh đối ứng trung vị: vàng 16, US500 9.
- **Đóng theo lãi/lỗ tổng, cắt một phần:** 117 cụm đóng; 86,3% cụm có lãi. Cụm ≥5 lệnh: 56 lãi / 6 lỗ. Vàng cụm đóng trung vị 5 lệnh, lãi trung vị +89,7 (có cụm −27.454 và +17.294).
- **Giữ:** vàng trung vị 20,5 phút (nhanh <5 phút: +40.950, WR 97,4%; 30p–4h: −14.930). US500 trung vị 55 phút; giữ >1 ngày lỗ.
- **Vốn / DD:** PnL giao dịch thuần +68.680. DD chỉ-deal (không gồm thả nổi) 29.775. Tài khoản bị SetCustomBalance nhiều lần (20–21/11 và 25/11, gồm +900.000 lúc 23:15 25/11). Equity realized cuối ~1.029.935. Lỗ thả nổi tệ nhất từng ghi khoảng −52,4k vàng. Đang mở (US500): 37 mua 3,7 lot @7323,5 (−59,83) + 9 bán 0,9 lot @7227,47 (−68,19), không SL/TP.
- **Lời Anh (transcript):** không cắt lỗ hedge vì làm tài khoản tệ hơn; hedge nhiều lệnh nhỏ đóng nhanh; “chỉ cần không cháy thì luôn gỡ được”; 95 giờ giữ được; vàng lỗ sâu vì tăng lot không hệ số; 10.000 USD demo ↔ 100 USD cent.

## Quy tắc máy (đã mã hóa)

1. Không SL cứng.
2. Vào cụm K=3 lệnh nhỏ (vàng 0,03 lot / US500 0,30 lot trên vốn 10.000 USD = 1.000.000 USC).
3. Điểm vào: chỉ báo truyền thống S≥1 (BB M15 < −2σ, râu từ chối M5, 2 giờ đầu phiên Mỹ, ATR thấp; VWAP < −2σ trừ điểm). Vàng: tín hiệu Fxaurum chỉ vào khi S≥1 cùng chiều; tín hiệu ngược thì chặn. Không có data → dùng S truyền thống.
4. DCA: khoảng 3 ATR M15, neo vùng trong ±1,5 ATR (biên 1,5–4,8 ATR). Hệ số lot 1,15 (không phải 1,0 thuần — bài học tăng lot không hệ số). Trần 15 tầng (Anh từng >80; trần đó không an toàn trên cent).
5. Cắt 50% mỗi tầng tại +1 ATR M15; đóng rổ khi hòa/lãi tổng.
6. Hedge cụm 5 lệnh ngược = 1× rổ (tối đa 2×), TP 0,8 ATR M5; không DCA khi hedge đang mở.
7. AG 1,5× khi EMA200 D1 dốc âm và rổ ≥5 tầng hoặc >5 ngày; đóng khi EMA200 lấy lại hoặc hòa.
8. Tài khoản cent, vốn 10.000 USD (1.000.000 USC), đòn bẩy 1:1000 như demo. Không giao dịch thật.
