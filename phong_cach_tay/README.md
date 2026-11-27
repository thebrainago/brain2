# phong_cach_tay — máy phong cách tay (dùng chung XAU và US500)

Mã dùng chung cho Part 2: đọc phong cách giao dịch tay của Anh từ lịch sử XM (và transcript XAUUSD Scalp Bot), mã hóa thành máy quy tắc trên tài khoản **cent**, kiểm 7 bước trên vàng và SP500.

Không đặt / sửa / đóng lệnh thật. Không đóng terminal MT5.

## Cấu trúc

- `du_lieu/` — xuất chỉ-đọc từ XM Global MT5 (demo 345930355), 27/11/2026.
- `ma/phan_tich_lich_su.py` — trích SL, hedge, DCA, cụm vào/ra, thời gian giữ, DD.
- `ma/may.py` — tham số máy (HYB+AG chỉnh theo số đo được) + quy tắc xác nhận chỉ báo.
- `ma/chay_kiem_7_buoc.py` — IS/OOS, spread ×2, 11 stress, lân cận, cháy vs 80%, DSR, nhật ký bóng.
- `bao_cao/` — báo cáo tiếng Việt.
- `ket_qua/` — CSV/JSON số đo.

Động cơ mô phỏng: `vang/ma/may_hyb.py`. Báo cáo cũng được sao vào `vang/bao_cao/PHONG_CACH_TAY.md` và `sp500/bao_cao/PHONG_CACH_TAY.md`.
