# Vòng 30 — KẾT QUẢ (MÔ PHỎNG, không phải MT5/tiền thật)

Tiền đăng ký: `reports/vong30_tien_dang_ky.md` (commit c23c73fe, trước khi chạy GĐ2). Tính chất sóng: `reports/tinh_chat_song.md` (+ `.json`, có cột điểm đủ số lẻ cho FX).
Mã: `nhan/song_zigzag_atr.py` (ZigZag-ATR, test không nhìn trước `test_song_zigzag_atr.py`), `v30.py`.
Phí XM Ultra Low (spread trung vị H1 + 1 bps trượt, swap 0). Holm cộng dồn 13000 → **13029**.

Luật quản lý: NGƯỢC = vào ngược chân sóng đẩy; chốt = tỉ lệ hồi p50 (GĐ1) × quãng đã đi; dừng = p90 biên độ đẩy (ATR) + đệm 0,5 ATR; giữ tối đa p90 số nến sóng hồi.
THUẬN = vào theo xu khi sóng hồi đạt tỉ lệ p50–p70 của sóng đẩy trước; chốt = về lại đỉnh/đáy sóng đẩy; dừng = quá chân sóng đẩy + 0,5 ATR.

Lưu ý đọc số: với MA200 làm “xu lớn”, tỉ lệ hồi p50 ≈ 0,9–1,05 (sóng hồi thường DÀI bằng sóng đẩy) → chốt gần như hồi trọn → win rate thấp. Volume: CHƯA ĐO ĐƯỢC (HistData không có volume thật).

Cột mỗi giai đoạn: lệnh / win % / PF / bps/lệnh / maxDD % (1 đơn vị, cộng bps) / MFE TB bps.

| Loại | Chiều | Khung | Hệ | GĐ1 | GĐ2 | p GĐ2 | p Holm | Qua? |
|---|---|---|---|---|---|---|---|---|
| luat_anh | nguoc | H1 | LUAT_P70 | 1056 / 38.5 / 0.83 / -4.24 / 57.31 / 43.9 | 975 / 39.9 / 0.86 / -3.86 / 49.25 / 49.7 | 0.941 | 1 | không |
| luat_anh | nguoc | H1 | LUAT_P90 | 355 / 14.1 / 0.72 / -3.32 / 16.83 / 27.9 | 326 / 9.5 / 0.43 / -8.52 / 28.16 / 30.0 | 1 | 1 | không |
| luat_anh | thuan | H1 | THUAN_GOC_r50_r70 | 1911 / 15.4 / 0.69 / -3.68 / 75.43 / 24.7 | 1907 / 16.3 / 0.77 / -2.86 / 64.34 / 27.2 | 1 | 1 | không |
| luat_anh | nguoc | H4 | LUAT_P70 | 251 / 38.2 / 0.85 / -7.73 / 39.84 / 90.6 | 241 / 44.0 / 1.28 / 15.14 / 29.12 / 125.3 | 0.155 | 1 | không |
| luat_anh | nguoc | H4 | LUAT_P90 | 86 / 10.5 / 0.56 / -10.72 / 12.71 / 53.4 | 66 / 13.6 / 0.28 / -17.37 / 12.39 / 40.0 | 1 | 1 | không |
| luat_anh | thuan | H4 | THUAN_GOC_r50_r70 | 503 / 18.3 / 1.0 / 0.06 / 23.16 / 57.1 | 541 / 16.6 / 0.91 / -2.15 / 29.6 / 53.4 | 0.745 | 1 | không |
| luat_anh | nguoc | D1 | LUAT_P70 | 344 / 40.7 / 0.78 / -36.78 / 127.46 / 266.8 | 315 / 42.2 / 1.06 / 10.29 / 94.14 / 328.3 | 0.423 | 1 | không |
| luat_anh | nguoc | D1 | LUAT_P90 | 114 / 7.9 / 0.42 / -37.27 / 44.0 / 145.0 | 92 / 14.1 / 1.09 / 6.7 / 27.55 / 248.9 | 0.411 | 1 | không |
| luat_anh | thuan | D1 | THUAN_GOC_r50_r70 | 689 / 20.0 / 1.12 / 7.54 / 40.61 / 157.7 | 723 / 18.8 / 0.98 / -1.43 / 66.7 / 148.9 | 0.582 | 1 | không |
| to_hop | nguoc | D1 | ibs+nen | 99 / 47.5 / 1.2 / 21.84 / 17.59 / 247.2 | 85 / 37.6 / 0.44 / -79.91 / 84.44 / 175.7 | 0.998 | 1 | không |
| to_hop | nguoc | H4 | p90+macd | 59 / 18.6 / 2.2 / 23.73 / 2.6 / 87.2 | 40 / 22.5 / 4.45 / 56.91 / 2.44 / 117.2 | 0.108 | 1 | không |
| to_hop | nguoc | H4 | rsi_dk+macd | 112 / 33.0 / 1.33 / 14.35 / 14.42 / 110.7 | 87 / 37.9 / 0.79 / -9.96 / 14.32 / 95.0 | 0.719 | 1 | không |
| to_hop | nguoc | H1 | pin+macd | 124 / 38.7 / 1.52 / 10.28 / 4.64 / 53.5 | 108 / 37.0 / 0.7 / -5.92 / 9.25 / 36.4 | 0.894 | 1 | không |
| to_hop | nguoc | D1 | p90+macd | 74 / 14.9 / 1.24 / 13.19 / 16.65 / 161.7 | 55 / 5.5 / 0.24 / -50.75 / 30.73 / 129.9 | 1 | 1 | không |
| to_hop | nguoc | H1 | p90+macd | 216 / 16.7 / 1.53 / 5.94 / 8.9 / 34.6 | 222 / 9.9 / 0.26 / -10.78 / 25.65 / 26.2 | 1 | 1 | không |
| to_hop | nguoc | H1 | p70+pin | 358 / 35.8 / 1.15 / 2.83 / 10.51 / 44.8 | 313 / 30.7 / 0.72 / -5.24 / 20.32 / 34.4 | 0.975 | 1 | không |
| to_hop | nguoc | H1 | pin+gio | 574 / 39.4 / 1.07 / 1.38 / 20.01 / 45.3 | 510 / 38.8 / 0.9 / -2.34 / 20.76 / 41.8 | 0.778 | 1 | không |
| to_hop | nguoc | D1 | pin+rsi_dk | 60 / 31.7 / 1.03 / 4.05 / 29.65 / 302.3 | 82 / 37.8 / 0.92 / -8.04 / 34.9 / 179.3 | 0.618 | 1 | không |
| to_hop | nguoc | H1 | macd+gio | 1078 / 42.4 / 1.04 / 0.91 / 30.21 / 47.3 | 1031 / 40.8 / 0.99 / -0.2 / 19.76 / 49.0 | 0.533 | 1 | không |
| to_hop | thuan | D1 | nen | 102 / 26.5 / 1.8 / 42.15 / 8.94 / 217.5 | 103 / 6.8 / 0.19 / -55.09 / 56.75 / 96.0 | 1 | 1 | không |
| to_hop | thuan | D1 | macd | 316 / 19.9 / 1.36 / 21.65 / 35.23 / 173.5 | 345 / 16.2 / 0.9 / -5.84 / 56.25 / 140.7 | 0.705 | 1 | không |
| to_hop | thuan | D1 | nen+ma200 | 49 / 32.7 / 1.87 / 50.28 / 9.95 / 295.0 | 49 / 8.2 / 0.17 / -68.58 / 33.6 / 111.3 | 1 | 1 | không |
| to_hop | thuan | D1 | pin+ma200 | 118 / 25.4 / 1.54 / 26.79 / 14.39 / 214.2 | 186 / 18.8 / 1.13 / 6.07 / 15.39 / 123.1 | 0.309 | 1 | không |
| to_hop | thuan | D1 | pin | 204 / 23.5 / 1.38 / 19.36 / 20.78 / 179.4 | 351 / 18.2 / 1.03 / 1.54 / 25.11 / 116.9 | 0.425 | 1 | không |
| to_hop | thuan | D1 | macd+ma200 | 184 / 20.7 / 1.31 / 19.28 / 18.06 / 178.5 | 191 / 17.3 / 1.03 / 1.81 / 36.45 / 152.5 | 0.457 | 1 | không |
| to_hop | thuan | D1 | nen+ibs | 53 / 22.6 / 1.6 / 35.49 / 15.08 / 184.2 | 45 / 6.7 / 0.22 / -61.89 / 27.85 / 115.3 | 1 | 1 | không |
| to_hop | thuan | D1 | ma200 | 459 / 21.4 / 1.18 / 11.72 / 26.77 / 169.5 | 451 / 17.5 / 0.85 / -9.57 / 80.02 / 141.4 | 0.879 | 1 | không |
| to_hop | thuan | D1 | nen+pin | 32 / 25.0 / 1.92 / 37.73 / 4.15 / 305.3 | 38 / 13.2 / 1.09 / 3.56 / 5.65 / 127.9 | 0.449 | 1 | không |
| to_hop | thuan | D1 | macd+pin | 55 / 20.0 / 1.37 / 18.3 / 11.3 / 139.4 | 111 / 17.1 / 0.92 / -3.17 / 11.56 / 99.3 | 0.622 | 1 | không |

**Kết luận: 0/29 ô qua Holm.** Luật p70/p90 của Anh âm GĐ1 ở cả 3 khung; p90 âm hoặc ≈0 cả hai. Tổ hợp tốt nhất GĐ2: NGƯỢC H4 p90+MACD (GĐ2 40 lệnh, PF 4,45, +56,9 bps, p 0,11) — quá ít lệnh. THUẬN D1 pin+MA200 dương nhẹ cả 2 (PF 1,54 / 1,13). Phần lớn tổ hợp chọn từ GĐ1 sụp ở GĐ2 (khớp nhiễu).

Chưa đo: volume, giờ vào D1 (02h), RSI khung lớn thật (đang xấp xỉ bằng RSI chu kỳ ×4 cùng khung), ZigZag khung lớn làm xu (chỉ dùng MA200), MT5.
