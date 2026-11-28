# v2 finalize: robust filter, placebo, WF, broker-cost estimates, no-prune check, export. PYTHON CONSERVATIVE SIMULATION.
import sys, os, json, glob, numpy as np, pandas as pd, multiprocessing as mp
A_=sys.argv[1]; sys.argv=[sys.argv[0],A_,'final']; sys.path.insert(0,os.path.dirname(__file__))
import v2, sweep as S, engine_export as EE
R=S.R; OUT=v2.OUT; CAP=S.CAP
def spm(r):
    sp={k[2:]:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in r.index if k.startswith('s_')}
    m={k[2:]:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in r.index if k.startswith('m_')}
    return sp,m
def fin(j):
    i,sp,m=j; s=v2.sig('o',sp); sm=v2.sig('m',sp); res={'i':i}
    nets=[]
    for seed in range(20):
        rng=np.random.default_rng(seed); runs=np.r_[0,np.nonzero(np.diff(s)!=0)[0]+1]; fl=rng.choice([-1,1],size=len(runs))
        rid=np.zeros(len(s),np.int64); rid[runs]=1; rid=np.cumsum(rid)-1; p=(np.abs(s)*fl[rid]).astype(np.int64)
        nets.append(v2.q(v2.ev(S.A,p,m))['net'])
    base=v2.q(v2.ev(S.A,s,m)); res['placebo_pct']=float((np.array(nets)<base['net']).mean()*100); res['placebo_med']=float(np.median(nets))
    for c in ['xm','exness_std','exness_raw']:
        for mul,sl,tag in [(1.0,0.5,''),(2.0,1.0,'_x2')]:
            x=v2.q(v2.ev(S.A,s,m,mul,sl,c)); res[f'{c}{tag}_net']=x['net']; res[f'{c}{tag}_dd']=x['dd']
    m0=dict(m,prune=0.0); x=v2.q(v2.ev(S.A,s,m0)); res['noprune_net']=x['net']; res['noprune_dd']=x['dd']
    x=v2.q(v2.ev(S.A,s,m0,3.0 if A_=='US500' else 2.0,1.0)); res['noprune_sx_net']=x['net']
    x=v2.q(v2.ev(v2.MA,sm,m0)); res['noprune_mir_net']=x['net']; res['noprune_mir_dd']=x['dd']
    x=v2.q(v2.ev(S.A,np.r_[np.zeros(2,np.int64),s[:-2]],m)); res['delay2_net']=x['net']; res['delay2_dd']=x['dd']
    # mirror placebo
    nm=[]
    for seed in range(10):
        rng=np.random.default_rng(100+seed); runs=np.r_[0,np.nonzero(np.diff(sm)!=0)[0]+1]; fl=rng.choice([-1,1],size=len(runs))
        rid=np.zeros(len(sm),np.int64); rid[runs]=1; rid=np.cumsum(rid)-1; nm.append(v2.q(v2.ev(v2.MA,(np.abs(sm)*fl[rid]).astype(np.int64),m))['net'])
    res['mir_placebo_pct']=float((np.array(nm)<v2.q(v2.ev(v2.MA,sm,m))['net']).mean()*100)
    return res
if __name__=='__main__':
    v2.init()
    D=pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f'{R}/v2_{A_}_parts/*.parquet'))],ignore_index=True)
    D['calmar']=D.net/D.dd_usd.clip(lower=1); D['minf']=D[['f1','f2','f3']].min(axis=1)
    if A_=='US500':
        ok=(D.net>0)&(D.minf>0)&(D.stopouts==0)&(D.sx_net>0)&(D.mir_net>0)&(D.mir_dd<25)&(D.mir_so==0)&(D.gapup20_dd<0.7)&(D.gapdn20_dd<0.7)
    else:
        ok=(D.net>0)&(D.dd_cap_pct<60)&(D.stopouts==0)&(D.mir_net>0)&(D.mir_dd<60)&(D.mir_so==0)&(D.sx_net>0)&(D.minf>-0.02*CAP)
    D['ok']=ok; print('configs',len(D),'pass_grid',int(ok.sum()),flush=True)
    # failure breakdown
    fb={'n':len(D),'net>0':int((D.net>0).sum()),'mirror_net>0':int((D.mir_net>0).sum()),'both_net>0':int(((D.net>0)&(D.mir_net>0)).sum()),
        'stress_net>0':int((D.sx_net>0).sum()),'all_months>0':int((D.minf>0).sum()),'pass_grid':int(ok.sum())}
    P=D[ok].copy()
    if len(P)==0:
        D['worst']=D[['net','mir_net']].min(axis=1); P=D[(D.stopouts==0)&(D.mir_so==0)].sort_values('worst',ascending=False).head(40).copy(); P['ok']=False
        cand=P
    else:
        cand=pd.concat([P.sort_values('net',ascending=False).head(30),P.sort_values('calmar',ascending=False).head(30)]).drop_duplicates(subset=['net','dd_cap_pct','mir_net'])
    jobs=[(int(i),*spm(r)) for i,r in cand.iterrows()]
    with mp.Pool(7,initializer=v2.init) as pool: F=pd.DataFrame(pool.map(fin,jobs)).set_index('i')
    C=cand.join(F); C['pass_placebo']=C.placebo_pct>=95
    C['final_ok']=C.ok&C.pass_placebo
    # walk-forward selection inside the robust (grid-pass) set
    wf={}
    if len(P) and P.ok.any():
        Q=P[P.ok]; a=(Q.f1/(Q.f1_dd*CAP/100).clip(lower=1)).idxmax(); wf['pick_on_F1']=dict(f1=Q.f1[a],oos_f2=Q.f2[a],oos_f3=Q.f3[a])
        b=((Q.f1+Q.f2)/(Q[['f1_dd','f2_dd']].max(axis=1)*CAP/100).clip(lower=1)).idxmax(); wf['pick_on_F1F2']=dict(is_=Q.f1[b]+Q.f2[b],oos_f3=Q.f3[b])
    Dall=D; aw=(Dall.f1/(Dall.f1_dd*CAP/100).clip(lower=1))[Dall.stopouts==0].idxmax(); wf['unrestricted_pick_on_F1']=dict(f1=Dall.f1[aw],oos_f2=Dall.f2[aw],oos_f3=Dall.f3[aw],mir_net=Dall.mir_net[aw])
    C=C.sort_values(['final_ok','net'],ascending=False); C.to_csv(f'{R}/v2_{A_}_finalists.csv')
    top=C[C.final_ok].head(3) if C.final_ok.any() else C.head(3)
    tops=[]; SYM={'US500':'US500Cash#','XAU':'GOLD.i#'}[A_]
    for n,(i,r) in enumerate(top.iterrows(),1):
        sp,m=spm(r); s=v2.sig('o',sp)
        out=EE.run(S.A['o'],S.A['h'],S.A['l'],S.A['c'],S.A['spr'],S.A['atr'],s,S.A['roll'],S.A['dow'],S.mgmt_vec(m)); opn=out[0]; ix=np.nonzero(opn)[0]; t=S.D.index[ix]
        name=f'{A_}_v2_c{n}'; srv=t.tz_convert('America/New_York').tz_localize(None)+pd.Timedelta(hours=7)
        if r.final_ok:
            pd.DataFrame({'thoi_gian':srv.strftime('%Y.%m.%d %H:%M:%S'),'time_utc':t.strftime('%Y-%m-%d %H:%M:%S'),'ma':SYM,'chieu':opn[ix],'gia_bid_open':S.A['o'][ix].round(2),'nguon':sp['fam'],'lot':m['L0']}).to_csv(f'{OUT}/{name}_entries.csv',index=False,lineterminator='\r\n')
        met={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in r.index if not k.startswith(('s_','m_'))}
        tops.append(dict(name=name,LABEL='PYTHON CONSERVATIVE SIMULATION - NOT MT5',passed_all=bool(r.final_ok),symbol=SYM,signal=sp,management=m,
            capital=dict(start=S.SPEC['EQ0'],topup=S.SPEC['topup'],dd_denominator=CAP),entries_csv=f'{OUT}/{name}_entries.csv' if r.final_ok else None,metrics=met))
    json.dump(dict(asset=A_,failure_breakdown=fb,walk_forward=wf,top3=tops),open(f'{OUT}/{A_}_v2_top3.json','w'),indent=1,default=float)
    print(json.dumps(fb)); print(json.dumps(wf,default=float))
    cols=['s_fam','s_k','s_adx','s_trend','s_sess','m_L0','m_mult','m_gap','m_maxN','m_btp','m_trim','m_prune','m_hedge','m_hr','m_hgap','m_comp','m_maxlots','net','dd_cap_pct','f1','f2','f3','sx_net','mir_net','mir_dd','gapup20_dd','gapdn20_dd','placebo_pct','mir_placebo_pct','noprune_net','noprune_sx_net','noprune_mir_net','exness_std_net','exness_raw_net','xm_x2_net','delay2_net','final_ok']
    print(C.head(8)[cols].round(2).to_string())
