import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd, bt, sig_v3 as S, battery as B, time
xa_c3=dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30,comp=0,dsig=0,maxlots=0)
D=bt.table('XAU'); s=S.filters(D,S.fam_sw(D,1.8,15,'fade'),'gt20','ldny','XAU'); s=np.where(D.fut_ok.values,s,0)
t=time.time(); r=B.battery('XAU',s,xa_c3); print(time.time()-t); print({k:(round(v,1) if isinstance(v,float) else v) for k,v in r.items() if k!='months'}); print(r['months'])
