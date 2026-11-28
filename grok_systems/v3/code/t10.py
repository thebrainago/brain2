import sys;sys.argv=['x','XAU']
import numpy as np,r5lib as R,bt
for k in ('up1','up2','up3'):
    a=R.S[k][0]; D=bt.table(a); fl=R.flat_arr(D,mode=2)
    o=R.run2(k,D,fl); o0=R.run2(k,D,np.zeros(len(D),np.int64)); o2=R.run2(k,D,fl,sprmul=2.0,slip=1.0)
    dd=lambda o:(np.maximum.accumulate(o['ec'])-o['ew']).max()/o['cap']*100
    print(k,a,R.REF[k],'base',round(o0['ec'][-1]),round(dd(o0),1),'W',round(o['ec'][-1]),round(dd(o),1),'sx2W',round(o2['ec'][-1]),round(dd(o2),1),'nb',int(o['st'][0]),flush=True)
