# Dịch tay đợt 4 (grokbot-tay) — 21/10/2026 (giờ Sài Gòn, UTC+7)

Không gọi ai-box / LLM trả phí (0 lần gọi, 0 token). Lần đầu dùng **chế độ lưới** (`"luoi"`, nhan/luoi_hai_chieu.py) cho EA
lưới vô điều kiện / lưới có bộ lọc chiều: giữ ĐÚNG tham số mặc định của tác giả (bước, TP, hệ số lot, số tầng), không tối ưu quản trị.
Bản dịch: `data/tho_box/dich_tay/<bam>.json`, mã sinh `data/tho_box/dich_tay_grok/viet2.py` (data/ không vào git).

## Kết quả đo

| Bước | Số |
|---|---|
| Mã nguồn đã dịch | 17 (12 lưới tham số tác giả, 5 python) → 18 thẻ |
| Kiểm tự động | 17 DAT / 1 HONG (BonusTrader v1.4: IT_LENH, 2 rổ lưới thật < 3 trên giá mẫu) |
| Lọc Python 65/15 sau phí (lot thật) | **2 DAT_LOC / 15 TRUOT_LOC** |
| Việc MT5 mới (VAO_CSV, XM + Exness) | 4 (2 thẻ) → hang_cho_mt5_box.jsonl |

Đạt lọc (MÔ PHỎNG, chưa MT5):

| Thẻ | EA | Mã/khung | Lãi %/năm | DD % |
|---|---|---|---|---|
| sk_ea_b7faac890a | Zerith Oneshot (DeMarker, 1 lệnh/phiên) | GBPUSD H1 | 75.0 | 62.2 |
| sk_ea_a0d40c82ed | Hon-Matrix (kênh + RSI, gần đúng) | EURUSD H1 | 19.0 | 16.5 |

Lưới tham số tác giả tốt nhất nhưng trượt: Blessing 3 (CADJPY H4 13.1%/33.0%), nyao (python, GBPCHF H1 13.5%/45.1%),
Dynamic Volatility (python, USDJPY H4 12.7%/50.7%).

## Tỉ lệ qua lọc theo đường dịch (CSDL box, cộng dồn)

| Người dịch / đường | DAT_LOC | TRUOT_LOC |
|---|---|---|
| qwen3.7-max python | 22 | 56 |
| qwen3.7-max spec | 17 | 49 |
| grokbot-tay python | 22 | 41 |
| grokbot-tay spec | 7 | 29 |
| grokbot-tay lưới (tham số tác giả) | 1 | 16 |

Nhận xét đo được: lưới giữ nguyên tham số tác giả qua lọc 1/17 — tham số mặc định tác giả hiếm khi đạt >15%/năm với DD<65%.
