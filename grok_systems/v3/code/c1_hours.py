import sys,os,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); sys.path.insert(0,'/workspace/bt_3m/code')
import bt,scalp as SC,cands as CD,portfolio as P
D=bt.table('XAU'); SC.init('XAU'); raw={}
mg=dict(L0=0.03,mult=1.0,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=0,hedge=0,cd=30)
mgh=dict(L0=0.03,mult=1.3,gap=6,gstep=1.4,maxN=4,btp=3,trim=0,prune=1.5,hedge=1,hgap=18,hr=0.5,htp=5.0,cd=30)
h=D.index.hour.values
def run(s,m,l):
    q=bt.quick('XAU',bt.run('XAU',s,m,D=D),D.index); pe=bt.periods(D)
    qa=bt.quick('XAU',bt.run('XAU',s,m,D=D),D.index)
    print(f"{l:42s} net={q['net']:8.0f} dd={q['dd_pct']:5.1f}% nb={q['nb']:4d} months={list(q['months'].values())}")
for pn,p in (('vwapatr_3',P.X('vwapatr_3','none','all')),('vwapatr_3 adx',P.X('vwapatr_3','gt20','all')),('sweep c3',P.X('sw_fade_15_1.8','gt20','ldny'))):
    s=CD.build_sig(D,'XAU',p,raw)
    for mn,m in (('hedge',mgh),('nh',mg)):
        run(s,m,f'{pn} {mn} ALL')
        s2=s.copy(); s2[~((h>=7)&(h<9))&~((h>=12)&(h<15))&~((h>=18)&(h<22))]=0 if False else 0; 
        bad=((h>=9)&(h<12))|((h>=15)&(h<18)); s3=s.copy(); s3[bad]=0; run(s3,m,f'{pn} {mn} noUTC09-12,15-18')
        ldn=(h>=7)&(h<12); s4=s.copy(); s4[~ldn]=0; run(s4,m,f'{pn} {mn} London(7-12UTC)')
