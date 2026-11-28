# MT5 joint DD for round-6 scenarios: linear lot scaling of MT5 per-system runs (merged equity by timestamp).
import json,joint5 as J
RUN={'gp1':('v7_gp1_006',.06),'gp2':('v7_gp2_006',.06),'gp3':('v7_gp3_005',.05),'up1':('v7_up1_20',2.0),'up2':('v7_up2_20',2.0),'up3':('v7_up3_10',1.0),'xs8':('v7_xs8_03',.3),'xs9':('v7_xs9_03',.3),'xs10':('v7_xs10_03',.3),'g1':('v5_G30_g1_004',.04),'g2':('v5_G30_g2_003',.03),'u10':('v5_G30_u10_18',1.8),'u11':('v5_G30_u11_04',.4),'u1':('v5_G30_u1_10',1.0),'u2':('v5_G30_u2_03',.3),'u6':('v5_G30_u6_10',1.0),'u7':('v5_G30_u7_16',1.6),
 'x1':('v5_G30_x1_004',.04),'x4':('v5_G30_x4_003',.03),'xs1':('v5_G30_xs1_06',.6),'xs2':('v5_G30_xs2_095',.95),'g3':('v5_n_g3_006',.06),'g5':('v5_n_g5_004',.04),'u12':('v5_n_u12_30',3.0),'u13':('v5_n_u13_30',3.0),
 'g7':('v6_g7_004',.04),'u15':('v6_u15_15',1.5),'u16':('v6_u16_10',1.0),'u17':('v6_u17_20',2.0),'u18':('v6_u18_15',1.5),'u19':('v6_u19_15',1.5),'xs3':('v6_xs3_03',.3),'xs4':('v6_xs4_03',.3),'xs5':('v6_xs5_03',.3),'xs6':('v6_xs6_03',.3),'xs7':('v6_xs7_03',.3)}
def mt5(lots,lab):
    names=[RUN[k][0] for k in lots]; sc={RUN[k][0]:lots[k]/RUN[k][1] for k in lots}
    r=J.joint(names,sc,lab); h=J.joint(names,{n:v*0.5 for n,v in sc.items()},lab); r['half']=dict(net=h['net'],dd_pct=h['dd_pct']); r['lots']=lots; return r
if __name__=='__main__':
    O=json.load(open('../results/r6/opt7.json')); out={}
    def pr(lab,r): print(lab,'net',round(r['net']),'dd',round(r['dd_pct'],1),'A/B',round(r['A']),round(r['B']),'m+',r['npos'],'half',round(r['half']['net']),round(r['half']['dd_pct'],1),flush=True)
    for key,v in O.items():
        if key=='greedy': continue
        l=v['robust']['lots']; r=mt5(l,f'{key}_robust'); out[f'{key}_robust']=r; pr(f'{key}_robust',r)
        # x-lot tiers while MT5 DD<19%
        for m in ((1.2,1.4,1.5,1.7,2.0) if 'aggressive' in key else (2.5,3,4,5) if 'MANUAL' in key else ()):
            lm={k:x*m for k,x in l.items()}; r=mt5(lm,f'{key}_x{m}')
            if r['dd_pct']>19.5: break
            out[f'{key}_x{m}']=r; pr(f'{key}_x{m}',r)
    json.dump(out,open('joint7.json','w'),indent=1)
