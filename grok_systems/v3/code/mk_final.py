import json,glob,sys
sys.argv=['x']
import numpy as np,opt as O
rows=[]
for f in ('r4','r6'):
    for l in open(f'../results/{f}.jsonl'):
        l=l[l.index('{'):] if l.lstrip().startswith('E:') or not l.startswith('{') else l
        rows.append(json.loads(l))
# dedupe: keep last of name
R={}
for r in rows: R[r['name']]=r
# pull v3c from PC later if missing
base={'x1':'x1','x2':'x2','x4':'x4','xs1':'xs1','xs2':'xs2','u1':'u1','u2':'u2','u6':'u6','u7':'u7'}
L=['## 15. MT5 TICK-REAL cho các hệ đã scale lot (100% real ticks, 01/06–27/11/2026; XAU vốn 30k, US500 vốn 10k)',
'| Job | Hệ | Lot | MT5 net | MT5 DD | PF | trades | Python net (tuyến tính theo lot) | Python DD |','|---|---|---|---|---|---|---|---|---|']
import re
for n in sorted(R):
    r=R[n]; m=re.match(r'v3b_[ABCS]_([a-z0-9]+)_',n); s=m.group(1); lot=r['params']['InpLot0']
    k=lot/O.C[s]['lot0']; pn=k*O.C[s]['ec'][-1]; ec,ew,_,_=O.agg([s],[k]); pdd=O.dd(ec,ew)/O.CAP[O.S[s][0]]*100
    L.append(f"| {n} | {s} | {lot} | {r['net']:,.0f} | {r['eq_dd_pct']}% | {r['pf']} | {r['trades']} | {pn:,.0f} | {pdd:.1f}% |")
open('../SUMMARY_MT5_part.md','w').write('\n'.join(L)); print('\n'.join(L))
