import sys,os,json,numpy as np,pandas as pd,multiprocessing as mp,time
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,portfolio as P
X=P.X; mgx=P.mgx; mgu=P.mgu
BASE={'x1':('XAU',X('sw_fade_15_1.8','gt20','ldny'),mgx['nh8']),'x4':('XAU',X('dz_fade_15_2.0','none','ldn'),mgx['nh8']),'x6':('XAU',X('imb_fade_15_1.5','gt20','ldn'),mgx['nh8']),
 'x7':('XAU',X('big3_mom_60_2.0','none','ny'),mgx['nh8']),
 'u1':('US500',X('sw_fade_15_1.8','gt20','ldny'),mgu['u1']),'u2':('US500',X('absorb_fade_5_1.5_1.0','none','ny'),mgu['u2']),'u6':('US500',X('dz_mom_5_1.5','none','all'),mgu['u2']),
 'u7':('US500',X('sw_fade_15_1.5','none','all'),mgu['u2']),'u9':('US500',X('imb_mom_15_1.5','none','ldny'),mgu['u3'])}
VETO={'XAU':['sw_fade_15_1.8','dz_fade_15_2.0','big3_mom_60_2.0','imb_fade_15_1.5','vwapatr_3'],'US500':['sw_fade_15_1.8','absorb_fade_5_1.5_1.0','dz_mom_5_1.5','sw_fade_15_1.5','imb_mom_15_1.5']}
G={}
def init():
    G['raw']={}
def window_any(r,W,d):  # any signal of direction d within last W bars (incl current)
    x=(r==d).astype(np.int32); c=np.cumsum(x); c2=np.r_[np.zeros(W,np.int64),c[:-W]] if W<len(c) else np.zeros_like(c); return (c-c2)>0
def filters_for(asset,D,raw):
    F={}; h=D.hour.values; dow=D.dow.values; side=D.ema55_side.values; adx=D.adx.values; atr=D.atr5.values
    for h0 in range(0,24,3): F[f'noh_{h0}-{h0+3}']=('keep',~((h>=h0)&(h<h0+3)))
    for d in range(5): F[f'nodow{d}']=('keep',dow!=d)
    med=pd.Series(atr).rolling(1440,min_periods=300).median().values; ratio=atr/np.where(med>0,med,np.nan)
    F['vol_notlow']=('keep',~(ratio<0.8)); F['vol_nothigh']=('keep',~(ratio>1.4)); F['vol_mid']=('keep',(ratio>=0.8)&(ratio<=1.4))
    F['adx_lt25']=('keep',~(adx>=25)); F['adx_gt15']=('keep',~(adx<15)); F['adx_15_30']=('keep',(adx>=15)&(adx<=30))
    F['with_trend']=('dir',side); F['against_trend']=('dir',-side)
    for w in ('d15z','d30z'):
        v=np.nan_to_num(D[w].values); F[f'flow_{w}_agree']=('dirv',np.sign(v)); F[f'flow_{w}_oppose']=('dirv',-np.sign(v))
    for nm in VETO[asset]:
        r=raw(nm)
        for W in (15,45): 
            F[f'veto_{nm}_{W}']=('veto',(r,W))
    return F
def apply(s,f):
    kind,v=f
    if kind=='keep': return np.where(v,s,0)
    if kind=='dir': return np.where(np.sign(v)==np.sign(s),s,0)
    if kind=='dirv': return np.where(v==np.sign(s),s,0)
    if kind=='veto':
        r,W=v; bad=np.where(s>0,window_any(r,W,-1),window_any(r,W,1)); return np.where(bad,0,s)
def job(name):
    asset,p,m=BASE[name]; D=bt.table(asset); SC.init(asset)
    raw_cache={}
    specs=SC.G['specs']
    def raw(n):
        if n not in raw_cache: raw_cache[n]=np.asarray(specs[n](D),dtype=np.int8)
        return raw_cache[n]
    s=CD.build_sig(D,asset,p,raw_cache); F=filters_for(asset,D,raw); rows=[]
    pe=bt.periods(D)
    def ev(sg,lab):
        o=bt.run(asset,np.ascontiguousarray(sg,dtype=np.int64),m,D=D); q=bt.quick(asset,o,D.index); en=o[0]-(o[3]-bt.SPEC[asset]['EQ0'])-bt.SPEC[asset]['EQ0']
        ia=int(np.searchsorted(D.index,bt.A_END)); a=float(en[ia-1]); b=float(en[-1]-en[ia-1])
        mv=list(q['months'].values()); return dict(sys=name,flt=lab,net=q['net'],dd_pct=q['dd_pct'],A=a,B=b,npos=sum(v>0 for v in mv),minm=min(mv),nb=q['nb'],so=q['so'])
    rows.append(ev(s,'BASE'))
    for k,f in F.items(): rows.append(ev(apply(s,f),k))
    return rows
if __name__=='__main__':
    t0=time.time(); names=list(BASE)
    with mp.Pool(min(8,len(names))) as Pl: res=Pl.map(job,names,chunksize=1)
    R=pd.DataFrame([r for rr in res for r in rr]); R.to_parquet('/workspace/bt_3m/v3/results/ovl.parquet'); print('done',len(R),round(time.time()-t0),flush=True)
