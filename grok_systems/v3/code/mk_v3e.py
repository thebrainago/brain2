import sys,os,json,copy,numpy as np,pandas as pd
sys.argv=[sys.argv[0],'XAU']
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import newsig as N,bt,sig_v3 as S,engine_export as EE,mt5prep as M
V='/workspace/bt_3m/v3'; ST=f'{V}/stage_mt5e'; os.makedirs(ST,exist_ok=True)
CAND={'XAU':[('e1_pdbreak_gt20_ldny','pd_break_flow','gt20','ldny',1),('e2_lnorbreak_gt20_all','lnor_break_trend','gt20','all',1)],
      'US500':[('e3_orbd_mom_gt20','orbd_mom','gt20','all',1),('e4_asiafail_gt20_ldny','asia_fail','gt20','ldny',2)]}
qx=json.load(open(f'{V}/ref/q_p4e.json')); qu=json.load(open(f'{V}/ref/q_p6e.json')); exp={}
for asset in ('XAU','US500'):
    N.ASSET=asset; D=bt.table(asset); sp=N.specs(D); jobs=[]
    MG=[dict(L0=0.03,mult=1.0,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=0,hedge=0,cd=30),dict(L0=0.03,mult=1.0,gap=4,gstep=1.4,maxN=3,btp=2,trim=0,prune=0,hedge=0,cd=30),dict(L0=0.03,mult=1.0,gap=8,gstep=1.4,maxN=4,btp=4,trim=0,prune=0,hedge=0,cd=30)] if asset=='XAU' else [dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=3,btp=6,trim=0,prune=0,hedge=0,cd=30),dict(L0=1.0,mult=1.0,gap=30,gstep=1.4,maxN=3,btp=4,trim=0,prune=0,hedge=0,cd=30),dict(L0=1.0,mult=1.0,gap=60,gstep=1.4,maxN=4,btp=8,trim=0,prune=0,hedge=0,cd=30)]
    for nm,sg,adx,se,mi in CAND[asset]:
        s=S.filters(D,sp[sg],adx,se,asset); s=np.where(D.fut_ok.values,s,0).astype(np.int64); m=MG[mi]
        A=bt.arrays(D); out=EE.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s,A['roll'],A['dow'],bt.mgmt_vec(asset,m)); opn=out[0]; ix=np.nonzero(opn)[0]; t=D.index[ix]
        sym='GOLD.i#' if asset=='XAU' else 'US500Cash#'
        df=pd.DataFrame({'thoi_gian':M.srv(t).strftime('%Y.%m.%d %H:%M:%S'),'ma':sym,'chieu':opn[ix],'gia':D.open.values[ix].round(2),'nguon':nm,'lot':m['L0']}); fn=f'v3e_{nm}_mt5.csv'; df.to_csv(f'{ST}/{fn}',index=False,lineterminator='\n')
        q=bt.quick(asset,bt.run(asset,s,m,D=D),D.index); exp[nm]=dict(py_net=q['net'],py_dd=q['dd_pct'],nb=q['nb'])
        tm=qx['jobs'][1] if asset=='XAU' else qu['jobs'][0]; j=copy.deepcopy(tm); j['name']='v3e_'+nm; j['desc']=nm; j['group']='v3e'; j['from']='2026.06.01'; j['to']='2026.11.27'; j['deposit']='30000' if asset=='XAU' else '10000'
        j['params'].update(dict(InpKieuLot=0,InpLot0=m['L0'],InpBuocGia=m['gap'],InpGianBuoc=1.4,InpMaxTang=m['maxN'],InpTPGia=m['btp'],InpHedgeKhiLoPct=0,InpHedgeTiLe=1.0,InpFileCsv='brain2\\'+fn)); jobs.append(j)
    q=dict(qx if asset=='XAU' else qu); q['jobs']=jobs; q['timeout_min']=100; json.dump(q,open(f'{ST}/q_{"p4" if asset=="XAU" else "p6"}v3e.json','w'),indent=1)
json.dump(exp,open(f'{V}/results/v3e_expected.json','w'),indent=1); print(exp)
