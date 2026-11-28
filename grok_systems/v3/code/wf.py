import sys,os,json,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import opt as O, bt, lotscale as LS
V=O.V; idx=O.idx; n=O.n
X={k:pickle.load(open(f'{LS.CD_}/{k}_x.pkl','rb')) for k in O.S}
def al(s,ix): return pd.Series(s,index=ix).reindex(idx).ffill().fillna(0).values
XC={k:dict(sx3=al(o['sx3'][0],o['index']),sx3w=al(o['sx3'][1],o['index']),sx2s=al(o['sx2s'][0],o['index']),sx2sw=al(o['sx2s'][1],o['index']),nl=al(o['nl'],o['index']),px=al(o['px'],o['index'])) for k,o in X.items()}
PV=bt.SPEC
def ddf(ec,ew): return float(np.max(np.maximum.accumulate(ec)-ew))
def stress(ks,lots,cap):
    kv=np.array([lots[k]/O.C[k]['lot0'] for k in ks]); r={}
    ec,ew,sec,sew=O.agg(ks,kv); r['base']=(float(ec[-1]),ddf(ec,ew)/cap*100); r['sx2']=(float(sec[-1]),ddf(sec,sew)/cap*100)
    e=sum(kv[i]*XC[k]['sx2s'] for i,k in enumerate(ks)); w=sum(kv[i]*XC[k]['sx2sw'] for i,k in enumerate(ks)); r['sx2+slip1']=(float(e[-1]),ddf(e,w)/cap*100)
    e3=sum(kv[i]*XC[k]['sx3'] for i,k in enumerate(ks)); w3=sum(kv[i]*XC[k]['sx3w'] for i,k in enumerate(ks)); r['sx3+slip1']=(float(e3[-1]),ddf(e3,w3)/cap*100)
    for Xg in (0.05,0.10,0.20):
        up={'XAU':0,'US500':0}; dn={'XAU':0,'US500':0}
        for i,k in enumerate(ks):
            a=O.S[k][0]; pv=PV[a]['pv']; nl=XC[k]['nl']*kv[i]
            up[a]=up[a]+np.maximum(-nl,0)*pv*XC[k]['px']*Xg; dn[a]=dn[a]+np.maximum(nl,0)*pv*XC[k]['px']*Xg
        best=0
        import itertools
        assets=[a for a in ('XAU','US500') if not np.isscalar(up[a])]
        for combo in itertools.product((0,1),repeat=len(assets)):
            loss=sum((up if c==0 else dn)[a] for a,c in zip(assets,combo)); best=max(best,ddf(ec,ew-loss)/cap*100)
        r[f'gap{int(Xg*100)}%']=(None,best)
    return r
def tune_scale(ks,base,cap,sl,dd_t=0.17,sx_t=0.25):
    kv0=np.array([base[k]/O.C[k]['lot0'] for k in ks]); lo,hi=0.0,8.0
    def ok(s):
        ec,ew,sec,sew=O.agg(ks,kv0*s,sl); return ddf(ec,ew)<=dd_t*cap and ddf(sec,sew)<=sx_t*cap
    for _ in range(22):
        m=(lo+hi)/2
        if ok(m): lo=m
        else: hi=m
    return lo
mon=idx.strftime('%Y-%m'); ms=sorted(set(mon)); msl={m:np.nonzero(mon==m)[0] for m in ms}
def sl_of(months): i=np.concatenate([msl[m] for m in months]); return slice(i[0],i[-1]+1)
def wf(ks,base,cap):
    kv0=np.array([base[k]/O.C[k]['lot0'] for k in ks]); rows=[]; chain=0.0; pk=0.0; worst=0.0
    for j in range(2,len(ms)):
        s=tune_scale(ks,base,cap,sl_of(ms[j-2:j])); sl=sl_of([ms[j]])
        ec,ew,sec,sew=O.agg(ks,kv0*s,sl); dd_m=ddf(ec,ew)/cap*100; net_m=float(ec[-1]-ec[0])
        # chain: equity relative continuing
        eqw=chain+(ew-ec[0]); eqc=chain+(ec-ec[0]); pk=max(pk,eqc.max()) if False else max(pk,chain); 
        pkn=max(pk,float(np.max(np.maximum.accumulate(eqc)))); worst=max(worst,float(np.max(np.maximum.accumulate(np.maximum(eqc,pk))-eqw)))
        chain=float(eqc[-1]); pk=max(pk,float(eqc.max()))
        rows.append(dict(month=ms[j],s=round(s,2),test_net=round(net_m),test_dd_pct=round(dd_m,1)))
    return rows,chain,worst/cap*100
if __name__=='__main__':
    SETS={'PortA':({'x1':0.09,'x2':0.10,'u1':1.0,'u7':1.0},40000),'PortB':({'x1':0.05,'x4':0.07,'xs1':0.57,'xs2':1.0,'u1':2.6,'u2':0.2,'u6':2.8,'u7':5.0},40000),
      'x1':({'x1':0.09},30000),'x2':({'x2':0.10},30000),'x4':({'x4':0.04},30000),'xs1':({'xs1':0.57},30000),'xs2':({'xs2':0.6},30000),'u1':({'u1':2.6},10000),'u6':({'u6':2.8},10000),'u7':({'u7':3.0},10000),
      'GOLD_bsk':({'x1':0.09,'x2':0.10,'x4':0.04,'xs1':0.57,'xs2':0.6},30000),'US_core':({'u1':2.6,'u2':0.2,'u6':2.8,'u7':3.0},10000)}
    res={}
    for nm,(lots,cap) in SETS.items():
        ks=list(lots); st=stress(ks,lots,cap); rows,chain,worst=wf(ks,lots,cap)
        s_min=min(r['s'] for r in rows); s_rob=min(1.0,s_min)
        kv0=np.array([lots[k]/O.C[k]['lot0'] for k in ks]); ec,ew,sec,sew=O.agg(ks,kv0*s_rob); rob=(float(ec[-1]),ddf(ec,ew)/cap*100,ddf(sec,sew)/cap*100)
        res[nm]=dict(lots=lots,cap=cap,stress={k:[v[0],v[1]] for k,v in st.items()},wf=rows,wf_chain_net=chain,wf_chain_dd=worst,s_rob=s_rob,rob_net=rob[0],rob_dd=rob[1],rob_sx2dd=rob[2],rob_lots={k:round(v*s_rob,3) for k,v in lots.items()})
        print(nm,'stress',{k:(None if v[0] is None else round(v[0]),round(v[1],1)) for k,v in st.items()}); print('   wf',rows,'chain',round(chain),round(worst,1),'s_rob',round(s_rob,2),'robnet',round(rob[0]),round(rob[1],1),flush=True)
        json.dump(res,open(f'{V}/results/stress_wf.json','w'),indent=1,default=float)
    print('WF DONE')
