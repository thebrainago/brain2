# Đặc tả ứng viên IBS US100 (CFD, khung ngày)

Cập nhật: 2026-11-15 07:55 (Asia/Saigon, UTC+7)

**Nhãn: ứng viên – chưa pass.** Dùng cho bộ hỗ trợ trading (bias / gợi ý vùng tín hiệu), không phải lệnh tự chạy hay đã vượt cổng SEEKER. Chi tiết độ bền: [ibs_cfd_robust.md](ibs_cfd_robust.md). Kiểm định gốc: [ibs_cfd_chi_so.md](ibs_cfd_chi_so.md).

## Quy tắc (ưu tiên)

- Thị trường: CFD US100 (Nasdaq 100). Đối chiếu US500 được phép, nhưng yếu hơn.
- Khung: ngày (D1).
- IBS = (Close − Low) / (High − Low). Nếu High = Low thì bỏ qua.
- **Vào:** khi IBS < 0,20, mua tại **giá mở cửa nến tiếp theo**. Không chồng lệnh.
- **Ra:** khi IBS > 0,80 (đánh giá lúc đóng cửa nến đang giữ) hoặc đã giữ tối đa 4 nến; khớp tại mở cửa nến sau tín hiệu ra.
- Không bắt buộc lọc SMA200.
- Không bắt buộc lọc VIX. Bối cảnh: lịch sử đầy đủ cho thấy lệnh khi VIX ≥ 20 tốt hơn rõ; khi VIX thấp cần thận trọng, nhưng đây chỉ là bias, chưa phải điều kiện vào lệnh đã kiểm OOS độc lập.

## Phương án phụ (đơn giản hơn, kém bền)

- Cùng vào IBS < 0,20, thoát sau đúng 1 nến (mở cửa nến t+2 nếu vào ở t+1).
- Dễ mất edge nếu khớp trễ thêm một nến. Chỉ dùng khi khớp sát mở cửa.

## Chi phí giả định khi đánh giá

- Spread US100: 1,5 điểm chỉ số (tương đương khoảng 0,037 điểm trên QQQ).
- Phí qua đêm long: 7,5%/năm / 365 trên danh nghĩa; thứ Sáu sang thứ Hai = 3 đêm.
- Nếu spread/swap sàn khác, phải chạy lại script, không dùng số dưới đây như cam kết lãi.

## Thống kê kỳ vọng (Yahoo, OOS 2015-01-01 → 2026-11-13, đã trừ phí trên)

Đây là quá khứ, không phải lời hứa.

| Chuỗi | Lệnh | Win% | Lãi TB / lệnh | PF | Sharpe | %/năm | Max DD | p vs ngẫu nhiên |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ^NDX, thoát 0,8 / 4 nến | 395 | 62,5 | +0,25% | 1,41 | 0,61 | 8,13 | 22,5% | 0,05–0,09 (không vững) |
| QQQ, thoát 0,8 / 4 nến | 371 | 63,3 | +0,32% | 1,51 | 0,71 | 9,68 | 22,7% | 0,030–0,050 |
| ^NDX, giữ 1 nến | 484 | 58,7 | +0,16% | 1,31 | 0,60 | 5,95 | 16,4% | ≈ 0,044 |
| QQQ, giữ 1 nến | 449 | 57,0 | +0,17% | 1,35 | 0,63 | 6,20 | 18,3% | ≈ 0,026 |

Walk-forward cố định thoát 0,8 / 4 nến: ^NDX 1995–2026 dương 75% số năm (từ 2015: 83%); QQQ 2004–2026 dương 65% (từ 2015: 75%). Năm 2022 lỗ khoảng 11–16% với quy tắc này.

## Những điều không được làm

- Không tối ưu lại ngưỡng 0,10 / thoát 0,9 chỉ vì lưới OOS đẹp hơn.
- Không coi đã pass vì một p < 0,05 trên OOS 2015: DSR sau ~150–237 phép thử chỉ khoảng 0,15–0,28.
- Không áp sang CFD forex, vàng, hay cặp chéo (đã kiểm, không edge).
- Không mở tài khoản thật, không copy lệnh, không kích hoạt chiến lược sống từ đặc tả này.
- Không dùng số liệu này như đã vượt kiểm SEEKER (chưa tick/CFD thật, chưa cổng FDR của SEEKER).

## Gợi ý cho bộ hỗ trợ

- Có thể hiện như **bias / xác nhận đảo chiều ngắn** trên US100 khi nến ngày đóng với IBS < 0,20, kèm nhắc thoát khi IBS > 0,80 hoặc hết 4 nến.
- Gắn nhãn rõ: “ứng viên – chưa pass”.
- Nên ghi kèm VIX (cao/thấp) như ngữ cảnh, không khóa lệnh.

## Cách chạy EA / Pine (chưa compile trên máy soạn mã)

Các file [IBS_US100.mq5](../../tools/kiem_dinh/evo/IBS_US100.mq5) và [ibs_us100.pine](../../tools/kiem_dinh/evo/ibs_us100.pine) bám đúng quy tắc ưu tiên ở trên. **Chưa compile / chưa validate** trên máy viết mã (không có MetaEditor hay Pine Editor). Hãy compile trong MetaEditor và (với Pine) bấm Add to chart trên TradingView, rồi tự đối chiếu lỗi cú pháp nếu có. Chỉ dùng **tài khoản demo / paper**. EA từ chối tài khoản thật và yêu cầu bật `InpAckDemoOnly`.

### MetaTrader 5 — Strategy Tester

1. Chép `IBS_US100.mq5` vào `MQL5/Experts/`, mở MetaEditor, nhấn Compile. Sửa lỗi nếu compiler báo (máy này chưa compile được).
2. Strategy Tester: Expert = IBS_US100; mã CFD US100 của sàn (tên có thể là US100, NAS100, USTEC, v.v.); khung **D1** (EA luôn đọc nến D1 dù đồ thị khác); mô hình **Every tick** hoặc **1 minute OHLC** (mở cửa D1 cần gần đúng).
3. Thời gian: **2015.01.01 – hiện tại** để đối chiếu OOS; có thể chạy thêm 1995–2014 để thấy giai đoạn lỗ/yếu.
4. Đầu vào: `InpAckDemoOnly = true`; lot nhỏ; `InpIbsBuy=0.20`, `InpIbsExit=0.80`, `InpMaxBars=4`; `InpUseVixFilter=false`; `InpMaxSpreadPoints` theo điểm của sàn (0 nếu chưa chắc đơn vị). Magic tuỳ ý. Không bật rủi ro % trừ khi đã hiểu ATR chỉ dùng để ước lượng lot, không phải SL.
5. Sau test, so với kỳ vọng Yahoo OOS 2015+ ở bảng trên (không phải mục tiêu phải khớp từng số, vì giá/spread/swap sàn khác Yahoo):
   - ^NDX, thoát 0,8 / 4 nến: khoảng 395 lệnh, thắng ~62,5%, lãi TB ~+0,25%/lệnh, PF ~1,41, Sharpe ~0,61, ~8%/năm, DD ~22%.
   - QQQ, cùng quy tắc: khoảng 371 lệnh, thắng ~63,3%, lãi TB ~+0,32%, PF ~1,51, Sharpe ~0,71, ~9,7%/năm, DD ~23%.
   - Cần xem thêm: tỷ lệ năm dương, lỗ năm 2022 (khoảng 11–16% trên dữ liệu Yahoo), và không kỳ vọng lặp lại IS trước 2010.
6. Nếu số lệnh lệch rất xa, kiểm tra tên mã, đơn vị giá, nến cuối tuần, và xem EA có khớp đúng **mở cửa nến ngày** không.

### MetaTrader 5 — tài khoản demo

1. Compile như trên. Đăng nhập **demo**, mở đồ thị mã US100 (nên D1). Kéo EA vào, bật AutoTrading.
2. Bật `InpAckDemoOnly`, lot nhỏ, lọc spread nếu biết điển hình của sàn, VIX tắt. Không chạy trên tài khoản thật (EA sẽ từ chối).
3. Nhật ký phải thấy dòng “DEMO only” lúc khởi tạo. Chỉ để quan sát lệch fill/spread/swap so với tester, không phải để “đi tiền”.

### TradingView — Pine v5

1. Mở Pine Editor, dán `ibs_us100.pine`, lưu, **Add to chart** trên hợp đồng/CFD Nasdaq 100 hoặc QQQ, khung **D1** (script cảnh báo nếu sai khung).
2. Properties: hoa hồng và slippage — đặt trùng với hai ô ghi chú trong input (mặc định 0% và 2 tick; `strategy()` không đổi commission/slippage theo input trên mọi phiên bản, nên phải chỉnh Properties).
3. Strategy Tester: khoảng 2015 đến nay, so với cùng bảng kỳ vọng ở trên. Bật “Recalculate on close” không cần; lệnh đặt lúc đóng cửa và khớp mở cửa nến sau.
