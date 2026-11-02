# Tổng hợp sổ kết quả

Sinh tự động bởi `python -m nhan.so_ket_qua --tong-hop` lúc 2026-11-03 00:03 (UTC+7).
Tiêu chí ĐẠT duy nhất: **max DD < 80% VÀ CAGR > 10%/năm**. Chỉ tính kết quả đo SAU khi vá lỗi lot (31/10/2026 01:53 UTC+7).

Tổng số dòng: **1206**

| Trạng thái | Số dòng |
|---|---|
| DAT | 2 |
| KHONG_DAT | 0 |
| BI_THAY_THE | 1200 |
| CHUA_DO | 4 |

## Danh sách ĐẠT hiện tại

| Hệ | Mã | TF | CAGR % | DD % | Nguồn |
|---|---|---|---|---|---|
| skea61c (sk_ea_61c21a2049) lot x4 | CADJPY | H4 | 13.3 | 10.74 | reports/kiem_toan_he_dat.md (so cai goc so_cai_from_nha_1845.jsonl khong con tren box) |
| brainxlmrz | GBPUSD | H4 | 13.31 | 78.81 | reports/kiem_toan_he_dat.md |

## Kết quả hợp lệ sau vá (DAT/KHONG_DAT)

| Hệ | Mã | TF | CAGR % | DD % | Trạng thái |
|---|---|---|---|---|---|
| skea61c (sk_ea_61c21a2049) lot x4 | CADJPY | H4 | 13.3 | 10.74 | DAT |
| brainxlmrz | GBPUSD | H4 | 13.31 | 78.81 | DAT |

Ghi chú: BI_THAY_THE = đo trước vá lot, phải chạy lại; CHUA_DO = thiếu số/không rõ lúc chạy, hoặc chỉ là MÔ PHỎNG Python.
