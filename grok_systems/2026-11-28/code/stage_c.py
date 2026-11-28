# Stage C: robust selection, stress, placebo null, mirror (trend-reversed) test, walk-forward, DSR. SIMULATED (Python) only.
import sys, os, json, glob, numpy as np, pandas as pd, multiprocessing as mp
sys.argv=[sys.argv[0],sys.argv[1],'C']+sys.argv[2:]
sys.path.insert(0,os.path.dirname(__file__)); import sweep as S, engine, signals
from scipy.stats import norm
ASSET=S.ASSET; R=S.R; CAP=S.CAP
def load_B():
    fs=sorted(glob.glob(f'{R}/{ASSET}_stageB_parts/*.parquet')); return pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
def spec_of(row): return {k[2:]:(row[k].item() if hasattr(row[k],'item') else row[k]) for k in row.index if k.startswith('s_')}
def m_of(row): return {k[2:]:(row[k].item() if hasattr(row[k],'item') else row[k]) for k in row.index if k.startswith('m_')}
MIRA=None
def init_all():
    global MIRA
    S.init(); M=pd.read_parquet(f'{S.B}/{S.SPEC["file"].replace(".parquet","_MIRROR.parquet")}')
    MIRA=(M,dict(o=M.open.values,h=M.high.values,l=M.low.values,c=M.close.values,spr=M.spread_px.values,atr=M.atr5.fillna(0).values,roll=M.rollover.values,dow=M.dow.values.astype(np.int64)))
def ev(A,s,m,sprmul=1.0,slip=0.5):
    out=engine.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],S.mgmt_vec(m,sprmul,slip)); return out
def quick(out):
    ec,ew,nl,dep,st=out; ex=dep-S.SPEC['EQ0']; en=ec-ex; ewn=ew-ex; pk=np.maximum.accumulate(en)
    return dict(net=float(en[-1]-S.SPEC['EQ0']),dd_cap_pct=float(np.max(pk-ewn)/CAP*100),stopouts=int(st[3]),topup=float(st[8]-S.SPEC['EQ0']))
def stress(job):
    i,spec,m=job; s=signals.make(S.D,spec,ASSET); res={'i':i}
    base=S.metrics(ev(S.A,s,m),0); res.update({'base_'+k:v for k,v in base.items()})
    for tag,sm,sl in [('spr2',2.0,1.0),('spr3',3.0,1.0)]:
        res.update({f'{tag}_'+k:v for k,v in quick(ev(S.A,s,m,sm,sl)).items()})
    sd=np.r_[np.zeros(2,np.int64),s[:-2]]; res.update({'delay2_'+k:v for k,v in quick(ev(S.A,sd,m)).items()})
    M,MA=MIRA; sm_=signals.make(M,spec,ASSET); res.update({'mirror_'+k:v for k,v in quick(ev(MA,sm_,m)).items()})
    res.update({'mirror_spr2_'+k:v for k,v in quick(ev(MA,sm_,m,2.0,1.0)).items()})
    # placebo null: same timestamps, random direction (20 seeds)
    nz=np.nonzero(s)[0]; nets=[]
    for seed in range(20):
        rng=np.random.default_rng(seed); p=np.zeros_like(s); 
        # keep runs of same signal grouped: random sign per contiguous run
        sg=s.copy(); runs=np.r_[0,np.nonzero(np.diff(sg)!=0)[0]+1]; flip=rng.choice([-1,1],size=len(runs))
        rid=np.zeros(len(s),np.int64); rid[runs]=1; rid=np.cumsum(rid)-1; p=np.abs(sg)*flip[rid]
        nets.append(quick(ev(S.A,p.astype(np.int64),m))['net'])
    nets=np.array(nets); res['placebo_med_net']=float(np.median(nets)); res['placebo_pctile']=float((nets<base['net']).mean()*100)
    return res
def dsr(sr_ann,T,sk,ku,N,var_sr):
    sr=sr_ann/np.sqrt(252); emax=np.sqrt(var_sr)*((1-0.5772)*norm.ppf(1-1/N)+0.5772*norm.ppf(1-1/(N*np.e)))
    den=np.sqrt(max(1e-12,1-sk*sr+(ku-1)/4*sr**2)); return float(norm.cdf((sr-emax)*np.sqrt(T-1)/den))
if __name__=='__main__':
    B_=load_B(); A_=pd.read_parquet(f'{R}/{ASSET}_stageA.parquet'); N=len(B_)+len(A_)
    print('configs',N,flush=True)
    var_sr=float(np.var(B_.sharpe/np.sqrt(252)))
    feas=(B_.net>0)&(B_.dd_cap_pct<80)&(B_.stopouts==0)&(B_.f1>0)&(B_.f2>0)&(B_.f3>0)&(B_.gapup10_dd<0.8)&(B_.gapdn10_dd<0.8)
    B_['score']=B_.net/np.maximum(B_.dd_usd,1.0)
    F=B_[feas&(B_.s_fam!='placebo')].copy(); print('feasible',len(F),'of',len(B_),flush=True)
    # walk-forward selection (by fold PnL/DD) using all configs incl infeasible
    wf={}
    sc1=B_.f1/np.maximum(B_.f1_dd*CAP/100,1); j=sc1[(B_.s_fam!='placebo')&(B_.stopouts==0)].idxmax()
    wf['pick_on_F1']=dict(idx=int(j),f1=B_.f1[j],oos_f2=B_.f2[j],oos_f3=B_.f3[j],f2_dd=B_.f2_dd[j],f3_dd=B_.f3_dd[j])
    sc2=(B_.f1+B_.f2)/np.maximum(np.maximum(B_.f1_dd,B_.f2_dd)*CAP/100,1); j=sc2[(B_.s_fam!='placebo')&(B_.stopouts==0)].idxmax()
    wf['pick_on_F1F2']=dict(idx=int(j),is_f1f2=B_.f1[j]+B_.f2[j],oos_f3=B_.f3[j],f3_dd=B_.f3_dd[j])
    # robust pick: median-rank of top-200 per family, then diversify
    F=F.sort_values('score',ascending=False)
    cand=pd.concat([g.head(4) for _,g in F.groupby(['s_fam','s_side'])]).sort_values('score',ascending=False).head(48)
    # also the top 12 by raw net with DD<60
    cand=pd.concat([cand,F[F.dd_cap_pct<60].sort_values('net',ascending=False).head(12)]).drop_duplicates()
    jobs=[(int(i),spec_of(r),m_of(r)) for i,r in cand.iterrows()]
    with mp.Pool(8,initializer=init_all) as P: st=list(P.imap(stress,jobs))
    ST=pd.DataFrame(st).set_index('i'); C=cand.join(ST)
    C['dsr']=[dsr(r['sharpe'],r['ndays'],r['skew'],r['kurt'],N,var_sr) for _,r in C.iterrows()]
    C['pass_spr2']=(C.spr2_net>0)&(C.spr2_dd_cap_pct<80)&(C.spr2_stopouts==0)
    C['pass_delay']=(C.delay2_net>0)&(C.delay2_dd_cap_pct<80)
    C['pass_mirror']=(C.mirror_dd_cap_pct<80)&(C.mirror_stopouts==0)
    C['pass_gap20']=(C.gapup20_dd<0.8)&(C.gapdn20_dd<0.8)
    C['pass_placebo']=C.placebo_pctile>=75
    C['n_pass']=C[['pass_spr2','pass_delay','pass_mirror','pass_gap20','pass_placebo']].sum(axis=1)
    C=C.sort_values(['n_pass','score'],ascending=False)
    C.to_csv(f'{R}/{ASSET}_stageC_candidates.csv')
    json.dump(dict(asset=ASSET,configs_tested=N,feasible=int(feas.sum()),var_sr_daily=var_sr,walk_forward=wf,
        placebo_stageB=dict(med_net=float(B_[B_.s_fam=='placebo'].net.median()),feasible_rate=float(feas[B_.s_fam=='placebo'].mean()),
                            signal_feasible_rate=float(feas[B_.s_fam!='placebo'].mean()))),
        open(f'{R}/{ASSET}_stageC_summary.json','w'),indent=1,default=float)
    print(C.head(10)[['s_fam','s_side','s_trend','s_macro','net','dd_cap_pct','f1','f2','f3','spr2_net','mirror_net','mirror_dd_cap_pct','placebo_pctile','dsr','n_pass']].to_string())
