# Coverage matrix: family x {fade,mom} x {basket,scalp} from all screen results. Writes v3/COVERAGE.md
import re,os,glob,pandas as pd,numpy as np
V='/workspace/bt_3m/v3'
F=[('Confluence pairs (đồng pha, 2 tín hiệu trong 30 bar)',r'^pair'),('Sweep (sw z)',r'(^sw_|sw30z|sw15z)'),('Delta z (dz)',r'(^dz_|dzstr)'),('Big prints / whale (g1–g3)',r'(^big\d|g[123]_\d+z|whale)'),
('CVD divergence / CVD lead',r'(cvddiv|div_|cvd_lead)'),('Absorption',r'(absorb|ad\d+z)'),('Imbalance / stacked',r'(^imb|imb\d+z|^stk)'),
('VWAP (z, ATR, cross, flow)',r'(vwapz|vwapatr|vwapx|vwapflow|vwap_cross)'),('Volume profile POC/VAH/VAL/naked POC/80% rule',r'(poc|va_|va80)'),
('Opening/session range (NY OR, IB, London OR, COMEX OR, Asia)',r'(orb|nyor|nyib|lnor|asia|opendrive|open_drive|open_fade)'),
('Prior day/week levels, NR day',r'(pd_|sweep_pd|sweep_day|sweep_as|pdbrk|pw_|day_ext|nr_)'),('Round numbers',r'rnd_'),
('Cross-asset lead-lag ES↔GC',r'(xlead|xdelta|ar\d+z)'),('Futures return / basis',r'(fz\d+z|basis)'),('Time-of-day anchors / news',r'(tod_|news)'),
('Volatility regime: squeeze/expansion/climax',r'(squeeze|rexp|vclimax|volspike)'),('Trend pullback (EMA/VWAP)',r'(emapull|pb_flow|vwap_trend)'),
('Gaps (overnight / weekend)',r'gap'),('IBS (prior-day close position)',r'ibs'),('60-bar high/low break/sweep',r'hl60'),('Placebo (control)',r'placebo')]
MOM=r'(_fade$(?!)|mom|break|brk|_go|drive|follow|catchup|trend|cvd_lead$|emapull|pb_flow|vwapx|vwap_cross|absorb_mom|whale_ext_absorb|rnd_break|squeeze)'
def mode(s):
    if s.startswith('pair'): return 'mom' if re.search(MOM,s.split('+')[0]) and re.search(MOM,s.split('+')[-1]) else 'fade'
    if s in ('emapull_fade','pb_flow_fade','vwap_trend_pb_fade'): return 'fade'
    return 'mom' if re.search(MOM,s) else 'fade'
rows=[]
def add(df,kind,src,sigcol='sig',score=None):
    for _,r in df.iterrows():
        s=re.sub(r'^n\d:','',str(r[sigcol])); 
        if kind=='basket': ok=(r['A']>0)&(r['B']>0)&(r['net']>0) if 'A' in r else (r['net']>0)
        else: ok=(r['A_e']>0)&(r['B_e']>0)&(r['e']>0)
        rows.append((s,kind,src,bool(ok)))
for a in ('XAU','US500'):
    for f in glob.glob(f'{V}/results/newsig*_{a}.parquet'): add(pd.read_parquet(f),'basket',os.path.basename(f))
    f=f'{V}/results/bsweep_{a}.parquet'
    if os.path.exists(f):
        B=pd.read_parquet(f); mc=[c for c in B.columns if c.startswith('m_')]; B['A']=B[mc[:3]].sum(1); B['B']=B[mc[3:]].sum(1); add(B,'basket','bsweep')
    for f in (f'{V}/results/scalp_{a}.parquet',f'{V}/results/r6/scalp2_{a}.parquet',f'{V}/results/r6/scalp2_n5_{a}.parquet'):
        if os.path.exists(f): add(pd.read_parquet(f,columns=['sig','e','A_e','B_e']),'scalp',os.path.basename(f))
    f=f'{V}/results/combo_{a}.parquet'
    if os.path.exists(f):
        C=pd.read_parquet(f,columns=['a','b','e','A_e','B_e']); C['sig']=C.a; add(C,'scalp','combo'); C['sig']=C.b; add(C,'scalp','combo')
R=pd.DataFrame(rows,columns=['sig','kind','src','ok']); R['mode']=R.sig.map(mode)
fam=[]
for s in R.sig: 
    m=[n for n,rx in F if re.search(rx,s)]; fam.append(m[0] if m else 'Other')
R['fam']=fam
G=R.groupby(['fam','mode','kind']).agg(n=('ok','size'),npass=('ok','sum')).reset_index()
cells=lambda f,m,k: (lambda x: f"{int(x.n.iloc[0])} cfg / {int(x.npass.iloc[0])} A&B+" if len(x) else 'CHƯA')(G[(G.fam==f)&(G['mode']==m)&(G.kind==k)])
L=['## COVERAGE — họ tín hiệu × {fade, momentum} × {basket, scalp SL/TP}','(số cấu hình đã chạy / số cấu hình dương cả A và B; "CHƯA" = chưa thử; cập nhật tự động bởi `code/cov.py`)','',
   '| Họ (family) | Fade·basket | Mom·basket | Fade·scalp | Mom·scalp |','|---|---|---|---|---|']
for n,_ in F+[('Other','')]:
    L.append(f'| {n} | '+' | '.join(cells(n,m,k) for k,m in (('basket','fade'),('basket','mom'),('scalp','fade'),('scalp','mom')))+' |')
L+=['','Gap qua đêm/cuối tuần: chỉ 3–15 sự kiện/6 tháng/asset → dưới ngưỡng 30 tín hiệu, KHÔNG đủ mẫu để kiểm (đã thử ở newsig4, bị loại vì mẫu). Placebo = nhóm đối chứng (không phải họ tín hiệu).','Không thể thử (thiếu dữ liệu): lead-lag NQ/SI/CL (KHÔNG CÓ dữ liệu), GEX / gamma flip / call-put walls (KHÔNG CÓ lịch sử), MBO/queue position (KHÔNG CÓ).',
    f'Tổng cấu hình đã chạy: basket {int((R.kind=="basket").sum()):,}, scalp {int((R.kind=="scalp").sum()):,} (gồm cả 2 tài sản).']
open(f'{V}/COVERAGE.md','w').write('\n'.join(L)); print('\n'.join(L))
