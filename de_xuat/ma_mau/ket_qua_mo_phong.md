# Kết quả đo đặc tính vận hành (DỮ LIỆU TỔNG HỢP — không phải giá thật)

Sinh bởi: `python de_xuat/ma_mau/mo_phong_dac_tinh.py` (16/10/2026, ~11 giây, seed cố định trong file).
Giả định (đổi được ở đầu file): sd mỗi lệnh 100 bps · lợi nhuận trung bình từng ô ~ chuẩn (CLT) · GĐ1 và GĐ2 độc lập,
cạnh KHÔNG phân rã giữa hai giai đoạn (lạc quan) · 2.000 ô nhiễu + 10 ô cạnh thật · k = 20 ô chuyển sang GĐ2.
Hạn chế: `rho`/`sd` là GIẢ ĐỊNH, chưa đo trên lệnh thật của v31/v32 — xem `03_KE_HOACH_THU.md` việc T1.

### A. Duong tinh gia khi lenh cung cum (n=150, 30 tuan x 5 lenh, KHONG co canh nao)

| ICC (rho) | deff do duoc | t-test tung lenh @0,05 | gom cum @0,05 | t-test tung lenh @0,0025 | gom cum @0,0025 |
|---|---|---|---|---|---|
| 0.0 | 1.01 | 0.049 | 0.049 | 0.0024 | 0.0027 |
| 0.1 | 1.43 | 0.084 | 0.052 | 0.0095 | 0.0027 |
| 0.3 | 2.21 | 0.131 | 0.049 | 0.0287 | 0.0026 |

### B. Duong ong sang GD1 -> kiem top-20 tren GD2 (2.000 o nhieu + 10 o canh that, 2.000 lan lap)

`that_chuyen` = so o that (trong 10) lot vao top-20 cua GD1. Moi cot cach hieu chinh: so o THAT / so o GIA duoc nhan trung binh moi lan, va xac suat bat duoc IT NHAT 1 o that.

| n/o | canh (bps) | t ky vong | that_chuyen | khong hieu chinh (that/gia · >=1) | Holm ho 20.503 | Holm k=20 | BH 10% |
|---|---|---|---|---|---|---|---|
| 150 | 5 | 0.61 | 0.45 | 0.063/0.942 · 0.062 | 0.0/0.0 · 0.0 | 0.004/0.048 · 0.004 | 0.01/0.116 · 0.009 |
| 150 | 10 | 1.22 | 1.29 | 0.434/0.934 · 0.364 | 0.0/0.0 · 0.001 | 0.074/0.038 · 0.071 | 0.123/0.113 · 0.108 |
| 150 | 20 | 2.45 | 5.08 | 4.024/0.744 · 0.993 | 0.09/0.0 · 0.087 | 1.866/0.046 · 0.872 | 3.324/0.355 · 0.941 |
| 150 | 40 | 4.9 | 9.9 | 9.893/0.514 · 1.0 | 6.221/0.0 · 1.0 | 9.791/0.047 · 1.0 | 9.893/0.588 · 1.0 |
| 1500 | 5 | 1.94 | 3.17 | 1.936/0.879 · 0.891 | 0.011/0.0 · 0.011 | 0.614/0.043 · 0.474 | 1.115/0.233 · 0.61 |
| 1500 | 10 | 3.87 | 9.07 | 8.946/0.562 · 1.0 | 2.21/0.0 · 0.921 | 8.036/0.042 · 1.0 | 8.941/0.576 · 1.0 |
| 1500 | 20 | 7.75 | 10.0 | 10.0/0.485 · 1.0 | 9.992/0.0 · 1.0 | 10.0/0.046 · 1.0 | 10.0/0.568 · 1.0 |
| 1500 | 40 | 15.49 | 10.0 | 10.0/0.503 · 1.0 | 10.0/0.0 · 1.0 | 10.0/0.054 · 1.0 | 10.0/0.584 · 1.0 |
