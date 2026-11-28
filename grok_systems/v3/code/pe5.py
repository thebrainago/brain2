import numpy as np,json,opt5 as O,p5,r5lib as R
O.LC.update({'u6':1.0,'u2':0.5,'u1':3.9,'x1':0.09,'x4':0.06,'g1':0.12,'g2':0.12,'u10':2.5,'u11':2.0,'u7':5.0,'xs1':0.6,'xs2':1.0,'g3':0.06,'g4':0.09,'u12':3.0})
ks=['x1','x4','g1','g2','g3','g4','xs1','xs2','u1','u2','u6','u7','u10','u11','u12']
W=dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
P=O.Port(ks,W)
FL={'x1':.02,'x4':.01,'g1':.03,'g2':.03,'g3':.02,'g4':.03,'xs1':.15,'xs2':.3,'u1':.5,'u2':.1,'u6':.3,'u7':.8,'u10':.5,'u11':.4,'u12':.6}
mn=np.array([FL[k]/u['lot0'] for k,u in zip(ks,P.U)])
out={}
for tag,kw in {'gap30':dict(GT=.30,WT=.40),'gap40':dict(GT=.40,WT=.50)}.items():
    kv=O.optimise(P,mn=mn,**kw); r=P.met(kv,full=True); r['lots']={k:round(float(f*u['lot0']),3) for k,f,u in zip(ks,kv,P.U)}
    h=P.met(kv*0.5,full=True); r['half']={k:h[k] for k in ('net','dd','sx_dd','gap5','wk10','A','B')}
    out[tag]=r; print(tag,r['lots'],'net',round(r['net']),'dd',round(r['dd'],1),'sx',round(r['sx_dd'],1),'gap5',round(r['gap5'],1),r['gap5_asset'],'wk10',round(r['wk10'],1),'A/B',round(r['A']),round(r['B']),r['npos'],'half',round(h['net']),round(h['dd'],1),round(h['gap5'],1),flush=True)
    json.dump(out,open('../results/r5/pe5.json','w'),default=float)
