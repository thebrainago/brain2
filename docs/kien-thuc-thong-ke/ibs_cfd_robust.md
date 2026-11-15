# Độ bền IBS long trên CFD chỉ số (US100, US500)

Cập nhật: 2026-11-15 07:55 (Asia/Saigon, UTC+7)

Kiểm tra độ bền của quy tắc long IBS đã đạt ngưỡng OOS đơn lẻ trong [ibs_cfd_chi_so.md](ibs_cfd_chi_so.md): walk-forward 5 năm/1 năm, lưới tham số, trễ khớp lệnh, chế độ VIX/SMA200/thời kỳ, và hiệu chỉnh kiểm định bội (BH-FDR, deflated Sharpe). Cùng phí CFD (US500 0,6 điểm, US100 1,5 điểm, long 7,5%/năm, thứ Sáu–thứ Hai = 3 đêm). Dữ liệu Yahoo đến 2026-11-13; VIX từ 1990-01-02.

**Kết luận sau kiểm độ bền: vẫn là ứng viên, không nâng lên “passed”.** Họ quy tắc long IBS trên US100 (và một phần US500) tạo thành **cao nguyên** trên OOS 2015–2026, không phải một đỉnh nhọn. Walk-forward từ 1995 cũng có tỷ lệ năm lãi khá, nhất là quy tắc thoát IBS>0,8 / tối đa 4 nến. Tuy nhiên deflated Sharpe sau hàng trăm phép thử chỉ khoảng 0,15–0,28 với các quy tắc đã công bố trước; IS trước 2010 lỗ nặng; và quy tắc giữ 1 nến có thể đổi dấu nếu vào lệnh trễ thêm một nến. Chưa đủ để đưa vào bộ hỗ trợ như tín hiệu đã chốt.

## 1. Walk-forward: train 5 năm, test 1 năm

Cửa sổ lăn từ 1990 (hoặc khi đủ dữ liệu: ^NDX/^GSPC test 1995–2026, QQQ 2004–2026). Mỗi năm test hoặc giữ nguyên hai quy tắc đã chọn trước, hoặc chọn ô lưới có Sharpe train tốt nhất rồi chạy năm sau.

| Chuỗi | Quy tắc | Số năm | Năm lãi | Lãi TB %/năm | Trước 2015 (năm lãi / TB) | Từ 2015 (năm lãi / TB) |
|---|---|---:|---:|---:|---|---|
| US100 (^NDX) | WF chọn lưới trên 5 năm | 32 | 68,8% | 7,83 | 60,0% / 6,17% | 83,3% / 10,58% |
| US100 (^NDX) | Cố định IBS 0,2 giữ 1 nến | 32 | 62,5% | 2,68 | 50,0% / 0,55% | 83,3% / 6,24% |
| US100 (^NDX) | Cố định IBS 0,2 thoát 0,8 / tối đa 4 | 32 | 75,0% | 9,35 | 70,0% / 9,63% | 83,3% / 8,87% |
| US100 (QQQ) | WF chọn lưới trên 5 năm | 23 | 56,5% | 3,98 | 45,5% / 1,10% | 66,7% / 6,62% |
| US100 (QQQ) | Cố định IBS 0,2 giữ 1 nến | 23 | 56,5% | 3,02 | 27,3% / -0,79% | 83,3% / 6,50% |
| US100 (QQQ) | Cố định IBS 0,2 thoát 0,8 / tối đa 4 | 23 | 65,2% | 6,14 | 54,5% / 1,07% | 75,0% / 10,79% |
| US500 (^GSPC) | WF chọn lưới trên 5 năm | 32 | 65,6% | 3,51 | 50,0% / 2,16% | 91,7% / 5,76% |
| US500 (^GSPC) | Cố định IBS 0,2 giữ 1 nến | 32 | 62,5% | 2,46 | 55,0% / 2,34% | 75,0% / 2,66% |
| US500 (^GSPC) | Cố định IBS 0,2 thoát 0,8 / tối đa 4 | 32 | 65,6% | 4,14 | 60,0% / 3,16% | 75,0% / 5,77% |

- Quy tắc cố định thoát IBS>0,8 / tối đa 4 nến ổn hơn chọn lại tham số mỗi năm (trên ^NDX: lãi TB 9,35%/năm so với 7,83% khi tối ưu lăn). Không có dấu hiệu “chỉ đỉnh lưới mới chạy được”.
- Từ 2015, cả ba chuỗi có 75–83% năm dương với quy tắc cố định (1 nến hoặc thoát 0,8).
- Trước 2015 lẫn lộn: QQQ giữ 1 nến chỉ dương 27% số năm; ^NDX thoát 0,8 vẫn dương 70% số năm trong 1995–2014 (IS lỗ của ^NDX chủ yếu nằm ở 1985–1994 và các lệnh pre-2010, không hoàn toàn trùng cửa sổ WF).
- Năm khó: 2001 (S&P giữ 1 nến −21%, thoát 0,8 −18%); 2022 làm quy tắc thoát 4 nến lỗ trên US100 (^NDX −15,5%, QQQ −10,6%) trong khi giữ 1 nến vẫn dương. Năm 2020 đóng góp lớn (QQQ thoát 0,8 +60%).

## 2. Lưới tham số — cao nguyên, không phải đỉnh nhọn

Long, không lọc SMA200, OOS 2015–2026, Sharpe đã trừ phí. Hàng là ngưỡng vào IBS, cột là cách thoát.

**US100 (^NDX), Sharpe OOS**

| IBS vào | 1bar | ex07_max2 | ex07_max4 | ex07_max6 | ex08_max2 | ex08_max4 | ex08_max6 | ex09_max2 | ex09_max4 | ex09_max6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,10 | 0,62 | 0,93 | 0,86 | 0,94 | 0,89 | 0,87 | 0,94 | 0,98 | 0,85 | 0,98 |
| 0,15 | 0,72 | 0,84 | 0,82 | 0,88 | 0,71 | 0,74 | 0,82 | 0,76 | 0,75 | 0,83 |
| 0,20 | 0,60 | 0,73 | 0,73 | 0,80 | 0,69 | 0,61 | 0,70 | 0,70 | 0,63 | 0,74 |
| 0,25 | 0,71 | 0,71 | 0,52 | 0,68 | 0,65 | 0,47 | 0,57 | 0,68 | 0,51 | 0,65 |
| 0,30 | 0,55 | 0,63 | 0,53 | 0,63 | 0,51 | 0,47 | 0,49 | 0,61 | 0,43 | 0,53 |

**US100 (QQQ), Sharpe OOS**

| IBS vào | 1bar | ex07_max2 | ex07_max4 | ex07_max6 | ex08_max2 | ex08_max4 | ex08_max6 | ex09_max2 | ex09_max4 | ex09_max6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,10 | 0,54 | 0,81 | 0,72 | 0,82 | 0,79 | 0,72 | 0,78 | 0,89 | 0,88 | 0,83 |
| 0,15 | 0,54 | 0,78 | 0,78 | 0,91 | 0,74 | 0,77 | 0,85 | 0,81 | 0,93 | 0,90 |
| 0,20 | 0,63 | 0,67 | 0,74 | 0,88 | 0,58 | 0,71 | 0,75 | 0,60 | 0,88 | 0,74 |
| 0,25 | 0,59 | 0,71 | 0,47 | 0,71 | 0,62 | 0,39 | 0,61 | 0,69 | 0,59 | 0,71 |
| 0,30 | 0,58 | 0,63 | 0,58 | 0,73 | 0,49 | 0,49 | 0,59 | 0,57 | 0,61 | 0,68 |

**US500 (^GSPC), Sharpe OOS**

| IBS vào | 1bar | ex07_max2 | ex07_max4 | ex07_max6 | ex08_max2 | ex08_max4 | ex08_max6 | ex09_max2 | ex09_max4 | ex09_max6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,10 | 0,52 | 0,80 | 0,67 | 0,71 | 0,79 | 0,66 | 0,77 | 0,81 | 0,69 | 0,84 |
| 0,15 | 0,44 | 0,73 | 0,77 | 0,71 | 0,71 | 0,66 | 0,72 | 0,65 | 0,76 | 0,86 |
| 0,20 | 0,40 | 0,59 | 0,67 | 0,68 | 0,56 | 0,59 | 0,68 | 0,51 | 0,63 | 0,84 |
| 0,25 | 0,31 | 0,68 | 0,53 | 0,59 | 0,67 | 0,38 | 0,55 | 0,58 | 0,39 | 0,64 |
| 0,30 | 0,27 | 0,44 | 0,41 | 0,47 | 0,38 | 0,21 | 0,39 | 0,29 | 0,19 | 0,48 |

Trên US100, **cả 50/50 ô** có Sharpe ≥ 0,39 và PF ≥ 1,20. US500: 43/50 ô (lỏng hơn khi IBS vào 0,25–0,30 và giữ 1 nến). Ô tốt hơn thường là IBS vào 0,10–0,20 và giữ hơi lâu (max 6) hoặc thoát 0,7–0,9. Quy tắc đã chọn trước (IBS 0,20, giữ 1 nến hoặc thoát 0,8 / tối đa 4) nằm **trong cao nguyên**, không phải một ô cô lập. Không được lấy ô đẹp nhất sau khi nhìn lưới (ví dụ ^NDX IBS 0,10 thoát 0,9 / tối đa 2, Sharpe 0,98) làm quy tắc mới.

## 3. Trễ khớp lệnh (OOS 2015+)

| Chuỗi | Biến thể | Khớp | Lệnh | Lãi TB % | PF | Sharpe | %/năm |
|---|---|---|---:|---:|---:|---:|---:|
| US500 (^GSPC) | Long IBS<0,2, giữ 1 nến | mở cửa nến sau (chuẩn) | 477 | 0,069 | 1,20 | 0,40 | 2,57 |
| US500 (^GSPC) | Long IBS<0,2, giữ 1 nến | trễ 1 nến (mở t+2) | 411 | -0,022 | 0,95 | -0,11 | -0,99 |
| US500 (^GSPC) | Long IBS<0,2, giữ 1 nến | cùng đóng cửa (tham chiếu) | 576 | 0,093 | 1,23 | 0,49 | 4,19 |
| US500 (^GSPC) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | mở cửa nến sau (chuẩn) | 390 | 0,172 | 1,37 | 0,59 | 5,43 |
| US500 (^GSPC) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | trễ 1 nến (mở t+2) | 345 | 0,121 | 1,23 | 0,36 | 3,12 |
| US500 (^GSPC) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | cùng đóng cửa (tham chiếu) | 402 | 0,229 | 1,48 | 0,67 | 7,39 |
| US100 (^NDX) | Long IBS<0,2, giữ 1 nến | mở cửa nến sau (chuẩn) | 484 | 0,155 | 1,31 | 0,60 | 5,95 |
| US100 (^NDX) | Long IBS<0,2, giữ 1 nến | trễ 1 nến (mở t+2) | 419 | 0,067 | 1,12 | 0,24 | 1,90 |
| US100 (^NDX) | Long IBS<0,2, giữ 1 nến | cùng đóng cửa (tham chiếu) | 571 | 0,222 | 1,48 | 0,92 | 10,52 |
| US100 (^NDX) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | mở cửa nến sau (chuẩn) | 395 | 0,254 | 1,41 | 0,61 | 8,13 |
| US100 (^NDX) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | trễ 1 nến (mở t+2) | 350 | 0,351 | 1,59 | 0,78 | 10,15 |
| US100 (^NDX) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | cùng đóng cửa (tham chiếu) | 410 | 0,404 | 1,72 | 0,96 | 13,86 |
| US100 (QQQ) | Long IBS<0,2, giữ 1 nến | mở cửa nến sau (chuẩn) | 449 | 0,173 | 1,35 | 0,63 | 6,20 |
| US100 (QQQ) | Long IBS<0,2, giữ 1 nến | trễ 1 nến (mở t+2) | 388 | 0,024 | 1,04 | 0,08 | 0,32 |
| US100 (QQQ) | Long IBS<0,2, giữ 1 nến | cùng đóng cửa (tham chiếu) | 526 | 0,216 | 1,45 | 0,84 | 9,36 |
| US100 (QQQ) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | mở cửa nến sau (chuẩn) | 371 | 0,317 | 1,51 | 0,71 | 9,68 |
| US100 (QQQ) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | trễ 1 nến (mở t+2) | 333 | 0,340 | 1,56 | 0,72 | 9,24 |
| US100 (QQQ) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | cùng đóng cửa (tham chiếu) | 381 | 0,413 | 1,73 | 0,92 | 13,12 |

Đúng kỳ vọng, khớp cùng đóng cửa (tham chiếu, lạc quan) luôn cao hơn. Trễ thêm một nến: quy tắc **giữ 1 nến bị yếu đi mạnh, và đổi dấu trên ^GSPC** (Sharpe +0,40 → −0,11); QQQ gần về 0. Quy tắc thoát IBS>0,8 / tối đa 4 nến vẫn dương (thậm chí tốt hơn trên ^NDX). Đây là lý do ưu tiên phương án thoát 4 nến nếu đưa vào bộ hỗ trợ.

## 4. Chế độ: vì sao IS trước 2015 lỗ

| Chuỗi | Biến thể | Chế độ | Lệnh | Win% | Lãi TB % | PF |
|---|---|---|---:|---:|---:|---:|
| US100 NDX | giữ 1 nến | trước 2010 | 1147 | 40,98 | -0,279 | 0,68 |
| US100 NDX | giữ 1 nến | 2010–2014 | 183 | 51,91 | -0,020 | 0,96 |
| US100 NDX | giữ 1 nến | từ 2015 | 484 | 58,68 | 0,155 | 1,31 |
| US100 NDX | giữ 1 nến | VIX < 20 | 872 | 45,07 | -0,248 | 0,58 |
| US100 NDX | giữ 1 nến | VIX ≥ 20 | 802 | 54,24 | 0,164 | 1,21 |
| US100 NDX | giữ 1 nến | trên SMA200 | 1257 | 46,62 | -0,161 | 0,75 |
| US100 NDX | giữ 1 nến | dưới SMA200 | 557 | 47,22 | -0,082 | 0,91 |
| US100 NDX | thoát 0,8 / 4 nến | trước 2010 | 893 | 53,42 | -0,137 | 0,87 |
| US100 NDX | thoát 0,8 / 4 nến | 2010–2014 | 151 | 67,55 | 0,150 | 1,23 |
| US100 NDX | thoát 0,8 / 4 nến | từ 2015 | 395 | 62,53 | 0,254 | 1,41 |
| US100 NDX | thoát 0,8 / 4 nến | VIX < 20 | 714 | 55,18 | -0,122 | 0,83 |
| US100 NDX | thoát 0,8 / 4 nến | VIX ≥ 20 | 617 | 65,80 | 0,414 | 1,41 |
| US100 NDX | thoát 0,8 / 4 nến | trên SMA200 | 1030 | 57,28 | -0,050 | 0,94 |
| US100 NDX | thoát 0,8 / 4 nến | dưới SMA200 | 409 | 57,70 | 0,127 | 1,11 |
| US100 QQQ | giữ 1 nến | trước 2010 | 476 | 51,05 | 0,140 | 1,17 |
| US100 QQQ | giữ 1 nến | 2010–2014 | 178 | 51,12 | -0,060 | 0,88 |
| US100 QQQ | giữ 1 nến | từ 2015 | 449 | 57,02 | 0,173 | 1,35 |
| US100 QQQ | giữ 1 nến | VIX < 20 | 540 | 51,67 | -0,054 | 0,88 |
| US100 QQQ | giữ 1 nến | VIX ≥ 20 | 563 | 55,24 | 0,290 | 1,35 |
| US100 QQQ | giữ 1 nến | trên SMA200 | 708 | 53,39 | 0,044 | 1,09 |
| US100 QQQ | giữ 1 nến | dưới SMA200 | 395 | 53,67 | 0,259 | 1,28 |
| US100 QQQ | thoát 0,8 / 4 nến | trước 2010 | 363 | 57,02 | 0,122 | 1,10 |
| US100 QQQ | thoát 0,8 / 4 nến | 2010–2014 | 142 | 65,49 | 0,041 | 1,06 |
| US100 QQQ | thoát 0,8 / 4 nến | từ 2015 | 371 | 63,34 | 0,317 | 1,51 |
| US100 QQQ | thoát 0,8 / 4 nến | VIX < 20 | 449 | 59,69 | 0,071 | 1,12 |
| US100 QQQ | thoát 0,8 / 4 nến | VIX ≥ 20 | 427 | 62,53 | 0,319 | 1,26 |
| US100 QQQ | thoát 0,8 / 4 nến | trên SMA200 | 584 | 61,30 | 0,128 | 1,19 |
| US100 QQQ | thoát 0,8 / 4 nến | dưới SMA200 | 292 | 60,62 | 0,319 | 1,25 |
| US500 | giữ 1 nến | trước 2010 | 1466 | 41,88 | -0,225 | 0,59 |
| US500 | giữ 1 nến | 2010–2014 | 182 | 56,59 | 0,120 | 1,31 |
| US500 | giữ 1 nến | từ 2015 | 477 | 57,02 | 0,069 | 1,20 |
| US500 | giữ 1 nến | VIX < 20 | 815 | 51,41 | -0,058 | 0,81 |
| US500 | giữ 1 nến | VIX ≥ 20 | 782 | 55,63 | 0,114 | 1,23 |
| US500 | giữ 1 nến | trên SMA200 | 1414 | 47,38 | -0,119 | 0,70 |
| US500 | giữ 1 nến | dưới SMA200 | 711 | 44,87 | -0,150 | 0,78 |
| US500 | thoát 0,8 / 4 nến | trước 2010 | 1178 | 53,82 | -0,192 | 0,74 |
| US500 | thoát 0,8 / 4 nến | 2010–2014 | 145 | 62,76 | 0,129 | 1,24 |
| US500 | thoát 0,8 / 4 nến | từ 2015 | 390 | 63,33 | 0,172 | 1,37 |
| US500 | thoát 0,8 / 4 nến | VIX < 20 | 677 | 58,79 | -0,020 | 0,95 |
| US500 | thoát 0,8 / 4 nến | VIX ≥ 20 | 606 | 63,70 | 0,199 | 1,28 |
| US500 | thoát 0,8 / 4 nến | trên SMA200 | 1174 | 56,98 | -0,090 | 0,83 |
| US500 | thoát 0,8 / 4 nến | dưới SMA200 | 539 | 56,22 | -0,063 | 0,93 |

- Lỗ IS tập trung **trước 2010**. Từ 2010–2014, ^GSPC đã dương; ^NDX thoát 0,8 cũng dương (PF 1,23), nhưng giữ 1 nến trên ^NDX/QQQ vẫn yếu. Edge hiện rõ từ khoảng 2010–2015, không có suốt lịch sử.
- **VIX ≥ 20** (theo đóng cửa ngày tín hiệu, mẫu đầy đủ): lãi TB và PF tốt hơn hẳn. VIX < 20 thường PF < 1 trên ^GSPC/^NDX. IBS kiểu mean-reversion hợp hơn khi biến động cao. Chưa biến điều này thành bộ lọc cứng (sẽ là thêm một lần chọn tham số).
- Lọc SMA200: không ổn định. Trên mẫu đầy đủ, cả trên và dưới SMA200 đều có thể lỗ vì giai đoạn pre-2010; trên QQQ thì dưới SMA200 còn tốt hơn một chút. Không bắt buộc lọc xu hướng cho ứng viên này.

## 5. Kiểm định bội

Đã thử (ước lượng thành thật, không đếm trùng phí):

- `ibs_cap_cheo.py`: 63 phép (4 cặp D1 + 3 H4, 9 biến thể) — không cái nào passed.
- `ibs_cfd_chi_so.py`: 24 phép chính (4 chuỗi × 6 biến thể, spread 1× + phí đêm); 6 dòng long từng vượt ngưỡng OOS đơn lẻ. (72 nếu đếm thêm 2 kịch bản phí).
- Lượt này: 150 ô lưới (3 chuỗi × 5 ngưỡng × 10 kiểu thoát), cộng chẩn đoán trễ lệnh và chế độ (không dùng để chọn quy tắc mới).

Tổng khoảng **237** phép thử họ IBS. BH-FDR trên 150 ô OOS 2015+: 68 ô qua q=0,05 (13/50 ^NDX, 22/50 QQQ, 34/50 ^GSPC). Con số này **không** nghĩa là có 68 edge độc lập — p-value phụ thuộc nhau vì các ô gần như cùng một họ trên cùng một giai đoạn thuận.

Deflated Sharpe (Bailey & López de Prado 2014; Sharpe đã niên hóa, T ≈ 11,87 năm OOS; công thức trong script lần đầu dùng nhầm T = số nến, đã sửa khi ghi tài liệu):

| Quy tắc (đã công bố trước, không phải ô đẹp nhất) | Sharpe OOS | DSR, N=50 | DSR, N=150 | DSR, N=237 |
|---|---:|---:|---:|---:|
| US100 QQQ, thoát 0,8 / 4 nến | 0,71 | 0,43 | 0,28 | 0,23 |
| US100 QQQ, giữ 1 nến | 0,63 | 0,35 | 0,22 | 0,18 |
| US100 ^NDX, giữ 1 nến | 0,60 | 0,33 | 0,20 | 0,16 |
| US500 ^GSPC, thoát 0,8 / 4 nến | 0,59 | 0,31 | 0,19 | 0,15 |
| Ô lưới đẹp nhất ^NDX (IBS 0,10, thoát 0,9 / max 2) | 0,98 | 0,61 | 0,46 | 0,40 |

DSR ≈ xác suất Sharpe quan sát không phải do chọn lọc. Với N=150–237, mọi quy tắc đã công bố đều dưới 0,30. Ngay cả ô đẹp nhất cũng chỉ 0,40–0,46. **Không đủ để giữ nhãn passed sau khi hiệu chỉnh chọn lọc.**

p ngẫu nhiên cũng dao động: cùng quy tắc ^NDX thoát 0,8 / 4 nến trước đây p=0,047 (1000 lần), lượt này 0,086 (500 lần) — sát ngưỡng 0,05 thì không vững.

## Verdict

| Đối tượng | Verdict | Lý do ngắn |
|---|---|---|
| Họ long IBS trên US100, OOS 2015+ | **ứng viên** | Cao nguyên tham số, WF sau 2015 tốt, nhưng DSR thấp, IS pre-2010 lỗ, một phần lãi OOS gắn với 2020 |
| Quy tắc giữ 1 nến US100 | **ứng viên yếu hơn** | WF sau 2015 ổn, nhưng trễ 1 nến gần như mất edge |
| Quy tắc thoát IBS>0,8 / tối đa 4 nến trên US100 | **ứng viên (ưu tiên)** | Chịu trễ lệnh tốt hơn, % năm dương cao hơn; 2022 lỗ đậm; DSR chưa đủ |
| Cùng quy tắc trên US500 | **ứng viên yếu** | OOS ^GSPC vừa đủ, SPY trước đó chưa passed, trễ lệnh dễ yếu |
| Short, forex, vàng | **không edge** | Các kiểm định trước |

Không nâng lên passed. Bản mô tả ứng viên để bộ hỗ trợ tham khảo: [ibs_us100_spec.md](ibs_us100_spec.md).

## Script

[`tools/kiem_dinh/evo/ibs_cfd_robust.py`](../../tools/kiem_dinh/evo/ibs_cfd_robust.py). CSV trung gian không commit. Không ghi dữ liệu giá lên Git.
