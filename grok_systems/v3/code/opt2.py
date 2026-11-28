import json,numpy as np
import opt as O, wf as W
O.LCAP.update({'g1':0.12,'g2':0.12,'u10':5.0,'u11':5.0})
res=dict(single=[],port=[])
for k in ('g1','g2','u10','u11'):
    r=O.single(k); res['single'].append(r); print(k,r['lot'],round(r['net']),round(r['dd_pct'],1),round(r['sx_dd_pct'],1),'A',round(r['A']),'B',round(r['B']),r['months'],r['npos'],r['pf_daily'],flush=True)
sets={'NEW4':['g1','g2','u10','u11'],'BASK_div':['x1','x4','g1','g2','u1','u7','u10','u11'],'ALL_pass':['x1','x2','x4','xs1','xs2','g1','g2','u1','u2','u7','u10','u11'],'GOLD_new':['x1','x4','xs1','xs2','g1','g2'],'US_new':['u1','u7','u10','u11']}
for name,ks in sets.items():
    kv,cap=O.optimise(ks); kv=O.roundk(ks,kv); g=0
    while not O.feasible(ks,kv,cap) and g<300:
        g+=1; i=int(np.argmax([kv[j]*O.C[ks[j]]['lot0']*(1 if O.S[ks[j]][0]=='XAU' else 0.1) for j in range(len(ks))])); kv[i]=max(0,kv[i]-O.STEP[O.S[ks[i]][0]]/O.C[ks[i]]['lot0'])
    r=O.evalp(ks,kv,cap); lots={k:round(float(x*O.C[k]['lot0']),3) for k,x in zip(ks,kv)}; r.update(name=name,cap=cap,lots=lots)
    r['safe']=O.evalp(ks,kv*0.5,cap); res['port'].append(r)
    st=W.stress({k:None for k in ks} and ks,lots,cap)
    r['stress']={k:[v[0],v[1]] for k,v in st.items()}
    print(name,lots,round(r['net']),round(r['dd_pct'],1),round(r['sx_dd_pct'],1),'A',round(r['A']),'B',round(r['B']),r['months'],r['pf_daily'],r['sharpe'],'| stress sx3',round(st['sx3+slip1'][1],1),'gap5',round(st['gap5%'][1]),flush=True)
    json.dump(res,open('../results/opt2.json','w'),indent=1,default=float)
print('OPT2 DONE')
