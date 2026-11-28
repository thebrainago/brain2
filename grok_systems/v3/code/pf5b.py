import json,numpy as np,opt5 as O,p5
O.LC.update({'g3':.06,'g4':.09,'g5':.04,'u12':3.0,'u13':3.0})
W=dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
G30={'x1':.04,'x4':.03,'g1':.04,'g2':.03,'xs1':.6,'xs2':.95,'u1':1.0,'u2':.3,'u6':1.0,'u7':1.6,'u10':1.8,'u11':.4}
NEWL={'g3':.06,'g4':.09,'g5':.04,'u12':3.0,'u13':3.0}
sets={'PortE(G30+g3,g5,u12,u13)':{**G30,'g3':.06,'g5':.04,'u12':3.0,'u13':3.0},'PortE_half':{**{k:v/2 for k,v in G30.items()},'g3':.03,'g5':.02,'u12':1.5,'u13':1.5},'PortD_G30':G30,'PortD_G30+new5':{**G30,**NEWL},'PortD_G30+new5_half':{**G30,**{k:v/2 for k,v in NEWL.items()}},'PortD_G30+u12u13':{**G30,'u12':3.0,'u13':3.0}}
out={}
for nm,l in sets.items():
    ks=list(l); P=O.Port(ks,W); kv=np.array([l[k]/u['lot0'] for k,u in zip(ks,P.U)]); r=P.met(kv,full=True); h=P.met(kv*0.5,full=True)
    r['half']={k:h[k] for k in ('net','dd','gap5','wk10')}; out[nm]=r
    print(nm,'net',round(r['net']),'dd',round(r['dd'],1),'sx2',round(r['sx_dd'],1),'gap5',round(r['gap5'],1),r['gap5_asset'],'wk10',round(r['wk10'],1),'A/B',round(r['A']),round(r['B']),r['npos'],'half',round(h['net']),round(h['dd'],1),round(h['gap5'],1),flush=True)
json.dump(out,open('../results/r5/pf5b.json','w'),default=float)
