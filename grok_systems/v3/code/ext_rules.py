# Re-test external rules on v3 tables (my interpretation). Costs: spread_px*1.5 round trip. adverse-first.
import sys,os,numpy as np,pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); import bt
def sim(h,l,c,i0,d,ent,sl,tp,iend,spr):
    # enter at bar i0 close price ent; walk bars i0+1.. iend; SL first (adverse-first)
    for j in range(i0+1,iend+1):
        if d>0:
            if l[j]<=sl: return j,(sl-ent)-1.5*spr
            if h[j]>=tp: return j,(tp-ent)-1.5*spr
        else:
            if h[j]>=sl: return j,(ent-sl)-1.5*spr
            if l[j]<=tp: return j,(ent-tp)-1.5*spr
    return iend,d*(c[iend]-ent)-1.5*spr
def stats(rows,label):
    if not rows: print(label,'n=0');return
    r=pd.DataFrame(rows,columns=['t','R','pnl']); n=len(r); R=r.R.values
    g=R[R>0].sum(); b=-R[R<=0].sum(); r['m']=pd.to_datetime(r.t).dt.strftime('%Y-%m')
    A=r[pd.to_datetime(r.t)<pd.Timestamp('2026-08-20',tz='UTC')].R; B=r[pd.to_datetime(r.t)>=pd.Timestamp('2026-08-20',tz='UTC')].R
    print(f"{label}: n={n} meanR={R.mean():+.3f} PF={g/b if b>0 else 9:.2f} win={np.mean(R>0):.0%} A(n={len(A)})={A.mean():+.3f} B(n={len(B)})={B.mean():+.3f} t={R.mean()/(R.std()/np.sqrt(n)):.2f} months+={int((r.groupby('m').R.sum()>0).sum())}/{r.m.nunique()}")
def orb(D,rr=2.0,trend=True,orm=15):
    ny=D.index.tz_convert('America/New_York'); h=D.high.values;l=D.low.values;c=D.close.values; sp=D.spread_px.values
    h1=D.close.resample('1h').last().dropna(); e200=h1.ewm(span=200,adjust=False).mean().shift(1).reindex(D.index,method='ffill').values
    day=ny.normalize(); rows=[]
    for dd in pd.unique(day):
        ix=np.nonzero((day==dd))[0]; tm=ny[ix].hour*60+ny[ix].minute
        o=ix[(tm>=570)&(tm<570+orm)]
        if len(o)<orm-3: continue
        hi=h[o].max(); lo=l[o].min(); mid=(hi+lo)/2; after=ix[(tm>=570+orm)&(tm<960)]
        for j in after:
            d=0
            if c[j]>hi: d=1
            elif c[j]<lo: d=-1
            if d==0: continue
            if trend and np.isfinite(e200[j]) and ((d>0)!=(c[j]>e200[j])): break  # first breakout against trend -> no trade that day
            R0=abs(c[j]-mid); tp=c[j]+d*rr*R0
            jj,p=sim(h,l,c,j,d,c[j],mid,tp,after[-1],sp[j]); rows.append((D.index[j],p/R0,p)); break
    return rows
def fvg(D,rr=2.0,trend=False,tf=5):
    M=D.resample(f'{tf}min').agg(dict(open='first',high='max',low='min',close='last',spread_px='mean')).dropna()
    ny=M.index.tz_convert('America/New_York'); tm=ny.hour*60+ny.minute
    h=M.high.values;l=M.low.values;c=M.close.values;o=M.open.values;sp=M.spread_px.values
    h1=D.close.resample('1h').last().dropna(); e=h1.ewm(span=50,adjust=False).mean().shift(1).reindex(M.index,method='ffill').values
    rows=[];last=-99
    for i in range(2,len(M)-40):
        if not (570<=tm[i]<690): continue   # NY first 2h
        d=0
        if l[i]>h[i-2] and c[i-1]>o[i-1]: d=1;sl=l[i-2]
        elif h[i]<l[i-2] and c[i-1]<o[i-1]: d=-1;sl=h[i-2]
        if d==0 or i-last<6: continue
        if trend and np.isfinite(e[i]) and ((d>0)!=(c[i]>e[i])): continue
        R0=abs(c[i]-sl)
        if R0<=0 or R0>8*np.nanmean(h[max(0,i-50):i]-l[max(0,i-50):i]): continue
        tp=c[i]+d*rr*R0; end=min(len(M)-1,i+int(180/tf)); jj,p=sim(h,l,c,i,d,c[i],sl,tp,end,sp[i]); last=i; rows.append((M.index[i],p/R0,p))
    return rows
if __name__=='__main__':
    U=bt.table('US500'); G=bt.table('XAU')
    for tr in (True,False):
        for rr in (1.5,2.0,3.0): stats(orb(U,rr,tr),f'US500 ORB15 trend={tr} TP{rr}R')
    for tr in (True,False):
        for rr in (2.0,): stats(orb(G,rr,tr),f'XAU ORB15 trend={tr} TP{rr}R')
    for tr in (False,True):
        for rr in (1.5,2.0,3.0): stats(fvg(G,rr,tr),f'XAU FVG-M5 NY2h trend50={tr} TP{rr}R')
    stats(fvg(U,2.0,False),'US500 FVG-M5 NY2h TP2R'); stats(fvg(U,2.0,True),'US500 FVG-M5 NY2h trend TP2R')
