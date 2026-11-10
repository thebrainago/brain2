#!/usr/bin/env python3
"""Chạy Cổng 0 hàng loạt khi Anh đã export hist cho mql5_dot2_ids.txt."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

IDS = Path('/workspace/quy_trinh_v3/mql5_dot2_ids.txt')
HIST = Path('/workspace/mql5_hist')
OUT = Path('/workspace/quy_trinh_v3')

def main():
    ids = [ln.strip() for ln in IDS.read_text().splitlines() if ln.strip()]
    have = [i for i in ids if (HIST/f'{i}.csv').exists()]
    miss = [i for i in ids if i not in have]
    print(f'dot2={len(ids)} have_hist={len(have)} missing={len(miss)}')
    if miss:
        (OUT/'mql5_dot2_missing.txt').write_text('\n'.join(miss)+'\n')
        print('missing -> mql5_dot2_missing.txt')
    if not have:
        print('Chưa có file hist — dừng.')
        return
    # Reuse phan_tich style: call analyze via small driver
    sys.path.insert(0, str(OUT))
    from phan_tich_mql5_hist import load_trades, load_phi, xm_cost_price, detect_grid_martingale, EDGE_COST_MIN
    import statistics as st
    from collections import Counter
    rows=[]
    for iid in have:
        tr=load_trades(HIST/f'{iid}.csv')
        if not tr:
            rows.append(dict(id=iid, ket='CHUA_DO', ly='0 trades')); continue
        grid=detect_grid_martingale(tr)
        years=max((max(t.t_close for t in tr)-min(t.t_open for t in tr)).total_seconds()/(365.25*86400),1e-9)
        nets=[]; grosses=[]; costs=[]; miss=Counter()
        for t in tr:
            phi=load_phi(t.symbol)
            if not phi: miss[t.symbol]+=1; continue
            hold=(t.t_close-t.t_open).total_seconds()/86400
            g=t.chieu*(t.price_close-t.price_open)
            sp,sw,cost=xm_cost_price(phi,hold,t.chieu,gia_tham=t.price_open)
            nets.append(g-sp+sw); grosses.append(g); costs.append(cost)
        if len(nets)<max(20,0.5*len(tr)):
            ket,ly='CHUA_DO',f'fee cover {len(nets)}/{len(tr)}'
            net_e=ratio=None
        else:
            net_e=st.mean(nets); cost_e=st.mean(costs); gross_e=st.mean(grosses)
            ratio=gross_e/cost_e if cost_e>1e-15 else float('inf')
            ket='PASS'; ly=''
            if net_e<=0: ket='REJECT'; ly=f'net_E={net_e:.6g}≤0'
            if ratio<EDGE_COST_MIN: ket='REJECT'; ly=(ly+'; ' if ly else '')+f'e/c={ratio:.3f}<{EDGE_COST_MIN}'
        rows.append(dict(id=iid,n=len(tr),years=round(years,2),net_E=round(net_e,6) if net_e is not None else None,
                         edge_cost=round(ratio,3) if ratio is not None else None, ket=ket, ly=ly,
                         grid=grid.get('grid'), mart=grid.get('martingale'),
                         syms=dict(Counter(t.symbol for t in tr).most_common(5))))
    (OUT/'mql5_dot2_cong0.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    pas=[r for r in rows if r['ket']=='PASS']
    print(f"PASS {len(pas)}/{len(rows)}")
    for r in sorted(rows, key=lambda x: -(x.get('edge_cost') or -9))[:15]:
        print(r['id'], r['ket'], 'e/c', r.get('edge_cost'), 'net', r.get('net_E'), 'n', r['n'])

if __name__=='__main__':
    main()
