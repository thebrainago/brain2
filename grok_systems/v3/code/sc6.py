# Round 6 scalp finalists: fixed-price SL/TP grid (EA-compatible). Config picked on A only, B reported as OOS. Saves USD curves for portfolio.
import sys,os,pickle,itertools,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
a=sys.argv[1]; sys.argv=[sys.argv[0],a]
import newsig as N, scalp as SC, sig_v3 as S, bt, scalp2 as S2
FIN={'XAU':[('n2:basis_rev','gt20','ny'),('n3:imb15z_fade3.0','gt20','all'),('n4:g1_30z_fade2.0','gt20','all'),('n4:g3_60z_mom3.0','none','ny'),('n2:day_ext_fail','gt20','ny'),('n4:cvd_lead','none','ny'),('n4:fz5z_fade3.0','gt20','ldny'),('n4:imb5z_fade3.0','gt20','all')],
     'US500':[('n4:g2_30z_fade3.0','gt20','ny'),('n4:nyib_break_flow','none','ldny'),('n4:fz5z_fade2.0','none','ny'),('n4:vclimax_fade_3','none','ldny')]}[a]
GR={'XAU':list(itertools.product((4,6,8,10,13),(4,6,8,10,13,18),(30,90))),'US500':list(itertools.product((4,6,8,12,16),(4,6,8,12,16,24),(30,90)))}[a]
LOT={'XAU':0.1,'US500':1.0}[a]
if __name__=='__main__':
    S2.init(); D=SC.G['D']; A=SC.G['A']; ok=D.fut_ok.values; one=np.ones(len(D)); pv=bt.SPEC[a]['pv']; isA=SC.G['isA']; mon=SC.G['mon']
    rows=[]; os.makedirs('/workspace/bt_3m/v3/results/r6/curves',exist_ok=True)
    for nm,adx,se in FIN:
        s=S.filters(D,S2.G['sp'][nm],adx,se,a).astype(np.int64); best=None
        for sl,tp,h in GR:
            idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],one,sl,tp,h,0.5); usd=pn*LOT*pv
            if len(usd)<40: continue
            pa=isA[idx]; r=dict(sig=nm,adx=adx,sess=se,sl=sl,tp=tp,hold=h,n=len(usd),net=usd.sum(),A=usd[pa].sum(),B=usd[~pa].sum(),nA=int(pa.sum()))
            r['tA']=usd[pa].mean()/(usd[pa].std(ddof=1)/np.sqrt(max(pa.sum(),2))+1e-9); r['tB']=usd[~pa].mean()/(usd[~pa].std(ddof=1)/np.sqrt(max((~pa).sum(),2))+1e-9)
            ec=np.cumsum(usd); r['dd']=float(np.max(np.maximum.accumulate(ec)-ec)); mm=[usd[mon[idx]==k].sum() for k in range(int(mon.max())+1)]; r['mpos']=int(sum(v>0 for v in mm))
            i2,p2,_=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr']*2,one,sl,tp,h,1.0); r['sx2']=float((p2*LOT*pv).sum())
            sd=np.r_[np.zeros(2,np.int64),s[:-2]]; i3,p3,_=SC.run_seq(sd,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],one,sl,tp,h,0.5); r['d2']=float((p3*LOT*pv).sum())
            rows.append(r)
            if best is None or r['tA']>best['tA']: best=dict(r)
        if best:
            sl,tp,h=best['sl'],best['tp'],best['hold']; out={}
            for tag,sm in (('base',1.0),('sx2s',2.0)):
                idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr']*sm,one,sl,tp,h,0.5 if sm==1 else 1.0); usd=pn*LOT*pv
                step=np.zeros(len(D)); np.add.at(step,ex,usd); ecum=np.cumsum(step); out[tag]=(ecum,ecum+np.minimum(step,0))
            out['lot']=LOT; out['index']=D.index; out['cfg']=best; out['sig']=s
            key=nm.split(':')[1]; pickle.dump(out,open(f'/workspace/bt_3m/v3/results/r6/curves/sc_{a}_{key}.pkl','wb'))
    R=pd.DataFrame(rows); R.to_parquet(f'/workspace/bt_3m/v3/results/r6/sc6_{a}.parquet')
    pd.set_option('display.width',250)
    B=R.sort_values('tA',ascending=False).drop_duplicates('sig')
    print(B[['sig','adx','sess','sl','tp','hold','n','net','A','B','tA','tB','dd','mpos','sx2','d2']].round(2).to_string())
