# Kiểm định IBS trên CFD chỉ số Mỹ (US500, US100)

Cập nhật: 2026-11-15 07:46 (Asia/Saigon, UTC+7)

Kiểm định quy tắc IBS kiểu Quantified Strategies trên CFD chỉ số, khung ngày, sau spread và phí qua đêm. Dữ liệu Yahoo: ^GSPC và SPY cho US500, ^NDX và QQQ cho US100.

**Kết luận:** một số biến thể **long** đạt “passed” trên OOS từ 2015, sau phí CFD giả định. Mạnh nhất là long IBS < 0,2 rồi thoát khi IBS > 0,8 (tối đa 4 nến) trên US100, và cùng quy tắc trên US500 đo bằng ^GSPC. Short không đạt trên US500 và chỉ là ứng viên yếu trên US100. Đây **chưa phải lệnh để vào tiền ngay**: IS trước 2015 trên chỉ số tiền mặt dài hạn (^GSPC từ 1970, ^NDX từ 1985) bị lỗ; SPY đối chiếu cùng hướng nhưng không đủ p ≤ 0,05; khớp lệnh là giá mở cửa Yahoo, không phải giá CFD thật.

## Quy tắc và chuẩn kiểm

- IBS = (Close − Low) / (High − Low). Long khi IBS < 0,2; short tham chiếu khi IBS > 0,8 và close < SMA200.
- Biến thể: có/không lọc close > SMA200 (long); thoát sau 1 nến, hoặc khi IBS đảo chiều và tối đa 4 nến.
- Tín hiệu tại đóng cửa nến t, khớp **mở cửa thật nến t+1**. Không chồng lệnh.
- Spread CFD: US500 **0,6 điểm** chỉ số, US100 **1,5 điểm** (chạy thêm độ nhạy 2×: 1,2 và 3,0 điểm). SPY và QQQ dùng cùng tỷ lệ phí, chia cho tỷ lệ quy mô trung vị GSPC/SPY = 9,995 và NDX/QQQ = 40,783.
- Phí qua đêm (luôn là chi phí): long **7,5%/năm**, short **2,5%/năm**, chia 365 mỗi đêm trên giá trị danh nghĩa. Thứ Sáu sang thứ Hai = 3 đêm lịch. Đây là hằng số; thực tế 2015–2021 lãi suất thấp hơn, nên OOS có phí có phần **khe chặt**.
- Tách IS trước 2015-01-01, OOS từ 2015. Báo thêm giai đoạn 2020 trở đi. Đối chứng: dịch vòng vị thế 1000 lần trong từng giai đoạn.
- Sharpe và %/năm tính trên chuỗi lợi nhuận theo lịch (kể cả ngày không có lệnh).
- **Passed** chỉ khi OOS 2015+ đứng một mình: ≥30 lệnh, PF ≥ 1,20, Sharpe ≥ 0,30, lãi TB > 0, p ≤ 0,05. Lãi mỏng hơn baseline nhưng chưa đủ mạnh: ứng viên yếu. OHLC của SPY/QQQ **không** điều chỉnh cổ tức (gần với CFD chỉ số giá hơn ETF tổng lợi nhuận).

## Dữ liệu (Yahoo Finance, tải 2026-11-15)

| Chuỗi | Mã Yahoo | Vai trò | Từ | Đến | Số nến | Spread quy về giá |
|---|---|---|---|---|---:|---|
| US500_GSPC | ^GSPC | Chính, US500 | 1970-01-02 | 2026-11-13 | 14321 | 0,60 điểm |
| US500_SPY | SPY | Đối chiếu | 1993-01-29 | 2026-11-13 | 8507 | 0,060 điểm |
| US100_NDX | ^NDX | Chính, US100 | 1985-10-01 | 2026-11-13 | 10360 | 1,50 điểm |
| US100_QQQ | QQQ | Đối chiếu | 1999-03-10 | 2026-11-13 | 6965 | 0,0368 điểm |

Không commit chuỗi giá thô. Không dùng nến H1 CFD (có file US500CASH_H1 trên box) trong lượt này.

## Bảng OOS 2015–2026, spread 1× + phí qua đêm

| Chuỗi | Biến thể | Lệnh | Win% | Lãi TB % | PF | Sharpe | %/năm | Max DD % | p vs ngẫu nhiên | Kết luận |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| US500 (^GSPC) | Long IBS<0,2, giữ 1 nến | 477 | 57,02 | 0,069 | 1,20 | 0,40 | 2,57 | 12,49 | 0,063 | ứng viên yếu |
| US500 (^GSPC) | Long IBS<0,2 + SMA200, giữ 1 nến | 365 | 55,89 | 0,021 | 1,07 | 0,14 | 0,54 | 12,49 | 0,318 | ứng viên yếu |
| US500 (^GSPC) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 390 | 63,33 | 0,172 | 1,37 | 0,59 | 5,43 | 11,14 | 0,027 | passed |
| US500 (^GSPC) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 303 | 60,73 | 0,114 | 1,29 | 0,45 | 2,76 | 13,12 | 0,099 | ứng viên yếu |
| US500 (^GSPC) | Short IBS>0,8 + SMA200, giữ 1 nến (tham chiếu) | 130 | 41,54 | -0,063 | 0,89 | -0,13 | -0,82 | 18,09 | 0,293 | không edge |
| US500 (^GSPC) | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến (tham chiếu) | 92 | 50,00 | -0,249 | 0,78 | -0,28 | -2,13 | 29,79 | 0,392 | không edge |
| US500 (SPY, đối chiếu) | Long IBS<0,2, giữ 1 nến | 444 | 55,86 | 0,031 | 1,08 | 0,15 | 0,86 | 24,12 | 0,293 | ứng viên yếu |
| US500 (SPY, đối chiếu) | Long IBS<0,2 + SMA200, giữ 1 nến | 337 | 55,19 | -0,000 | 1,00 | -0,00 | -0,12 | 19,24 | 0,518 | không edge |
| US500 (SPY, đối chiếu) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 363 | 59,50 | 0,151 | 1,29 | 0,44 | 4,29 | 20,87 | 0,097 | ứng viên yếu |
| US500 (SPY, đối chiếu) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 280 | 57,86 | 0,116 | 1,27 | 0,39 | 2,55 | 13,28 | 0,119 | ứng viên yếu |
| US500 (SPY, đối chiếu) | Short IBS>0,8 + SMA200, giữ 1 nến (tham chiếu) | 128 | 40,62 | -0,075 | 0,88 | -0,15 | -0,95 | 21,47 | 0,342 | không edge |
| US500 (SPY, đối chiếu) | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến (tham chiếu) | 94 | 46,81 | -0,270 | 0,76 | -0,29 | -2,42 | 36,33 | 0,455 | không edge |
| US100 (^NDX) | Long IBS<0,2, giữ 1 nến | 484 | 58,68 | 0,155 | 1,31 | 0,60 | 5,95 | 16,42 | 0,046 | passed |
| US100 (^NDX) | Long IBS<0,2 + SMA200, giữ 1 nến | 368 | 58,97 | 0,094 | 1,21 | 0,38 | 2,65 | 16,42 | 0,173 | ứng viên yếu |
| US100 (^NDX) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 395 | 62,53 | 0,254 | 1,41 | 0,61 | 8,13 | 22,51 | 0,047 | passed |
| US100 (^NDX) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 306 | 62,09 | 0,230 | 1,43 | 0,56 | 5,73 | 15,66 | 0,101 | ứng viên yếu |
| US100 (^NDX) | Short IBS>0,8 + SMA200, giữ 1 nến (tham chiếu) | 127 | 48,03 | 0,079 | 1,12 | 0,15 | 0,69 | 11,40 | 0,086 | ứng viên yếu |
| US100 (^NDX) | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến (tham chiếu) | 88 | 60,23 | 0,171 | 1,17 | 0,15 | 0,92 | 20,81 | 0,050 | ứng viên yếu |
| US100 (QQQ, đối chiếu) | Long IBS<0,2, giữ 1 nến | 449 | 57,02 | 0,173 | 1,35 | 0,63 | 6,20 | 18,34 | 0,025 | passed |
| US100 (QQQ, đối chiếu) | Long IBS<0,2 + SMA200, giữ 1 nến | 337 | 57,86 | 0,121 | 1,29 | 0,47 | 3,21 | 15,59 | 0,107 | ứng viên yếu |
| US100 (QQQ, đối chiếu) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 371 | 63,34 | 0,317 | 1,51 | 0,71 | 9,68 | 22,75 | 0,029 | passed |
| US100 (QQQ, đối chiếu) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 284 | 63,03 | 0,283 | 1,55 | 0,65 | 6,63 | 15,16 | 0,049 | passed |
| US100 (QQQ, đối chiếu) | Short IBS>0,8 + SMA200, giữ 1 nến (tham chiếu) | 127 | 48,82 | 0,077 | 1,13 | 0,15 | 0,68 | 11,94 | 0,077 | ứng viên yếu |
| US100 (QQQ, đối chiếu) | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến (tham chiếu) | 88 | 60,23 | 0,222 | 1,25 | 0,20 | 1,29 | 22,19 | 0,025 | ứng viên yếu |

### Những dòng đạt passed (OOS 2015+)

| Chuỗi | Biến thể | OOS lệnh | Win% | Lãi TB % | PF | Sharpe | %/năm | p | IS (trước 2015) | 2020+ | Còn passed khi spread 2×? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| US500 (^GSPC) | Long, thoát IBS>0,8 / tối đa 4 nến | 390 | 63,33 | 0,172 | 1,37 | 0,59 | 5,43 | 0,027 | không edge (Sharpe −0,45) | ứng viên yếu (p=0,058, PF 1,45) | Có (PF 1,33, p=0,018) |
| US100 (^NDX) | Long, giữ 1 nến | 484 | 58,68 | 0,155 | 1,31 | 0,60 | 5,95 | 0,046 | không edge (Sharpe −0,82) | passed (p=0,032, PF 1,39) | Có (PF 1,27, p=0,035) |
| US100 (^NDX) | Long, thoát IBS>0,8 / tối đa 4 nến | 395 | 62,53 | 0,254 | 1,41 | 0,61 | 8,13 | 0,047 | không edge (Sharpe −0,17) | ứng viên yếu (p=0,129) | Không, xuống ứng viên yếu (p=0,054) |
| US100 (QQQ) | Long, giữ 1 nến | 449 | 57,02 | 0,173 | 1,35 | 0,63 | 6,20 | 0,025 | ứng viên yếu (PF 1,12) | passed (p=0,046, PF 1,45) | Có (PF 1,31, p=0,029) |
| US100 (QQQ) | Long, thoát IBS>0,8 / tối đa 4 nến | 371 | 63,34 | 0,317 | 1,51 | 0,71 | 9,68 | 0,029 | ứng viên yếu (PF 1,09) | ứng viên yếu (p=0,075) | Có (PF 1,47, p=0,028) |
| US100 (QQQ) | Long + SMA200, thoát IBS>0,8 / tối đa 4 nến | 284 | 63,03 | 0,283 | 1,55 | 0,65 | 6,63 | 0,049 | không edge | ứng viên yếu (p=0,073) | Có (PF 1,51, p=0,034) |

Long giữ 1 nến trên ^GSPC chỉ là ứng viên yếu: PF 1,20 (làm tròn; thực 1,199), Sharpe 0,40, p=0,063 — trượt ngưỡng passed. SPY cùng quy tắc thoát IBS>0,8 có PF 1,29 và Sharpe 0,44 nhưng p=0,097, nên không passed; cùng hướng với ^GSPC, yếu hơn về mặt thống kê. Lọc SMA200 thường làm giảm số lệnh và hiếm khi giúp OOS. Short không edge trên US500; trên US100 chỉ ứng viên yếu.

IS âm trên ^GSPC (từ 1970) và ^NDX (từ 1985) là cảnh báo quan trọng: edge OOS tập trung ở khoảng 2015–2026. SPY (IS từ 1993) với cùng quy tắc thoát IBS>0,8 lại **passed trên IS** (705 lệnh, PF 1,31, Sharpe 0,48, p=0,001) — phần lỗ IS của ^GSPC chủ yếu nằm trước thời SPY.

## Tác động của phí qua đêm

Phí 7,5%/năm với lệnh long giữ 1–4 ngày ăn khoảng **1,1–2,7 điểm phần trăm CAGR** trên OOS, nhưng thường không làm đổi kết luận ở spread 1×. Bảng dưới chỉ các biến thể long, OOS 2015+:

| Chuỗi | Biến thể | CAGR có phí đêm | CAGR không phí đêm | Phí đêm ăn (điểm %) | PF 1x | PF 2x spread | Kết luận 1x | Kết luận 2x |
|---|---|---:|---:|---:|---:|---:|---|---|
| US500 (^GSPC) | Long IBS<0,2, giữ 1 nến | 2,57 | 3,82 | 1,24 | 1,20 | 1,14 | ứng viên yếu | ứng viên yếu |
| US500 (^GSPC) | Long IBS<0,2 + SMA200, giữ 1 nến | 0,54 | 1,47 | 0,93 | 1,07 | 1,01 | ứng viên yếu | ứng viên yếu |
| US500 (^GSPC) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 5,43 | 7,99 | 2,56 | 1,37 | 1,33 | passed | passed |
| US500 (^GSPC) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 2,76 | 4,73 | 1,96 | 1,29 | 1,24 | ứng viên yếu | ứng viên yếu |
| US500 (SPY, đối chiếu) | Long IBS<0,2, giữ 1 nến | 0,86 | 1,99 | 1,12 | 1,08 | 1,03 | ứng viên yếu | ứng viên yếu |
| US500 (SPY, đối chiếu) | Long IBS<0,2 + SMA200, giữ 1 nến | -0,12 | 0,72 | 0,84 | 1,00 | 0,94 | không edge | không edge |
| US500 (SPY, đối chiếu) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 4,29 | 6,68 | 2,39 | 1,29 | 1,25 | ứng viên yếu | ứng viên yếu |
| US500 (SPY, đối chiếu) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 2,55 | 4,39 | 1,84 | 1,27 | 1,23 | ứng viên yếu | ứng viên yếu |
| US100 (^NDX) | Long IBS<0,2, giữ 1 nến | 5,95 | 7,29 | 1,34 | 1,31 | 1,27 | passed | passed |
| US100 (^NDX) | Long IBS<0,2 + SMA200, giữ 1 nến | 2,65 | 3,63 | 0,98 | 1,21 | 1,17 | ứng viên yếu | ứng viên yếu |
| US100 (^NDX) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 8,13 | 10,81 | 2,67 | 1,41 | 1,38 | passed | ứng viên yếu |
| US100 (^NDX) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 5,73 | 7,76 | 2,03 | 1,43 | 1,40 | ứng viên yếu | ứng viên yếu |
| US100 (QQQ, đối chiếu) | Long IBS<0,2, giữ 1 nến | 6,20 | 7,43 | 1,23 | 1,35 | 1,31 | passed | passed |
| US100 (QQQ, đối chiếu) | Long IBS<0,2 + SMA200, giữ 1 nến | 3,21 | 4,11 | 0,90 | 1,29 | 1,24 | ứng viên yếu | ứng viên yếu |
| US100 (QQQ, đối chiếu) | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 9,68 | 12,21 | 2,54 | 1,51 | 1,47 | passed | passed |
| US100 (QQQ, đối chiếu) | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 6,63 | 8,52 | 1,88 | 1,55 | 1,51 | passed | passed |

Đội spread lên 2×: hầu hết dòng đã passed vẫn passed, trừ long thoát IBS>0,8 trên ^NDX (p tăng lên 0,054). Không tính phí đêm thì CAGR cao hơn, nhưng p đôi khi kém đi vì baseline ngẫu nhiên cũng đỡ bị phí — vì thế chuẩn chính vẫn là có spread 1× và có phí đêm.

## Ý nghĩa

- IBS **có thể** dùng để đánh CFD chỉ số Mỹ khung ngày (US500/US100), không dùng cho CFD forex hay vàng trên cơ sở các kiểm định trước.
- Ứng viên đáng xem nhất: long khi IBS < 0,2, thoát khi IBS > 0,8 hoặc tối đa 4 nến, trên US100; cùng quy tắc trên US500 cần đối chiếu thêm vì SPY chưa passed.
- Chưa đưa vào bộ hỗ trợ trading như tín hiệu đã chốt. Cần khớp với spread/swap thật của sàn định dùng, và nhớ IS dài hạn trên chỉ số tiền mặt không ủng hộ.
- Chưa phải kiểm thử SEEKER đầy đủ (chưa FDR như cổng pass/fail, chưa dữ liệu tick/CFD thật).

## Hạn chế

- Giá Yahoo của chỉ số/ETF, không phải giá bid-ask CFD; mở cửa phiên Mỹ chỉ là gần đúng với fill CFD.
- Phí đêm là hằng số 7,5%/2,5%, không theo lịch sử lãi suất từng năm.
- SPY/QQQ không cộng cổ tức; đúng hơn với CFD chỉ số giá, thấp hơn nếu so với nắm ETF.
- p của vài dòng passed sát 0,05; mẫu OOS ~11,8 năm nhưng số lần độc lập không lớn.
- Không commit dữ liệu giá.

## Script

Mã chạy lại: [`tools/kiem_dinh/evo/ibs_cfd_chi_so.py`](../../tools/kiem_dinh/evo/ibs_cfd_chi_so.py), tái sử dụng khung trong [`ibs_cap_cheo.py`](../../tools/kiem_dinh/evo/ibs_cap_cheo.py). Cần pandas/numpy và CSV Yahoo (không nằm trên Git).
