# Uoc swap hau ky tu bang Deals (tester GBPUSD# bao swap=0). Dung swap XM micro do 10/2026: mua -4.35, ban -2.96 diem/lot/dem, x3 dem thu 4.
import re,html,sys,json
from datetime import datetime,timedelta
def num(x): return float(x.replace(' ','').replace('\xa0','')) if x.strip() else 0.0
p=sys.argv[1]; dep=float(sys.argv[2]); d0=sys.argv[3]; d1=sys.argv[4]
SM,SB,GIA_DIEM_LOT=(float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7])) if len(sys.argv)>7 else (-4.35,-2.96,1.0)
t=open(p,'rb').read().decode('utf-16')
rows=re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S);st=False;D=[]
for r in rows:
    c=[html.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)]
    if c and c[0]=='Time' and len(c)>1 and c[1]=='Deal': st=True;continue
    if st and len(c)>=13 and c[3] in('buy','sell'): D.append((datetime.strptime(c[0],'%Y.%m.%d %H:%M:%S'),c[3],c[4],num(c[5]),num(c[8])+num(c[9])+num(c[10])))
L=S=0.0; sw=0.0; i=0
day=D[0][0].replace(hour=0,minute=0,second=0)+timedelta(days=1)
end=D[-1][0]
bal=dep; eq_pts=[]; tot=0; ev=[]
for d in D: ev.append(d)
swap_by_year={}
while day<=end+timedelta(days=1):
    while i<len(D) and D[i][0]<day:
        tm,ty,di,v,_=D[i]
        if di=='in': 
            if ty=='buy': L+=v
            else: S+=v
        elif di=='out':
            if ty=='sell': L-=v
            else: S-=v
        i+=1
    wd=(day-timedelta(days=1)).weekday()  # dem bat dau tu ngay wd
    if wd<5:
        k=3 if wd==2 else 1
        x=k*(L*SM+S*SB)*GIA_DIEM_LOT
        sw+=x; y=str((day-timedelta(days=1)).year); swap_by_year[y]=swap_by_year.get(y,0)+x
    day+=timedelta(days=1)
net=sum(d[4] for d in D); net2=net+sw
yrs=(datetime.strptime(d1,'%Y-%m-%d')-datetime.strptime(d0,'%Y-%m-%d')).days/365.25
c=lambda n: round(((1+n/dep)**(1/yrs)-1)*100,2) if n>-dep else -100
print(json.dumps(dict(net_tester=round(net,1),swap_uoc=round(sw,1),net_sau_swap=round(net2,1),cagr_tester=c(net),cagr_sau_swap=c(net2),swap_theo_nam={k:round(v,1) for k,v in swap_by_year.items()}),ensure_ascii=False))
