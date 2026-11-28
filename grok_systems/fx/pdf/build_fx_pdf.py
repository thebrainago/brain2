# -*- coding: utf-8 -*-
from pathlib import Path
from weasyprint import HTML

OUT=Path('/workspace/bt_3m/fx/pdf')
DEJ=Path('/usr/share/fonts/truetype/dejavu')
pdf=OUT/'TomTat_NghienCuu_FX_2026-11-28.pdf'

html=f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>Tóm tắt nghiên cứu cặp tiền và tài sản khác — 28/11/2026</title>
<style>
@font-face {{
  font-family: "DejaVu Sans";
  src: url("file://{DEJ}/DejaVuSans.ttf") format("truetype");
}}
@font-face {{
  font-family: "DejaVu Sans";
  src: url("file://{DEJ}/DejaVuSans-Bold.ttf") format("truetype");
  font-weight: 700;
}}
@page {{
  size: A4;
  margin: 11mm 12mm 14mm 12mm;
  @bottom-center {{
    content: "Tóm tắt nghiên cứu FX & tài sản khác  ·  28/11/2026  ·  trang " counter(page);
    font-size: 8pt; color: #555; font-family: "DejaVu Sans";
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: "DejaVu Sans", sans-serif;
  font-size: 9.6pt;
  line-height: 1.42;
  color: #1a1a1a;
}}
h1 {{ font-size: 16.5pt; margin: 0 0 4px; color: #123; }}
h2 {{ font-size: 12.2pt; margin: 11px 0 5px; color: #1f4e79; page-break-after: avoid; }}
p {{ margin: 0 0 6px; }}
ul {{ margin: 0 0 7px 16px; padding: 0; }}
li {{ margin: 0 0 2px; }}
.sub {{ color: #444; font-size: 9.1pt; margin-bottom: 8px; }}
.box, .warn, .ok {{
  border-radius: 6px; padding: 7px 10px; margin: 6px 0 8px;
}}
.box {{ background: #f4f7fb; border: 1px solid #c9d6e8; }}
.warn {{ background: #fff4f0; border: 1px solid #e8b4a8; }}
.ok {{ background: #f1f8f2; border: 1px solid #b7d5b9; }}
table {{
  width: 100%; border-collapse: collapse; margin: 4px 0 8px;
  font-size: 8.0pt;
}}
th, td {{
  border: 1px solid #ccd; padding: 2.5px 4.5px; text-align: left; vertical-align: top;
}}
th {{ background: #1f4e79; color: #fff; font-weight: 700; }}
td.n, th.n {{ text-align: right; white-space: nowrap; }}
tr:nth-child(even) td {{ background: #f6f8fb; }}
.keep {{ break-inside: avoid; page-break-inside: avoid; }}
tr {{ break-inside: avoid; page-break-inside: avoid; }}
.muted {{ color: #555; font-size: 8.1pt; }}
.k {{ font-weight: 700; }}
</style>
</head>
<body>

<h1>Tóm tắt nghiên cứu cặp tiền và tài sản khác</h1>
<p class="sub">28/11/2026 (giờ VN, UTC+7) · XSD-20 · Vốn tham chiếu 100.000 USD và tài khoản 100 USD cent · Mọi số trong tài liệu này là mô phỏng Python (engine2, bảo thủ), cửa sổ trong mẫu 02/06/2025–31/05/2026, ngoài mẫu 01/06–27/11/2026, lot 1,0 chuẩn — trừ khi ghi rõ MT5. <b>Kết quả MT5 100% tick: KHÔNG CÓ.</b> Không phải lời khuyên đầu tư, không phải kết quả live, không mở lệnh.</p>

<div class="warn keep">
<p><span class="k">Kết luận ngắn.</span> Không tìm thấy edge hồi quy đủ bền trên các cặp FX (kể cả nhóm AUD) để thêm vào sổ Vàng/SP500. Scalp chết vì phí spread. Tín hiệu giỏ thật không tốt hơn bản giả (placebo) khi xét cả họ. <span class="k">Không đưa hệ nào vào sổ khi chưa có xác nhận MT5.</span></p>
<ul>
<li><span class="k">Loại:</span> EURAUD (hỏng spread ×2), OIL (placebo 85%).</li>
<li><span class="k">Yếu / không đề xuất:</span> NZDJPY (lãi ngoài mẫu mất khi spread ×2); US100 = NAS100 (anh đã tắt cảnh báo, tương quan sổ +0,26).</li>
<li><span class="k">Ứng viên giấy (pin Python đạt, chờ MT5):</span> US30 và GER40. Nếu MT5 khớp, ước lượng Python khi gắn vào sổ Cân bằng 100k (lot để DD riêng = 5% vốn) là khoảng +15.400 USD / 6 tháng mỗi hệ, DD gộp không tăng hoặc tăng rất ít. Tài khoản 100 USD cent chỉ khoảng +15 USD / 6 tháng mỗi hệ.</li>
</ul>
</div>

<h2>1. Dữ liệu và cách làm</h2>
<p>Giá M1 BID + spread từng nến từ MT5 XM Ultra Low (slot p6, symbol có dấu <span class="k">#</span>), khoảng 18 tháng. Đã tải 15 cặp FX và 8 CFD (vàng bạc, dầu, US100, US30, JP225, Brent, GER40, UK100). Chưa tải một số cross (USDJPY, GBPJPY…). Order-flow CME Sierra chỉ thanh khoản khoảng 9 tuần (hợp đồng Z6 từ ~14/09/2026) — chỉ thăm dò. Không chạy syncTicks Fxaurum.</p>
<p>Họ tín hiệu: z-score, RSI2, IBS, Asia-range fade, họ dài hạn H4/D1 (<span class="mono">L_*</span>), phần dư cặp AUD–NZD. Quản lý: scalp SL/TP theo ATR-H1, hoặc giỏ DCA (bước nhồi, TP, tối đa 3/5 lớp) + flatten thứ Sáu ≥21:00 giờ máy chủ (Athens). Chi phí: spread từng nến + 0,5 trượt; có trừ swap (kể cả khi swap_mode=0). Chọn trên trong mẫu (lãi &gt; 0 và lãi/DD ≥ 3), chỉ kiểm trên ngoài mẫu (lãi &gt; 0 và lãi/DD ≥ 1). Pin: spread ×2/×3, trễ 2 nến, bỏ swap, khử/đảo xu hướng, chỉ mua / chỉ bán, shock gap 5%, placebo 40 seed.</p>

<h2>2. Kết quả sàng lọc</h2>
<p><span class="k">Scalp</span> (27.977 cấu hình, 23 mã): trung vị ngoài mẫu −0,30 ATR. Chọn theo trong mẫu: 7 cấu hình → chỉ 1 còn dương ngoài mẫu. Spreads FX ≈ 0,5 ATR-M5 — scalp hồi quy chết vì phí.</p>
<table class="keep">
<thead><tr><th>Bộ tín hiệu giỏ DCA</th><th class="n">Cấu hình</th><th class="n">Qua chọn trong mẫu</th><th class="n">Qua ngoài mẫu</th></tr></thead>
<tbody>
<tr><td>Thật (fade)</td><td class="n">39.915</td><td class="n">177</td><td class="n"><b>47</b></td></tr>
<tr><td>Placebo (hướng ngẫu nhiên, cùng thời điểm)</td><td class="n">39.995</td><td class="n">287</td><td class="n"><b>57</b></td></tr>
<tr><td>Gương (theo đà)</td><td class="n">39.999</td><td class="n">281</td><td class="n">49</td></tr>
</tbody>
</table>
<p>Cả họ, tín hiệu thật <span class="k">không tốt hơn ngẫu nhiên</span> (47 so với 57 và 49). Tỉ lệ dương cả hai cửa sổ: AUD 6,5%; NZD 2,2%; FX khác 9,0%; CFD 18,6% (placebo/gương cũng ra nhiều). <span class="k">AUD không đặc biệt hơn nhóm khác.</span></p>

<h2>3. Ứng viên và pin kiểm (giỏ, 1 lot, USD, Python)</h2>
<table class="keep">
<thead>
<tr><th>Hệ</th><th class="n">Ngoài mẫu / DD</th><th class="n">Placebo</th><th class="n">Spread ×2 (ngoài mẫu)</th><th>Kết luận</th></tr>
</thead>
<tbody>
<tr><td>NZDJPY IBS 240, London, gap 1, TP 2, N3</td><td class="n">+3.000 / 2.088</td><td class="n">97,5%</td><td class="n">−934</td><td>Yếu — lãi mất khi spread ×2. Không đưa vào sổ.</td></tr>
<tr><td>EURAUD z240, NY, gap 2, TP 1, N3</td><td class="n">+2.282 / 1.778</td><td class="n">90%</td><td class="n">−1.915</td><td><b>Loại.</b></td></tr>
<tr><td>OIL RSI2 1440, mọi phiên, gap 2, TP 1, N3</td><td class="n">+768 / 236</td><td class="n">85%</td><td class="n">+765</td><td><b>Loại</b> (placebo &lt; 95%).</td></tr>
<tr><td>US100 RSI2 1440 (NAS100), gap 1, TP 2, N3</td><td class="n">+1.762 / 603</td><td class="n">95%</td><td class="n">+1.762</td><td>Không đề xuất — NAS100 đã tắt cảnh báo, corr sổ +0,26.</td></tr>
<tr><td>US30 z240, NY, gap 1, TP 4, N5</td><td class="n">+7.053 / 2.286</td><td class="n">100%</td><td class="n">+7.291</td><td>Pin đạt (×3 vẫn +7.189; hai chiều dương). Chờ MT5. 26 giỏ / 14 thắng.</td></tr>
<tr><td>GER40 z15, phiên Á, gap 1, TP 1, N5</td><td class="n">+1.687 / 545</td><td class="n">100%</td><td class="n">+1.231</td><td>Pin đạt (×3 ngoài mẫu còn +414; trễ/khử xu hướng/hai chiều đều dương). Gap 5% đẩy DD cả kỳ lên ~7,3–7,9k. Phiên Á thanh khoản mỏng. Chờ MT5.</td></tr>
</tbody>
</table>
<p class="muted">JP225, Brent, UK100, Silver: không có ứng viên thật qua cửa chọn. Biến thể GER40 z5 hỏng spread ×3 — không dùng.</p>

<h2>4. Order-flow CME (thăm dò, ~9 tuần)</h2>
<p>90 phép thử (6A, 6E, 6B, 6C, SI). 6A/6E không có tín hiệu. <span class="k">6C→USDCAD</span> IC −0,029 (7/18) và <span class="k">SI→Silver</span> IC −0,036 (12/18, t tới −4,0): dòng lệnh lớn có xu hướng đảo sau 15–60 phút. Lãi gộp fade z&gt;2 khoảng 0,2–1,5 pip FX / 0,032 USD Silver — <span class="k">dưới spread</span>. Có tín hiệu thống kê nhưng chưa đủ lập hệ.</p>

<h2>5. Tác động lên sổ (Python, chưa có MT5)</h2>
<p>Sổ gốc là kịch bản <span class="k">Cân bằng</span> đã chốt (vốn 100k, số MT5 100% tick): ghép Vàng+SP500 +161.631, DD 6,8%; chỉ SP500 +81.769, DD 9,4%. US30/GER40 được ghép bằng đường vốn Python (cùng cửa sổ ngoài mẫu), lot chỉnh để DD riêng của hệ thêm = 5% của 100k (5.000 USD). Đây là ước lượng, không phải xác nhận live.</p>
<table class="keep">
<thead>
<tr><th>Thêm vào</th><th>Sổ</th><th class="n">Corr ngày</th><th class="n">Lot 5%</th><th class="n">Lãi thêm 6 tháng</th><th class="n">DD sổ gộp</th></tr>
</thead>
<tbody>
<tr><td>US30</td><td>Ghép 100k Cân bằng</td><td class="n">+0,05</td><td class="n">2,19</td><td class="n">+15.427</td><td class="n">6,8% → 6,2%</td></tr>
<tr><td>GER40</td><td>Ghép 100k Cân bằng</td><td class="n">+0,01</td><td class="n">9,17</td><td class="n">+15.470</td><td class="n">6,8% → 6,8%</td></tr>
<tr><td>Cả hai (mỗi hệ lot 5%)</td><td>Ghép 100k Cân bằng</td><td class="n">—</td><td class="n">2,19 + 9,17</td><td class="n">+30.897</td><td class="n">6,8% → 6,3%</td></tr>
<tr><td>US30</td><td>Chỉ SP500 Cân bằng</td><td class="n">−0,07</td><td class="n">2,19</td><td class="n">+15.427</td><td class="n">9,4% → 9,4%</td></tr>
<tr><td>GER40</td><td>Chỉ SP500 Cân bằng</td><td class="n">+0,02</td><td class="n">9,17</td><td class="n">+15.470</td><td class="n">9,4% → 10,0%</td></tr>
<tr><td>Cả hai (mỗi hệ lot 5%)</td><td>Chỉ SP500 Cân bằng</td><td class="n">—</td><td class="n">2,19 + 9,17</td><td class="n">+30.897</td><td class="n">9,4% → 10,9%</td></tr>
</tbody>
</table>
<p>Tài khoản <span class="k">100 USD cent (sách SP500)</span>: để DD riêng ≈ 5 USD cần khoảng 0,0022 lot chuẩn US30 hoặc 0,0092 lot chuẩn GER40, lãi ước lượng khoảng <span class="k">+15 USD / 6 tháng</span> mỗi hệ. <span class="k">Cỡ hợp đồng Exness US30c / GER40c: KHÔNG CÓ</span> (file symbols_xm.csv là tài khoản XM Ultra Low: 1 lot US30Cash#/GER40Cash# ≈ 1 USD/điểm, lot tối thiểu 0,10 — lớn hơn lot 5 USD ở trên). Số cent chỉ là phép quy đổi theo lot chuẩn XM, không phải lệnh Exness.</p>
<p class="muted">NZDJPY nếu gắn sổ 100k proxy trước đó: corr +0,20, +7.312 / 6 tháng, DD 6,0% → 6,9%; cent khoảng +7 USD. Không khuyến nghị vì pin spread ×2 thất bại.</p>

<div class="box keep">
<p><span class="k">Việc còn dang dở — MT5 100% tick.</span> Python kỳ vọng ngoài mẫu, 1 lot: NZDJPY +3.000 / DD 2.088; US30 +7.053 / DD 2.286; GER40 +1.687 / DD 545. Hàng đợi đã soạn (<span class="mono">q_p6_fx2.json</span>), đã sửa khung ATR thành PERIOD_H1, đã tải tick 06–11/2026 vào slot p6. Các lượt chạy sớm ra 0 lệnh hoặc bị treo; <span class="k">số MT5 hiện tại: KHÔNG CÓ.</span> Chỉ thêm vào sổ nếu sau này MT5 cùng dấu, lãi lệch không quá khoảng 30%, DD không xấu hơn nhiều, và pin đã đạt (NZDJPY đã trượt điều kiện này).</p>
<p>Chi tiết đầy đủ: <span class="mono">README_FX.md</span>, git nhánh <span class="mono">grok/scenarios-v3</span> thư mục <span class="mono">grok_systems/fx/</span>. Máy nhà: <span class="mono">E:\\GrokWork\\bt_fx</span> (và bản staging <span class="mono">C:\\Users\\DUNG\\v3work\\out\\bt_fx</span>).</p>
</div>

</body>
</html>
'''
HTML(string=html, base_url=str(OUT)).write_pdf(pdf)
print('WROTE', pdf, 'bytes', pdf.stat().st_size)
