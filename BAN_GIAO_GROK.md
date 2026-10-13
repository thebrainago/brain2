# Quy trình bàn giao (Grok → model tiếp)

Ngày: 2026-10-11. Repo: thebrainago/brain2, nhánh main.

## 1. Đọc theo thứ tự
- GHI_CHU_NANG_CAP_GROK.md (trạng thái + số đo mới nhất)
- tai_lieu/VAN_HANH_MAY_NHA.md (máy nhà: luật, quy tắc thao tác tay, WARP, danh mục tài khoản — KHÔNG có giá trị mật khẩu; đọc mục 0 và 7 trước)
- Luật user: gói the-brain ban_giao_brain2/01 (mâu thuẫn thì 01 thắng)
- Repo thebrainago/brain2 nhánh main

## 2. Việc đang dang dở (ưu tiên)

**NEXT cho bot mới:** (A) kho cơ chế AB/AC giới hạn 2–3 mảnh, hoặc (B) SEEKER thêm MQL5+`.set`, hoặc (C) chờ user repo hộp thư máy nhà.
M5 DONE (`e1e3c9ae`). RSI_Exhaustion MÔ PHỎNG −4,1% — không giữ.
1. **M5 ĐÃ XONG** (commit `e1e3c9ae`): HistData M5 EURUSD; RSI_Exhaustion_Reversal dịch được với .set tác giả; MÔ PHỎNG đoạn kiểm sau phí −4,1% / maxDD 4,2% / 185 lệnh — **không giữ** (spread XM ăn hết biên); lịch sử ASK/spread **CHƯA ĐO ĐƯỢC**.
2. Bot MQL5 khác có .set tác giả trên M5 (nếu HANG xếp được) — hiện HANG `co_set_mql5=1` chỉ RSI_Exhaustion → các .set còn lại là MQL4.
3. Kho cơ chế tách rời (SL/TP ATR, thoát đỉnh lỗ nổi, lọc spread…) + giới hạn tổ hợp AB/AC tối đa 2–3 mảnh; không để nổ tổ hợp.
4. Chờ user: repo riêng tư hộp thư máy nhà↔cloud + Python/git máy nhà; đăng nhập Telegram nếu muốn kênh mới.

## 3. Luật vận hành (không đổi)
- Mục tiêu tiền; số phải đo được; chưa đo ghi CHƯA ĐO ĐƯỢC; mô phỏng ghi rõ mô phỏng.
- Duyệt thật: lãi sau phí + maxDD <80%. Cổng chặt brain2 chỉ gắn nhãn, chưa đổi cổng.
- Loại sớm (nhãn): nghiêng lãi <5%/năm hoặc DD ~50–65% — chưa chốt số cuối.
- Không đưa khóa/token/mật khẩu vào git. Không tự join nhóm Telegram. Không mua VPS/nâng lõi khi chưa có số đo nghẽn.
- Python mô phỏng trước → MT5 chỉ cho danh sách ngắn đã qua lọc. Giả lập lưới từng lạc quan hơn MT5 (~2 lần trên ô sạch).

## 4. Bản đồ module
- Seeker: tru/seeker.py, nhan/cau_kho_ma.py, nhan/truy_van_seeker.py, nhan/xep_hang_ung_vien.py, nhan/dieu_toc.py, nhan/tg_cong_khai.py
- Hephaestus: nhan/doc_ma.py, nhan/huong_int_mql.py, nhan/mql4_chuan.py
- QuantLab: vong_thu_nghiem.py, nhan/mo_phong.py, nhan/luoi_duong.py, mau_thu/do_moc.py
- Evo: dieu_phoi.py

## 5. Số đo gần nhất (chạy lại trước khi tin)
- Commit M5: `e1e3c9ae` — khung M5 trong `vong_thu_nghiem` + dữ liệu HistData M5 EURUSD (`/workspace/du_lieu_fx/eurusd_m5_histdata_server.csv`, ngoài repo).
- Tập chờ: dịch được **5/94** điểm vào (thêm RSI_Exhaustion_Reversal hạng A với .set tác giả).
- RSI_Exhaustion MÔ PHỎNG M5 có phí (XM): đoạn kiểm sau phí **−4,1% / maxDD 4,2% / 185 lệnh** — **không giữ**; spread XM ăn hết biên. ASK/spread lịch sử **CHƯA ĐO ĐƯỢC**.
- Bot MQL5 khác có .set tác giả: **CHƯA CÓ** trong HANG/ea_ra_co_che (chỉ 1 = RSI_Exhaustion; 3 .set còn lại là MQL4, dịch logic 0/3).
- RiskGuardLite / EMA_Cross_Demo: mô phỏng EURUSD H1 có phí — không giữ.
- Commit trước M5: f164440f (int-dir + làn MQL4); 9f86bc31; 6a9936eb.

## 6. Cách nhận việc
1. git pull trên /workspace/brain2 (hoặc clone thebrainago/brain2).
2. Python: /workspace/venv/bin/python.
3. Đo: python mau_thu/do_moc.py; ứng viên: tru/cau_kho.py --khong-tai rồi vong_thu_nghiem.py --theo-hang.
4. Chỉ commit/push khi test liên quan qua VÀ số dịch/giữ tăng thật; cập nhật GHI_CHU_NANG_CAP_GROK.md.
5. Báo user lời thường 3–8 dòng: xong / chưa / kẹt / cần user làm gì.

## 7. Không làm
Chỉnh bộ đọc cho vừa đáp án; tuyên bố đã ra tiền từ mô phỏng; đổi cổng duyệt khi chưa đo; đưa secret vào git; mua máy khi chưa hỏi.

Khi nhận việc: paste file này + GHI_CHU_NANG_CAP_GROK.md là đủ để nối từ ưu tiên mục 2 (bot .set khác / kho cơ chế / chờ máy nhà).
