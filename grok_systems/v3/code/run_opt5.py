import sys,os,json,numpy as np,opt5 as O,p5
SETS={'PortB_sys':['x1','x4','xs1','xs2','u1','u2','u6','u7'],'NEW4':['g1','g2','u10','u11'],
 'PortD_sys':['x1','x4','g1','g2','xs1','xs2','u1','u2','u6','u7','u10','u11'],'GOLD_D':['x1','x4','g1','g2','xs1','xs2'],'US_D':['u1','u2','u6','u7','u10','u11'],'PortA_sys':['x1','x2','u1','u7']}
POLS={'base':dict(flat=0,hsk=0.0,hs=0.0,dl=0.0,minusN=0),'W':dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0),'W_mN':dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=1)}
f='../results/r5/opt5_%s.json'%('_'.join(sys.argv[1:2]) or 'all'); res=json.load(open(f)) if os.path.exists(f) else {}
cons={'dd17sx25':dict(use_gap=False),'gap40':dict(use_gap=True,GT=0.40,WT=0.30),'gap30':dict(use_gap=True,GT=0.30,WT=0.25),'gap25':dict(use_gap=True,GT=0.25,WT=0.22)}
only=sys.argv[1:] 
for sn,ks in SETS.items():
    if only and sn not in only: continue
    for pn,pol in POLS.items():
        for cn,ckw in cons.items():
            key=f'{sn}|{pn}|{cn}'
            if key in res: continue
            if pn=='base' and cn not in ('dd17sx25','gap30'): continue
            P=O.Port(ks,pol); kv=O.optimise(P,**ckw); r=P.met(kv,full=True); r['lots']={k:round(float(f*u['lot0']),3) for k,f,u in zip(ks,kv,P.U)}
            half=P.met(kv*0.5,full=True); r['half']={k:half[k] for k in ('net','dd','sx_dd','gap5','wk10')}
            res[key]=r; json.dump(res,open(f,'w'),default=float)
            print(key,r['lots'],'net',round(r['net']),'dd',round(r['dd'],1),'sx',round(r['sx_dd'],1),'gap5',round(r['gap5'],1),'wk10',round(r['wk10'],1),'A/B',round(r['A']),round(r['B']),r['npos'],flush=True)
print('OPT5 DONE')
