# Bước dịch bằng LLM (máy nhà)

Lần chạy 20/10/2026 21:00, 80 giây. Giá mẫu để kiểm: gia AUDCAD H1 (3000 nen).

| Chỉ số | Giá trị |
|---|---|
| Thẻ chờ dịch lúc bắt đầu | 16 |
| Thẻ thiếu mã trên máy (chưa dịch được) | 0 |
| Thẻ đã kiểm lần này | 8 |
| Đạt kiểm tự động → chạy tiếp toi_uu/loc | 3 |
| Không đạt kiểm (lí do trong thẻ) | 5 |
| Lỗi LLM (sẽ thử lại) | 8 |
| Mã nguồn gọi LLM mới | 16 |
| Mã nguồn lấy từ cache | 0 |
| Số lần gọi API | 16 |
| Lần gọi lỗi | 8 |
| Lần chuyển sang model dự phòng | 8 |
| Token vào | 29119 |
| Token ra | 20899 |
| Token suy luận (trong token ra) | 17836 |
| Lần bị 429 | 0 |
| Đánh dấu BO_QUA lần này (hỏng lặp lại / lỗi không do ta) | 0 |
| Câu trả lời chạm trần max_tokens | 0 |
| CHƯA CHẠY ĐƯỢC (không có khoá) | 0 |

## Lí do hỏng lần này (theo nhóm)

| Nhóm | Số thẻ | Nghĩa |
|---|---|---|
| LOI_LLM | 8 | LLM lỗi / không trả JSON (thử lại tối đa 3 lần rồi BO_QUA) |
| KHONG_RA_SPEC_PY | 5 | LLM không ra spec hay python dùng được |

## Cộng dồn trong CSDL (mọi lần dịch)

Trạng thái: DAT 144, HONG 147

| Nhóm | Số thẻ HONG/BO_QUA | Ví dụ |
|---|---|---|
| KHONG_RA_SPEC_PY | 120 | LLM khong ra spec hay python dung (Chi bao ASC su dung look-ahead bias (vong lap while kiem tra Table_value2[shift+i1] o tuong lai) de xac nhan tin hieu, khong  |
| IT_LENH | 16 | chi ra 0 lenh tren gia mau (< 3) |
| SPEC_KHONG_CHAY | 4 | spec khong chay duoc: "du lieu khong co cot 'upper'" |
| PY_LOI_CHAY | 3 | python: AttributeError: 'numpy.ndarray' object has no attribute 'shift' |
| NHIN_TRUOC | 2 | python: NHIN TRUOC: .roll |
| PY_CAM_CU_PHAP | 2 | python: cam thuoc tinh .to_datetime |

Còn chờ sau lần chạy: 16 thẻ (LLM: 0, EA bộ dịch không-LLM bỏ qua: 16, top 28: 0).

Theo model (cộng dồn trong tiến trình): qwen3.7-max: 103 lần, 342667/314470 token

Vì sao hàng chờ lớn lên: hàng gồm thẻ LLM (Python/Pine) **và mọi EA MQL mà bộ dịch không-LLM bỏ qua** (`ea_bo_qua`). Mỗi lần `nhan` nhận thẻ Seeker mới, các EA này vào hàng; mỗi lượt chỉ làm tối đa `--gioi_han` thẻ. Thẻ HONG không vào lại hàng trừ khi phiên prompt mới hơn và lí do thuộc nhóm lỗi phía ta; hỏng 3 lần → BO_QUA.

Kết quả dịch là nhãn LLM, cần MT5 xác nhận; số Python là MÔ PHỎNG, PHÍ TẠM.
