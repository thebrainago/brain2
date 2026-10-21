# Bước dịch bằng LLM (máy nhà)

Lần chạy 21/10/2026 00:11, 2 giây. Giá mẫu để kiểm: gia AUDCAD H1 (3000 nen).

| Chỉ số | Giá trị |
|---|---|
| Thẻ chờ dịch lúc bắt đầu | 3765 |
| Thẻ thiếu mã trên máy (chưa dịch được) | 0 |
| Thẻ đã kiểm lần này | 0 |
| Đạt kiểm tự động → chạy tiếp toi_uu/loc | 0 |
| Không đạt kiểm (lí do trong thẻ) | 0 |
| Lỗi LLM (sẽ thử lại) | 0 |
| Mã nguồn gọi LLM mới | 197 |
| Mã nguồn lấy từ cache | 0 |
| Số lần gọi API | 8 |
| Lần gọi lỗi | 8 |
| Lần chuyển sang model dự phòng | 8 |
| Token vào | 0 |
| Token ra | 0 |
| Token suy luận (trong token ra) | 0 |
| Lần bị 429 | 0 |
| Đánh dấu BO_QUA lần này (hỏng lặp lại / lỗi không do ta) | 0 |
| Câu trả lời chạm trần max_tokens | 0 |
| CHƯA CHẠY ĐƯỢC (không có khoá) | 200 |

## Cộng dồn trong CSDL (mọi lần dịch)

Trạng thái: DAT 395, HONG 338

| Nhóm | Số thẻ HONG/BO_QUA | Ví dụ |
|---|---|---|
| KHONG_RA_SPEC_PY | 269 | LLM khong ra spec hay python dung (Chi bao ASC su dung look-ahead bias (vong lap while kiem tra Table_value2[shift+i1] o tuong lai) de xac nhan tin hieu, khong  |
| IT_LENH | 39 | chi ra 0 lenh tren gia mau (< 3) |
| PY_CAM_CU_PHAP | 10 | python: cam thuoc tinh .to_datetime |
| SPEC_KHONG_CHAY | 9 | spec khong chay duoc: "du lieu khong co cot 'upper'" |
| PY_LOI_CHAY | 7 | python: AttributeError: 'numpy.ndarray' object has no attribute 'shift' |
| NHIN_TRUOC | 4 | python: NHIN TRUOC: .roll |

Còn chờ sau lần chạy: 3765 thẻ (LLM: 2, EA bộ dịch không-LLM bỏ qua: 3763, top 28: 0).

Theo model (cộng dồn trong tiến trình): qwen3.7-max: 8 lần, 0/0 token

Vì sao hàng chờ lớn lên: hàng gồm thẻ LLM (Python/Pine) **và mọi EA MQL mà bộ dịch không-LLM bỏ qua** (`ea_bo_qua`). Mỗi lần `nhan` nhận thẻ Seeker mới, các EA này vào hàng; mỗi lượt chỉ làm tối đa `--gioi_han` thẻ. Thẻ HONG không vào lại hàng trừ khi phiên prompt mới hơn và lí do thuộc nhóm lỗi phía ta; hỏng 3 lần → BO_QUA.

Kết quả dịch là nhãn LLM, cần MT5 xác nhận; số Python là MÔ PHỎNG, PHÍ TẠM.
