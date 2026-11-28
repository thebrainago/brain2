import json,copy,pandas as pd
V='/workspace/bt_3m/v3'; E=f'{V}/stage_mt5e'; ST=f'{V}/stage_mt5f'; import os; os.makedirs(ST,exist_ok=True)
qx=json.load(open(f'{E}/q_p4v3e.json')); qu=json.load(open(f'{E}/q_p6v3e.json'))
def mk(q,pick,name,lot):
    j=copy.deepcopy([x for x in q['jobs'] if pick in x['name']][0]); src=j['params']['InpFileCsv'].split('\\')[-1]
    df=pd.read_csv(f'{E}/{src}'); df['lot']=lot; fn=f'v3f_{name}_mt5.csv'; df.to_csv(f'{ST}/{fn}',index=False,lineterminator='\n')
    j['name']='v3f_'+name; j['params']['InpLot0']=lot; j['params']['InpFileCsv']='brain2\\'+fn; j['group']='v3f'; return j
G=[mk(qx,'e1','g1_pdbreak_012',0.12),mk(qx,'e2','g2_lnor_012',0.12)]; U=[mk(qu,'e3','u10_orbd_25',2.5),mk(qu,'e4','u11_asiafail_43',4.3)]
for q,J,n in((qx,G,'q_p4v3f.json'),(qu,U,'q_p6v3f.json')):
    q=dict(q); q['jobs']=J; json.dump(q,open(f'{ST}/{n}','w'),indent=1)
print('ok')
