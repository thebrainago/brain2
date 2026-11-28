import json
V='/workspace/bt_3m/v3'
F=json.load(open(f'{V}/results/r6/cent_final.json')); D=json.load(open(f'{V}/results/r6/direct9.json')); S=json.load(open(f'{V}/results/r6/cent_sens.json'))
BOOK={'JOINT':'Ghép Vàng+SP500','XAU':'Chỉ Vàng','US500':'Chỉ SP500'}
TV={'conservative':'An toàn','balanced':'Cân bằng','aggressive':'Mạnh tay','manual':'Đánh tay (xs1–xs10)'}
def f1(x): return f'{x:,.1f}'.replace(',','.')   # not used for thousands in cent
def row(book,tier,v,tag=''):
    net=v['net']; return f"| {BOOK[book]} | {tier} | {v['nsys']}/{v['nsel']} | +{net:,.0f} USD (+{net*100:,.0f} cent) | {v['dd']:.1f}% | {v['npos']}/6 | {v['gap5']:.0f}% | {v['sx2']:.1f}% |"
L=[]
L+=['## Vòng 8 — vốn 100 USD = 10.000 cent (tài khoản cent)','',
'Bạn sửa vốn: **10k cent = 100 USD**, không phải 100k USD. Phần này tính lại toàn bộ cho tài khoản cent. W (khóa hedge cuối tuần) bật. Số liệu dựa trên deals MT5 100% real ticks đã có (scale tuyến tính theo lot, **chưa chạy lại tester trên server cent**) và engine Python bảo thủ cho gap 5% / spread ×2. Net in USD và cent (×100). Cửa sổ 01/06–27/11/2026.','',
'### 8.1 Thông số hợp đồng đã tra (nguồn web, 28/11/2026)','',
'| Sàn / tài khoản | Vàng | US500 | Nguồn |','|---|---|---|---|',
'| **Exness Standard Cent** | XAUUSDc: 1 lot cent = 0,01 lot chuẩn = **1 oz**; min **0,01 lot cent** (= 0,01 oz); max 200 lot/lệnh; bước lot: KHÔNG CÓ (bài Help Center chỉ nêu min; em giả định 0,01) | **US500c có trên Cent, chỉ MT5 và Exness platform** (không MT4). Contract size US500c: KHÔNG CÓ. Min lot US500c: KHÔNG CÓ (bài Cent ghi chung 0,01 lot). Em giả định 1 lot cent = 0,01 lot chuẩn = 0,01 USD/điểm (US500 chuẩn contract size 1) | Exness Help Center “Standard Cent account” (cập nhật 27/11/2026) get.exness.help/hc/en-us/articles/17537782786588; “Indices” (13/11/2026) get.exness.help/hc/en-us/articles/17854383867548; “Common trading terms” (23/09/2026) |',
'| Exness (mâu thuẫn trong nguồn) | | Cùng bài Indices có 1 dòng ghi “Indices are not offered in Standard Cent accounts”, nhưng mục US500 ngay dưới lại ghi Standard Cent có trên MT5 và bài Cent liệt kê US500c. Em tin mục US500 và bài Cent (mới hơn). **Nên xác nhận trong MT5 của tài khoản thật.** US500 chuẩn: min 0,14 lot, contract size 1, pip 0,1 (không phải thông số cent) | cùng nguồn; ogcashback.com nói “no indices” (bên thứ ba, cũ hơn) |',
'| Exness spread | “từ 0,3 pip” (forex). Spread XAUUSDc / US500c thực tế: KHÔNG CÓ | | Help Center Cent |',
'| **XM Micro** | 1 lot Micro = 1.000 đơn vị, vàng 1 lot = 1 oz; **min 0,1 lot trên MT5** (0,01 lot trên MT4), bước 0,01, max 100 lot | US500Cash có trong danh sách sản phẩm Micro; contract size / min lot Micro của US500Cash: KHÔNG CÓ | xmtrading.com/account-types/micro (FAQ); XM Help Center “minimum lot size for Micro accounts”; fxfan.club |',
'| XM — số dư | **Số dư vẫn tính bằng USD**, XM không có tài khoản “cent” thật (số dư không đổi sang cent). 100 USD = 100 USD | | fxfan.club; xmtrading.com |','',
'**Kết luận:** 10.000 cent chỉ khớp **Exness Standard Cent (USC)**. EA đang chạy theo symbol XM (GOLD / US500Cash) nên khi chuyển sang XAUUSDc / US500c phải đổi symbol, nhập lot theo đơn vị lot cent, và tính lại InpCatLoPct (xem 8.5). Em chưa test EA trên server Exness.','',
'### 8.2 Quy đổi lot 100k → 100 USD','',
'- Vốn nhỏ đi 1.000 lần, lot chuẩn L (vàng 1 lot = 100 oz) → L/1.000 lot chuẩn = **L/10 lot cent** (vàng: 1 lot cent = 1 oz). Với US500c cùng công thức nếu giả định ở 8.1 đúng.',
'- Bước và min lot cent là 0,01 → tương đương bước **0,1 lot chuẩn ở vốn 100k** (thô gấp 10 lần bước 0,01 ở vốn 100k). Hệ nào có lot 100k nhỏ hơn 0,1 thì không đại diện được.',
'- Cách làm tròn trực tiếp: lot quy đổi < 0,01 lot cent thì **loại**; ≥ 0,01 thì làm tròn gần nhất (lệch có thể tới ±30% với lot nhỏ).','',
'### 8.3 Tính lại trực tiếp từ kịch bản 100k (không tối ưu lại)','',
'Hệ bị loại vì lot < 0,01 lot cent: ']
for lab,v in D.items():
    if v.get('drop'): L.append(f"- {lab.replace('_robust','')}: " + ', '.join(f'{k} ({x} lot cent)' for k,x in v['drop'].items()))
L+=['','| Sách | Kịch bản | Số hệ giữ | Net 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD |','|---|---|---|---|---|---|---|---|']
names={'JOINT_100k':'JOINT','XAU_100k':'XAU','US500_100k':'US500'}
for lab,v in D.items():
    if v.get('n',0)==0: continue
    mode=names[lab.split('_GREEDY')[0].split('_MANUAL')[0].rsplit('_',0)[0]] if False else lab.split('_')[0]
    tier={'GREEDY_conservative':'An toàn','GREEDY_balanced':'Cân bằng','GREEDY_aggressive':'Mạnh tay','MANUAL_conservative':'Đánh tay'}['_'.join(lab.split('_')[2:4])]
    net=v['net_usd']; py=v['py']
    L.append(f"| {BOOK[mode]} | {tier} | {v['n']}/{v['n100k']} | +{net:,.0f} USD (+{net*100:,.0f} cent) | {v['dd']:.1f}% | {v['npos']}/6 | {py['gap5']:.0f}% | {py['sx_dd']:.1f}% |")
L+=['','Nhận xét: bỏ hệ nhỏ (g2, x1, g5, g7) làm net giảm 22–26% ở An toàn/Cân bằng ghép (An toàn 96 → 71 USD, Cân bằng 162 → 127 USD); mạnh tay chỉ-vàng làm tròn x1/gp2 từ 0,014 → 0,01 lot cent nên DD tụt 19,3% → 13,9%, lợi nhuận giảm ít (208 → 193 USD).','',
'### 8.4 Kịch bản tối ưu lại trên lưới lot cent (khuyến nghị cho 100 USD)','',
'Tối ưu lại lot trên lưới 0,01 lot cent (cùng ngưỡng DD / spread ×2 / gap 5% như trước: An toàn 10/15/30, Cân bằng 15/22/50, Mạnh tay 19/28/100), rồi kiểm tra lại trên deals MT5. Làm tròn xuống rồi leo từng bước 0,01 trên toàn mẫu nên **có phần in-sample** — nửa A / nửa B của Python đều dương (xem cột bên dưới).','',
'| Sách | Kịch bản | Số hệ | Net 6T | DD MT5 | Tháng + | Gap 5% | Spread ×2 DD |','|---|---|---|---|---|---|---|---|']
for book in ['JOINT','XAU','US500']:
    for t in ['conservative','balanced','aggressive']:
        L.append(row(book,TV[t],F[f'{book}_{t}']))
    if book!='US500': L.append(row(book,TV['manual'],F[f'{book}_manual']))
L+=['','Bậc nhân lot tối đa (DD MT5 ≤ 19,5%; vượt ngưỡng sx2/gap của các bậc trên, cùng loại với bậc ×1,7 / ×5 ở vốn 100k):','',
'| Sách | Kịch bản | Nhân lot | Net 6T | DD MT5 | Gap 5% | Spread ×2 DD |','|---|---|---|---|---|---|---|']
for k,n in [('JOINT_aggressive_max','Ghép — Mạnh tay'),('XAU_aggressive_max','Chỉ Vàng — Mạnh tay'),('JOINT_manual_max','Ghép — Đánh tay'),('XAU_manual_max','Chỉ Vàng — Đánh tay')]:
    v=F[k]; L.append(f"| {n} | | ×{v['f']:.2f} | +{v['net']:,.0f} USD (+{v['net']*100:,.0f} cent) | {v['dd']:.1f}% | {v['gap5']:.0f}% | {v['sx2']:.1f}% |")
L+=['','**Gap 5% từ 100% trở lên nghĩa là một cú gap 5% trong phiên có thể xóa hết 100 USD** (stop-out 0% của Exness Cent cắt ở 0, nhưng vốn mất sạch). Kịch bản Mạnh tay và mọi bậc ×lot đều ở vùng này.','',
'Lot từng hệ (đơn vị **lot cent**, vàng 1 lot cent = 1 oz; US500c theo giả định ở 8.1):','','| Hệ | An toàn | Cân bằng | Mạnh tay | Mạnh tay max |','|---|---|---|---|---|']
for book in ['JOINT','XAU','US500']:
    L.append(f'| **{BOOK[book]}** | | | | |')
    ks=[]
    for t in ['conservative','balanced','aggressive']:
        for k in F[f'{book}_{t}']['cent']:
            if k not in ks: ks.append(k)
    for k in F[f'{book}_conservative']['dropped']+F[f'{book}_balanced']['dropped']+F[f'{book}_aggressive']['dropped']:
        if k not in ks: ks.append(k)
    for k in ks:
        cells=[]
        for t in ['conservative','balanced','aggressive']:
            c=F[f'{book}_{t}']['cent'].get(k); cells.append(f'{c:.2f}' if c else 'loại')
        mx=F.get(f'{book}_aggressive_max'); c=mx['cent'].get(k) if mx else None
        cells.append(f'{c:.2f}' if c else ('loại' if mx else '—'))
        L.append(f'| {k} | '+' | '.join(cells)+' |')
L+=['','Lot Đánh tay (lot cent): ' + '; '.join(f"{k} {v:.2f}" for k,v in F['XAU_manual']['cent'].items()),'']
L+=['### 8.5 Hệ quả cho tài khoản 100 USD','',
'- **Ít hệ hơn:** ở An toàn/Cân bằng ghép chỉ còn 12–14/15 hệ; chỉ-vàng còn 6–7/8. SP500 giữ 5/5 vì lot US500 lớn hơn nhiều so với min (nếu giả định US500c đúng).',
'- **Lot thô:** bước 0,01 lot cent tương đương 1 oz × 0,01. Hệ lot cent 0,01–0,03 chịu sai số làm tròn lớn; chỉ cần lệch 1 bước là đổi 30–100% lot của hệ đó. Nên chạy demo/real cực nhỏ trước.',
'- **XM Micro MT5 (min 0,1 lot = 0,1 oz) không dùng được:** chỉ còn 3/15 hệ ghép ở mọi bậc (đều là hệ SP500; hệ vàng cần lot 100k ≥ 1,0), chỉ-vàng 0/8 ở An toàn/Cân bằng và 2/8 ở Mạnh tay, Đánh tay 0/10. MT4 Micro (min 0,01) thì giống Exness nhưng EA này là MT5.',
'- **Rủi ro US500c:** nếu min lot US500c trên Exness là 0,14 lot cent (như US500 chuẩn ghi min 0,14) thì vẫn đủ cho 5/5 hệ SP500 ở mọi bậc (lot nhỏ nhất ≥ 0,40); nếu contract size khác 0,01 USD/điểm thì mọi lot SP500 phải tính lại. KHÔNG CÓ số chính thức nên cần kiểm tra Specification trong MT5.',
'- **Spread cent thường rộng hơn:** backtest dùng spread thật của XM. Cột Spread ×2 DD là giả lập spread gấp đôi (+ trượt giá); spread ×3 hoặc spread thực Exness cent: KHÔNG CÓ (chưa tính). Với net trung bình mỗi hệ rất nhỏ so với spread, nên coi bản Cân bằng là giới hạn.',
'- **InpCatLoPct (scalp, vàng):** = SL_giá × lot_cent × 1 oz ÷ vốn USD × 100. Ví dụ SL $10, 0,05 lot cent, vốn 100 USD → 0,5% vốn. Cần tính lại cho từng hệ scalp xs*.',
'- **Margin:** KHÔNG CÓ kiểm tra margin. Vị thế vàng vài chục 0,01 oz ≈ vài chục USD notional nên margin nhỏ ở đòn bẩy cao, nhưng đòn bẩy thực tế phụ thuộc tài khoản.',
'- Chưa chạy MT5 Tester lại trên 100 USD; nên chạy 1 lượt Tester cuối cho kịch bản được chọn.','']
open(f'{V}/results/r6/ROUND8_NOTES.md','w').write('\n'.join(L))
print(len(L))
