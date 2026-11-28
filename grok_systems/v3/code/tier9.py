import sys,os,json,numpy as np
sys.path.insert(0,'/workspace/bt_3m/v3/code'); sys.path.insert(0,'/workspace/bt_3m/v3/r4')
os.chdir('/workspace/bt_3m/v3/code')
import opt9 as O9
from opt9 import *
V='/workspace/bt_3m/v3'
R9=json.load(open(f'{V}/results/r6/opt9.json')); D9=json.load(open(f'{V}/results/r6/direct9.json'))
univs={'JOINT':UNIV,'XAU':XAU_U,'US500':US_U}
def pm(cent,ks,univ):
    LC=scale_lc(univ,CAP); ks=[k for k in ks]; P0=P(ks,CAP,LC); kv=kv_from_cent(P0,cent)
    PA=P(ks,CAP,LC,slice(0,iA)); PB=P(ks,CAP,LC,slice(iA,nb))
    return dict(full=P0.met(kv),A=PA.met(kv),B=PB.met(kv))
def maxtier(cent,ks,univ,lab,ddmax=19.5):
    best=None
    for f in np.arange(1.0,8.01,0.05):
        c={k:round(round(v*f/0.01)*0.01,2) for k,v in cent.items()}; c={k:v for k,v in c.items() if v>=0.01}
        r=mt5(c,lab)
        if r['dd_pct']<=ddmax: best=(f,c,r)
        else: break
    f,c,r=best; return f,c,r
out={}
for key,res in R9.items():
    mode=key.split('_')[0]; univ=univs[mode]; ks=res['sel']
    cent=res['cent']; ex=pm(cent,ks,univ)
    out[key]=dict(cent=cent,dropped=res['dropped'],net=res['mt5']['net'],dd=res['mt5']['dd_pct'],months=res['mt5']['months'],npos=res['mt5']['npos'],A=res['mt5']['A'],B=res['mt5']['B'],half=res['mt5']['half'],gap5=ex['full']['gap5'],sx2=ex['full']['sx_dd'],sxnet=ex['full']['sx_net'],pyA=ex['A']['net'],pyB=ex['B']['net'],nsys=len(cent),nsel=len(ks))
    print(key,round(res['mt5']['net'],1),'A/B py',round(ex['A']['net'],1),round(ex['B']['net'],1),flush=True)
# max tiers
for key in ['JOINT_aggressive','XAU_aggressive','JOINT_manual','XAU_manual']:
    mode=key.split('_')[0]; univ=univs[mode]; ks=R9[key]['sel']
    f,c,r=maxtier(R9[key]['cent'],ks,univ,key+'_max'); ex=pm(c,ks,univ)
    out[key+'_max']=dict(f=float(f),cent=c,dropped=[k for k in ks if k not in c],net=r['net'],dd=r['dd_pct'],months=r['months'],npos=r['npos'],A=r['A'],B=r['B'],gap5=ex['full']['gap5'],sx2=ex['full']['sx_dd'],sxnet=ex['full']['sx_net'],nsys=len(c),nsel=len(ks))
    print(key+'_max','x',round(f,2),round(r['net'],1),round(r['dd_pct'],1),'gap5',round(ex['full']['gap5']),'sx2',round(ex['full']['sx_dd'],1),flush=True)
json.dump(out,open(f'{V}/results/r6/cent_final.json','w'),indent=1,default=float)
# Min-lot sensitivity on the 100k books (direct): how many systems survive for different min-volume rules
J8=json.load(open(f'{V}/r4/joint8.json'))
sens={}
for lab in D9:
    l100=J8[lab]['lots']; row={}
    for nm,(mn,div) in {'exness0.01':(0.01,10),'xm_micro_mt4_0.01':(0.01,10),'xm_micro_mt5_0.1':(0.1,10)}.items():
        row[nm]=[k for k,L in l100.items() if L/div>=mn-1e-12]
    row['us500_min0.14']=[k for k,L in l100.items() if (k.startswith('u') and L/10>=0.14) or (not k.startswith('u') and L/10>=0.01)]
    sens[lab]=dict(n=len(l100),**row)
json.dump(sens,open(f'{V}/results/r6/cent_sens.json','w'),indent=1)
for lab,s in sens.items(): print(lab,s['n'],len(s['exness0.01']),len(s['xm_micro_mt5_0.1']),len(s['us500_min0.14']))
