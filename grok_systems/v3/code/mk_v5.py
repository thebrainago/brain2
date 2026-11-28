import json,csv,os,copy
S='stage_mt5r5'; V='/workspace/bt_3m/v3'
TPL={'x1':('stage_mt5b','p4','v3b_B_x1_005'),'x4':('stage_mt5b','p4','v3b_B_x4_007'),'xs1':('stage_mt5b','p4','v3b_B_xs1_057'),'xs2':('stage_mt5b','p4','v3b_B_xs2_100'),
 'u1':('stage_mt5b','p6','v3b_B_u1_26'),'u2':('stage_mt5b','p6','v3b_B_u2_02'),'u6':('stage_mt5b','p6','v3b_B_u6_28'),'u7':('stage_mt5b','p6','v3b_B_u7_50'),
 'g1':('stage_mt5f','p4','v3f_g1_pdbreak_012'),'g2':('stage_mt5f','p4','v3f_g2_lnor_012'),'u10':('stage_mt5f','p6','v3f_u10_orbd_25'),'u11':('stage_mt5f','p6','v3f_u11_asiafail_25')}
G30={'x1':.04,'x4':.03,'g1':.04,'g2':.03,'xs1':.6,'xs2':.95,'u1':1.0,'u2':.3,'u6':1.0,'u7':1.6,'u10':1.8,'u11':.4}
G40={'x1':.06,'x4':.04,'g1':.06,'g2':.04,'xs1':.58,'xs2':1.0,'u1':1.1,'u2':.3,'u6':1.0,'u7':3.1,'u10':1.6,'u11':.6}
N4={'g1':.12,'g2':.12,'u10':2.5,'u11':2.0}
EXTRA={'x1':.09}
sets=[('G30',G30),('G40',G40),('N4',N4),('X1',EXTRA)]
Q={'p4':[],'p6':[]}; seen=set()
for tag,lots in sets:
    for k,lot in lots.items():
        d,slot,tn=TPL[k]; qs=json.load(open(f'{V}/{d}/q_{slot}v3{d[-1]}.json')) if False else None
        # find template job
        import glob
        job=None
        for f in glob.glob(f'{V}/stage_mt5*/q_{slot}v3*.json'):
            for j in json.load(open(f)).get('jobs',[]):
                if j['name']==tn: job=j; base=json.load(open(f))
        j=copy.deepcopy(job); old=j['params']['InpLot0']; nm=f'v5_{tag}_{k}_{str(lot).replace(".","")}'
        if (k,lot) in seen and tag!='N4': pass
        j['name']=nm; j['params']['InpLot0']=lot; j['group']='v5'; j['desc']=f'r5_{tag}_{k}'
        if j['params'].get('InpCatLoPct',0)>0: j['params']['InpCatLoPct']=round(j['params']['InpCatLoPct']*lot/old,3)
        j['expert']=('BRAIN\\BRAIN_XuLiLenh_r5.ex5' if slot=='p4' else 'sp500\\BRAIN_XuLiLenh_r5.ex5')
        scalp=k in ('xs1','xs2')
        if not scalp: j['params']['InpTuanKhoaGio']=21; j['params']['InpNghiLe']='2026.07.03;2026.09.07;2026.11.26'
        j['params']['InpFileCsv']=f'brain2\\{nm}_mt5.csv'
        rows=list(csv.reader(open(f'{V}/{d}/{tn}_mt5.csv'))); hdr=rows[0]; li=hdr.index('lot')
        for r in rows[1:]: r[li]=str(lot)
        with open(f'{S}/{nm}_mt5.csv','w',newline='') as fh:
            w=csv.writer(fh,lineterminator='\n'); w.writerows([hdr]+rows[1:])
        Q[slot].append(j)
for slot in Q:
    base={'slot':slot,'slot_dir':f'E:\\mt5_tester\\{slot}','min_ram_start':10,'min_ram_run':6,'timeout_min':100}
    # order: N4 first, then G30, G40, X1
    json.dump(dict(base,jobs=Q[slot]),open(f'{S}/q_{slot}v5.json','w'),indent=1)
    print(slot,[j['name'] for j in Q[slot]])
