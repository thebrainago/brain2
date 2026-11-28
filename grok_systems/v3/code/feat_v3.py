# READ-ONLY parser of Fxaurum TickDb *.tick (FXTK). Extended 1m order-flow features incl. footprint imbalance. Never writes to TickDb.
import sys, os, glob, numpy as np, pandas as pd
from multiprocessing import Pool
SRC=r'C:\Users\DUNG\AppData\Local\FxaurumRithmic\TickDb'
OUT=r'E:\GrokWork\bt_v3\feat'
DT=np.dtype([('ts','<u8'),('px','<f8'),('q','<u4'),('sd','u1'),('ets','<u8'),('id','<u8')])
# sym: (tick, [big thresholds q1<q2<q3])
CFG={'CME.ESZ6':(0.25,[10,30,100]),'COMEX.GCZ6':(0.1,[3,8,25]),'CME.NQZ6':(0.25,[5,15,50]),'COMEX.GCG7':(0.1,[3,8,25])}
def load(fn):
    b=open(fn,'rb').read(); assert b[:4]==b'FXTK'
    n=(len(b)-32)//37
    return np.frombuffer(b,dtype=DT,count=n,offset=32)
def one(args):
    sym,fn=args; tk,th=CFG[sym]
    a=load(fn); a=a[(a['sd']==66)|(a['sd']==83)]; a=a[(a['px']>0)&(a['q']>0)]
    if len(a)==0: return None
    d=pd.DataFrame({'ts':a['ts'].astype('int64'),'px':a['px'],'q':a['q'].astype('int64'),'buy':a['sd']==66,'id':a['id'].astype('int64')})
    d=d.drop_duplicates(subset=['ts','id','px','q','buy']).sort_values('ts',kind='stable').reset_index(drop=True)
    return process(d,tk,th,os.path.basename(fn)[:8])
def process(d,tk,th,day):
    d['m']=d.ts//60000*60000
    d['p']=(d.px/tk).round().astype('int64')
    b=d.buy.values; q=d.q.values
    d['bv']=np.where(b,q,0); d['sv']=np.where(b,0,q); d['pq']=d.px*d.q
    for i,t in enumerate(th,1):
        g=q>=t; d[f'b{i}v']=np.where(g&b,q,0); d[f's{i}v']=np.where(g&~b,q,0)
        d[f'b{i}n']=(g&b).astype(np.int32); d[f's{i}n']=(g&~b).astype(np.int32)
    # sweep: same ms + same side spanning >=3 ticks
    g=d.groupby(['ts','buy']).agg(lo=('p','min'),hi=('p','max'),qq=('q','sum')).reset_index()
    g=g[(g.hi-g.lo)>=3].copy(); g['m']=g.ts//60000*60000
    g['swb_n']=g.buy.astype(int); g['sws_n']=(~g.buy).astype(int); g['swb_q']=np.where(g.buy,g.qq,0); g['sws_q']=np.where(g.buy,0,g.qq)
    sw=g.groupby('m')[['swb_n','sws_n','swb_q','sws_q']].sum()
    agg=dict(o=('px','first'),h=('px','max'),l=('px','min'),c=('px','last'),vol=('q','sum'),bv=('bv','sum'),sv=('sv','sum'),n=('q','size'),maxq=('q','max'),pq=('pq','sum'))
    for i in range(1,len(th)+1):
        for k in ('b','s'):
            agg[f'{k}{i}v']=(f'{k}{i}v','sum'); agg[f'{k}{i}n']=(f'{k}{i}n','sum')
    m=d.groupby('m').agg(**agg).join(sw)
    # footprint per (m,p)
    f=d.groupby(['m','p']).agg(bv=('bv','sum'),sv=('sv','sum')).reset_index()  # bv = ask-lift vol (aggressive buy), sv = bid-hit vol
    # buy imbalance at p: bv[p] vs sv[p-1] ; sell imbalance at p: sv[p] vs bv[p+1]
    key=f.set_index(['m','p'])
    sv_below=key.sv.reindex(pd.MultiIndex.from_arrays([f.m,f.p-1])).values
    bv_above=key.bv.reindex(pd.MultiIndex.from_arrays([f.m,f.p+1])).values
    sv_below=np.nan_to_num(sv_below); bv_above=np.nan_to_num(bv_above)
    thr=3.0; minv=max(1,th[0]//2)
    f['bimb']=((f.bv>=thr*np.maximum(sv_below,0.5))&(f.bv>=minv)).astype(int)
    f['simb']=((f.sv>=thr*np.maximum(bv_above,0.5))&(f.sv>=minv)).astype(int)
    # stacked (>=3 consecutive levels)
    def stacked(col):
        f2=f[['m','p',col]].copy(); f2['g']=(f2[col]!=f2[col].shift())|(f2.m!=f2.m.shift())|(f2.p!=f2.p.shift()+1)
        f2['gid']=f2.g.cumsum(); run=f2.groupby('gid')[col].transform('sum')
        f2['st']=((f2[col]==1)&(run>=3)).astype(int); return f2.groupby('m').st.sum()
    fm=f.groupby('m').agg(bimb=('bimb','sum'),simb=('simb','sum'),lv=('p','size'))
    fm['bstk']=stacked('bimb'); fm['sstk']=stacked('simb')
    # unfinished: ask vol at high, bid vol at low
    hi=f.loc[f.groupby('m').p.idxmax()].set_index('m'); lo=f.loc[f.groupby('m').p.idxmin()].set_index('m')
    fm['ask_at_hi']=hi.bv; fm['bid_at_hi']=hi.sv; fm['ask_at_lo']=lo.bv; fm['bid_at_lo']=lo.sv
    # minute POC and delta at poc
    f['v']=f.bv+f.sv; pocr=f.loc[f.groupby('m').v.idxmax()].set_index('m'); fm['poc']=pocr.p*tk; fm['poc_v']=pocr.v
    m=m.join(fm)
    # profile (session-file day)
    pr=f.groupby('p').agg(bv=('bv','sum'),sv=('sv','sum')).reset_index(); pr['file_day']=day; pr['px']=pr.p*tk
    return m, pr[['file_day','px','bv','sv']], (day,len(d))
def main(sym):
    os.makedirs(OUT,exist_ok=True)
    fns=sorted(glob.glob(os.path.join(SRC,sym,'*.tick')))
    with Pool(int(os.environ.get('NP','8'))) as P: res=P.map(one,[(sym,f) for f in fns],chunksize=1)
    res=[r for r in res if r]
    M=pd.concat([r[0] for r in res])
    sums=[c for c in M.columns if c not in('o','h','l','c','maxq','l','poc','poc_v','ask_at_hi','bid_at_hi','ask_at_lo','bid_at_lo')]
    M=M.groupby(level=0).agg({c:('first' if c=='o' else 'last' if c in('c','poc','poc_v','ask_at_hi','bid_at_hi','ask_at_lo','bid_at_lo') else 'max' if c in('h','maxq') else 'min' if c=='l' else 'sum') for c in M.columns})
    M=M.fillna(0); M.index.name='ts_ms'; M['time_utc']=pd.to_datetime(M.index,unit='ms',utc=True)
    M.to_parquet(os.path.join(OUT,f'{sym}_1m_v3.parquet'))
    pd.concat([r[1] for r in res]).to_parquet(os.path.join(OUT,f'{sym}_profile_v3.parquet'))
    print('DONE',sym,len(M),M.time_utc.min(),M.time_utc.max(),flush=True)
if __name__=='__main__':
    for s in sys.argv[1:]: main(s)
