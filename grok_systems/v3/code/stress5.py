import json,numpy as np,p5,r5lib as R,bt,opt5 as O
W=dict(flat=2,hsk=0.0,hs=0.0,dl=0.0,minusN=0); B0=dict(flat=0,hsk=0.0,hs=0.0,dl=0.0,minusN=0)
PORTS={'PortA':({'x1':.09,'x2':.10,'u1':1.0,'u7':1.0},B0),'PortA_W':({'x1':.09,'x2':.10,'u1':1.0,'u7':1.0},W),
 'PortB85':({'x1':.04,'x4':.06,'xs1':.48,'xs2':.85,'u1':2.2,'u2':.17,'u6':1.4,'u7':4.25},B0),'PortB85_W':({'x1':.04,'x4':.06,'xs1':.48,'xs2':.85,'u1':2.2,'u2':.17,'u6':1.4,'u7':4.25},W),
 'NEW4_W':({'g1':.12,'g2':.12,'u10':2.5,'u11':2.0},W),
 'PortD_G30_W':({'x1':.04,'x4':.03,'g1':.04,'g2':.03,'xs1':.6,'xs2':.95,'u1':1.0,'u2':.3,'u6':1.0,'u7':1.6,'u10':1.8,'u11':.4},W),
 'PortD_G40_W':({'x1':.06,'x4':.04,'g1':.06,'g2':.04,'xs1':.58,'xs2':1.0,'u1':1.1,'u2':.3,'u6':1.0,'u7':3.1,'u10':1.6,'u11':.6},W)}
def ddf(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
out={}
for nm,(lots,pol) in PORTS.items():
    cap=sum(p5.CAP[a] for a in {R.S[k][0] for k in lots}); res={}
    for lab,(sm,sl) in {'base':(1.0,0.5),'sx2s1':(2.0,1.0),'sx3s1':(3.0,1.0),'sx2s2':(2.0,2.0)}.items():
        ec=0;ew=0
        for k,l in lots.items():
            a=R.S[k][0]
            if k in p5.SCV:
                o,x=p5.SCV[k]; f=l/o['lot']
                if lab=='base': e=p5.al(o['base'][0],o['index']); w=p5.al(o['base'][1],o['index'])
                elif lab=='sx3s1': e=p5.al(x['sx3'][0],x['index']); w=p5.al(x['sx3'][1],x['index'])
                else: e=p5.al(x['sx2s'][0],x['index']); w=p5.al(x['sx2s'][1],x['index'])
                ec=ec+f*e; ew=ew+f*w
            else:
                D=p5.Dt[a]; r=R.run2(k,D,p5.FL[a][pol['flat']],sprmul=sm,slip=sl,lot=l); ec=ec+p5.al(r['ec'],D.index); ew=ew+p5.al(r['ew'],D.index)
        res[lab]=dict(net=float(ec[-1]),dd=ddf(ec,ew)/cap*100)
    out[nm]=res; print(nm,{k:(round(v['net']),round(v['dd'],1)) for k,v in res.items()},flush=True)
json.dump(out,open('../results/r5/stress5.json','w'),indent=1)
