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
- **14:44** Canh 30p: online. CPU ~2–18%, RAM trống lúc đầu **0,58 GB** (dưới ngưỡng 6 GB) do metatester g4/g6/g7 ~5 GB/con; WARP Connected; MT5 XM còn authorized (g1/p5). Terminal 13 + thợ g1–g12/p5. Hành động: taskkill PID chính xác thợ/terminal/metatester g3,g6–g12 + orch song-song trùng; trả 8 việc dang_lam → can_test. Sau đó: CPU thấp, RAM trống **~15,7 GB**, 4 terminal (g1,g2,g4,p5) + thợ g5 (chưa có terminal), metatester 3, hàng đợi can_test **64**, da_test mới chủ yếu TRƯỢT/HONG (khong_bao_cao). Không ĐẠT mới so với 14:24. Không gọi Seeker (hàng đợi >15).
- **15:05** Canh 30p: online. CPU **30%**, RAM trống **8,26 GB**, WARP Connected, MT5 XM authorized (g1/g2/g4/g5/p5). Slot chạy: terminal 5 (g1,g2,g4,g5,p5) + thợ tương ứng + orch `--song-song --tran 10`; metatester 4. Hàng đợi can_test **62** (không gọi Seeker). Log thợ bình thường (đổi micro→#), không HONG lặp. Việc xong gần đây: `cb_70796` TRƯỢT DD~100%; **ĐẠT mới** `lot_skea154c9fdee7_H4` (GBPCAD# H4, BRAIN_XuLiLenh) k=1 CAGR **41,37%**/năm DD **48,38%** (so_cai 14:44, lần canh trước chưa ghi). Không restart/taskkill; RAM đủ ngưỡng ≥6 GB.
- **15:07–15:35** Giảm RAM / tăng luồng: thêm chặn RAM trong thợ (commit 5cb956d2, 8a31c349, d8e1d3bf): trước mỗi lần phóng tester chờ RAM trống > `BRAIN_RAM_TRONG_MIN_GB` (máy nhà 11) và giãn cách 180 s giữa các lần phóng; MaxBars=50000; dọn Tester/cache cũ. Dừng đúng PID thợ/terminal/metatester (g1,g2,g4,g5,p5 + orch 6908), khởi động orch 13 slot (PID 7088) → bản đầu chỉ chặn lúc nhận việc nên g3 nhận thêm khi 5 việc dở chưa nạp tick → RAM trống tụt **0,74 GB**, CPU 31,6%. Sửa thành chặn trước mỗi lần phóng (d8e1d3bf); dừng đúng PID orch 7088, thợ g3,g6–g12, terminal 6812/metatester 17284 g3 (việc g3 nằm ở dang_lam_g3, sẽ chạy lại). Thợ g1,g2,g4,g5,p5 vẫn chạy code 8a31c349 (để việc dở chạy xong); orch mới PID 12576 cho g3,g6–g12 (chờ RAM). **15:30: 5 metatester, RAM trống 5,1–8,3 GB, CPU ~24%.** Kết luận: real ticks ~5 GB/test → trần ~5 test trên 32 GB, CPU 70–80% không đạt được nếu giữ RAM ≥ 6 GB.
