# Nhật ký vận hành máy nhà

> Cách vận hành: [`may_nha/VAN_HANH_MAY_NHA.md`](../may_nha/VAN_HANH_MAY_NHA.md). Routine canh 30 phút ghi tiếp vào cuối file này. Giờ Việt Nam (UTC+7).

## Phiên 2026-11-03
- **12:40** Máy nhà online, repo đã cập nhật.
- **13:00** Lỗi: chạy sai thư mục (thợ từ chối trong `C:\Users\DUNG\brain2`), lỗi UTF-8 (cp1252), redirect stdin qua cmd → vòng lặp khởi động lại 60 s. Sửa: dùng `D:\brain2_tho`, đặt PYTHONUTF8/PYTHONIOENCODING, gọi python trực tiếp.
- **13:09** Lỗi: tài khoản không có mã `*micro` → sửa đổi sang mã `#`: commit 416ab462, f222211e, c8a38629, 9e5e7eb1.
- **13:46** Chạy song song g1, g2, p5.
- **14:00** Seeker trên máy nhà khi chưa có WARP: 0 ứng viên (319cbec2).
- **14:04** Bật WARP.
- **14:24** 13 slot, CPU 31%, RAM trống 6,5 GB. Commit 6bcdcea0 (`--tran`, tỉ lệ CPU 0,8).
  - Kết quả `lot_2600ea39abbd7b0f_H1` GBPNZD#: k=1 CAGR 38,28% DD 15,80%; k=1,5 47,59% / 17,82%; k=3 83,44% / 22,64%.
  - `lot_b0be91a35f43f34a_H4` k=2: CAGR 64,74% / DD 75,65%.
  - 1 EA Forex Factory `ff_1408891` vào hàng đợi; hàng đợi còn 60 việc.
  - Đề xuất: muốn CPU cao hơn mà RAM giới hạn → tăng agent tester mỗi slot thay vì thêm terminal.
- **14:3x** Ghi tài liệu vận hành; máy nhà offline lúc này nên chưa kiểm lại trạng thái thật.
