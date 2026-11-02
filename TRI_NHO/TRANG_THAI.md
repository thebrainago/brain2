# Trạng thái hiện tại — cập nhật 03/11/2026 01:00 (UTC+7)

## Tóm tắt
- **Chưa có hệ nào ĐẠT** theo tiêu chí DD < 80% & CAGR > 10%/năm với kết quả hợp lệ (xem `so_ket_qua/TONG_HOP.md`).
- Grok Bot làm toàn bộ việc từ 02/11 (bot kia hết token).
- Máy nhà: tắt/park từ tối 31/10; routine giám sát 30′ tạm dừng.

## Làn lịch sử công khai (03/11/2026, `seeker/cong_khai/`)
- Quét mở rộng 03/11 05:41–06:2x (UTC+7, nền nohup, log `data/cong_khai/run.log`, cache 72h): 9 cách sắp × mt5/mt4 → **1600 id MQL5** (32 ứng viên cũ + 824 mới từ mt5, 744 từ mt4), **1562 đọc được**, 38 không đọc. Kết quả: **1065 ĐẠT / 1561 đo được = 68,2%** (496 KHÔNG ĐẠT, 1 chưa đo) theo chỉ DD<80% & CAGR>10%. 483 tín hiệu ĐẠT có tuổi ≥ 12 tháng (726/1562 tín hiệu ≥ 12 tháng). Sổ kết quả `nguon=CONG_KHAI` nay 1065 dòng (+773). Báo cáo: `reports/NGUON_CONG_KHAI_DAT.md`.
- Lần quét trước (00:2x–00:53): 292 đọc → 292 ĐẠT (chỉ danh sách mặc định, thiên lệch sống sót mạnh hơn).
- Lưu ý: danh sách mặc định MQL5 chỉ hiện tín hiệu xếp hạng cao → thiên lệch sống sót. Đây là ĐẠT theo **lịch sử công khai của người khác**, chưa phải hệ của mình đã chạy MT5 trên dữ liệu dài.
- Bị chặn: Myfxbook (Cloudflare 403, cả robots.txt), Exness Social Trading và my.litefinance.vn (lỗi TLS từ box), LiteFinance trang chi tiết trader chuyển hướng về danh sách (danh sách chỉ có lợi nhuận + rủi ro 1–10 → 16 trader CHƯA ĐO ĐƯỢC).
- Dịch ngược: CSV lịch sử MQL5 cần đăng nhập → 0 tín hiệu đưa vào được; đặt CSV tải tay ở `data/cong_khai/csv/<id>.csv` rồi chạy lại.

## Lỗi lot CSV ~100× — đã vá 31/10/2026 01:53 (UTC+7)
- Khi EA chạy `VAO_CSV`, lot trong CSV bị phình ~100× → lãi/DD sai hoàn toàn.
- Hệ quả: **78 hệ “ĐẠT” trong `reports/CHIEN_LUOC_DA_LOC.md` BỊ THAY THẾ**, chờ chạy lại. Mọi kết quả trước mốc này trong sổ có trạng thái `BI_THAY_THE`.
- Bản vá và sổ cái sau vá (`so_cai_from_nha_1845.jsonl`, `status_overnight_0217.txt`) nằm ở máy nhà/box cũ; **không còn trên box hiện tại** và chưa có trong git. Số sau vá chỉ còn dạng chép lại trong `reports/kiem_toan_he_dat.md`.

## Kiểm toán 01/11 (`reports/kiem_toan_he_dat.md`)
5 hệ từng báo ĐẠT → **0/5 còn đạt**: brainxlmrz GBPUSD H4 (CAGR 13,3%, DD 78,81%, 25% tick), skea61c CADJPY H4 ×4 (13,3%, DD 10,74%, IS), sk_ea_3279057100 EURGBP H1 (12,2%, chưa giải mã điểm vào), mql5344 NZDUSD H1 (CAGR thật 3,5%), ghep_0bf2 GBPCAD H4 (10,3%, IS). Thứ tự chạy lại đề xuất: skea61c → brainxlmrz → ghep_0bf2 → 3279 → mql5344.

## Khác
- Hệ tín hiệu công khai: `reports/HE_TIN_HIEU_CONG_KHAI.md` — 10 nền tảng, 32 ứng viên MQL5 (26–27/10).
- Dữ liệu dài: MT5 XM xong 19 cặp từ 2004; histdata dừng 09/2026; Dukascopy CHƯA chạy; `du_lieu_dai.json` CHƯA có.
- 13 thẻ dịch tay (đợt 3–5, 21/10) mới qua lọc Python — MÔ PHỎNG, chưa đo MT5.
- Dịch LLM (qwen/ai-box) TẮT.

## Vấn đề đã biết
- CSV tín hiệu chỉ phủ 2024–2026 → kết quả trên CSV đó là **in-sample**; cần tái sinh tín hiệu trên toàn lịch sử.
- Bộ test đầy đủ (`pytest`) treo ở ~60% và có ~30 lỗi; chạy theo file với `--timeout`. Lỗi cũ: test_dich_llm (403), test_an_toan_tester ×2, test_ghi_an_toan ×3, test_sinh_viec.
- Repo phình: `reports/phan_viec/viec_mt5` và `reports/KHO_*.json` (đề xuất chuyển ra ngoài git — chờ Anh duyệt).
- Vài file config/report (`config/ma_nguon_con_tro.json`, `config/ngan_sach_nhip.json`, `nhat_ky/kho_co_che_ghi.log`, `reports/EVO_SUC_KHOE.md`, `reports/VONG_DAY_DU.json`) đang thay đổi trên box do tiến trình khác — không commit ở phiên 03/11.
