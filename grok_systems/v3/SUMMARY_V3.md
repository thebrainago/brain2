# SUMMARY_V3 (FINAL pass, 28/11/2026 11:10 UTC+7) — mô phỏng PYTHON bảo thủ, CHƯA phải MT5 (trừ ghi chú)
## 1. Kiểm kê dữ liệu máy nhà (chỉ đọc)
| Nguồn | Nội dung | Khoảng thời gian | Dùng được? |
|---|---|---|---|
| FxaurumRithmic\TickDb (*.tick, có aggressor B/S) | ESZ6 2.3GB, NQZ6 1.2GB, GCZ6 329MB, GCG7, BTC/MBT, ESH7/NQH7/MESZ6/MNQZ6 (1 ngày) | 20/08–27/11 | CÓ (nguồn chính) |
| E:\GrokWork\research_expand_20261120\scid (Sierra .scid, bid/ask vol) | ESU6 63M tick (29/03–18/09), GCQ6 4.7M (27/02–26/08), GCZ6 2.9M, MESZ6, MNQZ6, SIZ6, CLF7 | 03/2026–20/11 | CÓ → kéo dài lịch sử vàng/ES về 01/06 (OOS thật) |
| FlowDb / BarDb | 97 file FlowDb, bar | ngắn | không cần |
| OptionsDb GCZ6 (.fxop 9.6GB) | quyền chọn vàng, chỉ 19–20/11 | 2 ngày | KHÔNG đủ lịch sử để backtest GEX/walls |
| mbo_data (MBO ES/NQ/GC jsonl.gz) | chỉ 28/11 (~100MB) | 1 ngày | KHÔNG đủ để backtest iceberg/DOM; đang ghi log để chấm sau |
| fxa_levels_hist, level_logger, mbo_shadow, walls_history | log mức giá vài ngày | 17/11–28/11 | quá ngắn |
| XM M1 US500/GOLD | 01/06 → 26/11 | 6 tháng | CÓ |
CPU máy nhà ~70–78%: tiến trình ăn CPU nhiều nhất là FxaurumRithmicApi_v1.13.5 (PID 5976, CPU-time 36.9k giây), rồi Fxaurum Platform (2 PID), Defender MsMpEng, chrome. Không kill gì.
## 2. Phát hiện kỹ thuật quan trọng
- **Lệch múi giờ XM tuần 25–31/10/2026**: v1/v2 đổi giờ server bằng NY+7h, nhưng XM theo EU DST (đổi 25/10) còn Mỹ đổi 01/11 → 1 tuần flow lệch 1 giờ (tương quan ES–CFD tụt về ~0). v3 dùng Europe/Athens → tương quan 0.95–0.99 cả 6 tháng.
- v1/v2 dùng ESZ6/GCZ6 mỏng trước ~10/09 (ES Z6 chỉ 6.8k hợp đồng/tháng 8). v3 ghép hợp đồng theo khối lượng ngày: ES = ESU6 (121 ngày) → ESZ6 (54), Gold = GCQ6 (107) → GCZ6 scid (16) → GCZ6 TickDb (72).
- Kiểm tra gương (mirror) gần như vô nghĩa với hệ đối xứng (kết quả y hệt). v3 thay bằng: tách Long/Short, drift-detrend (−1×drift), đảo xu hướng (−2×drift), delay 2 nến.
- Giỏ vàng không SL rất dễ "qua ải": hệ ngẫu nhiên (placebo) cũng dương ở 23% cấu hình → bắt buộc xét percentile placebo, không chỉ net>0.
## 3. OOS thật cho v2 (01/06–19/08, chưa từng dùng để chọn) — Python
| Hệ | A: 01/06–19/08 | B: 20/08–26/11 | 6 tháng |
|---|---|---|---|
| US500 v2_c1 (2.0 lot, sw_fade 1.8, ADX>20, LD/NY, hedge .5) | +758, DD 8.8% (T6 +606, T7 +327, T8 −175) | +1,696, DD 4.5% | +2,782, DD 8.8% |
| US500 v2_c3 (1.0 lot) | +478, DD 4.9% | +884, DD 2.7% | +1,555, DD 4.9% |
| XAU v2_c3 (sweep fade, hedge .5) | +1,937, DD 6.8% (30k) | +2,838, DD 3.1% | +4,775, DD 6.8%, 6/6 tháng dương |
| XAU v2_c1 (VWAP>3ATR) | −214, DD 16.0% (T8 −4,096 treo giỏ) | +4,970, DD 6.9% | +7,691, DD 22.8% → mong manh |
=> sweep-fade tiếp tục sống ngoài mẫu cả 2 mã; VWAP-fade vàng v2_c1 KHÔNG qua OOS (giỏ treo tháng 8).
## 4. Thư viện đặc trưng v3 (164 cột/bar): delta/CVD z (5/15/30/60), prints lớn 3 ngưỡng, sweep, footprint imbalance + stacked, ask@high/bid@low, absorption, VWAP z/ATR, ORB/IB/Asia/London range, PDH/PDL, POC/VAH/VAL phiên trước, cross-asset (NQ→ES, ES→GC), tick-time.
## 5. Sàng sự kiện (252 họ × 8 bộ lọc/mã; chi phí 1.5 spread) và scalp SL/TP (40 lưới SL/TP/hold)
- US500: **không có scalp SL/TP nào bền** (chọn trên A → B: trung bình −0.13R, 25% dương; chi phí spread ~0.21 ATR nuốt hết). Placebo trung bình −0.23 ATR.
- XAU: tín hiệu đơn kém bền (select A→B ≈ −0.01R) NHƯNG **đồng pha (2 tín hiệu khác họ) bền**: chọn trên A → B trung bình +0.081R (top137: +0.223R, 74% dương); chọn trên B → A +0.045R (top164: +0.204R, 74% dương).
- Bộ đồng pha vàng (trung vị min(A,B) qua tham số): 
  1. xlead_fadeself_5_2.5 + big2_mom_30_2.5 : n~87, min(A,B)=+0.28R, 91% biến thể dương (best n=106, +0.88R, PF 2.8, 6/6 tháng, t=5.3)
  2. absorb_mom_30 + emapull NY: +0.27R (94%)
  3. big3_mom_60_2.0 + xlead_fadeself : +0.19R (75%); 4. big3_mom_60_2.0 + emapull NY: +0.19R (81%, n=108 +0.70R); 5. big3_mom_60_2.0 + absorb_mom_30: +0.18R (96%)
  Ý nghĩa: vàng chạy 5 phút mạnh nhưng ES đứng yên và prints lớn (≥8 lot) đi ngược → đánh ngược cú chạy; whale-print momentum (≥25 lot, 60 phút, z>2) trong phiên NY.
- US500 đồng pha: không bền (median min(A,B) âm cho mọi cặp). Chỉ big2_fade_30_1.5 (prints ≥30 lot đánh ngược) NY ADX>20 qua lọc lẻ (n=366 +0.27R, PF 1.30, 6/6 tháng, flip-z 3.7) — chưa qua OOS A/B độc lập.
## 6. Giỏ (basket) battery — vàng (30k)
Bộ qua đủ (A>0,B>0,≥5/6 tháng, spread×2>0, placebo≥95): sw_fade_15_1.8 gt20 ldny (mg: gap8 N4 TP4 không hedge) +5,487 DD 7.0% (A +2,479 B +3,008; detr +5,317, rev +5,304; Exness raw +4,928; placebo 95th, median placebo +2,667); biến thể c3 (+4,775 DD 6.8%, placebo 100th, detr −205!, rev +4,050, delay2 −1,299); emapull NY (+4,196 DD 4%, rev −5,980 → phụ thuộc xu hướng); dz_fade_15_2.0 ldn (+3,856 DD 12%); imb_fade_15_1.5 gt20 ldn (+3,050 DD 7%).
Delay 2 nến làm sập sweep-fade vàng c3 (−1,299) → cần khớp lệnh nhanh (giây), không trễ phút.

## 7. Giỏ US500 battery (1 lot, 10k) — Python
Qua đủ (A>0,B>0, ≥5/6 tháng, spread×2>0, placebo≥95): 
| Hệ | Net | DD | A / B | tháng+ | spread×2 | detrend / reverse | placebo pct |
|---|---|---|---|---|---|---|---|
| sw_fade_15_1.8 ADX>20 LDNY, gap60 N3 TP6 không hedge (u1) | +1,391 | 4.4% | +379 / +848 | 6/6 | +1,027 | +1,299 / +751 | 95 |
| absorb_fade_5_1.5_1.0 NY, gap60 N4 TP8 (u2) | +2,008 | 11.3% | +453 / +1,074 | 5/6 (tháng 8 −421) | +1,376 | +1,344 / +1,194 | 95 |
| sw_fade + absorb_fade_5 W30 ADX>20 NY, gap30 N3 TP4 (u3) | +1,082 | 1.9% | +509 / +573 | 6/6 | +91 (yếu) | +1,070 / +1,068 | 100 |
| sw_fade + big2_fade_30_1.5 W10 LDNY (u4) | +654 | 2.8% | +294 / +360 | 6/6 | +582 | +654 / +550 | 95 |
Không qua: big2_fade_60 NY, vwapz_2.5, sweep_day, big1_mom (placebo thấp hoặc tháng âm).
## 8. MT5 TICK-REAL (100% real ticks, 01/06–27/11/2026, entries CSV giờ Athens) vs Python
| Hệ | MT5 net | MT5 DD(eq) | trades | PF | Python net / DD | nhận xét |
|---|---|---|---|---|---|---|
| XAU x1 sw_fade nh8 (0.03, gap8 N4 TP4) | +5,577 | 6.19% | 461 | 6.61 | +5,487 / 7.3% | KHỚP — top 1 vàng |
| XAU x5 sw_fade+vwapatr W30 nh8 | +5,112 | 6.28% | 423 | 6.54 | +5,036 / 7.3% | khớp |
| XAU x2 sweep c3 hedge (v2_c3 6 tháng) | +3,926 | 4.14% | 537 | 2.95 | +4,775 / 6.8% | Python hơi lạc quan 18%, DD thật thấp hơn |
| XAU x4 dz_fade_15_2.0 LDN nh8 | +3,449 | 11.4% | 286 | 8.61 | +3,856 / 12.0% | khớp, DD cao |
| XAU x3 imb_fade_15_1.5 LDN nh8 | +3,241 | **21.9%** | 268 | 7.18 | +4,427 / 7.1% | **DD MT5 gấp 3 Python → loại** |
| XAU scalp xs1 xlead_fadeself+big2_mom SL8 TP8 hold90 (0.10 lot) | +2,264 | 1.61% | 124 | 1.58 | +1,928 | tốt hơn Python |
| XAU scalp xs2 big3_mom_60+emapull NY SL8 TP13 hold90 | +3,295 | 2.24% | 135 | 1.65 | +3,099 | tốt hơn Python |
| US500 u1 sw_fade nh (1 lot) | +1,423 | 4.12% | 218 | 3.35 | +1,391 / 4.4% | KHỚP — top 1 US500 |
| US500 u2 absorb_fade_5 NY | +2,041 | 9.45% | 253 | 2.75 | +2,008 / 11.3% | khớp |
| US500 u3 sw_fade+absorb_fade W30 NY | +1,152 | 1.89% | 257 | 4.34 | +1,082 / 1.9% | khớp, DD thấp nhất |
| US500 u4 sw_fade+big2_fade | +678 | 2.69% | 112 | 3.38 | +654 / 2.8% | khớp |
| US500 u5 v2_c1 (2 lot, hedge) 6 tháng | +2,550 | 7.97% | 250 | 2.72 | +2,782 / 8.8% | khớp |
| US500 scalp us1 big2_fade_30 NY SL8 TP12 (đối chứng) | +416 | 2.09% | 608 | 1.15 | +25 | ≈0, không phải edge |
MT5 xác nhận Python trong ±20% trên 11/13 hệ (trừ x3 DD và us1); hệ nào Python lạc quan (x3, x2) đã ghi rõ.
## 9. Danh mục song song (Python, giỏ cộng dồn, DD cộng theo từng nến — bảo thủ)
| Danh mục | Net 6 tháng | DD | vốn | tháng+ | Sharpe ngày |
|---|---|---|---|---|---|
| x1 vàng | +5,487 | 7.3% | 30k | 6/6 | 3.05 |
| x1+x3+x4 vàng | +13,769 | 10.6% | 30k | 6/6 | 4.15 |
| u1+u2+u3 US500 | +4,481 | 13.0% | 10k | 5/6 | 2.23 |
| x1+u1 | +6,878 | 5.6% | 40k | 6/6 | 3.43 |
| x2+x1+u5+u1 (c3+nh8, v2_c1+u1; u1≈u5 tương quan 1.0) | +14,436 | 6.0% | 40k | 6/6 | 4.05 |
| x1+x3+x4+u1+u2+u3 | +18,251 | 8.6% | 40k | 6/6 | 4.34 |
Tương quan PnL ngày giữa hệ gold và US500 ≈ 0.0–0.2 (x1–u1 0.09) → ghép chéo tài sản giảm DD mạnh (x1+u1: DD 5.6% trên 40k vs 7.3% trên 30k chỉ vàng). x1–x5 tương quan 0.55 (cùng tín hiệu sweep) nên không cộng.
## 10. Luật ngoài kiểm lại trên data v3 (cách hiểu của tôi, phí 1.5 spread)
| Luật | n | mean R | PF | A / B | tháng+ | kết luận |
|---|---|---|---|---|---|---|
| US500 ORB15 + 1h EMA200 trend, SL giữa range, TP2R | 68 | +0.19 | 1.31 | +0.16 / +0.22 | 3/6 | t=1.07 chưa có ý nghĩa; TP3R +0.33R PF 1.52, 5/6 tháng (t 1.5) |
| XAU ORB15 + EMA200 trend TP2R | 74 | +0.22 | 1.39 | +0.31 / +0.17 | 4/6 | t 1.33; không trend: −0.05 |
| XAU FVG M5 NY 2h TP2R | 326 | +0.09 | 1.17 | −0.10 / +0.25 | 3/6 | chỉ sống sau 20/08 |
| XAU FVG M5 NY 2h + EMA50 1h trend TP1.5R | 225 | +0.17 | 1.36 | −0.10 / +0.39 | 5/6 | t 2.2, nhưng A âm → thiên regime |
=> khớp mức +0.2R của nguồn ngoài nhưng chưa vượt t=2 trừ FVG+trend (A âm); không đưa vào danh sách mạnh.
## 11. Đảo bias (flip) — thử lọc
Lọc "bỏ lệnh ngược chiều trong N phút sau tín hiệu trước" (drop_flip) hoặc "đứng ngoài N phút sau flip" (lock): không cải thiện lợi nhuận; lock 90 phút giảm DD (x1 7.3→2.8%, net 5,487→4,358, tức lợi/DD tốt hơn 2×); x3 drop_flip 240: net 4,427→4,591, DD 7.1→3.0%. Với u1/u2/x4 không có ích. Kết luận: dùng "đứng ngoài 90 phút sau flip" như phanh giảm DD cho x1, không bắt buộc.
## 12. XAU v2_c1 (VWAP-fade) lọc giờ
Trên 6 tháng, vwapatr_3 ADX>20 không hedge: ALL +7,691 DD 22.8%; bỏ UTC 09–12,15–18: +6,510 DD 22.8% (tháng 8 vẫn −3,356); chỉ London 7–12 UTC: +3,070 DD 21.0% (tháng 8 −2,852). Lọc giờ KHÔNG chữa lỗi tháng 8 của c1 trên mẫu 6 tháng (chỉ đúng trên mẫu 20/08–26/11).

## 12b. US500 bsweep (15,480 cấu hình) + battery bổ sung → 4 hệ mới
Đã chạy trên box (bản PC trùng đã dừng đúng PID). Lưới sàng không phân biệt tốt (placebo), nên chạy battery: qua đủ (A>0,B>0,≥5/6 tháng, spread×2>0, placebo≥95):
| Hệ (mg) | Net 1 lot | DD | A / B | tháng+ | sx2 net | detr / rev | placebo |
|---|---|---|---|---|---|---|---|
| u6 dz_mom_5_1.5 all (gap60 N4 TP8) | +2,767 | 5.0% | +823 / +1,693 | 6/6 | +640 | +2,043 / +1,597 | 100 (nhưng short +1,969, long +431: lệch) |
| u7 sw_fade_15_1.5 all (gap60 N4 TP8) | +2,339 | 7% | +712 / +1,441 | 6/6 | +1,979 | +2,175 / +1,445 | 100 — cân bằng 2 chiều |
| u8 stk_fade_15_2 LDNY (chỉ short, long +3) | +2,640 | 9% | +828 / +1,459 | 5/6 | +1,451 | +1,693 / +1,636 | 100 — lệch 1 chiều |
| u9 imb_mom_15_1.5 LDNY (gap30 N3 TP4) | +2,075 | 6% | +659 / +1,271 | 5/6 | +1,786 | +1,920 / +1,287 | 95 |
(Họ mới: stacked-imbalance fade, delta-z momentum, imbalance momentum.)

## 13. LOT-SCALE từng hệ (Python bảo thủ, DD<17% vốn, spread×2 DD<25%; XAU vốn 30k, US500 vốn 10k; tuyến tính theo lot rồi làm tròn bước lot)
| Hệ | Lot L0 | Net 6th | DD | DD spread×2 | Net spread×2 | A (6/1–19/8) | B (20/8–26/11) | tháng+ | PF ngày |
|---|---|---|---|---|---|---|---|---|---|
| x1 XAU sweep_fade 15m ADX>20 LDNY (gap8 N4 TP4 không hedge) | 0.06 | 10,973 | 14.7% | 21.2% | 7,799 | 4,958 | 6,016 | 6/6 | 2.47 |
| x2 XAU sweep_fade c3 hedge | 0.07 | 11,142 | 15.8% | 16.4% | 10,999 | 4,519 | 6,623 | 6/6 | 2.21 |
| x4 XAU dz_fade_15 LDN | 0.04 | 5,141 | 16.0% | 16.1% | 5,135 | 585 | 4,555 | 5/6 | 2.01 |
| x5 XAU sweep+VWAP W30 | 0.06 | 10,072 | 14.7% | 21.2% | 6,828 | 4,460 | 5,612 | 6/6 | 1.69 |
| xs1 XAU scalp xlead_fadeself+big2_mom (SL8 TP8) | 0.89 | 17,162 | 16.9% | 17.3% | 17,383 | 10,280 | 6,881 | 5/6 | 2.01 |
| xs2 XAU scalp big3_mom+emapull NY (SL8 TP13) | 0.63 | 19,523 | 16.9% | 17.7% | 17,750 | 10,765 | 8,758 | 5/6 | 2.48 |
| u1 US500 sweep_fade LDNY (gap60 N3 TP6) | 3.8 | 5,287 | 16.7% | 16.8% | 5,003 | 1,441 | 3,846 | 6/6 | 1.47 |
| u2 US500 absorb_fade_5 NY (gap60 N4 TP8) | 1.5 | 3,012 | 16.9% | 17.0% | 2,652 | 679 | 2,333 | 5/6 | 1.23 |
| u3 US500 sweep+absorb W30 NY (gap30 N3 TP4) | 8.0 | 8,656 | 15.4% | 24.1% | 8,477 | 4,071 | 4,586 | 6/6 | 3.18 |
| u5 US500 v2_c1 hedge | 3.8 | 5,287 | 16.7% | 16.8% | 5,003 | 1,441 | 3,846 | 6/6 | 1.47 |
| u6 US500 dz_mom_5_1.5 (mới) | 1.1 | 3,044 | 5.7% | 23.1% | 1,460 | 905 | 2,139 | 6/6 | 1.65 |
| u7 US500 sweep_fade_15_1.5 all (mới) | 2.5 | 5,847 | 16.7% | 21.8% | 4,612 | 1,780 | 4,067 | 6/6 | 1.61 |
| u8 US500 stk_fade_15_2 LDNY (mới, chỉ short) | 1.8 | 4,752 | 16.6% | 24.9% | 3,186 | 1,490 | 3,262 | 5/6 | 1.54 |
| u9 US500 imb_mom_15_1.5 LDNY (mới) | 2.8 | 5,810 | 16.5% | 16.6% | 5,454 | 1,845 | 3,965 | 5/6 | 1.47 |

Lưu ý: scalp xs1/xs2 trong Python chỉ tính DD theo lệnh đóng (không có DD trong lệnh) nên LẠC QUAN; số thật lấy theo MT5 (mục 15). Giới hạn lot an toàn gap: gold L0≤0.12, US500 ≤5 (u3 ≤8).

## 14. DANH MỤC chéo/song song tối ưu lot (DD joint<17%, sx2<25%; vốn = 30k gold + 10k US500 nếu có cả hai)
| Danh mục | Lot từng hệ | Net | DD | DD sx2 | Net sx2 | A / B | Net theo tháng | PF ngày / Sharpe | Mức an toàn ½ lot: Net / DD | OOS: lot tối ưu trên A → B net / DD | lot tối ưu trên B → A net / DD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GOLD_all (vốn 30,000) | x1:0.05, x2:0.05, x4:0.05, x5:0.01, xs1:0.06, xs2:0.05 | 27,914 | 16.8% | 20.4% | 24,493 | 10,382 / 17,532 | [6621, 4662, 1994, 6449, 3323, 4865] | 2.61 / 4.66 | 13,957 / 8.4% | 50,896 / 53.3% | 29,184 / 14.5% |
| GOLD_core (vốn 30,000) | x1:0.05, x4:0.05, xs1:0.33, xs2:0.73 | 44,555 | 16.9% | 17.1% | 39,930 | 21,149 / 23,407 | [5811, 7844, 11994, 1102, 7323, 10481] | 2.96 / 5.44 | 22,278 / 8.4% | 40,543 / 41.6% | 22,131 / 8.6% |
| US_all (vốn 10,000) | u3:1.4, u6:1.3, u7:1.4, u8:0.4 | 9,443 | 15.3% | 23.7% | 6,500 | 3,110 / 6,333 | [1872, 1579, 606, 1448, 1386, 2551] | 2.0 / 3.87 | 4,721 / 7.7% | 7,027 / 8.6% | 6,987 / 37.5% |
| US_core (vốn 10,000) | u1:0.4, u2:0.2, u6:1.2, u7:1.3 | 7,319 | 14.8% | 23.7% | 4,872 | 2,155 / 5,164 | [1483, 1074, 462, 1062, 1035, 2203] | 1.77 / 3.07 | 3,660 / 7.4% | 6,219 / 11.6% | 5,340 / 38.2% |
| CROSS_all (vốn 40,000) | x1:0.05, x2:0.12, x4:0.08, x5:0.02, xs1:0.38, xs2:1.0, u3:7.4, u6:2.3, u7:5.0, u8:1.8, u9:2.9 | 117,035 | 17.0% | 22.9% | 102,450 | 48,632 / 68,403 | [20095, 20453, 19145, 13469, 15726, 28147] | 3.18 / 6.77 | 58,518 / 8.5% | 87,894 / 55.9% | 50,445 / 20.7% |
| CROSS_core (vốn 40,000) | x1:0.05, x4:0.07, xs1:0.57, xs2:1.0, u1:2.6, u2:0.2, u6:2.8, u7:5.0 | 83,582 | 16.9% | 24.9% | 71,511 | 35,768 / 47,814 | [12515, 13855, 18272, 3873, 14289, 20778] | 2.95 / 5.91 | 41,791 / 8.5% | 64,009 / 39.0% | 35,326 / 14.4% |
| CROSS_x1_u1 (vốn 40,000) | x1:0.09, u1:3.3 | 21,051 | 17.0% | 22.9% | 16,044 | 8,688 / 12,363 | [5377, 3599, 1513, 3494, 2760, 4307] | 2.15 / 3.44 | 10,525 / 8.5% | 17,048 / 22.8% | 9,332 / 5.6% |
| CROSS_sw_only (vốn 40,000) | x1:0.09, x2:0.1, u1:1.0, u7:1.0 | 36,107 | 16.3% | 22.5% | 30,574 | 14,984 / 21,123 | [9651, 5498, 2841, 6867, 3622, 7628] | 2.37 / 3.9 | 18,054 / 8.2% | 35,546 / 21.5% | 20,640 / 18.9% |

**CẢNH BÁO OOS**: lot tối ưu chỉ trên giai đoạn A (01/06–19/08, DD thấp) khi áp sang B (20/08–26/11) cho DD 40–56% với danh mục có vàng — DD "17%" phụ thuộc mạnh vào giai đoạn; lot tối ưu trên B áp sang A an toàn (DD 6–21%). Khuyến nghị dùng mức ½ lot (DD ~8%) cho tiền thật/demo ban đầu; mức 17% chỉ là trần mô phỏng.

## 15. MT5 TICK-REAL cho các hệ đã scale lot (100% real ticks, 01/06–27/11/2026; XAU vốn 30k, US500 vốn 10k)
| Job | Hệ | Lot | MT5 net | MT5 DD | PF | trades | Python net (tuyến tính theo lot) | Python DD |
|---|---|---|---|---|---|---|---|---|
| v3b_A_u1_10 | u1 | 1.0 | 1,423 | 4.12% | 3.35 | 218 | 1,391 | 4.4% |
| v3b_A_u7_10 | u7 | 1.0 | 2,364 | 6.23% | 3.15 | 295 | 2,339 | 6.7% |
| v3b_A_x1_009 | x1 | 0.09 | 16,732 | 14.2% | 6.61 | 461 | 16,460 | 22.0% |
| v3b_A_x2_010 | x2 | 0.1 | 13,603 | 12.07% | 3.16 | 527 | 15,918 | 22.6% |
| v3b_B_u1_26 | u1 | 2.6 | 3,701 | 9.89% | 3.35 | 218 | 3,617 | 11.4% |
| v3b_B_u2_02 | u2 | 0.2 | 407 | 2.14% | 2.75 | 253 | 402 | 2.3% |
| v3b_B_u6_28 | u6 | 2.8 | 7,823 | 12.51% | 3.61 | 354 | 7,749 | 14.5% |
| v3b_B_u7_50 | u7 | 5.0 | 11,808 | 24.06% | 3.15 | 295 | 11,694 | 33.4% |
| v3b_B_x1_005 | x1 | 0.05 | 9,297 | 9.36% | 6.61 | 461 | 9,144 | 12.2% |
| v3b_B_x4_007 | x4 | 0.07 | 8,050 | 24.71% | 8.61 | 286 | 8,996 | 28.1% |
| v3b_B_xs1_057 | xs1 | 0.57 | 13,584 | 5.61% | 1.63 | 116 | 10,991 | 10.8% |
| v3b_B_xs2_100 | xs2 | 1.0 | 36,199 | 16.31% | 1.8 | 115 | 30,988 | 26.8% |
| v3b_C_u7_30 | u7 | 3.0 | 7,092 | 16.29% | 3.15 | 295 | 7,016 | 20.0% |
| v3b_C_x4_004 | x4 | 0.04 | 4,600 | 14.91% | 8.61 | 286 | 5,141 | 16.0% |
| v3b_C_xs2_060 | xs2 | 0.6 | 17,474 | 13.47% | 1.56 | 125 | 18,593 | 16.1% |
| v3b_S_u1_38 | u1 | 3.8 | 5,409 | 13.67% | 3.35 | 218 | 5,287 | 16.7% |
| v3b_S_x1_006 | x1 | 0.06 | 11,154 | 10.73% | 6.61 | 461 | 10,973 | 14.7% |

Nhận xét MT5 vs Python ở lot lớn: DD MT5 thấp hơn Python (Python bảo thủ hơn) ở cả basket và scalp; net MT5 scalp cao hơn Python (xs1 +13,584 vs 10,991; xs2 +36,199 vs 30,988). Các mức vượt trần: x4 0.07 (DD 24.7%), u7 5.0 (24.1%) → phải hạ (x4 0.04 → 14.9%, u7 3.0 → 16.3%).

## 16. KẾT LUẬN LOT & DANH MỤC (MT5-verified từng thành phần; DD joint chỉ đo bằng Python vì MT5 không cho gộp 2 mã)
**Lot khuyến nghị từng hệ (MT5 DD ≤ ~15%, đã kiểm trên tick thật):**
| Hệ | Lot | MT5 net 6th | MT5 DD | Vốn |
|---|---|---|---|---|
| XAU x1 sweep_fade LDNY | 0.09 | +16,732 | 14.2% | 30k |
| XAU x2 sweep c3 hedge (hedge% theo lot) | 0.10 | +13,603 | 12.1% | 30k |
| XAU x4 dz_fade LDN | 0.04 | +4,600 | 14.9% | 30k |
| XAU xs1 scalp SL8 TP8 | 0.57 | +13,584 | 5.6% | 30k |
| XAU xs2 scalp SL8 TP13 | 0.6 / 1.0 | +17,474 / +36,199 | 13.5% / 16.3% | 30k |
| US500 u1 sweep_fade LDNY | 2.6 / 3.8 | +3,701 / +5,409 | 9.9% / 13.7% | 10k |
| US500 u6 dz_mom | 2.8 | +7,823 | 12.5% | 10k |
| US500 u7 sw_fade_1.5 | 3.0 | +7,092 | 16.3% | 10k |
| US500 u2 absorb_fade | 0.2 | +407 | 2.1% | 10k |
**Danh mục (Python joint, 40k = 30k vàng + 10k US500):**
- PortA (x1 0.09, x2 0.10, u1 1.0, u7 1.0): net +36,107, DD 16.3%, sx2 DD 22.5%, A +14,984 / B +21,123, 6/6 tháng dương, PF ngày 2.37, Sharpe 3.9. MT5 tổng thành phần: +34,122 (x1 16,732 + x2 13,603 + u1 1,423 + u7 2,364).
- PortB (x1 .05, x4 .07, xs1 .57, xs2 1.0, u1 2.6, u2 .2, u6 2.8, u7 5.0): net +83,582, DD 16.9%, sx2 DD 24.9%, A +35,768 / B +47,814, 6/6 tháng dương, PF ngày 2.95. MT5 tổng thành phần +90,869 (vàng +67,130, US500 +23,739) nhưng DD thành phần MT5 từng hệ (x4 24.7%, xs2 16.3%, u7 24.1%) cộng lại lớn hơn DD joint 16.9% → DD joint chỉ đúng nhờ các hệ thắng lệch pha; KHÔNG có đo joint trên MT5.
- Mỗi tài sản riêng với lot tối ưu (Python): GOLD_core (x1 .05, x4 .05, xs1 .33, xs2 .73) +44,555 DD 16.9%; US_core (u1 .4, u2 .2, u6 1.2, u7 1.3) +7,319 DD 14.8%. Chéo tài sản giảm DD mạnh: x1+u1 (0.09 / 3.3) +21,051 DD 17%.
- Mức "an toàn" = ½ lot: PortB +41,791 DD 8.5%; PortA +18,054 DD 8.2%.
**CẢNH BÁO TRUNG THỰC:**
1. OOS: lot tối ưu trên A (DD thấp) áp sang B cho DD 40–56% (danh mục có vàng) → DD 17% không bền; tối ưu trên B áp sang A ổn (6–21%). Dùng ½ lot cho demo/tiền thật đầu tiên.
2. Chỉ 6 tháng (một nhịp vàng giảm sau 20/08). 1 tháng âm của scalp (Aug −2.2k/−2.3k ở lot tối ưu) → monthly positivity chỉ 5/6 cho xs1, xs2.
3. Gap shock không SL: basket gold 0.09×4 lớp/US500 3×4 lớp mất >50% vốn nếu gap ±10–20% — lot to tăng rủi ro này tuyến tính; chưa test gap trên lot scaled.
4. Multiple-testing: hàng chục nghìn cấu hình, DSR yếu; placebo≥95 và MT5 khớp là bằng chứng chính, không phải bằng chứng thống kê chặt.
5. Scalp xs1/xs2: n=115–125 lệnh, mẫu nhỏ.

## 17. ROUND 4 (28/11 11:40) — Joint-DD MT5, stress, walk-forward
### 17.1 Joint DD đo bằng equity MT5 (dựng từ deals trong report + M1 bid XM, gộp theo timestamp; khớp DD từng hệ của MT5 trong ±1–6%)
| Danh mục | Net MT5 | Joint DD MT5 | % vốn 40k | Tổng DD từng hệ (cộng) | A / B | tháng | Nửa lot (tuyến tính) |
|---|---|---|---|---|---|---|---|
| PortA (x1 .09, x2 .10, u1 1.0, u7 1.0) | +34,122 | 7,028 | **17.6%** (đáy 03/09) | 12,116 | +13,984 / +20,138 | 8,659 / 5,500 / 2,582 / 6,572 / 3,386 / 7,423 | +17,061, DD 8.8% |
| PortB (x1 .05, x4 .07, xs1 .57, xs2 1.0, u1 2.6, u2 .2, u6 2.8, u7 5.0) | +90,870 | 7,161 | **17.9%** (đáy 20/11) | 29,206 | +34,663 / +56,207 | 13,635 / 13,967 / 20,288 / 6,150 / 15,358 / 21,472 | +45,435, DD 9.0% |
| PortC (x1 .09, x2 .10, x4 .04, xs1 .57, xs2 .6, u1 2.6, u2 .2, u6 2.8, u7 3.0) | +85,016 | 8,731 | 21.8% | 28,627 | +35,624 / +49,393 | 6 tháng đều dương | +42,508, DD 10.9% |
=> Joint DD MT5 ≈ Python joint (16.3% / 16.9%), xác nhận hiệu ứng đa dạng hoá (DD joint ≪ tổng DD từng hệ). PortC vượt 20% nên KHÔNG dùng.
### 17.2 Stress ở lot đã scale (Python, % vốn: gold 30k, US500 10k, danh mục 40k)
| Hệ / danh mục (lot) | Base net / DD | spread×2 | spread×2 + slip 1.0 | spread×3 + slip 1.0 | Gap ±5% | Gap ±10% | Gap ±20% |
|---|---|---|---|---|---|---|---|
| PortA | 36,107 / 16.3% | 30,574 / 22.5% | 23,580 / 50.8% | 20,482 / 43.8% | 70% | 126% | 239% |
| PortB | 83,582 / 16.9% | 71,511 / 24.9% | 65,019 / 25.6% | 52,538 / 28.8% | 61% | 108% | 203% |
| x1 0.09 | 16,460 / 22.0% | 11,699 / 31.7% | 11,479 / 31.7% | 10,952 / 31.7% | 43% | 64% | 117% |
| x2 0.10 (hedge) | 15,918 / 22.6% | 15,713 / 23.4% | 8,831 / 75.4% | 6,524 / 27.9% | 69% | 115% | 208% |
| x4 0.04 | 5,141 / 16.0% | 5,135 / 16.1% | 5,152 / 16.1% | 5,115 / 17.3% | 29% | 41% | 66% |
| xs1 0.57 (scalp) | 10,991 / 10.8% | 11,133 / 11.1% | 10,562 / 9.9% | 8,032 / 13.5% | không đổi (SL) | | |
| xs2 0.6 (scalp) | 18,593 / 16.1% | 16,904 / 16.8% | 13,138 / 16.0% | 8,904 / 22.0% | không đổi (SL) | | |
| u1 2.6 | 3,617 / 11.4% | 3,423 / 11.5% | 3,070 / 11.5% | 2,669 / 21.0% | 42% | 72% | 133% |
| u6 2.8 | 7,749 / 14.5% | 3,718 / **58.9%** | 3,358 / 59% | 1,791 / 59% | 47% | 80% | 145% |
| u7 3.0 | 7,016 / 20.0% | 5,535 / 26.2% | 6,268 / 26.3% | 5,937 / 26.5% | 64% | 108% | 195% |
Kết luận stress: (1) mọi hệ basket không SL đều vượt 40% DD chỉ với gap 5% — rủi ro gap là rủi ro chính, lot to không giải quyết được; scalp có SL thì miễn nhiễm gap. (2) u6 (delta momentum) rất nhạy spread (sx2 DD 59%) → không dùng lot lớn. (3) x2 (hedge) vỡ khi slip 1.0 (DD 75%). (4) Python bảo thủ hơn MT5: DD Python ở lot "MT5-calibrated" cao hơn (x1 0.09: Python 22.0% vs MT5 14.2%).
### 17.3 Walk-forward (tune lot trên 2 tháng trước → áp tháng kế; test 4 tháng 08–11)
- Lot tối ưu tune trên 2 tháng RẤT KHÔNG ỔN ĐỊNH (hệ số s nhảy 0.4–4.5; x4 tháng 8 s=4.48 → DD 72%; xs1 tháng 9 lỗ −3,120 DD 17%; PortB tháng 8 s=1.42 → DD 23.5%). Không dùng tuning thích nghi tháng; dùng lot cố định bảo thủ.
- Lot cố định, OOS chain 08–11 (Python): 
| Hệ/danh mục | s=1 (lot đã nêu) OOS DD / sx2 DD / net | s=0.85 | s=0.75 | s=0.5 |
|---|---|---|---|---|
| PortA | 16.3 / 22.5 / 20,866 | 13.9 / 19.1 / 17,736 | 12.3 / 16.9 / 15,649 | 8.2 / 11.2 / 10,433 |
| PortB | 16.9 / 24.9 / 56,742 | 14.4 / 21.2 / 48,231 | 12.7 / 18.7 / 42,557 | 8.5 / 12.5 / 28,371 |
| x1 .09 | 22.0 / 31.7 / 9,023 | 18.7 / 27.0 / 7,670 | 16.5 / 23.8 / 6,768 | 11.0 / 15.9 / 4,512 |
| x2 .10 | 10.4 / 10.6 / 9,461 | 8.8 / 9.0 | 7.8 / 7.9 | 5.2 / 5.3 |
| x4 .04 | 16.0 / 16.1 / 3,266 | 13.6 / 13.7 | 12.0 / 12.0 | 8.0 / 8.0 |
| xs1 .57 | 10.8 / 11.1 / 5,743 | 9.2 / 9.4 | 8.1 / 8.3 | 5.4 / 5.5 |
| xs2 .6 | 16.1 / 16.8 / 15,189 | 13.7 / 14.3 | 12.1 / 12.6 | 8.0 / 8.4 |
| u1 2.6 | 11.4 / 11.5 / 2,284 | 9.7 / 9.8 | 8.6 / 8.6 | 5.7 / 5.7 |
| u6 2.8 | 13.9 / 58.9 / 4,944 | 11.8 / 50.1 | 10.4 / 44.2 | 7.0 / 29.5 |
| u7 3.0 | 13.2 / 13.6 / 4,509 | 11.2 / 11.6 | 9.9 / 10.2 | 6.6 / 6.8 |
### 17.4 BẢNG LOT KHUYẾN NGHỊ (full = DD Python OOS <20% & spread×2 <25% & MT5 joint ≤ ~18%; half = ½ full)
| Mục | FULL lot | Half lot | MT5/Python kỳ vọng (full) |
|---|---|---|---|
| PortA | x1 .09, x2 .10, u1 1.0, u7 1.0 | x1 .045, x2 .05, u1 .5, u7 .5 | MT5 +34,122, joint DD 17.6%; half ≈ +17,061 DD 8.8% |
| PortB (robust ×0.85) | x1 .04, x4 .06, xs1 .48, xs2 .85, u1 2.2, u2 .17, u6 2.4*, u7 4.25 | ×0.5 | Python OOS +48,231, DD 14.4%, sx2 21.2% (*u6 nhạy spread: nên ≤1.4) |
| x1 | 0.07 (Python DD 16.5%; MT5 ~11%) | 0.035 | |
| x2 | 0.10 | 0.05 | |
| x4 | 0.04 | 0.02 | |
| xs1 / xs2 | 0.57 / 0.6 | 0.28 / 0.3 | MT5 DD 5.6% / 13.5% |
| u1 | 2.6 | 1.3 | MT5 +3,701 DD 9.9% |
| u6 | 1.4 (spread nhạy) | 0.7 | |
| u7 | 2.5 | 1.25 | |
Gap: giữ thêm cầu chì tài khoản (cắt giỏ khi lỗ nổi ≥ 25% vốn) — chưa kiểm trên MT5.

## 18. Round 4 — hệ mới (Gold g1/g2, US500 u10/u11), overlay/filter, MT5 verify

### 18.1 Hệ mới tìm được (newsig 216 cấu hình/asset, battery batnew, A/B OOS)
| Hệ | Tín hiệu | Mgmt | Python (lot cơ sở) | A / B | Tháng+ | Ghi chú |
|---|---|---|---|---|---|---|
| g1 Gold | pd_break_flow gt20 ldny | gap4 N3 TP2 | +2,544 / DD 3.1% (0.03) | +1,069 / +1,476 | 6/6 | sx2 +2,488; detrend +1,352; delay2 −8,982 (cần vào lệnh nhanh) |
| g2 Gold | lnor_break_trend gt20 all | gap4 N3 TP2 | +2,619 / DD 2.3% (0.03) | +1,053 / +1,566 | 6/6 | placebo pct 90; delay2 +1,910 |
| u10 US500 | orbd_mom gt20 all | gap30 N3 TP4 | +1,461 / DD ~7% (1 lot) | +730 / +731 | 6/6 | placebo 100; sx +1,068 |
| u11 US500 | asia_fail gt20 ldny | gap60 N4 TP8 | +1,345 / DD 4% (1 lot) | | 6/6 | placebo 100 |
Loại: asia_break_trend, pd_sweep_flow, poc_rev, volspike_fade, vwapflow (A≈0 hoặc tháng âm).

### 18.2 MT5 real ticks (100% real ticks, 01.06–27.11)
| Job | Lot | MT5 net | MT5 DD (equity) | PF | Trades |
|---|---|---|---|---|---|
| g1 pd_break_flow | 0.12 | +10,184 | 10.9% | 9.17 | 421 |
| g2 lnor_break | 0.12 | +10,426 | 8.5% | 7.50 | 424 |
| u10 orbd_mom | 2.5 | +3,721 | 12.5% | 3.63 | 342 |
| u11 asia_fail | 4.3 | +5,574 | **28.8% (vượt cap)** | 3.63 | 162 |
| u11 asia_fail | 2.5 | +3,241 | 18.4% | 3.63 | 162 |
=> Khuyến nghị: g1 0.12, g2 0.12 (nửa lot 0.06), u10 2.5 (nửa 1.2), u11 2.0 (nửa 1.0; 2.5 đã 18.4%).
Python bảo thủ hơn MT5 cho g1/g2 (Python DD 12.4%/9.1% ở 0.12), nhưng u11 MT5 DD > Python (28.8% vs 17%) → luôn tin MT5.

### 18.3 Overlay/filter (hour block, DOW, vol, trend/flow align, veto bằng hệ khác) — KẾT QUẢ ÂM
Chọn trên A có tương quan −0.7 với B; tương quan A→B từng hệ: u1 0.04, u2 −0.01, u6 0.35, u7 −0.09, u9 0.29, x4 −0.61, x6 −0.7, x7 −0.8. MT5 verify 4 overlay (v3d): x4+veto_imb +3,524/DD 2.6% (nhưng base x4 MT5 DD 11.4%), x1+veto_big3 +4,998/2.6%, x6 vol_notlow +3,266 nhưng DD 21.8% (không sửa được), x7 nodow4 +3,483/2.8%. Kết luận: filter giờ/DOW/veto là nhiễu, KHÔNG khuyến nghị.

### 18.4 Danh mục (Python, opt2, lot cap g≤0.12, u10/u11≤5)
| Bộ | Net | DD / sx2 DD | A / B |
|---|---|---|---|
| NEW4 (g1 .12, g2 .12, u10 5, u11 5) | +34,682 | 10.2% / 18.1% | +15,689 / +18,993 (6/6 tháng; sx3 23%, gap5% 63%) |
| BASK_div (x1 .10, x4 .07, g1 .12, g2 .12, u1 5, u7 5, u10 5, u11 5) | +80,617 | 16.7% / 24.8% | |
| ALL_pass (12 hệ) | +129,823 | 16.7% / 24.5% | +56,672 / +73,151 |
Lưu ý: tối ưu trên cùng mẫu; u10/u11 lot 5.0 chỉ là cap Python — dùng lot MT5 ở 18.2 (u10 2.5, u11 2.0) cho thực chiến. Chưa chạy MT5 joint cho NEW4.

### 18.5 Dữ liệu GEX/flip/walls/MBO
Không có lịch sử options/GEX/walls/MBO trong kho Rithmic hiện có → không kiểm chứng được regime filter GEX/flip.

### 18.6 Rủi ro chính
Gap risk (basket không SL vượt 40% DD chỉ với gap 5%); x2 và u6 mong manh với spread/slippage; g1 nhạy độ trễ vào lệnh; walk-forward cho thấy lot tối ưu tune theo 2 tháng không ổn định → dùng lot cố định bảo thủ + bậc nửa lot.

## 19. Round 5 — xử lý rủi ro gap/đuôi, MT5 joint NEW4/PortD, hệ mới g3–g5/u12–u13

### 19.1 Kết luận nhanh
- **Gap cuối tuần/ngày lễ** (rủi ro gap thực tế nhất) xử lý gần như miễn phí bằng **khoá hedge cuối tuần "W"**: thứ Sáu từ 21:00 giờ server (và ngày trước/ngày lễ 03/07, 07/09, 26/11) mở lệnh hedge ngược bằng vị thế ròng của rổ, cấm mở rổ/nhồi trong cửa sổ, thứ Hai đóng hedge. Giữ 91–96% net, gap-5% cuối tuần giảm từ 28–50% xuống = DD thường (8–16%). **MT5 xác nhận**: x1 0.09 W +14,215 / DD 14.5% (Python W +14,827; MT5 không-W +16,732 / DD 14.2%); u10, u11, g1, g2 W khớp Python ≤5%.
- **Gap đột ngột trong phiên (flash 5%)** KHÔNG chặn được bằng stop (gap xuyên stop) — chỉ giảm bằng giảm exposure (lot). Muốn gap-5% (cả 2 tài sản cùng xấu nhất) < 30% phải hạ lot: PortD-G30 (bên dưới).
- **Stop cứng / kill ngày / giảm tầng** đều tốn 20–40% net cho lợi ích nhỏ (xem 19.2) và dựa vào vài sự kiện trong mẫu → KHÔNG khuyến nghị bật mặc định; kill lỗ ngày 6% chỉ như bảo hiểm tuỳ chọn (cắt DD spread×2 PortA 52.8%→25%, giá net −26%).
- **EA mới** `BRAIN_XuLiLenh_r5` (p4/p6, 0 lỗi biên dịch): thêm `InpTuanKhoaGio` (21) và `InpNghiLe` (YYYY.MM.DD cách nhau dấu phẩy) — mặc định TẮT (=0). Nguồn: `v3/r5ea/BRAIN_XuLiLenh_r5.mq5`.

### 19.2 Lưới chính sách rủi ro (Python engine2, lot đã scale, spread×2+slip1 = DD "sx")

**PortA**

| Chính sách | Net | %gốc | DD | DD spread×2+slip1 | Gap-5% bất kỳ lúc | Gap-5% cuối tuần | Gap-10% cuối tuần | A / B |
|---|---|---|---|---|---|---|---|---|
| Gốc (không bảo vệ) | 36,107 | 100% | 16.3% | 50.8% | 70% | 49.7% | 94.6% | 14,984 / 21,123 |
| W: khoá hedge cuối tuần/lễ | 34,029 | 94% | 16.2% | 52.8% | 70% | 16.2% | 16.2% | 14,921 / 19,108 |
| W + layer−1 | 16,126 | 45% | 19.3% | 36.5% | 46% | 19.3% | 19.3% | 13,052 / 3,074 |
| W + stop giá (hsk 1 gap sau lớp cuối) | 7,889 | 22% | 17.0% | 26.2% | 58% | 17.0% | 17.0% | 5,420 / 2,469 |
| W + stop rổ 8% vốn | 23,458 | 65% | 14.3% | 29.4% | 63% | 14.3% | 14.3% | 10,812 / 12,647 |
| W + kill lỗ ngày 6% | 25,427 | 70% | 11.6% | 25.0% | 60% | 11.6% | 11.6% | 11,143 / 14,285 |
| W + stop rổ 8% + kill ngày 6% | 25,429 | 70% | 11.6% | 24.7% | 60% | 11.6% | 11.6% | 11,145 / 14,285 |

**PortB85**

| Chính sách | Net | %gốc | DD | DD spread×2+slip1 | Gap-5% bất kỳ lúc | Gap-5% cuối tuần | Gap-10% cuối tuần | A / B |
|---|---|---|---|---|---|---|---|---|
| Gốc (không bảo vệ) | 67,839 | 100% | 14.5% | 17.1% | 49% | 29.1% | 49.1% | 29,341 / 38,498 |
| W: khoá hedge cuối tuần/lễ | 65,278 | 96% | 15.1% | 16.0% | 49% | 15.1% | 16.3% | 29,260 / 36,018 |
| W + layer−1 | 61,936 | 91% | 14.6% | 24.3% | 42% | 14.6% | 16.3% | 28,678 / 33,258 |
| W + stop giá (hsk 1 gap sau lớp cuối) | 59,120 | 87% | 14.4% | 15.8% | 39% | 14.4% | 16.3% | 29,087 / 30,033 |
| W + stop rổ 8% vốn | 53,100 | 78% | 14.4% | 17.2% | 33% | 14.4% | 16.3% | 25,827 / 27,273 |
| W + kill lỗ ngày 6% | 52,630 | 78% | 14.0% | 16.4% | 37% | 14.0% | 14.0% | 27,583 / 25,047 |
| W + stop rổ 8% + kill ngày 6% | 53,482 | 79% | 14.0% | 16.4% | 33% | 14.0% | 14.0% | 27,257 / 26,225 |

**NEW4**

| Chính sách | Net | %gốc | DD | DD spread×2+slip1 | Gap-5% bất kỳ lúc | Gap-5% cuối tuần | Gap-10% cuối tuần | A / B |
|---|---|---|---|---|---|---|---|---|
| Gốc (không bảo vệ) | 26,995 | 100% | 8.5% | 17.1% | 49% | 27.7% | 52.2% | 11,732 / 15,263 |
| W: khoá hedge cuối tuần/lễ | 24,449 | 91% | 8.5% | 19.1% | 50% | 8.5% | 14.3% | 9,862 / 14,588 |
| W + layer−1 | 3,080 | 11% | 39.7% | 47.3% | 52% | 39.7% | 39.7% | 8,810 / -5,729 |
| W + stop giá (hsk 1 gap sau lớp cuối) | -1,085 | -4% | 11.9% | 33.4% | 44% | 11.9% | 15.3% | -1,325 / 240 |
| W + stop rổ 8% vốn | 18,002 | 67% | 9.0% | 13.7% | 49% | 9.0% | 14.3% | 5,450 / 12,552 |
| W + kill lỗ ngày 6% | 15,772 | 58% | 12.9% | 22.1% | 50% | 12.9% | 14.3% | 2,920 / 12,852 |
| W + stop rổ 8% + kill ngày 6% | 16,141 | 60% | 12.0% | 19.2% | 49% | 12.0% | 14.3% | 3,289 / 12,852 |

**PortD0**

| Chính sách | Net | %gốc | DD | DD spread×2+slip1 | Gap-5% bất kỳ lúc | Gap-5% cuối tuần | Gap-10% cuối tuần | A / B |
|---|---|---|---|---|---|---|---|---|
| Gốc (không bảo vệ) | 86,502 | 100% | 13.7% | 21.8% | 57% | 41.3% | 80.1% | 38,400 / 48,103 |
| W: khoá hedge cuối tuần/lễ | 82,035 | 95% | 13.4% | 21.3% | 59% | 13.4% | 22.8% | 36,849 / 45,187 |
| W + layer−1 | 60,590 | 70% | 22.4% | 51.5% | 49% | 22.4% | 22.4% | 35,508 / 25,082 |
| W + stop giá (hsk 1 gap sau lớp cuối) | 53,769 | 62% | 13.6% | 22.3% | 48% | 13.6% | 22.8% | 26,947 / 26,821 |
| W + stop rổ 8% vốn | 69,221 | 80% | 12.5% | 16.3% | 62% | 12.5% | 22.8% | 33,438 / 35,782 |
| W + kill lỗ ngày 6% | 69,062 | 80% | 13.8% | 16.1% | 59% | 13.8% | 13.8% | 32,498 / 36,564 |
| W + stop rổ 8% + kill ngày 6% | 68,648 | 79% | 12.5% | 16.1% | 59% | 12.5% | 12.5% | 32,405 / 36,243 |
(Chú thích: "Gap-5% bất kỳ lúc" = sốc 5% tại thời điểm tồi nhất, mọi hệ cùng hướng xấu nhất, tính theo vị thế ròng; "cuối tuần" = sốc đặt tại bar cuối trước gián đoạn >5h. PortA/B/NEW4 lưới 144 chính sách; stop giá = đặt cách điểm vào đầu `hsk`×gap sau lớp cuối; stop rổ % tính trên vốn tài sản.)

### 19.3 Stress lại ở lot đã chọn (Python; DD % vốn)
| Danh mục | Net gốc / DD | spread×2+slip1 | spread×3+slip1 | spread×2+slip2 |
|---|---|---|---|---|
| PortA (không W) | 36,107 / 16.3% | 50.8% | 43.8% | 74.8% |
| PortA + W | 34,029 / 16.2% | 52.8% | 48.9% | 48.9% |
| PortB×0.85 | 67,839 / 14.5% | 17.1% | 24.3% | 24.0% |
| PortB×0.85 + W | 65,278 / 15.1% | 16.0% | 25.5% | 25.4% |
| NEW4 + W | 24,449 / 8.5% | 19.1% | 19.0% | 19.0% |
| PortD-G30 + W | 67,120 / 17.0% | 18.7% | 23.2% | 18.7% |
| PortD-G40 + W | 78,695 / 16.2% | 18.0% | 24.1% | 24.0% |
=> PortA (có x2 hedge) KHÔNG chịu được slip 1 (DD >48%); PortB/PortD đều <26% ở spread×3+slip1.

### 19.4 Lot tối ưu có ràng buộc gap (opt5; policy W; ràng buộc DD≤17%, sx2≤25%, gap-5% ≤ G, gap-10% cuối tuần ≤ 2G)
Tối ưu coordinate-ascent có sàn đa dạng hoá; cap lot theo MT5 đã kiểm: x1 .09, x4 .06, g1/g2 .12, xs1 .6, xs2 1.0, u1 3.9, u2 .5, u6 1.0, u7 5.0, u10 2.5, u11 2.0.
| Bộ | Lot | Net Python | DD / sx2 / gap-5% | A / B | tháng+ |
|---|---|---|---|---|---|
| **PortD-G30** (gap-5% ≤ 30%) | x1 .04, x4 .03, g1 .04, g2 .03, xs1 .6, xs2 .95, u1 1.0, u2 .3, u6 1.0, u7 1.6, u10 1.8, u11 .4 | +67,120 | 17.0% / 18.7% / 29.0% (XAU 25.5, US 24.6) | 32.7k / 34.4k | 6/6 |
| PortD-G40 (gap-5% ≤ 40%) | x1 .06, x4 .04, g1 .06, g2 .04, xs1 .58, xs2 1.0, u1 1.1, u2 .3, u6 1.0, u7 3.1, u10 1.6, u11 .6 | +78,695 | 16.2% / 18.0% / 38.5% | 37.2k / 41.5k | 6/6 |
| PortD-max (không ràng buộc gap) | x1 .06, x4 .06, g1 .12, g2 .11, xs1 .6, xs2 1.0, u1 3.9, u2 .5, u6 1.0, u7 5.0, u10 2.5, u11 2.0 | +102,801 | 16.4% / 24.4% / **79.6%** | 45.5k / 57.3k | 6/6 — KHÔNG an toàn gap |
Chi phí an toàn gap: PortB 80.8k → 61.9k (gap30, −23%); PortD 102.8k → 67.1k (−35%); NEW4 25k→13.9k. Scalp xs1/xs2 (SL-bound, không phơi gap) mang phần lớn net khi ràng buộc gap chặt.
Cảnh báo: tối ưu trên cùng mẫu; phần lớn net MT5 của PortD đến từ xs1+xs2 (~115 lệnh mỗi hệ) → phụ thuộc scalp.

### 19.5 MT5 real ticks (100% real ticks, 01.06–27.11; EA r5, W bật cho rổ; scalp W tắt)
| Job | Lot | MT5 net | MT5 DD | Python W |
|---|---|---|---|---|
| x1 | 0.09 | +14,215 | 14.5% | +14,827 / 22.0% |
| g1 | 0.12 | +9,514 | 11.0% | +9,514 / 12.4% |
| g2 | 0.12 | +9,583 | 8.5% | +9,871 / 9.1% |
| u10 | 2.5 | +2,986 | 13.1% | +2,988 / 16.5% |
| u11 | 2.0 | +2,043 | 14.7% | +2,076 / 16.4% |
| g3 (pw_break_flow) | 0.06 | +7,953 | 11.6% | +8,259 / 13.6% |
| g4 (basis_mom) | 0.09 | +4,892 | 16.5% | +5,872 / 12.6% |
| g5 (ad15z_fade NY) | 0.04 | +7,751 | 10.0% | +8,572 / 11.2% |
| u12 (rnd_break_50 NY) | 3.0 | +5,051 | 11.4% | +5,079 / 12.7% |
| u13 (imb15z_mom) | 3.0 | +5,604 | 8.2% | +5,967 / 9.4% |
Jobs của PortD-G30/G40: x1 .04 +6,318/8.0%; x4 .03 +2,961/11.8%; g1 .04 +3,171/3.9%; g2 .03 +2,396/2.2%; xs1 .6 +14,769/5.0%; xs2 .95 +34,889/15.5%; u1 1.0 +1,313/4.2%; u2 .3 +493/3.2%; u6 1.0 +2,344/4.7%; u7 1.6 +3,732/10.0%; u10 1.8 +2,149/10.0%; u11 .4 +409/3.2% (G40 tương tự, xem results_p4/p6.jsonl).

### 19.6 DD gộp đo trên MT5 (ghép equity theo timestamp; vốn 40k)
| Danh mục | Net MT5 | DD gộp | A / B | tháng+ | Nửa lot (×0.5) | Tổng DD thành phần |
|---|---|---|---|---|---|---|
| **NEW4** (g1 .12, g2 .12, u10 2.5, u11 2.0) + W | +24,126 | **8.4%** | 10.0k / 14.1k | 6/6 | +12,063 / 4.2% | 9.7k |
| **PortD-G30** (12 hệ, bảng 19.4) + W | +74,942 | **15.1%** | 31.6k / 43.3k | 6/6 | +37,471 / 7.5% | 22.8k |
| **PortD-G40** | +85,368 | **17.7%** | 36.0k / 49.4k | 6/6 | +42,684 / 8.9% | 28.4k |
| PortD-G30 + u12 + u13 (3.0/3.0) | +85,597 | 14.9% | 36.7k / 48.9k | 6/6 | +42,798 / 7.4% | |
| **PortE** = PortD-G30 + g3 .06 + g5 .04 + u12 3.0 + u13 3.0 | +101,301 | **13.2%** | 45.6k / 55.7k | 6/6 | +50,650 / 6.6% | |
| PortD-G30 + cả 5 hệ mới (g3,g4,g5,u12,u13) | +106,193 | **26.1% (vượt 20%)** | 48.7k / 57.5k | 6/6 | +53,097 / 13.1% | 36.2k |
| ... nhưng new ×0.5 | +90,568 | 19.8% | | 6/6 | | |
g4 (basis_mom) làm DD gộp tăng vọt (13.2% → 26.1%) → LOẠI g4 khỏi danh mục.
Python gap/stress của PortE: net +94,997, DD 16.1%, sx2 22.4%, **gap-5% 52% (không an toàn gap ở lot đầy)**; **PortE half-lot: gap-5% 26.1%**, DD 8.0%, sx2 11.2%, Python +47.5k / MT5 +50.7k, DD MT5 6.6%.

### 19.7 Khuyến nghị cuối vòng 5
| Mục tiêu | Danh mục | Lot | Kỳ vọng MT5 (6 tháng) |
|---|---|---|---|
| An toàn gap (gap-5% ≈ 26–29%) | **PortD-G30** hoặc **PortE ×0.5** | bảng 19.4 / ×0.5 PortE | PortD-G30 +74.9k / DD 15.1%; PortE half +50.7k / DD 6.6% |
| Cân bằng | PortD-G40 | bảng 19.4 | +85.4k / 17.7% (gap-5% 38.5%) |
| Tối đa lợi nhuận (chấp nhận gap) | PortE full | | +101.3k / 13.2% (gap-5% 52%) |
Mọi rổ phải bật W (EA r5: InpTuanKhoaGio=21, InpNghiLe="2026.07.03,2026.09.07,2026.11.26" — cập nhật ngày lễ thật cho tương lai; ngày lễ ở demo/Exness có thể khác giờ server). Demo forward nên chạy ×0.5.

### 19.8 Hệ mới vòng 5 (screen 246+666 cấu hình/asset → battery → MT5)
| Hệ | Tín hiệu | Mgmt | Python (lot ref) | A/B | Battery |
|---|---|---|---|---|---|
| g3 Gold | pw_break_flow (phá đỉnh/đáy tuần trước + dòng lệnh) gt20 ldny | gap8 N4 TP4 | +4,096 (0.03) DD 8% | 1,984 / 2,112 | 6/6, placebo 100, detrend +4,189, reverse +4,049, delay2 +4,253, cả 2 phía dương |
| g4 Gold | basis_mom (basis futures-CFD z>2 + flow) gt20 ldny | gap8 N4 TP4 | +2,589 DD 4% | 1,295 / 1,294 | 6/6, placebo 100, MT5 DD 16.5% → LOẠI |
| g5 Gold | ad15z_fade2.0 (absorption-delta fade) NY | gap8 N4 TP4 | +6,944 (0.03) DD 8.2% | 3,852 / 3,092 | 6/6, placebo 100, detrend +6,872, reverse +6,802; **delay2 −3,262: cần vào lệnh nhanh** |
| u12 US500 | rnd_break_50 (phá mốc tròn 50 điểm + flow) NY | gap60 N4 TP8 | +1,629 (1 lot) DD 5% | 817 / 812 | 6/6, placebo 100, detrend +1,670, reverse +1,687, delay2 +1,107 |
| u13 US500 | imb15z_mom2.0 (imbalance 15m đánh thuận) gt20 | gap60 N3 TP6 | +1,895 (1 lot) DD 4% | 729 / 1,166 | 6/6, placebo 100, sx +1,358, delay2 +1,507 |
Loại/ít tin cậy: g6 sw30z_fade (tương quan 0.77 với x1), u14 g3_15z_fade (DD 24%, tương quan 0.5 với u1), imb15z_fade (reverse âm), g2_15z_mom/sw30z_mom (reverse âm), rnd_sweep_*/div_fade (placebo thấp), hl60_break_flow (reverse âm), fz15z_mom3.0 (delay2 −11k, mong manh). Tương quan P&L ngày giữa hệ mới và hệ cũ ≤0.3 (trừ u13–u1 0.45).
Lưu ý đa kiểm định: 912 cấu hình/asset đã quét; bộ battery + A/B + MT5 giảm nhưng không loại hết rủi ro overfit; cần forward demo.

### 19.9 Hạn chế vòng 5
- Chính sách stop cứng/kill ngày chọn trên cùng mẫu 6 tháng, ít sự kiện (2–10 lần kích hoạt) → không dùng làm edge.
- W chỉ bảo vệ gap khi thị trường đóng cửa; hedge-lock có spread 2 lần + swap hedge; thanh khoản mở cửa Thứ Hai vẫn có trượt giá.
- MT5 joint DD là dựng lại từ bảng deals (sai số 1–6% so với eq_dd của MT5).
- Python gap tính theo vị thế ròng toàn bộ danh mục trong kịch bản xấu nhất mọi tài sản.
- Box bị khôi phục snapshot giữa vòng (12:18): các file mất đã dựng lại; kết quả trong results/r5/ và r4/joint5.json đã kiểm.


## 20. Round 6 — phủ toàn bộ họ tín hiệu, hệ mới g7/xs3–xs7/u15–u19, tìm combo & 3 kịch bản (28/11)
### 20.1 Phủ họ tín hiệu (coverage) — xem `COVERAGE.md`
- Vòng 6 thêm `newsig4` (93 spec/asset: naked POC, VA 80%, gap fill/go, NR-day, gap cuối tuần, mốc giờ cố định (London fix, NY close…), range-expansion, volume climax, cá mập tại cực trị, z-window 5/30/60 cho g1/g2/g3/imb/ar/fz/ad, VWAP trend pullback, NY IB, CVD lead) và `scalp2` (lưới SL/TP×hold 40 ô cho TẤT CẢ họ basket newsig1–4, 948 tổ hợp/asset), `newsig5` (đảo chiều pullback/IBS + 91 cặp đồng pha/asset).
- Tổng đã chạy: ~36k cấu hình basket + ~300k cấu hình scalp (2 tài sản). Ô duy nhất chưa thử được: gap qua đêm/cuối tuần (chỉ 8–15 sự kiện/6 tháng → không đủ mẫu), NQ/SI/CL lead-lag, GEX/flip/walls (KHÔNG CÓ dữ liệu).
- Cảnh báo cơ sở: basket không SL có thiên lệch dương — 53% cấu hình PLACEBO (vào lệnh ngẫu nhiên) cũng dương cả A và B → tiêu chí "A&B dương" vô nghĩa với basket nếu không có placebo-percentile, reverse-drift, delay.

### 20.2 Hệ mới vòng 6 (battery + MT5 100% real ticks)
| Mã | Tài sản | Tín hiệu | Lọc | Quản lý | Lot MT5 | MT5 net / DD | Python | Battery |
|---|---|---|---|---|---|---|---|---|
| g7 | XAU | `imb30z_fade2.0` (imbalance 30m |z|>2 → fade) | gt20, all | basket 8/4/4 + W | 0.04 | +7,544 / 8.9% | +6,849 / 10.4% | placebo 100, detrend +6,781, reverse +7,102, delay2 +6,448, long +2,946 / short +4,958, sx +6,266 |
| xs3 | XAU | `g1_30z_fade2.0` (lệnh lớn ngưỡng 1, 30m |z|>2 → fade) | gt20, all | scalp SL 13 / TP 8 / 90 bar | 0.30 | **+21,046 / 6.8%** (481 lệnh, PF 1.42) | +18,056 | cfg chọn trên A: B tB 3.08, flip-z 3.5, spread×2 +, delay2 + , 6/6 tháng |
| xs4 | XAU | `imb15z_fade3.0` | gt20, all | scalp SL 8 / TP 10 / 90 | 0.30 | +9,735 / 7.9% (270) | +11,246 | B tB 2.1, 6/6 |
| xs5 | XAU | `basis_rev` (basis futures−CFD lệch → hồi) | gt20, ny | scalp SL 8 / TP 6 / 90 | 0.30 | +7,019 / 3.8% (175) | +6,556 | B tB 1.9, 6/6 |
| xs6 | XAU | `g3_60z_mom3.0` (cá mập 60m |z|>3 → thuận) | none, ny | scalp SL 10 / TP 13 / 90 | 0.30 | +10,130 / 7.7% (95) | +9,575 | B tB 1.6, 5/6 — mẫu nhỏ |
| xs7 | XAU | `day_ext_fail` (phá đỉnh/đáy ngày thất bại) | gt20, ny | scalp SL 8 / TP 18 / 30 | 0.30 | +5,875 / 4.6% (89) | +6,482 | B tB 1.25, 6/6 — mẫu nhỏ |
| u15 | US500 | `fz5z_fade2.0` | none, ny | basket 60/3/6 + W | 1.5 | +2,649 / 11.9% | +2,859 / 14.6% | placebo 100 (tương quan 0.87 với u2) |
| u16 | US500 | `vclimax_fade_3` (volume climax tại đỉnh/đáy 60 bar → fade) | none, ldny | 60/4/8 + W | 1.0 | +1,818 / 8.7% | +2,169 | placebo 95 |
| u17 | US500 | `vclimax_mom_2` | none, ny | 60/4/8 + W | 2.0 | +3,030 / 9.8% | +3,546 | placebo 90 |
| u18 | US500 | `fz30z_fade2.0` | none, all | 60/4/8 + W | 1.5 | +1,879 / 12.4% | +1,970 | placebo 90 |
| u19 | US500 | `g2_60z_mom2.0` | none, all | 60/4/8 + W | 1.5 | +2,473 / 9.7% | +2,884 | placebo 90 |
- Scalp SL/TP theo GIÁ (USD/oz), cấu hình chọn trên nửa A rồi kiểm nửa B (OOS) — chống overfit. US500 scalp: không có hệ nào qua (B âm hoặc spread×2 âm).
- Loại sau battery: XAU g1_30z_mom/g2_30z_mom/ar30z_mom/fz30z_mom/g3_60z_mom basket (reverse-drift âm = ăn theo xu hướng giảm vàng), rexp_fade (B riêng âm), US500 fz5z_mom/imb5z_mom (placebo 80), rexp_mom/g1_30z_mom (placebo 40–45).

### 20.3 SỬA SỐ VÒNG 5 (quan trọng)
1. **Joint DD PortE**: bug phân loại g5 là US500 khi dựng equity → DD đúng là **14.9%** (không phải 13.2%); nửa lot **7.5%** (không phải 6.6%). Net không đổi (+101,301).
2. **Gap scalp**: vòng 5 coi scalp xs1/xs2 "miễn nhiễm gap" — SAI: gap xuyên SL. Vòng 6 tính cả vị thế scalp khi đang mở → gap-5% của các danh mục có scalp lot lớn cao hơn nhiều so với số vòng 5 (PortD-G30 "29%" bị đánh giá thấp).

### 20.4 Tìm combo (greedy theo tương quan + tối ưu lot, `opt6.py`)
- Vũ trụ 27 hệ đã pass (bỏ x2, g4). Greedy chọn theo Sharpe ngày của tổng (trọng số 1/DD): **g2 → xs6 → x1 → xs4 → xs7 → xs2 → u12 → xs3 → xs1 → u15 → u10 → g7 → g5 → xs5 → u17** (15 hệ, tương quan ngày giữa hệ mới với hệ cũ ≤0.27 trừ u15–u2 0.87, u18–u11 0.59).
- Chống overfit: tối ưu lot trên A rồi đo B, tối ưu trên B rồi đo A; **lot chốt = trung bình (lot tối ưu A, lot tối ưu B)**, scale cho vừa ràng buộc toàn mẫu, làm tròn bước lot (0.01 vàng, 0.1 US500).
- Kịch bản (ràng buộc Python: DD / spread×2 DD / gap-5%): an toàn 10/15/30, cân bằng 15/22/50, mạnh tay 19/28/không giới hạn gap.

### 20.5 KỊCH BẢN CHỐT (DD gộp đo trên MT5 = equity ghép theo timestamp, scale tuyến tính lot từ các run MT5 từng hệ; vốn 40k)
| Kịch bản | MT5 net | DD gộp | A / B | tháng+ | Nửa lot |
|---|---|---|---|---|---|
| **An toàn** | +33,686 | 3.6% | 15,629 / 18,056 | 6/6 | +16,843 / 1.8% |
| **Cân bằng** | +59,154 | 5.7% | 27,615 / 31,539 | 6/6 | +29,577 / 2.9% |
| **Mạnh tay** | +127,792 | 12.7% | 59,724 / 68,068 | 6/6 | +63,896 / 6.3% |
| Mạnh tay ×1.4 (DD<20% theo yêu cầu) | +177,154 | 17.1% | 82,724 / 94,430 | 6/6 | +88,577 / 8.6% |
| **Đánh tay** (7 scalp vàng) | +21,526 | 3.8% | 9,851 / 11,676 | 6/6 | +10,763 / 1.9% |
| Đánh tay ×2.5 | +53,770 | 9.6% | 24,596 / 29,173 | 6/6 | +26,885 / 4.8% |
| (so sánh) cả 27 hệ, mạnh tay | +124,667 | 12.4% | 53,480 / 71,187 | 6/6 | +62,334 / 6.2% |

- **An toàn — lot:** g2 0.02, xs6 0.12, x1 0.01, xs4 0.07, xs7 0.11, xs2 0.08, u12 2.3, xs3 0.07, xs1 0.16, u15 0.5, u10 1.3, xs5 0.11, u17 0.9. Python: net 32,301, DD 3.3%, spread×2+slip1 DD 4.8%, gap-5% 27%, A 15,421 / B 16,876.
- **Cân bằng — lot:** g2 0.04, xs6 0.21, x1 0.02, xs4 0.11, xs7 0.18, xs2 0.14, u12 2.7, xs3 0.12, xs1 0.27, u15 0.8, u10 1.6, g7 0.01, g5 0.01, xs5 0.19, u17 1.5. Python: net 56,742, DD 5.5%, spread×2+slip1 DD 8.1%, gap-5% 48%, A 27,138 / B 29,598.
- **Mạnh tay — lot:** g2 0.08, xs6 0.48, x1 0.06, xs4 0.26, xs7 0.4, xs2 0.41, u12 3.6, xs3 0.25, xs1 0.39, u15 1.8, u10 2.2, g7 0.03, g5 0.03, xs5 0.42, u17 2.7. Python: net 123,132, DD 12.1%, spread×2+slip1 DD 17.1%, gap-5% 98%, A 58,884 / B 64,236.
- **Đánh tay — lot:** xs1 0.15, xs2 0.08, xs3 0.08, xs4 0.06, xs5 0.1, xs6 0.09, xs7 0.1. Python: net 19,654, DD 4.3%, spread×2+slip1 DD 4.8%, gap-5% 29%, A 9,403 / B 10,252.
- Mạnh tay ×1.4: nhân mọi lot ở dòng "Mạnh tay" với 1.4 (u12 5.04, u10 3.08 vượt mức lot đã test MT5 riêng lẻ → rủi ro ngoại suy). Gap-5% Python ~137% vốn → một cú gap 5% có thể cháy tài khoản.
- Đánh tay ×2.5: xs1 .38, xs2 .20, xs3 .20, xs4 .15, xs5 .25, xs6 .22, xs7 .25 (tài khoản 30k).
- So với vòng 5: PortE (+101.3k, DD 14.9%) ↔ Mạnh tay (+127.8k, DD 12.7%) — tốt hơn cả net lẫn DD, và lot đã qua kiểm tra chéo A/B.

### 20.6 Cảnh báo vòng 6
- Đa kiểm định rất lớn (~336k cấu hình). Không hệ scalp nào sống sót hiệu chỉnh Bonferroni đầy đủ (t tối đa ~3.2 trên A+B); bảo vệ dựa vào: chọn cấu hình trên A – kiểm B, flip-z, spread×2, delay2, MT5. Cần forward demo.
- xs6, xs7 chỉ ~90 lệnh/6 tháng.
- Python DD của scalp chỉ tính lúc đóng lệnh (lạc quan); MT5 DD đã bao gồm thả nổi.
- Gap 5% đột ngột trong phiên vẫn là rủi ro lớn nhất; W chỉ xử lý gap cuối tuần/lễ.
