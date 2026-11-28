# MT5 joint equity for opt8 scenarios (linear scaling of existing per-system MT5 deals).
# Lot rounding: XAU 0.01, US500 0.1. If a book's MT5 DD > 19.5%, shrink lots and keep the raw book as *_raw.
import json,joint5 as J
from joint7 import RUN
def rndlot(k,x):
    return round(x+1e-12,1) if k.startswith('u') else round(x+1e-12,2)
def mt5(lots,lab,cap):
    names=[RUN[k][0] for k in lots]; sc={RUN[k][0]:lots[k]/RUN[k][1] for k in lots}
    r=J.joint(names,sc,lab,cap=cap); h=J.joint(names,{n:v*0.5 for n,v in sc.items()},lab,cap=cap)
    r['half']=dict(net=h['net'],dd_pct=h['dd_pct']); r['lots']=lots; r['cap']=cap; return r
if __name__=='__main__':
    O=json.load(open('../results/r6/opt8.json')); out={}
    def pr(lab,r):
        print(lab,'cap',r['cap'],'net',round(r['net']),'dd',round(r['dd_pct'],1),'A/B',round(r['A']),round(r['B']),'m+',r['npos'],'half',round(r['half']['net']),round(r['half']['dd_pct'],1),flush=True)
    for mode,blk in O.items():
        cap=blk['cap']
        for key,v in blk.items():
            if not isinstance(v,dict) or 'robust' not in v: continue
            l={k:rndlot(k,x) for k,x in v['robust']['lots'].items()}
            if not l: continue
            lab=f'{mode}_{key}_robust'
            r=mt5(l,lab,cap)
            if r['dd_pct']>19.5:
                out[lab+'_raw']=dict(r); pr(lab+'_raw',r)
                lo,hi=0.5,1.0; best=None
                for _ in range(16):
                    mm=(lo+hi)/2
                    lm={k:rndlot(k,x*mm) for k,x in l.items()}
                    rr=mt5(lm,lab+'_fit',cap)
                    if rr['dd_pct']<=19.5: lo=mm; best=(mm,lm,rr)
                    else: hi=mm
                mm,lm,rr=best; rr['scale_from_robust']=mm; rr['lots']=lm
                r=rr
            out[lab]=r; pr(lab,r)
            multipliers = (1.2,1.4,1.5,1.7,2.0,2.5) if 'aggressive' in key else ((2,2.5,3,4,5) if 'MANUAL' in key else ())
            for m in multipliers:
                lm={k:rndlot(k,x*m) for k,x in r['lots'].items()}
                rr=mt5(lm,f'{lab}_x{m}',cap)
                if rr['dd_pct']>19.5: break
                out[f'{lab}_x{m}']=rr; pr(f'{lab}_x{m}',rr)
    json.dump(out,open('joint8.json','w'),indent=1)
    print('WROTE joint8.json',len(out),'rows',flush=True)
