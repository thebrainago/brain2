# Round 9 (t158u): min lot 0.10 gold / 0.14 US500 (Exness), 100 USD feasibility + min capital.
import sys, os, json, itertools, numpy as np
sys.path.insert(0,'/workspace/bt_3m/v3/code'); sys.path.insert(0,'/workspace/bt_3m/v3/r4')
os.chdir('/workspace/bt_3m/v3/code')
import opt8 as O8
from opt8 import P, scale_lc, UNIV, XAU_U, US_U, MANUAL, iA, nb, U
os.chdir('/workspace/bt_3m/v3/r4')
import joint5 as J
from joint7 import RUN
V='/workspace/bt_3m/v3'
J8=json.load(open(f'{V}/r4/joint8.json'))
F=json.load(open(f'{V}/results/r6/cent_final.json'))
MIN_G=0.10; MIN_U=0.14; STEP=0.01
# assumption: 0.14 is official Exness US500 min (Help Center Indices 13/11/2026) and user t158u;
# gold min 0.10 = XM Micro MT5; if user's Exness gold is also 0.14 we also report that sensitivity.

def is_us(k): return k.startswith('u')
def minlot(k): return MIN_U if is_us(k) else MIN_G
def cent_from_100k(L, C): return L * C / 1000.0   # 1 cent lot = 0.01 std
def std_from_cent(c): return c * 0.01
def rndup(c, mn, step=STEP):
    if c < mn - 1e-12: return 0.0
    # already >= min: round to nearest step, but not below min
    r=round(round(c/step)*step, 2)
    if r < mn: r=mn
    return r
def mt5(cent, lab, cap):
    std={k:std_from_cent(v) for k,v in cent.items() if v>0}
    if not std: return dict(net=0,dd_pct=0,months=[],npos=0,A=0,B=0,n=0,half=dict(net=0,dd_pct=0))
    names=[RUN[k][0] for k in std]; sc={RUN[k][0]:std[k]/RUN[k][1] for k in std}
    r=J.joint(names,sc,lab,cap=cap)
    h=J.joint(names,{n:v*0.5 for n,v in sc.items()},lab,cap=cap)
    r['half']=dict(net=h['net'],dd_pct=h['dd_pct']); return r
def pyst(cent, cap, ks=None):
    ks=ks or list(cent)
    # use a large-enough LC so met() doesn't cap
    LC={k:max(scale_lc([k], max(cap,1000.)).get(k,1.0), std_from_cent(cent[k])*2, 10.0) for k in ks}
    # actually scale_lc expects universe; simpler: set LC high
    LC={k:100.0 for k in ks}
    P0=P(ks,cap,LC); kv=np.array([std_from_cent(cent[k])/U[k]['lot0'] for k in ks])
    PA=P(ks,cap,LC,slice(0,iA)); PB=P(ks,cap,LC,slice(iA,nb))
    return dict(full=P0.met(kv), A=PA.met(kv), B=PB.met(kv))

# Official 100k books
BOOKS=[
    ('JOINT','An toàn','JOINT_100k_GREEDY_conservative_robust'),
    ('JOINT','Cân bằng','JOINT_100k_GREEDY_balanced_robust'),
    ('JOINT','Mạnh tay','JOINT_100k_GREEDY_aggressive_robust'),
    ('JOINT','Đánh tay','JOINT_100k_MANUAL_conservative_robust'),
    ('XAU','An toàn','XAU_100k_GREEDY_conservative_robust'),
    ('XAU','Cân bằng','XAU_100k_GREEDY_balanced_robust'),
    ('XAU','Mạnh tay','XAU_100k_GREEDY_aggressive_robust'),
    ('XAU','Đánh tay','XAU_100k_MANUAL_conservative_robust'),
    ('US500','An toàn','US500_100k_GREEDY_conservative_robust'),
    ('US500','Cân bằng','US500_100k_GREEDY_balanced_robust'),
    ('US500','Mạnh tay','US500_100k_GREEDY_aggressive_robust'),
]
# Retuned 100 USD books from opt9/cent_final
RETUNE={
    ('JOINT','An toàn'):'JOINT_conservative',
    ('JOINT','Cân bằng'):'JOINT_balanced',
    ('JOINT','Mạnh tay'):'JOINT_aggressive',
    ('JOINT','Đánh tay'):'JOINT_manual',
    ('XAU','An toàn'):'XAU_conservative',
    ('XAU','Cân bằng'):'XAU_balanced',
    ('XAU','Mạnh tay'):'XAU_aggressive',
    ('XAU','Đánh tay'):'XAU_manual',
    ('US500','An toàn'):'US500_conservative',
    ('US500','Cân bằng'):'US500_balanced',
    ('US500','Mạnh tay'):'US500_aggressive',
}

def cap_all(lots100k, min_g=MIN_G, min_u=MIN_U):
    # min C so every system in the 100k book hits its min lot when scaled
    need=[]
    for k,L in lots100k.items():
        mn=min_u if is_us(k) else min_g
        if L<=0: continue
        need.append((k, 1000.0*mn/L))
    kmax,cmax=max(need, key=lambda x:x[1])
    return dict(C=cmax, bottleneck=kmax, per={k:round(c,1) for k,c in need})

out=dict(mins=dict(gold=MIN_G, us500=MIN_U, step=STEP, note='US500 min 0.14 = Exness official + user t158u; gold 0.10 = XM Micro MT5. If gold Exness also 0.14, see gold14 sensitivity.'))

# ---------- 1) 100 USD: drop below min (from official 100k scaled AND from retuned) ----------
CAP=100.0
feas={}
for book,tier,lab in BOOKS:
    lots=J8[lab]['lots']
    keep={}; drop={}
    for k,L in lots.items():
        raw=cent_from_100k(L, CAP); mn=minlot(k)
        if raw+1e-12 < mn:
            drop[k]=round(raw,4)
        else:
            keep[k]=rndup(raw,mn)
    rec=dict(src='scale100k', keep=keep, drop=drop, nkeep=len(keep), n0=len(lots))
    if keep:
        r=mt5(keep, f'{lab}_drop100', CAP); py=pyst(keep, CAP)
        rec.update(net=r['net'], dd=r['dd_pct'], months=r['months'], npos=r['npos'], A=r['A'], B=r['B'],
                   gap5=py['full']['gap5'], sx2=py['full']['sx_dd'], sxnet=py['full']['sx_net'], pyA=py['A']['net'], pyB=py['B']['net'])
    else:
        rec.update(net=0,dd=0,months=[],npos=0,A=0,B=0,gap5=None,sx2=None,note='KHÔNG hệ nào đạt min lot')
    feas[f'{book}_{tier}_scale']=rec
    print('SCALE',book,tier,'keep',len(keep),'/',len(lots), 'net',round(rec.get('net',0),1),'dd',round(rec.get('dd',0) or 0,1),'drop',list(drop), flush=True)

# retuned drop
for (book,tier),key in RETUNE.items():
    cent=F[key]['cent']; drop={}; keep={}
    for k,c in cent.items():
        mn=minlot(k)
        if c+1e-12 < mn: drop[k]=c
        else: keep[k]=rndup(c,mn)
    rec=dict(src='retune', keep=keep, drop=drop, nkeep=len(keep), n0=len(cent)+len(F[key].get('dropped') or []))
    if keep:
        r=mt5(keep, f'{key}_drop100', CAP); py=pyst(keep, CAP)
        rec.update(net=r['net'], dd=r['dd_pct'], months=r['months'], npos=r['npos'], A=r['A'], B=r['B'],
                   gap5=py['full']['gap5'], sx2=py['full']['sx_dd'], sxnet=py['full']['sx_net'])
    else:
        rec.update(net=0,dd=0,npos=0,gap5=None,sx2=None,note='KHÔNG hệ nào đạt min lot')
    feas[f'{book}_{tier}_retune']=rec
    print('RETUNE',book,tier,'keep',len(keep),'/',rec['n0'], 'net',round(rec.get('net',0),1),'dd',round(rec.get('dd') or 0,1),'keep',keep,'drop',list(drop), flush=True)

# ---------- force every system of a book up to min lot at 100 USD (dangerous) ----------
force={}
for book,tier,lab in BOOKS:
    lots=J8[lab]['lots']
    forced={k: max(minlot(k), rndup(cent_from_100k(L,CAP), minlot(k)) if cent_from_100k(L,CAP)+1e-12>=minlot(k) else minlot(k)) for k,L in lots.items()}
    # force ALL to at least min, including those below
    forced={k: minlot(k) if cent_from_100k(L,CAP)<minlot(k) else rndup(cent_from_100k(L,CAP), minlot(k)) for k,L in lots.items()}
    r=mt5(forced, f'{lab}_force100', CAP); py=pyst(forced, CAP)
    rec=dict(cent=forced, net=r['net'], dd=r['dd_pct'], months=r['months'], npos=r['npos'], A=r['A'], B=r['B'],
             gap5=py['full']['gap5'], sx2=py['full']['sx_dd'], n=len(forced),
             oversized={k:round(minlot(k)/(cent_from_100k(lots[k],CAP)+1e-12),2) for k in lots if cent_from_100k(lots[k],CAP)<minlot(k)})
    force[f'{book}_{tier}']=rec
    print('FORCE',book,tier,'net',round(r['net'],1),'dd',round(r['dd_pct'],1),'gap5',round(py['full']['gap5']),'sx2',round(py['full']['sx_dd'],1),'over',rec['oversized'], flush=True)

# ---------- individual systems at min lot, cap=100 ----------
# universe of systems that appear in any official book
sys=sorted({k for _,_,lab in BOOKS for k in J8[lab]['lots']})
solo={}
for k in sys:
    c=minlot(k)
    r=mt5({k:c}, f'solo_{k}', CAP); py=pyst({k:c}, CAP)
    solo[k]=dict(cent=c, net=r['net'], dd=r['dd_pct'], months=r['months'], npos=r['npos'], A=r['A'], B=r['B'],
                 gap5=py['full']['gap5'], sx2=py['full']['sx_dd'], sxnet=py['full']['sx_net'])
    print('SOLO',k,'lot',c,'net',round(r['net'],1),'dd',round(r['dd_pct'],1),'gap5',round(py['full']['gap5']),'sx2',round(py['full']['sx_dd'],1),'m+',r['npos'], flush=True)

# ---------- min capital for full books ----------
caps={}
for book,tier,lab in BOOKS:
    lots=J8[lab]['lots']
    a=cap_all(lots, MIN_G, MIN_U)
    b=cap_all(lots, 0.14, 0.14)  # if gold also 0.14
    c=cap_all(lots, 0.10, 0.10)  # if both 0.10
    caps[f'{book}_{tier}']=dict(C_g10_u14=round(a['C'],0), bot=a['bottleneck'], per={k:round(v) for k,v in a['per'].items()},
                               C_both14=round(b['C'],0), bot14=b['bottleneck'],
                               C_both10=round(c['C'],0), bot10=c['bottleneck'], n=len(lots))
    print('CAP',book,tier,'C_0.10/0.14',round(a['C']),'bot',a['bottleneck'],'C_both14',round(b['C']),'C_both10',round(c['C']), flush=True)

# ---------- at selected capitals, drop-below-min on official lots, MT5 ----------
cap_grid=[100,250,500,700,1000,2000,5000,10000]
grid={}
for C in cap_grid:
    for book,tier,lab in BOOKS:
        lots=J8[lab]['lots']; keep={}; drop=[]
        for k,L in lots.items():
            raw=cent_from_100k(L,C); mn=minlot(k)
            if raw+1e-12>=mn: keep[k]=rndup(raw,mn)
            else: drop.append(k)
        key=f'{book}_{tier}_{C}'
        rec=dict(C=C,keep=keep,drop=drop,nkeep=len(keep),n0=len(lots))
        if keep:
            r=mt5(keep, key, float(C)); py=pyst(keep, float(C))
            rec.update(net=r['net'], dd=r['dd_pct'], npos=r['npos'], months=r['months'], gap5=py['full']['gap5'], sx2=py['full']['sx_dd'])
        grid[key]=rec
    print('GRID C=',C,'done', flush=True)

# ---------- starter search: 2-4 gold scalps + optional 1-2 US at 100 USD, lots = max(min, scaled conservative or aggressive) ----------
# We'll evaluate predefined high-quality sets at C=100 with lot = min (or scaled if larger)
starters=[]
cands_g=['xs7','xs10','xs2','xs6','xs1','xs5','xs8','xs4']  # largest / best known scalps
cands_u=['u13','u12','u2','u15']
# also compute a few explicit baskets
def eval_set(name, cent, cap=100.0):
    r=mt5(cent, name, cap); py=pyst(cent, cap)
    return dict(name=name, cent=cent, cap=cap, net=r['net'], dd=r['dd_pct'], months=r['months'], npos=r['npos'],
                A=r['A'], B=r['B'], gap5=py['full']['gap5'], sx2=py['full']['sx_dd'], n=len(cent),
                half=r['half'])

# Gold singles already in solo. Combos:
sets=[]
# 1) US500-only official conservative/balanced already in feas
# 2) best 1 gold
for k in cands_g:
    sets.append((f'gold1_{k}', {k: MIN_G}))
# 3) best 2 gold
for a,b in itertools.combinations(cands_g[:6],2):
    sets.append((f'gold2_{a}_{b}', {a:MIN_G,b:MIN_G}))
# 4) best 3-4 gold (selected, not all combos of 8)
for trip in itertools.combinations(['xs7','xs10','xs2','xs6','xs1'],3):
    sets.append((f'gold3_{"_".join(trip)}', {k:MIN_G for k in trip}))
sets.append(('gold4_xs7_xs10_xs2_xs6', {k:MIN_G for k in ['xs7','xs10','xs2','xs6']}))
sets.append(('gold4_xs7_xs10_xs2_xs1', {k:MIN_G for k in ['xs7','xs10','xs2','xs1']}))
# 5) 1 gold + US500 conservative lots (already >= min) 
us_cons={k:F['US500_conservative']['cent'][k] for k in F['US500_conservative']['cent']}
# maybe too much combined. try 2 US + 1-2 gold
for g in ['xs7','xs10']:
    sets.append((f'g1us5_{g}', {**{g:MIN_G}, **us_cons}))
sets.append(('g2us5_xs7_xs10', {**{'xs7':MIN_G,'xs10':MIN_G}, **us_cons}))
# smaller US: just u13+u12 at conservative lots plus 1 gold
us2={'u13':us_cons['u13'],'u12':us_cons['u12']}
sets.append(('g1us2_xs7', {**{'xs7':MIN_G}, **us2}))
sets.append(('g2us2_xs7_xs10', {**{'xs7':MIN_G,'xs10':MIN_G}, **us2}))
# US500 2-system only
sets.append(('us2_u13_u12', us2))
sets.append(('us1_u13', {'u13':us_cons['u13']}))
sets.append(('us1_u12', {'u12':us_cons['u12']}))

starter_res=[]
for name,cent in sets:
    rec=eval_set(name,cent,100.0)
    starter_res.append(rec)
    if rec['dd']<=20 or rec['n']<=2:
        print('SET',name,'net',round(rec['net'],1),'dd',round(rec['dd'],1),'gap5',round(rec['gap5']),'sx2',round(rec['sx2'],1),'m+',rec['npos'], flush=True)

# min capital for starter sets: scale their "design" lots from 100k official if available, else from aggressive gold / conservative US
# For a chosen starter, C_min so each system can be at least min lot at the SAME relative weights as 100k book (use aggressive XAU or conservative joint/US)
# Also: C such that running each at exactly min lot keeps DD<=19.5 (search cap downward... actually at min lot, DD_abs is fixed, DD% = DD_abs/C so C_min_dd = DD_abs/0.195)

def ddabs_at_min(ks):
    cent={k:minlot(k) for k in ks}
    r=mt5(cent, 'ddabs_'+'_'.join(ks), 100.0)  # cap only affects dd_pct
    return r['dd_pct']/100.0*100.0, r  # dd_abs

# For interesting starters, compute C to have DD<=19.5% when all at min lot (C = dd_abs/0.195), and C to match 100k-relative weights with all >= min
extra={}
interesting=[
    ['xs7'],['xs10'],['xs7','xs10'],['xs7','xs10','xs2'],['xs7','xs10','xs2','xs6'],
    ['xs1','xs2','xs7','xs10'],
    ['u13'],['u12'],['u13','u12'],
    ['u13','u12','u2','up1','up2'],
    ['xs7','u13'],
    ['xs7','xs10','u13','u12'],
]
for ks in interesting:
    cent={k:minlot(k) for k in ks}
    r=mt5(cent,'cmin_'+'_'.join(ks), 100.0)
    dd_abs=r['dd_pct']/100.0*100.0
    C_dd20=dd_abs/0.195 if dd_abs>0 else 100.0
    # also C to keep 100k-relative (use XAU/JOINT/US official conservative or aggressive average)
    # find lots from XAU aggressive or US conservative or joint conservative
    lots_ref={}
    for lab in ['XAU_100k_GREEDY_aggressive_robust','US500_100k_GREEDY_conservative_robust','JOINT_100k_GREEDY_conservative_robust','XAU_100k_MANUAL_conservative_robust','JOINT_100k_MANUAL_conservative_robust']:
        for k in ks:
            if k in J8[lab]['lots'] and k not in lots_ref:
                lots_ref[k]=J8[lab]['lots'][k]
    if len(lots_ref)==len(ks):
        Cm=cap_all(lots_ref)
        C_weight=Cm['C']
    else:
        C_weight=None
    py=pyst(cent, 100.0)
    # at C_dd20, gap and sx scale: gap% and sx% scale as 1/C because abs is fixed (lots fixed at min)
    extra['_'.join(ks)]=dict(ks=ks, dd_abs=dd_abs, net_at_minlot=r['net'],  # net is in USD, independent of cap!
                             C_for_DD19_5=round(C_dd20,0),
                             C_for_weights=round(C_weight,0) if C_weight else None,
                             gap5_at_100=py['full']['gap5'], sx2_at_100=py['full']['sx_dd'],
                             npos=r['npos'], months=r['months'],
                             # at C_dd20, gap% = gap5_at_100 * 100 / C_dd20
                             gap5_at_Cdd=py['full']['gap5']*100/C_dd20 if C_dd20 else None,
                             sx2_at_Cdd=py['full']['sx_dd']*100/C_dd20 if C_dd20 else None)
    print('CMIN',ks,'dd_abs',round(dd_abs,1),'C_DD19.5',round(C_dd20),'C_w',C_weight,'gap@100',round(py['full']['gap5']), flush=True)

out.update(feas=feas, force=force, solo=solo, caps=caps, grid={k:v for k,v in grid.items()}, starters=starter_res, cmin=extra)
json.dump(out, open(f'{V}/results/r6/minlot10.json','w'), indent=1, default=float)
print('WROTE minlot10.json')
