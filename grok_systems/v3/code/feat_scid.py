# READ-ONLY: Sierra .scid tick files (Grok copies in E:\GrokWork\research_expand_*) -> same 1m schema as feat_v3 (history before 2026-08-20).
import sys, os, numpy as np, pandas as pd
from multiprocessing import Pool
import feat_v3 as F
SC=r'E:\GrokWork\research_expand_20261120\scid'; OUT=r'E:\GrokWork\bt_v3\feat'
D=np.dtype([('t','<i8'),('o','<f4'),('h','<f4'),('l','<f4'),('c','<f4'),('nt','<u4'),('v','<u4'),('bv','<u4'),('av','<u4')])
# name: (file, tick, thresholds, price divisor, start, end)
J={'ESU6':('ESU6.CME.scid',0.25,[10,30,100],100.0,'2026-03-29','2026-09-18'),
   'MESZ6':('MESZ6.CME.scid',0.25,[10,30,100],100.0,'2026-05-17','2026-11-20'),
   'MNQZ6':('MNQZ6.CME.scid',0.25,[5,15,50],100.0,'2026-05-17','2026-11-20'),
   'GCQ6':('GCQ6.COMEX.scid',0.1,[3,8,25],10.0,'2026-02-27','2026-08-26'),
   'GCZ6s':('GCZ6.COMEX.scid',0.1,[3,8,25],10.0,'2026-05-14','2026-11-20')}
EPOCH=pd.Timestamp('1899-12-30')
def day_job(a):
    name,day,i0,i1=a; fn,tk,th,div,_,_=J[name]
    m=np.memmap(os.path.join(SC,fn),dtype=D,mode='r',offset=56,shape=(os.path.getsize(os.path.join(SC,fn))-56)//40)
    r=np.array(m[i0:i1])
    r=r[(r['v']>0)&((r['bv']>0)|(r['av']>0))]
    if len(r)==0: return None
    ts=(r['t']//1000)+int((pd.Timestamp('1899-12-30')-pd.Timestamp('1970-01-01')).total_seconds()*1000)
    px=r['c'].astype('float64')/div
    # side: aggressive buy if av>0 and bv==0; sell if bv>0 and av==0; mixed -> split to two virtual trades
    buy=r['av']>0; sell=r['bv']>0
    parts=[]
    for msk,side,qcol in ((buy,True,'av'),(sell,False,'bv')):
        parts.append(pd.DataFrame({'ts':ts[msk],'px':px[msk],'q':r[qcol][msk].astype('int64'),'buy':side}))
    d=pd.concat(parts).sort_values('ts',kind='stable').reset_index(drop=True)
    d=d[(d.px>0)&(d.q>0)].reset_index(drop=True)
    return F.process(d,tk,th,day)
def run(name):
    fn,tk,th,div,s,e=J[name]; path=os.path.join(SC,fn); n=(os.path.getsize(path)-56)//40
    m=np.memmap(path,dtype=D,mode='r',offset=56,shape=(n,)); t=m['t']
    days=pd.date_range(pd.Timestamp(s)-pd.Timedelta(days=1)+pd.Timedelta(hours=22),pd.Timestamp(e)+pd.Timedelta(hours=22),freq='D'); off=int((pd.Timestamp('1970-01-01')-EPOCH).total_seconds()*1e6)
    b=np.array([int((x-pd.Timestamp('1970-01-01')).total_seconds()*1e6)+off for x in days])
    idx=np.searchsorted(t,b); jobs=[(name,(days[k]+pd.Timedelta(days=1)).strftime('%Y%m%d'),int(idx[k]),int(idx[k+1])) for k in range(len(days)-1) if idx[k+1]>idx[k]]
    with Pool(int(os.environ.get('NP','8'))) as P: res=[r for r in P.map(day_job,jobs,chunksize=1) if r]
    M=pd.concat([r[0] for r in res])
    M=M.groupby(level=0).agg({c:('first' if c=='o' else 'last' if c in('c','poc','poc_v','ask_at_hi','bid_at_hi','ask_at_lo','bid_at_lo') else 'max' if c in('h','maxq') else 'min' if c=='l' else 'sum') for c in M.columns})
    M=M.fillna(0); M.index.name='ts_ms'; M['time_utc']=pd.to_datetime(M.index,unit='ms',utc=True)
    M.to_parquet(os.path.join(OUT,f'{name}_1m_v3.parquet')); pd.concat([r[1] for r in res]).to_parquet(os.path.join(OUT,f'{name}_profile_v3.parquet'))
    print('DONE',name,len(M),M.time_utc.min(),M.time_utc.max(),flush=True)
if __name__=='__main__':
    for s in sys.argv[1:]: run(s)
