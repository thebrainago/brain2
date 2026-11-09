# V3 MT5 ghep60ff adxngang GBPCAD# H1 (09/11/2026, máy nhà, slot g12)

EA `BRAIN\BRAIN_XuLiLenh.ex5` bản 30/10 (B10A892B; không có InpAdxMin/Max — .set đặt 0 nên không khác). CSV `v3a_ghep60ff_adxngang_H1_vao_hash.csv` (sha256 ddbd0c93, 13.758 dòng) ở Common\Files. Model 4, 10.000 USD, 1:500, tới 2026.10.10.
Swap tester = 0 (symbol #). Swap ước: XM micro GBPCAD mua +0,57 / bán −16,22 điểm/lot/đêm, ×3 đêm thứ 4, 1 điểm/lot = 0,71211 USD (tỉ giá CAD lúc đo 10/2026).

| Lượt | Tick thật | Lãi ròng | CAGR kép | CAGR sau swap ước | DD equity max | DD equity tương đối | PF | Lệnh | Rổ (EA) | Giữ max | Lot mở max | Swap ước | Python (CAGR/DD) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A 2009.01–2026.10 | 15% | +27.809,26 | 7,77% | 7,87% | 14.699,51 (67,89%) | 75,91% | 1,71 | 563 | 366 | 32,0 ngày | 7,41 | +619,9 | 12,81% / 46,69% |
| B 2024.01–2026.10 | 99% | +25.729,77 | 58,27% | 58,96% | 14.699,51 (75,11%) | 75,11% | 2,35 | 257 | 165 | 30,4 ngày | 7,41 | +435,1 | 63,82% / 68,11% |

Lệnh MT5 đầu tiên của Lượt A: 2018.04.19. Lịch sử GBPCAD# 2007–2017 trên máy nhà chỉ 59–467 KB/năm → EA bỏ 6.308 dòng CSV vì trễ (bo_tre). Python có 2011–2015 lãi ≈ +43.651 USD.
Riêng đoạn MT5 có dữ liệu (2018.04.19–2026.10.10, 8,48 năm): CAGR 16,99% (17,21% sau swap ước).

Kết luận: Lượt B ĐẠT; Lượt A TRƯỢT (CAGR 7,87% < 10%), nhưng Lượt A thiếu dữ liệu 2009–2018 nên chưa phải phép đo đầy đủ.
