# Round 6 MT5 job builder: basket finalists (W) + XAU scalp finalists (fixed price SL/TP).
import sys,os,json,copy,pickle,numpy as np,pandas as pd
sys.argv=[sys.argv[0],'XAU']
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,'/workspace/bt_3m/code')
import r5lib as R,bt,engine_export as EE,mt5prep as M,scalp as SC
V=R.V; ST=f'{V}/stage_mt5r6'; os.makedirs(ST,exist_ok=True)
q4=json.load(open(f'{V}/stage_mt5r5/q_p4v5.json')); q6=json.load(open(f'{V}/stage_mt5r5/q_p6v5.json'))
tpl={'XAU':[j for j in q4['jobs'] if j['name']=='v5_N4_g1_012'][0],'US500':[j for j in q6['jobs'] if j['name']=='v5_N4_u10_25'][0],'SC':[j for j in q4['jobs'] if j['name']=='v5_G30_xs1_06'][0]}
BAS=[('g7','XAU',0.04,'p4'),('u15','US500',1.5,'p6'),('u16','US500',1.0,'p6'),('u17','US500',2.0,'p6'),('u18','US500',1.5,'p6'),('u19','US500',1.5,'p6')]
SCL=[('xs3','g1_30z_fade2.0'),('xs4','imb15z_fade3.0'),('xs5','basis_rev'),('xs6','g3_60z_mom3.0'),('xs7','day_ext_fail')]
exp={}; Q={'p4':[],'p6':[]}
for k,asset,lot,slot in BAS:
    a,kk,p,m=R.S[k]; D=bt.table(asset); s=R.sig(k,D); A=bt.arrays(D)
    out=EE.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],bt.mgmt_vec(asset,m)); opn=out[0]; ix=np.nonzero(opn)[0]; t=D.index[ix]
    sym='GOLD.i#' if asset=='XAU' else 'US500Cash#'; nm=f'v6_{k}_{str(lot).replace(".","")}'
    pd.DataFrame({'thoi_gian':M.srv(t).strftime('%Y.%m.%d %H:%M:%S'),'ma':sym,'chieu':opn[ix],'gia':D.open.values[ix].round(2),'nguon':k,'lot':lot}).to_csv(f'{ST}/{nm}_mt5.csv',index=False,lineterminator='\n')
    j=copy.deepcopy(tpl[asset]); j['name']=nm; j['desc']='r6_'+k; j['group']='v6'
    j['params'].update(dict(InpLot0=lot,InpBuocGia=m['gap'],InpGianBuoc=1.4,InpMaxTang=m['maxN'],InpTPGia=m['btp'],InpFileCsv='brain2\\'+nm+'_mt5.csv')); Q[slot].append(j)
    fl=R.flat_arr(D,mode=2); o=R.run2(k,D,fl,lot=lot); exp[nm]=dict(py_W_net=float(o['ec'][-1]),py_W_dd=float((np.maximum.accumulate(o['ec'])-o['ew']).max()/o['cap']*100),nb=int(o['st'][0]))
D=bt.table('XAU'); SC.init('XAU'); A=SC.G['A']; ok=D.fut_ok.values; one=np.ones(len(D)); LOT=0.3
for k,key in SCL:
    o=pickle.load(open(f'{V}/results/r6/curves/sc_XAU_{key}.pkl','rb')); c=o['cfg']; s=o['sig']
    idx,pn,ex=SC.run_seq(s,ok,A['o'],A['h'],A['l'],A['c'],A['spr'],one,c['sl'],c['tp'],c['hold'],0.5); ix=idx+1; t=D.index[ix]
    nm=f'v6_{k}_03'
    pd.DataFrame({'thoi_gian':M.srv(t).strftime('%Y.%m.%d %H:%M:%S'),'ma':'GOLD.i#','chieu':s[idx],'gia':D.open.values[ix].round(2),'nguon':k,'lot':LOT}).to_csv(f'{ST}/{nm}_mt5.csv',index=False,lineterminator='\n')
    j=copy.deepcopy(tpl['SC']); j['name']=nm; j['desc']=f"r6_scalp_{k}_{key}_SL{c['sl']}_TP{c['tp']}_H{c['hold']}"; j['group']='v6'
    j['params'].update(dict(InpLot0=LOT,InpTPGia=c['tp'],InpCatLoPct=round(c['sl']*LOT*100/30000*100,3),InpGiuToiDaNen=int(c['hold']),InpFileCsv='brain2\\'+nm+'_mt5.csv')); Q['p4'].append(j)
    usd=pn*LOT*100; exp[nm]=dict(py_net=float(usd.sum()),n=len(usd),cfg={kk:c[kk] for kk in ('sl','tp','hold')},sig=key)
for slot in Q:
    b=dict(q4 if slot=='p4' else q6); b['jobs']=Q[slot]; json.dump(b,open(f'{ST}/q_{slot}v6.json','w'),indent=1)
json.dump(exp,open(f'{V}/results/r6/v6_expected.json','w'),indent=1); print(json.dumps(exp,indent=0)[:3000])
