# -*- coding: utf-8 -*-
from pathlib import Path
from weasyprint import HTML

FIG=Path('/workspace/bt_3m/v3/pdf/fig')
OUT=Path('/workspace/bt_3m/v3/pdf')
DEJ=Path('/usr/share/fonts/truetype/dejavu')

def img(name, cls='fig'):
    return f'<img class="{cls}" src="{FIG/name}"/>'

html=f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>Tóm tắt kịch bản vàng và SP500 — 28/11/2026</title>
<style>
@font-face {{
  font-family: "DejaVu Sans";
  src: url("file://{DEJ}/DejaVuSans.ttf") format("truetype");
  font-weight: 400;
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
    content: "Tóm tắt kịch bản Vàng & SP500  ·  28/11/2026  ·  trang " counter(page);
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
h1 {{ font-size: 17.5pt; margin: 0 0 4px; color: #123; }}
h2 {{ font-size: 12.8pt; margin: 13px 0 5px; color: #1f4e79; page-break-after: avoid; }}
h3 {{ font-size: 11pt; margin: 10px 0 4px; color: #1f4e79; page-break-after: avoid; }}
p {{ margin: 0 0 6px; }}
ul, ol {{ margin: 0 0 7px 16px; padding: 0; }}
li {{ margin: 0 0 2px; }}
.sub {{ color: #444; font-size: 9.2pt; margin-bottom: 9px; }}
.box, .warn, .ok {{
  border-radius: 6px; padding: 7px 10px; margin: 7px 0 9px;
}}
.box {{ background: #f4f7fb; border: 1px solid #c9d6e8; }}
.warn {{ background: #fff4f0; border: 1px solid #e8b4a8; }}
.ok {{ background: #f1f8f2; border: 1px solid #b7d5b9; }}
table {{
  width: 100%; border-collapse: collapse; margin: 5px 0 9px;
  font-size: 8.2pt;
}}
th, td {{
  border: 1px solid #ccd; padding: 3px 4.5px; text-align: left; vertical-align: top;
}}
th {{ background: #1f4e79; color: #fff; font-weight: 700; }}
td.n, th.n {{ text-align: right; white-space: nowrap; }}
tr:nth-child(even) td {{ background: #f6f8fb; }}
img.fig {{ width: 100%; height: auto; max-height: 58mm; object-fit: contain; object-position: center top; margin: 2px 0 5px; display: block; }}
img.hero {{ width: 100%; height: 50mm; object-fit: contain; object-position: center top; margin: 4px 0 2px; display: block; }}
th, td {{ padding: 2.5px 4.5px; }}

td.s, th.s {{ white-space: nowrap; }}
.keep {{ break-inside: avoid; page-break-inside: avoid; }}
thead, tbody {{ break-inside: auto; }}
tr {{ break-inside: avoid; page-break-inside: avoid; }}
.muted {{ color: #555; font-size: 8.2pt; }}
.k {{ font-weight: 700; }}
code, .mono {{ font-family: "DejaVu Sans", sans-serif; font-size: 8.2pt; }}
small {{ font-size: 8pt; color: #444; }}
</style>
</head>
<body>

<h1>Tóm tắt kịch bản giao dịch Vàng và SP500</h1>
<p class="sub">28/11/2026 (giờ VN, UTC+7) · Vốn tham chiếu 100.000 USD · Số liệu MT5 100% real ticks, cửa sổ 01/06–27/11/2026 · Tài liệu bàn giao, không phải lời khuyên đầu tư, không phải kết quả live.</p>

<div class="ok">
<p><span class="k">Khuyến nghị chốt.</span> Chọn kịch bản <span class="k">Cân bằng</span> hoặc <span class="k">Mạnh tay ở lot gốc</span> (không nhân lot). Chạy <span class="k">demo nửa lot</span> trên XM/Exness trước khi tăng. Cùng vốn 100k, <span class="k">ghép vàng và SP500 lãi nhiều hơn mà DD lại thấp hơn</span> so với đánh riêng từng tài sản, vì hai mã bù rủi ro cho nhau.</p>
<ul>
<li><span class="k">Cân bằng, ghép 2 tài sản, vốn 100k:</span> +161.631 USD, DD 6,8%, gap 5% ước tính 48%, spread ×2 thì DD khoảng 8,4%. Đây là lựa chọn em khuyên.</li>
<li><span class="k">Mạnh tay, lot gốc, cùng vốn:</span> +304.204 USD, DD 11,0%. Gap 5% trong phiên ước tính gần 99% vốn — chỉ dùng sau khi demo khớp.</li>
<li>Các bậc nhân lot (Mạnh tay ×1,4 / ×1,7, Đánh tay ×5) chỉ giữ DD dưới 20% trên dữ liệu cũ. Gặp gap 5% trong phiên có thể mất quá vốn.</li>
</ul>
</div>

<h2>1. Kết quả chính — vốn 100k, khóa hedge cuối tuần bật</h2>
<p>DD là DD gộp trên equity MT5 (ghép deals từng hệ, scale tuyến tính theo lot). Mọi kịch bản dưới đây lãi <span class="k">đủ 6/6 tháng</span>. Lot đã làm tròn bước sàn: vàng 0,01, chỉ số 0,1.</p>

<table>
<thead>
<tr><th class="s">Sách</th><th class="s">Kịch bản</th><th class="n">MT5 lãi 6 tháng</th><th class="n">DD gộp</th><th class="n">Nửa A / nửa B</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th></tr>
</thead>
<tbody>
<tr><td class="s">Ghép 2 mã (15 hệ)</td><td class="s">An toàn</td><td class="n">+96.123</td><td class="n">3,7%</td><td class="n">44,7k / 51,4k</td><td class="n">28,4%</td><td class="n">5,0%</td></tr>
<tr><td class="s">Ghép 2 mã</td><td class="s"><b>Cân bằng</b></td><td class="n"><b>+161.631</b></td><td class="n"><b>6,8%</b></td><td class="n">75,0k / 86,6k</td><td class="n">48,3%</td><td class="n">8,4%</td></tr>
<tr><td class="s">Ghép 2 mã</td><td class="s"><b>Mạnh tay</b></td><td class="n"><b>+304.204</b></td><td class="n"><b>11,0%</b></td><td class="n">139,3k / 164,9k</td><td class="n">98,8%</td><td class="n">16,9%</td></tr>
<tr><td class="s">Ghép 2 mã</td><td class="s">Mạnh tay ×1,7</td><td class="n">+517.672</td><td class="n">18,7%</td><td class="n">236,9k / 280,3k</td><td class="n">~168%</td><td class="n">~29%</td></tr>
<tr><td class="s">Ghép 2 mã</td><td class="s">Đánh tay (10 scalp)</td><td class="n">+72.846</td><td class="n">3,6%</td><td class="n">33,6k / 39,2k</td><td class="n">29,2%</td><td class="n">4,3%</td></tr>
<tr><td class="s">Ghép 2 mã</td><td class="s">Đánh tay ×5</td><td class="n">+364.231</td><td class="n">18,0%</td><td class="n">—</td><td class="n">~146%</td><td class="n">—</td></tr>
</tbody>
</table>
<p class="muted">Gap 5% và spread ×2 là mô phỏng Python (stress), không phải MT5. Nửa A = 01/06–19/08, nửa B = 20/08–27/11. Kết quả chỉ vàng / chỉ SP500 ở mục 4.</p>
{img('eq_joint100.png','hero')}
{img('mon_joint100.png')}

<h2>2. Các loại tín hiệu đã chốt</h2>
<p>Mọi tín hiệu lấy từ <span class="k">dòng lệnh (order-flow) Rithmic</span> trên nến 1 phút (GC = vàng COMEX, ES = S&amp;P mini), rồi khớp lệnh trên giá CFD XM (GOLD.i#, US500Cash). Không dùng indicator thông thường, không có dữ liệu GEX / gamma flip / NQ / SI / CL / MBO.</p>

<table>
<thead>
<tr><th>Loại</th><th>Ý nghĩa dễ hiểu</th><th>Hệ dùng</th></tr>
</thead>
<tbody>
<tr><td><b>Bắt ngược cú quét</b><br/>(sweep fade)</td><td>Giá quét qua đỉnh hoặc đáy nến 15 phút, nhưng dòng lệnh lệch mạnh ngược lại (z &gt; 1,8, thường kèm ADX &gt; 20) thì vào <b>ngược</b> chiều cú quét. Đây là tín hiệu chủ lực.</td><td>x1, u1, u7; một phần xs10, gp2, up1, up3</td></tr>
<tr><td><b>Delta và hấp thụ</b><br/>(fade hoặc thuận)</td><td>Delta (mua trừ bán) tăng giảm bất thường so với bình thường: đánh ngược hoặc thuận tùy hệ. Khi lệnh lớn đập vào mà giá không chạy (có bên đỡ) thì đánh ngược, thường chỉ phiên NY.</td><td>x4, g5, u2, u6, u15, u18, up2</td></tr>
<tr><td><b>Imbalance</b><br/>(lệch mua–bán)</td><td>Nhiều mức giá hoặc cửa sổ 15–30 phút bị lệch mua/bán mạnh (|z| lớn): fade hoặc thuận tùy hệ.</td><td>g7, xs4, u13, gp3</td></tr>
<tr><td><b>Phá biên / phá đỉnh–đáy / mốc tròn</b></td><td>Giá phá đỉnh hoặc đáy ngày/tuần, biên London, biên mở cửa NY, range phiên Á thất bại, hoặc mốc 50 điểm — có dòng lệnh xác nhận thì vào thuận hoặc fade tùy luật.</td><td>g1, g2, g3, u10, u11, u12, xs8, gp1</td></tr>
<tr><td><b>Lệnh lớn, volume climax, basis</b></td><td>Cá mập (lệnh lớn 30–60 phút), đỉnh volume tại biên, hoặc basis futures–CFD lệch rồi hồi.</td><td>xs2, xs3, xs6, xs9, xs5, u16, u17, u19</td></tr>
<tr><td><b>Scalp đồng pha</b><br/>(có SL/TP)</td><td>Hai tín hiệu xuất hiện gần nhau (trong khoảng 30 nến), vào <b>một lệnh</b> có cắt lỗ và chốt lời cố định theo USD/oz, giữ tối đa 30–90 nến. Dễ đánh tay nhất.</td><td>xs1–xs10</td></tr>
</tbody>
</table>
<p>Hai kiểu quản lý lệnh: <span class="k">giỏ (basket)</span> — nhồi DCA, không SL từng lệnh, chốt tổng theo giá, có khóa hedge cuối tuần; và <span class="k">scalp</span> — một lệnh, SL/TP/hold cố định, không khóa hedge (không có giỏ để khóa).</p>

<h2>3. Danh sách hệ đã pass (MT5 tick thật, lot kiểm chứng)</h2>
<p>Số MT5 dưới đây là tại <span class="k">lot kiểm chứng</span> (không phải lot trong danh mục 100k). Vốn đo: vàng 30k, SP500 10k. Đã loại: x2 (sụp khi trượt 1 điểm), g4, g6, x5, u14, vàng v2_c1 (trượt ngoài mẫu).</p>

<h3>3.1 Vàng (GOLD.i#)</h3>
<table>
<thead>
<tr><th>Mã</th><th>Tín hiệu (ngắn)</th><th class="n">Lot test</th><th class="n">MT5 lãi / DD</th><th>Ghi chú</th></tr>
</thead>
<tbody>
<tr><td>x1</td><td>Bắt ngược cú quét 15 phút</td><td class="n">0,09</td><td class="n">+16.732 / 14,2%</td><td>Chủ lực; có W: +14.215 / 14,5%</td></tr>
<tr><td>x4</td><td>Bắt ngược delta 15 phút</td><td class="n">0,04</td><td class="n">+4.600 / 14,9%</td><td>0,07 lot → DD 24,7%</td></tr>
<tr><td>g1</td><td>Phá đỉnh/đáy ngày + dòng lệnh</td><td class="n">0,12</td><td class="n">+10.184 / 10,9%</td><td>Cần vào nhanh (trễ 2 nến là lỗ)</td></tr>
<tr><td>g2</td><td>Phá biên London theo xu hướng</td><td class="n">0,12</td><td class="n">+10.426 / 8,5%</td><td></td></tr>
<tr><td>g3</td><td>Phá đỉnh/đáy tuần + dòng lệnh</td><td class="n">0,06</td><td class="n">+7.953 / 11,6%</td><td></td></tr>
<tr><td>g5</td><td>Bắt ngược hấp thụ-delta 15 phút</td><td class="n">0,04</td><td class="n">+7.751 / 10,0%</td><td>Cần vào nhanh</td></tr>
<tr><td>g7</td><td>Bắt ngược imbalance 30 phút</td><td class="n">0,04</td><td class="n">+7.544 / 8,9%</td><td></td></tr>
<tr><td>gp1</td><td>Cặp phá tuần + hồi EMA</td><td class="n">0,06</td><td class="n">+9.237 / 8,5%</td><td>Tập con, ít vào danh mục greedy</td></tr>
<tr><td>gp2</td><td>Cặp quét fade + delta fade</td><td class="n">0,06</td><td class="n">+7.479 / 11,4%</td><td>Có trong danh mục chỉ-vàng</td></tr>
<tr><td>gp3</td><td>Cặp delta fade + imbalance</td><td class="n">0,05</td><td class="n">+5.677 / 10,6%</td><td></td></tr>
<tr><td>xs1</td><td>Scalp: vàng chạy trước, fade lệnh lớn</td><td class="n">0,57</td><td class="n">+13.584 / 5,6%</td><td>SL≈8, TP 8, hold 90; ~116 lệnh</td></tr>
<tr><td>xs2</td><td>Scalp: cá mập 60 phút + hồi EMA, NY</td><td class="n">1,00</td><td class="n">+36.199 / 16,3%</td><td>SL≈8, TP 13, hold 90; ~115 lệnh</td></tr>
<tr><td>xs3</td><td>Scalp: fade lệnh lớn 30 phút</td><td class="n">0,30</td><td class="n">+21.046 / 6,8%</td><td>SL 13 / TP 8 / 90; 481 lệnh</td></tr>
<tr><td>xs4</td><td>Scalp: fade imbalance 15 phút</td><td class="n">0,30</td><td class="n">+9.735 / 7,9%</td><td>SL 8 / TP 10 / 90; 270 lệnh</td></tr>
<tr><td>xs5</td><td>Scalp: basis futures–CFD hồi</td><td class="n">0,30</td><td class="n">+7.019 / 3,8%</td><td>SL 8 / TP 6 / 90; 175 lệnh</td></tr>
<tr><td>xs6</td><td>Scalp: cá mập 60 phút, thuận, NY</td><td class="n">0,30</td><td class="n">+10.130 / 7,7%</td><td>SL 10 / TP 13 / 90; 95 lệnh, mẫu nhỏ</td></tr>
<tr><td>xs7</td><td>Scalp: phá đỉnh/đáy ngày thất bại</td><td class="n">0,30</td><td class="n">+5.875 / 4,6%</td><td>SL 8 / TP 18 / 30; 89 lệnh, mẫu nhỏ</td></tr>
<tr><td>xs8</td><td>Scalp: phá đỉnh ngày và tuần cùng lúc</td><td class="n">0,30</td><td class="n">+10.437 / 6,1%</td><td>SL 10 / TP 18 / 90; 86 lệnh</td></tr>
<tr><td>xs9</td><td>Scalp: cá mập 60 phút, hai thước đo</td><td class="n">0,30</td><td class="n">+11.815 / 11,0%</td><td>Chồng lấn xs6/xs2; 129 lệnh</td></tr>
<tr><td>xs10</td><td>Scalp: quét fade + cá mập</td><td class="n">0,30</td><td class="n">+10.140 / 6,9%</td><td>Vào danh mục greedy; 120 lệnh</td></tr>
</tbody>
</table>

<h3>3.2 SP500 (US500Cash)</h3>
<table>
<thead>
<tr><th>Mã</th><th>Tín hiệu (ngắn)</th><th class="n">Lot test</th><th class="n">MT5 lãi / DD</th><th>Ghi chú</th></tr>
</thead>
<tbody>
<tr><td>u1</td><td>Bắt ngược cú quét 15 phút</td><td class="n">3,8 / 1,0</td><td class="n">+5.409 / 13,7% · +1.313 / 4,2%</td><td>Chủ lực</td></tr>
<tr><td>u2</td><td>Fade hấp thụ, phiên NY</td><td class="n">0,30</td><td class="n">+493 / 3,2%</td><td>Nhỏ</td></tr>
<tr><td>u6</td><td>Theo đà delta 5 phút</td><td class="n">1,0 / 2,8</td><td class="n">+2.344 / 4,7% · +7.823 / 12,5%</td><td>Spread ×2 ở 2,8 lot → DD 59%: giới hạn ≤1,4 trên vốn 10k</td></tr>
<tr><td>u7</td><td>Bắt ngược cú quét, nhạy hơn</td><td class="n">3,0 / 1,6</td><td class="n">+7.092 / 16,3% · +3.732 / 10,0%</td><td></td></tr>
<tr><td>u10</td><td>Theo đà phá biên mở cửa NY</td><td class="n">2,5</td><td class="n">+3.721 / 12,5%</td><td>Có W: +2.986 / 13,1%</td></tr>
<tr><td>u11</td><td>Phá biên phiên Á thất bại</td><td class="n">2,0</td><td class="n">+2.043 / 14,7% (W)</td><td>2,5 lot → DD 18,4%</td></tr>
<tr><td>u12</td><td>Phá mốc tròn 50 điểm + dòng lệnh</td><td class="n">3,0</td><td class="n">+5.051 / 11,4%</td><td></td></tr>
<tr><td>u13</td><td>Theo đà imbalance 15 phút</td><td class="n">3,0</td><td class="n">+5.604 / 8,2%</td><td></td></tr>
<tr><td>u15</td><td>Fade lợi suất futures 5 phút</td><td class="n">1,5</td><td class="n">+2.649 / 11,9%</td><td></td></tr>
<tr><td>u16</td><td>Bắt ngược đỉnh volume</td><td class="n">1,0</td><td class="n">+1.818 / 8,7%</td><td></td></tr>
<tr><td>u17</td><td>Theo đà đỉnh volume, NY</td><td class="n">2,0</td><td class="n">+3.030 / 9,8%</td><td></td></tr>
<tr><td>u18</td><td>Fade lợi suất futures 30 phút</td><td class="n">1,5</td><td class="n">+1.879 / 12,4%</td><td></td></tr>
<tr><td>u19</td><td>Theo đà lệnh lớn 60 phút</td><td class="n">1,5</td><td class="n">+2.473 / 9,7%</td><td></td></tr>
<tr><td>up1</td><td>Cặp hai ngưỡng quét fade</td><td class="n">2,0</td><td class="n">+4.245 / 7,4%</td><td>Tập con u1/u7; vào danh mục chỉ-SP500</td></tr>
<tr><td>up2</td><td>Cặp đà delta + phá mốc 50</td><td class="n">2,0</td><td class="n">+2.921 / 6,4%</td><td>Tập con; vào danh mục chỉ-SP500</td></tr>
<tr><td>up3</td><td>Cặp quét fade + climax fade</td><td class="n">1,0</td><td class="n">+1.604 / 8,9%</td><td></td></tr>
</tbody>
</table>
<p class="muted">Không có scalp SP500 nào pass đủ bộ lọc. Cũng từng pass nhưng không dùng trong danh mục khuyến nghị: u3, u5, u8, u9.</p>

<h2>4. Lot từng hệ — vốn 100k (kịch bản khuyến nghị)</h2>
<p>Lot <span class="k">robust</span> = trung bình lot tối ưu trên nửa A và nửa B, rồi scale cho vừa ràng buộc DD / spread ×2 / gap 5%, làm tròn bước sàn. Khóa hedge cuối tuần (W) bật cho mọi giỏ.</p>

<h3>4.1 Ghép vàng + SP500, 15 hệ</h3>
<table>
<thead>
<tr><th class="s">Hệ</th><th class="n">An toàn</th><th class="n">Cân bằng</th><th class="n">Mạnh tay</th><th class="n">Mạnh tay ×1,7</th></tr>
</thead>
<tbody>
<tr><td class="s">g2</td><td class="n">0,05</td><td class="n">0,09</td><td class="n">0,20</td><td class="n">0,34</td></tr>
<tr><td class="s">xs10</td><td class="n">0,24</td><td class="n">0,40</td><td class="n">0,79</td><td class="n">1,34</td></tr>
<tr><td class="s">x1</td><td class="n">0,05</td><td class="n">0,07</td><td class="n">0,12</td><td class="n">0,20</td></tr>
<tr><td class="s">xs6</td><td class="n">0,30</td><td class="n">0,52</td><td class="n">0,99</td><td class="n">1,68</td></tr>
<tr><td class="s">xs4</td><td class="n">0,15</td><td class="n">0,26</td><td class="n">0,51</td><td class="n">0,87</td></tr>
<tr><td class="s">u15</td><td class="n">1,6</td><td class="n">2,4</td><td class="n">4,4</td><td class="n">7,5</td></tr>
<tr><td class="s">xs2</td><td class="n">0,24</td><td class="n">0,31</td><td class="n">0,81</td><td class="n">1,38</td></tr>
<tr><td class="s">xs7</td><td class="n">0,23</td><td class="n">0,39</td><td class="n">0,96</td><td class="n">1,63</td></tr>
<tr><td class="s">u12</td><td class="n">6,5</td><td class="n">8,1</td><td class="n">7,7</td><td class="n">13,1</td></tr>
<tr><td class="s">xs3</td><td class="n">0,14</td><td class="n">0,33</td><td class="n">0,66</td><td class="n">1,12</td></tr>
<tr><td class="s">xs1</td><td class="n">0,20</td><td class="n">0,38</td><td class="n">0,85</td><td class="n">1,45</td></tr>
<tr><td class="s">g7</td><td class="n">0,01</td><td class="n">0,02</td><td class="n">0,05</td><td class="n">0,09</td></tr>
<tr><td class="s">u13</td><td class="n">3,2</td><td class="n">5,2</td><td class="n">7,7</td><td class="n">13,1</td></tr>
<tr><td class="s">xs5</td><td class="n">0,24</td><td class="n">0,40</td><td class="n">0,80</td><td class="n">1,36</td></tr>
<tr><td class="s">g5</td><td class="n">0,03</td><td class="n">0,06</td><td class="n">0,07</td><td class="n">0,12</td></tr>
</tbody>
</table>
<p><span class="k">Đánh tay (10 scalp, vốn 100k):</span> xs1 0,30 · xs2 0,21 · xs3 0,17 · xs4 0,15 · xs5 0,24 · xs6 0,16 · xs7 0,35 · xs8 0,28 · xs9 0,15 · xs10 0,22. Bậc ×3 / ×5: nhân tất cả rồi làm tròn 0,01. Đánh tay ×3: +218.538 / DD 10,8%.</p>
<p class="muted">Lãi từng tháng kịch bản An toàn (USD): 18.839, 18.009, 13.042, 10.917, 14.609, 20.708.</p>

<h3>4.2 Chỉ vàng, 8 hệ (tối ưu riêng, có thêm gp2)</h3>
<table>
<thead>
<tr><th>Kịch bản</th><th class="n">MT5 lãi / DD</th><th>Lot (g2, xs10, x1, xs6, xs4, xs7, xs2, gp2)</th></tr>
</thead>
<tbody>
<tr><td>An toàn</td><td class="n">+74.963 / 6,9%</td><td>0,10 · 0,42 · 0,05 · 0,28 · 0,26 · 0,46 · 0,32 · 0,05</td></tr>
<tr><td>Cân bằng</td><td class="n">+126.015 / 11,7%</td><td>0,17 · 0,70 · 0,09 · 0,46 · 0,43 · 0,78 · 0,54 · 0,08</td></tr>
<tr><td>Mạnh tay (đã cắt ×0,906)</td><td class="n">+208.221 / 19,3%</td><td>0,25 · 1,18 · 0,14 · 0,81 · 0,72 · 1,26 · 0,91 · 0,14</td></tr>
<tr><td>Đánh tay xs1–xs10</td><td class="n">+71.064 / 3,5%</td><td>0,29 · 0,20 · 0,14 · 0,15 · 0,24 · 0,16 · 0,38 · 0,29 · 0,15 · 0,22</td></tr>
<tr><td>Đánh tay ×5</td><td class="n">+355.318 / 17,6%</td><td>Nhân ×5, làm tròn 0,01</td></tr>
</tbody>
</table>

<h3>4.3 Chỉ SP500, 5 hệ (u13, u12, u2, up1, up2 — không có scalp pass)</h3>
<table>
<thead>
<tr><th>Kịch bản</th><th class="n">MT5 lãi / DD</th><th>Gap 5%</th><th>sx2</th><th>Lot u13 / u12 / u2 / up1 / up2</th></tr>
</thead>
<tbody>
<tr><td>An toàn</td><td class="n">+49.551 / 5,5%</td><td class="n">29,6%</td><td class="n">7,7%</td><td>6,8 / 5,2 / 4,0 / 5,6 / 6,6</td></tr>
<tr><td>Cân bằng</td><td class="n">+81.769 / 9,4%</td><td class="n">49,6%</td><td class="n">12,6%</td><td>11,0 / 8,5 / 6,9 / 9,4 / 10,7</td></tr>
<tr><td>Mạnh tay</td><td class="n">+167.946 / 18,8%</td><td class="n">99,8%</td><td class="n">24,4%</td><td>21,0 / 22,6 / 12,6 / 19,0 / 20,3</td></tr>
</tbody>
</table>
<p class="muted">Mạnh tay chỉ-SP500 dùng lot lớn (u12 22,6; u13 21,0). Cần kiểm tra trần lot của sàn trước khi chạy. Tháng 8 yếu nhất nhưng vẫn dương.</p>

{img('eq_split100.png')}
{img('mon_split100.png')}

<h2>5. Tóm tắt vốn 50k (tối ưu riêng, DD gần như giữ nguyên)</h2>
<p>Lãi xấp xỉ một nửa so với 100k vì ràng buộc là theo % vốn. Lot không luôn đúng bằng một nửa do bước làm tròn 0,01 / 0,1.</p>
<table>
<thead>
<tr><th>Sách</th><th>Kịch bản</th><th class="n">MT5 lãi / DD</th><th>Lot</th></tr>
</thead>
<tbody>
<tr><td>Chỉ vàng</td><td>An toàn</td><td class="n">+36.069 / 5,5%</td><td>g2 0,05 · xs10 0,21 · x1 0,02 · xs6 0,14 · xs4 0,13 · xs7 0,23 · xs2 0,16 · gp2 0,02</td></tr>
<tr><td>Chỉ vàng</td><td>Cân bằng</td><td class="n">+61.656 / 11,0%</td><td>g2 0,08 · xs10 0,35 · x1 0,04 · xs6 0,23 · xs4 0,21 · xs7 0,39 · xs2 0,27 · gp2 0,04</td></tr>
<tr><td>Chỉ vàng</td><td>Mạnh tay (đã cắt ×0,938)</td><td class="n">+106.622 / 19,3%</td><td>g2 0,13 · xs10 0,61 · x1 0,07 · xs6 0,41 · xs4 0,37 · xs7 0,65 · xs2 0,47 · gp2 0,07</td></tr>
<tr><td>Chỉ vàng</td><td>Đánh tay / ×5</td><td class="n">+34.876 / 3,5% · +174.378 / 17,3%</td><td>xs1 0,14 · xs2 0,10 · xs3 0,07 · xs4 0,07 · xs5 0,12 · xs6 0,08 · xs7 0,19 · xs8 0,14 · xs9 0,07 · xs10 0,11</td></tr>
<tr><td>Chỉ SP500</td><td>An toàn</td><td class="n">+24.776 / 5,5%</td><td>u13 3,4 / u12 2,6 / u2 2,0 / up1 2,8 / up2 3,3</td></tr>
<tr><td>Chỉ SP500</td><td>Cân bằng</td><td class="n">+40.645 / 9,3%</td><td>5,5 / 4,2 / 3,4 / 4,7 / 5,3</td></tr>
<tr><td>Chỉ SP500</td><td>Mạnh tay</td><td class="n">+83.900 / 18,8%</td><td>10,5 / 11,3 / 6,3 / 9,5 / 10,1</td></tr>
</tbody>
</table>
<p class="muted">Sách ghép 2 tài sản được tính ở vốn 100k (mục 1 và 4.1). Mục này chỉ tóm tắt sách một tài sản ở vốn 50k.</p>

<h2>6. Rủi ro, khóa hedge cuối tuần, và cài đặt EA</h2>
<div class="warn keep">
<p><span class="k">Rủi ro cần nhớ</span></p>
<ul>
<li><span class="k">Gap trong phiên:</span> xuyên mọi SL, không chặn được, chỉ giảm bằng cách hạ lot. Mạnh tay ghép 2 tài sản: gap 5% ước tính ~99% vốn; bậc ×1,7 ~168%. Mạnh tay một tài sản cũng ~82–100%.</li>
<li><span class="k">Mẫu ngắn:</span> chỉ 6 tháng dữ liệu (vàng có một nhịp giảm sau 20/08). Một số scalp chỉ khoảng 90–130 lệnh (xs6, xs7, xs8).</li>
<li><span class="k">Overfit / multiple testing:</span> đã quét hàng chục nghìn cấu hình. Có A/B, placebo, đảo dấu, spread ×2, trễ 2 nến và MT5, nhưng vẫn cần forward demo.</li>
<li><span class="k">Lot lớn SP500:</span> Mạnh tay 100k dùng 21–22 lot/hệ. Kiểm tra trần lot sàn. u6 rất nhạy spread (ở 2,8 lot trên vốn 10k, spread ×2 → DD 59%).</li>
<li>Joint DD MT5 dựng từ deals + giá M1 bid, sai số khoảng 1–6%. Số gap 5% và spread ×2 là mô phỏng Python.</li>
</ul>
</div>

<div class="box keep">
<p><span class="k">Khóa hedge cuối tuần và ngày lễ (W).</span> Từ 21:00 tối Thứ Sáu giờ server (XM, Europe/Athens) và trước ngày lễ, EA mở lệnh hedge đúng vị thế ròng của giỏ, dừng nhồi, đầu tuần (hoặc hết lễ) thì gỡ hedge. Cách này giữ khoảng 91–96% lợi nhuận, và cắt DD khi gặp gap 5% cuối tuần (ví dụ PortA: từ 49,7% xuống 16,2%). <span class="k">Mặc định trong mã nguồn: W TẮT</span> — phải bật khi chạy danh mục này. Gap trong phiên không dùng được cách này.</p>
<p>Ngày lễ đã khai báo cho cửa sổ test: <span class="mono">2026.07.03, 2026.09.07, 2026.11.26</span>. Cần cập nhật lịch lễ khi chạy tiếp.</p>
</div>

<h3>EA <span class="mono">BRAIN_XuLiLenh_r5</span></h3>
<p>Nguồn: <span class="mono">ea/BRAIN_XuLiLenh_r5.mq5</span> (UTF-16LE). Chế độ CSV điểm vào: <span class="mono">InpVao=4</span>, <span class="mono">InpCsvChung=true</span>, file <span class="mono">brain2\\&lt;job&gt;_mt5.csv</span> trong Common\\Files. Cột CSV: <span class="mono">thoi_gian, ma, chieu, gia, nguon, lot</span> (giờ server).</p>
<table>
<thead>
<tr><th>Input</th><th>Giỏ (basket)</th><th>Scalp</th><th>Ý nghĩa</th></tr>
</thead>
<tbody>
<tr><td>InpLot0</td><td>lot lệnh đầu (bảng mục 4)</td><td>lot scalp</td><td>Khối lượng lệnh đầu</td></tr>
<tr><td>InpNhoi</td><td>1</td><td>0</td><td>Bật DCA</td></tr>
<tr><td>InpBuocGia</td><td>8 (vàng) / 30–60 (SP500)</td><td>6</td><td>Bước nhồi theo giá</td></tr>
<tr><td>InpGianBuoc</td><td>1,4</td><td>—</td><td>Giãn bước mỗi tầng</td></tr>
<tr><td>InpMaxTang</td><td>3–4</td><td>1</td><td>Số tầng tối đa</td></tr>
<tr><td>InpTPGia</td><td>2–8 (theo hệ)</td><td>TP giá (vd xs1 = 8, xs2 = 13)</td><td>Chốt giỏ / chốt scalp</td></tr>
<tr><td>InpGiuToiDaNen</td><td>0</td><td>30 hoặc 90</td><td>Giữ tối đa (nến)</td></tr>
<tr><td>InpCatLoPct</td><td>0</td><td>SL_giá × lot × 100 / vốn × 100</td><td>SL % balance. Ví dụ xs3 lot 0,3, SL 13, vốn 30k → 1,3%</td></tr>
<tr><td><b>InpTuanKhoaGio</b></td><td><b>21</b></td><td><b>0</b></td><td>W: giờ server Thứ Sáu bắt đầu khóa hedge (0 = tắt)</td></tr>
<tr><td>InpNghiLe</td><td>2026.07.03, 2026.09.07, 2026.11.26</td><td>—</td><td>Dùng dấu phẩy. Dấu ; trong file .set là comment</td></tr>
</tbody>
</table>
<p class="muted">Hedge W gắn comment lệnh <span class="mono">XL_WB</span> / <span class="mono">XL_WS</span>. Không đặt lệnh thật từ tài liệu này.</p>

<h2>7. Vị trí file và cách đọc số</h2>
<ul>
<li><span class="k">Máy nhà:</span> <span class="mono">E:\\GrokWork\\bt_v3\\</span> — <span class="mono">README_SCENARIOS.md</span> (mục 12), <span class="mono">SUMMARY_V3.md</span> (mục 22), <span class="mono">results\\r6\\ROUND7_NOTES.md</span>, và file PDF này.</li>
<li><span class="k">Git:</span> repo <span class="mono">thebrainago/brain2</span>, nhánh <span class="k">grok/scenarios-v3</span> (không động nhánh main), thư mục <span class="mono">grok_systems/v3/</span>. Xem commit mới nhất trên nhánh này.</li>
<li><span class="k">Máy Grok (box):</span> <span class="mono">/workspace/bt_3m/v3/</span> — code <span class="mono">opt8.py</span>, <span class="mono">r4/joint8.py</span>, số <span class="mono">results/r6/opt8.json</span>, <span class="mono">r4/joint8.json</span>.</li>
<li>Tái lập: <span class="mono">python opt8.py</span> rồi <span class="mono">python ../r4/joint8.py</span> (tái dùng đường vốn đơn vị và deals MT5 đã có).</li>
</ul>
<p><span class="k">Cách đọc số.</span> Cột “MT5” là Strategy Tester 100% real ticks — số chốt khi so sánh hệ và danh mục. Gap 5% và spread ×2 là mô phỏng Python (engine bảo thủ). Mọi số trong tài liệu này là <span class="k">backtest</span>, không phải kết quả tài khoản live. Thiếu dữ liệu thì tài liệu gốc ghi <span class="k">KHÔNG CÓ</span>.</p>

</body>
</html>
'''

pdf=OUT/'TomTat_KichBan_Vang_SP500_2026-11-28.pdf'
HTML(string=html, base_url=str(OUT)).write_pdf(pdf)
print('wrote', pdf, 'bytes', pdf.stat().st_size)
