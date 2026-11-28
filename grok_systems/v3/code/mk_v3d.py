import sys,os,json,copy,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import ovl,bt,scalp as SC,cands as CD,engine_export as EE,mt5prep as M
V='/workspace/bt_3m/v3'; ST=f'{V}/stage_mt5d'; os.makedirs(ST,exist_ok=True)
CAND=[('d1_x4_veto_imb','x4','veto_imb_fade_15_1.5_15'),('d2_x1_veto_big3','x1','veto_big3_mom_60_2.0_15'),('d3_x6_volnotlow','x6','vol_notlow'),('d4_x7_nodow4','x7','nodow4')]
asset='XAU'; D=bt.table(asset); SC.init(asset); rc={}; specs=SC.G['specs']
def raw(n):
    if n not in rc: rc[n]=np.asarray(specs[n](D),dtype=np.int8)
    return rc[n]
exp={}
jobs=[]
qx=json.load(open(f'{V}/ref/q_p4e.json')); gx1=qx['jobs'][1]
for nm,sysn,flt in CAND:
    a,p,m=ovl.BASE[sysn]; s=CD.build_sig(D,a,p,rc); F=ovl.filters_for(a,D,raw); s2=np.ascontiguousarray(ovl.apply(s,F[flt]),dtype=np.int64)
    A=bt.arrays(D); out=EE.run(A['o'],A['h'],A['l'],A['c'],A['spr'],A['atr'],s2,A['roll'],A['dow'],bt.mgmt_vec(a,m)); opn=out[0]; ix=np.nonzero(opn)[0]
    t=D.index[ix]; df=pd.DataFrame({'thoi_gian':M.srv(t).strftime('%Y.%m.%d %H:%M:%S'),'ma':'GOLD.i#','chieu':opn[ix],'gia':D.open.values[ix].round(2),'nguon':nm,'lot':0.03})
    fn=f'v3d_{nm}_mt5.csv'; df.to_csv(f'{ST}/{fn}',index=False,lineterminator='\n')
    q=bt.quick(a,bt.run(a,s2,m,D=D),D.index); exp[nm]=dict(py_net=q['net'],py_dd=q['dd_pct'],nb=q['nb'])
    j=copy.deepcopy(gx1); j['name']='v3d_'+nm; j['desc']=nm; j['group']='v3d'; j['from']='2026.06.01'; j['to']='2026.11.27'; j['deposit']='30000'
    j['params'].update(dict(InpKieuLot=0,InpLot0=0.03,InpBuocGia=m['gap'],InpGianBuoc=1.4,InpMaxTang=m['maxN'],InpTPGia=m['btp'],InpHedgeKhiLoPct=0,InpHedgeTiLe=1.0,InpFileCsv='brain2\\'+fn)); jobs.append(j)
q=dict(qx); q['jobs']=jobs; q['timeout_min']=100; json.dump(q,open(f'{ST}/q_p4v3d.json','w'),indent=1); json.dump(exp,open(f'{V}/results/v3d_expected.json','w'),indent=1); print(exp)
