import sys,os,numpy as np,pandas as pd,json
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,portfolio as P
def filt(s,win,mode):
    s=s.copy(); out=s.copy(); idx=np.nonzero(s)[0]; last_i=-10**9; last_d=0
    for i in idx:
        d=s[i]; flip=(last_d!=0 and d!=last_d and i-last_i<=win)
        if flip:
            if mode=='drop_flip': out[i]=0
        last_i=i; last_d=d
    if mode=='lock':   # after a flip, lock out ALL entries for win bars (stand aside)
        out=s.copy(); lock=-1
        last_i=-10**9; last_d=0
        for i in idx:
            d=s[i]
            if i<lock: out[i]=0
            elif last_d!=0 and d!=last_d and i-last_i<=win: out[i]=0; lock=i+win
            last_i=i; last_d=d
    return out
res=[]
for n,a,p,m in P.SYS:
    if n not in ('x1','x3','x4','u1','u2','x2'): continue
    D=bt.table(a); SC.init(a); s=CD.build_sig(D,a,p,{}); nflip=0
    base=bt.quick(a,bt.run(a,s,m,D=D),D.index); res.append((n,'base',0,base['net'],base['dd_pct'],base['nb']))
    for win in (30,90,240):
        for mode in ('drop_flip','lock'):
            s2=filt(s,win,mode); q=bt.quick(a,bt.run(a,s2,m,D=D),D.index); res.append((n,mode,win,q['net'],q['dd_pct'],q['nb']))
df=pd.DataFrame(res,columns=['sys','mode','win_min','net','dd_pct','nb']); print(df.to_string()); df.to_csv('/workspace/bt_3m/v3/results/flipfilt.csv',index=False)
