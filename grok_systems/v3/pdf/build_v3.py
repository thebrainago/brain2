# -*- coding: utf-8 -*-
"""PDF v3: two 100 USD cent accounts, min lot 0.10 gold / 0.14 US500."""
import json, re
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from weasyprint import HTML

V=Path('/workspace/bt_3m/v3'); OUT=V/'pdf'; FIG=OUT/'fig'; DEJ=Path('/usr/share/fonts/truetype/dejavu')
FIG.mkdir(exist_ok=True)
M=json.load(open(V/'results/r6/minlot10.json'))
plt.rcParams['font.family']='DejaVu Sans'

# monthly chart: US500 balanced + gold3 starter
us=M['feas']['US500_Cân bằng_scale']
g3=next(s for s in M['starters'] if s['name']=='gold3_xs7_xs10_xs2')
g2=next(s for s in M['starters'] if s['name']=='gold2_xs7_xs2')
g4=next(s for s in M['starters'] if s['name']=='gold4_xs7_xs10_xs2_xs6')
mon=['Th6','Th7','Th8','Th9','Th10','Th11']
fig,ax=plt.subplots(figsize=(8.2,2.7)); w=0.22; x=np.arange(6)
sets=[(us['months'],'TK SP500 — Cân bằng','#4f9d69'),
      (g3['months'],'TK Vàng — 3 scalp (khuyên)','#d4a017'),
      (g2['months'],'TK Vàng — 2 scalp an toàn hơn','#1f4e79')]
for i,(m,l,c) in enumerate(sets):
    ax.bar(x+(i-1)*w, m, w, label=l, color=c)
ax.set_xticks(x); ax.set_xticklabels(mon)
ax.set_ylabel('USD / tháng (mỗi TK 100 USD)')
ax.axhline(0,color='#333',lw=.6)
ax.legend(fontsize=7.5,ncol=3,loc='upper center',bbox_to_anchor=(0.5,1.18),frameon=False)
ax.grid(axis='y',alpha=.3)
plt.tight_layout(); plt.savefig(FIG/'mon_twoacc.png',dpi=170); plt.close()

# reuse CSS from v1
src=(OUT/'build_pdf.py').read_text()
css=re.search(r'<style>(.*?)</style>',src,re.S).group(1).replace('{{','{').replace('}}','}')
css=css.replace('{DEJ}',str(DEJ))
css=css.replace('Tóm tắt kịch bản Vàng & SP500  ·  28/11/2026  ·  trang ',
                'Hai TK 100 USD  ·  min lot 0,10/0,14  ·  28/11/2026  ·  trang ')

def usd(v):
    return f"+{v:,.0f} USD<br/><small>(+{v*100:,.0f} cent)</small>".replace(',','.')

html=f'''<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"/>
<title>Hai tài khoản 100 USD — vàng và SP500, min lot 0,10 / 0,14</title>
<style>{css}</style></head><body>

<h1>Hai tài khoản cent 100 USD — tách vàng và SP500</h1>
<p class="sub">28/11/2026 (giờ VN, UTC+7) · Mỗi tài khoản 100 USD = 10.000 cent · Lot tối thiểu: vàng 0,10 / US500 0,14 · Deals MT5 100% real ticks scale tuyến tính, cửa sổ 01/06–27/11/2026 · Backtest, không phải kết quả live, không phải lời khuyên đầu tư.</p>

<div class="ok">
<p><span class="k">Khuyến nghị cho kế hoạch hai tài khoản.</span></p>
<ul>
<li><span class="k">Tài khoản SP500, 100 USD:</span> chạy đủ kịch bản <span class="k">Cân bằng</span> (5/5 hệ). Lãi 6 tháng +82 USD, DD 9,4%, gap 5% khoảng 50%. Đủ 6/6 tháng.</li>
<li><span class="k">Tài khoản vàng, 100 USD:</span> không chạy đủ kịch bản gốc (An toàn / Cân bằng / Đánh tay đều 0 hệ đạt min 0,10). Chạy bộ khởi đầu 3 scalp <span class="k">xs7 + xs10 + xs2</span>, mỗi hệ 0,10 lot. Lãi +90 USD, DD 8,0%, gap 5% khoảng 48%. Đủ 6/6 tháng. Không chạy hệ giỏ (g2, x1, gp2, g5, g7) trên 100 USD.</li>
<li>Vốn tối thiểu để chạy <span class="k">đủ</span> kịch bản gốc chỉ-SP500: <span class="k">35 USD</span>. Chỉ-vàng đủ sách An toàn: <span class="k">2.000 USD</span>, Cân bằng: <span class="k">1.250 USD</span>.</li>
</ul>
</div>

<div class="warn">
<p><span class="k">Giả định lot tối thiểu — xác nhận trong MT5 của tài khoản thật.</span> Vàng 0,10 lot (1 lot = 1 oz) lấy từ XM Micro MT5; Exness Standard Cent ghi chính thức min 0,01. Bạn nói Exness cũng khoảng 0,14. Em dùng 0,10 cho vàng và <span class="k">0,14 cho US500</span> (trùng Help Center Indices 13/11/2026 và lời bạn). Bước lot giả định 0,01. Nếu vàng cũng min 0,14 thì nâng lot starter lên 0,14, DD và gap tăng khoảng 40%. Contract size US500c: <span class="k">KHÔNG CÓ</span> — giả định 1 lot cent = 0,01 USD/điểm. Spread thực Exness cent: KHÔNG CÓ; cột spread ×2 là mức stress. Chưa chạy lại Tester trên server Exness.</p>
</div>

<h2>1. Tài khoản SP500 — vốn 100 USD</h2>
<p>Cả 5 hệ (u13, u12, u2, up1, up2) đều trên min 0,14 ở mọi bậc. 100 USD đủ để giữ đúng tỷ lệ lot của sách 100k. Tháng 8 yếu nhất nhưng vẫn dương.</p>
<table>
<thead><tr><th class="s">Kịch bản</th><th class="n">Số hệ</th><th class="n">Lãi 6 tháng</th><th class="n">DD MT5</th><th class="n">Tháng +</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th><th class="n">A / B</th></tr></thead>
<tbody>
<tr><td class="s">An toàn</td><td class="n">5/5</td><td class="n">{usd(49.551)}</td><td class="n">5,5%</td><td class="n">6/6</td><td class="n">30%</td><td class="n">7,7%</td><td class="n">20 / 29</td></tr>
<tr><td class="s"><b>Cân bằng</b></td><td class="n"><b>5/5</b></td><td class="n"><b>{usd(81.769)}</b></td><td class="n"><b>9,4%</b></td><td class="n">6/6</td><td class="n">50%</td><td class="n">12,6%</td><td class="n">33 / 49</td></tr>
<tr><td class="s">Mạnh tay</td><td class="n">5/5</td><td class="n">{usd(167.946)}</td><td class="n">18,8%</td><td class="n">6/6</td><td class="n">100%</td><td class="n">24,4%</td><td class="n">69 / 99</td></tr>
</tbody></table>
<p>Lot cent Cân bằng: u13 1,10 · u12 0,85 · u2 0,69 · up1 0,94 · up2 1,07. An toàn: 0,68 / 0,52 / 0,40 / 0,56 / 0,66. Mạnh tay: 2,10 / 2,26 / 1,26 / 1,90 / 2,03.</p>
<p>Lãi theo tháng Cân bằng (USD): 22, 12, 2, 13, 8, 25. <span class="k">Không chạy Mạnh tay</span> — gap 5% trong phiên có thể xóa sạch 100 USD.</p>

<h2>2. Tài khoản vàng — vốn 100 USD</h2>
<p>Lot quy đổi từ sách 100k (chia 10) hầu hết dưới 0,10. An toàn / Cân bằng / Đánh tay gốc: <span class="k">0 hệ đạt min</span>. Chỉ Mạnh tay gốc giữ xs10 (0,12) và xs7 (0,13): +66 USD, DD 9,6%, gap 59%. Ép mọi hệ giỏ lên 0,10 lot thì DD <span class="k">142%</span> — không dùng. Hệ giỏ đơn lẻ ở 0,10 lot / 100 USD có DD 22–87%.</p>
<p>Bộ khởi đầu dưới đây chỉ dùng scalp xs*, mỗi hệ <span class="k">0,10 lot cent = 0,10 oz</span>. InpCatLoPct với SL 10 USD = 1,0% vốn.</p>
<table>
<thead><tr><th class="s">Bộ khởi đầu</th><th class="s">Hệ (lot 0,10)</th><th class="n">Lãi 6 tháng</th><th class="n">DD MT5</th><th class="n">Tháng +</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th></tr></thead>
<tbody>
<tr><td class="s">An toàn hơn</td><td class="s">xs7, xs2</td><td class="n">{usd(56.309)}</td><td class="n">7,1%</td><td class="n">6/6</td><td class="n">28%</td><td class="n">7,6%</td></tr>
<tr><td class="s"><b>Cân bằng (khuyên)</b></td><td class="s"><b>xs7, xs10, xs2</b></td><td class="n"><b>{usd(90.110)}</b></td><td class="n"><b>8,0%</b></td><td class="n">6/6</td><td class="n">48%</td><td class="n">10,8%</td></tr>
<tr><td class="s">Mạnh hơn</td><td class="s">xs7, xs10, xs2, xs6</td><td class="n">{usd(123.876)}</td><td class="n">9,4%</td><td class="n">6/6</td><td class="n">71%</td><td class="n">12,5%</td></tr>
</tbody></table>
<p>Thêm một bản 4 hệ, lot tối ưu lại (xs7 0,16 · xs10 0,14 · xs6 0,11 · xs2 0,10): {usd(152.5)}, DD 13,1%, gap 96%, spread ×2 17,1%, đủ 6/6 tháng. Lãi theo tháng bộ 3 hệ (USD): 11, 19, 19, 8, 13, 20. Tháng 9 của bộ 4 hệ (lot đều 0,10) chỉ +1 USD nhưng vẫn dương. Nếu min vàng thật là 0,14: nhập 0,14, lãi / DD / gap khoảng ×1,4 (bộ 3 hệ ≈ DD 11%, gap 67%).</p>

<img class="fig" src="{FIG/'mon_twoacc.png'}"/>
<p class="muted">Lãi từng tháng trên mỗi tài khoản 100 USD: SP500 Cân bằng (đủ 5 hệ) và hai bộ khởi đầu vàng. Cả ba dương đủ 6/6 tháng.</p>

<h2>3. Vốn tối thiểu để chạy đủ kịch bản gốc</h2>
<p>Giữ đúng tỷ lệ lot của sách 100k, mọi hệ đạt min lot. DD% gần như không đổi vì lot và vốn cùng scale.</p>
<table class="keep">
<thead><tr><th class="s">Sách</th><th class="n">An toàn</th><th class="n">Cân bằng</th><th class="n">Mạnh tay</th><th class="n">Đánh tay</th></tr></thead>
<tbody>
<tr><td class="s">Chỉ SP500 (min 0,14)</td><td class="n"><b>35 USD</b> (u2)</td><td class="n">20 USD</td><td class="n">11 USD</td><td class="n">—</td></tr>
<tr><td class="s">Chỉ vàng (min 0,10)</td><td class="n"><b>2.000 USD</b> (x1, gp2)</td><td class="n"><b>1.250 USD</b> (gp2)</td><td class="n">714 USD</td><td class="n">714 USD (xs3)</td></tr>
<tr><td class="s">Chỉ vàng nếu min 0,14</td><td class="n">2.800 USD</td><td class="n">1.750 USD</td><td class="n">1.000 USD</td><td class="n">1.000 USD</td></tr>
<tr><td class="s">Ghép 2 mã (min 0,10 / 0,14)</td><td class="n">10.000 USD (g7)</td><td class="n">5.000 USD</td><td class="n">2.000 USD</td><td class="n">667 USD</td></tr>
</tbody></table>
<p>Nếu chấp nhận bỏ hệ lot nhỏ (x1, gp2, g2): sách vàng Cân bằng còn 5 scalp từ khoảng 250–500 USD. Đánh tay đủ 10 hệ từ 714 USD (min 0,10). Ở 500 USD, Đánh tay mới giữ được 6/10 hệ.</p>

<h2>4. Nếu ghép cả hai mã trên một tài khoản 100 USD</h2>
<p>Không phải kế hoạch của bạn, chỉ để đối chiếu. Sau khi loại hệ dưới min, chỉ còn 3 hệ SP500 (u15, u12, u13): An toàn +20 USD / DD 2,7%; Cân bằng +28 USD / DD 3,6% — yếu hơn tài khoản SP500 tách riêng (thiếu u2, up1, up2). Ép hệ vàng lên 0,10 lot: DD 116%, gap khoảng 370%.</p>
<p>Hai tài khoản 100 USD tách riêng tốt hơn một tài khoản 100 USD ghép: bên SP500 giữ đủ 5 hệ, bên vàng chọn được bộ scalp vừa min lot, và không bị lỗ vàng làm tăng DD của SP500.</p>

<h2>5. Việc cần làm trước khi chạy</h2>
<ul>
<li>Trong MT5 Exness Cent, mở Specification của <span class="mono">XAUUSDc</span> và <span class="mono">US500c</span>: min lot, bước lot, contract size. Nếu khác giả định, nhắn để em tính lại.</li>
<li>Đổi symbol EA sang XAUUSDc / US500c, nhập lot cent. Scalp vàng: InpCatLoPct = 1,0 khi SL 10 USD và lot 0,10 trên vốn 100 USD.</li>
<li>Chạy một lượt MT5 Tester cuối cho đúng lot, rồi demo / vốn cực nhỏ trước.</li>
<li>Chưa tính: spread thực cent, spread ×3, margin và đòn bẩy thật — <span class="k">KHÔNG CÓ</span>.</li>
</ul>
<p class="muted">File: <span class="mono">README_SCENARIOS.md</span> mục 14, <span class="mono">SUMMARY_V3.md</span> mục 24, <span class="mono">results/r6/ROUND9_NOTES.md</span>, <span class="mono">minlot10.json</span>. Git nhánh <span class="mono">grok/scenarios-v3</span>, thư mục <span class="mono">grok_systems/v3/</span>. Máy nhà: <span class="mono">E:\\GrokWork\\bt_v3\\</span>.</p>
</body></html>'''

html=re.sub(r'(?<=>)(\d+)\.(\d)%', r'\1,\2%', html)
pdf=OUT/'TomTat_KichBan_v3_minlot01_2026-11-28.pdf'
HTML(string=html, base_url=str(OUT)).write_pdf(pdf)
print('wrote', pdf, 'bytes', pdf.stat().st_size)
