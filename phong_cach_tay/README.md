Walk-forward + MT5 cửa sổ đầy (22:25 UTC+7 27/11/2026): `bao_cao/BAO_CAO_VANG_WF.md`. Ứng viên Python `flat_orphan=1` maxL=8: +57.231,94 / DD 13,14%, WF 12/12, stress 15/15 — **MT5 p4 tick thật cùng cửa sổ −9.993,99 / DD 99,94%** (cháy từ rổ bán DCA 01/10/2025, không đợi tháng 1). Bộ guard v1.02 (dca_mode=2, short_cap 0,04, max_lc 2/6900, day 15%, week 20%, eq_lot): MT5 −8.941,37 / DD 90,47%, còn 1.058,63. Chưa cấu hình nào đạt lãi>0 và DD<80% trên MT5. Không đặt lệnh thật.

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
- `ma/may_v2.py` — máy tay_v2 (cụm, TP giá, DCA cố định, hedge, đóng rổ; flcap / hfrac / dca_max_bars).
- `ma/chay_v2.py`, `chay_v2_p1.py`, `chay_vang_an_toan.py` — 7 bước, lọc P1, chữa cháy vàng.
- `tin_hieu_data.py` — sinh tín hiệu Part 1 (**không sửa**).

Động cơ mô phỏng: `vang/ma/may_hyb.py`. Báo cáo cũng được sao vào `vang/bao_cao/PHONG_CACH_TAY.md` và `sp500/bao_cao/PHONG_CACH_TAY.md`.

Chữa cháy vàng (20:50 UTC+7): `bao_cao/BAO_CAO_VANG_AN_TOAN.md`. Mặc định vàng L0=0,01 K=4 hfrac=1 lọc delta15: +14.032,99 USD, DD 34,24% trên Jun–Nov (stress 8/11). US500 mặc định `p1_union_es`.

Tối ưu 11 stress (21:31 UTC+7): `bao_cao/BAO_CAO_VANG_11.md`. Mặc định vàng L0=0,01 K=4 loss_close=0,30 adx_th=30 lọc delta15: +15.930,00 USD, DD 31,08%, stress 11/11.

Đối chiếu MT5 + stress hai chiều (21:55 UTC+7): `bao_cao/BAO_CAO_TAYV2_MT5.md`, `bao_cao/BAO_CAO_VANG_2CHIEU.md`. Mặc định 59672872 cháy trên MT5 tick 2025.09–2026.11 (−9.994,02 / DD 99,94%) và gãy gap vàng tăng (13/15). Ứng viên `short_cap=0,04` + cooldown 20.000: Jun–Nov +9.959,63 / DD 21,74%, stress 15/15; cửa sổ dài +2.359,88 / DD 66,24% (Python, chưa MT5).
