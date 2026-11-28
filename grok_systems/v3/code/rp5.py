import numpy as np,json,opt5 as O,p5
L={'x1':.09,'x4':.05,'g1':.12,'g2':.12,'xs1':.57,'xs2':1.0,'u1':3.8,'u2':.3,'u6':1.4,'u7':3.0,'u10':2.5,'u11':2.0}
W=dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
ks=list(L); P=O.Port(ks,W); base=np.array([L[k]/u['lot0'] for k,u in zip(ks,P.U)])
def okf(f,GT,WT,DDT=.17,SXT=.25):
    kv=base*f; m=P.met(kv); return m['dd']<=DDT*100 and m['sx_dd']<=SXT*100 and m['gap5']<=GT*100 and m['wk10']<=WT*100,m
out={}
for tag,(GT,WT) in {'gap30':(.30,.40),'gap40':(.40,.50),'none':(9,9)}.items():
    lo,hi=0.0,1.5
    for _ in range(14):
        m_=(lo+hi)/2
        if okf(m_,GT,WT)[0]: lo=m_
        else: hi=m_
    kv=base*lo; lots={k:round(float(x*u['lot0']),3) for k,x,u in zip(ks,kv,P.U)}
    # round to steps
    lots={k:(round(l/O.STEP[P.U[i]['a']])*O.STEP[P.U[i]['a']]) for i,(k,l) in enumerate(lots.items())}
    kv2=np.array([lots[k]/u['lot0'] for k,u in zip(ks,P.U)]); r=P.met(kv2,full=True); r['f']=lo; r['lots']=lots
    out[tag]=r; print(tag,round(lo,3),lots,'net',round(r['net']),'dd',round(r['dd'],1),'sx',round(r['sx_dd'],1),'gap5',round(r['gap5'],1),r['gap5_asset'],'wk10',round(r['wk10'],1),'A/B',round(r['A']),round(r['B']),r['npos'],flush=True)
json.dump(out,open('../results/r5/rp5.json','w'),default=float)
