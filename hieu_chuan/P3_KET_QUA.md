# P3 — swap theo từng lệnh + phí đúng thời kỳ (11/10/2026)

Mọi số là **MÔ PHỎNG** (EURUSD Dukascopy H1 2003-05 → 2021-12, giờ server Helsinki; phần kiểm 30 % cuối ≈ 2016-2021),
không phải tiền thật. Cổng giữ **không đổi** (không nới, không siết). Tài khoản khai báo 10.000 USD 1:100 stop-out 50 %.

## Đã sửa
1. **Swap theo lệnh, tính lúc rollover** (`chi_phi.dem_qua_dem`, `MoHinhChiPhi.kieu_qua_dem="nua_dem"`): chỉ lệnh CÒN MỞ qua
   nửa đêm giờ server mới trả swap; thứ Tư ×3 (FX; CFD ×3 thứ Sáu), thứ Bảy/CN 0. Trước: phí rải liên tục theo giờ (lệnh mở
   10:00 đóng 16:00 cũng trả swap; không có ×3 thứ Tư). Tổng một tuần vẫn = 7 đêm → lệnh giữ dài trả như cũ.
2. **Swap gắn vào từng lệnh trong rổ** (`mo_phong.chay_he`, `L["sw"]`): vốn ròng = số dư + lời thả nổi − swap lệnh mở (như MT5);
   đóng lệnh → số dư += lời − swap của lệnh đó; stop-out chọn lệnh LỖ NHẤT tính cả swap từng lệnh. Trước: swap trừ thẳng vào
   số dư chung. Kiểm: với mô hình phí cũ, kết quả vòng EURUSD **giống hệt từng số** bản trước (dc074dab) → phần tái cấu trúc trung tính.
3. **Tỉ lệ swap theo THÁNG** (`nhan/lai_suat_fx.py`, `config/lai_suat_qua_dem_thang.csv`, dựng bằng `hieu_chuan/p3_lai_suat.py`):
   swap mua(t) = [lãi qua đêm USD − EUR](tháng t) + markup sàn; bán(t) = −chênh + markup. Lãi suất: FRED DFF (USD),
   IRSTCI01EZM156N (EUR qua đêm; sau 01/2026 nối bằng ECBDFR − 0,066). Markup đo từ swap XM 09/2026: mua +1,04 %, bán +0,99 %/năm
   (đối xứng — hợp lý). **GIẢ ĐỊNH**: markup sàn không đổi theo thời gian (trước 2026 CHƯA ĐO ĐƯỢC).
   Chi phí giữ lệnh MUA EURUSD trung bình năm: 2003 −0,0 %, 2006 +3,2 %, 2008 −0,9 % (được nhận), 2012 +1,0 %, 2019 +3,6 %,
   2021 +1,7 % (hôm nay +2,48 %). Cặp không có lãi suất trong bảng → giữ tỉ lệ hôm nay + cảnh báo (không đoán).
4. **Spread theo NĂM** (`chi_phi.do_spread_theo_nam`): đo trung vị cột spread của bar từng năm khi dữ liệu CÓ cột spread (bar MT5).
   Dữ liệu EURUSD Dukascopy/komo/Yahoo hiện có **không có cột spread** → spread thời kỳ **CHƯA ĐO ĐƯỢC**; vẫn dùng spread XM hôm nay
   (1,63 bps) cho mọi năm → **lạc quan cho 2003-2010** (spread thời đó rộng hơn). Báo cáo in rõ dòng này.
- "Thời kỳ" = **tháng lịch** cho swap, **năm lịch** cho spread.
- Nhãn phiên bản trong báo cáo/JSON (`mo_hinh_phi`): `cp3` (cũ, `--phi-cu`) / `cp3+p3(swap_nua_dem,swap_theo_thang[,spread_theo_nam])`.
- Chỉ áp trong `vong_thu_nghiem` (mặc định). Các đường ống cũ gọi `chi_phi.tu_du_lieu` trực tiếp (quantlab…) giữ nguyên `cp3`.

## Số đo trước / sau (phần kiểm 2016-2021, sau tối ưu; `hieu_chuan/p3_so_sanh.txt`)
| hệ | loi_log kiểm | tài khoản: vốn cuối · DD vốn ròng · swap USD · stop-out | giữ | đạt 25/09 |
|---|---|---|---|---|
| Breakout5(-2-2) lưới | +6,666 → **+7,574** | 35.546 → **37.663** USD · 95,6 % → **95,4 %** · 1.375 → 1.393 · 9 → **7** | 0 → 0 (p 0,24 → 0,19; cháy/năm 89,8 % không đổi) | không → không (DD > 80 %, stop-out) |
| Breakout2 / 3 rổ hedge | −0,635 → −0,628 | 9.036 → 9.115 · 11,5 % → 10,7 % · 642 → 564 · 0 | 0 → 0 | không (lỗ) |
| Breakout2-2 rổ hedge | −0,499 → −0,497 | 8.741 → 8.762 · 17,9 % → 17,6 % · 845 → 824 · 0 | 0 → 0 | không (lỗ) |
| Breakout1 lệnh đơn | −0,408 → −0,408 | — | 0 → 0 | không (lỗ) |
| Template lệnh đơn | −0,425 → −0,421 | — | 0 → 0 | không (lỗ) |

- Ảnh hưởng nhỏ với lệnh đơn/hedge (+0,0004…+0,007 log); lưới Breakout5 nhạy hơn vì thời điểm swap đổi đường vốn → 2 lần
  stop-out ít hơn, vốn cuối +6 %; vẫn chạm 96 % DD → **vẫn loại**. Phần tối ưu (2003-2015, swap thấp hơn hôm nay):
  Breakout2-2 tham số gốc vốn cuối 68 → 4.656 USD — rổ hedge gần cháy rất nhạy với chi phí giữ lệnh.
- **Giữ lại: 0/6 trước và sau.** Không hệ nào đổi kết luận. Mô hình mới hơi ÍT phí hơn (lệnh trong ngày không trả swap;
  2016-2021 swap mua TB ≈ hôm nay), nên kết luận "không có lợi thế sau phí" càng chắc.
- CHƯA ĐO ĐƯỢC: spread lịch sử EURUSD (không có dữ liệu ask/spread 2003-2021); markup swap của sàn trước 2026;
  swap trên MT5 thật để đối chiếu (tester luôn ghi swap = 0 — gói the-brain B3).

Tái lập:

    python hieu_chuan/p3_lai_suat.py /duong/fred_csv     # dựng bảng lãi suất (tải FRED nếu thiếu)
    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/eurusd_h1_duka_jw_server.csv            # P3 (mặc định)
    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/eurusd_h1_duka_jw_server.csv --phi-cu   # mô hình cũ
