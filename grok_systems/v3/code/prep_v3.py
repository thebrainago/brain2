# v3 feature tables on XM M1 grid (UTC aligned with Europe/Athens server tz = fixes Oct25-31 misalignment) Jun01..Nov26.
import pandas as pd, numpy as np, os, sys
B='/workspace/bt_3m'; V=f'{B}/v3'; FE=f'{V}/feat'; TB=f'{V}/tbl'
START='2026-06-01'
def cfd_utc(fn):
    x=pd.read_csv(fn,parse_dates=['time'])
    x['t']=x.time.dt.tz_localize('Europe/Athens',ambiguous='NaT',nonexistent='NaT').dt.tz_convert('UTC')
    x=x.dropna(subset=['t']).drop_duplicates('t').set_index('t').sort_index()
    return x[x.index>=START][['open','high','low','close','spread','tick_volume']]
def ldf(n):
    d=pd.read_parquet(f'{FE}/{n}_1m_v3.parquet'); d.index=pd.DatetimeIndex(d.time_utc); return d.drop(columns='time_utc')
def sess_label(idx): return (idx.tz_convert('America/New_York')+pd.Timedelta(hours=6)).strftime('%Y%m%d')
def choose(segs):
    """segs: list of (df, name). choose per trading-day the contract with larger daily volume, monotonic roll order."""
    vols=[]
    for d,n in segs:
        s=d.vol.groupby(sess_label(d.index)).sum(); vols.append(s.rename(n))
    V_=pd.concat(vols,axis=1).fillna(0).sort_index()
    pick=[]; cur=0
    for day,row in V_.iterrows():
        nxt=cur+1
        while nxt<len(segs) and row.iloc[nxt]>row.iloc[cur]: cur=nxt; nxt=cur+1
        pick.append(cur)
    P=pd.Series(pick,index=V_.index)
    return P,V_
def stitch(segs):
    P,V_=choose(segs); parts=[]; prof_sel={}
    for k,(d,n) in enumerate(segs):
        lab=pd.Series(sess_label(d.index),index=d.index); m=lab.map(P)
        parts.append(d[(m==k).values])
    out=pd.concat(parts).sort_index(); out=out[~out.index.duplicated()]
    return out,P,V_
def mirror_fut(f,prof,P0):
    f=f.copy(); 
    o,h,l,c=2*P0-f.o,2*P0-f.l,2*P0-f.h,2*P0-f.c; f['o'],f['h'],f['l'],f['c']=o,h,l,c
    f['pq']=2*P0*f.vol-f.pq; f['poc']=2*P0-f.poc
    def sw(a,b):
        t=f[a].copy(); f[a]=f[b]; f[b]=t
    for a,b in [('bv','sv'),('bimb','simb'),('bstk','sstk'),('swb_n','sws_n'),('swb_q','sws_q'),('ask_at_hi','bid_at_lo'),('bid_at_hi','ask_at_lo')]: sw(a,b)
    for i in (1,2,3):
        sw(f'b{i}v',f's{i}v'); sw(f'b{i}n',f's{i}n')
    prof=prof.copy(); prof['px']=2*P0-prof.px; prof[['bv','sv']]=prof[['sv','bv']].values
    return f,prof
def value_area(pr):
    """pr: file_day,px,bv,sv -> dict day-> (poc,vah,val)"""
    res={}
    for day,g in pr.groupby('file_day'):
        g=g.groupby('px')[['bv','sv']].sum(); v=(g.bv+g.sv).sort_index()
        if v.sum()<=0 or len(v)<3: continue
        px=v.index.values; vv=v.values.astype(float); i=int(np.argmax(vv)); lo=hi=i; tot=vv.sum(); acc=vv[i]
        while acc<0.7*tot and (lo>0 or hi<len(vv)-1):
            up=vv[hi+1:hi+3].sum() if hi<len(vv)-1 else -1; dn=vv[max(lo-2,0):lo].sum() if lo>0 else -1
            if up>=dn: 
                step=min(2,len(vv)-1-hi); acc+=vv[hi+1:hi+1+step].sum(); hi+=step
            else:
                step=min(2,lo); acc+=vv[lo-step:lo].sum(); lo-=step
        res[day]=(px[i],px[hi],px[lo])
    return res
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def adx(h,l,c,n=14):
    up=h.diff(); dn=-l.diff(); pdm=np.where((up>dn)&(up>0),up,0.); mdm=np.where((dn>up)&(dn>0),dn,0.)
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.ewm(alpha=1/n,adjust=False).mean()
    pdi=100*pd.Series(pdm,index=h.index).ewm(alpha=1/n,adjust=False).mean()/atr; mdi=100*pd.Series(mdm,index=h.index).ewm(alpha=1/n,adjust=False).mean()/atr
    dx=100*(pdi-mdi).abs()/(pdi+mdi); return dx.ewm(alpha=1/n,adjust=False).mean(),atr
EVENTS=[('2026-06-05 12:30',30),('2026-06-17 18:00',60),('2026-07-02 12:30',30),('2026-07-29 18:00',60),('2026-08-07 12:30',30),('2026-09-04 12:30',30),('2026-09-16 18:00',60),('2026-10-02 12:30',30),('2026-10-28 18:00',60),('2026-11-06 13:30',30)]
def build(asset,mirror=False):
    if asset=='US500':
        cf='US500Cash_M1_xmserver.csv'; tick=0.01
        segs=[(ldf('ESU6'),'ESU6'),(ldf('CME.ESZ6'),'ESZ6')]; profs={'ESU6':pd.read_parquet(f'{FE}/ESU6_profile_v3.parquet'),'ESZ6':pd.read_parquet(f'{FE}/CME.ESZ6_profile_v3.parquet')}
        aux_segs=[(ldf('CME.NQZ6'),'NQZ6')]
    else:
        cf='GOLD_i_M1_xmserver.csv'; tick=0.01
        g=ldf('GCZ6s'); g=g[g.index<'2026-08-20 08:42']
        segs=[(ldf('GCQ6'),'GCQ6'),(g,'GCZ6s'),(ldf('COMEX.GCZ6'),'GCZ6')]
        profs={'GCQ6':pd.read_parquet(f'{FE}/GCQ6_profile_v3.parquet'),'GCZ6s':pd.read_parquet(f'{FE}/GCZ6s_profile_v3.parquet'),'GCZ6':pd.read_parquet(f'{FE}/COMEX.GCZ6_profile_v3.parquet')}
        es=[(ldf('ESU6'),'ESU6'),(ldf('CME.ESZ6'),'ESZ6')]; aux_segs=[(stitch(es)[0],'ES')]
    x=cfd_utc(f'{B}/{cf}')
    f,P,V_=stitch(segs); f=f[f.index>=START]
    # profile for selected contract per day
    names=[n for _,n in segs]; pr=[]
    for day,k in P.items():
        p=profs[names[k]]; pr.append(p[p.file_day==day])
    prof=pd.concat(pr)
    fa=stitch(aux_segs)[0] if len(aux_segs)>1 else aux_segs[0][0]; fa=fa[fa.index>=START]
    if mirror:
        P0=f.c.iloc[0]; f,prof=mirror_fut(f,prof,P0)
        Pa=fa.c.iloc[0]; fa,_=mirror_fut(fa,prof.iloc[:0] if False else pd.DataFrame({'file_day':[],'px':[],'bv':[],'sv':[]}),Pa)
        Pc=x.close.iloc[0]; x=x.assign(open=2*Pc-x.open,high=2*Pc-x.low,low=2*Pc-x.high,close=2*Pc-x.close)
    f=f.copy(); f['d1']=f.bv-f.sv
    lab=sess_label(f.index); f['sess']=lab; g=f.groupby('sess')
    f['cvd']=g.d1.cumsum(); f['vwap']=g.pq.cumsum()/g.vol.cumsum()
    idx=x.index; F=pd.DataFrame(index=idx)
    def fl(col,expr=None):
        return (f[col] if expr is None else expr).reindex(idx).fillna(0)
    F['d1']=fl('d1'); F['vol']=fl('vol'); F['n']=fl('n')
    for i in (1,2,3): F[f'g{i}']=(f[f'b{i}v']-f[f's{i}v']).reindex(idx).fillna(0)
    F['swn']=(f.swb_q-f.sws_q).reindex(idx).fillna(0)
    F['imb']=(f.bimb-f.simb).reindex(idx).fillna(0); F['stk']=(f.bstk-f.sstk).reindex(idx).fillna(0)
    F['ask_hi']=f.ask_at_hi.reindex(idx).fillna(0); F['bid_lo']=f.bid_at_lo.reindex(idx).fillna(0)
    for c in ['o','h','l','c','cvd','vwap']: F['f_'+c]=f[c].reindex(idx).ffill(limit=30)
    F['fut_ok']=f['c'].reindex(idx).notna().rolling(30,min_periods=1).sum()>=5
    D=x.join(F)
    # aux (cross asset) returns & flows
    fa=fa.copy(); fa['d1']=fa.bv-fa.sv
    D['a_c']=fa.c.reindex(idx).ffill(limit=30); D['a_d1']=fa.d1.reindex(idx).fillna(0); D['a_vol']=fa.vol.reindex(idx).fillna(0)
    D['a_ok']=fa['c'].reindex(idx).notna().rolling(30,min_periods=1).sum()>=5
    # ATR / EMAs / ADX on CFD
    m5=D[['open','high','low','close']].resample('5min').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    tr=pd.concat([m5.high-m5.low,(m5.high-m5.close.shift()).abs(),(m5.low-m5.close.shift()).abs()],axis=1).max(axis=1)
    m5['atr5']=tr.ewm(alpha=1/14,adjust=False).mean(); m5['ema20']=ema(m5.close,20); m5['ema200']=ema(m5.close,200)
    m5s=m5[['atr5','ema20','ema200']].shift(1); m5s.index=m5s.index+pd.Timedelta(minutes=5); D=D.join(m5s.reindex(idx,method='ffill'))
    h1=D[['open','high','low','close']].resample('1h').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    h1['ema55']=ema(h1.close,55); h1['adx'],h1['atrh1']=adx(h1.high,h1.low,h1.close); h1['ema55_slope']=np.sign(h1.ema55-h1.ema55.shift(3)); h1['ema55_side']=np.sign(h1.close-h1.ema55)
    h1s=h1[['ema55','adx','atrh1','ema55_slope','ema55_side']].shift(1); h1s.index=h1s.index+pd.Timedelta(hours=1); D=D.join(h1s.reindex(idx,method='ffill'))
    D['basis']=(D.f_c-D.close).rolling(60,min_periods=10).median()
    D['vwap_cfd']=D.f_vwap-D.basis; D['vwap_dev']=(D.close-D.vwap_cfd)/D.atr5
    dev=(D.f_c-D.f_vwap); sess=pd.Series(sess_label(idx),index=idx)
    # session-expanding std of dev
    s1=dev.groupby(sess).cumsum(); cnt=dev.groupby(sess).cumcount()+1; s2=(dev**2).groupby(sess).cumsum()
    D['vwap_sd']=np.sqrt(np.maximum(s2/cnt-(s1/cnt)**2,0)); D['vwap_z']=dev/D.vwap_sd.replace(0,np.nan)
    # rolling flow features
    z=lambda s,n=1440: s/s.rolling(n,min_periods=300).std()
    for w in (5,15,30,60):
        D[f'd{w}']=D.d1.rolling(w).sum(); D[f'd{w}z']=z(D[f'd{w}'])
        D[f'v{w}']=D.vol.rolling(w).sum(); D[f'vr{w}']=D[f'v{w}']/D[f'v{w}'].rolling(1440,min_periods=300).mean()
        D[f'fr{w}']=(D.f_c-D.f_c.shift(w))/D.atr5
        D[f'cr{w}']=(D.close-D.close.shift(w))/D.atr5
    for i in (1,2,3):
        for w in (15,30,60): D[f'g{i}_{w}']=D[f'g{i}'].rolling(w).sum(); D[f'g{i}_{w}z']=z(D[f'g{i}_{w}'])
    for w in (15,30): D[f'sw{w}']=D.swn.rolling(w).sum(); D[f'sw{w}z']=z(D[f'sw{w}'])
    for w in (5,15,30): D[f'imb{w}']=D.imb.rolling(w).sum(); D[f'stk{w}']=D.stk.rolling(w).sum(); D[f'imb{w}z']=z(D[f'imb{w}'])
    D['cvd30']=D.f_cvd.diff(30); D['cvd60']=D.f_cvd.diff(60); D['fpx30']=D.f_c.diff(30)
    # rolling extremes of futures price and CVD (for divergence)
    for w in (15,30,60):
        D[f'fhi{w}']=D.f_c.rolling(w).max(); D[f'flo{w}']=D.f_c.rolling(w).min(); D[f'chi{w}']=D.f_cvd.rolling(w).max(); D[f'clo{w}']=D.f_cvd.rolling(w).min()
        D[f'hi{w}']=D.high.rolling(w).max().shift(1); D[f'lo{w}']=D.low.rolling(w).min().shift(1)
    D['cvd_sd']=D.d1.rolling(1440,min_periods=300).std()
    # aux returns
    for w in (5,15,30):
        D[f'ar{w}']=(D.a_c-D.a_c.shift(w)); D[f'ar{w}z']=D[f'ar{w}']/D[f'ar{w}'].rolling(1440,min_periods=300).std()
        D[f'fz{w}']=(D.f_c-D.f_c.shift(w)); D[f'fz{w}z']=D[f'fz{w}']/D[f'fz{w}'].rolling(1440,min_periods=300).std()
        D[f'ad{w}']=D.a_d1.rolling(w).sum(); D[f'ad{w}z']=D[f'ad{w}']/D[f'ad{w}'].rolling(1440,min_periods=300).std()
    # day structure
    nyd=pd.Series((idx.tz_convert('America/New_York')+pd.Timedelta(hours=7)).strftime('%Y-%m-%d'),index=idx); D['nyday']=nyd.values
    dd=D.groupby('nyday').agg(H=('high','max'),L=('low','min'),C=('close','last')); dd['ibs']=(dd.C-dd.L)/(dd.H-dd.L)
    D['pdH']=D.nyday.map(dd.H.shift(1)); D['pdL']=D.nyday.map(dd.L.shift(1)); D['pdC']=D.nyday.map(dd.C.shift(1)); D['ibs_prev']=D.nyday.map(dd.ibs.shift(1))
    D['dH']=D.high.groupby(D.nyday).cummax().shift(1); D['dL']=D.low.groupby(D.nyday).cummin().shift(1)  # running day hi/lo excl current bar
    ny=idx.tz_convert('America/New_York'); ldn=idx.tz_convert('Europe/London')
    def orng(local,h0,m0,h1_,m1_,name):
        t=local.hour*60+local.minute; inw=(t>=h0*60+m0)&(t<h1_*60+m1_)
        s=pd.Series(inw,index=idx); hh=D.high.where(s); ll=D.low.where(s); key=pd.Series(local.strftime('%Y%m%d'),index=idx)
        H=hh.groupby(key).transform('max'); L=ll.groupby(key).transform('min')
        done=pd.Series(t>=h1_*60+m1_,index=idx)
        D[name+'_hi']=H.where(done); D[name+'_lo']=L.where(done)
    orng(ny,9,30,10,0,'nyor'); orng(ny,9,30,10,30,'nyib'); orng(ny,8,20,8,50,'cxor'); orng(ldn,8,0,8,30,'lnor')
    # asia range 00:00-07:00 UTC
    t=idx.hour*60+idx.minute; inw=pd.Series(t<420,index=idx); key=pd.Series(idx.strftime('%Y%m%d'),index=idx)
    H=D.high.where(inw).groupby(key).transform('max'); L=D.low.where(inw).groupby(key).transform('min'); done=pd.Series(t>=420,index=idx); D['as_hi']=H.where(done); D['as_lo']=L.where(done)
    # profile levels of previous session (mapped to CFD via basis)
    va=value_area(prof); days=sorted(va); sx=pd.Series(sess_label(idx),index=idx)
    prev={days[i]:va[days[i-1]] for i in range(1,len(days))}
    for j,nm in enumerate(['poc','vah','val']): D[nm+'_p']=sx.map({d:v[j] for d,v in prev.items()})-D.basis
    # time & news
    D['hour']=idx.hour; D['minute']=idx.minute; D['dow']=idx.day_of_week; D['ny_t']=ny.hour*60+ny.minute
    D['rollover']=nyd.ne(nyd.shift()).values; D['spread_px']=D.spread*tick
    nb=np.zeros(len(D),bool)
    for tt,w in EVENTS:
        tt=pd.Timestamp(tt,tz='UTC'); nb|=(idx>=tt-pd.Timedelta(minutes=w))&(idx<=tt+pd.Timedelta(minutes=w))
    D['news']=nb
    D['month']=idx.strftime('%Y-%m')
    out=f'{TB}/{asset}{"_MIRROR" if mirror else ""}.parquet'; D.to_parquet(out)
    print(asset,'mirror' if mirror else '',len(D),idx.min(),idx.max(),'fut_ok%',round(D.fut_ok.mean()*100,1),'roll picks',P.groupby(P).size().to_dict() if False else dict(zip(names,[int((P==k).sum()) for k in range(len(names))])),flush=True)
    return D
if __name__=='__main__':
    for a in sys.argv[1:]:
        build(a,False); build(a,True)
