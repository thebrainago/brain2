import sys,os,json,copy,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import mt5prep as M, portfolio as P
V='/workspace/bt_3m/v3'; O=f'{V}/mt5_ready'; ST=f'{V}/stage_mt5c'; os.makedirs(ST,exist_ok=True)
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
G=[job(gx1,'C_x4_004','x4_dzfade_nh8',0.04,nh(8,4),'PortC x4 0.04','30000'),job(gx1,'C_xs2_060','xs2_big3_emapull',0.6,sc(30000,8,0.6,100,13,90),'PortC xs2 0.6','30000')]
U=[job(uc,'C_u7_30','u7_swfade15',3.0,nu(60,8,4),'PortC u7 3.0','10000')]
for q,J,n in((qx,G,'q_p4v3c.json'),(qu,U,'q_p6v3c.json')):
    q=dict(q); q['jobs']=J; q['timeout_min']=100; json.dump(q,open(f'{ST}/{n}','w'),indent=1)
print(len(G),len(U))
