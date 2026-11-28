import sys,os,json,copy,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import mt5prep as M, portfolio as P
V='/workspace/bt_3m/v3'; O=f'{V}/mt5_ready'; ST=f'{V}/stage_mt5b'; os.makedirs(ST,exist_ok=True)
X=P.X
# new entries for u6 (dz_mom_5_1.5 none/all) with u2-style mgmt
for nm,pg in (('u6_dzmom',X('dz_mom_5_1.5','none','all')),('u7_swfade15',X('sw_fade_15_1.5','none','all'))):
    if not os.path.exists(f'{O}/{nm}_mt5.csv'):
        r=M.basket('US500',nm,pg,P.mgu['u2']); print(nm,r['py_net'],r['py_dd_pct'])
        d=pd.read_csv(f'{O}/{nm}_vao.csv'); d['gia']=d.gia_bid_open; d[['thoi_gian','ma','chieu','gia','nguon','lot']].to_csv(f'{O}/{nm}_mt5.csv',index=False,lineterminator='\n')
qx=json.load(open(f'{V}/ref/q_p4e.json')); qu=json.load(open(f'{V}/ref/q_p6e.json')); gx=qx['jobs'][0]; gx1=qx['jobs'][1]; uc=qu['jobs'][0]
def job(tmpl,name,base_csv,lot,over,desc,dep):
    df=pd.read_csv(f'{O}/{base_csv}_mt5.csv'); df['lot']=lot; fn=f'v3b_{name}_mt5.csv'; df.to_csv(f'{ST}/{fn}',index=False,lineterminator='\n')
    j=copy.deepcopy(tmpl); j['name']='v3b_'+name; j['desc']=desc; j['group']='v3b'; j['from']='2026.06.01'; j['to']='2026.11.27'; j['deposit']=dep
    j['params'].update(over); j['params']['InpLot0']=lot; j['params']['InpFileCsv']='brain2\\'+fn; return j
def nh(g,tp,N=4): return dict(InpKieuLot=0,InpBuocGia=g,InpGianBuoc=1.4,InpMaxTang=N,InpTPGia=tp,InpHedgeKhiLoPct=0,InpHedgeTiLe=1.0)
def sc(dep,sl,lot,pv,tp,hold): return dict(InpKieuLot=0,InpNhoi=0,InpMaxTang=1,InpTPGia=tp,InpCatLoPct=round(sl*lot*pv/dep*100,4),InpGiuToiDaNen=hold,InpHedgeKhiLoPct=0,InpHedgeTiLe=1.0)
def nu(g,tp,N): return dict(InpKieuLot=0,InpBuocGia=g,InpGianBuoc=1.4,InpMaxTang=N,InpTPGia=tp,InpHedgeKhiLoPct=0,InpHedgeTiLe=1.0)
G=[ # name, base csv, lot
 job(gx1,'A_x1_009','x1_swfade_nh8',0.09,nh(8,4),'PortA x1 0.09','30000'),
 job(gx,'A_x2_010','x2_swfade_c3',0.10,dict(InpHedgeKhiLoPct=round(0.36*0.10/0.03,2)),'PortA x2 0.10 c3 hedge','30000'),
 job(gx1,'B_x1_005','x1_swfade_nh8',0.05,nh(8,4),'PortB x1 0.05','30000'),
 job(gx1,'B_x4_007','x4_dzfade_nh8',0.07,nh(8,4),'PortB x4 0.07','30000'),
 job(gx1,'B_xs1_057','xs1_xlead_big2',0.57,sc(30000,8,0.57,100,8,90),'PortB xs1 scalp 0.57','30000'),
 job(gx1,'B_xs2_100','xs2_big3_emapull',1.0,sc(30000,8,1.0,100,13,90),'PortB xs2 scalp 1.0','30000'),
 job(gx1,'S_x1_006','x1_swfade_nh8',0.06,nh(8,4),'single x1 0.06 (DD17)','30000')]
U=[job(uc,'A_u1_10','u1_swfade_nh',1.0,nu(60,6,3),'PortA u1 1.0','10000'),
 job(uc,'A_u7_10','u7_swfade15',1.0,nu(60,8,4),'PortA u7 1.0','10000'),
 job(uc,'B_u1_26','u1_swfade_nh',2.6,nu(60,6,3),'PortB u1 2.6','10000'),
 job(uc,'B_u2_02','u2_absorbfade5',0.2,nu(60,8,4),'PortB u2 0.2','10000'),
 job(uc,'B_u6_28','u6_dzmom',2.8,nu(60,8,4),'PortB u6 2.8','10000'),
 job(uc,'B_u7_50','u7_swfade15',5.0,nu(60,8,4),'PortB u7 5.0','10000'),
 job(uc,'S_u1_38','u1_swfade_nh',3.8,nu(60,6,3),'single u1 3.8 (DD17)','10000')]
for q,J,n in((qx,G,'q_p4v3b.json'),(qu,U,'q_p6v3b.json')):
    q=dict(q); q['jobs']=J; q['timeout_min']=100; json.dump(q,open(f'{ST}/{n}','w'),indent=1)
print(len(G),len(U))
