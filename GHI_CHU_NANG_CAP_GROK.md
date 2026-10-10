# Ghi chú nâng cấp (Grok trên brain2) — cập nhật 2026-10-10 (khuya, giờ VN)

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
