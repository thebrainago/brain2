# Ghi chú nâng cấp (Grok trên brain2) — cập nhật 2026-10-10 (17:10, giờ VN)


## Vòng "LƯỚI MARTINGALE" (sau 54c8597e) — Breakout5 / Breakout5-2-2 dịch đúng như EA
### 1. Đọc (`nhan/ro_mql.py`: `doc_luoi` + trình thông dịch MQL nhỏ `_ThongDich`)
Hàm đóng của hai EA: cập nhật đỉnh `peakwin=MathMax(peakwin,profits)` (không về 0 khi lỗ) →
`if(peakwin>=E && profits<=peakwin*0.7) CloseAll()` → **cổng bar** `if(curTime==prevTime) return;`
→ khối lưới: `up = initup && giá <= S`, `down = !initup && giá >= S` → thêm lệnh **CÙNG chiều**,
`S = BID ∓ 30 point`, `volume = round2(lastvolume × 1.45)`, `peakwin=0`. KHÔNG giới hạn số lệnh.
- Khối lệnh không đọc bằng regex từng dòng: được **chạy thử** bằng một trình thông dịch tập con
  MQL5 (khai báo, gán, `if/else`, `SymbolInfoDouble(BID|ASK)`, `_Point`, `MathRound`,
  `NormalizeDouble`, hàm thuần chỉ phụ thuộc input như `GetStartVolume()`), cho cả hai trường hợp
  lệnh đầu mua / bán. Biến không rõ trong điều kiện, hàm lạ có thể có tác dụng phụ, điều kiện phụ
  thuộc số lệnh (ngoài `postotal>0`) → `_Kh` → **không dịch** (không đoán).
- Chuỗi lot lấy bằng cách chạy THẬT phép gán `lastvolume` 54 bước (không đoán công thức):
  0.02 → 0.03, 0.04, 0.06, 0.09, 0.13, 0.19, 0.28, 0.41, … (Breakout5 `MathRound(x*100)/100` và
  5-2-2 `NormalizeDouble(x,2)` + `if(volume<0.02)` cho cùng chuỗi — test kiểm).
- 5-2-2: `expectation = takeprofitamountperstartvolume × GetStartVolume() = 250×0.02 = 5` (tính từ
  input); lọc magic (`PosTotal`, `IsTRadeOpen`, `GetProfits`, `CloseAll(all=true)`) → giả định tài
  khoản chỉ có EA này (ghi `gia_dinh`). Nhánh `else if(zonesequence!=0)` (hedge vùng) **không tới
  được với input mặc định** `hedgeatlevel=0` → mã chết; đổi `hedgeatlevel=3` → KHÔNG dịch (test).
  Ở input mặc định 5-2-2 ≡ Breakout5 (khóa `ro` giống hệt → vòng lặp bỏ trùng).
- Hàm mở: `prevTime` chỉ gán SAU khi mở lệnh → **mở tối đa 1 lần/bar nhưng ở BẤT KỲ tick nào**
  khi đang không có lệnh (`ro.cong_mo_bar`). Cặp mua `giá < pivot giờ` / bán `giá >= pivot` bù nhau
  → khi rổ chốt GIỮA bar, EA vào lại ngay theo giá lúc đó (`vao_lai_giua_bar` → `muc_lai` ở
  `ngu_phap.sinh_chan`; `doc_ma._vao_lai_giua_bar` chỉ gắn khi chắc: 2 chân ngược chiều, một điều
  kiện `close <phép> M` cùng M, hai phép bù nhau, có cổng mở bar).
- Đột biến kiểm (test): `volumefactor=2` → lot 0.04/0.08/0.16; `HedgeRange=50` → ±50 point;
  `takeprofit…=500` → mốc 10$; bỏ cổng bar, chèn hàm lạ, `hedgeatlevel=3`, hoa hồng > 0,
  khối lượng theo vốn (`AccountInfoDouble`) → đều KHÔNG dịch.
### 2. Mô phỏng (`mo_phong.chay_he`, khóa `ro.luoi`)
- Lưới chỉ xét ở **lần gọi hàm đóng ĐẦU TIÊN của mỗi bar** (cổng `prevTime` toàn cục của hàm
  đóng — cả khi lần gọi đó là tick ngay sau lệnh mở), tại giá lúc đó (≈ open); không thêm giữa bar.
- Chốt đỉnh giữa bar tìm CHÍNH XÁC trên từng đoạn đơn điệu (như rổ hedge). Thêm lệnh khi vừa
  `CloseAll` cùng tick (`postotal` cũ) → đếm `ro_bat_thuong`, không mở.
- Chẩn đoán mới `chi_tiet["luoi"]`: số lệnh / lot lớn nhất một rổ, lỗ thả nổi lớn nhất ($).
  **KHÔNG mô phỏng** ký quỹ / stop-out / `SYMBOL_VOLUME_MAX` của sàn (phụ thuộc tài khoản & sàn,
  không có trong mã) — đây là giới hạn lớn nhất của kết quả lưới.
### Số đo
| | 54c8597e | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 11/22 = 50,0% | **13/22 = 59,1%** (8 tín hiệu + 3 hedge + **2 lệnh thêm của lưới**) |
| Phân loại | dịch 8+3 · quản lý vị thế 4 · mã chết 5 · chưa dịch 2 | dịch 8+5 · quản lý vị thế **1** (hedge Breakout4) · mã chết **6** (+ nhánh hedge vùng 5-2-2 ở input mặc định) · chưa dịch 2 |
| Thoát lệnh đúng EA | B1, B2, B2-2, B3, Template | + **Breakout5, 5-2-2 (lưới + chốt đỉnh 5$)** — không còn hệ nào thoát theo `giu` N bar trong mẫu |
| Test lõi + mới | 152 xanh | **165 xanh** (`test_luoi_martingale.py` 13; 1 kỳ vọng cũ sửa: 5-2-2 có 2 điểm vào dịch được) |
| 70 file test chạm `doc_ma/ngu_phap/mo_phong/vong/chi_phi/ro_mql` | 1068 xanh / 40 đỏ / 9 lỗi | **1081 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (đỏ cũ giống hệt bản gốc trên cùng tập file; 2 đỏ `test_sua_bang_llm` chỉ hiện khi chạy cả bộ — phụ thuộc thứ tự, chạy riêng xanh ở cả hai bản) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ THẬT
`7 bóc được, 1 trùng (Breakout5 = 5-2-2), 6 chạy được → **giữ lại: 0**` (`/workspace/vong_eurusd_luoi.json`).
Ngưỡng KHÔNG đổi: t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47 / ≥20 lệnh, phí thật.
| hệ | trước (giu N bar, riêng từng chân), kiểm | **bây giờ** (lưới đúng EA), kiểm | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout5-2-2 (= Breakout5) | mua −1,65/49 · bán +0,39/93 | **+1,06 / 465 rổ** (842 lệnh thêm) | **+1,4 / +1,0** → không giữ |
| các hệ khác | — | không đổi so với 54c8597e | — |
- Lưới trên EURUSD: phần tối ưu tối đa **17 lệnh/rổ, lot 7,99, lỗ thả nổi 6.086 $** (lệnh đầu 0,02 lot);
  phần kiểm 13 lệnh, 1,81 lot, 1.431 $. Mọi rổ đóng bằng chốt đỉnh (không có cắt lỗ).
- **PLACEBO (random walk `--gia-lap-duong`, CÓ phí, seed 1-10): lưới cho Sharpe kiểm DƯƠNG 10/10
  seed (+0,16 … +2,35, trung bình ≈ +1,1)** — đúng đặc tính martingale (thắng nhỏ đều, đuôi phá sản
  hiếm, không xảy ra trong mẫu hữu hạn và không mô phỏng ký quỹ). Nên Sharpe +1,06 trên EURUSD
  **KHÔNG phân biệt được với giả dược → KHÔNG phải bằng chứng edge**. Giữ lại 0/10 seed placebo.
- **Kết luận vẫn như các vòng trước: edge sau phí được giữ = 0.** Dịch đúng hơn tăng độ trung thực
  (thoát lệnh, khối lượng, vào lại giữa bar) nhưng không tạo ra cơ chế qua ngưỡng.

### Breakout4 (PivotsDay R1/S1) — BỎ QUA có ghi lý do (không đoán)
Có mã `MultiPivots.mqh` (/tmp, peterthomet), nhưng dịch chắc chắn cần cả ba thứ chưa có:
1. **`±5*_Point`** quanh R1/S1 (`PivotsIsPivotRange(close+5pt, close−5pt, …)`): phụ thuộc symbol;
   DSL `toan_hang` không biết `_Point` → phải thêm tham số tường minh `diem` vào lớp tín hiệu
   (hiện chỉ mô phỏng biết `diem`). Không tự gán 1e-5.
2. **Biên ngày của pivot**: `PivotsFindWeekDayStart` tự dò giờ đầu ngày từ khe cuối tuần (>86400 s)
   trên giờ máy chủ, `PivotsCalculatePivotRange(DAY)` + `PivotsCleanupWeeekendAndDaysGaps` — cần
   dịch nguyên văn (Chủ nhật / ngày lễ) mới đúng; `PivotsDayList[1]` là ngày nào phải kiểm tay.
3. **Vào lệnh MỖI tick** (cổng `prevTime` đã bị comment) khi giá rơi VÀO DẢI [L−5pt, L+5pt] →
   mô phỏng cần kiểu kích hoạt "dải" trong bar (chưa có). Kèm luật 1 lệnh/ngày + rổ hedge (đã đọc được).
→ Breakout4 vẫn `co_che=0`; hedge của nó vẫn `quan_ly_vi_the` ("lệnh đầu của rổ chưa dịch").

### Vấn đề mở (ưu tiên vòng sau)
1. **Cổng giữ cho lưới/martingale**: Sharpe/t không phải phép thử hợp lệ (placebo dương 10/10). Cần
   mô hình ký quỹ/stop-out với vốn & đòn bẩy KHAI BÁO, hoặc so với phân phối placebo cùng cấu trúc,
   trước khi một hệ lưới được phép "giữ". (Chưa đổi ngưỡng — chỉ ghi lại.)
2. `SYMBOL_VOLUME_MAX` / ký quỹ: tham số hóa tường minh (`lot_toi_da`, vốn) khi có thông số sàn.
3. Breakout4: ba mục trên. CurrencyStrength1 (`CSValues[s1]`, iCustom), Pivots1: chưa dịch.
4. (cũ) ngưỡng tiền theo USD; `MinStopDistance`; đường giá trong bar nên kiểm bằng M1.

---

## (trước) Vòng "RỔ HEDGE + SL/TP ATR" (sau 21cc69dc) — thoát lệnh Breakout2/2-2/3 và Template đúng như EA
### 1. Rổ lệnh Breakout2/2-2/3 (`nhan/ro_mql.py` mới, gắn vào `doc_ma`)
Trước: ba EA này đóng lệnh sau `giu` bar — một hệ KHÁC hẳn. Mã thật: `OnTick` gọi
`checkForClose()` MỖI tick khi có vị thế, hàm đó làm việc trên TỔNG lời lỗ (tiền) của cả rổ:
`profits=GetProfits()` → cập nhật đỉnh `peakwin` → `if(peakwin>=45 && profits<peakwin*0.9) CloseAll()`
→ `if(profits<=-120) CloseAll()` → hedge NGƯỢC chiều khi số lệnh == 1.
- `doc_ro(vb)` đọc đúng các dạng đó, câu lệnh lạ trong phần mã sống → trả `None` + lý do
  (không đoán). Phần sau `return;` vô điều kiện bỏ qua (mã chết). Kết quả = khoá DSL `ro`:
| EA | đỉnh | cắt lỗ | hedge |
|---|---|---|---|
| Breakout2 | ≥45$, đóng khi <0,9·đỉnh; đỉnh về 0 khi lời ≤0 | −120$ | 0,4 lot khi BID chạm ASK_vào − 300 point (mua) / BID_vào + 300 (bán) |
| Breakout2-2 | như trên | −120$ | 0,3 lot khi lời ≤ −30$ |
| Breakout3 | ≥45$; đỉnh = max từ lúc vào/hedge (về 0 khi vào lệnh và khi hedge) | −120$ | 0,4 lot, khoảng = input `HedgeRange`=300 |
- Khối `if(postotal==22)` (Breakout2/3/4): KHÔNG BAO GIỜ tới được — lệnh đầu chỉ mở khi không có
  vị thế, mỗi khối hedge thêm đúng 1 lệnh → số lệnh ∈ {1,2}. Xếp `ma_chet` (giả định tài khoản chỉ có EA này).
- Breakout2 ≡ Breakout3 về hành vi (số đo giống hệt): đỉnh chỉ có tác dụng khi ≥45, mà lời rơi
  từ ≥45 sẽ bị chốt trước khi về ≤0, nên hai cách reset đỉnh cho cùng kết quả — kiểm chứng tốt.
- Giả định ghi trong `gia_dinh`: lời lỗ tính bằng tiền yết giá (USD cho EURUSD), hợp đồng
  100.000/lot, tài khoản HEDGING, `_Point`=1e-5 (ước từ giá, có cảnh báo).
### 2. Mô phỏng rổ (`mo_phong.chay_he`, chân có `ro`)
- Lời lỗ EA = Σ lot·100000·(chiều·(giá−giá_vào)) − 1 spread mỗi lệnh (giá là BID như biểu đồ MT5).
  Trên mỗi đoạn đơn điệu của đường giá trong bar lời lỗ TUYẾN TÍNH theo giá → mức chốt đỉnh /
  cắt lỗ / hedge tìm được CHÍNH XÁC (không lấy mẫu). Thứ tự trong một tick y hệt mã: cập nhật
  đỉnh → chốt → cắt lỗ → hedge (với `postotal` đọc trước khi đóng). Gap qua mức → khớp ở open.
  Ca EA mở hedge “mồ côi” ngay sau CloseAll (chỉ khi gap) → đếm `ro_bat_thuong` (EURUSD: 0).
- Lợi suất theo vốn danh nghĩa LỆNH ĐẦU (hedge 0,4 lot = trọng số 4); phí spread/trượt theo
  khối lượng từng lệnh; qua đêm tính RIÊNG lệnh mua và lệnh bán (tài khoản hedging trả cả hai).
- `so_lenh` = số rổ (đơn vị độc lập để đếm đủ lệnh); số hedge báo riêng.
### 3. SL/TP ATR của Template (`ro_mql.doc_sltp_kc`) — form chắc chắn nên đã dịch
`OpenTrade(sig>0?BUY:SELL, atr*InpSlAtrMult, atr*InpTpAtrMult)`; trong `OpenTrade`:
`slDist=MathMax(slDist,MinStopDistance())`, `sl=price−dir·slDist`, `tp=price+dir·tpDist`,
`lot=LotsForRisk(slDist)` (1% vốn mỗi SL), `atr` = `CopyBuffer(iATR(...,InpAtrPeriod),0,1,1,v)`.
- `sltp: {sl_kc: 2×ATR14, tp_kc: 3×ATR14, sl_kc_min_spread: 3, rui_ro: 0.01}`; ATR kiểu MT5 =
  trung bình CỘNG của TR (`{"chi_bao":"atr","kieu":"sma"}` mới — DSL cũ là Wilder); bar 1 → trễ 0.
- `MinStopDistance`: STOPS/FREEZE level phụ thuộc sàn → GIẢ ĐỊNH = 0 (→ 3×spread), ghi `gia_dinh`.
- Trọng số lệnh = rui_ro·giá/khoảng_SL (khối lượng theo rủi ro). `SpreadOK()` (≤30 point) → lọc
  bằng spread theo giờ của mô hình chi phí. `CountMyPositions()>0` → một vị thế một lúc (chạy
  NHÓM qua `nhom_he`); hai điều kiện này bỏ khỏi `bo_qua_quan_tri` vì đã mô hình hoá.
- Tham số EA phơi cho tối ưu: `sltp_atr_n`, `sltp_sl_he`, `sltp_tp_he` (ứng viên ×0,5…×2).
- Đột biến mã (ATR ở bar 0, SL dạng khác) → KHÔNG dịch (test).
### Số đo
| | 21cc69dc | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **11/22 = 50,0%** = 8 tín hiệu thanh nến + **3 lệnh hedge mô phỏng đúng trong `ro`** |
| Phân loại 22 điểm vào | dịch 8 · quản lý vị thế 10 · mã chết 2 · chưa dịch 2 | dịch 8 + hedge dịch 3 · quản lý vị thế 4 (Breakout4 hedge vì lệnh đầu chưa dịch; lưới martingale Breakout5/5-2-2) · mã chết 5 (+3 khối `postotal==22` không tới được) · chưa dịch 2 |
| Tín hiệu thanh nến | 8/10 | 8/10 (không đổi — không nới gì ở phần tín hiệu) |
| Thoát lệnh đúng EA | Breakout1 | Breakout1 + **Breakout2, 2-2, 3 (rổ)** + **Template (SL/TP ATR)**; còn `giu` N bar: Breakout5-2-2 (lưới) |
| Test lõi (`test_doc_ma*`, `test_trong_bar`, `test_sltp_he`, `test_toan_hang_tuyen_tinh`) + mới | 122 xanh | **152 xanh** (`test_ro_hedge.py` 20, `test_sltp_atr.py` 10; 3 test cũ sửa kỳ vọng phân loại) |
| 69 file test chạm `doc_ma/ngu_phap/mo_phong/vong/chi_phi` | worktree sạch 21cc69dc: 1028 xanh / 50 đỏ / 9 lỗi thu thập | **1068 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (10 đỏ chỉ ở worktree sạch: thiếu file dữ liệu cục bộ) |
| Placebo `--gia-lap-duong` (7 dòng/seed) | — | CÓ phí seed 1-12: **giữ 0/84**; KHÔNG phí seed 1-20: giữ 2/140 (1,4%: Template seed 5, Breakout5-2-2 bán seed 20) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ (mặc định)
`9 bóc được, 2 trùng (Breakout5=5-2-2), 7 chạy được → **giữ lại: 0**`. Kết quả `/workspace/vong_eurusd_ro.json`.
| cơ chế | trước (21cc69dc) kiểm sau tối ưu, t | **bây giờ**: kiểm gốc → sau tối ưu | t (tối ưu/kiểm) | ghi chú |
|---|---|---|---|---|
| HỆ Breakout1 | −2,36/187, −1,3/−2,1 | −4,10/204 → −2,36/187 | −1,3/−2,1 | không đổi |
| HỆ Breakout2-2 (rổ, hedge theo lời −30) | −3,03/217 (giữ N bar), −1,4/−2,8 | −3,07/93 → −1,67/88 (24+37 hedge) | −1,6/−1,5 | giờ 8→9 |
| HỆ Breakout2 (=Breakout3) (rổ, hedge 300 point) | (trùng 2-2 vì cùng điểm vào) | −3,29/110 → −2,07/112 (38+36 hedge) | −0,2/−1,9 | giờ 8→11 |
| HỆ Template (SL/TP ATR, rủi ro 1%, 1 vị thế) | mua −1,60/50 · bán +0,43/39 (riêng, giữ N bar) | −4,31/359 → −0,33/53 | −0,7/−0,3 | ATR 10, SL 2,5×, TP 12× |
| Breakout5-2-2 mua / bán | −1,65/49 · +0,39/93 | không đổi | −0,6/−1,5 · −1,1/+0,3 | thoát vẫn `giu` (lưới martingale chưa dịch) |
Toàn kỳ (không chia), có phí: Breakout2 427 rổ = 285 chốt đỉnh + 141 cắt lỗ −120$, giữ trung vị
15 bar; lời TB/rổ trước phí ngoài spread ≈ −2,5$ → spread (0,47 log) ăn hết. Kết luận vẫn như vòng
trước: mô hình thoát lệnh đúng hơn KHÔNG làm xuất hiện edge sau phí.

### Vấn đề mở (ưu tiên vòng sau)
1. Breakout5 / 5-2-2: lưới martingale (`stepprice`, `volumefactor`, `hedgeatlevel`, `zonesequence`,
   cổng `prevTime` mỗi bar) — chưa dịch, vẫn `giu` N bar. Breakout4: lệnh đầu cần `PivotsDay` R1/S1.
2. Ngưỡng tiền (45/−120/−30$) chỉ đúng cho cặp yết giá USD + tài khoản USD; cặp khác cần quy đổi.
3. `MinStopDistance` giả định STOPS/FREEZE level = 0; nên đọc từ dữ liệu sàn khi có.
4. Đường giá trong bar vẫn là giả định (gần open trước); rổ hedge nhạy với thứ tự chạm → nên kiểm
   bằng M1 (cũ). Tối ưu Template 4 tham số → t tối ưu trên placebo thường >2; phần KIỂM là chốt chặn.
5. (cũ) `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn, bộ chọn sàn.

---

## (trước) Vòng 10/10 đêm — SL/TP + KÉO SL + MỘT LỆNH/NGÀY + MÔ PHỎNG CẢ HỆ (phí thật)
### 1. Đọc từ mã EA (`nhan/doc_ma.py`)
- **SL/TP** (`_sltp_mql`): từ `PositionOpen(sym, type, vol, price, sl, tp)` tìm phép gán
  trong nhánh `if(upbreakout){...}`: `price = SymbolInfoDouble(_Symbol,SYMBOL_ASK|BID)`,
  `sl = <mức>` (phải dịch được thành mức CỐ ĐỊNH trong bar), `tp = price ± ((price−sl)·k)`
  với k là hằng/input (`TPFactor`). Breakout1: SL mua = đáy phiên 5-8h, SL bán = đỉnh
  phiên, TP = 1R. Mẫu khác (TP hằng số pip, `price−calculateDistance`) → KHÔNG đoán, ghi
  `gia_dinh`, giữ `giu` như cũ. Breakout2/2-2/3/5 mở lệnh `NULL, NULL` → không có SL/TP.
- **Kéo SL** (`_keo_sl_mql`): `sl = MathMax(sl, lowrange)` + `PositionModify` trong khối
  `if(posType==POSITION_TYPE_BUY)` (MathMin cho SELL), `sl` đọc từ `POSITION_SL`, hàm gọi
  từ `OnTick` → Breakout1: kéo theo `thap_nhat(low,3)` / `cao_nhat(high,3)` (3 bar đã đóng).
- **Sửa lỗi kèm** (`_bang_mql`): mảng `highs/lows` được `Copy*` ở NHIỀU hàm; bản cũ giữ lần
  Copy CUỐI trong file nên `lowrange` của `checkForClose` bị dịch thành đáy PHIÊN. Giờ lấy
  lần Copy gần nhất TRƯỚC phép gán. (JSON 14 cơ chế trước/sau giống hệt ngoài khoá mới.)
- **Một lệnh/ngày** (`_mot_lenh_ngay_mql`): `if(a==dt.day || b==dt.day) return;` trước lệnh
  + `if(up) a=dt.day;` sau lệnh → `"mot_lenh_ngay": {"nhom", "chan_boi", "dat"}`; guard bỏ
  khỏi `bo_qua_quan_tri` (giờ được mô hình hoá). Có ở Breakout1, 2, 2-2, 3.
- **Cờ vs lọc** (`trong_bar.loc`): `bool up = current[0].high > H;` là CỜ (cực trị bar đang
  chạy, bật là giữ suốt bar); `if(up && close<MA) return;` là LỌC gắn với cờ. Đo trên
  EURUSD: 42/682 lệnh (6%) của mô hình độc lập là lệnh EA KHÔNG vào được (giá đã xuyên
  biên kia trong cùng bar → hai lọc MA trái nhau → `return` hết bar).
### 2. DSL (`nhan/ngu_phap.py`)
- Khoá mới: `"sltp": {"sl": toán hạng, "tp": hệ số R | null, "keo": toán hạng | null}`,
  `"mot_lenh_ngay"`, `trong_bar.loc`; `kiem_khai_bao` kiểm cả ba.
- `sinh_chan(spec, df)` → mảng biết tại close bar i (cho/mức/SL/kéo/cờ/lọc).
- `tham_so_cua`: có `sltp` thì KHÔNG phơi `giu` (EA không đóng theo giờ) mà phơi `sltp_tp`
  (TPFactor) và `sltp_keo_n`; `ap_tham_so` đặt ngược được.
### 3. Mô phỏng (`nhan/mo_phong.chay_he`)
Một tài khoản, nhiều chân: một vị thế một lúc (`if(PositionSelect) checkForClose(); else
checkForOpen();`), luật ngày theo NGÀY-TRONG-THÁNG như EA, tick đầu: hết giờ/gap qua SL/TP
→ đóng ở open, rồi kéo SL (chỉ siết, bỏ nếu mức mới vượt giá hiện tại – MT5 từ chối).
Đường giá trong bar: O → cực trị GẦN open hơn → cực trị kia → C (cùng quy tắc dự án ở
`chay_tpsl`, không mặc định SL). Đóng giữa bar xong vẫn có thể vào lại (EA chạy mọi tick).
Chặn chéo cờ/lọc như trên. `nhat_ky=` ghi từng lệnh để soát tay. Không nhìn trước: test cắt.
### 4. Vòng lặp (`vong_thu_nghiem.py`)
- Các chân cùng `mot_lenh_ngay.nhom` chạy CHUNG (`danh_gia_nhom`), một dòng kết quả “HE …”,
  in thêm từng chân + mô hình cũ (riêng, giữ N bar) để so.
- Tối ưu cả hệ (`toi_uu_nhom`): tham số có mặt ở mọi chân với CÙNG giá trị là MỘT input của
  EA (giờ, chu kỳ MA, TPFactor, kéo SL) → buộc chung; ứng viên TPFactor {0.5…3}R.
- Ngưỡng giữ KHÔNG đổi: t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47 lệnh tối ưu & ≥20 lệnh kiểm, phí thật.
- `--he-so-spread F`: chỉ là ĐỘ NHẠY (nhân spread đo được), mặc định 1 = phí thật.

### Số đo
| | 9c39b674 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **8/22 = 36,4%** (vòng này sửa ĐỘ ĐÚNG mô phỏng, không đổi tỷ lệ) |
| Cơ chế có SL/TP thật / luật ngày | 0 / 0 | **2 (Breakout1) / 8 chân (Breakout1, 2, 2-2, 3)** |
| `test_sltp_he.py` (mới) | — | **18 xanh** (đọc SL/TP/kéo/luật ngày + 5 đột biến mã EA, khớp giá tay: TP, gap SL, kéo SL, luật ngày bán chặn mua, một vị thế, chặn chéo cờ/lọc, phép cắt, placebo) |
| `test_doc_ma*`, `test_trong_bar`, `test_toan_hang_tuyen_tinh` | 104 xanh | 104 xanh (2 test sửa kỳ vọng: Breakout1 giờ là 1 dòng NHÓM 2 chân) |
| 54 file test chạm `doc_ma`/`ngu_phap`/`mo_phong`/`vong` | (worktree sạch 9c39b674) 920 xanh / 46 đỏ / 5 lỗi | **948 xanh / 36 đỏ / 5 lỗi, 0 đỏ mới** (10 đỏ chỉ ở worktree sạch – thiếu file dữ liệu cục bộ; đỏ còn lại có sẵn: scipy, nao.db…) |
| Placebo `--gia-lap-duong` seed 1-16, KHÔNG phí | — | **giữ 0/16** (hệ Breakout1: Sharpe kiểm gốc TB +0,28; t tối ưu thường >2 – quá khớp trong mẫu, phần kiểm chặn được) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ (mặc định)
Spread 1,63 bps/chiều (XM), trượt 0,41 bps, qua đêm mua +2,48%/bán −0,45%/năm.
`10 bóc được, 4 trùng, 6 chạy được → **giữ lại: 0**`. Kết quả: `/workspace/vong_eurusd_sltp.json`.
| cơ chế | tối ưu: gốc → tốt nhất (sh/lệnh) | kiểm sau tối ưu | t (tối ưu/kiểm) | ghi chú |
|---|---|---|---|---|
| **HỆ Breakout1** (mua+bán, SL/TP/kéo/1 lệnh ngày) | −3,12/474 → −0,96/426 | −2,36/187 (mua −1,61/88, bán −1,72/99) | −1,3/−2,1 | tham số chọn: TP 3R, kéo 4 bar, giờ 9-14, SMA 19 trễ 20 |
| (cũ, cùng phí) Breakout1 mua / bán riêng, giữ 1 bar | | −1,01/124 · −0,50/113 | −1,0/−0,9 · −0,1/−0,5 | mô hình SAI (không SL/TP, không luật ngày) |
| HỆ Breakout2-2 (=2=3; giu, luật ngày) | −10,1/508 → −0,98/507 | −3,03/217 | −1,4/−2,8 | thoát vẫn `giu` (lưới hedge chưa dịch) |
| Breakout5-2-2 mua / bán | | −1,65/49 · +0,39/93 | −0,6/−1,5 · −1,1/+0,3 | không đổi |
| Template mua / bán | | −1,60/50 · +0,43/39 | −0,5/−1,4 · −0,9/+0,4 | không đổi |
So sánh: **không phí** hệ Breakout1 GIỮ (kiểm +1,75/194, t +2,9/+1,6); **spread ×0,33** (~ECN,
chưa cộng hoa hồng) vẫn 0 giữ (hệ Breakout1 kiểm −0,45, t +0,7/−0,4). Biên lợi thô ~1 bps/lệnh
(682 lệnh, thắng 47,5%, giữ TB 2,1 bar) < phí khứ hồi ~4 bps → không có edge giao dịch được.

### Lựa chọn mở (chưa làm, không chặn)
- **Sàn/tài khoản**: spread hiện đo từ XM micro (1,63 bps/chiều). Tài khoản ECN rẻ hơn ~3 lần
  về spread nhưng có hoa hồng (~0,3 bps/chiều EURUSD). Nên thêm bộ chọn sàn (spread + hoa
  hồng + qua đêm theo sàn) khi có số liệu sàn thật; tạm thời `--he-so-spread` để đo độ nhạy.

### Vấn đề mở (ưu tiên vòng sau)
1. Breakout2/2-2/3: thoát vẫn là `giu` N bar — lệnh hedge/lưới (`Tradesinfo.*`) trong
   `checkForClose` chưa dịch, nên hệ này vẫn là xấp xỉ.
2. Template: SL/TP theo ATR (`InpSlAtrMult`/`InpTpAtrMult`, `g_trade.Buy(lot,_Symbol,0,sl,tp)`)
   chưa đọc — mẫu `price ± dir*slDist` với `slDist` từ ATR.
3. Đường giá trong bar là giả định (gần open trước); với H1 có thể kiểm bằng dữ liệu M1.
4. Chỉ báo bar 0 đổi theo tick (cũ); `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn (cũ).
5. Tối ưu cả hệ có 6 tham số → t tối ưu trên placebo thường > 2; ngưỡng phần KIỂM là chốt chặn
   thật. Nếu thêm tham số nên cân nhắc hiệu chỉnh đa phép thử (không nới ngưỡng).

---

## (trước) Ghi chú nâng cấp (Grok trên brain2) — cập nhật 2026-10-10 (khuya, giờ VN)

## Vòng 10/10 khuya (2) — LỆNH DỪNG TRONG BAR + ĐỦ LỆNH HAI PHẦN + **PHÍ THẬT**
### 0. Lỗi lớn tìm ra: vòng lặp chạy KHÔNG PHÍ từ trước tới giờ
`vong_thu_nghiem.danh_gia` gọi `CP.MoHinhChiPhi(ma="EURUSD")` — constructor trần, spread =
trượt = phí qua đêm = 0. Mọi bảng số vòng lặp bên dưới (kể cả "Breakout1 mua t=+1.5/+2.3")
là **không phí** dù ghi chú nói "sau phí". Đã sửa: `mo_hinh_chi_phi()` = `chi_phi.tu_du_lieu`
(EURUSD: spread 1,63 bps/chiều đo từ bar H1 XM, trượt 0,41 bps, qua đêm mua +2,48 %/năm,
bán −0,45 %/năm, `do_tin=SAN`). `--khong-phi` chỉ để so với số cũ.

### 1. EA kiểm lại MỖI tick → lệnh dừng trong bar (`nhan/doc_ma.py`)
- Giá sống bar 0 (`current[0].high/low/close`, `iClose(..,0)`) giờ đi qua token nội bộ
  `_gia0_` → toán hạng `close` có dấu `_bar0` (bóc ra trước khi trả co_che; nghĩa DSL cũ
  KHÔNG đổi — so JSON 14 cơ chế trước/sau: giống hệt, chỉ thêm khoá mới).
- `_kiem_moi_tick`: đi chuỗi gọi từ hàm chứa lệnh vào ngược lên `OnTick`, tìm cổng bar mới
  CÓ HIỆU LỰC: `if(!IsNewBar()) return;`, `if(dt.min!=0) return;` (phút đầu), `if(curTime==
  prevTime) return;` CHỈ KHI `prevTime=curTime;` đứng trước mọi `return` sau cổng; lời gọi
  nằm trong `if(IsNewBar…)`.
- Phân loại điều kiện: KÍCH HOẠT (`giá_sống ? mức`, mức cố định trong bar) / CHO PHÉP (không
  dùng giá sống) / phức tạp. Kết quả:
| file | phát hiện | xử lý |
|---|---|---|
| Breakout1 (mua/bán) | mỗi tick (prevTime gán sau lệnh) | `trong_bar` `>`/`<`, kích = biên phiên 5-8h + lọc MA; giờ 9-17 là cho phép |
| Breakout2, 2-2, 3 | mỗi tick (bỏ cổng) | **cặp bù nhau** (giá > giữa / giá < giữa cùng mức): tick đầu luôn kích một chiều → dịch tick đầu là ĐÚNG, không đổi |
| Breakout5, 5-2-2 | cổng `dt.min!=0` | không đổi |
| Template | `if(!IsNewBar()) return;` ở OnTick | không đổi |
- DSL (`ngu_phap.py`): khoá tuỳ chọn `"trong_bar": {"huong": ">"|"<", "kich": [chỉ số vao]}`,
  `sinh_trong_bar(spec, df)` → (cho_phep, muc, huong) biết tại close bar i; `kiem_khai_bao`
  kiểm khoá này. `vao` giữ bản xấp xỉ tick đầu (vân tay/tham số không đổi; tối ưu `vao[k].phai`
  đổi luôn mức khớp).
- Khớp lệnh (`mo_phong.chay_dung_trong_bar`): bar j=i+1, `>`: open>mức → khớp open (gap),
  high>mức → khớp ở mức; giữ tới open bar j+giu; phí spread+trượt mỗi lần vào/ra. Không nhìn
  trước: chỉ dùng O/H/L của chính bar j (lệnh chờ nằm sẵn) + cho_phep/muc bar ≤ i (test cắt).
- Placebo đúng cho lệnh trong bar: `du_lieu_gia_lap_duong` (bar dựng từ 240 bước con — râu
  nến là cực trị THẬT; giả lập cũ vẽ râu bằng nhiễu độc lập nên sai cho lệnh dừng).
  20 seed × 8 cơ chế, không phí: giữ 3/160 (1,9%), Sharpe gốc kiểm trung bình của cơ chế
  `trong_bar` +0,07 (≈0, đúng định lý dừng tuỳ chọn). Có phí: giữ 0/160.

### 2. Đủ lệnh ở CẢ HAI phần (`vong_thu_nghiem.py`)
- Phần kiểm ≥ `--lenh-toi-thieu` (20); phần tối ưu ≥ `lenh_min_phan_tu` = ⌈20·70/30⌉ = **47**
  (cùng mật độ lệnh — bộ tối ưu không được nhìn phần kiểm nên đòi mật độ thay vì đòi số lệnh
  kiểm). Bộ tối ưu chỉ chấp nhận tham số đạt 47; thiếu ở phần nào → `it_lenh`, không giữ.
- Breakout5-2-2 mua: trước chọn `giu=8` (20 lệnh tối ưu, phơi nhiễm 99,6% ≈ mua-giữ, 5 lệnh
  kiểm); giờ chọn tham số có 49 lệnh kiểm.

### Số đo
| | 890ba3e4 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **8/22 = 36,4%** (không đổi; thêm mô hình trong bar cho 2 cơ chế) |
| `test_doc_ma*` + `test_toan_hang_tuyen_tinh` | 90 xanh | 90 xanh |
| `test_trong_bar.py` (mới) | — | **14 xanh** (phát hiện, cổng prevTime/IsNewBar, khớp giá, cắt không nhìn trước, placebo, đủ lệnh, phí ≠ 0) |
| 52 file test chạm `doc_ma`/`ngu_phap`/`vong`/`mo_phong` (worktree sạch, + test_trong_bar) | 906 xanh / 46 đỏ / 5 lỗi thu thập | **920 xanh / 46 đỏ / 5 lỗi — cùng đúng tập đỏ, 0 đỏ mới** (tập đỏ có sẵn ở 890ba3e4, không liên quan thay đổi này) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar)
| cơ chế | không phí, tick đầu (cũ) | không phí, trong bar | **CÓ PHÍ** (thật), trong bar | t có phí (tối ưu/kiểm) |
|---|---|---|---|---|
| Breakout1 mua | kiểm gốc +1,06/103 l | +1,57/214 → tối ưu +2,54/189, t +2,6/+2,3 (GIỮ) | gốc −2,82/214 → tối ưu −1,01/124 | −1,0/−0,9 |
| Breakout1 bán | −0,69/140 | +2,39/229 → +2,40/160, t +3,5/+2,2 (GIỮ) | −2,25/229 → −0,50/113 | −0,1/−0,5 |
| Breakout2-2 mua/bán | | | −9,0 / −7,9 gốc → −2,7 / −1,7 | âm |
| Breakout5-2-2 mua/bán | | | −15,4 / −14,4 gốc → −1,65/49 l / +0,39/93 l | −0,6/−1,5 · −1,1/+0,3 |
| Template mua/bán | | | −17,0 / −16,1 gốc → −1,6/50 l / +0,43/39 l | âm |
**Giữ lại (luật trung thực, có phí): 0.** Không phí thì mô hình trong bar giữ 2 (Breakout1 cả
hai chiều) — nhưng biên lợi nhuận đó nhỏ hơn spread+trượt (~4 bps khứ hồi), nên không phải
edge giao dịch được. Kết quả ghi `/workspace/vong_eurusd_tb.json` (có phí) và
`/workspace/vong_eurusd_tb--khong-phi.json`.

### Vấn đề mở
1. Chỉ báo đọc ở bar 0 (`MaValues[last]`) cũng đổi theo tick — hiện coi là cố định (tre 0);
   Breakout1 dùng phần tử cũ nhất nên không ảnh hưởng.
2. "1 lệnh/ngày" (`lastupday/lastdownday`) vẫn bỏ qua (quản trị) — trong bar, chiều kia
   khớp trước sẽ chặn chiều này cả ngày; chưa mô hình hoá.
3. SL/TP của EA (Breakout1: SL = biên đối diện, TP = R·TPFactor) chưa dịch — vẫn `giu` N bar.
4. Spread EURUSD lấy từ XM micro (1,63 bps/chiều) — tài khoản ECN rẻ hơn ~3 lần; nên thêm
   lựa chọn sàn khi chạy vòng lặp.
5. (cũ) `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn.

---

## (trước) Vòng 10/10 khuya — SỬA LỆCH MỘT BAR trong quy ước chỉ số MQL5

### Quy ước mới (ghi ở `nhan/doc_ma.py`, khối chú thích trên `_ten_bar_mql`)
Mô phỏng quyết định ở ĐÓNG bar i, vào lệnh ở OPEN bar i+1. EA MQL5 chạy ở TICK ĐẦU
của bar mới (`IsNewBar`, `curTime!=prevTime`, `dt.min==0`) = đúng lúc mở bar i+1.
| MQL5 | DSL (mới) | bản cũ |
|---|---|---|
| `iClose(...,k)`, `arr[k]` với k ≥ 1 (bar đã đóng) | `tre k−1` (`iClose(..,1)` = `close`) | `tre k` (trễ thừa 1 bar) |
| bar 0 `current[0].open/high/low/close` (mới có 1 tick) | `close` (giá tick đầu ≈ close bar i) | `high`/`low`/`close` của bar i |
| chỉ báo ở bar 0 (`MaValues` phần tử mới nhất) | `tre 0` | `tre 0` (nhưng các phần tử cũ hơn lệch 1) |
| `CopyHigh(..,a,b,..)` số | `cao_nhat(high,b) tre a−1` (a=0 → b−1 bar, tre 0) | `tre a` |
| `dt.hour`, `dt.day_of_week` | `gio`/`ngay_trong_tuan` với `"luc": "dong"` = giờ ĐÓNG bar i (= giờ mở bar i+1; đóng vào T7/CN → 00:00 Thứ Hai) | giờ MỞ bar i |
| khung phiên `CopyHigh(starttime,endtime)` | `cao_trong_gio` `"luc": "dong"`: có giá trị khi giờ đóng bar i > `gio_den` (bar `gio_den` vừa đóng là đủ) | cần giờ mở bar i > `gio_den` (trễ 1 bar) |
| pivot giờ (MultiPivots `PivotsHour`) | `(high+low+close)/3` của bar i | của bar i−1 |
Không nhìn trước: mọi thứ chỉ dùng bar ≤ i (test `kiem_khong_nhin_truoc` cho MỌI cơ chế mẫu).
Pine KHÔNG đổi (script Pine chạy ở đóng bar, `x[1]` = 1 bar trước là đúng).
`ngu_phap.py`: thêm `_luc_dong(df)` + tuỳ chọn `"luc": "dong"` cho `gio`,
`ngay_trong_tuan`, `cao_trong_gio`/`thap_trong_gio` (mặc định giữ nghĩa cũ).
Sửa kèm: biến bí danh cột giá trần (`double c1 = iClose(..,1)` → `c1 = close`) trước
đây rơi vì `_tuyen_tinh` từ chối định danh trần; `_ho_gia_thuan` chấp nhận mốc CÙNG
bar nếu là tổ hợp nhiều cột (giá tick đầu so với pivot của bar vừa đóng).

### Số đo
| | ff1f94a8 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36.4% | **8/22 = 36.4%** (cùng cơ chế, căn bar đúng) |
| Cơ chế / qua `kiem_khai_bao` | 14 / 14 | 14 / 14 |
| `test_doc_ma*.py` + `test_toan_hang_tuyen_tinh.py` | 83 xanh | **90 xanh** (7 test mới: ánh xạ k→k−1, khớp EA từng bar, CopyHigh số, giờ lúc đóng + cuối tuần, khung phiên, không nhìn trước toàn bộ mẫu) |
| 38 file test chạm `doc_ma`/`ngu_phap`/`vong_thu_nghiem` | 20 đỏ | 20 đỏ, **0 đỏ mới** (cùng tập lỗi môi trường; `test_sua_bang_llm` đỏ khi chạy chung là phụ thuộc thứ tự, chạy riêng xanh ở cả hai bản) |

### Vòng lặp EURUSD H1 thật (`/workspace/eurusd_h1_server.csv`, 17.127 bar)
14 bóc được, 6 trùng, 8 chạy được → **giữ lại: 0** (ngưỡng t ≥ 2.0 tối ưu / 1.5 kiểm).
| cơ chế | kiểm gốc | kiểm sau tối ưu | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout1 mua | +1.06 / 103 | +2.54 / 94 | **+1.5 / +2.3** (gần nhất, rớt vì t tối ưu < 2.0) |
| Breakout1 bán | −0.69 / 140 | −0.34 / 159 | +0.4 / −0.3 |
| Breakout2-2 mua | −1.18 / 97 | −1.18 / 97 | +0.6 / −1.1 |
| Breakout2-2 bán | −0.54 / 121 | −0.17 / 122 | +1.0 / −0.2 |
| Breakout5-2-2 mua | −0.07 / 1310 | −0.78 / 5 | +0.5 / −0.7 |
| Breakout5-2-2 bán | +1.06 / 1310 | +1.59 / 375 | +0.0 / +1.4 |
| Template mua (c1>c2) | −1.29 / 1287 | −1.30 / 115 | +0.6 / −1.2 |
| Template bán | −0.23 / 1314 | +1.15 / 158 | −0.3 / +1.1 |
Placebo (dữ liệu ngẫu nhiên, seed 1-5, 8 cơ chế/seed): giữ 1/40 (~2.5%), đúng mức kỳ vọng.

### Vấn đề mở (ưu tiên vòng sau)
1. **EA kiểm lại mỗi tick** (Breakout1: `prevTime` chỉ cập nhật SAU khi vào lệnh, nhánh
   không phá vỡ `return` trước đó; Breakout2/2-2/3 bỏ hẳn cổng bar mới) → thực chất là
   lệnh dừng TRONG bar. Dịch theo tick đầu bar là xấp xỉ; cần tự phát hiện + gắn
   `gia_dinh`, hoặc thêm toán hạng "phá vỡ trong bar" vào DSL (vào tại mức giá).
2. Tối ưu chọn tham số cho 5 lệnh trên phần kiểm (Breakout5-2-2 mua, `giu=8`):
   `lenh_min` chỉ áp lên phần tối ưu — cân nhắc áp cả phần kiểm khi báo cáo.
3. `PivotsDay` (R1/S1/P ngày) qua `moc_ky`; `±5*_Point` cần giả định symbol.
4. Bắt `SellLimit`/`BuyLimit` làm điểm vào (lệnh chờ tại mức giá).
5. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.

---

## Vòng 10/10 tối — SỐ ĐO THẬT (`python mau_thu/do_moc.py`)
| | 908075c0 (chiều) | bây giờ |
|---|---|---|
| **Điểm vào dịch được (số chính)** | 6/22 = 27.3% | **8/22 = 36.4%** |
| Cơ chế rút ra | 10 | 14 |
| Qua `kiem_khai_bao` | 8/10 (2 họ `khac`) | **14/14** |
| Tín hiệu thanh nến (bỏ hedge/lưới + mã chết khỏi mẫu số) | không đo | 8/10 = 80% |
| `test_doc_ma.py` + `test_doc_ma_mql5.py` + `test_toan_hang_tuyen_tinh.py` | 72 xanh | **83 xanh** (11 test mới) |
| Bộ test chạm `doc_ma`/`ngu_phap`/`vong_thu_nghiem` (38 file) | 30 đỏ trước đó | 20 đỏ, **0 đỏ mới** (đỏ còn lại do môi trường: thiếu scipy, nao.db...) |

### Phân loại 22 điểm vào (`phan_loai_vao_lenh` trong `doc_chien_luoc`)
- `dich_duoc` 8 — Breakout1, 2, 2-2, 3, 5, 5-2-2 (lệnh đầu), Template mua+bán.
- `quan_ly_vi_the` 10 — hedge/lưới/nhồi lệnh theo `Tradesinfo.*`, `postotal`,
  `profits`: phụ thuộc GIÁ VÀO LỆNH / số lệnh đang mở, không phải tín hiệu bar.
- `ma_chet` 2 — Pivots1 và CurrencyStrength1: khối breakout + PositionOpen nằm
  SAU `return;` vô điều kiện (tác giả đặt SellLimit tại R1 rồi return). Bản cũ
  đếm chúng như tín hiệu chưa dịch; dịch chúng ra là gán cho tác giả chiến lược
  họ KHÔNG chạy.
- `chua_dich` 2 — Breakout4 (`PivotsIsPivotRange` R1/S1 ngày ±5·`_Point`, phụ thuộc
  symbol) và CurrencyStrength1 (`iCustom` CSValues, không có mã).
- Số chính VẪN là 8/22 (mẫu số đủ 22). Dòng "tín hiệu thanh nến" chỉ để biết còn
  bao nhiêu tín hiệu thật chưa dịch. Lưu ý: `_VAO_LENH` không bắt `SellLimit`/
  `BuyLimit`, nên 2 lệnh chờ ĐANG CHẠY thật (SellLimit R1 ở Pivots1/CurrencyStrength1)
  không nằm trong 22 — nếu thêm thì mẫu số thành 24.

### Đã làm (nhan/doc_ma.py)
1. **Pivot giờ theo mã thật của `MultiPivots.mqh`** (lấy từ
   github.com/peterthomet/MetaTrader-5-and-4-Tools/Include/MultiPivots.mqh):
   `PivotsIsAbovePivot(x, pd.PivotsHour, "P")` = `x >= P`, P = (H+L+C)/3 của thanh
   H1 đã đóng ngay trước (TRADITIONAL/CLASSIC/FIBONACCI cùng P). Chỉ dịch khi file
   bật `Settings.PivotTypeHour` loại đó VÀ có gọi `.Calculate(` (không thì struct = 0).
   Cơ chế mang `gia_dinh` ("đúng khi chạy trên dữ liệu H1"). PivotsDay/R1/S1 chưa dịch.
2. **Gập `if` chỉ phụ thuộc cấu hình** (`_gap_hang_cau_hinh`): `if(ReverseEntry)` với
   `input bool ReverseEntry=false`, `if(startmanual!=0){...}` trong
   `checkForOpen(int startmanual=0)` (chỉ gọi có đối số từ `OnChartEvent` = bấm phím
   tay). Trước đó bảng bool lấy phép gán CUỐI theo văn bản = `upbreakout=true` trong
   nhánh không bao giờ chạy → sai. Chỉ `input` (không `extern`); tham số bị gán lại
   trong thân hàm thì không coi là hằng. Test: đổi `ReverseEntry=true` → chiều đảo.
3. **Họ cho cơ chế chỉ so giá với mốc giá cũ hơn** (`_ho_gia_thuan`) — tự quyết theo
   quyền được giao: mua khi giá mới TRÊN mốc cũ (bán khi dưới) = `xu_huong`
   (động lượng); mua khi DƯỚI (bán khi trên) = `quay_ve_trung_binh`. Template
   `close[1] > close[2]` → `xu_huong`; Breakout5 (mua dưới pivot) → `quay_ve_trung_binh`.
   Chỉ gán khi MỌI điều kiện đều là giá thô bên trái, mốc cũ hơn bên phải, cùng hướng.
4. **Bỏ điều kiện trùng/bị kéo theo** (`_bo_trung_dieu_kien`): nhánh bán Template từ
   `c1<c2 và c1<=c2 và c1<=c2` → `c1<c2` (cùng tập bar).
5. **Mã chết** (`_ma_chet`) và **phân loại điểm vào** (`_phu_thuoc_vi_the`).
6. `tuyen_tinh` lồng `(a+b+c)/3` được làm phẳng (chỉ chế độ MQL5; Pine giữ dạng lồng
   để `mult` của Bollinger vẫn là tham số riêng).

### Vòng lặp trên dữ liệu H1 THẬT
Repo không có CSV giá. Đã tải EURUSD H1 từ Yahoo (yfinance, 2023-12-26 → 2026-10-09,
17.127 bar sau khi bỏ bar phẳng), đổi sang giờ server ước lượng `Europe/Helsinki`
(UTC+2/+3 — bộ lọc giờ của EA viết theo giờ server). File để ngoài repo:
`/workspace/eurusd_h1_server.csv`; kết quả `/workspace/vong_eurusd.json`.

    python vong_thu_nghiem.py --csv /workspace/eurusd_h1_server.csv

Kết quả: 14 bóc được, 6 trùng, 8 chạy được → **giữ lại: 0**.
| cơ chế | kiểm gốc | kiểm sau tối ưu | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout1 mua | sh −0.58 / 145 lệnh | +1.26 / 106 | +1.5 / +1.1 |
| Breakout1 bán | +0.02 / 164 | −0.02 / 138 | +0.4 / −0.0 |
| Breakout2-2 mua | +1.50 / 98 | +0.28 / 101 | +1.4 / +0.2 |
| Breakout2-2 bán | −0.18 / 120 | +0.31 / 116 | +1.1 / +0.3 |
| Breakout5-2-2 mua (dưới pivot) | −0.05 / 1090 | −0.05 / 1090 | +1.4 / −0.1 |
| Breakout5-2-2 bán (trên pivot) | +1.05 / 1090 | +1.05 / 1090 | +0.7 / +0.9 |
| Template mua (c1>c2) | −2.39 / 1287 | −2.39 / 1287 | +0.6 / −2.2 |
| Template bán (c1<c2) | −0.52 / 1313 | −0.11 / 685 | +0.1 / −0.1 |
Không cơ chế nào qua ngưỡng t ≥ 2.0 / 1.5. Đó là kết quả trung thực: các EA mẫu
này là bộ khung hedge/lưới, phần tín hiệu vào lệnh đơn thuần không có edge sau phí.

### Vấn đề mở (ưu tiên vòng sau)
1. ~~**Lệch một bar trong quy ước chỉ số MQL5.**~~ (ĐÃ SỬA ở vòng 10/10 khuya, xem trên) EA chạy ở tick ĐẦU của bar mới (cổng
   `curTime!=prevTime`, `dt.min==0`), nên `current[0].close` ≈ close bar vừa đóng,
   còn chỉ số MQL5 k≥1 ứng với trễ k−1 trong DSL (quyết định lúc đóng bar). Quy ước
   hiện tại ánh xạ thẳng k → trễ k (cũng áp cho pivot giờ để nhất quán). Không nhìn
   trước (mốc cũ hơn 1 bar) nhưng không khớp tuyệt đối với EA — cần quyết định
   rồi sửa đồng loạt + test.
2. `PivotsDay` (R1/S1/P ngày) qua `moc_ky`; `±5*_Point` cần giả định symbol.
3. Bắt `SellLimit`/`BuyLimit` làm điểm vào (lệnh chờ tại mức giá).
4. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.

---

## Vòng 10/10 chiều (908075c0)

## Trạng thái hiện tại — SỐ ĐO THẬT (`python mau_thu/do_moc.py`)
| | trước (c5d5fcd9) | bây giờ |
|---|---|---|
| Cơ chế rút ra / 22 điểm vào | 10 (45.5%) — **phần lớn sai nghĩa** | **10 (45.5%) — đúng nghĩa** |
| Điểm vào dịch được thật | không đo | **6/22 = 27.3%** |
| `test_doc_ma.py` | **19/36 đỏ** | **36/36 xanh** |
| Qua `kiem_khai_bao` + không nhìn trước | — | 8/10 (2 cái họ `khac`) |

### Vì sao con số 45.5% cũ phải bỏ
Các commit 8cfa3f8b → 700d395a đạt 13.6% → 45.5% bằng cách làm SAI nghĩa và
làm đỏ 18-19 test của `test_doc_ma.py` (trước đó 36/36 xanh):
- Coi mọi định danh lạ là `close` → `Tradesinfo.hedgeprice` thành `close`, ra cơ
  chế `close >= close` (luôn đúng → `phoi_nhiem=0.996`, tức mua-giữ).
- Tách `or` như thể là `and`.
- Giữ cơ chế khi một vế không dịch được — trái nguyên tắc đã ghi trong
  `doc_chien_luoc` ("bỏ một vế làm điều kiện LỎNG hơn bản gốc ... là nói dối").

Đã khôi phục `doc_ma.py` về bản c2fe17a0 (36/36 xanh) rồi làm lại đúng cách.

## Việc đã làm (lớp đọc MQL5 trong `nhan/doc_ma.py`)
- `&&`/`||` → `and`/`or`; `iClose(_Symbol,_Period,k)` → `close[k]`.
- Mảng dữ liệu: `current[0].close` sau `CopyRates(...,0,1,current)`, `MaValues[0]`
  sau `CopyBuffer(MaHandle,0,0,10,MaValues)` — mảng KHÔNG đảo chiều thì phần tử 0
  là bar CŨ NHẤT (ra `sma(50) trễ 9`, đúng như code tác giả chạy).
- `(_Point*margin)` với `margin = BOMargin = 0` → 0.
- Biên phiên: `highs[ArrayMaximum(highs)]` sau `CopyHigh` theo khung giờ dựng từ
  `dt.hour=H` + `StructToTime` → toán hạng DSL mới `cao_trong_gio`/`thap_trong_gio`
  (thêm vào `nhan/ngu_phap.py`, chỉ có giá trị khi giờ > `gio_den` → không nhìn trước).
  `CopyHigh(...,1,3,highs)` (số) → `cao_nhat(high,3) trễ 1`.
- Vế so sánh là biểu thức số học (`close < lowrange+((highrange-lowrange)/2)`).
- Guard tìm theo KHỐI `{}` bao lệnh vào (bản cũ vớ `if(downbreakout){..}` đã đóng).
- `if(up||down){ if(up){type=BUY} if(down){type=SELL} ... PositionOpen(type) }`
  → tách đúng 2 cơ chế mua/bán.
- Bộ lọc thoát sớm `if(dt.hour<9||dt.hour>17) return;` → `gio>=9 và gio<=17`;
  `if(up && close<MA) return;` → nhánh mua thêm `close >= MA`.
- Hàm tín hiệu: `OpenTrade(sig>0 ? BUY : SELL)` + `sig=GetSignal()` +
  `if(c1>c2) return 1;` → điều kiện của từng chiều.
- Điều kiện QUẢN TRỊ (Copy* lỗi, 1 lệnh/ngày, đã có vị thế, giá trị <= 0) được bỏ
  qua nhưng ghi rõ ở `bo_qua_quan_tri`. Lệnh hedge/lưới theo `Tradesinfo.*`
  (giá vào lệnh) và hàm include không có mã (`PivotsIs*`, `iCustom`) KHÔNG dịch.
- Test mới: `test_doc_ma_mql5.py` (8 test: nghĩa, chiều, bộ lọc, không nhìn trước,
  vòng thử nghiệm).

## Trần của bộ mẫu `mau_thu/` (vì sao chưa đạt ≥40% theo điểm vào)
22 điểm vào = 6 dịch được + 10 lệnh hedge/lưới phụ thuộc giá vào lệnh (không
phải tín hiệu bar) + 5 phụ thuộc `MultiPivots.mqh`/`iCustom` không có trong repo
+ 1 nhánh `else` thủ công. Muốn vượt 27.3% theo điểm vào cần mã của
`MultiPivots.mqh` hoặc bộ mẫu rộng hơn — không thể "dịch" đúng thứ không có mã.

## Vòng lặp `vong_thu_nghiem.py`
- Dữ liệu H1 giả lập (hoặc `--csv` dữ liệu thật), chia thời gian 70% tối ưu / 30% kiểm.
- Tối ưu thật: dò từng toạ độ trên `ngu_phap.tham_so_cua` (chu kỳ, ngưỡng, giữ), 2 lượt.
- Dùng đúng `chieu` (bản cũ bỏ qua → lệnh bán chạy như mua).
- Giữ lại khi t = Sharpe×√năm ≥ 2.0 (tối ưu) và ≥ 1.5 (kiểm), đủ ≥20 lệnh, qua kiểm cú pháp.
- Bỏ trùng vân tay (Breakout2/2-2/3 cùng điều kiện).
- Placebo trên dữ liệu ngẫu nhiên: ngưỡng cũ "Sharpe kiểm > 0" giữ 3-5/6 mỗi seed;
  ngưỡng mới giữ 3 lần trên 20 seed × 4 cơ chế đủ điều kiện (~4%).

## Ưu tiên tiếp
1. Chạy vòng lặp trên dữ liệu H1 thật (EURUSD...) bằng `--csv`.
2. ~~Họ cho cơ chế `close[1] > close[2]`~~ — đã gán `xu_huong` ở vòng 10/10 tối.
3. Nếu có `MultiPivots.mqh`: dịch pivot ngày bằng `moc_ky` (cao/thấp/đóng trước).
4. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.
