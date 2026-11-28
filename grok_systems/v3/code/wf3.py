import json,numpy as np
import wf as W, opt as O
SETS=json.load(open('../results/wf2.json'))
out={}
for nm,v in SETS.items():
    b=v['base']; cap=v['cap']; ks=list(b); kv0=np.array([b[k]/O.C[k]['lot0'] for k in ks]); out[nm]={}
    for s in (1.0,0.85,0.75,0.6,0.5):
        md=[]; 
        for j in range(2,len(W.ms)):
            sl=W.sl_of([W.ms[j]]); ec,ew,_,_=O.agg(ks,kv0*s,sl); md.append(round(W.ddf(ec,ew)/cap*100,1))
        sl=W.sl_of(W.ms[2:]); ec,ew,sec,sew=O.agg(ks,kv0*s,sl); chain=W.ddf(ec,ew)/cap*100; sxc=W.ddf(sec,sew)/cap*100
        ecf,ewf,secf,sewf=O.agg(ks,kv0*s); out[nm][s]=dict(month_dd=md,oos_chain_dd=round(chain,1),oos_sx2_dd=round(sxc,1),oos_net=round(float(ec[-1]-ec[0])),full_dd=round(W.ddf(ecf,ewf)/cap*100,1),full_net=round(float(ecf[-1])),lots={k:round(b[k]*s,3) for k in ks})
    print(nm,{s:(r['oos_chain_dd'],r['oos_sx2_dd'],r['oos_net'],r['full_dd']) for s,r in out[nm].items()},flush=True)
json.dump(out,open('../results/wf3.json','w'),indent=1)
