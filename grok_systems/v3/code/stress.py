import sys,os,json,pickle,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,lotscale as LS
V=LS.V; D_={}
for asset in ('XAU','US500'):
    D=bt.table(asset); SC.init(asset); raw={}
    for n,a,k,p,m in LS.SYS:
        if a!=asset: continue
        f=f'{LS.CD_}/{n}_x.pkl'
        if os.path.exists(f): continue
        s=CD.build_sig(D,a,p,raw); o={}
        if k=='b':
            P=bt.SPEC[a]
            ec,ew,nl,dep,st=bt.run(a,s,m,D=D,sprmul=3.0,slip=1.0); ex=dep-P['EQ0']; o['sx3']=(ec-ex-P['EQ0'],ew-ex-P['EQ0'])
            ec,ew,nl,dep,st=bt.run(a,s,m,D=D); o['nl']=nl; 
            ec,ew,nl2,dep,st=bt.run(a,s,m,D=D,sprmul=2.0,slip=1.0); ex=dep-P['EQ0']; o['sx2s']=(ec-ex-P['EQ0'],ew-ex-P['EQ0'])
        else:
            sl,tp,hold,lot=m; A=SC.G['A']; one=np.ones(len(D)); ok=np.ones(len(D),bool); pv=bt.SPEC[a]['pv']
            for tag,sm in (('sx3',3.0),('sx2s',2.0)):
                idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr']*sm,one,sl,tp,hold,1.0); usd=pn*lot*pv
                step=np.zeros(len(D)); np.add.at(step,ex,usd); ecum=np.cumsum(step); o[tag]=(ecum,ecum+np.minimum(step,0))
            o['nl']=np.zeros(len(D))
        o['px']=D.close.values; o['index']=D.index; pickle.dump(o,open(f,'wb')); print('saved',n,flush=True)
print('STRESS CURVES DONE')
