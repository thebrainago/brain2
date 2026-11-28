# Build MT5-ready entries CSV + queue json for v3 finalists (server time = Europe/Athens). PYTHON expectations stored.
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt, sig_v3 as S, scalp as SC, cands as CD, engine_export as EE
V='/workspace/bt_3m/v3'; OUT=f'{V}/mt5_ready'; os.makedirs(OUT,exist_ok=True)
SYM={'US500':'US500Cash#','XAU':'GOLD.i#'}
def srv(t): return t.tz_convert('Europe/Athens').tz_localize(None)
def write_entries(asset,D,ix,dirs,name,lot):
    t=D.index[ix]
    df=pd.DataFrame({'thoi_gian':srv(t).strftime('%Y.%m.%d %H:%M:%S'),'time_utc':t.strftime('%Y-%m-%d %H:%M:%S'),'ma':SYM[asset],'chieu':dirs,'gia_bid_open':D.open.values[ix].round(2),'nguon':name,'lot':lot})
    df.to_csv(f'{OUT}/{name}_vao.csv',index=False,lineterminator='\r\n'); return len(df)
def basket(asset,name,prog,m):
    D=bt.table(asset); raw={}; SC.init(asset); s=CD.build_sig(D,asset,prog,raw); A=bt.arrays(D)
    out=EE.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],bt.mgmt_vec(asset,m)); opn=out[0]; ix=np.nonzero(opn)[0]
    n=write_entries(asset,D,ix,opn[ix],name,m['L0'])
    o2=bt.run(asset,s,m,D=D); q=bt.quick(asset,o2,D.index)
    return dict(name=name,kind='basket',asset=asset,prog=prog,mgmt=m,entries=n,py_net=q['net'],py_dd_pct=q['dd_pct'],py_nb=q['nb'],py_months=q['months'])
def scalp(asset,name,prog,sl,tp,hold,lot):
    D=bt.table(asset); raw={}; SC.init(asset); s=CD.build_sig(D,asset,prog,raw)
    A=SC.G['A']; one=np.ones(len(D)); ok=np.ones(len(D),bool)
    idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],one,sl,tp,hold,0.5)
    pv=bt.SPEC[asset]['pv']; usd=pn*lot*pv; ix=idx+1
    n=write_entries(asset,D,ix,s[idx],name,lot)
    mon=pd.Series(usd,index=D.index[ix]).groupby(D.index[ix].strftime('%Y-%m')).sum()
    return dict(name=name,kind='scalp',asset=asset,prog=prog,sl=sl,tp=tp,hold=hold,lot=lot,entries=n,py_net=float(usd.sum()),py_n=len(usd),py_win=float((usd>0).mean()),py_pf=float(usd[usd>0].sum()/-usd[usd<=0].sum()),py_months={k:round(float(v),1) for k,v in mon.items()})
if __name__=='__main__':
    R=[]
    mgx={'c3':dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30),
         'nh8':dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30)}
    X=lambda a,adx,se,b=None,W=0:dict(kind='single' if b is None else 'pair',a=a,b=b,W=W,adx=adx,sess=se)
    R.append(basket('XAU','x1_swfade_nh8',X('sw_fade_15_1.8','gt20','ldny'),mgx['nh8']))
    R.append(basket('XAU','x2_swfade_c3',X('sw_fade_15_1.8','gt20','ldny'),mgx['c3']))
    R.append(basket('XAU','x3_imbfade_nh8',X('imb_fade_15_1.5','gt20','ldn'),mgx['nh8']))
    R.append(basket('XAU','x4_dzfade_nh8',X('dz_fade_15_2.0','none','ldn'),mgx['nh8']))
    R.append(basket('XAU','x5_sw_vwap_nh8',X('sw_fade_15_1.8','gt20','all','vwapatr_3',30),mgx['nh8']))
    R.append(scalp('XAU','xs1_xlead_big2',X('xlead_fadeself_5_2.5','gt20','all','big2_mom_30_2.5',30),8.0,8.0,90,0.1))
    R.append(scalp('XAU','xs2_big3_emapull',X('big3_mom_60_2.0','none','ny','emapull',30),8.0,13.0,90,0.1))
    mgu={'u1':dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30),
         'u2':dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30),
         'u3':dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30),
         'c1':dict(L0=2.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=1.5,hedge=1,hgap=90,hr=0.5,htp=5.0,cd=30)}
    R.append(basket('US500','u1_swfade_nh',X('sw_fade_15_1.8','gt20','ldny'),mgu['u1']))
    R.append(basket('US500','u2_absorbfade5',X('absorb_fade_5_1.5_1.0','none','ny'),mgu['u2']))
    R.append(basket('US500','u3_sw_absorb',X('sw_fade_15_1.8','gt20','ny','absorb_fade_5_1.5_1.0',30),mgu['u3']))
    R.append(basket('US500','u4_sw_big2',X('sw_fade_15_1.8','gt20','ldny','big2_fade_30_1.5',10),mgu['u1']))
    R.append(basket('US500','u5_v2c1_6m',X('sw_fade_15_1.8','gt20','ldny'),mgu['c1']))
    R.append(scalp('US500','us1_big2fade_ny',X('big2_fade_30_1.5','gt20','ny'),8.0,12.0,90,1.0))
    json.dump(R,open(f'{OUT}/expected_python.json','w'),indent=1,default=str)
    for r in R: print(r['name'],r['entries'],'py_net',round(r['py_net'],1),r.get('py_dd_pct'),r.get('py_n'),r.get('py_pf'))
