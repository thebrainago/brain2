# Doi chieu MT5 <-> Python tren CUNG du lieu nen M5 XM (xuat bang EA SP500_XuatNen) va CUNG lich NYSE (ban Python cua LichNYSE.mqh).
# Mo phong TOM (mua 15:50 NY ngay GD cuoi thang, ban 15:50 ngay GD thu n thang moi) va IBS (<0.1, tren SMA200 D1, giu 3 ngay).
import sys, json, datetime as dt, numpy as np, pandas as pd
F=sys.argv[1]; MT5=sys.argv[2:]   # csv XM; cac csv giao dich MT5
def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
    mo=(h+l-7*m+114)//31; da=((h+l-7*m+114)%31)+1; return dt.date(y,mo,da)
def nth(y,m,wd,n):
    d=dt.date(y,m,1); d+=dt.timedelta((wd-d.weekday())%7); return d+dt.timedelta(7*(n-1))
def last(y,m,wd):
    d=dt.date(y,m+1,1)-dt.timedelta(1) if m<12 else dt.date(y,12,31); return d-dt.timedelta((d.weekday()-wd)%7)
def obs(d):
    if d.weekday()==5: return d-dt.timedelta(1)
    if d.weekday()==6: return d+dt.timedelta(1)
    return d
def nghi(y):
    s={obs(dt.date(y,1,1)),nth(y,1,0,3),nth(y,2,0,3),easter(y)-dt.timedelta(2),last(y,5,0),obs(dt.date(y,7,4)),nth(y,9,0,1),nth(y,11,3,4),obs(dt.date(y,12,25)),dt.date(2018,12,5),dt.date(2025,1,9)}
    if y>=2022: s.add(obs(dt.date(y,6,19)))
    return s
NGHI=set().union(*[nghi(y) for y in range(2015,2028)])
def dong_som(d): return (d.month==12 and d.day==24) or (d.month==7 and d.day==3) or d==nth(d.year,11,3,4)+dt.timedelta(1)
x=pd.read_csv(F); x['t']=pd.to_datetime(x.time,format='%Y.%m.%d %H:%M')
x=x[x.t>='2016-01-01']
ny=x.t.dt.tz_localize('Europe/Athens',ambiguous='NaT',nonexistent='NaT').dt.tz_convert('America/New_York').dt.tz_localize(None)
x['ny']=ny; x=x.dropna(subset=['ny']); x['ngay']=x.ny.dt.date; x['p']=x.ny.dt.hour*60+x.ny.dt.minute
x['sv_ngay']=x.t.dt.date
d1=x.groupby('sv_ngay').close.last()            # nen D1 theo gio may chu (nhu EA dung PERIOD_D1)
rth=x[(x.p>=570)&(x.p<960)]
ngay=sorted(d for d in set(rth.ngay) if d.weekday()<5 and d not in NGHI)
def gia_quyet_dinh(d):
    pd_=(780 if dong_som(d) else 960)-10; g=rth[(rth.ngay==d)]
    tr=g[g.p<pd_]; nx=x[(x.ngay==d)&(x.p>=pd_)]
    if len(tr)==0 or len(nx)==0: return None
    return dict(c=float(nx.open.iloc[0]),h=float(tr.high.max()),l=float(tr.low.min()),cl=float(tr.close.iloc[-1]),k=len(tr))
G={}
for d in ngay:
    q=gia_quyet_dinh(d)
    if q: G[d]=q
ds=sorted(G)
def sim(lenh,L=5.0,von=10000.0):
    eq=von; out=[]
    for a,b in lenh:
        pa=G[a]['c']; pb=G[b]['c']; lot=np.floor(L*eq/pa*10)/10; pl=lot*(pb-pa); eq+=pl; out.append((str(a),str(b),lot,pa,pb,pl))
    return eq,out
# TOM n3
tom=[]
for i,d in enumerate(ds[:-1]):
    if ds[i+1].month!=d.month:
        j=i+1; k=0
        while j<len(ds) and ds[j].month==ds[i+1].month:
            k+=1
            if k==3: tom.append((d,ds[j])); break
            j+=1
# IBS
ibs=[]; i=0
d1i=pd.Series(d1.values,index=pd.to_datetime(d1.index))
while i<len(ds):
    d=ds[i]; q=G[d]; ib=(q['cl']-q['l'])/(q['h']-q['l']) if q['h']>q['l'] and q['k']>=10 else 0.5
    prev=d1i[d1i.index<pd.Timestamp(d)]
    ok=len(prev)>=200 and q['c']>prev.iloc[-200:].mean()
    if ib<0.1 and ok and i+3<len(ds): ibs.append((d,ds[i+3])); i+=4; continue   # EA: ngay dong lenh khong vao lai
    i+=1
kq={}
for ten,le in (('tom3',tom),('ibs',ibs)):
    le=[z for z in le if z[0]>=dt.date(2017,1,1)]
    eq,out=sim(le); kq[ten]=dict(so_lenh=len(le),von_cuoi=round(eq,2),lenh=out)
    print(ten,'so lenh',len(le),'von cuoi (khong swap, khong spread)',round(eq,2))
# so voi MT5
for f in MT5:
    m=pd.read_csv(f); m['t']=pd.to_datetime(m.time,format='%Y.%m.%d %H:%M')
    vao=m[m.entry==0]; ra=m[m.entry==1]
    vd=set(vao.t.dt.date); ten='tom3' if 'tom3' in f else 'ibs'
    py=set(dt.date.fromisoformat(o[0]) for o in kq[ten]['lenh'])
    print(f.split('/')[-1],'MT5 lenh',len(vao),'Python',len(py),'trung ngay vao',len(vd&py),'chi MT5',sorted(map(str,vd-py))[:12],'chi Python',sorted(map(str,py-vd))[:12])
    kq[ten]['mt5']=dict(so_lenh=len(vao),trung=len(vd&py),chi_mt5=sorted(map(str,vd-py)),chi_python=sorted(map(str,py-vd)),
        lai_mt5=round(float(m.profit.sum()),2),swap_mt5=round(float(m.swap.sum()),2))
    print('  MT5 lai gop',round(m.profit.sum(),2),'swap',round(m.swap.sum(),2))
json.dump(kq,open('/workspace/brain2/sp500/ket_qua/doi_chieu_xm_mt5.json','w'),ensure_ascii=False,indent=0,default=str)
