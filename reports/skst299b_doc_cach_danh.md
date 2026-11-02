# skst299b — Đọc cách đánh huanghq2000 / fx_trading (StrategyTester-From2502-v2.0)

**Thẻ:** `sk_st_299b0817f66d4096` (alias skst299b) · EURUSD · brain2 ghi H1 nhưng statement là **H4**  
**Ngày phân tích:** 2026-11-01 (Asia/Bangkok) · chỉ trên box · không commit/push

---

## 1. Nguồn dữ liệu

| Mục | Đường dẫn / ghi chú |
|-----|---------------------|
| Statement gốc | `/workspace/brain2/data/seeker_da_nguon/tai_ve/github/huanghq2000__fx_trading/report-macd/StrategyTester-From2502-v2.0.htm` |
| EA trong repo | cùng thư mục: `macd_sample.mq4` (+ `hhq_test.mq4`, `moving_average.mq4` — **không** khớp báo cáo v2.0) |
| Repo upstream | https://github.com/huanghq2000/fx_trading |
| CSV replay brain2 | `reports/ong_dan/viec_mt5/sk_st_299b0817f66d4096/od_skst299b0817f66d4096_{XM,Exness}_CSV_vao.csv` (**90** dòng vào) |
| Cách sinh CSV | `nhan/ong_dan.py` → `xuat_csv_vao` / `ghi_csv_vao`: lấy lệnh mở từ statement, snap theo H1 server sàn, xuất `thoi_gian,ma,chieu,gia,nguon,lot` |
| Sổ cơ chế | `reports/kho_co_che/so_co_che.jsonl` id=`sk_st_299b0817f66d4096` — `vao: lệnh statement ngoài`, ql brain2 DCA 0.8%×1.3 max4 + hedge 10% |
| Giá dùng phân tích | `data_khung/EURUSD_H1__EURUSD_H1__v2.parquet`, `EURUSD_H4__EURUSD_H1__v2.parquet` (≈2000-01 → 2026-10-02) |
| Artefact tạm | `/tmp/skst299b_analysis/{trades.csv,feat.json,sims.json}` |

**Múi giờ:** timestamp statement = giờ server MT4 Swissquote-Demo1 (thường UTC+2/+3 theo DST). Parquet brain2 cũng theo trục thời gian server sàn đã chuẩn hoá trong pipeline; khớp mở lệnh ≤2h với CSV replay.

**Tiêu đề HTML:** `Strategy Tester: MACD Sample` — không phải EA tự viết “grid/DCA”.

**Thông số trên báo cáo:** TakeProfit=**50**, Lots=**0.1**, TrailingStop=**30**, MACDOpenLevel=**3**, MACDCloseLevel=**2**, MATrendPeriod=**26**.  
TP thực tế trên lệnh: Ask/Bid ± **0.00050** = **50 point = 5 pip** (đơn vị Point 5-digit, không phải 50 pip).

---

## 2. Thống kê lệnh tác giả (194 lệnh)

| Chỉ số | Giá trị |
|--------|---------|
| Kỳ | **2025-02-04 → 2026-05-26** |
| Symbol | EURUSD only |
| Long / Short | 111 / 83 |
| Lot | cố định **0.1** (không tăng lot) |
| Đồng thời | **max = 1** (không grid, không DCA, không martingale) |
| Winrate | **94.3%** |
| Net tác giả | **−166.54** trên vốn 1000 · DD ~**65%** |
| PnL TB thắng / thua | ~**+3.58** / **−74.7** (thua hiếm nhưng rất nặng) |
| Thoát | t/p **120** · s/l **69** (nhiều s/l là trailing đã lời) · close **5** |
| Giữ lệnh | median ~**0.29 h** · p90 ~**49.5 h** |
| Giờ vào đỉnh | khoảng **16h** server (phiên London/NY overlap) |
| Khoảng TP | **5 pip** cố định · trailing ~**3 pip** (30 point) |

**Kết luận phong cách:** single-shot **MACD Sample H4** + TP hẹp + trailing. Brain2 gán nhãn `dca/martingale/hedge` trong `so_co_che` là **quản lý của chúng ta đè lên lệnh statement**, không phải cách anh ta đánh. Ghi chú “DCA” trong một số file dò ngược statement là **ảo ảnh** (re-entry sau TP 5 pip trong cùng nến H4 trông như “nhồi”).

CSV replay chỉ lấy **90/194** lần mở (đã lọc/snap H1) → backtest Python IS (+5134 / DD 17.9% trên 10k) = **replay thời điểm vào của anh ta + ql brain2**, in-sample, **không tradeable**.

---

## 3. Luật vào thật (từ mã + khớp lệnh)

Logic MetaQuotes **MACD Sample** (mọi tick trên chart H4):

- **BUY:** MACD < 0 **và** MACD cắt lên Signal **và** \|MACD\| > 3·Point **và** EMA(26) đang tăng  
- **SELL:** MACD > 0 **và** MACD cắt xuống Signal **và** MACD > 3·Point **và** EMA(26) đang giảm  
- Đóng / không vào mới khi điều kiện close-level; một vị thế tại một thời điểm  
- Sau TP 5 pip, nếu điều kiện còn đúng **trong cùng nến H4** → vào lại (đó là lý do 194 lệnh >> số tín hiệu đóng nến)

### Feature vs baseline (cùng giờ 3–21)

Hiệu ứng yếu khi gộp long+short; tách chiều thì **bb_z, macd_hist, RSI, ret6/12** tách tốt — **đúng hướng momentum MACD**, không phải mean-reversion thuần.

Cây quyết định nông (depth≤3, vào vs random):  
**coverage ≈ 100% · precision ≈ 2%** → **vô dụng** (bắn gần như mọi bar). Không dùng cây này để trade.

Tái tạo tín hiệu **đóng nến H4** trên parquet brain2: ~**32** cross/kỳ statement · coverage hướng ~**43%** · precision ~**6%**.  
“Soft state” (điều kiện MACD còn đúng, không bắt buộc cross mới): khớp hướng ~**42%**.  
Gap còn lại = **vào intra-bar / tick** + lệch feed Swissquote vs parquet.

**Ứng viên luật tốt nhất để trade forward = chính MACD Sample H4** (có mã nguồn), không phải rule học từ feature.

---

## 4. Mô phỏng nhanh (OHLC H4, spread ~14 point, vốn 10 000)

*Gần đúng, không phải tick tester; phí đã trừ dạng spread.*

### Quản lý kiểu tác giả (1 lệnh, TP 50 point, trail 30 point)

| Kỳ | Mode | Lệnh | PnL | %/năm | Max DD |
|----|------|------|-----|-------|--------|
| IS 2025-02→2026-05 | cross đóng nến | 32 | +45 | +0.3% | 7.6% |
| IS | soft (gần re-entry) | 178 | −1397 | −11% | 30.5% |
| OOS trước 2023-01→2025-01 | cross | 57 | −2346 | −12% | 33.8% |
| OOS dài 2020→2024 | cross | 132 | −7946 | −27% | 83% |
| OOS sau 2026-05→2026-10 | cross | 11 | +396 | ~+12% | 0%* |

\*Mẫu OOS sau rất ngắn (~4 tháng). Soft + ql tác giả OOS dài **phá tài khoản**.

### Entry MACD + quản lý brain2 (DCA 0.8%×1.3 max ~4, hedge ~10%, basket TP 0.3%) — xấp xỉ bar

| Kỳ | Mode | PnL | %/năm | Max DD |
|----|------|-----|-------|--------|
| IS | soft | +4320 | ~+32% | 11.7% |
| OOS trước | cross | +1560 | ~+7.2% | 19.6% |
| OOS trước | soft | +2780 | ~+12.5% | 14.5% |
| OOS dài 2020–24 | cross | +3720 | ~+6.5% | 16.4% |
| OOS dài | soft | −3957 | −9.6% | **94.8%** |
| OOS sau | soft | +780 | ~+24% | 4.4% |

Chạy cùng rule trên **H1** (sai TF so với statement) với ql tác giả: thua rõ trên mọi kỳ.

**Pass tiêu chí user (lãi sau phí, DD≤80%, ≥10%/năm):**  
- Luật tác giả thuần: **không đạt** OOS dài.  
- MACD H4 **cross đóng nến** + ql brain2: OOS dài ~**6.5%/năm**, DD~16% — **dưới 10%/năm**, chưa đạt ngưỡng lãi; DD ổn.  
- Soft + brain2: IS đẹp nhưng OOS dài **DD ~95%** → **không đạt**.  
- Con số +5 134 IS replay statement **không** chứng minh edge vào lệnh.

---

## 5. Độ tin cậy & hạn chế

| Khẳng định | Tin cậy |
|------------|---------|
| Statement = MACD Sample H4, params như trên | **Cao** (tiêu đề HTML + mã repo + TP 5 pip khớp) |
| Không phải grid/DCA/martingale của tác giả | **Cao** (max đồng thời 1, lot cố định) |
| Lãi IS brain2 đến từ ql ngoại lai trên thời điểm vào statement | **Cao** |
| Tái tạo 100% mọi timestamp vào bằng chỉ báo đóng nến | **Thấp–trung** (cần tick / cùng feed Swissquote) |
| OOS sim OHLC dự báo live | **Trung–thấp** (xấp xỉ; soft vs tick khác nhau) |

**Dữ liệu thêm sẽ giúp:** lịch sử MQL5/Myfxbook đầy đủ hơn (nếu có live chứ không chỉ Strategy Tester); tick EURUSD cùng broker; chạy lại `macd_sample.mq4` đúng H4 trên máy nhà với cùng kỳ để đối chiếu từng lệnh; không nhầm các file `From2502-v3/v4`, `h4v2.0` (thẻ khác trong `so_co_che`).

---

## 6. Kết luận ngắn (trả lời “đọc được cách đánh?”)

1. Anh ta (báo cáo này) đánh **MACD Sample chuẩn MetaQuotes trên EURUSD H4**: cắt MACD/Signal dưới/trên 0 có ngưỡng 3 point, lọc EMA26, TP 5 pip, trail 30 point, **một lệnh**.  
2. **Không** có lưới / DCA / hedge trong statement; WR cao + kỳ vọng âm là đặc trưng TP hẹp / đuôi lỗ dài.  
3. Không tìm thấy rule feature “bí mật” tốt hơn MACD; cây nông precision ~2%.  
4. Muốn trade forward: implement đúng MACD Sample (ưu tiên tick H4) — **ql tác giả không kỳ vọng lãi bền**; ghép ql brain2 chỉ khảo sát được mức ~6–7%/năm OOS với cross đóng nến, **chưa đủ ≥10%/năm**, và tuyệt đối **không** bật soft-reentry + DCA trên lịch sử dài.  
5. Backtest replay CSV hiện tại **chỉ để benchmark quản lý**, không phải chiến lược vào lệnh có thể live.

