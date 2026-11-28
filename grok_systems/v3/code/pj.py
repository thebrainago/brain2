import json,numpy as np,opt as O
sets={'PortA':{'x1':0.09,'x2':0.10,'u1':1.0,'u7':1.0},'PortB':{'x1':0.05,'x4':0.07,'xs1':0.57,'xs2':1.0,'u1':2.6,'u2':0.2,'u6':2.8,'u7':5.0},'PortC':{'x1':0.09,'x2':0.10,'x4':0.04,'xs1':0.57,'xs2':0.6,'u1':2.6,'u2':0.2,'u6':2.8,'u7':3.0},
 'PortC_gold':{'x1':0.09,'x2':0.10,'x4':0.04,'xs1':0.57,'xs2':0.6},'PortC_us':{'u1':2.6,'u2':0.2,'u6':2.8,'u7':3.0}}
out={}
for n,l in sets.items():
    ks=list(l); kv=np.array([l[k]/O.C[k]['lot0'] for k in ks]); r=O.evalp(ks,kv,O.capof(ks)); r['lots']=l; r['cap']=O.capof(ks); out[n]=r
    print(n,round(r['net']),round(r['dd_pct'],1),round(r['sx_dd_pct'],1),round(r['sx_net']),round(r['A']),round(r['B']),r['months'],r['pf_daily'],r['sharpe'])
json.dump(out,open('../results/port_abc.json','w'),indent=1)
