# Quy trình bàn giao (Grok → model tiếp)

Ngày: 2026-10-11. Repo: thebrainago/brain2, nhánh main.

## 1. Đọc theo thứ tự
- GHI_CHU_NANG_CAP_GROK.md (trạng thái + số đo mới nhất)
- Luật user: gói the-brain ban_giao_brain2/01 (mâu thuẫn thì 01 thắng)
- Repo thebrainago/brain2 nhánh main

## 2. Việc đang dang dở (uưu tiên)
1. Mở khung M5 trong vong_thu_nghiem để bot có .set (RSI_Exhaustion_Reversal, InpTimeframe=5) vào thử được — dữ liệu M5 công khai, không đoán khung khác. (Có thể đang chạy nền từ Grok.)
2. Sau đó: kho cơ chế tách rời (SL/TP ATR, thoát đỉnh lỗ nổi, lọc spread…) + giới hạn tổ hợp AB/AC tối đa 2–3 mảnh; không để nổ tổ hợp.
3. Chờ user: repo riêng tư hộp thư máy nhà↔cloud + Python/git máy nhà; đăng nhập Telegram nếu muốn kênh mới.

## 3. Luật vận hành (không đổi)
- Mục tiêu tiền; số phải đo được; chưa đo ghi CHƯA ĐO ĐƯỢC; mô phỏng ghi rõ mô phổng.
- Duyệt thật: lãi sau phí + maxDD <80%. Cổng chặt brain2 chỉ gắn nhãn, chưa đổi cổng.
- Loại sớm (nhãn): nghiêng lãi <5%/năm hoặc DD ~50–65% — chưa chốt số cuối.
- Không đưa khóa/token/mật khẩu vào git. Không tự join nhóm Telegram. Không mua VPS/nâng lõi khi chưa có số đo nghẽn.
- Python mô phổng trước → MT5 chỉ cho danh sách ngắn đã qua lọc. Giả lập lưới từng lạc quan hơn MT5 (~2 lần trên ô sạch).

## 4. Bản đồ module
- Seeker: tru/seeker.py, nhan/cau_kho_ma.py, nhan/truy_van_seeker.py, nhan/xep_hang_ung_vien.py, nhan/dieu_toc.py, nhan/tg_cong_khai.py
- Hephaestus: nhan/doc_ma.py, nhan/huong_int_mql.py, nhan/mql4_chuan.py
- QuantLab: vong_thu_nghiem.py, nhan/mo_phong.py, nhan/luoi_duong.py, mau_thu/do_moc.py
- Evo: dieu_phoi.py

## 5. Số đo gần nhất (chạy lại trước khi tin)
- Tập chờ: dịch được 4/94 điểm vào (RiskGuardLite, EMA_Cross_Demo hạng A; mô phổng EURUSD H1 có phí: không giữ).
- 3 bot MQL4 có .set: đọc cú pháp được, dịch logic 0/3.
- RSI_Exhaustion: chỉ .set M5 — chưa vào --theo-hang đến khi có M5.
- Commit gần: f164440f (int-dir + làn MQL4); trước đó 9f86bc31, 6a9936eb.

## 6. Cách nhận việc
1. git pull trên /workspace/brain2 (hoặc clone thebrainago/brain2).
2. Python: /workspace/venv/bin/python.
3. Đo: python mau_thu/do_moc.py; ứng viên: tru/cau_kho.py --khong-tai rồi vong_thu_nghiem.py --theo-hang.
4. Chỉ commit/push khi test liên quan qua VÀ số dịch/giữ tăng thật; cập nhật GHI_CHU_NANG_CAP_GROK.md.
5. Báo user lời thường 3–8 dòng: xong / chưa / kẹt / cần user làm gì.

## 7. Không làm
Chỉnh bộ đọc cho vừa đáp án; tuyên bố đã ra tiền từ mô phổng; đổi cổng duyệt khi chưa đo; đưa secret vào git; mua máy khi chưa hỏi.

Khi nhận việc: paste file này + GHI_CHU_NANG_CAP_GROK.md là đủ để nối từ bước M5.
