# KẾT QUẢ TEST 5 — BẢN ĐỒ XÁC SUẤT THEO MỐC PHIÊN (Vàng & S&P 500)

**Câu hỏi:** "Mở cửa ngày ở 4000 thì giá hay đi về đâu nhất?" Mốc được kiểm tra gồm: giá mở cửa ngày/phiên, PDC/PDH/PDL/PDM (đóng, cao, thấp, giữa ngày trước), số tròn, đỉnh/đáy giờ đầu, các bậc ±% và ±ATR, và Sq9 45/90/180.

**Dữ liệu:**
- Nến 1h từ Yahoo (giới hạn khoảng 2 năm):
  - GC=F và ES=F: 17/07/2024 → 13/11/2026, 582 ngày.
  - ^GSPC phiên chính (RTH): 10/01/2024 → 13/11/2026, 707 ngày.
- Chia đôi IS/OOS theo thời gian:
  - Futures: IS đến 02/09/2025, OOS từ 03/09/2025.
  - SPX: tách ở 03/06/2025.
- Kiểm tra độ bền dài hạn bằng nến ngày: GC=F 2008–2026 (4.557 ngày); ES=F và ^GSPC 2000–2026 (6.585 và 6.738 ngày). Có thống kê theo từng năm.

**Định nghĩa:**
- "Ngày" futures bắt đầu lúc 18:00 New York, tức 05:00 (mùa hè Mỹ) hoặc 06:00 (mùa đông Mỹ) giờ VN (UTC+7). Ngày này trùng với nến D của CME trên TradingView. XAUUSD của broker mở lúc 17:00 NY nên gần như tương đương. Có thêm biến thể "ngày UTC" (07:00 VN) cho vàng, kết quả gần giống.
- SPX RTH: mở 09:30 NY, tức 20:30/21:30 VN.
- ATR = ATR14 ngày, lấy giá trị của hôm trước, nên không nhìn trước (no lookahead).
- "Chạm" là chạm bất kỳ lúc nào trong ngày đó, tính đến lúc đóng ngày.
- **MAE** là mức giá đi ngược tối đa trước khi chạm, tính theo đơn vị ATR ngày.

**Cách so "baseline":**
1. Với đích cấu trúc (PDC, PDH, PDL, PDM, số tròn, Sq9), xác suất kỳ vọng lấy từ **đường cong khoảng cách**. Đường cong này cho biết P(chạm | cách open bao nhiêu ATR), gộp mọi ngày. Bootstrap theo tuần, sau đó hiệu chỉnh FDR Benjamini–Hochberg.
2. Với hành vi "về lại mốc sau một nhịp", so với **mốc giả** đặt lệch ±0,1/0,2 ATR so với mốc thật.

---

## 1. KẾT LUẬN NGẮN

1. **Có nhiều đích tỷ lệ cao và ổn định** (85–94%, IS ≈ OOS, và 18–26 năm dữ liệu ngày xác nhận). Danh sách ở mục 2.
2. **Nhưng không đích nào "hút giá" hơn khoảng cách của nó.**
   - Đích cấu trúc: 0/207 phép so với đường cong khoảng cách có ý nghĩa sau FDR (q<0,05). PDC, PDH, PDL, PDM, số tròn và Sq9 chạm với tần suất bằng đúng một mức giá bất kỳ cách open cùng số ATR.
   - "Về lại mốc mở phiên": lệch so với mốc giả chỉ khoảng ±3–5 điểm %. Dấu thì đổi chiều: nhịp 0,15 ATR cho dương, nhịp 0,25 ATR cho âm. Đây là dấu hiệu tạo tác của cách đo bằng nến 1h, không phải lực hút thật.
   - **Tóm lại: xác suất chạm chỉ do khoảng cách và biến động quyết định.** Gần thì chạm nhiều, xa thì chạm ít.
3. **Đo khoảng cách bằng ATR, đừng dùng % hay số tròn cố định.**
   - Vàng chạm +0,5% từ open: IS 59%, OOS 75%. Lý do là giá vàng tăng gấp đôi và biến động thay đổi.
   - Vàng chạm +0,25 ATR: IS 69,6%, OOS 72,6%, ổn định.
   - Số tròn $25 của vàng: IS 67%, OOS 85%, không ổn định vì cùng lý do.
4. **Scalp:** đã thử 138 tổ hợp, gồm:
   - fade nhịp 0,15/0,25/0,5 ATR quay về mốc mở ngày/Á/London/NY;
   - đi về PDC;
   - đi về PDH/PDL gần nhất;
   - mỗi tổ hợp với SL 0,25/0,5/1 ATR, có trừ spread (vàng 0,3, ES 0,25).
   
   Kết quả: **không tổ hợp nào có kỳ vọng dương ở cả IS lẫn OOS**, và 0 tổ hợp có ý nghĩa sau FDR. Win-rate cao (65–78%) nhưng lệnh thua lớn hơn, nên kỳ vọng ≈ 0 hoặc âm. Con số OOS đẹp nhất là ES về PDC với SL 0,25 ATR: +0,21R, n=59. Nhưng IS của nó là −0,21R, nên đây chỉ là nhiễu.
5. **Dùng thực tế:** bản đồ này phù hợp để **đặt chốt lời (TP) thực tế và tránh đặt TP quá xa**. Ví dụ: xác suất chạm ±0,5 ATR cả hai phía trong cùng ngày chỉ khoảng 5–6%. Bản đồ **không phải tín hiệu vào lệnh** có lợi thế.

---

## 2. TOP-10 MỖI SẢN PHẨM

Cột:
- **P**: tỷ lệ chạm (%).
- **IS/OOS**: tỷ lệ ở nửa đầu / nửa sau mẫu.
- **Ổn định**: |IS−OOS| ≤ 7 điểm và n ≥ 150.
- **> baseline?**: có hơn baseline khoảng cách / mốc giả không.
- **t½**: số giờ trung vị tới lúc chạm, tính từ mốc.
- **MAE**: trung vị / phân vị 80 (đơn vị ATR ngày).

### 2a. VÀNG (GC=F, ngày futures 18:00 NY), n = 582

| # | Hành vi / đích (tính từ open ngày) | P | IS / OOS | Ổn định | > baseline? | t½ | MAE (med/p80) |
|---|---|---|---|---|---|---|---|
| 1 | Chạm open ±0,1% (khoảng ±4 USD), mỗi phía | 93 / 92 | 92/95 · 89/95 | ✔ | = khoảng cách | 1h | 0,07 / 0,19 |
| 2 | Chạm PDC (open futures thường mở sát PDC) | 93,6 | 95,4 / 92,0 | ✔ | = (−1,1 điểm) | 1h | 0,0 |
| 3 | Số tròn 10 USD gần nhất, phía trên / dưới | 90,7 / 88,5 | 88/93 · 84/93 | ✔ | = | 1–2h | 0,1 |
| 4 | Sau giờ đầu, giá quay lại chạm open ngày | 89,2 | 91,5 / 87,0 | ✔ | (mốc giả cũng tương tự) | — | — |
| 5 | Đỉnh giờ đầu bị vượt / đáy giờ đầu bị thủng | 88,5 / 85,2 | 90/87 · 87/83 | ✔ | — | — | — |
|   | ↳ nếu giờ đầu **tăng**: đỉnh bị vượt 93,3%, đáy bị thủng 79,5% · nếu giờ đầu **giảm**: đáy bị thủng 91,2%, đỉnh bị vượt 83,5% | | IS/OOS lệch ≤ 10 | ✔ | | | |
| 6 | **PDH hoặc PDL** bị lấy (ít nhất một bên) | 87,3 | 85,9 / 88,6 | ✔ (2008–26: 84,5%, theo năm 78–89) | = | — | — |
| 7 | Phá **cả** đỉnh và đáy giờ đầu | 73,7 | 77,0 / 70,6 | ✔ | — | — | — |
| 8 | Chạm open +0,25 ATR / −0,25 ATR | 71,1 / 64,4 | 70/73 · 65/64 | ✔ | (đây chính là đường cong) | 5–6h | 0,13 / 0,3 |
| 9 | Chạm PDM (giữa ngày trước) | 67,2 | 66,1 / 68,2 | ✔ (2008–26: 53,5%; 5 năm gần: 65%) | = (+2,0, q=0,8) | 4h | 0,1 |
| 10 | Về lại mốc open sau nhịp 0,15 ATR | 73,6 | 73,1 / 74,0 | ✔ | = mốc giả (73,6) | 2h | 0,2 / 0,6 |

Tỷ lệ thấp, cần biết để **đừng đặt TP vào đó**:
- PDH bị vượt: 52,9%. PDL bị thủng: 44,0%.
- Cả PDH và PDL đều bị lấy: 9,6%.
- ±0,5 ATR: một phía khoảng 40%, cả hai phía 5,7%.
- ±1 ATR: khoảng 12%.
- Sq9 ±45° (khoảng 0,4 ATR) chạm 45–49%. Sq9 ±90°: khoảng 19%. Không khác gì đường cong khoảng cách.

### 2b. S&P 500 — ES=F (ngày futures 18:00 NY), n = 582

| # | Hành vi / đích | P | IS / OOS | Ổn định | > baseline? | t½ | MAE |
|---|---|---|---|---|---|---|---|
| 1 | Chạm PDC | 92,1 | 90,5 / 93,6 | ✔ (2000–26: 92,1%) | = | 1h | 0,0 |
| 2 | Đỉnh giờ đầu bị vượt | 92,1 | 90,1 / 94,0 | ✔ | — | — | — |
| 3 | Sau giờ đầu, quay lại chạm open ngày | 90,7 | 90,1 / 91,3 | ✔ | — | — | — |
| 4 | Chạm open ±0,1% (khoảng ±7 điểm), mỗi phía | 89,5 / 88,5 | ~89/90 | ✔ | = | 2–3h | 0,08 / 0,2 |
| 5 | **PDH hoặc PDL** bị lấy | 88,0 | 88,0 / 88,0 | ✔ (2000–26: 87,4%, theo năm 81–92) | = | — | — |
| 6 | Đáy giờ đầu bị thủng | 86,2 | 86,6 / 86,0 | ✔ | — | — | — |
|   | ↳ nếu giờ đầu **tăng**: đỉnh giờ đầu bị vượt 94,3% · nếu giờ đầu **giảm**: đáy giờ đầu bị thủng 91,9% | | | ✔ | | | |
| 7 | Số tròn 25 điểm gần nhất, trên / dưới | 79,9 / 78,2 | 77/83 · 76/81 | ✔ | = | 4h | 0,1 |
| 8 | Phá cả đỉnh và đáy giờ đầu | 78,4 | 76,7 / 79,9 | ✔ | — | — | — |
| 9 | Về lại mốc open sau nhịp 0,15 ATR | 77,4 | 76,9 / 77,9 | ✔ | +3,4 so với mốc giả (q=0,05, xem mục 1.2) | 5h | 0,2 / 0,5 |
| 10 | Chạm PDM | 67,5 | 67,8 / 67,2 | ✔ (2000–26: 65,2%) | = (+4,1, q=0,6) | 8h | 0,1 |

Thêm:
- Chạm +0,25 ATR: 66,5%. Chạm −0,25 ATR: 64,1%.
- ±0,5 ATR: một phía khoảng 39%, cả hai phía 6,5%.
- PDH bị vượt: 56%. PDL bị thủng: 45%.
- Mở trên PDC → PDL bị thủng chỉ 39%. Mở dưới PDC → PDL bị thủng 51%.

### 2c. S&P 500 — ^GSPC phiên chính (mở 09:30 NY; nến 1h nên giờ đầu là nến 09:30–10:30), n = 707

| # | Hành vi / đích | P | IS / OOS | Ổn định | > baseline? | t½ | MAE |
|---|---|---|---|---|---|---|---|
| 1 | PDH hoặc PDL bị lấy | 90,1 | 88,2 / 92,0 | ✔ (2000–26: 88,2%) | = | — | — |
| 2 | Chạm open ±0,1% | 84,6 / 82,3 | ~85/82 | ✔ | = | 1h | 0,15 |
| 3 | **Gap lên (mở trên PDC) → PDH bị vượt** | 75,9 | 73,8 / 77,9 | ✔ n=432 | (khoảng cách nhỏ hơn) | — | — |
| 4 | **Gap xuống → PDL bị thủng** | 71,3 | 69,9 / 72,7 | ✔ n=275 | (khoảng cách nhỏ hơn) | — | — |
| 5 | Giờ đầu tăng → đỉnh giờ đầu bị vượt | 81,5 | 84,0 / 79,4 | ✔ n=363 | — | — | — |
| 6 | Giờ đầu giảm → đáy giờ đầu bị thủng | 77,6 | 79,1 / 76,0 | ✔ n=344 | — | — | — |
| 7 | Chạm open +0,2% / −0,2% | 70,2 / 68,0 | ổn định | ✔ | = | 1h | 0,14 |
| 8 | Số tròn 25 điểm gần nhất, trên / dưới | 69,3 / 69,5 | 68/70 · 69/70 | ✔ | = | 1h | 0,1 |
| 9 | Chạm +0,25 ATR / −0,25 ATR | 61,2 / 60,7 | 60/63 · 61/60 | ✔ | = | 1h | 0,12 |
| 10 | Sau giờ đầu, quay lại open | 58,6 | 60,1 / 57,1 | ✔ | — | — | — |

Lưu ý: trên ^GSPC, PDC chỉ chạm **57,8%**, khác hẳn ES (92%). Lý do là chỉ số phiên chính có gap thật lúc 09:30, còn ES đã giao dịch xuyên đêm. Mở trong biên ngày trước → PDC chạm 67%. Mở trên PDH / dưới PDL → PDC chạm chỉ 46% / 38%.

---

## 3. ĐIỀU KIỆN (chỉ giữ cái ổn định, n ≥ 150)
- **Hướng giờ đầu** mạnh nhất cho "giá phá đỉnh/đáy giờ đầu theo hướng đó": 91–94% với futures, 78–82% với SPX RTH. Hiệu ứng chênh khoảng 10–35 điểm, ổn định IS/OOS. Đây là quán tính ngắn hạn. Tuy vậy, khoảng cách từ giá cuối giờ đầu tới đỉnh/đáy giờ đầu cũng nhỏ hơn ở phía đó, nên phần lớn vẫn là hiệu ứng khoảng cách.
- **Gap so với PDC** chỉ quan trọng với SPX RTH (xem 2c #3–4). Với futures, chênh lệch ≤ 12 điểm.
- **Mức ATR** (tercile) và **thứ trong tuần**: không có khác biệt ổn định.
- Điều kiện theo hướng giờ đầu cho PDH/PDL/PDC **không đưa vào top** vì có tính cả giờ đầu (đã biết một phần kết quả).

## 4. SCALP (có spread, SL theo ATR, thoát cuối ngày)
- Tổng cộng 138 tổ hợp (sản phẩm × phiên × chiến lược × SL).
- R_IS > 0 và R_OOS > 0: **0**. Có ý nghĩa sau FDR: **0**.
- Win-rate 60–78% không đủ bù lệnh thua: kỳ vọng nằm trong khoảng −0,05 đến 0R mỗi lệnh.
- Bảng đầy đủ: `results5/scalp_summary.csv`.

## 5. HẠN CHẾ
- Nến 1h nên:
  - Không đo được thứ tự chạm trong cùng một nến (các trường hợp mơ hồ bị bỏ).
  - "NY open" của futures là nến 09:00 NY (gần đúng 09:30).
  - Chưa có đỉnh/đáy phiên đêm (overnight H/L) cho RTH.
- Mẫu intraday chỉ khoảng 2,3 năm. Mẫu dài hạn chỉ dùng nến ngày.
- Số tròn và % phụ thuộc mặt bằng giá, nên không bền theo thời gian. Dùng bậc ATR.
- Tất cả các con số là **tần suất lịch sử**, không phải lợi thế giao dịch.

## 6. FILE
- `test_e_session_map.py`: tạo sự kiện.
- `analyze_e.py`: phân tích.
- `test_e_daily_history.py`: kiểm tra 2000/2008–2026.
- `results5/`: `targets_map.csv`, `behaviors_map.csv`, `conditional.csv`, `scalp_summary.csv`, `daily_history_by_year.csv`.
- `session_prob_map.pine`: chỉ báo vẽ các mốc kèm xác suất đã hardcode (chưa compile trên TradingView).
