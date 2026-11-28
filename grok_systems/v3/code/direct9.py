# Round 8: 100 USD (=10,000 US cents) cent-account recompute.
# Mapping 100k std lots L -> 100 USD: exposure x1/1000.  Gold: 1 std lot=100 oz, Exness cent lot = 1 oz => cent_lot = L/10.
# US500: assumption (Exness: 1 cent lot = 0.01 std lot, std contract size 1 => $0.01/pt per cent lot) => cent_lot = L/10.
# Direct mapping: raw<min -> dropped; else round to nearest step. MT5 joint from existing deals scaled linearly.
import sys,json,os
sys.path.insert(0,'/workspace/bt_3m/v3/code'); sys.path.insert(0,'/workspace/bt_3m/v3/r4')
os.chdir('/workspace/bt_3m/v3/code')
import numpy as np
import opt8 as O8
os.chdir('/workspace/bt_3m/v3/r4')
import joint5 as J
from joint7 import RUN
V='/workspace/bt_3m/v3'
STEP=0.01; MINLOT=0.01; CAP=100.0
O=json.load(open(f'{V}/results/r6/opt8.json')); J8=json.load(open(f'{V}/r4/joint8.json'))
def mt5(lots_std,lab):
    names=[RUN[k][0] for k in lots_std]; sc={RUN[k][0]:lots_std[k]/RUN[k][1] for k in lots_std}
    r=J.joint(names,sc,lab,cap=CAP); h=J.joint(names,{n:v*0.5 for n,v in sc.items()},lab,cap=CAP)
    r['half']=dict(net=h['net'],dd_pct=h['dd_pct']); return r
def pyst(lots_std,ks):
    P=O8.P(ks,CAP,O8.scale_lc(ks,CAP)); kv=np.array([lots_std.get(k,0.0)/O8.U[k]['lot0'] for k in ks]); m=P.met(kv)
    return m
def mapdirect(lots100k,minlot=MINLOT,step=STEP,div=10.0):
    keep={};drop={};near={}
    for k,L in lots100k.items():
        raw=L/div
        if raw<minlot-1e-12: drop[k]=round(raw,4); continue
        c=round(round(raw/step)*step,4); keep[k]=c
        if abs(c-raw)/raw>0.25: near[k]=(round(raw,4),c)
    return keep,drop,near
BOOKS=[('JOINT_100k','joint'),('XAU_100k','xau'),('US500_100k','us')]
TIERS=[('GREEDY_conservative','An toàn'),('GREEDY_balanced','Cân bằng'),('GREEDY_aggressive','Mạnh tay'),('MANUAL_conservative','Đánh tay')]
if __name__=='__main__':
    out={}
    for mode,tag in BOOKS:
        for key,vn in TIERS:
            lab=f'{mode}_{key}_robust'
            if lab not in J8: continue
            l100=J8[lab]['lots']   # official (trimmed if needed) std lots at 100k
            keep,drop,near=mapdirect(l100)
            if not keep:
                out[lab]=dict(vn=vn,keep={},drop=drop,near=near,n=0,note='KHÔNG ĐẠI DIỆN ĐƯỢC'); print(lab,'ALL DROPPED',drop); continue
            std={k:c*0.01 for k,c in keep.items()}   # cent lot -> std lot (x0.01)
            r=mt5(std,lab); m=pyst(std,list(std))
            out[lab]=dict(vn=vn,keep=keep,drop=drop,near=near,n=len(keep),n100k=len(l100),net_usd=r['net'],net_cent=r['net']*100,dd=r['dd_pct'],A=r['A'],B=r['B'],months=r['months'],npos=r['npos'],half=r['half'],py=m)
            # compare with full 100k book
            out[lab]['ref100k']=dict(net=J8[lab]['net'],dd=J8[lab]['dd_pct'])
            print(lab,'keep',len(keep),'/',len(l100),'net$',round(r['net'],1),'dd',round(r['dd_pct'],1),'m+',r['npos'],'gap5',round(m['gap5'],1),'sx2',round(m['sx_dd'],1),'| drop',drop,flush=True)
    json.dump(out,open(f'{V}/results/r6/direct9.json','w'),indent=1,default=float)
