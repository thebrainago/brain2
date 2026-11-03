# Sổ quyết định (chỉ thêm, không xóa)

| Ngày (UTC+7) | Quyết định | Nguồn |
|---|---|---|
| 16/10/2026 | Thả lỏng luật học thuật: chỉ cần lợi nhuận; p-value/Holm/FDR/placebo chỉ là nhãn | `CHI_THI_CHU_DU_AN.md` |
| 17/10/2026 | Mục đích: tìm mảnh và KẾT HỢP thành hệ ghép (DCA, gồng, gỡ lệnh, hedge), đo ở cấp tài khoản | commit Claude 17/10 |
| 21/10/2026 | Tắt dịch LLM trả phí (qwen/ai-box) | `tai_lieu/BAN_GIAO_CLAUDE_21_10.md` |
| 01/11/2026 | Replay statement/CSV chưa giải mã điểm vào hoặc chỉ in-sample → không tính đạt | `reports/kiem_toan_he_dat.md` |
| 01/11/2026 | Cặp có USD ưu tiên thấp; ưu tiên cặp chéo biên độ hẹp (AUDCAD, AUDNZD, CADJPY…) | `docs/ban-giao/EVOLUTION_ban_giao.md` |
| 02/11/2026 | **Tiêu chí ĐẠT duy nhất: max DD < 80% VÀ CAGR > 10%/năm.** Không tiêu chí nào khác (thay ngưỡng ≥10%/năm cũ) | Anh, 02/11 |
| 02/11/2026 | Grok Bot làm toàn bộ công việc (bot kia hết token) | Anh, 02/11 |
| 02/11/2026 | Lập `TRI_NHO/` làm bộ nhớ chung giữa các phiên + sổ kết quả chung cho mọi test | Anh, 02/11 |
| 02/11/2026 | Ưu tiên quay lại Seeker (rộng, sâu, đa ngôn ngữ, mạng xã hội, dịch ngược lịch sử trade); QuantLab tăng tốc + số test | Anh, 02/11 |

- 2026-11-03 00:03 (UTC+7): Anh hạ ngưỡng lãi xuống > 10%/năm (vì có thể tăng lot), DD < 80% giữ nguyên. Không thêm tiêu chí khác.
- 2026-11-03 08:40 (UTC+7): **CAGR thấp được nâng lot, miễn DD<80%** (Anh: “Cagr có thể không cao thì nâng lot, miễn sao dd không bị quá là được”). Hệ đạt nếu tồn tại k lot cho CAGR>10% & DD<80%; đo bằng `nhan/nang_lot.py`.
