# DSR + stress cho tay_v2 US500 ×1,5/×0,5 và stress CHUNG VỐN thật (27/11, 21:50 giờ VN)

Mã nguồn: `sp500/ma/stress_chung.py`, dùng lại phần nạp dữ liệu của `danh_muc.py`. Kết quả nằm trong `sp500/ket_qua/stress_chung/`: `tay_us_dsr.csv`, `tay_us_stress4.csv`, `chung_von.csv`, `chung_von_tomtat.csv`.
Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC. Mọi số dưới đây đều đo được.

Các hệ đã chạy lại và khớp số gốc:

| Hệ | Phiên bản | Chạy lại |
|---|---|---|
| HYB+AG US500 | — | +1.501,90 |
| tay_v2 US500 `p1_union_es` | engine `5f393920` | +657,83 |
| tay_v2 US500 ×1,5/×0,5 (ngữ cảnh H60) | — | +920,39 |
| Lệnh phụ US500 (union, giữ 60′) | — | +697,02 |
| tay_v2 XAU 11/11 | commit `59672872`: `L0 0,01, K4, maxL20, flcap 0,15, hfrac 1, loss_close 0,30, adx_th 30, cooldown 240`, lọc delta15 | +15.930,00, DD 31,08% (khớp BAO_CAO_VANG_11) |

## 1. tay_v2 US500 ×1,5/×0,5

**DSR** tính theo lãi/lỗ ngày (153 ngày, 01/06–26/11), trên 12 biến thể đã thử ở vòng trước (H30/H60 × 6 mức nhân). Ngưỡng Sharpe kỳ vọng tối đa của nhóm SR₀ = 0,019/ngày.

| Biến thể | Sharpe ngày | PSR | DSR |
|---|---:|---:|---:|
| gốc ×1/×1 | 0,191 | 0,987 | 0,978 |
| H60 ×1,5/×0,5 | 0,204 | 0,996 | **0,993** |
| H30 ×1,5/×0,5 | 0,196 | 0,996 | 0,991 |
| H60 ×2/×0,5 | 0,211 | 0,997 | 0,994 |
| H60 ×1,25/×0,75 | 0,176 | 0,988 | 0,978 |

- Bước 6 **đạt** (DSR ≥ 0,95).
- Tuy vậy gốc cũng đạt 0,978, vì 12 biến thể gần như cùng một đường vốn. DSR cho thấy hệ có lợi thế, **không** chứng minh riêng phần lợi do hệ số lot.
- Cột `dsr_kieu_cu` (cách tính theo nến của worker Phần 2) = 1,00 cho mọi biến thể, nên không phân biệt được gì.

**4 stress tổng hợp.** Gap đặt tại đáy vốn của chính biến thể đó; grind tính từ 01/06. Ngữ cảnh dữ liệu giữ nguyên.

| Kịch bản | Gốc: lãi / DD % | ×1,5/×0,5: lãi / DD % | ×1,5/×0,5: lỗ thả nổi tệ nhất |
|---|---|---|---:|
| gap −10% | +543,28 / 1,65 | +708,58 / 1,85 | −226,61 |
| gap −20% | +454,25 / 1,63 | +633,65 / 1,72 | −182,50 |
| grind −20%/60 ngày | +450,82 / 1,63 | +628,60 / 1,72 | −182,50 |
| grind −35%/120 ngày | +301,49 / 1,68 | +437,42 / 1,99 | −266,52 |

- Đạt 4/4, không cháy.
- 7 cửa sổ sập lịch sử không có dữ liệu Fxaurum nên không có lệnh (trung tính). Tổng cộng 11/11 sống.
- Gốc gap −10% ra +543,28, còn worker Phần 2 ghi +539,99. Chênh vì thời điểm đáy vốn lấy hơi khác.
- **tay_v2 US500 ×1,5/×0,5 giờ đã qua đủ các bước 1–6** (bước 7 bóng = logger đang ghi `vah_val_pha` / `cvd_pk` / `delta15`).
- Lưu ý: 93,7% lệnh vào vốn đã cùng chiều với ngữ cảnh, nên phần lớn mức tăng là do lot lớn hơn.

## 2. Stress chung vốn thật

**Cách làm:**
- Cùng một cú sốc giá, tại cùng một thời điểm UTC, áp cho mọi hệ trong danh mục.
- Mỗi hệ chạy lại engine trên giá đã sốc. HYB+AG dựng lại toàn bộ đặc trưng qua `runag.Data`; tay XAU tính lại ATR/ADX/slope bằng `chay_vang_11._pack_from_raw`.
- Equity từng hệ được cộng theo phút trên vốn chung 10k.
- "Cháy" = equity chung ≤ 0. Kiểm thêm DD < 80% của 10k và của 30k (gồm tiền nạp thêm).
- Gap thử tại đáy vốn chung và tại đáy vốn từng hệ, lấy trường hợp tệ nhất. Khi có vàng, thử cả vàng −g và vàng +g (vàng thường tăng khi cổ phiếu sập).
- 7 cửa sổ sập: HYB US500 dùng M15 của bộ gốc, tay XAU dùng M5 parquet, cùng ngày bắt đầu/kết thúc. tay US500 và lệnh phụ không có lệnh vì thiếu dữ liệu.
- Giới hạn: mỗi engine vẫn tự kiểm cháy và ký quỹ trên 10k riêng của nó. Không hệ nào tự cháy trong các kịch bản dưới đây, nên phép cộng là đúng.

**Tóm tắt 11 kịch bản:**

| Danh mục | Gốc Jun–Nov: lãi / DD | Sống 11 (10k) | Sống 11 (30k) | DD tệ nhất | Vốn chung thấp nhất |
|---|---|---:|---:|---|---:|
| HYB US500 + tay US500 | +2.159,72 / 4,73% | **11/11** | 11/11 | 4.522,50 (45,2%, grind −35%) | 5.487,04 |
| HYB US500 + tay US500 ×1,5/×0,5 | +2.422,29 / 4,61% | **11/11** | 11/11 | 4.522,50 (45,2%) | 5.487,04 |
| HYB US500 + tay US500 + lệnh phụ | +2.856,74 / 4,59% | **11/11** | 11/11 | 4.522,50 (45,2%) | 5.487,04 |
| HYB US500 + tay ×1,5/×0,5 + lệnh phụ | +3.119,31 (311.931 USC) / 4,59% | **11/11** | 11/11 | 4.522,50 (45,2%) | 5.487,04 |
| HYB US500 + tay US500 + tay XAU 11/11 | +18.089,72 / 27,45% | 8/11 | **11/11** | 11.402,30 (114,0% / 38,0% của 30k) | 753,92 |
| HYB US500 + tay ×1,5/×0,5 + lệnh phụ + tay XAU 11/11 | +19.049,31 / 27,45% | 8/11 | **11/11** | 11.402,30 | 753,92 |

**Lõi US500, từng kịch bản (danh mục HYB + tay ×1,5/×0,5 + lệnh phụ, vốn chung):**

| Kịch bản | Lãi chung | DD chung | Chi tiết |
|---|---:|---|---|
| gap −10% (11/06 07:18 giờ VN, đáy HYB) | −774,97 | 19,94% | HYB −2.089,48 / tay +703,69 / lệnh phụ +610,82 |
| gap −20% | −1.565,96 | 31,65% | — |
| grind −20%/60 ngày | +546,26 | 27,18% | — |
| grind −35%/120 ngày | +740,25 | 45,22% | — |
| Covid | −2.439,20 | 41,40% | — |
| 08-10/2023 | −1.710,72 | 33,70% | — |

Các cửa sổ sập khác có DD 16,7–24,7%. tay US500 và lệnh phụ đều dương trong mọi kịch bản tổng hợp nên kéo DD chung xuống, nhưng không làm DD tệ nhất (grind −35%, do HYB) đổi.

**Thêm tay XAU 11/11, 3 kịch bản vượt 80% của 10k:**

| Kịch bản | Lãi chung | DD chung | Riêng tay XAU |
|---|---:|---|---|
| gap US500 −20% / vàng **+20%** (18/06 00:33 giờ VN, đáy vốn chung) | +4.994,60 | 11.402,30 (114,0%) | DD 11.765,26 |
| gap US500 −10% / vàng +10% | +5.744,41 | 9.092,03 (90,9%) | DD 9.297,13 |
| Covid (cùng cửa sổ) | +309,52 | 8.682,63 (86,8%) | lãi +2.754,73 |

- Riêng gap vàng tăng: tay XAU 11/11 **tự nó vượt 80%**. Bộ 11 stress của worker vàng chỉ thử gap giảm, nên chưa bắt được kịch bản này.
- Với 30k (tính nạp thêm) thì 11/11 đều sống, tệ nhất 38,0%. Equity chung chưa lần nào ≤ 0; thấp nhất 753,92 USD.
- Kịch bản gap vàng −g (cùng chiều US500) nhẹ hơn vàng +g ở cùng mốc.

## Kết luận (chỉ số đo)

1. **tay_v2 US500 ×1,5/×0,5 đạt bước 1–6:** DSR 0,993; stress 4/4 tổng hợp và 11/11 tính cả cửa sổ trung tính. Đề xuất thay gốc ở mức **ứng viên mặc định**, chờ bóng xác nhận. Không đổi luật live.
2. **Danh mục lõi chung vốn** = HYB+AG US500 + tay_v2 US500 ×1,5/×0,5 + lệnh phụ US500:
   - +3.119,31 USD, DD 4,59%.
   - Stress chung vốn 11/11 trên 10k, DD tệ nhất 45,22%.
   - Lệnh phụ vẫn chỉ là ứng viên (DSR 0,58 ở vòng trước).
3. **Thêm tay XAU 11/11:** lãi gốc +18–19k, nhưng chỉ sống đủ 11/11 khi tính nạp thêm lên 30k. Trên 10k gãy 3/11, gồm 2 kịch bản gap vàng tăng mà chính tay XAU vượt 80%.
   - Đề nghị worker vàng thêm kịch bản **gap vàng +10%/+20%** vào bộ 11 stress của họ.
