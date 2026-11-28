import time,r5lib as R,bt,numpy as np
for asset,names in (('XAU',['x1','g1','g2','x4']),('US500',['u1','u7','u10','u11'])):
    D=bt.table(asset); fl0=np.zeros(len(D),np.int64)
    for n in names:
        for lab,fl in (('none',fl0),('flat',R.flat_arr(D,mode=1)),('hedge',R.flat_arr(D,mode=2)),('hedge23',R.flat_arr(D,fh=23,mode=2))):
            o=R.run2(n,D,fl); ec=o['ec'];ew=o['ew']; dd=(np.maximum.accumulate(ec)-ew).max()
            print(n,lab,'net',round(ec[-1]),'dd%',round(dd/o['cap']*100,1),'stats',o['st'][[0,9,10,11]],flush=True)
