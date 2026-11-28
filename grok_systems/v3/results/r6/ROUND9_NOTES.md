## Vòng 9 — lot tối thiểu 0,10 (vàng) / 0,14 (US500); hai tài khoản cent 100 USD tách riêng

Bạn xác nhận Exness cũng lấy lot nhỏ nhất khoảng 0,14 (t158u), và sẽ đánh **hai tài khoản cent 100 USD tách riêng**: một chỉ vàng, một chỉ SP500 (t159u).

**Giả định lot tối thiểu (cần xác nhận trên MT5 của tài khoản thật):**
- **Vàng (XAUUSDc / XM Micro):** min **0,10 lot**, bước 0,01, 1 lot = 1 oz. Min 0,10 lấy từ XM Micro MT5 (Help Center). Exness Standard Cent ghi chính thức min 0,01; nếu tài khoản vàng Exness của bạn cũng là 0,14 thì lot starter vàng nâng lên 0,14 và DD / gap tăng khoảng 40%.
- **US500c:** min **0,14 lot**, bước giả định 0,01. Trùng với Exness Help Center “Indices” (13/11/2026, US500 chuẩn min 0,14) và lời bạn. Contract size US500c: vẫn **KHÔNG CÓ** — em giả định 1 lot cent = 0,01 USD/điểm (0,01 lot chuẩn). Nếu Specification khác, mọi lot SP500 phải tính lại.
- Số liệu là deals MT5 100% real ticks đã có, **scale tuyến tính theo lot**, chưa chạy lại Tester trên server Exness Cent. W (khóa hedge cuối tuần) bật. Cửa sổ 01/06–27/11/2026. Net in USD và cent (×100).

### 9.1 Tài khoản SP500, vốn 100 USD (ưu tiên — đủ chạy kịch bản gốc)

Cả 5 hệ của sách chỉ-SP500 (u13, u12, u2, up1, up2) đều trên min 0,14 ở mọi bậc. Vốn tối thiểu để giữ đủ 5 hệ theo đúng tỷ lệ lot gốc: **An toàn 35 USD**, Cân bằng 20 USD, Mạnh tay 11 USD. 100 USD là đủ.

| Kịch bản | Số hệ | Lot cent (u13 / u12 / u2 / up1 / up2) | Lãi 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD | A / B |
|---|---|---|---|---|---|---|---|---|
| An toàn | 5/5 | 0,68 / 0,52 / 0,40 / 0,56 / 0,66 | +50 USD (+4.955 cent) | 5,5% | 6/6 (13, 7, 2, 8, 5, 15) | 30% | 7,7% | 20 / 29 |
| **Cân bằng** | 5/5 | 1,10 / 0,85 / 0,69 / 0,94 / 1,07 | **+82 USD (+8.177 cent)** | **9,4%** | 6/6 (22, 12, 2, 13, 8, 25) | 50% | 12,6% | 33 / 49 |
| Mạnh tay | 5/5 | 2,10 / 2,26 / 1,26 / 1,90 / 2,03 | +168 USD (+16.795 cent) | 18,8% | 6/6 (44, 26, 6, 26, 17, 50) | 100% | 24,4% | 69 / 99 |

**Khuyến nghị tài khoản SP500:** chạy **Cân bằng**. An toàn nếu muốn DD thấp hơn. Không chạy Mạnh tay: gap 5% trong phiên ≈ 100% vốn.

### 9.2 Tài khoản vàng, vốn 100 USD (không chạy đủ kịch bản gốc)

Lot quy đổi từ sách 100k xuống 100 USD (L/10 lot cent) hầu hết dưới 0,10. **An toàn, Cân bằng, Đánh tay gốc: 0/8 và 0/10 hệ** đạt min. Chỉ bản Mạnh tay giữ được xs10 (0,12) và xs7 (0,13): +66 USD, DD 9,6%, gap 59%, 6/6 tháng. Ép tất cả hệ (kể cả giỏ g2/x1/gp2) lên 0,10 lot thì DD MT5 **142%**, gap ~300% — không dùng.

Hệ giỏ (g2, g5, g7, x1, gp2) ở 0,10 lot / 100 USD có DD đơn lẻ 22–87%. Chỉ scalp xs* ở 0,10 lot còn DD đơn lẻ dưới 14%.

**Bộ khởi đầu (mọi hệ 0,10 lot cent = 0,10 oz), đã kiểm deals MT5:**

| Bộ | Hệ (lot 0,10) | Lãi 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD | A / B |
|---|---|---|---|---|---|---|---|
| An toàn hơn | xs7 + xs2 | +56 USD (+5.631 cent) | 7,1% | 6/6 (4, 15, 16, 1, 7, 14) | **28%** | 7,6% | 28 / 29 |
| **Cân bằng (khuyên)** | xs7 + xs10 + xs2 | **+90 USD (+9.011 cent)** | **8,0%** | 6/6 (11, 19, 19, 8, 13, 20) | 48% | 10,8% | 39 / 51 |
| Mạnh hơn | xs7 + xs10 + xs2 + xs6 | +124 USD (+12.388 cent) | 9,4% | 6/6 (16, 30, 22, 1, 23, 31) | 71% | 12,5% | 57 / 67 |
| Mạnh tay 4 hệ (lot tối ưu lại) | xs7 0,16, xs10 0,14, xs6 0,11, xs2 0,10 | +152 USD (+15.252 cent) | 13,1% | 6/6 (21, 39, 24, 4, 27, 37) | 96% | 17,1% | 71 / 82 |

Tháng 9 thường yếu nhất nhưng các bộ trên vẫn dương. **Khuyến nghị tài khoản vàng 100 USD:** bộ 3 scalp **xs7 + xs10 + xs2**, mỗi hệ 0,10 lot. Không chạy hệ giỏ trên tài khoản này. Nếu vàng Exness min thật là 0,14: dùng đúng 0,14, lãi/DD/gap roughly ×1,4 (bộ 3 hệ ≈ DD 11%, gap 67%).

InpCatLoPct (scalp, SL 10 USD, lot 0,10, vốn 100): = 10 × 0,10 × 1 / 100 × 100 = **1,0%**.

### 9.3 Vốn tối thiểu để chạy đủ kịch bản gốc (mọi hệ đạt min lot, giữ tỷ lệ lot 100k, DD% không đổi)

| Sách | An toàn | Cân bằng | Mạnh tay | Đánh tay |
|---|---|---|---|---|
| **Chỉ SP500** (min 0,14) | **35 USD** (nút thắt u2) | 20 USD | 11 USD | — |
| **Chỉ Vàng** (min 0,10) | **2.000 USD** (x1, gp2) | **1.250 USD** (gp2) | 714 USD (x1, gp2) | 714 USD (xs3) |
| Chỉ Vàng nếu min cũng 0,14 | 2.800 USD | 1.750 USD | 1.000 USD | 1.000 USD |
| Ghép 2 tài sản (min 0,10/0,14) | 10.000 USD (g7) | 5.000 USD (g7) | 2.000 USD (g7) | 667 USD (xs4, xs9) |

Mốc vàng nếu chấp nhận bỏ hệ lot nhỏ (x1, gp2, g2): Cân bằng 5 scalp còn lại khoảng **250–500 USD**; Đánh tay đủ 10 hệ từ khoảng **714 USD** (min 0,10) hoặc 1.000 USD (min 0,14). Ở 500 USD, Đánh tay mới giữ được 6/10 hệ.

### 9.4 Một tài khoản 100 USD ghép cả hai mã (không phải kế hoạch của bạn, để đối chiếu)

Sau khi loại hệ dưới min, chỉ còn 3 hệ SP500 (u15, u12, u13): An toàn +20 USD / DD 2,7%; Cân bằng +28 USD / DD 3,6%. Yếu hơn tài khoản SP500 tách riêng (thiếu u2, up1, up2). Ép mọi hệ vàng lên 0,10 lot: DD 116%, gap ~370% — không dùng.

Hai tài khoản 100 USD tách riêng tốt hơn một tài khoản 100 USD ghép, vì tài khoản SP500 giữ đủ 5 hệ và tài khoản vàng chọn được bộ scalp vừa min lot.
