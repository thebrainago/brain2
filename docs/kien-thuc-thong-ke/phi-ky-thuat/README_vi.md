# Kiểm định các hệ “phi kỹ thuật” trên vàng và S&P 500

Cập nhật: 2026-11-15 07:14 (Asia/Saigon, UTC+7)

Thư mục này thu **kết quả 7 vòng kiểm định** do module Gann SQ9 Research tự chạy trên vàng (GC=F) và S&P 500 (ES=F, ^GSPC, SPY). Mục tiêu: tìm hệ / chiến lược nào có edge thật, sau khi khớp giá thật, trừ phí, chia mẫu trong/ngoài và so với đối chứng.

Mã nguồn, script tải dữ liệu và CSV kết quả nhỏ nằm ở [`tools/kiem_dinh/gann_sq9/`](../../../tools/kiem_dinh/gann_sq9/). Catalog các quy tắc đã thử: [`items.json`](items.json) (cùng schema với kho kiến thức thống kê của nhánh `evo/thong-ke-kien-thuc`).

## Không phải gì

- Không phải danh sách hệ đã “pass” chuẩn kiểm định chung. **Chỉ pass khi nửa ngoài mẫu (OOS) đơn độc vẫn qua FDR (q < 0,05).** Theo chuẩn này, không hệ nào trong 7 vòng đạt. Ứng viên tốt nhất (IBS < 0,2 trên ES) chỉ qua FDR khi **gộp hai nửa** (q = 0,038); riêng OOS thì q = 0,53 — vì thế được gắn **ứng viên**, không phải pass.
- Không commit chuỗi giá thô (Yahoo `.pkl`), `.npy`, `.venv`, hay `tai_khoan.json`.
- Không khẳng định edge sẽ còn mãi: IBS/Connors là hiệu ứng đã công bố, có thể yếu dần.

## Phương pháp (dùng thống nhất 7 vòng)

- **Khớp lệnh:** tín hiệu tính tại close nến t (chỉ dùng dữ liệu ≤ t), khớp tại **giá mở cửa THẬT của nến t+1**. Không khớp tại giá Heikin Ashi, giá gạch Renko hay giá trung bình.
- **Phí:** mỗi lượt mua+bán trả 1 spread: vàng 0,3; ES 0,25; ^GSPC 0,5; SPY 0,02 điểm. Một số phép thử thêm phí ×4.
- **Chia mẫu:** nến ngày tách IS trước 2016 / OOS từ 2016. Intraday chia đôi theo thời gian. Dữ liệu 1h Yahoo chỉ khoảng 2,4 năm; 15m/5m chỉ khoảng 60 ngày (tham khảo).
- **Đối chứng:** góc/thang lệch pha (±22,5°), thang đều % hoặc cùng khoảng cách ATR, neo ngẫu nhiên, hoán vị thời gian, Buy & Hold, Donchian/EMA (trend-following đơn giản), và (vòng 7) dịch vòng chuỗi vị thế để giữ cùng độ phơi nhiễm.
- **Nhiều phép thử:** FDR Benjamini–Hochberg; một số vòng thêm Bonferroni.
- **Dữ liệu:** Yahoo Finance, tải 14/11/2026, tới phiên 13/11/2026. GC=F dùng từ 2008 (trước đó nhiều nến High=Low bị hỏng). ES=F là hợp đồng gần nhất, không điều chỉnh roll. ^GSPC Open trước ~2014 trên Yahoo thường trùng Close hôm trước — overnight và khớp open của ^GSPC được kiểm tra chéo bằng SPY.

## Bảy vòng

| Vòng | Câu hỏi | Báo cáo |
| --- | --- | --- |
| 1 | Mức Gann Square of 9 từ neo thường (đóng cửa ngày trước, mở phiên, swing) có hơn góc ngẫu nhiên cùng khoảng cách? | [KET_QUA_vi.md](KET_QUA_vi.md) |
| 2 | Sq9 giá từ đỉnh/đáy lớn, và Sq9 thời gian, có edge ngoài mẫu? | [KET_QUA_2_vi.md](KET_QUA_2_vi.md) |
| 3 | Sau khi phá A, xác suất đi tiếp B/C/D của bậc Sq9 có hơn thang đều % / dời pha / vô điều kiện? | [KET_QUA_3_vi.md](KET_QUA_3_vi.md) |
| 4 | Sau cú sập (tăng) mạnh, neo đáy (đỉnh), mục tiêu Sq9/Fib nào hay chạm, và scalp nào dương ở OOS? | [KET_QUA_4_vi.md](KET_QUA_4_vi.md) |
| 5 | Mở phiên xong, giá hay đi về đích nào (PDC/PDH/PDL, số tròn, ATR, Sq9)? Scalp theo mốc phiên có lãi sau phí? | [KET_QUA_5_vi.md](KET_QUA_5_vi.md) |
| 6 | Fibo xoắn ốc, và chiến lược trên Heikin Ashi / Renko / Point & Figure / Three Line Break / Kagi, có edge khi khớp giá thật? | [KET_QUA_6_vi.md](KET_QUA_6_vi.md) |
| 7 | Trend-following, hồi về trung bình ngắn hạn, hiệu ứng lịch/thời gian, biến động và ngày tin (FOMC, CPI, NFP) — hướng nào tốt nhất? | [KET_QUA_7_vi.md](KET_QUA_7_vi.md) |

## Bảng kết luận theo hệ

Chuẩn chung: **pass** chỉ khi OOS đơn độc qua FDR (q < 0,05). Cột “Kết luận” dùng: không đạt / ứng viên / không có edge (mô tả, không giao dịch).

| Hệ | Kết luận | Số liệu then chốt (lấy từ báo cáo, không ước đoán) |
| --- | --- | --- |
| Gann Sq9 — mức giá (neo thường) | Không có edge | Touch/hold/rev gần như trùng đối chứng góc lệch ±22,5°. 192 phép so, 1 phép z>1,96 (ít hơn dương tính giả kỳ vọng). |
| Gann Sq9 — mức giá (neo đỉnh/đáy lớn) | Không có edge | Hiệu so với góc lệch < 2 điểm; 0 phép qua FDR. Khác biệt vs neo ngẫu nhiên đổi dấu IS/OOS. |
| Gann Sq9 — thời gian | Không có edge | 0/144 phép qua FDR và Bonferroni. Hợp lưu giá+thời gian không hơn mức lệch. |
| Gann Sq9 — xác suất đi tiếp A→B/C/D | Không có edge | Vs thang đều %: hiệu TB 0,0 điểm. Vs dời pha: hơi kém (−0,7 điểm), do có mức ngay tại giá neo, không do góc Gann. Phá mức không hơn vô điều kiện (hiệu TB −1,0 điểm). |
| Fibonacci (mục tiêu sau cú sập) | Không có edge | Fib vs đường cong khoảng cách: hiệu −0,3 điểm; 1/1135 phép qua FDR theo hướng Fib tốt hơn. Chỉ khoảng cách quyết định tỷ lệ chạm. |
| Scalp Sq9/Fib sau cú sập | Không đạt | 32 382 combo. Lệnh hồi ≈ 0R sau spread. Lệnh đi tiếp IS +0,14R / OOS +0,05R, **góc lệch ngẫu nhiên cho y hệt**. 0 combo top-IS còn ý nghĩa ở OOS sau Bonferroni. |
| Fibo xoắn ốc (chạm đường / mốc thời gian) | Không có edge | 0/432 lát cắt qua FDR. φ bằng hệ số tăng trưởng ngẫu nhiên. |
| Heikin Ashi | Không có edge | Khớp giá thật: Sharpe quanh 0. **Khớp ảo (giá HA)** thổi phồng rất mạnh: ví dụ HA đổi màu ES 1h, Sharpe ảo 10,8 / PF 3,1 so với thật −0,6 / 0,93. |
| Renko | Không có edge | 0 cấu hình chọn từ IS thắng bootstrap ở OOS. Khớp ảo thổi Sharpe khoảng +0,4 đến +2,4. |
| Point & Figure | Không có edge | Double top/bottom ngang Donchian. Triple và catapult quá ít lệnh (thường 3–27). |
| Three Line Break | Không có edge | Không hơn đối chứng trend-following. |
| Kagi (yin/yang) | Không có edge (yếu) | Đảo 3 ATR chỉ Long gần như cầm dài hạn (≈ Buy & Hold). Vàng 1h OOS Sharpe 1,54 nhưng p bootstrap = 0,19. |
| Bản đồ xác suất mốc phiên | Không có edge (chỉ mô tả khoảng cách) | Nhiều đích chạm 85–94% và ổn định, nhưng 0/207 phép hơn đường cong khoảng cách sau FDR. 138 tổ hợp scalp: 0 dương cả IS lẫn OOS, 0 qua FDR. |
| Trend / momentum (Donchian, EMA, SMA, TSMOM) | Không đạt (hữu ích như lọc rủi ro) | 81/102 cấu hình dương cả 2 nửa, nhưng không thắng ngẫu nhiên cùng phơi nhiễm (p OOS ≥ 0,06) và không thắng B&H về Sharpe OOS. ES C>SMA200: MaxDD OOS 18,7% so với B&H 34,5%. |
| Hồi về trung bình — IBS < 0,2 trên ES (Long, giữ 1 phiên, khớp open) | **Ứng viên, không phải pass** | IS Sharpe 0,60 / OOS 0,88; PF 1,40 / 1,70; 609 / 361 lệnh; MaxDD 24,6% / 17,9%; CAGR 5,8% / 8,0%. q gộp = 0,038, **q OOS đơn độc = 0,53**. Lặp lại trên ^GSPC và SPY. Không áp dụng cho vàng. Phải vào sát close Mỹ (mở 9:30 hôm sau làm Sharpe OOS của SPY còn 0,59, mất ý nghĩa). |
| Hiệu ứng lịch (turn-of-month, thứ trong tuần, pre-holiday, giờ/phiên vàng) | Không đạt | Turn-of-month dương nhẹ, không có ý nghĩa thống kê. Giờ/phiên vàng đổi dấu giữa 2 nửa (London IS 2,29 → OOS −0,23). |
| Overnight S&P | Không đạt (có thật nhưng phí ăn) | SPY trước phí: IS 0,54 / OOS 0,86. Sau 1 spread/ngày: IS 0,03 / OOS 0,72. Không đạt ở nửa IS. |
| Drift ngày FOMC | Không đạt (suy giảm) | IS Sharpe 0,67–0,73 (p 0,001–0,002), OOS 0,03–0,07. |
| CPI / NFP, NR7, inside bar | Không đạt | Đổi dấu hoặc không lặp lại trên sản phẩm giao dịch được (ES). |

**Không có gì thắng trend-following đơn giản một cách có ý nghĩa ở OOS.** Ở vòng 6, 0/65 cấu hình chart phi chuẩn (chọn tốt nhất IS) có p bootstrap OOS < 0,05.

## Ứng viên duy nhất và chuẩn chung

IBS = (Close − Low) / (High − Low) của nến ngày. Khi IBS < 0,2: mua ở open phiên kế tiếp; giữ 1 phiên, nếu hôm sau IBS vẫn < 0,2 thì giữ tiếp. Số liệu đã trừ phí, khớp open nến sau, ES=F, 2000–2015 / 2016–11/2026: xem bảng trên và [KET_QUA_7_vi.md](KET_QUA_7_vi.md).

Nếu chỉ xét “dương cả hai nửa và qua FDR khi gộp”, IBS trông như có edge yếu–vừa. **Theo chuẩn chung đã thống nhất với module kiến thức thống kê (chỉ pass khi OOS đơn độc qua FDR), đây là ứng viên, không phải pass.** Edge phụ thuộc chế độ (Sharpe 2015–19 ≈ 0,30; mạnh hơn khi VIX > 20), không thay thế Buy & Hold về CAGR, và phải vào lệnh sát giờ đóng cửa Mỹ.

Pine: `tools/kiem_dinh/gann_sq9/pine/best_strategy_r7.pine` (có bộ lọc tùy chọn VIX > 20 và SMA200; chưa compile-check trên TradingView trong lượt đóng gói này).

## File trong thư mục này

| File | Nội dung |
| --- | --- |
| [items.json](items.json) | Một mục cho mỗi hệ/quy tắc đã thử, schema thống nhất (rule, market, sample, result, …). Số liệu chỉ lấy từ báo cáo/CSV; thiếu thì để `null`. |
| [KET_QUA_vi.md](KET_QUA_vi.md) … [KET_QUA_7_vi.md](KET_QUA_7_vi.md) | Báo cáo đầy đủ từng vòng. |

## File đã cố ý không đưa lên git

- Mọi `data_*.pkl`, `results*/**/*.pkl`, `*.npy`, `levels.csv.gz` (dữ liệu thô / quá lớn; tải lại bằng `download_data.py`).
- `results3/tests.csv` (~2,0 MB) và `results4/scalp_all.csv` (~2,4 MB) — vượt ngưỡng ~1 MB/file.
- `.venv/`, `__pycache__/`, log chạy, `gann_sq9_indicator.pine` (bản gốc đã lỗi; dùng bản `_fixed`).
- Không có `tai_khoan.json` hay bí mật trong module này.
