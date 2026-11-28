import sys, os, json, numpy as np, pandas as pd, itertools
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt, scalp as SC, cands as CD, mt5prep as M
X=lambda a,adx,se,b=None,W=0:dict(kind='single' if b is None else 'pair',a=a,b=b,W=W,adx=adx,sess=se)
mgx=dict(c3=dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30),nh8=dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30))
mgu=dict(u1=dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30),u2=dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30),
 u3=dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30),c1=dict(L0=2.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=1.5,hedge=1,hgap=90,hr=0.5,htp=5.0,cd=30))
SYS=[('x1','XAU',X('sw_fade_15_1.8','gt20','ldny'),mgx['nh8']),('x2','XAU',X('sw_fade_15_1.8','gt20','ldny'),mgx['c3']),('x3','XAU',X('imb_fade_15_1.5','gt20','ldn'),mgx['nh8']),
 ('x4','XAU',X('dz_fade_15_2.0','none','ldn'),mgx['nh8']),('x5','XAU',X('sw_fade_15_1.8','gt20','all','vwapatr_3',30),mgx['nh8']),
 ('u1','US500',X('sw_fade_15_1.8','gt20','ldny'),mgu['u1']),('u2','US500',X('absorb_fade_5_1.5_1.0','none','ny'),mgu['u2']),
 ('u3','US500',X('sw_fade_15_1.8','gt20','ny','absorb_fade_5_1.5_1.0',30),mgu['u3']),('u5','US500',X('sw_fade_15_1.8','gt20','ldny'),mgu['c1'])]
CAP={'XAU':30000.,'US500':10000.}
if __name__=='__main__':
    ser={}; 
    for asset in ('XAU','US500'):
        D=bt.table(asset); SC.init(asset); raw={}
        for n,a,p,m in SYS:
            if a!=asset: continue
            s=CD.build_sig(D,a,p,raw); ec,ew,nl,dep,st=bt.run(a,s,m,D=D); P=bt.SPEC[a]; ex=dep-P['EQ0']
            ser[n]=(pd.Series(ec-ex-P['EQ0'],index=D.index),pd.Series(ew-ex-P['EQ0'],index=D.index))
    idx=ser['x1'][0].index.union(ser['u1'][0].index)
    EC={k:v[0].reindex(idx).ffill().fillna(0) for k,v in ser.items()}; EW={k:v[1].reindex(idx).ffill().fillna(0) for k,v in ser.items()}
    def stat(names):
        ec=sum(EC[n] for n in names); ew=sum(EW[n] for n in names); cap=sum(CAP['XAU'] if n[0]=='x' else CAP['US500'] for n in {a for a in names} ) if False else (30000*(any(n[0]=='x' for n in names))+10000*(any(n[0]=='u' for n in names)))
        pk=np.maximum.accumulate(ec.values); dd=float(np.max(pk-ew.values)); 
        mon=ec.groupby(idx.strftime('%Y-%m')).last().diff(); mon.iloc[0]=ec.groupby(idx.strftime('%Y-%m')).last().iloc[0]
        d=ec.resample('1D').last().diff().dropna()
        return dict(net=round(float(ec.iloc[-1])),dd=round(dd),dd_pct=round(dd/cap*100,1),cap=cap,months=[round(float(v)) for v in mon],npos=int((mon>0).sum()),sharpe_d=round(float(d.mean()/d.std()*np.sqrt(252)),2) if d.std()>0 else 0)
    out={}
    for combo in [['x1'],['x3'],['u1'],['u2'],['x1','x3'],['x1','x3','x4'],['x1','x5'],['u1','u2'],['u1','u2','u3'],['x1','u1'],['x1','x3','u1','u2'],['x1','x3','x4','u1','u2','u3'],['x2','u5'],['x2','x1','u5','u1']]:
        out['+'.join(combo)]=stat(combo)
    # daily pnl corr
    d=pd.DataFrame({k:v.resample('1D').last().diff() for k,v in EC.items()}).dropna()
    print(d.corr().round(2).to_string())
    for k,v in out.items(): print(k,v)
    d.corr().to_csv('/workspace/bt_3m/v3/results/portfolio_corr.csv'); json.dump(out,open('/workspace/bt_3m/v3/results/portfolio.json','w'),indent=1)
