# -*- coding: utf-8 -*-
import json,re,subprocess
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from weasyprint import HTML
V=Path('/workspace/bt_3m/v3'); OUT=V/'pdf'; FIG=OUT/'fig'; DEJ=Path('/usr/share/fonts/truetype/dejavu')
F=json.load(open(V/'results/r6/cent_final.json')); D=json.load(open(V/'results/r6/direct9.json'))
plt.rcParams['font.family']='DejaVu Sans'
# chart: monthly net USD, re-tuned, joint/xau/us500 balanced + joint aggressive
mon=['Th6','Th7','Th8','Th9','Th10','Th11']
sets=[('JOINT_balanced','Ghép Cân bằng','#1f4e79'),('JOINT_aggressive','Ghép Mạnh tay','#c0504d'),('XAU_balanced','Vàng Cân bằng','#d4a017'),('US500_balanced','SP500 Cân bằng','#4f9d69')]
fig,ax=plt.subplots(figsize=(8.2,2.9)); w=0.2; x=np.arange(6)
for i,(k,l,c) in enumerate(sets):
    m=F[k]['months']; ax.bar(x+(i-1.5)*w,m,w,label=l,color=c)
ax.set_xticks(x); ax.set_xticklabels(mon); ax.set_ylabel('USD / tháng (vốn 100 USD)'); ax.axhline(0,color='#333',lw=.6)
ax.legend(fontsize=7.5,ncol=4,loc='upper center',bbox_to_anchor=(0.5,1.16),frameon=False); ax.grid(axis='y',alpha=.3)
plt.tight_layout(); plt.savefig(FIG/'mon_cent.png',dpi=170); plt.close()
src=(OUT/'build_pdf.py').read_text()
css=re.search(r'<style>(.*?)</style>',src,re.S).group(1).replace('{{','{').replace('}}','}')
css=css.replace('{DEJ}',str(DEJ))
css=css.replace('Tóm tắt kịch bản Vàng & SP500  ·  28/11/2026  ·  trang ','Vốn 100 USD cent  ·  28/11/2026  ·  trang ')
def usd(v): return f"+{v:,.0f} USD<br/><small>(+{v*100:,.0f} cent)</small>".replace(',','.')
BOOK={'JOINT':'Ghép Vàng+SP500','XAU':'Chỉ Vàng','US500':'Chỉ SP500'}
TV={'conservative':'An toàn','balanced':'Cân bằng','aggressive':'Mạnh tay','manual':'Đánh tay'}
def r(b,t,bold=False):
    v=F[f'{b}_{t}']; bd=(lambda s:f'<b>{s}</b>') if bold else (lambda s:s)
    return f"<tr><td class='s'>{BOOK[b]}</td><td class='s'>{bd(TV[t])}</td><td class='n'>{v['nsys']}/{v['nsel']}</td><td class='n'>{bd(usd(v['net']))}</td><td class='n'>{bd(format(v['dd'],'.1f')+'%')}</td><td class='n'>{v['npos']}/6</td><td class='n'>{v['gap5']:.0f}%</td><td class='n'>{v['sx2']:.1f}%</td></tr>".replace('.',',') if False else \
    f"<tr><td class='s'>{BOOK[b]}</td><td class='s'>{bd(TV[t])}</td><td class='n'>{v['nsys']}/{v['nsel']}</td><td class='n'>{bd(usd(v['net']))}</td><td class='n'>{bd(f'{v[chr(100)+chr(100)]:.1f}'.replace('.',',')+'%')}</td><td class='n'>{v['npos']}/6</td><td class='n'>{v['gap5']:.0f}%</td><td class='n'>{f'{v[chr(115)+chr(120)+chr(50)]:.1f}'.replace('.',',')}%</td></tr>"
rows=''.join(r(b,t,bold=(t=='balanced')) for b in ['JOINT','XAU','US500'] for t in (['conservative','balanced','aggressive','manual'] if b!='US500' else ['conservative','balanced','aggressive']))
mx=''.join(f"<tr><td class='s'>{n}</td><td class='n'>×{F[k]['f']:.2f}</td><td class='n'>{usd(F[k]['net'])}</td><td class='n'>{F[k]['dd']:.1f}%</td><td class='n'>{F[k]['gap5']:.0f}%</td><td class='n'>{F[k]['sx2']:.1f}%</td></tr>".replace('×','×') for k,n in [('JOINT_aggressive_max','Ghép — Mạnh tay'),('XAU_aggressive_max','Chỉ Vàng — Mạnh tay'),('JOINT_manual_max','Ghép — Đánh tay'),('XAU_manual_max','Chỉ Vàng — Đánh tay')])
names={'JOINT_100k':'JOINT','XAU_100k':'XAU','US500_100k':'US500'}
tmap={'GREEDY_conservative':'An toàn','GREEDY_balanced':'Cân bằng','GREEDY_aggressive':'Mạnh tay','MANUAL_conservative':'Đánh tay'}
dr=''
for lab,v in D.items():
    if v.get('n',0)==0: continue
    b=lab.split('_')[0]; t=tmap['_'.join(lab.split('_')[2:4])]
    dr+=f"<tr><td class='s'>{BOOK[b]}</td><td class='s'>{t}</td><td class='n'>{v['n']}/{v['n100k']}</td><td class='n'>{usd(v['net_usd'])}</td><td class='n'>{v['dd']:.1f}%</td><td class='n'>{v['py']['gap5']:.0f}%</td><td class='n'>{v['py']['sx_dd']:.1f}%</td></tr>".replace('%</td>','%</td>')
    dr=dr.replace('0,0','0,0')
lotk=['xs1','xs2','xs3','xs4','xs5','xs6','xs7','xs8','xs9','xs10','g2','x1','g5','g7','gp2','u12','u13','u15','u2','up1','up2']
def lotrow(book,ks):
    h=''
    for k in ks:
        cells=[]
        for t in ['conservative','balanced','aggressive']:
            c=F[f'{book}_{t}']['cent'].get(k); cells.append(f'{c:.2f}'.replace('.',',') if c else 'loại')
        if all(c=='loại' for c in cells): continue
        h+=f"<tr><td class='s'>{k}</td>"+''.join(f"<td class='n'>{c}</td>" for c in cells)+'</tr>'
    return h
def sel(book): return F[f'{book}_balanced']['dd'] and [k for k in lotk if k in set(F[f'{book}_conservative']['cent'])|set(F[f'{book}_balanced']['cent'])|set(F[f'{book}_aggressive']['cent'])|set(F[f'{book}_aggressive']['dropped'])|set(F[f'{book}_conservative']['dropped'])]
man=', '.join(f"{k} {v:.2f}".replace('.',',') for k,v in F['XAU_manual']['cent'].items())
html=f'''<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"/><title>Kịch bản Vàng & SP500 — vốn 100 USD (cent)</title><style>{css}</style></head><body>
<h1>Vốn 100 USD (10.000 cent) — kịch bản Vàng và SP500</h1>
<p class="sub">28/11/2026 (giờ VN, UTC+7) · Cập nhật sau khi vốn được sửa từ 100k USD xuống 100 USD · Deals MT5 100% real ticks scale tuyến tính, cửa sổ 01/06–27/11/2026 · Backtest, không phải kết quả live, không phải lời khuyên đầu tư.</p>
<div class="warn"><p><span class="k">Điểm chính.</span></p><ul>
<li>10.000 cent chỉ khớp <span class="k">Exness Standard Cent (USC)</span>. <span class="k">XM Micro</span> vẫn tính số dư bằng USD và min 0,1 lot trên MT5 (= 0,1 oz vàng) nên gần như không đại diện được các hệ này.</li>
<li>Bước lot cent 0,01 (vàng 1 lot cent = 1 oz) tương đương bước 0,1 lot chuẩn ở vốn 100k. Các hệ lot nhỏ (g2, x1, g5, g7, gp2) bị loại hoặc làm tròn rất thô.</li>
<li>Em chưa chạy MT5 Tester trên server Exness. Số MT5 ở đây là deals đã có, scale tuyến tính theo lot.</li></ul></div>
<h2>1. Thông số hợp đồng đã tra</h2>
<table><thead><tr><th class="s">Sàn</th><th>Vàng</th><th>US500</th></tr></thead><tbody>
<tr><td class="s"><b>Exness Standard Cent</b></td><td>XAUUSDc: 1 lot cent = 0,01 lot chuẩn = 1 oz. Min 0,01 lot cent. Max 200 lot/lệnh. Bước lot: KHÔNG CÓ (giả định 0,01).</td><td>US500c có trên Cent, chỉ MT5 và Exness platform. Contract size / min lot US500c: KHÔNG CÓ (em giả định 1 lot cent = 0,01 USD/điểm, min 0,01).</td></tr>
<tr><td class="s">Exness spread</td><td colspan="2">Cent “từ 0,3 pip” (forex). Spread XAUUSDc, US500c thực tế: KHÔNG CÓ.</td></tr>
<tr><td class="s"><b>XM Micro</b></td><td>1 lot = 1.000 đơn vị, vàng 1 lot = 1 oz. Min 0,1 lot trên MT5 (0,01 trên MT4), bước 0,01. Số dư vẫn USD, không có tài khoản cent thật.</td><td>US500Cash có trên Micro; contract size, min lot: KHÔNG CÓ.</td></tr>
</tbody></table>
<p class="muted">Nguồn: Exness Help Center “Standard Cent account” (cập nhật 27/11/2026), “Indices” (13/11/2026), “Common trading terms” (23/09/2026); xmtrading.com/account-types/micro và XM Help Center (minimum lot size for Micro accounts); fxfan.club. Bài “Indices” của Exness tự mâu thuẫn: một dòng nói chỉ số không có trên Standard Cent, mục US500 ngay dưới và bài Cent lại ghi có US500c trên MT5. Em tin hai nguồn sau (mới hơn); nên xác nhận trong MT5 thật.</p>
<h2>2. Quy đổi lot 100k → 100 USD</h2>
<p>Vốn nhỏ đi 1.000 lần. Lot chuẩn L ở vốn 100k thành <span class="k">L/10 lot cent</span>, làm tròn 0,01. Lot quy đổi dưới 0,01 thì loại hệ đó. Các bảng dưới ghi lãi bằng USD và cent (×100), DD là DD gộp MT5, gap 5% và spread ×2 là mô phỏng Python (spread cent thường rộng hơn XM nên spread ×2 là mức gần thực tế hơn).</p>
<h2>3. Kịch bản tối ưu lại trên lưới lot cent (khuyến nghị cho 100 USD)</h2>
<p>Ngưỡng giữ như trước: An toàn 10/15/30, Cân bằng 15/22/50, Mạnh tay 19/28/100 (DD / spread ×2 / gap 5%). Lot được làm tròn xuống rồi leo từng bước 0,01 trên toàn mẫu, nên có phần in-sample. Nửa A / nửa B Python đều dương trong mọi sách.</p>
<table><thead><tr><th class="s">Sách</th><th class="s">Kịch bản</th><th class="n">Số hệ</th><th class="n">Lãi 6 tháng</th><th class="n">DD MT5</th><th class="n">Tháng +</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th></tr></thead><tbody>{rows}</tbody></table>
<img class="fig" src="{FIG/'mon_cent.png'}"/>
<p class="muted">Lãi theo tháng (USD, vốn 100 USD): cả bốn sách dương đủ 6/6 tháng; tháng 8 yếu nhất.</p>
<div class="warn keep"><p><span class="k">Gap 5% ≥ 100% = một cú gap 5% trong phiên có thể xóa sạch 100 USD.</span> Mạnh tay và mọi bậc nhân lot nằm ở vùng này. Cân bằng (gap ~50%) là mức em khuyên dùng khi bắt đầu, và vẫn nên chạy cực nhỏ trước.</p></div>
<h3>Bậc nhân lot tối đa (DD MT5 ≤ 19,5%)</h3>
<table class="keep"><thead><tr><th class="s">Sách / kịch bản</th><th class="n">Nhân lot</th><th class="n">Lãi 6 tháng</th><th class="n">DD MT5</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th></tr></thead><tbody>{mx}</tbody></table>
<h2 style="page-break-before:auto">4. Tính lại trực tiếp từ kịch bản 100k (không tối ưu lại)</h2>
<p>Hệ bị loại vì lot cent dưới 0,01: ghép An toàn / Cân bằng mất g2, x1, g5, g7; ghép Mạnh tay mất g5, g7; chỉ-vàng An toàn / Cân bằng mất x1, gp2. SP500 và Đánh tay giữ đủ. Ở bản tối ưu lại, g7 (ghép) và gp2 (chỉ-vàng) luôn bị loại.</p>
<table class="keep"><thead><tr><th class="s">Sách</th><th class="s">Kịch bản</th><th class="n">Số hệ giữ</th><th class="n">Lãi 6 tháng</th><th class="n">DD MT5</th><th class="n">Gap 5%</th><th class="n">Spread ×2 DD</th></tr></thead><tbody>{dr}</tbody></table>
<h2>5. Lot từng hệ (lot cent, bản tối ưu lại)</h2>
<table class="keep"><thead><tr><th class="s">Ghép Vàng+SP500</th><th class="n">An toàn</th><th class="n">Cân bằng</th><th class="n">Mạnh tay</th></tr></thead><tbody>{lotrow('JOINT',sel('JOINT'))}</tbody></table>
<table class="keep"><thead><tr><th class="s">Chỉ Vàng</th><th class="n">An toàn</th><th class="n">Cân bằng</th><th class="n">Mạnh tay</th></tr></thead><tbody>{lotrow('XAU',sel('XAU'))}</tbody></table>
<table class="keep"><thead><tr><th class="s">Chỉ SP500</th><th class="n">An toàn</th><th class="n">Cân bằng</th><th class="n">Mạnh tay</th></tr></thead><tbody>{lotrow('US500',sel('US500'))}</tbody></table>
<p>Lot Đánh tay (lot cent): {man}.</p>
<h2>6. Hệ quả và việc cần làm</h2>
<ul>
<li><span class="k">Ít hệ hơn:</span> ghép còn 12–14/15 hệ, chỉ-vàng 6–7/8, SP500 giữ 5/5 (nếu giả định US500c đúng). Hệ lot cent 0,01–0,03 sai số làm tròn 30–100% mỗi bước.</li>
<li><span class="k">XM Micro MT5:</span> chỉ còn 3/15 hệ ghép (đều là SP500), chỉ-vàng 0–2/8, Đánh tay 0/10.</li>
<li><span class="k">EA:</span> đổi symbol sang XAUUSDc / US500c, nhập lot theo lot cent. Scalp vàng: InpCatLoPct = SL_giá × lot_cent × 1 oz ÷ vốn USD × 100. Em chưa test EA trên Exness.</li>
<li><span class="k">Rủi ro chưa tính:</span> spread thực XAUUSDc / US500c, spread ×3, margin và đòn bẩy thực của tài khoản: KHÔNG CÓ.</li>
<li>Nên chạy một lượt MT5 Tester cuối trên kịch bản được chọn, rồi demo / vốn cực nhỏ.</li></ul>
<p class="muted">File: <span class="mono">README_SCENARIOS.md</span> mục 13, <span class="mono">SUMMARY_V3.md</span> mục 23, <span class="mono">results/r6/ROUND8_NOTES.md</span>, <span class="mono">cent_final.json</span>, git nhánh grok/scenarios-v3 (thư mục grok_systems/v3/). Phụ lục từ trang sau: bản tham chiếu vốn 100k (đánh số lại).</p>
</body></html>'''
import re as _re
html=_re.sub(r'(?<=>)(\d+)\.(\d)%',r'\1,\2%',html)
html=_re.sub(r'×(\d+)\.(\d+)',r'×\1,\2',html)
pdf=OUT/'_cent_part.pdf'
HTML(string=html,base_url=str(OUT)).write_pdf(pdf)
final=OUT/'TomTat_KichBan_v2_100USD_cent_2026-11-28.pdf'
subprocess.run(['pdfunite',str(pdf),str(OUT/'TomTat_KichBan_Vang_SP500_2026-11-28.pdf'),str(final)],check=True)
print('wrote',final,final.stat().st_size)
