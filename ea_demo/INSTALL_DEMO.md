# Cài EA demo brain2 trên MT5 (tài khoản DEMO XM) — vòng 13

> Đây là EA để **chạy thử trên tài khoản DEMO** và so với mô phỏng. Kết quả brain2 đều là **mô phỏng**, không phải tiền thật.
> Chưa biên dịch được trên box (không có MetaEditor) — lần đầu bấm Compile, nếu có lỗi hãy gửi lại dòng lỗi.

## 1. Chép file
1. MT5 → File → Open Data Folder → `MQL5/Experts/` → chép `BRAIN_IBS_Demo.mq5`, `BRAIN_MuaVu_SPX.mq5`.
2. Chép hai file `.set` vào `MQL5/Presets/`.
3. Mở MetaEditor (F4), mở từng file `.mq5`, bấm **Compile** (F7). Phải ra `0 errors`.

## 2. Kiểm tên mã và giờ server
- Market Watch → chuột phải → Symbols → tìm tên chỉ số Mỹ trên XM của bạn (thường `US500Cash`, `US100Cash`; tài khoản khác có thể có hậu tố như `#`, `.`). Sửa input `InpSymbols` / `InpSymbol` cho đúng.
- Giờ server XM = GMT+2 (mùa đông) / GMT+3 (mùa hè Mỹ) — phiên cash Mỹ 09:30–16:00 New York = **16:30–23:00 giờ server**. EA kiểm lúc **22:55 server** (input `InpGioKiem/InpPhutKiem`). Nếu sàn của bạn đóng chỉ số sớm hơn, lùi giờ kiểm cho trước giờ đóng vài phút.

## 3. Gắn EA
- Mở chart bất kỳ (ví dụ US500Cash, khung nào cũng được) → kéo EA vào → tab Inputs → **Load** file `.set` → bật **Algo Trading**.
- `BRAIN_IBS_Demo`: mỗi ngày lúc kiểm, tính IBS của phiên Mỹ hôm đó; IBS < 0,2 → mua `InpLots` (0,10), giữ tới lần kiểm hôm sau; nếu hôm sau vẫn IBS < 0,2 thì giữ tiếp, không thì đóng.
- `BRAIN_MuaVu_SPX`: mỗi ngày đặt khối lượng cho phiên kế tiếp = số quy tắc đang bật × `InpLotMoiQT` (0,05): đầu/cuối tháng, Santa, Halloween (tháng 11–4), năm thứ 3 chu kỳ bầu cử (2027 là năm 3). Có công tắc riêng từng quy tắc.
- Lịch dùng thứ 2–6, **không tính ngày lễ Mỹ** (ngày lễ: sàn đóng thì lệnh không khớp; lệch nhỏ so với mô phỏng, đã đo ~2 % số ngày).

## 4. Nhật ký để so với mô phỏng
EA ghi `MQL5/Files/brain2_ibs_log.csv` và `brain2_muavu_log.csv`: mỗi lần kiểm (bid/ask/spread/IBS hoặc số quy tắc) và mỗi lệnh khớp (giá, spread, **swap**, hoa hồng, lời). Sau 1–3 tháng gửi hai file này để brain2 so phí thật với mô hình phí mô phỏng.

## 5. Rủi ro
Khối lượng cố định nhỏ, không SL (đúng như mô phỏng: giữ 1 ngày / theo lịch). Chỉ chạy trên DEMO. Mô phỏng: IBS S&P CAGR ~4 %, DD ~38 %; danh mục 4 quy tắc CAGR ~2,6 %, DD ~16 % (sau phí CFD + qua đêm).
