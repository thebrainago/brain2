import json
r=json.load(open('/workspace/bt_3m/v3/results/opt_results.json'))
NAME={'x1':'XAU sweep_fade 15m ADX>20 LDNY (gap8 N4 TP4 không hedge)','x2':'XAU sweep_fade c3 hedge','x4':'XAU dz_fade_15 LDN','x5':'XAU sweep+VWAP W30','xs1':'XAU scalp xlead_fadeself+big2_mom (SL8 TP8)','xs2':'XAU scalp big3_mom+emapull NY (SL8 TP13)',
 'u1':'US500 sweep_fade LDNY (gap60 N3 TP6)','u2':'US500 absorb_fade_5 NY (gap60 N4 TP8)','u3':'US500 sweep+absorb W30 NY (gap30 N3 TP4)','u5':'US500 v2_c1 hedge','u6':'US500 dz_mom_5_1.5 (mới)','u7':'US500 sweep_fade_15_1.5 all (mới)','u8':'US500 stk_fade_15_2 LDNY (mới, chỉ short)','u9':'US500 imb_mom_15_1.5 LDNY (mới)'}
L=['## 13. LOT-SCALE từng hệ (Python bảo thủ, DD<17% vốn, spread×2 DD<25%; XAU vốn 30k, US500 vốn 10k; tuyến tính theo lot rồi làm tròn bước lot)',
'| Hệ | Lot L0 | Net 6th | DD | DD spread×2 | Net spread×2 | A (6/1–19/8) | B (20/8–26/11) | tháng+ | PF ngày |','|---|---|---|---|---|---|---|---|---|---|']
for x in r['single']:
    L.append(f"| {x['sys']} {NAME[x['sys']]} | {x['lot']} | {x['net']:,.0f} | {x['dd_pct']:.1f}% | {x['sx_dd_pct']:.1f}% | {x['sx_net']:,.0f} | {x['A']:,.0f} | {x['B']:,.0f} | {x['npos']}/6 | {x['pf_daily']} |")
L+=['','Lưu ý: scalp xs1/xs2 trong Python chỉ tính DD theo lệnh đóng (không có DD trong lệnh) nên LẠC QUAN; số thật lấy theo MT5 (mục 15). Giới hạn lot an toàn gap: gold L0≤0.12, US500 ≤5 (u3 ≤8).','',
'## 14. DANH MỤC chéo/song song tối ưu lot (DD joint<17%, sx2<25%; vốn = 30k gold + 10k US500 nếu có cả hai)',
'| Danh mục | Lot từng hệ | Net | DD | DD sx2 | Net sx2 | A / B | Net theo tháng | PF ngày / Sharpe | Mức an toàn ½ lot: Net / DD | OOS: lot tối ưu trên A → B net / DD | lot tối ưu trên B → A net / DD |','|---|---|---|---|---|---|---|---|---|---|---|---|']
for x in r['port']:
    lots=', '.join(f"{k}:{v}" for k,v in x['lots'].items() if v>0)
    L.append(f"| {x['name']} (vốn {x['cap']:,.0f}) | {lots} | {x['net']:,.0f} | {x['dd_pct']:.1f}% | {x['sx_dd_pct']:.1f}% | {x['sx_net']:,.0f} | {x['A']:,.0f} / {x['B']:,.0f} | {x['months']} | {x['pf_daily']} / {x['sharpe']} | {x['safe']['net']:,.0f} / {x['safe']['dd_pct']:.1f}% | {x['oos']['B_net']:,.0f} / {x['oos']['B_dd_pct']:.1f}% | {x['oos2']['A_net']:,.0f} / {x['oos2']['A_dd_pct']:.1f}% |")
L+=['','**CẢNH BÁO OOS**: lot tối ưu chỉ trên giai đoạn A (01/06–19/08, DD thấp) khi áp sang B (20/08–26/11) cho DD 40–56% với danh mục có vàng — DD "17%" phụ thuộc mạnh vào giai đoạn; lot tối ưu trên B áp sang A an toàn (DD 6–21%). Khuyến nghị dùng mức ½ lot (DD ~8%) cho tiền thật/demo ban đầu; mức 17% chỉ là trần mô phỏng.']
open('/workspace/bt_3m/v3/SUMMARY_LOT_part.md','w').write('\n'.join(L)); print('\n'.join(L)[:300])
