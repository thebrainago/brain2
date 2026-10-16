# 04 — Câu hỏi cần chủ dự án quyết (Grok KHÔNG tự điền)

Mỗi mục có chỗ trống `____`. Chủ dự án điền, hoặc ghi "bỏ qua" (khi đó giữ mặc định ghi bên cạnh).
Grok: nếu thấy chỗ trống còn trống, **dùng mặc định và ghi rõ trong báo cáo là mặc định**, đừng đoán số.

## 1. Ba số kinh tế (V, C, π) — làm cho ngưỡng α thôi là "mặc định học thuật"

`nhan/cong.py: nguong()` đã tự suy α từ ba số này (khóa trong `config/nguong.json`):

| Khóa | Nghĩa | Đơn vị | Điền |
|---|---|---|---|
| `gia_tri_mot_chien_luoc_tot_nam` (V) | Một chiến lược thật sự tốt đáng bao nhiêu mỗi năm | USD/năm | ____ |
| `thiet_hai_mot_chien_luoc_vo_dung_nam` (C) | Một chiến lược vô dụng bị tin nhầm làm mất bao nhiêu mỗi năm (tiền + thời gian + chi phí chờ) | USD/năm (cùng đơn vị V) | ____ |
| `xac_suat_tien_nghiem` (π) | Anh tin khoảng bao nhiêu % ý tưởng được đưa vào thử là thật | 0–1 | ____ |

Công thức đang chạy: `α = π·V / ((1−π)·C) · 0,5`, kẹp vào [0,001; 0,20]; `p_siet = α/5`. Ví dụ MINH HOẠ (không phải khuyến nghị):

| π | V | C | α suy ra |
|---|---|---|---|
| 0,02 | 1.000 | 100 | 0,102 |
| 0,01 | 1.000 | 200 | 0,0253 |
| 0,005 | 500 | 200 | 0,0063 |

Mặc định nếu bỏ qua: α = 0,05 (`MAC_DINH`). Lưu ý đơn vị V và C phải trùng nhau; α tăng khi π cao hoặc khi thiệt hại do tin nhầm thấp.

## 2. Mức rủi ro dùng trong định nghĩa "tốt" (`02` mục 1)

| Tham số | Gợi ý | Điền |
|---|---|---|
| `D_cap` — sụt giảm tối đa chấp nhận khi chọn đòn bẩy `f*` | 30 % | ____ |
| `ε` — xác suất cho phép vượt `D_cap` | 5 % | ____ |

Hiện có nhiều ngưỡng DD cùng tồn tại: duyệt thật `maxDD < 80 %` (`BAN_GIAO_GROK.md` mục 3, `VONG_LAP.md`); nhãn loại sớm `DD > 65 %` hoặc lãi `< 10 %/năm`
(luật chủ dự án 11/10, `hieu_chuan/P5_KET_QUA.md`), và `P6` đề xuất `DD > 50–65 %` hoặc lãi `< 5 %` nhưng **chưa chốt**.
Với `D_cap` thấp hơn nhiều so với 80 %, nhiều hệ DD 50–65 % hiện "qua" sẽ không còn qua. Chọn mức nào là quyết định của anh.

## 3. Kiểu thua chấp nhận được

Hệ lưới / tỉa lệnh / martingale (nhiều khoản lãi nhỏ, hiếm khoản lỗ lớn):
- ☐ Chấp nhận, miễn là CVaR 5 % ngày ≤ ____ % vốn và P(stop-out dưới stress) ≤ ____ %.
- ☐ Chỉ thử trên demo để học, không đưa vào danh sách "CHAY_DUOC".
- ☐ Không thử họ này nữa.

## 4. Forward demo (tầng 5)

| Tham số | Gợi ý | Điền |
|---|---|---|
| Có tài khoản demo riêng cho forward không (tên/server, KHÔNG đặt mật khẩu trong git) | | ____ |
| Thời hạn tối đa mỗi ứng viên | 8 tuần | ____ |
| `e1` — cạnh nhỏ nhất đáng giao dịch | 2× phí mỗi lệnh | ____ |
| Ai theo dõi và dừng | | ____ |

## 5. Ngân sách tìm kiếm

Chia công sức giữa (a) quét thêm tín hiệu kỹ thuật (nhiễu nhiều, prior thấp), (b) cạnh có cơ chế (carry/swap, trend đa tài sản vol-target, hiệu ứng qua đêm/lịch — nơi IBS US500/US100 đang nằm):

(a) ____ % · (b) ____ %. Gợi ý của mình: nghiêng về (b) hơn so với hiện nay, vì 20.503 ô (a) đã không cho gì.

## 6. Cách đưa vào vận hành

- ☐ Cho Grok làm ngay T0–T7 ở chế độ bóng (chỉ thêm số đo, không đổi cổng) — đề xuất của mình.
- ☐ Chờ anh duyệt từng mục trước.
- ☐ Gộp nhánh `de-xuat-cong-kiem-dinh` vào `main` để Grok `git pull` thấy (hiện chỉ ở nhánh, chưa vào `main`).
