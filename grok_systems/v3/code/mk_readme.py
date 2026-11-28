# Generates README_SCENARIOS.md (self-contained handoff). Re-run at each round end.
import json,os,datetime,glob
V='/workspace/bt_3m/v3'
J=json.load(open(f'{V}/r4/joint5.json'))
now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
r6=open(f'{V}/results/r6/ROUND6_NOTES.md').read() if os.path.exists(f'{V}/results/r6/ROUND6_NOTES.md') else '_(vòng 6 đang chạy — xem STATUS.md)_'
r7=open(f'{V}/results/r6/ROUND7_NOTES.md').read() if os.path.exists(f'{V}/results/r6/ROUND7_NOTES.md') else ''
cov=open(f'{V}/COVERAGE.md').read() if os.path.exists(f'{V}/COVERAGE.md') else ''
def jrow(k,lab=None):
    r=J.get(k); 
    if not r: return f'| {lab or k} | KHÔNG CÓ | | | | |'
    h=r.get('half',{})
    return f"| {lab or k} | {r['net']:+,.0f} | {r['dd_pct']:.1f}% | {r.get('A',0):,.0f} / {r.get('B',0):,.0f} | {r.get('npos','?')}/6 | {h.get('net',0):+,.0f} / {h.get('dd_pct',0):.1f}% |"
S=f"""# README_SCENARIOS — Hệ thống & kịch bản Vàng (XAU) / SP500 (US500) — bản bàn giao (handoff)
Cập nhật: {now} (Asia/Saigon). Tác giả: Grok Bot (executor XSD-16). Tài liệu tự-đủ (self-contained) cho Grok khác / phát triển sau.
**Không có secret trong tài liệu/code này. Mọi số là BACKTEST (Python bảo thủ hoặc MT5 100% real ticks), KHÔNG phải kết quả live.** Thiếu số → ghi `KHÔNG CÓ`.

## 0. Tóm tắt 1 phút
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
| Vốn chuẩn | XAU 30,000 USD; US500 10,000 USD; danh mục chéo 40,000 USD |
| Lot chuẩn k=1 | XAU basket L0 0.03; US500 basket L0 1.0; lot scale tuyến tính |
| Phiên (UTC, theo `sig_v3.filters`) | ldny = 07–20h; ny = 13–20h; ldn = 07–13h; all = cả ngày; luôn bỏ bar có tin (news) |
| ADX lọc | gt20 = ADX(14, M1 trên CFD) > 20 |

## 2. Định nghĩa đặc trưng chính (order-flow)
- `d{{w}}z`: delta (ask−bid volume) cộng dồn w phút / độ lệch chuẩn cuộn → z.
- `sw{{w}}z`: sweep ròng (lệnh quét nhiều mức giá, mua − bán) cộng w phút, z-score.
- `g1/g2/g3_{{w}}z`: delta của lệnh lớn theo 3 ngưỡng kích thước (g3 = cá mập), w phút, z.
- `imb{{w}}z`, `stk{{w}}`: imbalance chéo footprint (z) và số mức stacked imbalance.
- `ad{{w}}z`: absorption-delta (delta lớn nhưng giá futures không chạy); `fz{{w}}z`: lợi suất futures z; `ar{{w}}z`: lợi suất tài sản chéo (ES cho vàng, GC cho SP) z.
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
{jrow('NEW4','NEW4 (g1 .12, g2 .12, u10 2.5, u11 2.0)')}
{jrow('PortD_G30','PortD-G30')}
{jrow('PortD_G40','PortD-G40')}
{jrow('G30+u12,u13 full','PortD-G30 + u12 3.0 + u13 3.0')}
{jrow('G30+g3,g5,u12,u13 full','PortE = PortD-G30 + g3 .06 + g5 .04 + u12 3.0 + u13 3.0')}
{jrow('G30+g3,g5,u12,u13 x0.5','PortD-G30 + (g3,g5,u12,u13)×0.5')}
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
Chế độ CSV điểm vào: `InpVao=4`, `InpCsvChung=true`, `InpFileCsv=brain2\\<job>_mt5.csv` (thư mục Common\\Files), CSV cột `thoi_gian,ma,chieu,gia,nguon,lot` (giờ server).
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
| `pdf/TomTat_KichBan_Vang_SP500_2026-11-28.pdf` | bản PDF tóm tắt 6 trang (kịch bản 100k, chỉ vàng, chỉ SP500) |
| `SUMMARY_V3.md` | nhật ký đầy đủ các vòng 1–6 (bảng số) |
| `COVERAGE.md` | danh sách họ tín hiệu đã/chưa thử |
| `code/` | toàn bộ code Python (engine, tín hiệu, battery, tối ưu, MT5 job builders) |
| `results/` | kết quả tóm tắt (json/md/csv/parquet nhỏ) — không có dữ liệu thô |
| `ea/BRAIN_XuLiLenh_r5.mq5` | EA MT5 có khoá hedge cuối tuần |
Máy nhà: `E:\\GrokWork\\bt_v3\\` (bản đồng bộ đầy đủ), MT5 runs `E:\\GrokWork\\mt5_runs\\` (`runq.py`, `results_p4.jsonl` vàng, `results_p6.jsonl` SP500, `reports\\v5_*.htm`). Box: `/workspace/bt_3m/v3/`.

## 10. Chạy lại (how to re-run)
```bash
# môi trường: python 3.10+ với numpy pandas numba pyarrow
cd v3/code
python newsig4.py XAU          # screen họ tín hiệu (newsig/newsig2/newsig3/newsig4) → results/newsigN_<asset>.parquet
python batnew3.py US500        # battery (A/B, placebo, detrend, reverse, spread, delay2)
python scalp2.py XAU           # pass scalp SL/TP trên các họ basket
python pf5.py                  # đánh giá danh mục: net, DD, spread×2, gap5, wk10, A/B (policy W)
python stress5.py              # stress spread/slip
python mk_v5.py                # tạo CSV điểm vào + queue MT5 (sau đó chạy E:\\GrokWork\\mt5_runs\\runq.py q.json trên máy Windows)
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
{r6}

## 12. Vốn 100k / tách vàng & SP500 (vòng 7)
{r7}

{cov}
"""
open(f'{V}/README_SCENARIOS.md','w').write(S); print('ok',len(S))
