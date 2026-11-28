# README_SCENARIOS — Hệ thống & kịch bản Vàng (XAU) / SP500 (US500) — bản bàn giao (handoff)
Cập nhật: 2026-11-28 16:48 (Asia/Saigon). Tác giả: Grok Bot (executor XSD-16). Tài liệu tự-đủ (self-contained) cho Grok khác / phát triển sau.
**Không có secret trong tài liệu/code này. Mọi số là BACKTEST (Python bảo thủ hoặc MT5 100% real ticks), KHÔNG phải kết quả live.** Thiếu số → ghi `KHÔNG CÓ`.

## 0. Tóm tắt 1 phút
- **VỐN THỰC TẾ = hai tài khoản cent 100 USD tách riêng** (một chỉ vàng, một chỉ SP500). Lot tối thiểu dùng trong tính toán: vàng **0,10**, US500 **0,14**. Bảng chính ở **mục 14**. Mục 13 (min 0,01) đã lỗi thời với min lot thực tế. Các mục 1–12 là vốn tham chiếu 100k/50k, giữ để so sánh.
- Dữ liệu: Rithmic/Fxaurum futures order-flow (GC = vàng COMEX, ES = S&P mini) 1 phút, 01/06–26/11/2026 → tín hiệu; khớp lệnh trên giá CFD XM (GOLD.i#, US500Cash) M1 bid + spread XM thật. KHÔNG có NQ/SI/CL, KHÔNG có lịch sử GEX/Gamma flip/Walls/MBO.
- Kiểm định: A/B OOS (A = 01/06–19/08, B = 20/08–26/11), placebo (đảo dấu ngẫu nhiên 20 lần), detrend/reverse drift, spread×2/×3 + slippage, trễ vào lệnh 2 nến (delay2), chỉ long/chỉ short, MT5 100% real ticks (EA BRAIN_XuLiLenh, chế độ đọc CSV điểm vào).
- Hai kiểu hệ: **basket** (giỏ DCA không SL, chốt tổng TP theo giá) và **scalp** (1 lệnh, SL/TP/hold cố định).
- Rủi ro chính: gap trong phiên (xuyên mọi SL, chỉ giảm bằng lot), mẫu 6 tháng, ~900+ cấu hình/asset đã quét (multiple testing), scalp xs1/xs2 chỉ ~115 lệnh mỗi hệ nhưng chiếm ~2/3 lợi nhuận danh mục.

## 1. Nguồn dữ liệu & giờ
| Mục | Giá trị |
|---|---|
| Tín hiệu | Rithmic GC (COMEX.GCZ6/GCG7) & ES (CME.ESZ6) footprint 1m → 164 đặc trưng/bar (`v3/tbl/XAU.parquet`, `US500.parquet`) |
| Khớp lệnh | XM CFD M1 bid (`GOLD_i_M1_xmserver.csv`, `US500Cash_M1_xmserver.csv`) + spread XM, slippage 0.5×spread, swap |
| Giờ server | Europe/Athens (XM theo DST châu Âu). File điểm vào CSV cho EA dùng giờ server |
| Vốn chuẩn | XAU 30,000 USD; US500 10,000 USD; danh mục chéo 40,000 USD (vòng 7: 100k/50k; **vòng 8: 100 USD cent**) |
| Lot chuẩn k=1 | XAU basket L0 0.03; US500 basket L0 1.0; lot scale tuyến tính |
| Phiên (UTC, theo `sig_v3.filters`) | ldny = 07–20h; ny = 13–20h; ldn = 07–13h; all = cả ngày; luôn bỏ bar có tin (news) |
| ADX lọc | gt20 = ADX(14, M1 trên CFD) > 20 |

## 2. Định nghĩa đặc trưng chính (order-flow)
- `d{w}z`: delta (ask−bid volume) cộng dồn w phút / độ lệch chuẩn cuộn → z.
- `sw{w}z`: sweep ròng (lệnh quét nhiều mức giá, mua − bán) cộng w phút, z-score.
- `g1/g2/g3_{w}z`: delta của lệnh lớn theo 3 ngưỡng kích thước (g3 = cá mập), w phút, z.
- `imb{w}z`, `stk{w}`: imbalance chéo footprint (z) và số mức stacked imbalance.
- `ad{w}z`: absorption-delta (delta lớn nhưng giá futures không chạy); `fz{w}z`: lợi suất futures z; `ar{w}z`: lợi suất tài sản chéo (ES cho vàng, GC cho SP) z.
- `basis` = futures − CFD; `vwap_cfd`, `vwap_z`, `poc_p/vah_p/val_p` (profile phiên trước), `pdH/pdL/pdC` (ngày trước theo ngày NY+7h), `nyor/nyib/lnor/cxor/as` (opening range NY, IB NY, London OR, COMEX OR, range phiên Á).
- Mọi tín hiệu: chỉ cạnh lên của điều kiện (`cross`) + cooldown 10 bar; vào ở **open nến kế tiếp**.

## 3. Quản lý lệnh (management)
**Basket (giỏ DCA, không SL):** vào L0; mỗi khi giá đi ngược thêm `gap` (bước giá, giãn ×`gstep`=1.4 mỗi tầng) nhồi thêm 1 lệnh cùng lot (mult 1.0) tới `maxN` tầng; đóng cả giỏ khi giá về cách giá trung bình `btp` (TP theo giá) — cooldown 30 phút sau khi đóng. Không SL; stop-out 50% margin.
**Scalp:** 1 lệnh, SL/TP theo giá, giữ tối đa 90 bar M1, không nhồi.
**Khoá hedge cuối tuần (W, vòng 5):** Thứ Sáu ≥21:00 giờ server và ngày trước ngày lễ (03/07, 07/09, 26/11/2026) ≥21:00: mở 1 lệnh ngược bằng đúng vị thế ròng của giỏ, cấm mở giỏ/nhồi; bar đầu tiên sau cửa sổ đóng hedge. Giữ 91–96% net, xoá rủi ro gap cuối tuần. Chỉ áp cho basket.

## 4. Danh sách hệ ĐÃ PASS (đủ A/B dương, placebo ≥90%, MT5 verified)
Cột "MT5" = 100% real ticks 01/06–27/11/2026 ở lot ghi chú. Python = engine bảo thủ.
### 4.1 Vàng XAU (vốn 30k)
| Mã | Tín hiệu (code name) | Ý nghĩa | Lọc | Mgmt (gap/maxN/btp, giá USD) | Lot chuẩn | MT5 net / DD | Ghi chú |
|---|---|---|---|---|---|---|---|
| x1 | `sw_fade_15_1.8` | |sw15z|>1.8 → vào NGƯỢC chiều sweep (bắt ngược cú quét) | gt20, ldny | 8 / 4 / 4 | 0.09 (G30: .04) | +16,732 / 14.2% (W: +14,215 / 14.5%) | chủ lực |
| x2 | `sw_fade_15_1.8` + hedge | như x1, mult 1.3, gap 6, btp 3, prune 1.5, hedge khi lỗ (hgap 18, hr .5, htp 5) | gt20, ldny | 6/4/3 | 0.10 | +13,603 / 12.1% | **mong manh**: sụp khi slip 1 → KHÔNG dùng |
| x4 | `dz_fade_15_2.0` | |d15z|>2 → fade | none, ldn | 8/4/4 | 0.04 (G30 .03) | +4,600 / 14.9% (G30 +2,961 / 11.8%) | 0.07 → DD 24.7% |
| g1 | `pd_break_flow` | phá pdH/pdL với d15z>1 cùng chiều | gt20, ldny | 4/3/2 | 0.12 (G30 .04) | +10,184 / 10.9% (W +9,514 / 11.0%) | cần vào nhanh (delay2 lỗ) |
| g2 | `lnor_break_trend` | phá London opening range theo phía EMA55 | gt20, all | 4/3/2 | 0.12 (G30 .03) | +10,426 / 8.5% (W +9,583 / 8.5%) | |
| g3 | `pw_break_flow` (newsig2) | phá đỉnh/đáy TUẦN trước + flow | gt20, ldny | 8/4/4 | 0.06 | +7,953 / 11.6% | battery mạnh nhất vòng 5 |
| g5 | `ad15z_fade2.0` (newsig3) | absorption-delta 15m |z|>2 → fade | none, ny | 8/4/4 | 0.04 | +7,751 / 10.0% | delay2 −3,262: cần vào nhanh |
| xs1 | `xlead_fadeself_5_2.5` ∧ `big2_mom_30_2.5` (trong 30 bar) | vàng chạy trước khi ES đứng yên, ngược với lệnh lớn → fade | gt20, all | SCALP TP 8 USD, SL ≈ 8 USD (EA: InpCatLoPct ≈ 1.6%×lot/0.6), hold 90 | 0.57–0.6 | +13,584 / 5.6% (0.57); +14,769 / 5.0% (0.6) | ~116 lệnh |
| xs2 | `big3_mom_60_2.0` ∧ `emapull` (30 bar) | cá mập 60m một chiều + hồi về EMA, phiên NY → thuận | none, ny | SCALP TP 13, SL ≈ 8, hold 90 | 0.6–1.0 | +36,199 / 16.3% (1.0); +34,889 / 15.5% (0.95); +17,474 / 13.5% (0.6) | ~115 lệnh |
| g7 | `imb30z_fade2.0` (newsig4) | imbalance 30m |z|>2 → fade | gt20, all | 8/4/4 | 0.04 | +7,544 / 8.9% | vòng 6, battery đầy đủ dương |
| xs3 | `g1_30z_fade2.0` (newsig4) | lệnh lớn ngưỡng 1 30m |z|>2 → fade | gt20, all | SCALP SL 13 / TP 8 / hold 90 | 0.3 | **+21,046 / 6.8%** (481 lệnh) | vòng 6, cfg chọn trên A |
| xs4 | `imb15z_fade3.0` (newsig3) | imbalance 15m |z|>3 → fade | gt20, all | SCALP SL 8 / TP 10 / 90 | 0.3 | +9,735 / 7.9% (270) | vòng 6 |
| xs5 | `basis_rev` (newsig2) | basis futures−CFD lệch → hồi | gt20, ny | SCALP SL 8 / TP 6 / 90 | 0.3 | +7,019 / 3.8% (175) | vòng 6 |
| xs6 | `g3_60z_mom3.0` (newsig4) | cá mập 60m |z|>3 → thuận | none, ny | SCALP SL 10 / TP 13 / 90 | 0.3 | +10,130 / 7.7% (95) | mẫu nhỏ |
| xs7 | `day_ext_fail` (newsig2) | phá đỉnh/đáy ngày thất bại → fade | gt20, ny | SCALP SL 8 / TP 18 / 30 | 0.3 | +5,875 / 4.6% (89) | mẫu nhỏ |
| gp1 | pair `pw_break_flow`+`emapull` | | none, all | 8/4/4 | 0.06 | +9,237 / 8.5% | vòng 6b, tập con x1/g2 |
| gp2 | pair `sw_fade_15_1.8`+`dz_fade_15_2.0` | | gt20, all | 8/4/4 | 0.06 | +7,479 / 11.4% | vòng 6b |
| gp3 | pair `dz_fade_15_2.0`+`imb30z_fade2.0` | | gt20, all | 8/4/4 | 0.05 | +5,677 / 10.6% | vòng 6b |
| xs8 | pair `pd_break_flow`+`pw_break_flow` | phá đỉnh/đáy ngày+tuần cùng lúc → thuận | gt20, ny | SCALP SL 10 / TP 18 / 90 | 0.3 | +10,437 / 6.1% (86) | vòng 6b, mẫu nhỏ |
| xs9 | pair `g3_60z_mom3.0`+`big3_mom_60_2.0` | cá mập 60m 2 thước đo → thuận | none, ny | SCALP SL 10 / TP 18 / 90 | 0.3 | +11,815 / 11.0% (129) | chồng lấn xs6/xs2 |
| xs10 | pair `sw_fade_15_1.8`+`big3_mom_60_2.0` | sweep fade + cá mập | gt20, all | SCALP SL 10 / TP 18 / 30 | 0.3 | +10,140 / 6.9% (120) | vào danh mục greedy |
Đã loại: x5 (cặp sw+vwapatr), g4 `basis_mom` (MT5 DD 16.5%, làm DD gộp 26%), g6 `sw30z_fade` (tương quan 0.77 với x1), XAU v2_c1 VWAP-fade (fail OOS).
### 4.2 SP500 US500 (vốn 10k)
| Mã | Tín hiệu | Ý nghĩa | Lọc | Mgmt (gap/maxN/btp, điểm) | Lot | MT5 net / DD | Ghi chú |
|---|---|---|---|---|---|---|---|
| u1 | `sw_fade_15_1.8` | fade sweep | gt20, ldny | 60/3/6 | 3.8 max; G30 1.0 | +5,409 / 13.7% (3.8); +1,313 / 4.2% (1.0) | |
| u2 | `absorb_fade_5_1.5_1.0` | |d5z|>1.5, |fr5|<1 ATR, vr5>1 → fade | none, ny | 60/4/8 | 0.2–0.3 | +493 / 3.2% (0.3) | nhỏ |
| u6 | `dz_mom_5_1.5` | |d5z|>1.5 → thuận | none, all | 60/4/8 | ≤1.0–1.4 | +2,344 / 4.7% (1.0); +7,823 / 12.5% (2.8) | spread×2 → DD 59% ở 2.8: GIỚI HẠN ≤1.4 |
| u7 | `sw_fade_15_1.5` | fade sweep nhạy hơn | none, all | 60/4/8 | 1.6–3.1 | +7,092 / 16.3% (3.0); +3,732 / 10.0% (1.6) | |
| u10 | `orbd_mom` | phá NY opening range + d15z>0.5 | gt20, all | 30/3/4 | 1.8–2.5 | +3,721 / 12.5% (2.5); W +2,986 / 13.1% | |
| u11 | `asia_fail` | quét range phiên Á rồi đóng lại trong range → fade | gt20, ldny | 60/4/8 | 0.4–2.0 | W +2,043 / 14.7% (2.0) | 2.5 → DD 18.4% |
| u12 | `rnd_break_50` (newsig2) | phá mốc tròn 50 điểm + flow | none, ny | 60/4/8 | 3.0 | +5,051 / 11.4% | |
| u13 | `imb15z_mom2.0` (newsig3) | imbalance 15m |z|>2 → thuận | gt20, all | 60/3/6 | 3.0 | +5,604 / 8.2% | tương quan 0.45 với u1 |
| u15 | `fz5z_fade2.0` (newsig4) | lợi suất futures 5m |z|>2 → fade | none, ny | 60/3/6 | 1.5 | +2,649 / 11.9% | tương quan 0.87 với u2 |
| u16 | `vclimax_fade_3` | volume climax (vr15>3) tại đỉnh/đáy 60 bar → fade | none, ldny | 60/4/8 | 1.0 | +1,818 / 8.7% | |
| u17 | `vclimax_mom_2` | volume climax (vr15>2) → thuận | none, ny | 60/4/8 | 2.0 | +3,030 / 9.8% | |
| u18 | `fz30z_fade2.0` | lợi suất futures 30m |z|>2 → fade | none, all | 60/4/8 | 1.5 | +1,879 / 12.4% | |
| u19 | `g2_60z_mom2.0` | lệnh lớn ngưỡng 2 60m → thuận | none, all | 60/4/8 | 1.5 | +2,473 / 9.7% | |
| up1 | pair `sw_fade_15_1.8`+`sw_fade_15_1.5` | | none, all | 60/4/8 | 2.0 | +4,245 / 7.4% | vòng 6b, tập con u1/u7 |
| up2 | pair `dz_mom_5_1.5`+`rnd_break_50` | | none, ny | 60/4/8 | 2.0 | +2,921 / 6.4% | vòng 6b |
| up3 | pair `sw_fade_15_1.5`+`vclimax_fade_3` | | none, ldny | 60/4/8 | 1.0 | +1,604 / 8.9% | vòng 6b |
Cũng pass vòng 3 nhưng không dùng trong danh mục khuyến nghị: u3 (sw_fade ∧ absorb, NY), u5 (u1 + hedge), u8 `stk_fade_15_2` (chỉ short), u9 `imb_mom_15_1.5`. Loại: u14 `g3_15z_fade3.0` (DD 24%).

## 5. Danh mục / KỊCH BẢN (vốn 40k, W bật cho mọi basket; DD = DD gộp equity MT5 ghép theo timestamp)
| Kịch bản | Thành phần & lot | MT5 net | DD gộp | A / B | tháng+ | Nửa lot net / DD |
|---|---|---|---|---|---|---|
| NEW4 (g1 .12, g2 .12, u10 2.5, u11 2.0) | +24,126 | 8.4% | 9,998 / 14,128 | 6/6 | +12,063 / 4.2% |
| PortD-G30 | +74,942 | 15.1% | 31,608 / 43,334 | 6/6 | +37,471 / 7.5% |
| PortD-G40 | +85,368 | 17.7% | 35,954 / 49,414 | 6/6 | +42,684 / 8.9% |
| PortD-G30 + u12 3.0 + u13 3.0 | +85,597 | 14.9% | 36,719 / 48,878 | 6/6 | +42,798 / 7.4% |
| PortE = PortD-G30 + g3 .06 + g5 .04 + u12 3.0 + u13 3.0 | +101,301 | 14.9% | 45,629 / 55,672 | 6/6 | +50,650 / 7.5% |
| PortD-G30 + (g3,g5,u12,u13)×0.5 | +88,121 | 14.4% | 38,619 / 49,503 | 6/6 | +44,061 / 7.2% |
- **PortD-G30 lot:** x1 .04, x4 .03, g1 .04, g2 .03, xs1 .6, xs2 .95, u1 1.0, u2 .3, u6 1.0, u7 1.6, u10 1.8, u11 .4 (gap-5% Python 29%).
- **PortD-G40 lot:** x1 .06, x4 .04, g1 .06, g2 .04, xs1 .58, xs2 1.0, u1 1.1, u2 .3, u6 1.0, u7 3.1, u10 1.6, u11 .6 (gap-5% 38.5%).
### KỊCH BẢN CHỐT CUỐI (vòng 6b, opt7 — lot đầy đủ ở mục 11)
| Kịch bản | Hệ | MT5 net 6 tháng | DD gộp MT5 | Gap-5% (Python) |
|---|---|---|---|---|
| **An toàn** | 14 hệ greedy | +36,064 | 3.7% | 27% |
| **Cân bằng** | 15 hệ greedy | +63,102 | 6.3% | 48% |
| **Mạnh tay** | 15 hệ greedy | +119,372 | 11.0% | 98% |
| Mạnh tay ×1.4 / ×1.7 | nhân lot | +167,120 / +202,932 | 15.5% / 18.8% | ~137% / ~167% |
| **Đánh tay** | 10 scalp vàng xs1–xs10 | +20,143 (×3: +60,430; ×5: +100,717) | 3.3% (×3: 9.9%; ×5: 16.5%) | 28% |
Ghi chú: số PortE vòng 5 đã sửa (DD 14.9%, không phải 13.2%). Gap-5% vòng 5 của danh mục có scalp bị đánh giá thấp (vòng 5 coi scalp miễn nhiễm gap).

## 6. Stress (Python, % vốn; xem `results/r5/stress5.json`)
| Danh mục | gốc | spread×2+slip1 | spread×3+slip1 | spread×2+slip2 |
|---|---|---|---|---|
| PortA (x1,x2,u1,u7) | 36,107 / 16.3% | 50.8% | 43.8% | 74.8% | 
| PortB×0.85 + W | 65,278 / 15.1% | 16.0% | 25.5% | 25.4% |
| NEW4 + W | 24,449 / 8.5% | 19.1% | 19.0% | 19.0% |
| PortD-G30 + W | 67,120 / 17.0% | 18.7% | 23.2% | 18.7% |
| PortD-G40 + W | 78,695 / 16.2% | 18.0% | 24.1% | 24.0% |
| PortE + W (Python) | 94,997 / 16.1% | 22.4% | KHÔNG CÓ | KHÔNG CÓ |
| Vòng 6 An toàn / Cân bằng / Mạnh tay (Python, spread×2+slip1 DD) | 32,301 / 3.3% · 56,742 / 5.5% · 123,132 / 12.1% | 4.8% · 8.1% · 17.1% | KHÔNG CÓ | KHÔNG CÓ |
Gap 5% đột ngột trong phiên (mọi hệ cùng hướng xấu nhất): PortD-G30 29%, PortD-G40 38.5%, PortE 52%, PortE×0.5 26%. Stop cứng/kill lỗ ngày không giảm gap (gap xuyên stop) và tốn 20–40% net → không bật mặc định.

## 7. EA MT5 `BRAIN_XuLiLenh_r5` (nguồn: `ea/BRAIN_XuLiLenh_r5.mq5`, UTF-16LE)
Chế độ CSV điểm vào: `InpVao=4`, `InpCsvChung=true`, `InpFileCsv=brain2\<job>_mt5.csv` (thư mục Common\Files), CSV cột `thoi_gian,ma,chieu,gia,nguon,lot` (giờ server).
| Input | Basket (vd x1 .09) | Scalp (vd xs2 .95) | Ý nghĩa |
|---|---|---|---|
| InpLot0 | 0.09 | 0.95 | lot lệnh đầu |
| InpNhoi | 1 | 0 | bật DCA |
| InpBuocGia | 8 (XAU) / 30–60 (US500) | 6 | bước nhồi theo giá |
| InpGianBuoc | 1.4 | – | giãn bước mỗi tầng |
| InpMaxTang | 3–4 | 1 | số tầng tối đa |
| InpTPGia | 2–8 | 8 (xs1) / 13 (xs2) | TP giỏ / TP scalp theo giá |
| InpGiuToiDaNen | 0 | 90 | giữ tối đa (bar) |
| InpCatLoPct | 0 | ≈1.55–2.67 (scale tuyến tính theo lot) | SL theo % balance cho scalp |
| InpHedgeKhiLoPct | 0 | 0 | hedge theo % lỗ (chỉ x2) |
| **InpTuanKhoaGio** | 21 | 0 | **W**: giờ server Thứ Sáu bắt đầu khoá hedge (0 = tắt) |
| **InpNghiLe** | "2026.07.03,2026.09.07,2026.11.26" | – | ngày lễ (dấu phẩy; `;` là comment trong .set) — cập nhật lịch lễ tương lai |
Scalp: `InpNhoi=0, InpMaxTang=1, InpTPGia=TP giá, InpGiuToiDaNen=hold, InpCatLoPct = SL_giá × lot × 100 / vốn × 100` (vàng; vd xs3 lot 0.3, SL 13 → 13×0.3×100/30000×100 = 1.3%). Bảng SL/TP từng scalp ở mục 4.1. Mặc định trong mã nguồn: W TẮT. Hedge W gắn comment `XL_WB`/`XL_WS`.

## 8. Cảnh báo / caveats
1. 6 tháng dữ liệu, một nhịp vàng giảm sau 20/08; multiple testing ~900–2,000 cấu hình/asset → cần forward demo (XM/Exness) nửa lot ≥4–8 tuần trước khi tăng lot.
2. Scalp xs1/xs2 chiếm ~2/3 lợi nhuận danh mục, n≈115.
3. g1, g5 nhạy độ trễ vào lệnh (delay 2 nến lỗ) → cần khớp ngay open nến kế tiếp.
4. Gap trong phiên không chặn được bằng SL; chỉ giảm bằng lot.
5. Joint DD MT5 dựng lại từ deals + M1 bid (sai số 1–6%).
6. Không có dữ liệu GEX/flip/walls/NQ/SI/CL → không kiểm được lọc theo regime options hay lead-lag NQ.

## 9. Bản đồ file (file map)
| Đường dẫn (trong repo `grok_systems/v3/`) | Nội dung |
|---|---|
| `README_SCENARIOS.md` | tài liệu này |
| `pdf/TomTat_KichBan_v3_minlot01_2026-11-28.pdf` | PDF v3: hai TK 100 USD, min lot 0,10/0,14 |
| `pdf/TomTat_KichBan_v2_100USD_cent_2026-11-28.pdf` | PDF v2: min lot 0,01 (đã lỗi thời với min 0,10/0,14) |
| `pdf/TomTat_KichBan_Vang_SP500_2026-11-28.pdf` | PDF v1 vốn 100k (6 trang) |
| `SUMMARY_V3.md` | nhật ký đầy đủ các vòng 1–6 (bảng số) |
| `COVERAGE.md` | danh sách họ tín hiệu đã/chưa thử |
| `code/` | toàn bộ code Python (engine, tín hiệu, battery, tối ưu, MT5 job builders) |
| `results/` | kết quả tóm tắt (json/md/csv/parquet nhỏ) — không có dữ liệu thô |
| `ea/BRAIN_XuLiLenh_r5.mq5` | EA MT5 có khoá hedge cuối tuần |
Máy nhà: `E:\GrokWork\bt_v3\` (bản đồng bộ đầy đủ), MT5 runs `E:\GrokWork\mt5_runs\` (`runq.py`, `results_p4.jsonl` vàng, `results_p6.jsonl` SP500, `reports\v5_*.htm`). Box: `/workspace/bt_3m/v3/`.

## 10. Chạy lại (how to re-run)
```bash
# môi trường: python 3.10+ với numpy pandas numba pyarrow
cd v3/code
python newsig4.py XAU          # screen họ tín hiệu (newsig/newsig2/newsig3/newsig4) → results/newsigN_<asset>.parquet
python batnew3.py US500        # battery (A/B, placebo, detrend, reverse, spread, delay2)
python scalp2.py XAU           # pass scalp SL/TP trên các họ basket
python pf5.py                  # đánh giá danh mục: net, DD, spread×2, gap5, wk10, A/B (policy W)
python stress5.py              # stress spread/slip
python mk_v5.py                # tạo CSV điểm vào + queue MT5 (sau đó chạy E:\GrokWork\mt5_runs\runq.py q.json trên máy Windows)
python ../r4/joint5.py         # DD gộp từ deals MT5
python newsig5.py; python batnew5.py XAU; python sc6.py   # vòng 6b: cặp đồng pha + scalp
python opt7.py                 # greedy + tối ưu lot 3 kịch bản (A/B robust) → results/r6/opt7.json
python ../r4/joint7.py         # DD gộp MT5 cho các kịch bản opt7 + bậc ×lot → r4/joint7.json
python opt8.py                 # kịch bản vốn 100k + chỉ XAU / chỉ US500 (50k và 100k) → results/r6/opt8.json
python ../r4/joint8.py         # DD gộp MT5, cap tuỳ vốn, cắt lot nếu DD>19.5% → r4/joint8.json
python cov.py                  # COVERAGE.md
```
Cần bảng đặc trưng `v3/tbl/<asset>.parquet` (dựng bằng `prep_v3.py` + `feat_v3.py` từ dữ liệu Rithmic 1m — dữ liệu thô KHÔNG có trong git). Engine: `bt.py` (wrapper) → `engine2.py` (numba; P[27..29] = stop giá, stop USD, kill ngày; `fl` = 1 flat / 2 hedge-lock).

## 11. Vòng 6 (đã xong — ALL DONE)
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
## Vòng 6b (newsig5: inverse/pullback/IBS + 91 cặp đồng pha `pair:A+B` trong 30 bar) — HOÀN TẤT
### Hệ mới pass battery + MT5 (100% real ticks, khớp Python)
| Mã | Tín hiệu | Lọc | Kiểu / mgmt | Lot test | MT5 net / DD (lệnh) | Python |
|---|---|---|---|---|---|---|
| gp1 | pair `pw_break_flow` + `emapull` | none, all (XAU) | basket 8/4/4 | 0.06 | +9,237 / 8.5% (402) | 9,288 / 10.3% |
| gp2 | pair `sw_fade_15_1.8` + `dz_fade_15_2.0` | gt20, all | basket | 0.06 | +7,479 / 11.4% (354) | 7,463 / 14.6% |
| gp3 | pair `dz_fade_15_2.0` + `imb30z_fade2.0` | gt20, all | basket | 0.05 | +5,677 / 10.6% (361) | 5,102 / 12.7% |
| up1 | pair `sw_fade_15_1.8` + `sw_fade_15_1.5` | none, all (US500) | basket 60/4/8 | 2.0 | +4,245 / 7.4% (278) | 4,386 / 8.5% |
| up2 | pair `dz_mom_5_1.5` + `rnd_break_50` | none, ny | basket | 2.0 | +2,921 / 6.4% (202) | 2,998 / 7.8% |
| up3 | pair `sw_fade_15_1.5` + `vclimax_fade_3` | none, ldny | basket | 1.0 | +1,604 / 8.9% (193) | 1,861 / 10.6% |
| xs8 | pair `pd_break_flow` + `pw_break_flow` | gt20, ny (XAU) | SCALP SL10 TP18 H90 | 0.3 | +10,437 / 6.1% (86) | 9,894 |
| xs9 | pair `g3_60z_mom3.0` + `big3_mom_60_2.0` | none, ny | SCALP SL10 TP18 H90 | 0.3 | +11,815 / 11.0% (129) | 13,224 (chồng lấn xs6/xs2) |
| xs10 | pair `sw_fade_15_1.8` + `big3_mom_60_2.0` | gt20, all | SCALP SL10 TP18 H30 | 0.3 | +10,140 / 6.9% (120) | 10,123 (tB 3.09) |
Ghi chú: gp*/up* là TẬP CON của hệ cha (x1/g2/g7, u1/u7/u6/u12/u16) → greedy không chọn (trùng tín hiệu). Chỉ xs10 vào danh mục greedy (đứng thứ 2). Cặp scalp tốt nhất `big3_mom+emapull` = chính xs2 → xác nhận lại xs2. EA scalp: InpCatLoPct = 10×lot×100/30000×100 (vd lot 0.3 → 1.0%).

### KỊCH BẢN CHỐT CUỐI (opt7, universe 36 hệ, lot robust = trung bình lot tối ưu trên A và trên B; DD = equity MT5 gộp)
| Kịch bản | MT5 net 6T | DD MT5 | A / B | tháng+ | Nửa lot | Gap-5% Py | spread×2 DD Py |
|---|---|---|---|---|---|---|---|
| **An toàn** (14 hệ) | +36,064 | 3.7% | 16.8k / 19.3k | 6/6 | +18.0k / 1.9% | 27% | 5.1% |
| **Cân bằng** (15 hệ) | +63,102 | 6.3% | 29.2k / 33.9k | 6/6 | +31.6k / 3.2% | 48% | 7.7% |
| **Mạnh tay** (15 hệ) | +119,372 | 11.0% | 54.5k / 64.9k | 6/6 | +59.7k / 5.5% | 98% | 17.2% |
| Mạnh tay ×1.4 | +167,120 | 15.5% | 76.3k / 90.9k | 6/6 | | ~137% | ~24% |
| Mạnh tay ×1.7 (trần DD<20%) | +202,932 | 18.8% | 92.6k / 110.3k | 6/6 | | ~167% | ~29% |
| ALL-36 mạnh tay | +139,341 | 17.1% | 59.4k / 79.9k | 6/6 | +69.7k / 8.5% | 95% | 24.7% |
| **Đánh tay** 10 scalp xs1–xs10 | +20,143 | 3.3% | 9.4k / 10.8k | 6/6 | | 28% | 3.9% |
| Đánh tay ×3 | +60,430 | 9.9% | | 6/6 | | ~83% | |
| Đánh tay ×5 | +100,717 | 16.5% | | 6/6 | | ~139% | |
So với vòng 6a: An toàn +7%, Cân bằng +7% (DD ~bằng), Mạnh tay: lợi nhuận/DD 10.9 (6a: 10.1); ×1.7 = +202.9k/18.8% vs 6a ×1.5 +189.8k/19.0%. Đánh tay ×5 +100.7k/16.5% vs 6a ×4 +86.1k/15.4%.
**Lot (robust):**
- An toàn: g2 .02, xs10 .09, x1 .02, xs6 .12, xs4 .06, u15 .6, xs2 .09, xs7 .09, u12 2.6, xs3 .05, xs1 .08, u13 1.2, xs5 .09, g5 .01
- Cân bằng: g2 .03, xs10 .16, x1 .03, xs6 .20, xs4 .10, u15 .9, xs2 .12, xs7 .15, u12 3.2, xs3 .13, xs1 .15, g7 .01, u13 2.1, xs5 .16, g5 .02
- Mạnh tay: g2 .08, xs10 .31, x1 .05, xs6 .39, xs4 .20, u15 1.7, xs2 .32, xs7 .38, u12 3.1, xs3 .26, xs1 .34, g7 .02, u13 3.1, xs5 .32, g5 .02 (×1.4 / ×1.7: nhân tất cả, làm tròn bước lot)
- Đánh tay: xs1 .08, xs2 .06, xs3 .04, xs4 .04, xs5 .07, xs6 .05, xs7 .11, xs8 .08, xs9 .04, xs10 .06 (×3 / ×5)
**CẢNH BÁO:** các bậc ×1.4/×1.7/×5 chỉ thoả DD<20% trên lịch sử; gap 5% trong phiên ≈137–167% vốn và spread×2 DD ~24–29% → chỉ dùng sau forward demo, khuyến nghị thực tế: Cân bằng hoặc Mạnh tay ×1.0.
### Độ phủ không gian tìm kiếm: XONG
Mọi họ tín hiệu × {fade, momentum} × {basket, scalp} đã chạy (xem COVERAGE.md, ~39.6k cfg basket + ~340k cfg scalp). Ngoại lệ: gap qua đêm/cuối tuần (3–15 sự kiện → không đủ mẫu), NQ/SI/CL/GEX/MBO (KHÔNG CÓ dữ liệu).


## 12. Vốn 100k / tách vàng & SP500 (vòng 7)
## Vòng 7 — Kịch bản vốn 100k, và danh mục chỉ Vàng / chỉ SP500
Cập nhật: 2026-11-28 15:30 (Asia/Saigon). Khóa hedge cuối tuần (W) BẬT cho mọi basket. Lot làm tròn bước sàn: vàng 0.01, chỉ số 0.1. DD = DD gộp equity MT5 (scale tuyến tính từ deals tick thật đã có; không chạy lại Strategy Tester). Lot robust = trung bình lot tối ưu trên nửa A và nửa B, rồi scale cho vừa ràng buộc DD/spread×2/gap-5%. Mọi kịch bản dưới đây lãi **6/6 tháng**.

So với vốn 40k (vòng 6b): gần như tuyến tính ×2.5 (cùng hệ, lot × ~2.5). Lợi ích đa dạng hóa: cùng vốn 100k, danh mục **chung hai tài sản** có DD thấp hơn rõ và lãi cao hơn danh mục chỉ một tài sản.

**Khuyến nghị thực tế:** Cân bằng hoặc Mạnh tay ×1.0; chạy demo nửa lot trước. Các bậc nhân lot (×1.4/×1.7/×5) chỉ thoả DD<20% trên lịch sử — gap 5% trong phiên có thể vượt 100% vốn, spread×2 đẩy DD lên ~20–29%.

### 12.1 Cả hai tài sản, vốn 100k (15 hệ greedy; đánh tay = 10 scalp vàng)
| Kịch bản | MT5 net 6T | DD MT5 | A / B | Nửa lot | Gap-5% (Py) | spread×2 DD (Py) |
|---|---|---|---|---|---|---|
| **An toàn** | +96,123 | 3.7% | 44.7k / 51.4k | +48.1k / 1.9% | 28.4% | 5.0% |
| **Cân bằng** | +161,631 | 6.8% | 75.0k / 86.6k | +80.8k / 3.4% | 48.3% | 8.4% |
| **Mạnh tay** | +304,204 | 11.0% | 139.3k / 164.9k | +152.1k / 5.5% | 98.8% | 16.9% |
| Mạnh tay ×1.4 | +426,366 | 15.5% | 195.1k / 230.9k | | ~138% | ~24% |
| Mạnh tay ×1.7 | +517,672 | 18.7% | 236.9k / 280.3k | | ~168% | ~29% |
| **Đánh tay** xs1–xs10 | +72,846 | 3.6% | 33.6k / 39.2k | +36.4k / 1.8% | 29.2% | 4.3% |
| Đánh tay ×3 | +218,538 | 10.8% | | | ~88% | |
| Đánh tay ×5 | +364,231 | 18.0% | | | ~146% | |

**Lot An toàn / Cân bằng / Mạnh tay / Mạnh tay ×1.7** (15 hệ):
| Hệ | An toàn | Cân bằng | Mạnh tay | ×1.7 |
|---|---|---|---|---|
| g2 | 0.05 | 0.09 | 0.20 | 0.34 |
| xs10 | 0.24 | 0.40 | 0.79 | 1.34 |
| x1 | 0.05 | 0.07 | 0.12 | 0.20 |
| xs6 | 0.30 | 0.52 | 0.99 | 1.68 |
| xs4 | 0.15 | 0.26 | 0.51 | 0.87 |
| u15 | 1.6 | 2.4 | 4.4 | 7.5 |
| xs2 | 0.24 | 0.31 | 0.81 | 1.38 |
| xs7 | 0.23 | 0.39 | 0.96 | 1.63 |
| u12 | 6.5 | 8.1 | 7.7 | 13.1 |
| xs3 | 0.14 | 0.33 | 0.66 | 1.12 |
| xs1 | 0.20 | 0.38 | 0.85 | 1.45 |
| g7 | 0.01 | 0.02 | 0.05 | 0.09 |
| u13 | 3.2 | 5.2 | 7.7 | 13.1 |
| xs5 | 0.24 | 0.40 | 0.80 | 1.36 |
| g5 | 0.03 | 0.06 | 0.07 | 0.12 |

**Lot đánh tay** (10 scalp vàng, vốn 100k): xs1 0.30, xs2 0.21, xs3 0.17, xs4 0.15, xs5 0.24, xs6 0.16, xs7 0.35, xs8 0.28, xs9 0.15, xs10 0.22. Bậc ×3 / ×5: nhân tất cả rồi làm tròn 0.01.

Tháng (An toàn, USD): 18.8k, 18.0k, 13.0k, 10.9k, 14.6k, 20.7k.

### 12.2 Chỉ Vàng, vốn 100k và 50k (8 hệ greedy: g2, xs10, x1, xs6, xs4, xs7, xs2, gp2)
Tối ưu riêng (không lấy subset của danh mục chung). gp2 vào vì không còn các hệ SP500 để đa dạng hóa. **Mạnh tay gốc** vượt DD 20% trên MT5 (100k: 21.4%; 50k: 20.7%) dù Python báo 18.2%/17.6% — đã cắt lot (×0.906 / ×0.938) để DD MT5 = 19.3%.

| Vốn | Kịch bản | MT5 net | DD MT5 | A / B | Gap-5% | sx2 DD | Lot |
|---|---|---|---|---|---|---|---|
| **100k** | An toàn | +74,963 | 6.9% | 34.7k / 40.3k | 29.3% | 7.9% | g2 .10, xs10 .42, x1 .05, xs6 .28, xs4 .26, xs7 .46, xs2 .32, gp2 .05 |
| 100k | Cân bằng | +126,015 | 11.7% | 58.4k / 67.6k | 49.2% | 13.7% | g2 .17, xs10 .70, x1 .09, xs6 .46, xs4 .43, xs7 .78, xs2 .54, gp2 .08 |
| 100k | **Mạnh tay (đã cắt)** | +208,221 | 19.3% | 96.4k / 111.8k | 82.2% | 20.9% | g2 .25, xs10 1.18, x1 .14, xs6 .81, xs4 .72, xs7 1.26, xs2 .91, gp2 .14 |
| 100k | Đánh tay xs1–xs10 | +71,064 | 3.5% | 33.1k / 38.0k | 29.2% | 4.2% | xs1 .29, xs2 .20, xs3 .14, xs4 .15, xs5 .24, xs6 .16, xs7 .38, xs8 .29, xs9 .15, xs10 .22 |
| 100k | Đánh tay ×5 | +355,318 | 17.6% | | ~146% | | nhân ×5, làm tròn 0.01 |
| **50k** | An toàn | +36,069 | 5.5% | 16.6k / 19.4k | 28.0% | 7.8% | g2 .05, xs10 .21, x1 .02, xs6 .14, xs4 .13, xs7 .23, xs2 .16, gp2 .02 |
| 50k | Cân bằng | +61,656 | 11.0% | 28.5k / 33.1k | 48.3% | 12.9% | g2 .08, xs10 .35, x1 .04, xs6 .23, xs4 .21, xs7 .39, xs2 .27, gp2 .04 |
| 50k | **Mạnh tay (đã cắt)** | +106,622 | 19.3% | 49.3k / 57.3k | 84.3% | 21.6% | g2 .13, xs10 .61, x1 .07, xs6 .41, xs4 .37, xs7 .65, xs2 .47, gp2 .07 |
| 50k | Đánh tay | +34,876 | 3.5% | 16.2k / 18.7k | 28.7% | 4.1% | xs1 .14, xs2 .10, xs3 .07, xs4 .07, xs5 .12, xs6 .08, xs7 .19, xs8 .14, xs9 .07, xs10 .11 |
| 50k | Đánh tay ×5 | +174,378 | 17.3% | | | | nhân ×5, làm tròn 0.01 |

### 12.3 Chỉ SP500, vốn 100k và 50k (5 hệ greedy: u13, u12, u2, up1, up2)
Tối ưu riêng. up1/up2 vào (tập con của u1/u7/u6+u12) vì greedy một tài sản chọn chúng thay cho hệ cha. **Không có scalp US500 pass.** Lot Mạnh tay 100k khá lớn (u12 22.6, u13 21.0) — cần kiểm tra trần lot của sàn trước khi chạy. Tháng 8 yếu nhất nhưng vẫn dương.

| Vốn | Kịch bản | MT5 net | DD MT5 | A / B | Gap-5% | sx2 DD | Lot (u13 / u12 / u2 / up1 / up2) |
|---|---|---|---|---|---|---|---|
| **100k** | An toàn | +49,551 | 5.5% | 20.2k / 29.4k | 29.6% | 7.7% | 6.8 / 5.2 / 4.0 / 5.6 / 6.6 |
| 100k | Cân bằng | +81,769 | 9.4% | 33.1k / 48.7k | 49.6% | 12.6% | 11.0 / 8.5 / 6.9 / 9.4 / 10.7 |
| 100k | Mạnh tay | +167,946 | 18.8% | 69.0k / 99.0k | 99.8% | 24.4% | 21.0 / 22.6 / 12.6 / 19.0 / 20.3 |
| **50k** | An toàn | +24,776 | 5.5% | 10.1k / 14.7k | 29.6% | 7.7% | 3.4 / 2.6 / 2.0 / 2.8 / 3.3 |
| 50k | Cân bằng | +40,645 | 9.3% | 16.5k / 24.2k | 49.2% | 12.5% | 5.5 / 4.2 / 3.4 / 4.7 / 5.3 |
| 50k | Mạnh tay | +83,900 | 18.8% | 34.4k / 49.5k | 99.8% | 24.4% | 10.5 / 11.3 / 6.3 / 9.5 / 10.1 |

### 12.4 Cách tái lập
```
cd v3/code && python opt8.py          # → results/r6/opt8.json (tái dùng U6.pkl, W bật)
cd v3/r4  && python joint8.py         # → r4/joint8.json (scale deals MT5, cap truyền vào, cắt lot nếu DD>19.5%)
```
File: `results/r6/opt8.json`, `r4/joint8.json`, `results/r6/ROUND7_NOTES.md`.

### 12.5 Caveat thêm (vòng 7)
1. Không chạy lại tester MT5: số joint là scale tuyến tính từ deals đã xác minh 100% real ticks (sai số 1–6% như trước). Riêng Mạnh tay chỉ-vàng, DD MT5 lệch lên trên Python nên đã cắt lot.
2. Gap 5% trong phiên không chặn được bằng SL — chỉ giảm bằng lot. Mạnh tay (chung hoặc một tài sản) có gap ≈ 82–100% vốn (bậc nhân còn cao hơn).
3. Vẫn 6 tháng mẫu, multiple testing; cần forward demo nửa lot trước khi tăng.


## 13. Vốn 100 USD = 10.000 cent (vòng 8)
Mục con 8.x bên dưới = 13.x.
## Vòng 8 — vốn 100 USD = 10.000 cent (tài khoản cent)

Bạn sửa vốn: **10k cent = 100 USD**, không phải 100k USD. Phần này tính lại toàn bộ cho tài khoản cent. W (khóa hedge cuối tuần) bật. Số liệu dựa trên deals MT5 100% real ticks đã có (scale tuyến tính theo lot, **chưa chạy lại tester trên server cent**) và engine Python bảo thủ cho gap 5% / spread ×2. Net in USD và cent (×100). Cửa sổ 01/06–27/11/2026.

### 8.1 Thông số hợp đồng đã tra (nguồn web, 28/11/2026)

| Sàn / tài khoản | Vàng | US500 | Nguồn |
|---|---|---|---|
| **Exness Standard Cent** | XAUUSDc: 1 lot cent = 0,01 lot chuẩn = **1 oz**; min **0,01 lot cent** (= 0,01 oz); max 200 lot/lệnh; bước lot: KHÔNG CÓ (bài Help Center chỉ nêu min; em giả định 0,01) | **US500c có trên Cent, chỉ MT5 và Exness platform** (không MT4). Contract size US500c: KHÔNG CÓ. Min lot US500c: KHÔNG CÓ (bài Cent ghi chung 0,01 lot). Em giả định 1 lot cent = 0,01 lot chuẩn = 0,01 USD/điểm (US500 chuẩn contract size 1) | Exness Help Center “Standard Cent account” (cập nhật 27/11/2026) get.exness.help/hc/en-us/articles/17537782786588; “Indices” (13/11/2026) get.exness.help/hc/en-us/articles/17854383867548; “Common trading terms” (23/09/2026) |
| Exness (mâu thuẫn trong nguồn) | | Cùng bài Indices có 1 dòng ghi “Indices are not offered in Standard Cent accounts”, nhưng mục US500 ngay dưới lại ghi Standard Cent có trên MT5 và bài Cent liệt kê US500c. Em tin mục US500 và bài Cent (mới hơn). **Nên xác nhận trong MT5 của tài khoản thật.** US500 chuẩn: min 0,14 lot, contract size 1, pip 0,1 (không phải thông số cent) | cùng nguồn; ogcashback.com nói “no indices” (bên thứ ba, cũ hơn) |
| Exness spread | “từ 0,3 pip” (forex). Spread XAUUSDc / US500c thực tế: KHÔNG CÓ | | Help Center Cent |
| **XM Micro** | 1 lot Micro = 1.000 đơn vị, vàng 1 lot = 1 oz; **min 0,1 lot trên MT5** (0,01 lot trên MT4), bước 0,01, max 100 lot | US500Cash có trong danh sách sản phẩm Micro; contract size / min lot Micro của US500Cash: KHÔNG CÓ | xmtrading.com/account-types/micro (FAQ); XM Help Center “minimum lot size for Micro accounts”; fxfan.club |
| XM — số dư | **Số dư vẫn tính bằng USD**, XM không có tài khoản “cent” thật (số dư không đổi sang cent). 100 USD = 100 USD | | fxfan.club; xmtrading.com |

**Kết luận:** 10.000 cent chỉ khớp **Exness Standard Cent (USC)**. EA đang chạy theo symbol XM (GOLD / US500Cash) nên khi chuyển sang XAUUSDc / US500c phải đổi symbol, nhập lot theo đơn vị lot cent, và tính lại InpCatLoPct (xem 8.5). Em chưa test EA trên server Exness.

### 8.2 Quy đổi lot 100k → 100 USD

- Vốn nhỏ đi 1.000 lần, lot chuẩn L (vàng 1 lot = 100 oz) → L/1.000 lot chuẩn = **L/10 lot cent** (vàng: 1 lot cent = 1 oz). Với US500c cùng công thức nếu giả định ở 8.1 đúng.
- Bước và min lot cent là 0,01 → tương đương bước **0,1 lot chuẩn ở vốn 100k** (thô gấp 10 lần bước 0,01 ở vốn 100k). Hệ nào có lot 100k nhỏ hơn 0,1 thì không đại diện được.
- Cách làm tròn trực tiếp: lot quy đổi < 0,01 lot cent thì **loại**; ≥ 0,01 thì làm tròn gần nhất (lệch có thể tới ±30% với lot nhỏ).

### 8.3 Tính lại trực tiếp từ kịch bản 100k (không tối ưu lại)

Hệ bị loại vì lot < 0,01 lot cent: 
- JOINT_100k_GREEDY_conservative: g2 (0.005 lot cent), x1 (0.005 lot cent), g7 (0.001 lot cent), g5 (0.003 lot cent)
- JOINT_100k_GREEDY_balanced: g2 (0.009 lot cent), x1 (0.007 lot cent), g7 (0.002 lot cent), g5 (0.006 lot cent)
- JOINT_100k_GREEDY_aggressive: g7 (0.005 lot cent), g5 (0.007 lot cent)
- XAU_100k_GREEDY_conservative: x1 (0.005 lot cent), gp2 (0.005 lot cent)
- XAU_100k_GREEDY_balanced: x1 (0.009 lot cent), gp2 (0.008 lot cent)

| Sách | Kịch bản | Số hệ giữ | Net 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD |
|---|---|---|---|---|---|---|---|
| Ghép Vàng+SP500 | An toàn | 11/15 | +71 USD (+7,101 cent) | 3.8% | 6/6 | 25% | 3.3% |
| Ghép Vàng+SP500 | Cân bằng | 11/15 | +127 USD (+12,683 cent) | 5.6% | 6/6 | 47% | 6.6% |
| Ghép Vàng+SP500 | Mạnh tay | 13/15 | +280 USD (+28,039 cent) | 10.8% | 6/6 | 94% | 17.7% |
| Ghép Vàng+SP500 | Đánh tay | 10/10 | +78 USD (+7,763 cent) | 3.7% | 6/6 | 30% | 4.5% |
| Chỉ Vàng | An toàn | 6/8 | +62 USD (+6,218 cent) | 4.7% | 6/6 | 28% | 7.0% |
| Chỉ Vàng | Cân bằng | 6/8 | +104 USD (+10,352 cent) | 8.3% | 6/6 | 50% | 13.9% |
| Chỉ Vàng | Mạnh tay | 8/8 | +193 USD (+19,303 cent) | 13.9% | 6/6 | 77% | 18.4% |
| Chỉ Vàng | Đánh tay | 10/10 | +73 USD (+7,257 cent) | 3.6% | 6/6 | 30% | 4.2% |
| Chỉ SP500 | An toàn | 5/5 | +50 USD (+4,955 cent) | 5.5% | 6/6 | 30% | 7.7% |
| Chỉ SP500 | Cân bằng | 5/5 | +82 USD (+8,177 cent) | 9.4% | 6/6 | 50% | 12.6% |
| Chỉ SP500 | Mạnh tay | 5/5 | +168 USD (+16,795 cent) | 18.8% | 6/6 | 100% | 24.4% |

Nhận xét: bỏ hệ nhỏ (g2, x1, g5, g7) làm net giảm 22–26% ở An toàn/Cân bằng ghép (An toàn 96 → 71 USD, Cân bằng 162 → 127 USD); mạnh tay chỉ-vàng làm tròn x1/gp2 từ 0,014 → 0,01 lot cent nên DD tụt 19,3% → 13,9%, lợi nhuận giảm ít (208 → 193 USD).

### 8.4 Kịch bản tối ưu lại trên lưới lot cent (khuyến nghị cho 100 USD)

Tối ưu lại lot trên lưới 0,01 lot cent (cùng ngưỡng DD / spread ×2 / gap 5% như trước: An toàn 10/15/30, Cân bằng 15/22/50, Mạnh tay 19/28/100), rồi kiểm tra lại trên deals MT5. Làm tròn xuống rồi leo từng bước 0,01 trên toàn mẫu nên **có phần in-sample** — nửa A / nửa B của Python đều dương (xem cột bên dưới).

| Sách | Kịch bản | Số hệ | Net 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD |
|---|---|---|---|---|---|---|---|
| Ghép Vàng+SP500 | An toàn | 12/15 | +112 USD (+11,186 cent) | 4.3% | 6/6 | 30% | 6.2% |
| Ghép Vàng+SP500 | Cân bằng | 14/15 | +190 USD (+19,016 cent) | 8.8% | 6/6 | 50% | 11.0% |
| Ghép Vàng+SP500 | Mạnh tay | 14/15 | +379 USD (+37,889 cent) | 17.0% | 6/6 | 100% | 24.3% |
| Ghép Vàng+SP500 | Đánh tay (xs1–xs10) | 10/10 | +86 USD (+8,570 cent) | 4.2% | 6/6 | 30% | 5.1% |
| Chỉ Vàng | An toàn | 6/8 | +62 USD (+6,218 cent) | 5.1% | 6/6 | 29% | 7.1% |
| Chỉ Vàng | Cân bằng | 7/8 | +130 USD (+12,962 cent) | 8.1% | 6/6 | 50% | 16.2% |
| Chỉ Vàng | Mạnh tay | 7/8 | +210 USD (+21,025 cent) | 14.8% | 6/6 | 96% | 22.8% |
| Chỉ Vàng | Đánh tay (xs1–xs10) | 10/10 | +78 USD (+7,818 cent) | 3.8% | 6/6 | 30% | 4.6% |
| Chỉ SP500 | An toàn | 5/5 | +50 USD (+5,026 cent) | 5.5% | 6/6 | 30% | 7.8% |
| Chỉ SP500 | Cân bằng | 5/5 | +82 USD (+8,229 cent) | 9.5% | 6/6 | 50% | 12.6% |
| Chỉ SP500 | Mạnh tay | 5/5 | +168 USD (+16,845 cent) | 18.9% | 6/6 | 100% | 24.5% |

Bậc nhân lot tối đa (DD MT5 ≤ 19,5%; vượt ngưỡng sx2/gap của các bậc trên, cùng loại với bậc ×1,7 / ×5 ở vốn 100k):

| Sách | Kịch bản | Nhân lot | Net 6T | DD MT5 | Gap 5% | Spread ×2 DD |
|---|---|---|---|---|---|---|
| Ghép — Mạnh tay | | ×1.20 | +450 USD (+45,021 cent) | 17.9% | 120% | 30.6% |
| Chỉ Vàng — Mạnh tay | | ×1.30 | +269 USD (+26,918 cent) | 19.2% | 124% | 28.6% |
| Ghép — Đánh tay | | ×4.60 | +395 USD (+39,512 cent) | 19.4% | 138% | 23.5% |
| Chỉ Vàng — Đánh tay | | ×5.15 | +393 USD (+39,288 cent) | 19.1% | 150% | 23.0% |

**Gap 5% từ 100% trở lên nghĩa là một cú gap 5% trong phiên có thể xóa hết 100 USD** (stop-out 0% của Exness Cent cắt ở 0, nhưng vốn mất sạch). Kịch bản Mạnh tay và mọi bậc ×lot đều ở vùng này.

Lot từng hệ (đơn vị **lot cent**, vàng 1 lot cent = 1 oz; US500c theo giả định ở 8.1):

| Hệ | An toàn | Cân bằng | Mạnh tay | Mạnh tay max |
|---|---|---|---|---|
| **Ghép Vàng+SP500** | | | | |
| g2 | 0.01 | 0.01 | 0.03 | 0.04 |
| xs10 | 0.03 | 0.05 | 0.08 | 0.10 |
| xs6 | 0.04 | 0.06 | 0.13 | 0.16 |
| xs4 | 0.02 | 0.03 | 0.06 | 0.07 |
| u15 | 0.19 | 0.30 | 0.51 | 0.61 |
| xs2 | 0.02 | 0.04 | 0.12 | 0.14 |
| xs7 | 0.03 | 0.04 | 0.10 | 0.12 |
| u12 | 0.77 | 1.00 | 1.00 | 1.20 |
| xs3 | 0.04 | 0.04 | 0.10 | 0.12 |
| xs1 | 0.02 | 0.03 | 0.08 | 0.10 |
| u13 | 0.35 | 0.57 | 0.83 | 1.00 |
| xs5 | 0.02 | 0.04 | 0.08 | 0.10 |
| x1 | loại | 0.01 | 0.02 | 0.02 |
| g5 | loại | 0.01 | 0.01 | 0.01 |
| g7 | loại | loại | loại | loại |
| **Chỉ Vàng** | | | | |
| g2 | 0.01 | 0.02 | 0.02 | 0.03 |
| xs10 | 0.05 | 0.08 | 0.14 | 0.18 |
| xs6 | 0.02 | 0.05 | 0.11 | 0.14 |
| xs4 | 0.03 | 0.05 | 0.08 | 0.10 |
| xs7 | 0.05 | 0.08 | 0.16 | 0.21 |
| xs2 | 0.03 | 0.06 | 0.10 | 0.13 |
| x1 | loại | 0.01 | 0.01 | 0.01 |
| gp2 | loại | loại | loại | loại |
| **Chỉ SP500** | | | | |
| u13 | 0.69 | 1.11 | 2.11 | — |
| u12 | 0.53 | 0.86 | 2.27 | — |
| u2 | 0.40 | 0.70 | 1.26 | — |
| up1 | 0.57 | 0.94 | 1.90 | — |
| up2 | 0.67 | 1.07 | 2.04 | — |

Lot Đánh tay (lot cent): xs1 0.03; xs2 0.03; xs3 0.02; xs4 0.02; xs5 0.03; xs6 0.02; xs7 0.04; xs8 0.02; xs9 0.01; xs10 0.02

### 8.5 Hệ quả cho tài khoản 100 USD

- **Ít hệ hơn:** ở An toàn/Cân bằng ghép chỉ còn 12–14/15 hệ; chỉ-vàng còn 6–7/8. SP500 giữ 5/5 vì lot US500 lớn hơn nhiều so với min (nếu giả định US500c đúng).
- **Lot thô:** bước 0,01 lot cent tương đương 1 oz × 0,01. Hệ lot cent 0,01–0,03 chịu sai số làm tròn lớn; chỉ cần lệch 1 bước là đổi 30–100% lot của hệ đó. Nên chạy demo/real cực nhỏ trước.
- **XM Micro MT5 (min 0,1 lot = 0,1 oz) không dùng được:** chỉ còn 3/15 hệ ghép ở mọi bậc (đều là hệ SP500; hệ vàng cần lot 100k ≥ 1,0), chỉ-vàng 0/8 ở An toàn/Cân bằng và 2/8 ở Mạnh tay, Đánh tay 0/10. MT4 Micro (min 0,01) thì giống Exness nhưng EA này là MT5.
- **Rủi ro US500c:** nếu min lot US500c trên Exness là 0,14 lot cent (như US500 chuẩn ghi min 0,14) thì vẫn đủ cho 5/5 hệ SP500 ở mọi bậc (lot nhỏ nhất ≥ 0,40); nếu contract size khác 0,01 USD/điểm thì mọi lot SP500 phải tính lại. KHÔNG CÓ số chính thức nên cần kiểm tra Specification trong MT5.
- **Spread cent thường rộng hơn:** backtest dùng spread thật của XM. Cột Spread ×2 DD là giả lập spread gấp đôi (+ trượt giá); spread ×3 hoặc spread thực Exness cent: KHÔNG CÓ (chưa tính). Với net trung bình mỗi hệ rất nhỏ so với spread, nên coi bản Cân bằng là giới hạn.
- **InpCatLoPct (scalp, vàng):** = SL_giá × lot_cent × 1 oz ÷ vốn USD × 100. Ví dụ SL $10, 0,05 lot cent, vốn 100 USD → 0,5% vốn. Cần tính lại cho từng hệ scalp xs*.
- **Margin:** KHÔNG CÓ kiểm tra margin. Vị thế vàng vài chục 0,01 oz ≈ vài chục USD notional nên margin nhỏ ở đòn bẩy cao, nhưng đòn bẩy thực tế phụ thuộc tài khoản.
- Chưa chạy MT5 Tester lại trên 100 USD; nên chạy 1 lượt Tester cuối cho kịch bản được chọn.


## 14. Hai tài khoản 100 USD, min lot 0,10 / 0,14 (vòng 9)
Mục con 9.x bên dưới = 14.x.
## Vòng 9 — lot tối thiểu 0,10 (vàng) / 0,14 (US500); hai tài khoản cent 100 USD tách riêng

Bạn xác nhận Exness cũng lấy lot nhỏ nhất khoảng 0,14 (t158u), và sẽ đánh **hai tài khoản cent 100 USD tách riêng**: một chỉ vàng, một chỉ SP500 (t159u).

**Giả định lot tối thiểu (cần xác nhận trên MT5 của tài khoản thật):**
- **Vàng (XAUUSDc / XM Micro):** min **0,10 lot**, bước 0,01, 1 lot = 1 oz. Min 0,10 lấy từ XM Micro MT5 (Help Center). Exness Standard Cent ghi chính thức min 0,01; nếu tài khoản vàng Exness của bạn cũng là 0,14 thì lot starter vàng nâng lên 0,14 và DD / gap tăng khoảng 40%.
- **US500c:** min **0,14 lot**, bước giả định 0,01. Trùng với Exness Help Center “Indices” (13/11/2026, US500 chuẩn min 0,14) và lời bạn. Contract size US500c: vẫn **KHÔNG CÓ** — em giả định 1 lot cent = 0,01 USD/điểm (0,01 lot chuẩn). Nếu Specification khác, mọi lot SP500 phải tính lại.
- Số liệu là deals MT5 100% real ticks đã có, **scale tuyến tính theo lot**, chưa chạy lại Tester trên server Exness Cent. W (khóa hedge cuối tuần) bật. Cửa sổ 01/06–27/11/2026. Net in USD và cent (×100).

### 9.1 Tài khoản SP500, vốn 100 USD (ưu tiên — đủ chạy kịch bản gốc)

Cả 5 hệ của sách chỉ-SP500 (u13, u12, u2, up1, up2) đều trên min 0,14 ở mọi bậc. Vốn tối thiểu để giữ đủ 5 hệ theo đúng tỷ lệ lot gốc: **An toàn 35 USD**, Cân bằng 20 USD, Mạnh tay 11 USD. 100 USD là đủ.

| Kịch bản | Số hệ | Lot cent (u13 / u12 / u2 / up1 / up2) | Lãi 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD | A / B |
|---|---|---|---|---|---|---|---|---|
| An toàn | 5/5 | 0,68 / 0,52 / 0,40 / 0,56 / 0,66 | +50 USD (+4.955 cent) | 5,5% | 6/6 (13, 7, 2, 8, 5, 15) | 30% | 7,7% | 20 / 29 |
| **Cân bằng** | 5/5 | 1,10 / 0,85 / 0,69 / 0,94 / 1,07 | **+82 USD (+8.177 cent)** | **9,4%** | 6/6 (22, 12, 2, 13, 8, 25) | 50% | 12,6% | 33 / 49 |
| Mạnh tay | 5/5 | 2,10 / 2,26 / 1,26 / 1,90 / 2,03 | +168 USD (+16.795 cent) | 18,8% | 6/6 (44, 26, 6, 26, 17, 50) | 100% | 24,4% | 69 / 99 |

**Khuyến nghị tài khoản SP500:** chạy **Cân bằng**. An toàn nếu muốn DD thấp hơn. Không chạy Mạnh tay: gap 5% trong phiên ≈ 100% vốn.

### 9.2 Tài khoản vàng, vốn 100 USD (không chạy đủ kịch bản gốc)

Lot quy đổi từ sách 100k xuống 100 USD (L/10 lot cent) hầu hết dưới 0,10. **An toàn, Cân bằng, Đánh tay gốc: 0/8 và 0/10 hệ** đạt min. Chỉ bản Mạnh tay giữ được xs10 (0,12) và xs7 (0,13): +66 USD, DD 9,6%, gap 59%, 6/6 tháng. Ép tất cả hệ (kể cả giỏ g2/x1/gp2) lên 0,10 lot thì DD MT5 **142%**, gap ~300% — không dùng.

Hệ giỏ (g2, g5, g7, x1, gp2) ở 0,10 lot / 100 USD có DD đơn lẻ 22–87%. Chỉ scalp xs* ở 0,10 lot còn DD đơn lẻ dưới 14%.

**Bộ khởi đầu (mọi hệ 0,10 lot cent = 0,10 oz), đã kiểm deals MT5:**

| Bộ | Hệ (lot 0,10) | Lãi 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD | A / B |
|---|---|---|---|---|---|---|---|
| An toàn hơn | xs7 + xs2 | +56 USD (+5.631 cent) | 7,1% | 6/6 (4, 15, 16, 1, 7, 14) | **28%** | 7,6% | 28 / 29 |
| **Cân bằng (khuyên)** | xs7 + xs10 + xs2 | **+90 USD (+9.011 cent)** | **8,0%** | 6/6 (11, 19, 19, 8, 13, 20) | 48% | 10,8% | 39 / 51 |
| Mạnh hơn | xs7 + xs10 + xs2 + xs6 | +124 USD (+12.388 cent) | 9,4% | 6/6 (16, 30, 22, 1, 23, 31) | 71% | 12,5% | 57 / 67 |
| Mạnh tay 4 hệ (lot tối ưu lại) | xs7 0,16, xs10 0,14, xs6 0,11, xs2 0,10 | +152 USD (+15.252 cent) | 13,1% | 6/6 (21, 39, 24, 4, 27, 37) | 96% | 17,1% | 71 / 82 |

Tháng 9 thường yếu nhất nhưng các bộ trên vẫn dương. **Khuyến nghị tài khoản vàng 100 USD:** bộ 3 scalp **xs7 + xs10 + xs2**, mỗi hệ 0,10 lot. Không chạy hệ giỏ trên tài khoản này. Nếu vàng Exness min thật là 0,14: dùng đúng 0,14, lãi/DD/gap roughly ×1,4 (bộ 3 hệ ≈ DD 11%, gap 67%).

InpCatLoPct (scalp, SL 10 USD, lot 0,10, vốn 100): = 10 × 0,10 × 1 / 100 × 100 = **1,0%**.

### 9.3 Vốn tối thiểu để chạy đủ kịch bản gốc (mọi hệ đạt min lot, giữ tỷ lệ lot 100k, DD% không đổi)

| Sách | An toàn | Cân bằng | Mạnh tay | Đánh tay |
|---|---|---|---|---|
| **Chỉ SP500** (min 0,14) | **35 USD** (nút thắt u2) | 20 USD | 11 USD | — |
| **Chỉ Vàng** (min 0,10) | **2.000 USD** (x1, gp2) | **1.250 USD** (gp2) | 714 USD (x1, gp2) | 714 USD (xs3) |
| Chỉ Vàng nếu min cũng 0,14 | 2.800 USD | 1.750 USD | 1.000 USD | 1.000 USD |
| Ghép 2 tài sản (min 0,10/0,14) | 10.000 USD (g7) | 5.000 USD (g7) | 2.000 USD (g7) | 667 USD (xs4, xs9) |

Mốc vàng nếu chấp nhận bỏ hệ lot nhỏ (x1, gp2, g2): Cân bằng 5 scalp còn lại khoảng **250–500 USD**; Đánh tay đủ 10 hệ từ khoảng **714 USD** (min 0,10) hoặc 1.000 USD (min 0,14). Ở 500 USD, Đánh tay mới giữ được 6/10 hệ.

### 9.4 Một tài khoản 100 USD ghép cả hai mã (không phải kế hoạch của bạn, để đối chiếu)

Sau khi loại hệ dưới min, chỉ còn 3 hệ SP500 (u15, u12, u13): An toàn +20 USD / DD 2,7%; Cân bằng +28 USD / DD 3,6%. Yếu hơn tài khoản SP500 tách riêng (thiếu u2, up1, up2). Ép mọi hệ vàng lên 0,10 lot: DD 116%, gap ~370% — không dùng.

Hai tài khoản 100 USD tách riêng tốt hơn một tài khoản 100 USD ghép, vì tài khoản SP500 giữ đủ 5 hệ và tài khoản vàng chọn được bộ scalp vừa min lot.


## COVERAGE — họ tín hiệu × {fade, momentum} × {basket, scalp SL/TP}
(số cấu hình đã chạy / số cấu hình dương cả A và B; "CHƯA" = chưa thử; cập nhật tự động bởi `code/cov.py`)

| Họ (family) | Fade·basket | Mom·basket | Fade·scalp | Mom·scalp |
|---|---|---|---|---|
| Confluence pairs (đồng pha, 2 tín hiệu trong 30 bar) | 2457 cfg / 1795 A&B+ | 627 cfg / 485 A&B+ | 31064 cfg / 3728 A&B+ | 7987 cfg / 1284 A&B+ |
| Sweep (sw z) | 1096 cfg / 854 A&B+ | 1096 cfg / 507 A&B+ | 12114 cfg / 1157 A&B+ | 6057 cfg / 79 A&B+ |
| Delta z (dz) | 2560 cfg / 1617 A&B+ | 2048 cfg / 1391 A&B+ | 16614 cfg / 1060 A&B+ | 14146 cfg / 675 A&B+ |
| Big prints / whale (g1–g3) | 2916 cfg / 1509 A&B+ | 2916 cfg / 1791 A&B+ | 27375 cfg / 1321 A&B+ | 26835 cfg / 3443 A&B+ |
| CVD divergence / CVD lead | 1224 cfg / 628 A&B+ | 72 cfg / 35 A&B+ | 9869 cfg / 259 A&B+ | 960 cfg / 90 A&B+ |
| Absorption | 2504 cfg / 1376 A&B+ | 2504 cfg / 1390 A&B+ | 16776 cfg / 565 A&B+ | 16391 cfg / 1042 A&B+ |
| Imbalance / stacked | 2904 cfg / 1653 A&B+ | 2904 cfg / 1136 A&B+ | 23532 cfg / 848 A&B+ | 19182 cfg / 545 A&B+ |
| VWAP (z, ATR, cross, flow) | 1096 cfg / 533 A&B+ | 244 cfg / 183 A&B+ | 15406 cfg / 383 A&B+ | 1412 cfg / 44 A&B+ |
| Volume profile POC/VAH/VAL/naked POC/80% rule | 590 cfg / 325 A&B+ | 134 cfg / 71 A&B+ | 8861 cfg / 229 A&B+ | 640 cfg / 31 A&B+ |
| Opening/session range (NY OR, IB, London OR, COMEX OR, Asia) | 425 cfg / 241 A&B+ | 1253 cfg / 824 A&B+ | 5018 cfg / 282 A&B+ | 10120 cfg / 735 A&B+ |
| Prior day/week levels, NR day | 748 cfg / 402 A&B+ | 200 cfg / 162 A&B+ | 10540 cfg / 452 A&B+ | 1638 cfg / 136 A&B+ |
| Round numbers | 72 cfg / 41 A&B+ | 72 cfg / 40 A&B+ | 960 cfg / 0 A&B+ | 960 cfg / 1 A&B+ |
| Cross-asset lead-lag ES↔GC | 2368 cfg / 442 A&B+ | 2424 cfg / 402 A&B+ | 14787 cfg / 843 A&B+ | 14653 cfg / 483 A&B+ |
| Futures return / basis | 252 cfg / 118 A&B+ | 252 cfg / 87 A&B+ | 3360 cfg / 197 A&B+ | 3360 cfg / 41 A&B+ |
| Time-of-day anchors / news | 141 cfg / 51 A&B+ | 141 cfg / 113 A&B+ | 1640 cfg / 114 A&B+ | 1640 cfg / 251 A&B+ |
| Volatility regime: squeeze/expansion/climax | 177 cfg / 84 A&B+ | 177 cfg / 83 A&B+ | 2360 cfg / 184 A&B+ | 2360 cfg / 17 A&B+ |
| Trend pullback (EMA/VWAP) | 75 cfg / 34 A&B+ | 167 cfg / 95 A&B+ | 960 cfg / 0 A&B+ | 4815 cfg / 712 A&B+ |
| Gaps (overnight / weekend) | CHƯA | CHƯA | CHƯA | CHƯA |
| IBS (prior-day close position) | 120 cfg / 109 A&B+ | 81 cfg / 72 A&B+ | 944 cfg / 42 A&B+ | 840 cfg / 123 A&B+ |
| 60-bar high/low break/sweep | 36 cfg / 12 A&B+ | 36 cfg / 15 A&B+ | 480 cfg / 0 A&B+ | 480 cfg / 0 A&B+ |
| Placebo (control) | 512 cfg / 272 A&B+ | CHƯA | 2560 cfg / 50 A&B+ | CHƯA |
| Other | CHƯA | CHƯA | CHƯA | CHƯA |

Gap qua đêm/cuối tuần: chỉ 3–15 sự kiện/6 tháng/asset → dưới ngưỡng 30 tín hiệu, KHÔNG đủ mẫu để kiểm (đã thử ở newsig4, bị loại vì mẫu). Placebo = nhóm đối chứng (không phải họ tín hiệu).
Không thể thử (thiếu dữ liệu): lead-lag NQ/SI/CL (KHÔNG CÓ dữ liệu), GEX / gamma flip / call-put walls (KHÔNG CÓ lịch sử), MBO/queue position (KHÔNG CÓ).
Tổng cấu hình đã chạy: basket 39,621, scalp 339,696 (gồm cả 2 tài sản).
