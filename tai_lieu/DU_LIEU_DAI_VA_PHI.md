# Dữ liệu dài và mô hình phí XM Micro (21/10/2026)

Mục tiêu: backtest Python vòng 2 trên lịch sử **2004–2026** (không chỉ 2,8 năm) với **phí đúng của XM Micro**. Theo quyết định của anh, việc tải dữ liệu chạy trên **máy nhà** (Windows, `C:\Users\DUNG\brain2`, terminal MT5 XM). Box chỉ viết code, test và kiểm tra trên dữ liệu đang có. Không gọi LLM, không đăng nhập web, không vượt chống bot.

## 1. Nguồn dữ liệu (theo thứ tự ưu tiên)

| # | Nguồn | Nội dung | Giờ | Cách lấy | Ghi chú |
|---|---|---|---|---|---|
| 1 | **MT5 XM (server của chính sàn)** | Nến M1 + H1, mẫu tick (bid/ask), `symbol_info` | giờ server XM (GMT+2/+3) | `mt5tools/tai_lich_su_mt5.py` (gói `MetaTrader5`, `copy_rates_range` / `copy_ticks_range`) | Giống hệt dữ liệu tester. Độ dài M1/tick do XM quyết định: **CHƯA ĐO ĐƯỢC** cho tới khi máy nhà chạy (bảng `ma.csv` ghi H1 XM có từ 2016–2017) |
| 1b | **MT5 MetaQuotes-Demo (slot riêng)** | M1 + H1 + tick, thường dài hơn XM | giờ server MetaQuotes → hiệu chỉnh theo XM | `tai_lich_su_mt5.py <slot> --vai phu` | Chỉ dùng khi XM thiếu lịch sử; xem mục 6 |
| 2 | **histdata.com** | M1 ASCII, giá bid, từ 2000–2010 tuỳ cặp | EST cố định (UTC−5) → đổi sang giờ server | `nhan/tai_du_lieu.py --chi-histdata`: gửi form tải thường của trang (anh đã cho phép), 1 luồng, nghỉ 6–12 giây | Đã thử trên box 21/10: EURUSD 2000 tải được (143.167 nến M1, từ 31/05/2000); GBPCAD/GBPNZD/EURCHF năm 2000 không có |
| 3 | **Dukascopy datafeed** | Nến phút **BID + ASK** → spread lịch sử | UTC → giờ server | `nhan/tai_du_lieu.py --chi-duka`: mẫu 2 ngày giữa tuần mỗi tháng, 2004→nay | Box 21/10 bị **429/503** liên tục. Code lùi theo cấp số nhân (60 giây ×2ⁿ, tối đa 1 giờ, theo Retry-After), 1 luồng |

Mọi tệp thô đều nằm trong `data/du_lieu_dai/` (git bỏ qua). Tệp đã có thì bỏ qua (chạy lại sẽ tự tiếp tục). Trạng thái lưu ở `data/du_lieu_dai/trang_thai_<nguồn>.json` và `data/du_lieu_dai/mt5/<server>/<MÃ>/trang_thai.json`.

**Mã cần tải (19, của 78 hệ ĐẠT):** EURUSD, GBPCAD, GBPNZD, EURCHF, XAUUSD (GOLDmicro), EURGBP, USDCAD, USDJPY, CADJPY, AUDUSD, AUDJPY, EURCAD, GBPUSD, CHFJPY, NZDJPY, EURAUD, AUDNZD, EURNZD, GBPAUD.

## 2. Hướng dẫn chạy trên máy nhà (khi máy rảnh)

1. `git pull` trong `C:\Users\DUNG\brain2`. Cần Python với `MetaTrader5`, `pandas`, `numpy` (đã có, `do_phi_san.py` dùng chung).
2. Mở terminal **XM** đang đăng nhập. Vào *Tools → Options → Charts → Max bars in chart* = **Unlimited** (nếu không, MT5 cắt lịch sử), rồi khởi động lại terminal.
3. Chạy `mt5tools\TAI_LICH_SU_MT5.bat` (đường dẫn terminal khác thì truyền vào: `TAI_LICH_SU_MT5.bat "D:\XM\terminal64.exe"`). Script lần lượt:
   1. `python mt5tools\tai_lich_su_mt5.py <terminal>`: M1 theo tháng từ 2004-01, H1 toàn bộ, mẫu tick, `symbol_info.json`. Ước tính vài chục phút đến vài giờ, tuỳ lượng lịch sử XM trả về.
   2. `python -m nhan.tai_du_lieu --chi-histdata`: khoảng 19 mã × 27 kỳ ≈ 500 lần tải, 6–12 giây mỗi lần, ≈ 1,5–3 giờ.
   3. `python -m nhan.tai_du_lieu --chi-duka`: 19 × 2 phía × khoảng 550 ngày mẫu ≈ 21.000 tệp nhỏ; khi bị giới hạn tốc độ có thể mất **nhiều giờ đến 1–2 ngày**. Muốn bỏ qua bước 2–3 thì chạy `tai_lich_su.ps1 -BoDuPhong`.
   4. `python -m nhan.du_lieu_dai --dung`: gộp nguồn (MT5 XM ưu tiên, histdata lấp chỗ trống), dựng M5 giờ server, kiểm tra độ phủ, lỗ hổng và độ lệch so với nến MT5 thật. Kết quả ra `reports/du_lieu_dai/PHU_SONG.md`.
   5. `python -m nhan.phi_dai`: tính hệ số spread theo năm, ghi `config/phi_xm_micro.json`.
4. Dừng bằng Ctrl+C bất kỳ lúc nào; chạy lại sẽ tự tiếp tục. Sau đó commit `reports/du_lieu_dai/` và `config/phi_xm_micro.json` (**không** commit `data/`).
5. Chạy vòng 2 trên dữ liệu dài: `set BRAIN_ONG_DAN_DU_LIEU=data\du_lieu_dai\du_lieu_dai.json`, rồi `python -m nhan.vong2 --top 40`.

## 3. Múi giờ và kiểm tra nối dữ liệu

- Giờ server XM = giờ New York + 7 (GMT+2 mùa đông, GMT+3 mùa hè, đổi cùng ngày DST của Mỹ). histdata (EST cố định) được đổi: +5 giờ ra UTC → New York → +7. Có test cho cả mùa đông lẫn mùa hè.
- **Đã đo trên box** (dữ liệu histdata 2024–2026 đang có, đổi về giờ server, so với nến H1 của chính các lần chạy MT5 XM 12/2023–10/2026). Độ lệch giờ tốt nhất (thử −2…+2 giờ) đều bằng **0**, tức múi giờ khớp:

| Mã | Lệch close p50 / p95 (điểm) | Nến H1 chung |
|---|---|---|
| EURUSD | 8 / 12 | 8.293 |
| GBPCAD | 15 / 27 | 17.034 |
| GBPNZD | 15 / 36 | 16.988 |
| XAUUSD (GOLD) | 6,5 / 37,5 (điểm 0,01) | 16.202 |
| EURGBP | 8 / 12 | 17.031 |
| USDCAD | 9 / 13 | 17.024 |
| CADJPY | 15 / 21 | 17.030 |
| AUDUSD | 7 / 10 | 16.585 |
| EURCAD | 8 / 16 | 17.032 |
| GBPUSD | 8 / 14 | 17.025 |
| CHFJPY | 9 / 33 | 17.007 |
| EURAUD | 8 / 19 | 17.010 |
| AUDNZD | 11 / 17 | 17.040 |
| EURNZD | 7 / 34 | 17.040 |
| GBPAUD | 6 / 31 | 17.030 |
| EURCHF, USDJPY, AUDJPY, NZDJPY | CHƯA ĐO ĐƯỢC (các hệ của những mã này chỉ có nến H4 MT5) | — |

  Mức lệch khoảng 0,6–1,5 pip ở p50 là chênh lệch nguồn bid (histdata/ECN so với XM), không phải lệch giờ. Vì vậy MT5 XM được ưu tiên khi có.

## 4. Mô hình phí XM Micro (`nhan/phi_dai.py`, `config/phi_xm_micro.json`, dùng trong `nhan/tai_khoan.py`)

`spread(t) = spread_gio_XM[giờ server] × hệ_số_năm[năm]`

- **Spread theo giờ: ĐO.** Lấy từ tick thật của tài khoản XM (`reports/phi_san/XMGlobal-MT5_10/spread_gio.csv`, tháng 10/2026); `ho_so_phi` đã dùng từ trước.
- **Hệ số theo năm:** median spread năm y chia median spread năm mốc, tính trên giờ 02–22. Nguồn ưu tiên là tick XM (MT5 máy nhà), sau đó tới Dukascopy (nối với XM qua năm có cả hai nguồn). Năm không có nguồn lấy theo năm đo được sớm nhất, nhãn **NGOẠI SUY**. Hiện tại **CHƯA ĐO ĐƯỢC** (chưa có dữ liệu tải về) nên hệ số = 1,0. Lưu ý: cột `spread_point` trong nến MT5 tester gần như phẳng (ví dụ GBPNZD 65–69 điểm qua cả 4 năm, EURUSD 18–19), không dùng làm hệ số năm được.
- **Hoa hồng: ĐO = 0 USD/lot.** Tổng cột hoa hồng của **37.773 deal** trong `reports/ong_dan/ket_qua_mt5/*_lenh_mt5.csv` = 0,00 USD.
- **Swap: ĐO 06/10/2026** (điểm/lot/đêm, ngày ×3 = thứ Tư). Swap lịch sử theo lãi suất từng năm: **CHƯA ĐO ĐƯỢC**, tạm dùng mức hiện tại.

| Mã | Symbol XM | Spread p50 (giá) | Spread p90 (giá) | Swap mua | Swap bán |
|---|---|---|---|---|---|
| EURUSD | EURUSDmicro | 0,00020 | 0,00022 | −7,48 | 1,23 |
| GBPCAD | GBPCADmicro | 0,00055 | 0,00058 | 0,57 | −16,22 |
| GBPNZD | GBPNZDmicro | 0,00076 | 0,00085 | −3,55 | −19,32 |
| EURCHF | EURCHFmicro | 0,00032 | 0,00034 | 1,73 | −12,18 |
| XAUUSD | GOLDmicro | 0,55 | 0,57 | −83,83 | 20,64 |
| EURGBP | EURGBPmicro | 0,00024 | 0,00025 | −5,40 | 0,49 |
| USDCAD | USDCADmicro | 0,00029 | 0,00032 | 2,01 | −11,78 |
| USDJPY | USDJPYmicro | 0,024 | 0,026 | 2,11 | −29,59 |
| CADJPY | CADJPYmicro | 0,041 | 0,045 | −1,08 | −11,48 |
| AUDUSD | AUDUSDmicro | 0,00023 | 0,00025 | −1,71 | −3,20 |
| AUDJPY | AUDJPYmicro | 0,035 | 0,037 | 3,67 | −16,21 |
| EURCAD | EURCADmicro | 0,00034 | 0,00037 | −5,05 | −8,14 |
| GBPUSD | GBPUSDmicro | 0,00024 | 0,00026 | −4,35 | −2,96 |
| CHFJPY | CHFJPYmicro | 0,039 | 0,044 | −17,80 | −4,10 |
| NZDJPY | NZDJPYmicro | 0,037 | 0,041 | −1,51 | −11,91 |
| EURAUD | EURAUDmicro | 0,00037 | 0,00040 | −15,25 | 1,68 |
| AUDNZD | AUDNZDmicro | 0,00040 | 0,00045 | −0,84 | −12,96 |
| EURNZD | EURNZDmicro | 0,00049 | 0,00055 | −11,49 | −10,57 |
| GBPAUD | GBPAUDmicro | 0,00045 | 0,00051 | −11,78 | −5,10 |

## 5. Trạng thái

- Box 21/10/2026, khoảng 10:00 (UTC+7): đã dừng mọi tiến trình tải trên box. Đã tải thử 1 tệp histdata (EURUSD 2000); Dukascopy bị 429/503.
- Chạy lại vòng 2 trên dữ liệu dài cho 20 hệ có tín hiệu Python: **CHƯA ĐO ĐƯỢC**, chờ máy nhà chạy mục 2.

## 6. Nguồn dự phòng MetaQuotes-Demo (slot MT5 riêng)

Khi XM không trả đủ lịch sử dài, lấy lịch sử từ server **MetaQuotes-Demo** bằng một terminal MT5 **riêng**. Slot này **không bao giờ** là terminal XM giao dịch (`C:\Program Files\XM Global MT5\terminal64.exe`). Script tự từ chối nếu: (a) đường dẫn là terminal XM, hoặc (b) slot phụ đang đăng nhập server có chữ "XM".

**Tạo slot (làm một lần, bằng tay, khi máy nhà rảnh):**
1. Tải bộ cài MT5 gốc của MetaQuotes (`mt5setup.exe` từ metatrader5.com). Khi cài, chọn *Settings* → thư mục **`C:\MT5_lich_su_metaquotes`**. Không cài đè lên thư mục XM.
2. Chạy ở chế độ portable để dữ liệu nằm trong thư mục slot: tạo lối tắt `C:\MT5_lich_su_metaquotes\terminal64.exe /portable`.
3. Trong terminal đó: *File → Open an Account* → tìm **MetaQuotes Software Corp.** → chọn **MetaQuotes-Demo** → *Open a demo account* → điền thông tin → *Next*. Đây là hộp thoại thường của MT5; tài khoản demo miễn phí, không có tiền thật.
4. **Thông tin đăng nhập demo** (số tài khoản, mật khẩu) MT5 tự lưu trong slot. Nếu cần ghi lại, chỉ ghi ở `C:\Users\DUNG\mat_khau_rieng\metaquotes_demo.txt` (ngoài repo). **Không bao giờ** đưa vào `brain2`, git hay chat. Script không đọc mật khẩu: nó gắn vào terminal đang đăng nhập.
5. *Tools → Options → Charts → Max bars in chart = Unlimited*, rồi khởi động lại slot.

**Chạy:** `mt5tools\TAI_LICH_SU_MT5.bat` tự nhận slot nếu có `C:\MT5_lich_su_metaquotes\terminal64.exe`; đường dẫn khác thì truyền làm tham số thứ 2: `TAI_LICH_SU_MT5.bat "<XM>" "<slot>"`. Có thể chạy riêng: `python mt5tools\tai_lich_su_mt5.py "C:\MT5_lich_su_metaquotes\terminal64.exe" --vai phu`. Dữ liệu lưu theo server: `data\du_lieu_dai\mt5\MetaQuotes-Demo\<MÃ>\`.

**Tên mã:** MetaQuotes dùng tên không hậu tố (`XAUUSD`, `EURUSD`…); XM dùng `GOLDmicro`, `EURUSDmicro`. Script thử lần lượt `GOLDmicro / GOLD / XAUUSDmicro / XAUUSD` và `<MÃ>micro / <MÃ># / <MÃ>`.

**Gộp và hiệu chỉnh (`nhan/du_lieu_dai.py`):**
- Thứ tự ưu tiên: **MT5 XM** → MT5 server khác (MetaQuotes-Demo) → histdata. Mỗi mã lấy hợp tất cả nguồn; nến nào XM có thì luôn dùng XM, nguồn sau chỉ lấp chỗ trống, nên mã nào cũng được phủ dài nhất có thể.
- Mỗi nguồn phụ được **hiệu chỉnh trên đoạn chồng lấn** với phần đã gộp (H1, cần ≥ 200 nến chung): (1) **lệch giờ** trong khoảng −3…+3 giờ, chọn mức cho lệch close nhỏ nhất; nếu giờ server MetaQuotes khác XM, bước này tự dịch; (2) **lệch giá** = median(XM − nguồn phụ) sau khi dịch giờ, cộng vào toàn bộ nguồn phụ. Kết quả lưu trong `hieu_chinh` của `reports/du_lieu_dai/PHU_SONG.json`, gồm lệch giờ, lệch giá, số nến chung và lệch còn lại sau hiệu chỉnh.
- Báo cáo `PHU_SONG.md` có bảng **nguồn theo năm** (% nến M5 của từng nguồn trong mỗi năm), để biết năm nào là dữ liệu XM thật và năm nào là MetaQuotes hay histdata.
- Lưu ý: spread và swap của MetaQuotes-Demo **không** dùng cho mô hình phí. Phí luôn là phí XM (mục 4).
