# BẢNG HỌ CHIẾN LƯỢC — tổng hợp vòng 7–29 + sổ MT5 + lưới Python box

Lập 14/10/2026 (giờ VN). **Toàn bộ là MÔ PHỎNG / backtest tester MT5 trên tài khoản demo, không phải tiền thật.**
Chỉ chép số đo thật có trong repo; ô nào repo không có số → **CHƯA ĐO ĐƯỢC**.

Nguồn: `reports/vong7…vong29_x.json` + `*_tien_dang_ky.md`, `reports/vong19.json` (`bang_nhom`), `reports/vong19b.json`,
`reports/vong22.json` (`bang`), `reports/mt5_lien_tuc/so_cai.jsonl` (630 lần chạy MT5), `reports/mt5_lien_tuc/box_luoi_python.json`
(38.736 lần thử Python), `tai_lieu/KINH_NGHIEM.md`, `GHI_CHU_NANG_CAP_GROK.md`.

Cách hiểu các cột:
- **Cơ chế phát hiện** = số luật vào lệnh khác nhau đã gán vào họ. Cột này lấy `so_co_che` của bảng nhóm vòng 19 (gồm kết quả cũ v14–v18 gán nhãn cố định) và cộng thêm các luật mới ở vòng sau nếu có ghi.
- **Biến thể đã thử** = số ô (luật × thoát × tài sản × khung) đếm được trong file json.
- **Lãi cả 2 giai đoạn sau phí** = nửa phát hiện > 0 **và** nửa kiểm > 0, đã trừ phí XM. Chỉ đếm trong file có đủ hai cột này (đã ghi nguồn).
- **Qua Holm** = qua Holm cộng dồn tại thời điểm chạy (họ phép thử lúc cuối là 13.000). Chỉ 4 hệ từng qua.

## 1. Bảng theo họ

| Họ | Cơ chế phát hiện | Biến thể đã thử | Lãi cả 2 giai đoạn sau phí | Qua Holm | Hệ tốt nhất (số đo thật) | Đã ghép đa cơ chế? |
|---|---|---|---|---|---|---|
| **Lịch / mùa vụ** (cuối-đầu tháng, Halloween, năm 3 bầu cử, Santa, tháng × thứ…) | 4.036 (v19) | v10: 8 luật; v14: 4.258 ô; v16: 16; v17 hàng hoá: 351; v29 R4: 5 tài sản | v29 R4: 4/5 tài sản (SPX, NDX, vàng; DAX nửa kiểm không đạt cổng T2) — các vòng khác: CHƯA ĐO ĐƯỢC theo kiểu “2 nửa” (đo theo vượt mua-giữ) | **2**: DANH_MUC_4_SPX (p_holm 0,0033), DAU_CUOI_THANG (p_holm 0,023) — vòng 15, họ 4.347 | DANH_MUC_4_SPX: z 4,81, maxDD 16,2 %. R4 Turn-of-month SPX (v29): holdout 93 lệnh, 60,6 bps/lệnh, PF 1,90 (Holm 1,0). Win rate: CHƯA ĐO ĐƯỢC | **Có**: danh mục 4 luật lịch; v14 ghép 2 mảnh lịch (thứ×tháng, chu kỳ×tháng…). Chưa ghép lịch với IBS/RSI |
| **IBS** (giá đóng sát đáy nến ngày) | 3 dạng: IBS<0,2 giữ 1 ngày (v11b–v15), V6 IBS (S&P+NDX), IBS<0,2 thoát close>high hôm trước (v29 R6) | v11b/v12: S&P; v13: 5 tài sản; v15: 2; v29 R6: 5 tài sản | v29: 4/5 qua T1+T2 (SPX, NDX, vàng, GBPUSD Yahoo — GBPUSD bị loại vì OHLC Yahoo sai); DAX không | **2**: R6 US500 (p_holm 0,0033), R6 US100 (p_holm 0,0015) — họ 13.000 | R6 NDX: holdout 241 lệnh, 76,2 bps/lệnh, PF 2,48; R6 SPX: 236 lệnh, 56,2 bps, PF 2,49. Win rate: CHƯA ĐO ĐƯỢC. MT5: CHƯA ĐO ĐƯỢC (cần EA thoát mới) | Một phần: R7 = dải biên độ + IBS<0,3 (Holm 1,0). Chưa ghép IBS với RSI2 / N ngày giảm / lịch |
| **Mean reversion** (z-score, MRZ, gặp lại EMA, Bollinger) | 79 (v19) + EMA-MR v21 (4 EMA × 4 k) + MRZ các vòng 24–28 | v21: 5.472 ô (2.614 đủ lệnh); v22 MR+EMA: 426 ô; v19 MR: 56 ô; v26–28: ~30 ô; Python box MRZ+RSI: 19.368 cặp IS/OOS; MT5 MRZ: 117 cặp IS/OOS | v21: 329/2.614; v22 MR 6/142, EMA 11/284; v19: 0/56; Python box (MRZ+RSI chung): 748; **MT5 MRZ: 113/117** cặp có net > 0 cả IS lẫn OOS | **0** (MT5: p IS nhỏ nhất 0,0158; Python: Holm 0) | MRZ AUDUSD D1 vào 02h (v26): 29,5 / 67,8 bps/lệnh, 78/85 lệnh, p 0,008. Python box AUDUSD#: PF IS 2,41 (63 lệnh) / OOS 2,46 (31 lệnh). MT5 AUDUSD#: PF IS 2,21 (51 lệnh) / OOS 2,5 (25 lệnh). Win rate: CHƯA ĐO ĐƯỢC | **Có**: v19 ghép MR+ĐẢO_CHIỀU (126 ô ghép, 0 sống); v26 lọc EMA200/vol thấp/+DINH20 (ghép DINH20 làm xấu đi); v27 MRZ+EMA12/26, MRZ+RSI cạn; v28 MRZ+ADX<20/ATR thấp, MRZ+W1 EMA20 |
| **Đảo chiều theo dao động** (RSI 30/70, BB, Stoch, MACD) | 349 (v19) | v17: 14 tổ hợp ≤3 mảnh × 4 quản lý × 7 cặp = 392 ô; v19: 56; v22: 142; MT5 RSI: 134 cặp IS/OOS | v17: 10/392; v19: 0/56; v22: 9/142; **MT5 RSI: 134/134** cặp net > 0 cả hai | **0** (MT5 p IS nhỏ nhất 0,054) | Python box RSI EURJPY#: PF IS 2,25 (40 lệnh) / OOS 2,27 (19 lệnh). MT5 RSI EURJPY#: PF IS 2,26 (35 lệnh) / OOS 3,61 (15 lệnh). v24 RSI_TR2_D1 pool 54 tài sản: +25 bps/lệnh nửa kiểm nhưng nửa đầu −6 bps | **Có**: v17 ghép RSI+BB+MACD+STO (gồm “MACD xác nhận”), v19 ghép với MR |
| **Bắt đảo chiều sau cú giảm mạnh** (sự kiện hiếm) | 6: SPX_3TUAN_GIAM (v11), R1 RSI5<30+SMA200, R2 RSI4<30+EMA100 lên, R3 Triple RSI (RSI5<30 + 3 ngày giảm + SMA200), R5 3 ngày giảm, R7 dải biên độ+IBS<0,3; thêm v18 B4 “kiệt sức-đảo chiều” H1 | v11: 1; v18 B4: 21 ô (7 cặp × 3); v29: 5 luật × 5 tài sản = 25 ô | v29: 17/25 qua T1+T2 (xem mục 3) | **0** | R3 NDX: phát hiện 56 lệnh 133 bps PF 4,96 / holdout 21 lệnh 97 bps PF 3,68 (p 0,014, Holm 1,0). R1 SPX: holdout 48 lệnh 70 bps PF 2,77 | **Có một phần**: R1, R3 ghép quá bán + lọc MA200; R3 xếp chồng 3 điều kiện. Chưa ghép IBS + RSI2 + z-score |
| **Trend following / động lượng / xu hướng dài** (ROC, MACD cắt 0, MA50/200, Donchian55, Supertrend, TrendBreaker, Ichimoku) | 154 (v19 ĐỘNG_LƯỢNG) + XU_HƯỚNG_DÀI 2 + ICHIMOKU 1 (v19b) + TradingView v23 | v19: 112; v19b: 78+36+39; v22: 568; v23: 1.408 ô (1.175 đủ lệnh, gồm cả họ khác) | v19: 5/112; v19b XU_HƯỚNG_DÀI 6/78, ICHIMOKU 2/39, ĐỘNG_LƯỢNG 3/36; v22: ĐỘNG_LƯỢNG 12/284, XU_HƯỚNG_DÀI 4/284; v23 (mọi họ): 106/1.175 | **0** | TRENDBREAKER H4 (v23): 8/10 chuỗi lãi nửa kiểm, trung vị +2,1 %; USDJPY H1 TRENDBREAKER+Supertrend p 0,014. PF / win rate: CHƯA ĐO ĐƯỢC | **Có**: v23 ghép 6 tín hiệu × 5 lọc × 2 quản lý (960 ô); lọc MA200 cho đòn bẩy US500 (v17) |
| **Phá vỡ (breakout) / break-retest** | 140 (v19) | v17: 4 luật × 84 ô; v18: 84 ô (straddle, breakout 24 bar); v19: 56; v19b: 18; v22: 142 | v17: 1/84; v19: 0/56; v19b: 0/18; v22: 4/142 | **0** | Trung vị nửa kiểm âm ở mọi khung (v22 H4 −6,3 %); không có ô tốt nổi bật. Break-**retest**: chỉ có `quant/co_che_A_cung_cau_engulfing.py` (retest vùng cung-cầu + engulfing), **không có số trong bảng vòng 17–29 → CHƯA ĐO ĐƯỢC** | Có: ghép với DINH20 trong v26 (làm xấu). Retest + xác nhận: chưa |
| **Đánh cản / hỗ trợ-kháng cự** (pivot, Fib, SMC order block/sweep/FVG) | SR_PIVOT 1 + FIB 1 + SMC 2 (v19b) | v19b: 39+39+78; v22 SMC: 284 | v19b: SR_PIVOT 4/39, FIB 1/39, SMC 5/78; v22 SMC 14/284 | **0** | SMC bộ 2 p 0,0074 nhưng trung vị kiểm −25,7 %; thuộc nhóm tệ nhất v19b. PF: CHƯA ĐO ĐƯỢC | Chưa |
| **Mô hình nến** (engulfing, pinbar) | 112 (v19) | v19: 112; v19b: 36; v22: 284 | v19: 0/112; v19b: 5/36; v22: 12/284 | **0** | Nhóm tệ nhất v19 (trung vị kiểm −15,2 %). | Chưa (trừ retest+engulfing chưa đo) |
| **Gap / đa khung / news fade / ML** | GAP 1, ĐA_KHUNG 1, NEWS_FADE 1, ML 1 (v19b) | v19b: 39 mỗi họ; v22: 142 (GAP), 142+130 (đa khung), 142 (news fade) | v19b GAP 5/39, ĐA_KHUNG 8/39, ML 7/39, VĨ_MÔ(news fade) 8/39; v22 GAP 15/142, ĐA_KHUNG 6+5, NEWS_FADE 5 | **0** | NZDUSD H1 GAP_FILL p thô 0,00067 (47 lệnh, v22); ĐA_KHUNG bộ 1: 52 % ô lãi nửa kiểm | Chưa |
| **Vĩ mô / liên thị trường** (lãi suất, carry, chéo tài sản) | 599 (v19) | v11: 13 luật; v14 phần chéo (trong 4.258) | CHƯA ĐO ĐƯỢC theo 2 nửa | **0 còn sống** (NDX sau USDCAD giảm qua Holm ở v14, p_holm 0,038, nhưng rớt ở v15, p 0,10) | TNX_USDJPY v15: z 3,05, p 0,0011, Holm 1,0 | Chưa |
| **Phiên / giờ** | 98 (v19) | v19: 56; v19b: 57; v22: 284 | v19: 0; v19b: 2/57; v22: **0/284** | **0** | Tệ nhất mọi vòng | Chưa |
| **Lưới / hedge / martingale** | 7 (v19) | v18 B5: 7 cặp | 0 | **0** | 7/7 cặp lỗ 62–100 %, cháy 3/7 | — |
| **Đòn bẩy mua-giữ** | 12 (v19) | v17: 36 ô | CHƯA ĐO ĐƯỢC theo 2 nửa | **0** | US500 lọc MA200 1×: 2,5 %/năm, DD 40 % (z 1,4) | Có lọc MA200, vol-target |

## 2. Trả lời ngắn (a) (b) (c)

**(a) Đã lọc ra họ tốt nhất chưa?** Có, ở mức “họ nào còn sống sau Holm”:
1. **IBS trên chỉ số Mỹ** (US500, US100) — 2 hệ qua Holm cộng dồn 13.000 (v29). Chưa chạy MT5.
2. **Lịch / mùa vụ trên S&P** — 2 hệ qua Holm ở vòng 15 (danh mục 4 luật, đầu/cuối tháng).
3. **Mean reversion / đảo chiều RSI trên D1** — nhiều biến thể lãi cả hai giai đoạn (MT5 113/117 MRZ, 134/134 RSI) nhưng **0 qua Holm**: ứng viên gần nhất là MRZ AUDUSD.
Các họ còn lại (trend, breakout, cản, nến, phiên, lưới) chưa có hệ nào qua Holm; trung vị nửa kiểm đều âm sau phí.

**(b) Số cơ chế và số ghép:** xem cột 2–3 và cột cuối của bảng trên. Ghép đa cơ chế đã làm nhiều nhất ở MR/đảo chiều (v17: 14 tổ hợp RSI/BB/MACD/Stoch; v19: 126 ô ghép; v26–28: lọc EMA200/ADX/W1) và trend (v23: 960 ô ghép lọc).

**(c) Ý “sự kiện hiếm, xác suất hồi nhẹ cao”:** chính là các họ IBS + bắt đáy sau cú giảm (mục 3). Đây cũng là chỗ duy nhất ra hệ qua Holm (IBS).

## 3. Nhóm sự kiện hiếm — win rate và mức hồi trung bình (v29, sau phí, D1, holdout từ 2019)

Win rate (tỷ lệ lệnh thắng): **CHƯA ĐO ĐƯỢC** — `vong29_x.json` chỉ lưu n, bps/lệnh trung bình, PF, p. Sổ MT5 cũng không ghi win rate.
Mức hồi trung bình = bps/lệnh trung bình sau phí.

| Luật | Tài sản | Phát hiện: lệnh / bps / PF | Holdout: lệnh / bps / PF | p_holm |
|---|---|---|---|---|
| R6 IBS<0,2, thoát close>high hôm trước | SPX | 511 / 35,0 / 1,61 | 236 / 56,2 / 2,49 | **0,0033 (qua)** |
| R6 | NDX | 512 / 47,8 / 1,64 | 241 / 76,2 / 2,48 | **0,0015 (qua)** |
| R6 | Vàng | 502 / 18,8 / 1,28 | 141 / 42,4 / 1,71 | 1,0 |
| R6 | DAX | 479 / 8,0 / 1,08 | 211 / 3,0 / 1,04 | 1,0 |
| R1 RSI5<30 & >SMA200 | SPX / NDX / vàng | 100/75,8/3,37 · 114/86,6/2,92 · 88/72,3/2,02 | 48/70,0/2,77 · 48/80,8/2,82 · 36/83,0/2,53 | 1,0 |
| R2 RSI4<30 & EMA100 lên | SPX / NDX / vàng | 158/45,6/2,15 · 167/70,4/2,53 · 125/37,7/1,56 | 74/51,2/2,16 · 71/72,8/2,42 · 53/55,8/2,00 | 1,0 |
| R3 Triple RSI (RSI5<30 + giảm 3 ngày + >SMA200) | SPX / NDX / vàng | 40/107,8/4,01 · 56/133,2/4,96 · 42/95,5/2,80 | 23/89,1/3,69 · 21/97,4/3,68 · 21/110,7/4,19 | 1,0 |
| R3 | DAX | 53 / 125,5 / 6,58 | 20 / **−77,0** / 0,58 | 1,0 |
| R5 3 ngày giảm, mua close bán open | SPX / NDX | 381/1,1/1,21 · 399/14,1/1,50 | 168/10,8/1,58 · 140/18,8/1,61 | 1,0 |
| R7 dải biên độ + IBS<0,3 | SPX / NDX / vàng | 236/55,7/1,95 · 256/82,8/2,41 · 296/17,1/1,24 | 97/61,1/2,25 · 95/68,0/1,91 · 74/70,8/2,78 | 1,0 |

Gần với “hồi lại” nhất có số xác suất: vòng 21 đo **tỷ lệ giá chạm lại EMA** sau khi lệch ≥ k·ATR (đây là xác suất chạm, không phải win rate sau phí): D1 EMA20 k=2: 87 % (chuỗi ngẫu nhiên 76 %, z 3,1); H1 EMA50 k=3: 85 % vs 78 %. Nhưng giao dịch theo nó (5.472 ô) thì 0 qua Holm.

Nhận xét: luật càng hiếm (R3 ~20 lệnh/holdout) thì bps/lệnh càng cao nhưng p không đủ nhỏ để qua Holm 13.000 (cần p ≲ 4e-6). Luật dày hơn (IBS ~240 lệnh) mới qua được. DAX không lặp lại → cạnh đặc thù chỉ số Mỹ.

## 4. Ghép nối CHƯA TỪNG THỬ (không tìm thấy trong repo)

1. **Mô hình 2 đáy / 2 đỉnh (double bottom/top)**: không có máy phát hiện nào trong mã Python (tìm `double bottom`, `hai_day`… không ra). → chưa thử, kể cả 2 đáy + MACD chuyển dương.
2. **MACD làm xác nhận cho mô hình giá**: MACD chỉ được ghép với dao động (RSI/BB/Stoch, v17, FX H1). Chưa ghép MACD với 2 đáy, với IBS, với cú giảm mạnh.
3. **Break-retest** có mã (`quant/co_che_A_cung_cau_engulfing.py`) nhưng không có số trong các vòng 17–29 → CHƯA ĐO ĐƯỢC.
4. **Lọc MA200 / ADX cho IBS**: IBS R6 chưa có lọc MA200, ADX. MA200 chỉ dùng cho R1/R3 (RSI), đòn bẩy US500 (v17), EMA200 cho MRZ (v25–26, còn < 30 lệnh). ADX chỉ dùng cho MRZ (v28) và phân trạng thái (v20).
5. **Xếp chồng sự kiện hiếm có hệ thống**: chỉ có R3 (RSI5 + 3 ngày giảm + SMA200) và R7 (dải + IBS). **Chưa thử**: IBS thấp + RSI2 cực thấp; IBS + N ngày giảm liên tiếp; z-score cực (≤ −2,5/−3) + IBS; RSI2 (chưa có luật RSI2 nào); giảm N ngày + mùa vụ (cuối tháng).
6. **Ghép sự kiện hiếm với lịch** (IBS/RSI × cửa sổ đầu-cuối tháng): chưa thử, dù đây là 2 họ duy nhất qua Holm.
7. **Sự kiện hiếm trên tài sản khác chỉ số Mỹ với OHLC broker**: FX trên Yahoo bị loại (OHLC sai); IBS/R3 trên dữ liệu MT5 XM: CHƯA ĐO ĐƯỢC.
8. **Win rate, mức hồi tối đa trong N ngày (MFE)** của các sự kiện hiếm: CHƯA ĐO ĐƯỢC.

## 5. Đề xuất 3–5 hệ ghép sự kiện hiếm nên thử tiếp (phải tiền đăng ký, ít ô, đếm Holm)

1. **IBS<0,2 + close > MA200** trên US500/US100 (lọc regime cho hệ đã qua Holm; thoát close>high hôm trước).
2. **IBS<0,2 + RSI2<10** (hai thước đo “đóng cửa yếu” chồng nhau), cùng thoát R6; đo thêm win rate và MFE 1–5 ngày.
3. **Giảm ≥3 ngày liên tiếp + IBS<0,25 + close > MA200** (R3 rút gọn, thay RSI5 bằng IBS để tăng n).
4. **z-score(20) ≤ −2,5 + MA200 lên + ADX<25** trên chỉ số Mỹ và vàng D1 (MRZ phiên bản “sụp hiếm” trong xu hướng tăng).
5. **IBS<0,2 trong cửa sổ cuối/đầu tháng** (ghép 2 họ duy nhất sống).
Song song: viết **máy phát hiện 2 đáy** + xác nhận **MACD histogram chuyển dương**, lọc MA200 — để lấp lỗ hổng mục 4.1 (một ô duy nhất mỗi tài sản, không quét lưới).
Mỗi hệ: tối đa 1 cấu hình cố định × 2–4 tài sản, ghi win rate + bps/lệnh + PF + n, áp lực spread ×1,5 + 1 bps, rồi MT5.

---

# 6. Hai EA chuyên biệt cho sự kiện hiếm (bổ sung 14/10/2026, theo yêu cầu của Anh)

Bối cảnh: Anh từng x2 tài khoản vàng, x9 tài khoản dầu nhờ mua đuổi sóng lớn. Cần 2 EA: (1) bám trend mạnh có nhồi lệnh + trailing rộng; (2) đánh hồi sau cú quét cực mạnh, chốt nhanh.
Toàn bộ số dưới đây là **MÔ PHỎNG** Python trên giá D1, không phải MT5 hay tiền thật.

## 6.1 Repo đã thử gì gần giống (số đo thật)

**Gần EA (1) – bám trend:**
- v19b XU_HƯỚNG_DÀI (Donchian55, MA50/200): bộ 1 42 ô, 23,8 % ô lãi nửa kiểm, trung vị kiểm −2,4 %; bộ 2 33 ô, 27,3 %, −2,91 %, p tốt nhất 0,037. Holm 0.
- v22 XU_HƯỚNG_DÀI: 284 ô, 4 ô lãi cả 2 nửa sau phí. v22 ĐỘNG_LƯỢNG 284 ô, 12 ô.
- v23 TRENDBREAKER H4: 8/10 chuỗi lãi nửa kiểm, trung vị +2,1 %; D1 p 0,10; PAXG_ST D1 (Supertrend) +6,6 % nửa kiểm, p 0,26 (v24).
- v18 “bắt cú chạy mạnh” (breakout 24 bar, straddle): 84 ô, 0 sống, trung vị kiểm −18,5 % với TP nhỏ.
- v17 đòn bẩy US500 + lọc MA200: 2,5 %/năm (1×), DD 40 %.
- **Nhồi lệnh (pyramid) thuận trend: CHƯA từng thử** trước lần đo này. Repo chỉ có nhồi khi LỖ (lưới/martingale): v18 B5 cháy 3/7 cặp; PMG grid.

**Gần EA (2) – đánh hồi sau cú quét:**
- v29 R3 Triple RSI, R5 3 ngày giảm, R1 RSI5<30+SMA200, R6 IBS (xem mục 3): IBS US500/US100 là hệ duy nhất qua Holm.
- v18 B4 “kiệt sức-đảo chiều” FX H1: trung vị kiểm ≈ −0,1…−2,7 %, 0 sống.
- v11 SPX_3TUAN_GIAM: p_holm 1,0. v21 lệch ≥k·ATR khỏi EMA: tỷ lệ chạm lại EMA20 D1 (k=2) 87 % vs 76 % ngẫu nhiên, nhưng giao dịch 0 qua Holm.
- MRZ (z50 ±2) D1: gần nhất là AUDUSD (mục 1).

## 6.2 Thiết kế EA (1) — BAM_TREND_MANH

- **Phát hiện trend (cả 4 phải đúng tại nến D1 vừa đóng):**
  1. Donchian: close > đỉnh 55 nến trước (mua) / < đáy 55 nến (bán).
  2. ADX14 > 25.
  3. Độ dốc MA: SMA50 hôm nay > SMA50 10 nến trước (mua), ngược lại cho bán.
  4. (tuỳ chọn, chưa đo) ATR breakout: biên độ nến tín hiệu ≥ 1,5·ATR14 — để chỉ bắt “sóng lớn”.
- **Bộ lọc:** spread hiện tại ≤ 2× trung vị; không vào ở 00h server (spread 00h đắt 3–5× — KN 3), vào 02h; tuỳ chọn lọc tuần W1 cùng chiều (EMA20 W1).
- **Quản lý lệnh:** vào open nến kế; dừng đầu 3·ATR14; **trailing chandelier 3·ATR** từ giá đóng tốt nhất; **nhồi**: thêm 1 đơn vị mỗi khi giá đi thêm +1·ATR(lúc vào) so với đơn vị trước, tối đa 4 đơn vị; mọi đơn vị dùng chung stop trailing; không chốt lời cố định. Rủi ro mỗi đơn vị ≤ 0,5 % vốn để 4 đơn vị không quá 2 %.
- Tài sản: vàng, dầu, chỉ số, FX (đề xuất ưu tiên dầu theo số đo dưới).

## 6.3 Thiết kế EA (2) — DANH_HOI_SAU_QUET

- **Phát hiện cú quét (một trong các máy, tại nến D1 đóng):**
  - `atr3`: close − close[3 nến trước] ≤ −3·ATR14 (mua) / ≥ +3·ATR14 (bán).
  - `z25`: z-score 20 nến ≤ −2,5 / ≥ +2,5.
  - `dn4`: ≥ 4 nến đóng giảm liên tiếp / tăng liên tiếp.
  - `gap`: gap mở cửa ≤ −1·ATR / ≥ +1·ATR.
  - `atr3_ma200`: atr3 nhưng chỉ chiều mua khi close > MA200.
- **Bộ lọc:** (đề xuất, mục 5) MA200, IBS<0,2, RSI2<10; spread ≤ 2× trung vị.
- **Quản lý lệnh:** vào open nến kế, **chốt nhanh TP = +0,5·ATR14**, SL = 2·ATR14, giữ tối đa 5 nến (hết hạn đóng ở close). Nếu chạm SL và TP cùng nến: tính SL trước (giả định xấu nhất).

## 6.4 Đo nhanh (MÔ PHỎNG, 14/10/2026)

Dữ liệu: Yahoo D1 2004 → 10/2026 (`/workspace/du_lieu_ngay/v24`, ngoài git), 15 mã có trong bảng phí `phi_xm_that.BANG` (XM **Ultra Low**, hậu tố `#`):
FX 7 cặp (EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD); “vàng” = GC_F + **SI_F (bạc, spread 8,2 bps)**; dầu = CL_F; chỉ số = SPX, NDX, DJI, DAX, FTSE.
Phí mỗi lệnh khứ hồi = spread trung vị H1 Ultra Low (bps, 0,52–8,19) + 1 bps trượt; swap = 0 (nhóm `#` DISABLED — chưa chắc khi chạy thật); hoa hồng CHƯA ĐO ĐƯỢC.
Giai đoạn 1 = trước 2015-04-01, giai đoạn 2 = sau. Chưa đếm Holm; đây là đo khám phá, **không phải kết quả qua cổng**.
Hạn chế: GC_F/CL_F là hợp đồng tương lai liên tục (có bước nhảy khi đáo hạn) — kết quả vàng/dầu có thể lệch; FX Yahoo OHLC đã biết là kém (KN 20). Script: `/workspace/scratch/do_2ea.py` (ngoài repo).
“Tần suất” = số sự kiện / tài sản / năm. “Lãi TB” = bps/lệnh sau phí (EA 1 có nhồi: cộng bps của mọi đơn vị). “MFE” = mức hồi thuận lợi tối đa trung bình trong ≤ 5 nến (bps), trước phí.

**EA (1) bám trend (Donchian55 + ADX>25 + dốc SMA50, trailing 3 ATR):**

| Lớp | Bản | Lệnh (tần suất/năm) | Win % | Lãi TB bps | PF | GĐ1: win / TB / PF | GĐ2: win / TB / PF |
|---|---|---|---|---|---|---|---|
| Dầu | không nhồi | 56 (2,5) | 32,1 | +85,7 | 1,18 | 33,3 / +219 / 1,63 | 31,0 / −38 / 0,94 |
| Dầu | **nhồi tối đa 4** | 56 (2,5) | 25,0 | **+405,6** | **1,42** | 29,6 / +540 / 1,60 | 20,7 / +280 / 1,28 |
| Vàng+bạc | không nhồi | 128 (2,9) | 35,2 | −14,2 | 0,95 | 38,8 / +11 / 1,04 | 31,1 / −42 / 0,87 |
| Vàng+bạc | nhồi | 128 (2,9) | 20,3 | −27,8 | 0,96 | 19,4 / −91 / 0,86 | 21,3 / +41 / 1,07 |
| Chỉ số | không nhồi | 283 (2,6) | 34,6 | −60,8 | 0,72 | 34,0 / −70 / 0,69 | 35,3 / −51 / 0,76 |
| Chỉ số | nhồi | 283 (2,6) | 16,6 | −261,9 | 0,54 | 16,7 / −242 / 0,56 | 16,5 / −285 / 0,52 |
| FX | không nhồi | 307 (2,0) | 37,1 | −12,5 | 0,92 | 42,2 / +51 / 1,32 | 32,0 / −76 / 0,45 |
| FX | nhồi | 307 (2,0) | 23,1 | +3,3 | 1,01 | 30,5 / +219 / 1,66 | 15,7 / −214 / 0,29 |

→ Chỉ **dầu có nhồi** dương ở cả hai giai đoạn (PF 1,60 / 1,28), nhưng chỉ 56 lệnh (1 mã) — p, Holm: CHƯA ĐO ĐƯỢC. Nhồi khuếch đại: tốt ở dầu, rất xấu ở chỉ số (chỉ số tăng chậm, hay giật ngược). FX: trend tốt GĐ1, sập GĐ2. Khớp kinh nghiệm “x9 dầu” của Anh nhưng mẫu quá nhỏ để kết luận.

**EA (2) đánh hồi (TP 0,5 ATR, SL 2 ATR, giữ ≤5 nến):**

| Máy | Lớp | Lệnh (tần suất/năm) | Win % | Lãi TB bps | PF | MFE TB bps | GĐ1: win / TB / PF | GĐ2: win / TB / PF |
|---|---|---|---|---|---|---|---|---|
| atr3 | Chỉ số | 327 (3,0) | 73,1 | −5,1 | 0,91 | 133 | 69,7 / −21 / 0,70 | 75,4 / +5,7 / 1,11 |
| **atr3_ma200** (chỉ mua) | **Chỉ số** | 132 (1,2) | **81,1** | **+9,1** | **1,22** | 120 | 75,9 / −1,2 / 0,97 | 85,1 / +17,2 / 1,46 |
| atr3 | Dầu | 30 (1,4) | 73,3 | +42,7 | 1,35 | 419 | 64,3 / −19 / 0,86 | 81,2 / +96,5 / 1,85 |
| atr3 | FX | 164 (1,1) | 72,0 | −4,6 | 0,90 | 95 | 70,6 / −8,3 / 0,83 | 76,3 / +7,7 / 1,23 |
| atr3 | Vàng+bạc | 362 (8,2) | 61,6 | −58,5 | 0,46 | 130 | 65,5 / −48 / 0,51 | 56,8 / −71 / 0,40 |
| z25 | Chỉ số | 450 (4,1) | 73,8 | −3,2 | 0,94 | 113 | 68,8 / −14,5 / 0,78 | 77,3 / +4,9 / 1,11 |
| z25 | **Dầu** | 87 (4,0) | 74,7 | **+38,3** | **1,35** | 328 | 68,4 / +2,7 / 1,03 | 79,6 / +65,9 / 1,54 |
| z25 | FX | 610 (4,0) | 70,7 | −0,8 | 0,98 | 74 | 66,9 / −7,0 / 0,84 | 73,6 / +4,1 / 1,14 |
| z25 | Vàng+bạc | 204 (4,6) | 59,3 | −64,9 | 0,43 | 129 | 56,1 / −59 / 0,48 | 61,5 / −69 / 0,39 |
| dn4 | Chỉ số | 1.752 (15,9) | 72,3 | −0,6 | 0,99 | 105 | 74,1 / +1,2 / 1,02 | 70,6 / −2,3 / 0,95 |
| dn4 | Dầu | 331 (15,1) | 71,3 | −18,4 | 0,86 | 234 | 72,4 / −7,4 / 0,94 | 70,3 / −28 / 0,81 |
| dn4 | FX | 2.442 (16,1) | 69,8 | −1,1 | 0,97 | 69 | 72,0 / −1,3 / 0,96 | 68,0 / −0,9 / 0,97 |
| dn4 | Vàng+bạc | 658 (15,0) | 67,0 | −30,8 | 0,64 | 128 | 65,8 / −38 / 0,58 | 68,1 / −25 / 0,69 |
| gap | Chỉ số | 360 (3,3) | 70,8 | −6,0 | 0,90 | 123 | 74,7 / +5,4 / 1,09 | 69,4 / −10,2 / 0,84 |
| gap | Dầu | 22 (1,0) | 68,2 | +74,0 | 1,42 | 443 | 55,6 / −117 / 0,51 | 76,9 / +206 / 2,54 |
| gap | FX | 2.145 (14,1) | 67,5 | −4,5 | 0,87 | 62 | 67,1 / −6,4 / 0,83 | 67,7 / −3,5 / 0,89 |
| gap | Vàng+bạc | 662 (15,1) | 66,6 | −29,9 | 0,64 | 137 | 66,0 / −32 / 0,64 | 67,5 / −27 / 0,64 |

→ **Win rate “hồi nhẹ” cao thật (67–85 %)**, nhưng TP 0,5 ATR / SL 2 ATR nên một lệnh thua ăn 4 lệnh thắng; phần lớn ô PF < 1 sau phí. Dương cả 2 giai đoạn chỉ có: **z25 trên dầu** (PF 1,03 / 1,54) — các ô khác GĐ1 âm. Ô gần nhất cho chỉ số: atr3 + MA200 (win 81 %, PF 1,22, GĐ1 hoà vốn). Vàng+bạc âm mọi máy (nghi do bạc spread 8 bps + bước nhảy đáo hạn GC_F → cần đo lại riêng GOLD trên dữ liệu MT5: CHƯA ĐO ĐƯỢC). MFE trung bình (dầu 328–443 bps, chỉ số 105–133 bps) lớn hơn nhiều TP 0,5 ATR → TP có thể nới (chưa đo, phải tiền đăng ký).
Chưa đo: H1/H4, dữ liệu MT5 XM, p-value/Holm, win rate R3/IBS ghép với 2 EA.

## 6.5 Việc tiếp cho 2 EA (đề xuất, tiền đăng ký trước)
1. EA (1): dầu + Brent (BZ_F) + nhóm hàng hoá có xu hướng (HG, NG) với cùng cấu hình cố định để tăng n; đo GOLD.i# riêng (không trộn bạc) trên dữ liệu MT5.
2. EA (2): z25 / atr3 + MA200 + IBS<0,2 trên US500/US100/OILCash; thử TP 1·ATR thay 0,5 (1 ô).
3. Viết EA MQL5 chỉ sau khi ô Python qua tầng 2 giai đoạn + áp lực ×1,5 spread; chạy tester máy nhà.

# 7. Đề xuất làm The Brain hiệu quả hơn

**Nguồn đã cho kết quả tốt (theo số):**
- **Luật công bố/học thuật có lâu đời** (lịch S&P: Halloween, đầu-cuối tháng, Santa — vòng 10–16): 2 hệ qua Holm.
- **X — tài khoản tự chạy lại có phí** (@EmpiricaLab, @QuantifiedStrat, v29): ~380 bài → 8 luật → **2 hệ qua Holm** (IBS US500/US100) + nhiều ô lãi cả 2 nửa. Năng suất cao nhất trên mỗi lệnh gọi.
- **Hệ đơn giản tự thiết kế D1** (MRZ, RSI trailing): near-miss tốt nhất (MRZ AUDUSD p 0,008; MT5 113/117 lãi IS+OOS).

**Nguồn gần như vô ích (theo số):**
- **Kho EA GitHub/MQL5 qua bộ đọc**: 3.204 tệp → 85 EA dịch được (3,57 %) → v25 396 ô **0 sống**; v18 29 EA → dịch 0. Phần lớn là công cụ/lưới.
- **TradingView/fxblue/QuantPedia/SSRN**: 403/Cloudflare từ box → CHƯA ĐO ĐƯỢC; v23 bản dịch theo mô tả 1.175 ô, 0 sống.
- **Tín hiệu MQL5 Signals** (`signal_ho_so.json`): nhiều là lưới/DCA (win 68–76 % nhưng nhồi khi lỗ).
- **Quét lưới rộng khung nhỏ (M5–M30)**: phí 35–50 % biên độ nến → âm (v22); Holm cộng dồn đã > 13.000 nên quét rộng chỉ làm khó qua cổng hơn.
- **Lọc trạng thái (v20), nến/phiên/SMC**: nhóm tệ nhất.

**Đổi hướng đề xuất:**
1. Dồn ngân sách vào **sự kiện hiếm D1 trên chỉ số Mỹ + dầu** (IBS, z, cú quét) và **trend dầu có nhồi**; mỗi vòng ≤ 10 ô tiền đăng ký.
2. Nguồn: ưu tiên X tài khoản hạng A + sách/paper kinh điển (Connors RSI2, Turtle) — luật rõ, dịch nhanh; **dừng** đầu tư vào bộ đọc EA kho (năng suất 0 hệ sống).
3. Gộp đa tài sản cùng cấu hình để tăng n thay vì thêm bộ lọc (KN 18); luôn có giai đoạn 2 + áp lực ×1,5 spread.
4. Chuyển ứng viên sang **MT5 dữ liệu XM** sớm (IBS US500/US100 chưa có EA) — dữ liệu Yahoo FX/futures có lỗi OHLC/đáo hạn.
5. Ghi **win rate + MFE** vào mọi json vòng sau (hiện thiếu, nên nhiều ô CHƯA ĐO ĐƯỢC).
