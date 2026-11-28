import sys,os,json,copy,numpy as np,pandas as pd
sys.argv=[sys.argv[0],'XAU']
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,'/workspace/bt_3m/code')
import r5lib as R,bt,engine_export as EE,mt5prep as M
V=R.V; ST=f'{V}/stage_mt5r5b'; os.makedirs(ST,exist_ok=True)
q4=json.load(open(f'{V}/stage_mt5r5/q_p4v5.json')); q6=json.load(open(f'{V}/stage_mt5r5/q_p6v5.json'))
tpl={'XAU':[j for j in q4['jobs'] if j['name']=='v5_N4_g1_012'][0],'US500':[j for j in q6['jobs'] if j['name']=='v5_N4_u10_25'][0]}
NEWS=[('g3','XAU',0.06,'p4'),('g4','XAU',0.09,'p4'),('u12','US500',3.0,'p6')]
exp={}; Q={'p4':[],'p6':[]}
for k,asset,lot,slot in NEWS:
    a,kk,p,m=R.S[k]; D=bt.table(asset); s=R.sig(k,D); A=bt.arrays(D)
    out=EE.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],bt.mgmt_vec(asset,m)); opn=out[0]; ix=np.nonzero(opn)[0]; t=D.index[ix]
    sym='GOLD.i#' if asset=='XAU' else 'US500Cash#'; nm=f'v5_n_{k}_{str(lot).replace(".","")}'
    pd.DataFrame({'thoi_gian':M.srv(t).strftime('%Y.%m.%d %H:%M:%S'),'ma':sym,'chieu':opn[ix],'gia':D.open.values[ix].round(2),'nguon':k,'lot':lot}).to_csv(f'{ST}/{nm}_mt5.csv',index=False,lineterminator='\n')
    j=copy.deepcopy(tpl[asset]); j['name']=nm; j['desc']='r5_new_'+k; j['group']='v5'
    j['params'].update(dict(InpLot0=lot,InpBuocGia=m['gap'],InpGianBuoc=1.4,InpMaxTang=m['maxN'],InpTPGia=m['btp'],InpFileCsv='brain2\\'+nm+'_mt5.csv')); Q[slot].append(j)
    fl=R.flat_arr(D,mode=2); o=R.run2(k,D,fl); exp[nm]=dict(py_W_net=float(o['ec'][-1]),py_W_dd=float((np.maximum.accumulate(o['ec'])-o['ew']).max()/o['cap']*100),nb=int(o['st'][0]))
for slot in Q:
    b=dict(q4 if slot=='p4' else q6); b['jobs']=Q[slot]; json.dump(b,open(f'{ST}/q_{slot}v5b.json','w'),indent=1)
json.dump(exp,open(f'{V}/results/v5b_expected.json','w'),indent=1); print(exp)
