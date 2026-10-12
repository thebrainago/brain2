# Backtest MT5 hai ứng viên vòng 24 (RSI trailing D1, MRZ trailing D1) — MÔ PHỎNG

**Trạng thái: CHƯA COMPILE** — box không có MetaEditor/MT5; mã viết theo MQL5 chuẩn, cần compile trên máy Windows.
Nhắc lại: vòng 24 **không có hệ nào sống** (Holm 1,0; nửa 2004–2015 lỗ). Backtest MT5 chỉ để kiểm tra bản Python có khớp với
dữ liệu/phí thật của XM không. Demo là bước cuối, chỉ khi có hệ sống.

## File
- `ea_demo/BRAIN_V24_Chung.mqh` — logic chung (khớp `v24.py` → `v22.chay(thoat="TR2")` + `v19.tin_hieu`).
- `ea_demo/BRAIN_V24_RSI_Trail_D1.mq5` + `.set` — RSI14 < 30 mua, > 70 bán.
- `ea_demo/BRAIN_V24_MRZ_Trail_D1.mq5` + `.set` — z50 = (close − SMA50)/STD50 < −2 mua, > 2 bán.
- `ea_demo/ea_logic_v24.py` + `test_ea_v24.py` — bản Python theo đúng luồng EA, kiểm khớp từng lệnh với `v22.chay`.

Luật (cố định, không tối ưu): xét nến D1 vừa đóng; vào lệnh ở open nến kế tiếp (lệnh thị trường lúc mở nến);
SL ban đầu = giá vào ∓ 1,5×ATR14 (ATR Wilder của nến tín hiệu); sau mỗi nến đóng: best = max/min(best, close),
SL = best ∓ 2×ATR14 của nến đó, chỉ kéo theo hướng có lợi; giữ tối đa 72 nến (đóng ở open nến thứ 73 và nến đó không vào mới);
một vị thế mỗi chart; vào lại được ngay nến sau khi dính SL.
Khác biệt đã biết với Python: MT5 khớp SL theo tick thật (có gap → khớp xấu hơn mức SL), Python khớp đúng mức SL;
Python dùng giá Yahoo (giữa) + spread theo bảng, MT5 dùng bid/ask thật của XM.

## 1. Compile
1. MT5 (XM) → **Tools → MetaQuotes Language Editor** (F4).
2. Trong MetaEditor: **File → Open Data Folder** → `MQL5\Experts\` → tạo thư mục `brain2`, chép 3 file
   `BRAIN_V24_Chung.mqh`, `BRAIN_V24_RSI_Trail_D1.mq5`, `BRAIN_V24_MRZ_Trail_D1.mq5` vào đó (cùng thư mục, vì `#include "..."`).
3. Mở từng `.mq5` → **Compile** (F7). Phải 0 error. Nếu có lỗi, chụp tab *Errors* gửi lại.
4. Chép 2 file `.set` vào `MQL5\Profiles\Tester\`.

## 2. Strategy Tester (Ctrl+R)
- Expert: `brain2\BRAIN_V24_RSI_Trail_D1` (rồi lặp với MRZ). Bấm **Inputs → Load** chọn `.set` tương ứng.
- Symbol: một mã mỗi lần chạy (một EA gắn một chart). Timeframe: **D1**.
- Modelling: **Every tick based on real ticks**. (Nếu XM không có real ticks cho giai đoạn cũ, Tester tự lùi về "Every tick" —
  ghi lại điều này trong báo cáo.)
- Date: chạy **2 lần**: `2004.01.01 – 2015.03.31` (nửa phát hiện) và `2015.04.01 – 2026.10.01` (nửa kiểm), cùng mốc tách như Python.
  Nếu dữ liệu XM không đủ về 2004, ghi ngày bắt đầu thật. Có thể chạy thêm 2016–2026.
- Deposit 10.000 USD, Leverage 1:30 (hoặc mức tài khoản), lot cố định 0,01 (`InpCheDoLot=0`). Muốn % rủi ro: `InpCheDoLot=1`, `InpRuiRoPct=0.5`.
- Delays: Zero latency (để so với Python); có thể chạy thêm "Random delay".
- Danh sách symbol XM gợi ý (tên có thể có hậu tố như `#`, `.`, `micro` — xem Market Watch → Symbols):
  FX: EURUSD GBPUSD USDJPY AUDUSD NZDUSD USDCAD USDCHF EURGBP EURJPY EURCHF EURAUD EURCAD EURNZD GBPJPY GBPCHF GBPAUD GBPCAD GBPNZD
  AUDJPY AUDNZD AUDCAD AUDCHF NZDJPY NZDCAD NZDCHF CADJPY CADCHF CHFJPY;
  kim loại: GOLD SILVER; năng lượng: OILCash BRENTCash NGASCash; chỉ số: US500Cash US100Cash US30Cash US2000Cash GER40Cash UK100Cash
  FRA40Cash EU50Cash JP225Cash HK50Cash AUS200Cash. Mã nào không có ở XM thì bỏ (Python vẫn giữ để so).
- Có thể dùng **Optimization → "All symbols selected in Market Watch"** (không tối ưu tham số, chỉ chạy lần lượt các mã) để chạy hàng loạt.

## 3. Xuất kết quả gửi lại
Cho mỗi lần chạy (EA × mã × giai đoạn):
1. Tab **Backtest** → chuột phải → **Report → HTML** (hoặc Open XML) → lưu tên `v24_<RSI|MRZ>_<MA>_<2004|2015>.html`.
2. Tab **Positions/Deals** → chuột phải → **Report** đã gồm danh sách deal; nếu chạy hàng loạt thì lưu thêm bảng Optimization Results (XML).
3. Log CSV EA (`InpLogChung=true`): `%APPDATA%\MetaQuotes\Terminal\Common\Files\brain2_v24_rsi_log.csv` / `brain2_v24_mrz_log.csv`.
   Đổi tên theo lần chạy trước khi chạy lần kế (EA ghi nối thêm).
4. Đo phí thật: `python do_phi_xm.py <các file log> --ra reports\phi_xm_v24.json` (xem `tai_lieu/CHAY_MAY_NHA.md`).
5. Nén các file HTML/XML + CSV + JSON gửi lại hoặc commit vào `reports/mt5_v24/` (không chứa số tài khoản/mật khẩu — xoá dòng Account trong HTML nếu có).

Bên box sẽ so: số lệnh, ngày vào/ra từng lệnh, lợi nhuận trung bình/lệnh (bps) theo mã và giai đoạn với `reports/vong24.json`.
