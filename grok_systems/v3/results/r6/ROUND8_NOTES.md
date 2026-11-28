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
