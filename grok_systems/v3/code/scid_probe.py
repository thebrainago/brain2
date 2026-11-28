import numpy as np, glob, os, datetime as dt
D=np.dtype([('t','<i8'),('o','<f4'),('h','<f4'),('l','<f4'),('c','<f4'),('nt','<u4'),('v','<u4'),('bv','<u4'),('av','<u4')])
def ts(x): return (dt.datetime(1899,12,30)+dt.timedelta(microseconds=int(x))).strftime('%Y-%m-%d %H:%M:%S')
for fn in sorted(glob.glob(r'E:\GrokWork\research_expand_20261120\scid\*.scid'))+[r'E:\GrokWork\tick_store\ESZ6\20261113.scid']:
    sz=os.path.getsize(fn); n=(sz-56)//40
    m=np.memmap(fn,dtype=D,mode='r',offset=56,shape=(n,))
    print(os.path.basename(fn),n,ts(m[0]['t']),ts(m[-1]['t']),'px',float(m[n//2]['c']),'bv+av==v frac',float(np.mean((m[:2000]['bv'].astype(int)+m[:2000]['av'])==m[:2000]['v'])))
