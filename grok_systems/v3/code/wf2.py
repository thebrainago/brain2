import sys,json,numpy as np
import wf as W, opt as O
V=W.V
def run(ks,base,cap,dd_t):
    sx_t=dd_t*25/17; kv0=np.array([base[k]/O.C[k]['lot0'] for k in ks]); chain=0.0; pk=0.0; worst=0.0; rows=[]
    for j in range(2,len(W.ms)):
        s=W.tune_scale(ks,base,cap,W.sl_of(W.ms[j-2:j]),dd_t,sx_t); sl=W.sl_of([W.ms[j]])
        ec,ew,_,_=O.agg(ks,kv0*s,sl); eqc=chain+(ec-ec[0]); eqw=chain+(ew-ec[0])
        run_pk=np.maximum.accumulate(np.maximum(eqc,pk)); worst=max(worst,float(np.max(run_pk-eqw))); pk=max(pk,float(eqc.max())); chain=float(eqc[-1])
        rows.append((W.ms[j],round(s,2),round(float(ec[-1]-ec[0])),round(W.ddf(ec,ew)/cap*100,1)))
    s_dec=W.tune_scale(ks,base,cap,W.sl_of(W.ms[-2:]),dd_t,sx_t)
    return dict(dd_t=dd_t,chain_net=chain,chain_dd=worst/cap*100,rows=rows,s_dec=s_dec,dec_lots={k:round(base[k]*s_dec,3) for k in ks},posmonths=sum(1 for r in rows if r[2]>0))
if __name__=='__main__':
    SETS={'PortA':({'x1':0.09,'x2':0.10,'u1':1.0,'u7':1.0},40000),'PortB':({'x1':0.05,'x4':0.07,'xs1':0.57,'xs2':1.0,'u1':2.6,'u2':0.2,'u6':2.8,'u7':5.0},40000),
      'x1':({'x1':0.09},30000),'x2':({'x2':0.10},30000),'x4':({'x4':0.04},30000),'xs1':({'xs1':0.57},30000),'xs2':({'xs2':0.6},30000),'u1':({'u1':2.6},10000),'u6':({'u6':2.8},10000),'u7':({'u7':3.0},10000)}
    res={}
    for nm,(b,cap) in SETS.items():
        best=None
        for t in (0.17,0.15,0.13,0.11,0.09,0.07,0.05):
            r=run(list(b),b,cap,t)
            if r['chain_dd']<=20.0: best=r; break
        res[nm]=dict(base=b,cap=cap,pick=best); 
        print(nm,None if not best else (best['dd_t'],round(best['chain_net']),round(best['chain_dd'],1),best['rows'],best['dec_lots']),flush=True)
        json.dump(res,open(f'{V}/results/wf2.json','w'),indent=1,default=float)
    print('WF2 DONE')
