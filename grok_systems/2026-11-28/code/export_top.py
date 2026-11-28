# Export top-5 SIMULATED candidates with exact specs + entry CSVs (XM server time = New York + 7h) for MT5 tick-real verification.
import sys, os, json, numpy as np, pandas as pd
ASSET=sys.argv[1]; sys.argv=[sys.argv[0],ASSET,'X']
sys.path.insert(0,os.path.dirname(__file__)); import sweep as S, signals, engine_export as EE
S.init(); R=S.R; OUT=f'{R}/mt5_ready'; os.makedirs(OUT,exist_ok=True)
C=pd.read_csv(f'{R}/{ASSET}_stageC_candidates.csv',index_col=0)
C['pass_mirror_profit']=C.mirror_net>0
C['n_pass6']=C.n_pass+C.pass_mirror_profit.astype(int)
C=C.drop_duplicates(subset=['s_fam','s_side','s_trend','s_adx','s_macro','s_sess','net','dd_cap_pct'])
C=C.sort_values(['n_pass6','score'],ascending=False)
# diversify: at most 2 per signal family
pick=[]; cnt={}
for i,r in C.iterrows():
    if cnt.get(r.s_fam,0)>=2: continue
    pick.append(i); cnt[r.s_fam]=cnt.get(r.s_fam,0)+1
    if len(pick)==5: break
SYM={'US500':'US500Cash#','XAU':'GOLD.i#'}[ASSET]
tops=[]
for n,i in enumerate(pick,1):
    r=C.loc[i]; spec={k[2:]:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in r.index if k.startswith('s_')}
    m={k[2:]:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in r.index if k.startswith('m_')}
    s=signals.make(S.D,spec,ASSET)
    out=EE.run(S.A['o'],S.A['h'],S.A['l'],S.A['c'],S.A['spr'],S.A['atr'],s,S.A['roll'],S.A['dow'],S.mgmt_vec(m))
    opn=out[0]; idx=np.nonzero(opn)[0]; t=S.D.index[idx]
    srv=(t.tz_convert('America/New_York').tz_localize(None)+pd.Timedelta(hours=7))
    name=f'{ASSET}_c{n}'
    pd.DataFrame({'thoi_gian':srv.strftime('%Y.%m.%d %H:%M:%S'),'time_utc':t.strftime('%Y-%m-%d %H:%M:%S'),'ma':SYM,'chieu':opn[idx],
                  'gia_bid_open':S.A['o'][idx].round(2),'nguon':spec['fam'],'lot':m['L0']}).to_csv(f'{OUT}/{name}_entries.csv',index=False,lineterminator='\r\n')
    # full signal state per minute (only non-zero), for DCA gating if dsig=1
    nz=np.nonzero(s)[0]; ts=S.D.index[nz]
    pd.DataFrame({'thoi_gian':(ts.tz_convert('America/New_York').tz_localize(None)+pd.Timedelta(hours=7)).strftime('%Y.%m.%d %H:%M:%S'),'chieu':s[nz]}).to_csv(f'{OUT}/{name}_signal_minutes.csv',index=False,lineterminator='\r\n')
    keep=['net','dd_cap_pct','dd_pct_peak','dd_usd','baskets','basket_wins','orders','max_layers','max_lots','topup_used','f1','f2','f3','f1_dd','f2_dd','f3_dd','sharpe','dsr',
          'spr2_net','spr2_dd_cap_pct','spr3_net','spr3_dd_cap_pct','delay2_net','delay2_dd_cap_pct','mirror_net','mirror_dd_cap_pct','mirror_stopouts','mirror_spr2_net','mirror_spr2_dd_cap_pct',
          'gapup5_dd','gapdn5_dd','gapup10_dd','gapdn10_dd','gapup20_dd','gapdn20_dd','placebo_med_net','placebo_pctile','n_pass','n_pass6','pass_mirror_profit','pass_spr2','pass_delay','pass_mirror','pass_gap20','pass_placebo']
    met={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in keep if k in r.index}
    tops.append(dict(name=name,LABEL='SIMULATED (Python M1 bar engine) - NOT MT5',symbol=SYM,window_utc='2026-08-20 -> 2026-11-26 12:04',
        capital=dict(start=S.SPEC['EQ0'],topup=S.SPEC['topup'],topup_trigger_equity=S.SPEC['ttrig']*S.SPEC['EQ0'],dd_denominator=S.CAP),
        costs=dict(spread='XM M1 spread column (bid bars, ask=bid+spread)',slippage='0.5 x spread per fill',swap_long_per_lot_night=S.SPEC['swl'],swap_short_per_lot_night=S.SPEC['sws'],
                   triple_swap_dow_utc=S.SPEC['tdow'],commission=0,leverage=S.SPEC['lev'],stop_out='equity < 50% used margin (max(long,short) lots)'),
        signal=spec,management=m,entries_csv=f'{OUT}/{name}_entries.csv',signal_minutes_csv=f'{OUT}/{name}_signal_minutes.csv',n_entries=int(len(idx)),metrics=met))
json.dump(tops,open(f'{OUT}/{ASSET}_top5.json','w'),indent=1,default=float)
print(json.dumps([dict(name=t['name'],sig=t['signal'],m=t['management'],net=round(t['metrics']['net'],1),dd=round(t['metrics']['dd_cap_pct'],1)) for t in tops],default=float))
