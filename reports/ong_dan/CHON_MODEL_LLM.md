# Chọn model LLM cho dich_llm

Lúc 2026-10-20T10:25:00 (giờ máy nhà). Sinh bởi `nhan/chon_model_llm.py`; số đo thật trên 20 EA mẫu (kiểm tự động trên giá mẫu — tín hiệu là MÔ PHỎNG).

- Model có trên ai-box: đo trên box (khoá chủ dự án cấp qua biến môi trường, không ghi ra). Lượt A/B thứ hai (10:40) hỏng: ai-box trả HTTP 403 'insufficient user quota, remaining: 0.0 đ' — không dùng số lượt đó; glm-5.3 và qwen3.7-flash chưa đo được trọn 20 mẫu
- Ứng viên (theo ưu tiên): kimi-k2.7-code, glm-5.3, qwen3.7-max, ds/deepseek-v4-pro
- **Chọn: qwen3.7-max** (dự phòng chỉ khi lỗi 5xx: kimi-k2.7-code)

| Model | ĐẠT | JSON hợp lệ | Tỉ lệ ĐẠT | Giây/mẫu | Token ra TB | Chạm trần token |
|---|---|---|---|---|---|---|
| ds/deepseek-v4-pro | 6/20 | 20 | 30.0% | 128.4 | 10219 | 0 |
| kimi-k2.7-code | 7/20 | 19 | 35.0% | 89.8 | 9726 | 0 |
| qwen3.7-max | 7/20 | 20 | 35.0% | 52.1 | 4559 | 0 |

Lý do hỏng theo nhóm (bộ kiểm của dich_llm):

- ds/deepseek-v4-pro: IT_LENH 8, KHONG_RA_SPEC_PY 3, PY_CAM_CU_PHAP 2, PY_LOI_CHAY 1
- kimi-k2.7-code: IT_LENH 6, KHONG_RA_SPEC_PY 3, SPEC_KHONG_CHAY 3, LOI_LLM 1
- qwen3.7-max: IT_LENH 9, SPEC_KHONG_CHAY 2, KHONG_RA_SPEC_PY 1, PY_CAM_CU_PHAP 1

Mẫu: 10 EA dài hơn 16.000 ký tự (trước đây bị cắt mất OnTick) và 10 EA ngắn, lấy theo thứ tự sha1 từ hàng chờ dịch trên box. Mỗi model chạy 5 lời gọi song song, max_tokens 32000, timeout 600 giây. Box không có lịch sử dịch, nên không xác định được thẻ nào đã hỏng trước đây. Sau lượt đo, đã sửa lỗi hộp cát (KeyError '__import__' khi numpy gọi import từ C). Kiểm lại đầu ra đã lưu: với qwen3.7-max, lỗi này làm hỏng oan 1 mẫu. Nhóm IT_LENH (0 lệnh trên giá mẫu) không đổi khi tăng giá mẫu lên 12.000 nến, nên nguyên nhân là tín hiệu thật sự ra 0 lệnh chứ không phải do thiếu dữ liệu.
